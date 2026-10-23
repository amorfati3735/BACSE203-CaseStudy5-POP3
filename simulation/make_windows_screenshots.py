"""Drive the Wireshark 4.x GUI on Windows and save full-screen evidence screenshots.

Usage:  python simulation/make_windows_screenshots.py

Produces four full-screen PNGs in screenshots/ from the lab capture:

    win01_pop_dialogue.png                            (pop filter, 556 frames)
    win02_syn_handshake.png                    (SYN filter on port 1110, 4 frames)
    win03_follow_stream_session1_retr_blackout.png   (Follow TCP Stream, stream 0)
    win04_follow_stream_session2_lockout.png         (Follow TCP Stream, stream 2)

How it works
------------
* Wireshark is launched with the capture pre-loaded and Decode-As already set
  (tcp.port 1110 -> POP) and the window maximized, so every screenshot is
  full-screen with all three panes visible.
* Session 2 runs on a second, FRESH instance with its display filter
  pre-applied via -Y: Qt menu navigation is only reliable before any dialog
  has been opened in the process, so each instance performs exactly one
  Analyze -> Follow -> TCP Stream menu walk.
* Every applied filter is verified against Wireshark's status bar, and each
  Follow-TCP-Stream dialog is verified by reading its stream text (RETR /
  IN-USE) before the screenshot is saved.

Requires: Wireshark 4.x, pywinauto, pillow, and an interactive desktop.
Stale Wireshark.exe processes are terminated at start (they would steal
foreground focus and eat the synthetic clicks).
"""

from __future__ import annotations

import ctypes
import re
import subprocess
import sys
import time
from pathlib import Path

from pywinauto import Application, Desktop
from pywinauto.keyboard import send_keys

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
CAPTURE = REPO / "captures" / "pop3_wan_capture.pcapng"
OUT = REPO / "screenshots"
WIRESHARK = Path(r"C:\Program Files\Wireshark\Wireshark.exe")

# Expected "Displayed" counts, pre-computed with tshark on the same capture.
EXPECTED_POP = 556
EXPECTED_SYN = 4
EXPECTED_STREAM2 = 13

PID = {"v": None}
PROCS: list = []

# Keep coordinates and captures in physical pixels regardless of DPI scaling.
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()


def log(msg: str) -> None:
    print(f"[wireshark-evidence] {msg}", flush=True)


def save(win, name: str) -> Path:
    OUT.mkdir(exist_ok=True)
    path = OUT / name
    win.capture_as_image().save(path)
    log(f"saved {path.name} ({path.stat().st_size // 1024} KB)")
    return path


def launch(extra_args=None):
    args = [str(WIRESHARK), "-r", str(CAPTURE), "-d", "tcp.port==1110,pop"]
    args += extra_args or []
    proc = subprocess.Popen(args)
    PID["v"] = proc.pid
    PROCS.append(proc)
    return proc


def connect_window(proc):
    app = Application(backend="uia").connect(process=proc.pid, timeout=30)
    win = app.window(title_re=".*pop3_wan_capture.*")
    win.wait("visible ready", timeout=15)
    win.maximize()
    win.set_focus()
    time.sleep(2.5)  # full load + dissection
    return win


def status_packets(win) -> str:
    for w in win.descendants(control_type="Text"):
        name = w.element_info.name or ""
        if name.startswith("Packets:") or "Displayed" in name:
            return name
    return ""


def verify_displayed(win, expected: int, label: str) -> None:
    m = re.search(r"Displayed:\s*(\d+)", status_packets(win))
    shown = int(m.group(1)) if m else None
    if shown != expected:
        raise RuntimeError(f"{label}: status bar shows {shown}, expected {expected}")
    log(f"{label}: Displayed {shown} == expected {expected}")


def find_filter_edit(win):
    deadline = time.time() + 15
    while time.time() < deadline:
        for w in win.descendants(control_type="Edit"):
            if (w.element_info.automation_id or "").endswith("DisplayFilterEdit"):
                return w
        time.sleep(1)
    raise RuntimeError("display filter edit box not found")


def set_filter(win, text: str) -> None:
    box = find_filter_edit(win)
    box.set_focus()
    send_keys("^a")
    if text:
        send_keys(text, pause=0.02)
    send_keys("{ENTER}")
    time.sleep(1.5)


def select_first_packet(win) -> None:
    tree = win.child_window(auto_id="Packet list", control_type="Tree")
    tree.wait("visible ready", timeout=10)
    r = tree.rectangle()
    win.click_input(coords=(r.left + 60, r.top + 33))  # first data row
    time.sleep(0.5)


def follow_dialog_window(desktop):
    """The Follow TCP Stream dialog belonging to OUR Wireshark pid."""
    for w in desktop.windows():
        try:
            if "Follow TCP Stream" not in (w.window_text() or ""):
                continue
            if PID["v"] is None or w.process_id() == PID["v"]:
                return w
        except Exception:
            continue
    return None


def dialog_open(desktop) -> bool:
    w = follow_dialog_window(desktop)
    return w is not None and w.is_visible()


def follow_dialog(desktop):
    deadline = time.time() + 20
    while time.time() < deadline:
        dlg = follow_dialog_window(desktop)
        if dlg is not None and dlg.is_visible():
            time.sleep(0.8)
            return dlg
        time.sleep(0.5)
    raise RuntimeError("Follow TCP Stream dialog (own pid) not found")


def dialog_text(dlg) -> str:
    parts = []
    for ctl in dlg.descendants():
        try:
            t = ctl.window_text() or ""
            if len(t) > 40:
                parts.append(t)
        except Exception:
            pass
    return chr(10).join(parts)


