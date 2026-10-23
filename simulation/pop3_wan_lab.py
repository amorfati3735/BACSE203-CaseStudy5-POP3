#!/usr/bin/env python3
"""
pop3_wan_lab.py — reproducible POP3-over-WAN experiment for BACSE203 Case Study 5.

What this builds (all on 127.0.0.1, no root, nothing to install beyond Python 3
and tshark):

    MUA client  --->  127.0.0.1:1110  [WAN EMULATOR]  --->  127.0.0.1:1111
                      256 kbps token bucket                POP3 server
                      225 ms one-way delay                 (5.8 MB spool)

The emulator is a user-space TCP relay. It shapes the *application* dialogue:
each client command is delayed by 225 ms, and the server->client direction is
paced at 256 kbps (32,000 B/s), so a POP3 command/response turn takes ~450 ms
and the RETR payload arrives at link rate. The TCP handshake itself terminates
on loopback and is therefore local; this is disclosed in the report.

After CUTOFF_BYTES of the 1,887,436-byte message the emulator blacks out the
link: it stops forwarding in both directions but leaves both TCP sockets open,
which is the half-open failure mode of a VSAT fade. The client's read timeout
fires, it reconnects, and the server — still holding the spool lock because no
QUIT arrived — answers `-ERR [IN-USE]`.

Run:
    python3 simulation/pop3_wan_lab.py            # lab + capture (needs tshark)
    python3 simulation/pop3_wan_lab.py --no-capture
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

# --------------------------------------------------------------------------
# Link and workload parameters (kept identical to the report's Table 4)
# --------------------------------------------------------------------------
LINK_BPS = 256_000                 # 256 kbps rate-limited VSAT backhaul
ONE_WAY_DELAY = 0.225              # 225 ms one-way -> ~450 ms POP3 turn RTT
SPOOL_SIZES = [12_288, 87_040, 460_800, 1_887_436, 3_355_440]
CUTOFF_BYTES = 780_000             # ~41 % of message 4, then the link dies
LOCK_TIMEOUT = 300                 # server keeps an orphaned lock this long
PROXY_PORT = 1110
SERVER_PORT = 1111
CLIENT_TIMEOUT = 8.0
BOUNDARY = b"----=_BACSE203_LabBoundary_2026"

HERE = Path(__file__).resolve().parent
CAPTURE_DIR = HERE.parent / "captures"
CAPTURE_PATH = CAPTURE_DIR / "pop3_wan_capture.pcapng"
SUMMARY_PATH = CAPTURE_DIR / "run_summary.json"

_log_lock = threading.Lock()


def log(msg: str) -> None:
    with _log_lock:
        print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# --------------------------------------------------------------------------
# Message construction — real Base64 MIME, exact octet sizes
# --------------------------------------------------------------------------
def build_message(size: int, subject: str, msg_id: str) -> bytes:
    head = (
        b"Return-Path: <engineering-hq@enterprise.com>\r\n"
        b"From: Engineering HQ <engineering-hq@enterprise.com>\r\n"
        b"To: branch_user1@enterprise.com\r\n"
        b"Subject: " + subject.encode() + b"\r\n"
        b"Date: Thu, 22 Oct 2026 09:15:00 +0000\r\n"
        b"Message-ID: <" + msg_id.encode() + b"@enterprise.com>\r\n"
        b"MIME-Version: 1.0\r\n"
        b'Content-Type: multipart/mixed; boundary="' + BOUNDARY + b'"\r\n'
        b"\r\n"
    )
    text = (
        b"--" + BOUNDARY + b"\r\n"
        b"Content-Type: text/plain; charset=us-ascii\r\n"
        b"Content-Transfer-Encoding: 7bit\r\n\r\n"
        b"Please find the attached drawing set for the current revision.\r\n\r\n"
    )
    attachment = (
        b"--" + BOUNDARY + b"\r\n"
        b'Content-Type: application/pdf; name="blueprints.pdf"\r\n'
        b"Content-Transfer-Encoding: base64\r\n\r\n"
    )
    tail = b"\r\n--" + BOUNDARY + b"--\r\n"

    body_len = size - len(head) - len(text) - len(attachment) - len(tail)
    if body_len < 4:
        raise ValueError(f"message size {size} too small for the MIME envelope")

    # RFC 2045: Base64 lines are at most 76 characters, terminated by CRLF.
    full_lines, remainder = divmod(body_len, 78)
    body = (b"A" * 76 + b"\r\n") * full_lines
    if remainder:
        body += b"A" * (remainder - 2) + b"\r\n" if remainder >= 2 else b"A" * remainder
    message = head + text + attachment + body + tail

    if len(message) != size:  # keep LIST/STAT arithmetic exact
        delta = size - len(message)
        message = message.replace(b"\r\n--" + BOUNDARY + b"--", b"A" * delta + b"\r\n--" + BOUNDARY + b"--")
    assert len(message) == size, (len(message), size)
    return message


def build_spool() -> list[dict]:
    subjects = [
        "Weekly shift roster",
        "Supplier manifest - October",
        "Pump station inspection report",
        "CRITICAL: Q4 structural blueprints attachment",
        "Site survey archive (drawings + photographs)",
    ]
    return [
        {"n": i + 1, "subject": subjects[i], "data": build_message(size, subjects[i], f"{i+1:08x}")}
        for i, size in enumerate(SPOOL_SIZES)
    ]


# --------------------------------------------------------------------------
# POP3 server (RFC 1939 command set, exclusive spool lock)
# --------------------------------------------------------------------------
class Pop3Server(threading.Thread):
    daemon = True

    def __init__(self, spool: list[dict]):
        super().__init__(name="pop3-server")
        self.spool = spool
        self.lock = threading.Lock()
        self.lock_owner: str | None = None
        self.lock_acquired_at: float = 0.0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", SERVER_PORT))
        self.sock.listen(5)
        self.sock.settimeout(0.5)
        self.stop = threading.Event()

    # mailbox lock -----------------------------------------------------------
    def try_acquire(self, who: str) -> bool:
        with self.lock:
            if self.lock_owner is not None:
                if time.time() - self.lock_acquired_at < LOCK_TIMEOUT:
                    return False
                log(f"server: stale lock from {self.lock_owner} expired")
            self.lock_owner = who
            self.lock_acquired_at = time.time()
            return True

    def release(self) -> None:
        with self.lock:
            self.lock_owner = None

    # main loop --------------------------------------------------------------
    def run(self) -> None:
        while not self.stop.is_set():
            try:
                conn, addr = self.sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            threading.Thread(target=self.handle, args=(conn, addr), daemon=True).start()

    def handle(self, conn: socket.socket, addr) -> None:
        who = f"{addr[0]}:{addr[1]}"
        authed = False
        clean_quit = False
        conn.settimeout(LOCK_TIMEOUT)
        log(f"server: connection from {who}")
        try:
            conn.sendall(b"+OK BACSE203 lab POP3 server ready\r\n")
            stream = conn.makefile("rb")
            while True:
                line = stream.readline(4096)
                if not line:
                    break
                cmd, _, arg = line.decode("ascii", "replace").strip().partition(" ")
                cmd = cmd.upper()
                log(f"server <- {line.decode(errors='replace').strip()}")
                if cmd == "USER":
                    conn.sendall(b"+OK User accepted\r\n")
                elif cmd == "PASS":
                    if not self.try_acquire(who):
                        conn.sendall(b"-ERR [IN-USE] Mailbox is locked by another session!\r\n")
                        log("server: spool lock held by an orphaned session -> -ERR [IN-USE]")
                        break
                    authed = True
                    conn.sendall(b"+OK Logged in. Mailbox spool locked exclusively.\r\n")
                elif cmd in {"STAT", "LIST", "UIDL", "NOOP"} and not authed:
                    conn.sendall(b"-ERR Authenticate first\r\n")
                elif cmd == "STAT":
                    total = sum(len(m["data"]) for m in self.spool)
                    conn.sendall(f"+OK {len(self.spool)} {total}\r\n".encode())
                elif cmd == "LIST":
                    out = [f"+OK {len(self.spool)} messages ({sum(len(m['data']) for m in self.spool)} octets)"]
                    out += [f"{m['n']} {len(m['data'])}" for m in self.spool]
                    out.append(".")
                    conn.sendall(("\r\n".join(out) + "\r\n").encode())
                elif cmd == "UIDL":
                    out = ["+OK"] + [f"{m['n']} {uuid.uuid5(uuid.NAMESPACE_DNS, m['subject'])}" for m in self.spool] + ["."]
                    conn.sendall(("\r\n".join(out) + "\r\n").encode())
                elif cmd == "TOP":
                    try:
                        num, nlines = (int(x) for x in arg.split())
                    except ValueError:
                        conn.sendall(b"-ERR usage: TOP msg n\r\n")
                        continue
                    msg = self.spool[num - 1]["data"]
                    header_end = msg.find(b"\r\n\r\n") + 4
                    body_lines = msg[header_end:].split(b"\r\n")[:nlines]
                    payload = msg[:header_end] + b"\r\n".join(body_lines) + (b"\r\n" if nlines else b"") + b".\r\n"
                    conn.sendall(b"+OK top of message follows\r\n" + payload)
                    log(f"server: TOP {num} {nlines} -> {len(payload)} bytes")
                elif cmd == "RETR":
                    try:
                        num = int(arg)
                    except ValueError:
                        conn.sendall(b"-ERR usage: RETR msg\r\n")
                        continue
                    msg = self.spool[num - 1]["data"]
                    conn.sendall(f"+OK {len(msg)} octets\r\n".encode())
                    log(f"server: RETR {num} -> streaming {len(msg)} octets")
                    conn.sendall(msg + b"\r\n.\r\n")
                    log(f"server: RETR {num} complete")
                elif cmd == "DELE":
                    conn.sendall(b"+OK message marked for deletion (not yet committed)\r\n")
                elif cmd == "RSET":
                    conn.sendall(b"+OK\n")
                elif cmd == "QUIT":
                    conn.sendall(b"+OK BACSE203 lab server signing off\r\n")
                    clean_quit = True
                    break
                else:
                    conn.sendall(b"-ERR Unsupported command\r\n")
        except (ConnectionResetError, BrokenPipeError, socket.timeout, OSError) as exc:
            log(f"server: session error for {who}: {type(exc).__name__}")
        finally:
            if clean_quit:
                self.release()
                log(f"server: QUIT from {who} -> spool lock released")
            else:
                log(f"server: {who} dropped without QUIT -> spool lock retained")
            try:
                conn.close()
            except OSError:
                pass

    def shutdown(self) -> None:
        self.stop.set()
        try:
            self.sock.close()
        except OSError:
            pass


# --------------------------------------------------------------------------
# User-space WAN emulator: 225 ms one-way delay + 256 kbps token bucket
# --------------------------------------------------------------------------
class WanEmulator(threading.Thread):
    daemon = True

    def __init__(self):
        super().__init__(name="wan-emulator")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", PROXY_PORT))
        self.sock.listen(5)
        self.sock.settimeout(0.5)
        self.stop = threading.Event()
        self.bytes_to_client = 0
        self.blackhole = threading.Event()
        self.cutoff_at: float | None = None
        self.held: list[socket.socket] = []

    def run(self) -> None:
        while not self.stop.is_set():
            try:
                client, _ = self.sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            if self.blackhole.is_set():
                # The scenario's link is restored before the reconnect attempt.
                self.blackhole.clear()
                self.bytes_to_client = 0
                log("wan: link restored for the reconnect attempt")
            try:
                server = socket.create_connection(("127.0.0.1", SERVER_PORT), timeout=5)
            except OSError:
                client.close()
                continue
            self.held += [client, server]
            threading.Thread(target=self.relay_up, args=(client, server), daemon=True).start()
            threading.Thread(target=self.relay_down, args=(server, client), daemon=True).start()

    def relay_up(self, client: socket.socket, server: socket.socket) -> None:
        """Client -> server: one 225 ms propagation delay per command."""
        try:
            while not self.stop.is_set():
                data = client.recv(65536)
                if not data:
                    break
                if self.blackhole.is_set():
                    continue  # link is down: swallow, do not close (half-open)
                time.sleep(ONE_WAY_DELAY)
                server.sendall(data)
        except OSError:
            pass

    def relay_down(self, server: socket.socket, client: socket.socket) -> None:
        """Server -> client: 225 ms one-way delay, paced at 256 kbps."""
        rate = LINK_BPS / 8.0                    # 32,000 bytes/s
        capacity = 1460.0
        tokens = capacity
        last = time.monotonic()
        try:
            while not self.stop.is_set():
                data = server.recv(65536)
                if not data:
                    break
                if self.blackhole.is_set():
                    continue
                # Control replies get the one-way propagation delay; bulk data
                # streams continuously, exactly as a pipelined satellite link does.
                if len(data) <= 1024:
                    time.sleep(ONE_WAY_DELAY)
                for i in range(0, len(data), 1460):
                    chunk = data[i:i + 1460]
                    while True:
                        now = time.monotonic()
                        tokens = min(capacity, tokens + (now - last) * rate)
                        last = now
                        if tokens >= len(chunk):
                            break
                        time.sleep((len(chunk) - tokens) / rate)
                    tokens -= len(chunk)
                    client.sendall(chunk)
                    self.bytes_to_client += len(chunk)
                    if self.bytes_to_client >= CUTOFF_BYTES and not self.blackhole.is_set():
                        self.cutoff_at = time.monotonic()
                        self.blackhole.set()
                        log(
                            f"wan: link blackout after {self.bytes_to_client} bytes "
                            f"({self.bytes_to_client / len_retr():.1%} of RETR 4); "
                            "sockets left half-open, no FIN/RST"
                        )
                        return
        except OSError:
            pass

    def shutdown(self) -> None:
        self.stop.set()
        try:
            self.sock.close()
        except OSError:
            pass
        for s in self.held:
            try:
                s.close()
            except OSError:
                pass


def len_retr() -> int:
    return SPOOL_SIZES[3]


# --------------------------------------------------------------------------
# Client
# --------------------------------------------------------------------------
class Pop3Client:
    def __init__(self, timeout: float = CLIENT_TIMEOUT):
        self.sock = socket.create_connection(("127.0.0.1", PROXY_PORT), timeout=timeout)
        self.sock.settimeout(timeout)
        self.stream = self.sock.makefile("rb")

    def readline(self) -> str:
        return self.stream.readline(4096).decode("ascii", "replace").rstrip("\r\n")

    def cmd(self, line: str) -> str:
        self.sock.sendall(line.encode() + b"\r\n")
        return self.readline()

    def read_multiline(self) -> tuple[bytes, int]:
        buf = bytearray()
        while True:
            line = self.stream.readline(8192)
            if not line:
                break
            if line == b".\r\n":
                break
            buf += line
        return bytes(buf), len(buf)

    def close(self) -> None:
        try:
            self.sock.close()
        except OSError:
            pass


def run_lab(summary: dict) -> None:
    # -- Session 1: triage with UIDL + TOP, then a RETR that dies -----------
    log("client: --- SESSION 1 -------------------------------------------------")
    c = Pop3Client()
    print("S:", c.readline())
    for line in ["USER branch_user1", "PASS SecretP@ss2026!", "STAT", "LIST", "UIDL"]:
        print(f"C: {line}")
        c.sock.sendall(line.encode() + b"\r\n")
        print("S:", c.readline())
        if line.split()[0] in {"LIST", "UIDL"}:
            _, n = c.read_multiline()
            print(f"   ({n} bytes of multiline data)")
    print("C: TOP 4 0")
    first = c.cmd("TOP 4 0")
    header, top_len = c.read_multiline()
    print("S:", first)
    print(f"   header block: {top_len} bytes (subject = {len(header)} B incl. CRLFs)")
    summary["top_header_bytes"] = top_len
    summary["top_reply_bytes"] = top_len + 3  # headers + CRLF + terminating '.'

    print("C: RETR 4")
    print("S:", c.cmd("RETR 4"))
    start = time.monotonic()
    received = 0
    last_data = start
    try:
        while True:
            chunk = c.sock.recv(65536)
            if not chunk:
                break
            received += len(chunk)
            last_data = time.monotonic()
    except socket.timeout:
        log("client: read timeout — link produced no data (blackout)")
    except ConnectionResetError:
        log("client: connection reset by the network")
    elapsed = last_data - start
    summary.update(retr_received=received, retr_seconds=round(elapsed, 2),
                   retr_kbps=round(received * 8 / elapsed / 1000, 1) if elapsed else 0)
    log(f"client: RETR aborted after {received} bytes in {elapsed:.2f}s "
        f"({received * 8 / elapsed / 1000:.1f} kbps)")
    c.close()

    # -- Session 2: reconnect while the orphaned lock still exists ----------
    log("client: --- SESSION 2 (reconnect) --------------------------------------")
    time.sleep(1.0)
    c2 = Pop3Client()
    print("S:", c2.readline())
    print("C: USER branch_user1"); print("S:", c2.cmd("USER branch_user1"))
    print("C: PASS SecretP@ss2026!"); resp = c2.cmd("PASS SecretP@ss2026!")
    print("S:", resp)
    summary["reconnect_response"] = resp
    c2.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-capture", action="store_true", help="skip the tshark capture")
    args = ap.parse_args()

    if shutil.which("tshark") is None and not args.no_capture:
        print("tshark not found; re-run with --no-capture", file=sys.stderr)
        return 2

    CAPTURE_DIR.mkdir(exist_ok=True)
    summary: dict = {
        "link_bps": LINK_BPS,
        "one_way_delay_ms": int(ONE_WAY_DELAY * 1000),
        "spool_sizes": SPOOL_SIZES,
        "spool_total": sum(SPOOL_SIZES),
        "cutoff_bytes": CUTOFF_BYTES,
    }

    spool = build_spool()
    log(f"spool built: {len(spool)} messages, {sum(len(s['data']) for s in spool)} octets total")

    server = Pop3Server(spool)
    wan = WanEmulator()
    server.start()
    wan.start()
    time.sleep(0.3)

    tshark = None
    if not args.no_capture:
        tshark = subprocess.Popen(
            ["tshark", "-i", "lo", "-f", f"tcp port {PROXY_PORT} or tcp port {SERVER_PORT}",
             "-w", str(CAPTURE_PATH), "-q"],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        )
        time.sleep(1.0)

    try:
        run_lab(summary)
    finally:
        time.sleep(2.0)          # let the lockout response reach the client
        if tshark:
            tshark.send_signal(signal.SIGINT)
            try:
                tshark.wait(timeout=10)
            except subprocess.TimeoutExpired:
                tshark.kill()
        wan.shutdown()
        server.shutdown()

    summary["cutoff_at_seconds"] = round(wan.cutoff_at - start_time, 2) if wan.cutoff_at and start_time else None
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n")
    log(f"summary -> {SUMMARY_PATH}")
    if not args.no_capture:
        log(f"capture -> {CAPTURE_PATH}")
    return 0


start_time = time.monotonic()

if __name__ == "__main__":
    raise SystemExit(main())
