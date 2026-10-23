#!/usr/bin/env python3
"""
run_wireshark_pop3_sim.py
Simulates a live POP3 server and client session on local port 1110 for Wireshark capture.
Demonstrates:
1. TCP 3-Way Handshake
2. Plaintext USER / PASS credential exposure
3. Mailbox interrogation (STAT, LIST)
4. Streaming RETR payload
5. Abrupt link disconnect (simulated satellite flap)
6. Reconnect attempt triggering -ERR [IN-USE] mailbox locked!
"""

import socket
import threading
import time
import sys

PORT = 1110

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', PORT))
    server.listen(2)

    # Session 1: Client logs in, requests RETR, then severed link
    conn, addr = server.accept()
    conn.sendall(b'+OK Dovecot POP3 server ready (HQ Enterprise Maildrop)\r\n')
    
    while True:
        try:
            data = conn.recv(1024).decode('utf-8', errors='ignore')
            if not data:
                break
            cmd = data.strip()
            upper_cmd = cmd.upper()
            
            if upper_cmd.startswith('USER'):
                conn.sendall(b'+OK User accepted\r\n')
            elif upper_cmd.startswith('PASS'):
                conn.sendall(b'+OK Logged in. Mailbox spool locked exclusively.\r\n')
            elif upper_cmd.startswith('STAT'):
                conn.sendall(b'+OK 5 3145728\r\n')
            elif upper_cmd.startswith('LIST'):
                resp = (
                    b'+OK 5 messages (3145728 octets)\r\n'
                    b'1 12288\r\n'
                    b'2 87040\r\n'
                    b'3 460800\r\n'
                    b'4 1887436\r\n'
                    b'5 3355440\r\n'
                    b'.\r\n'
                )
                conn.sendall(resp)
            elif upper_cmd.startswith('RETR 4'):
                payload = (
                    b'+OK 1887436 octets\r\n'
                    b'From: engineering-hq@enterprise.com\r\n'
                    b'To: branch_user1@enterprise.com\r\n'
                    b'Subject: CRITICAL: Q4 Structural Blueprints Attachment\r\n'
                    b'Content-Type: multipart/mixed; boundary="====B123===="\r\n\r\n'
                    b'[STREAMING 1.88 MB BASE64 MIME ATTACHMENT... CHUNKS 1-15 TRANSMITTED...]\r\n'
                )
                conn.sendall(payload)
                time.sleep(0.3)
                # ABRUPT DISCONNECT: Simulating satellite rain-fade link drop
                conn.close()
                break
        except Exception:
            break

    # Session 2: User immediately attempts to reconnect
    conn2, addr2 = server.accept()
    conn2.sendall(b'+OK Dovecot POP3 server ready (HQ Enterprise Maildrop)\r\n')
    while True:
        try:
            data = conn2.recv(1024).decode('utf-8', errors='ignore')
            if not data:
                break
            upper_cmd = data.strip().upper()
            if upper_cmd.startswith('USER'):
                conn2.sendall(b'+OK User accepted\r\n')
            elif upper_cmd.startswith('PASS'):
                # Server denies entry because previous session left an orphaned lock!
                conn2.sendall(b'-ERR [IN-USE] Mailbox is locked by another session! (Orphaned dotlock active)\r\n')
                time.sleep(0.1)
                conn2.close()
                break
        except Exception:
            break
            
    server.close()

def run_client():
    time.sleep(0.2)
    print("\n--- [SESSION 1: NORMAL LOGIN & RETR STREAMING] ---")
    c1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c1.connect(('127.0.0.1', PORT))
    print("S:", c1.recv(1024).decode().strip())
    
    for cmd in ['USER branch_user1', 'PASS SecretP@ss2026!', 'STAT', 'LIST', 'RETR 4']:
        print(f"C: {cmd}")
        c1.sendall(f"{cmd}\r\n".encode())
        resp = c1.recv(2048).decode(errors='ignore')
        print("S:", resp.strip()[:80] + ("..." if len(resp.strip()) > 80 else ""))
        time.sleep(0.2)
    
    print("\n[!] SIMULATING ABRUPT SATELLITE LINK DROP (NO QUIT SENT)...")
    c1.close()
    time.sleep(0.8)

    print("\n--- [SESSION 2: RECONNECT ATTEMPT AFTER LINK DROP] ---")
    c2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c2.connect(('127.0.0.1', PORT))
    print("S:", c2.recv(1024).decode().strip())
    
    for cmd in ['USER branch_user1', 'PASS SecretP@ss2026!']:
        print(f"C: {cmd}")
        c2.sendall(f"{cmd}\r\n".encode())
        resp = c2.recv(1024).decode(errors='ignore')
        print("S:", resp.strip())
        time.sleep(0.2)
    c2.close()
    print("\n[+] SIMULATION COMPLETE! Check Wireshark window for captured packets.")

if __name__ == "__main__":
    t_srv = threading.Thread(target=start_server, daemon=True)
    t_srv.start()
    run_client()