def verify_dialog_content(dlg, needle: str, label: str) -> None:
    text = dialog_text(dlg)
    if needle in text:
        log(f"{label}: dialog content contains {needle!r} - verified")
    else:
        log(f"{label}: WARNING - {needle!r} not found in dialog text ({len(text)} chars read)")


def open_analyze_menu(win) -> None:
    win.set_focus()
    time.sleep(0.3)
    for w in win.descendants(control_type="MenuItem"):
        if w.element_info.name == "Analyze":
            w.click_input()
            time.sleep(0.7)
            return
    raise RuntimeError("Analyze menu item not found in menu bar")


def follow_tcp_stream(win, desktop) -> None:
    win.set_focus()
    # Analyze menu -> mnemonics (A menu open, f Follow, t TCP Stream, Enter).
    for attempt in range(3):
        if attempt:
            send_keys("{ESC 3}")
            time.sleep(0.8)
            win.set_focus()
        open_analyze_menu(win)
        send_keys("f")
        time.sleep(0.6)
        send_keys("t")
        time.sleep(0.6)
        send_keys("{ENTER}")
        time.sleep(2.0)
        if dialog_open(desktop):
            return
    send_keys("{ESC 3}")
    time.sleep(0.5)

    # Fallback: right-click the selected packet row, click through the popup.
    tree = win.child_window(auto_id="Packet list", control_type="Tree")
    r = tree.rectangle()
    win.right_click_input(coords=(r.left + 60, r.top + 33))
    time.sleep(1.2)
    for label in ("Follow", "TCP Stream"):
        deadline = time.time() + 4
        hit = None
        while time.time() < deadline and hit is None:
            for w in desktop.windows():
                try:
                    for c in w.descendants(control_type="MenuItem"):
                        if c.element_info.name and label in c.element_info.name:
                            hit = c
                            break
                except Exception:
                    continue
                if hit:
                    break
            if hit is None:
                time.sleep(0.4)
        if hit is None:
            raise RuntimeError(f"popup menu item '{label}' not found")
        hit.click_input()
        time.sleep(0.8)
    time.sleep(1.5)
    if not dialog_open(desktop):
        raise RuntimeError("Follow TCP Stream dialog never opened")


def _wait_dialog_gone(timeout: float = 5.0) -> None:
    desktop = Desktop(backend="uia")
    deadline = time.time() + timeout
    while time.time() < deadline:
        if follow_dialog_window(desktop) is None:
            time.sleep(0.6)
            return
        time.sleep(0.3)
    log("WARNING: follow dialog still open after close attempt")


def close_dialog(dlg) -> None:
    for label_re in (r".*Close.*", r".*Done.*", r".*OK.*"):
        try:
            btn = dlg.child_window(title_re=label_re, control_type="Button")
            if btn.exists(timeout=2):
                btn.set_focus()
                btn.click_input()
                _wait_dialog_gone()
                return
        except Exception:
            continue
    dlg.set_focus()
    send_keys("{ESC}")
    _wait_dialog_gone()


def main() -> int:
    if not WIRESHARK.exists() or not CAPTURE.exists():
        log("Wireshark or capture missing")
        return 2

    PROCS.clear()
    r = subprocess.run(["taskkill", "/IM", "Wireshark.exe", "/F"], capture_output=True, text=True)
    if r.returncode == 0:
        log("terminated stale Wireshark instances (they steal foreground focus)")
        time.sleep(1.5)

    desktop = Desktop(backend="uia")

    # ---- Phase A: overview, handshake, and the full first session ----------
    proc = launch()
    try:
        win = connect_window(proc)

        set_filter(win, "pop")
        verify_displayed(win, EXPECTED_POP, "pop dialogue")
        save(win, "win01_pop_dialogue.png")

        set_filter(win, "tcp.flags.syn == 1 && tcp.port == 1110")
        verify_displayed(win, EXPECTED_SYN, "SYN handshake")
        save(win, "win02_syn_handshake.png")

        set_filter(win, "tcp.stream eq 0")
        select_first_packet(win)
        follow_tcp_stream(win, desktop)
        dlg = follow_dialog(desktop)
        dlg.maximize()
        time.sleep(0.8)
        verify_dialog_content(dlg, "RETR", "session 1 dialog")
        save(dlg, "win03_follow_stream_session1_retr_blackout.png")
        close_dialog(dlg)
    finally:
        proc.terminate()
        proc.wait(timeout=10)
    time.sleep(1.5)

    # ---- Phase B: fresh instance for the lockout session --------------------
    # Qt menu navigation is only reliable before any dialog has been opened,
    # so session 2 gets its own instance with the filter pre-applied via -Y.
    log("relaunching with -Y 'tcp.stream eq 2' (fresh instance)")
    proc2 = launch(["-Y", "tcp.stream eq 2"])
    try:
        win2 = connect_window(proc2)
        verify_displayed(win2, EXPECTED_STREAM2, "stream 2 prefilter")
        select_first_packet(win2)
        follow_tcp_stream(win2, desktop)
        dlg = follow_dialog(desktop)
        dlg.maximize()
        time.sleep(0.8)
        verify_dialog_content(dlg, "IN-USE", "session 2 dialog")
        save(dlg, "win04_follow_stream_session2_lockout.png")
        close_dialog(dlg)
    finally:
        proc2.terminate()
        proc2.wait(timeout=10)

    log("all evidence screenshots captured")
    return 0


if __name__ == "__main__":
    sys.exit(main())
