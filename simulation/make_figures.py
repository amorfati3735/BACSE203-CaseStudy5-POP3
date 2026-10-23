#!/usr/bin/env python3
"""
make_figures.py — regenerates every figure used in FINAL_REPORT.md.

The two original diagrams clipped their right-hand columns (text ran off the
canvas) and quoted inconsistent timings. These versions lay boxes out in data
units so nothing overflows, and they use the measured values written by
simulation/pop3_wan_lab.py to captures/run_summary.json.

    python3 simulation/make_figures.py
"""

from __future__ import annotations

import json
import subprocess
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)
CAP = ROOT / "captures" / "pop3_wan_capture.pcapng"
SUMMARY = json.loads((ROOT / "captures" / "run_summary.json").read_text())

NAVY = "#16243d"
BLUE = "#1d4ed8"
GREEN = "#047857"
AMBER = "#b45309"
RED = "#b91c1c"
PURPLE = "#6d28d9"
GREY = "#475569"
LIGHT = "#f8fafc"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.edgecolor": "#cbd5e1",
    "savefig.facecolor": "white",
})

HEADER = 8.5          # height of a box's coloured title band, in data units
LINE = 3.1            # vertical pitch of body text, in data units


def canvas(w, h, title, subtitle):
    fig = plt.figure(figsize=(w, h), dpi=300)
    fig.patch.set_facecolor("white")
    fig.text(0.02, 0.97, title, fontsize=18, fontweight="bold", color=NAVY, va="top")
    fig.text(0.02, 0.925, subtitle, fontsize=10, color=GREY, va="top")
    return fig


def box(ax, x, y, w, h, title, lines, color, title_size=10.5, body_size=8.2, wrap=36):
    """Rounded card with a coloured header band; body text starts below it."""
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.010,rounding_size=1.4",
        linewidth=1.5, edgecolor=color, facecolor="white", zorder=2))
    ax.add_patch(FancyBboxPatch(
        (x, y + h - HEADER), w, HEADER, boxstyle="round,pad=0.010,rounding_size=1.4",
        linewidth=0, facecolor=color, alpha=0.14, zorder=3))
    ax.text(x + w / 2, y + h - HEADER / 2, title, ha="center", va="center",
            fontsize=title_size, fontweight="bold", color=color, zorder=4)
    body = "\n".join(textwrap.fill(line, wrap) for line in lines)
    ax.text(x + 1.0, y + h - HEADER - 2.4, body, ha="left", va="top",
            fontsize=body_size, color="#1f2937", linespacing=1.42, zorder=4)


def arrow(ax, p1, p2, color=GREY, lw=1.8, dashed=False, rad=0.0):
    ax.add_patch(FancyArrowPatch(
        p1, p2, arrowstyle="-|>", mutation_scale=15, linewidth=lw, color=color,
        linestyle="--" if dashed else "-", connectionstyle=f"arc3,rad={rad}", zorder=5))


# ---------------------------------------------------------------------------
# Figure 1 — RFC 1939 state machine
# ---------------------------------------------------------------------------
def fig_state_machine():
    fig = canvas(13.2, 6.6, "RFC 1939 POP3 finite state machine",
                 "Three sequential states, the commands valid in each, and the lock left behind when QUIT never arrives.")
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.845])
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

    box(ax, 0.6, 45, 16, 28, "CLOSED",
        ["No TCP session", "Mailbox not locked", "Listener on 110 / 995"],
        GREY, 10, 7.9, 24)
    box(ax, 20.5, 45, 21, 41, "1 · AUTHORIZATION",
        ["TCP handshake, greeting, then",
         "USER <name> · PASS <pw>",
         "APOP <name> <digest>",
         "STLS · CAPA · QUIT",
         "Server validates the credentials,",
         "locks the spool, replies +OK"],
        BLUE, 10, 7.9, 27)
    box(ax, 46, 45, 24, 41, "2 · TRANSACTION",
        ["Mailbox exclusively locked",
         "STAT · LIST · UIDL",
         "TOP <msg> <n>  headers only",
         "RETR <msg>  whole message",
         "DELE <msg>  flag only, in memory",
         "RSET · NOOP",
         "No disk change yet"],
        GREEN, 10, 7.9, 30)
    box(ax, 74, 45, 22.5, 41, "3 · UPDATE",
        ["Entered only after QUIT",
         "Expunge DELE-flagged messages",
         "Release the spool lock",
         "Reply +OK to QUIT",
         "Close the TCP connection"],
        PURPLE, 10, 7.9, 26)

    arrow(ax, (16.8, 59), (20.3, 59), BLUE)
    arrow(ax, (41.7, 65.5), (45.8, 65.5), GREEN)
    arrow(ax, (70.2, 65.5), (73.8, 65.5), PURPLE)

    # return path well below the cards
    arrow(ax, (85, 44.8), (85, 36), PURPLE)
    arrow(ax, (85, 36), (8.6, 36), PURPLE)
    arrow(ax, (8.6, 36), (8.6, 44.8), PURPLE)
    ax.text(13, 33.2, "clean teardown: UPDATE commits the deletions, releases the lock, returns to CLOSED",
            ha="left", fontsize=8.2, color=PURPLE)

    # labels live above the cards, clear of every body text block
    ax.text(18.5, 89.5, "TCP connect", ha="center", fontsize=8, color=BLUE)
    ax.text(43.8, 89.5, "+OK, lock held", ha="center", fontsize=8, color=GREEN)
    ax.text(72.0, 89.5, "QUIT", ha="center", fontsize=8, color=PURPLE)
    for x in (18.5, 43.8, 72.0):
        ax.plot([x, x], [88, 86.5], color="#cbd5e1", linewidth=0.8, zorder=1)

    # failure path
    ax.add_patch(FancyBboxPatch((46, 3), 50.5, 22,
                                boxstyle="round,pad=0.010,rounding_size=1.4",
                                linewidth=1.4, edgecolor=RED, facecolor="#fef2f2", zorder=2))
    ax.text(48, 21.5, "FAILURE PATH · link drops during TRANSACTION",
            fontsize=9.8, fontweight="bold", color=RED)
    ax.text(48, 18.2,
            "No QUIT → no UPDATE → the DELE flags roll back. The server keeps the spool lock and a\n"
            "half-open socket (TCP keepalive default 7200 s; operators often tune it to 600–1800 s).\n"
            "Every reconnect is answered  −ERR [IN-USE]  until that timer expires.",
            fontsize=8.1, color="#7f1d1d", linespacing=1.55, va="top")
    arrow(ax, (58, 44.8), (58, 25.2), RED, dashed=True)
    ax.text(59.2, 40.2, "abrupt disconnect, no FIN from the client", fontsize=8, color=RED)

    fig.savefig(FIG / "fig1_pop3_state_machine.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 2 — failure modes
# ---------------------------------------------------------------------------
def fig_failure_modes():
    fig = canvas(13.2, 6.2, "Why unmanaged POP3 fails on a 256 kbps / 450 ms branch link",
                 "Four independent failure modes; each is measured or derived in the report.")
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.83])
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

    cards = [
        ("1 · Monolithic RETR", BLUE, [
            "RFC 1939 has no per-part fetch: RETR sends headers, text and every attachment.",
            "Base64 turns a 3.00 MiB PDF into 4.11 MiB on the wire (+36.9 %).",
            "At 256 kbps that is ≈138 s of a link shared by the whole branch.",
        ]),
        ("2 · No resumption", RED, [
            "RETR has no byte-offset argument (contrast HTTP Range, RFC 7233).",
            "A drop at 41 % — as captured here — discards 781 kB and restarts at byte 0.",
            "Repeated flaps can trap a message in a re-download loop.",
        ]),
        ("3 · Exclusive lock", AMBER, [
            "TRANSACTION holds an exclusive spool lock (flock / dotlock).",
            "Without QUIT the lock outlives the dead session until keepalive expires.",
            "Reconnects get −ERR [IN-USE] for 10–30 min: a self-inflicted DoS.",
        ]),
        ("4 · Non-atomic delete", PURPLE, [
            "DELE only flags a message in memory; the disk changes in UPDATE.",
            "A severed session rolls the flags back, so the message is delivered again.",
            "Duplicates waste the scarcest resource on the link: airtime.",
        ]),
    ]
    for i, (title, color, lines) in enumerate(cards):
        x = 1.0 + i * 24.6
        box(ax, x, 30, 23.0, 50, title, lines, color, 10.6, 8.2, 32)

    fig.savefig(FIG / "fig2_failure_modes.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 3 — five-tier workflow as a layer stack
# ---------------------------------------------------------------------------
def fig_workflow():
    fig = canvas(13.2, 7.2, "Five-tier resilient email-access architecture",
                 "Each tier removes one dependency between the branch user and the impaired WAN.")
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.85])
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

    ax.text(2, 92, "TIER", fontsize=8, fontweight="bold", color=GREY)
    ax.text(21, 92, "WHAT RUNS AT THE BRANCH", fontsize=8, fontweight="bold", color=GREY)
    ax.text(68.5, 92, "WHAT CROSSES THE WAN", fontsize=8, fontweight="bold", color=GREY)

    rows = [
        ("Tier 1", "LAN isolation", BLUE,
         "MUA ↔ edge gateway on 192.168.10.0/24; the user reads and searches a local mailbox.",
         "no interactive WAN traffic"),
        ("Tier 2", "Header pre-fetch", GREEN,
         "Daemon issues UIDL then TOP <msg> 0, caching envelopes in SQLite keyed by UIDL.",
         "≈1 kB of headers per message"),
        ("Tier 3", "Attachment policy", AMBER,
         "Messages <100 kB sync immediately; larger parts stay at HQ and a stub is shown.",
         "headers only until the user clicks"),
        ("Tier 4", "Compression + TLS", PURPLE,
         "TLS 1.3 on :995 with gzip, SACK and tuned keepalives; retries ride out flaps.",
         "60–70 % fewer bytes, encrypted"),
        ("Tier 5", "Outbound spooling", RED,
         "Local Postfix accepts mail instantly and queues it with exponential backoff + jitter.",
         "batched when the link is healthy"),
    ]
    top, h, gap = 87, 11.8, 1.2
    for i, (tier, name, color, branch, wan) in enumerate(rows):
        y = top - (i + 1) * h - i * gap
        ax.add_patch(FancyBboxPatch((2, y), 96, h, boxstyle="round,pad=0.010,rounding_size=1.2",
                                    linewidth=1.1, edgecolor="#e2e8f0", facecolor="white", zorder=2))
        ax.add_patch(FancyBboxPatch((2, y), 2.2, h, boxstyle="round,pad=0.010,rounding_size=1.0",
                                    linewidth=0, facecolor=color, zorder=3))
        ax.text(6, y + h - 3.7, tier, fontsize=9.6, fontweight="bold", color=color)
        ax.text(6, y + h - 7.9, name, fontsize=7.8, color=GREY)
        ax.text(21, y + h / 2, textwrap.fill(branch, 62), fontsize=8.3,
                va="center", color="#1f2937", linespacing=1.4)
        ax.text(68.5, y + h / 2, textwrap.fill(wan, 34), fontsize=8.3,
                va="center", color=color, linespacing=1.4)

    ax.plot([19, 19], [23, 88], color="#e2e8f0", linewidth=1)
    ax.plot([67, 67], [23, 88], color="#e2e8f0", linewidth=1)

    # sequence strip
    ax.text(2, 19.5, "ONE MAIL CHECK, END TO END", fontsize=8, fontweight="bold", color=GREY)
    steps = [
        ("1", "MUA asks the\nlocal proxy", BLUE),
        ("2", "UIDL + TOP n 0\nover the WAN", GREEN),
        ("3", "Headers cached;\nstub for big parts", AMBER),
        ("4", "User clicks:\nqueued RETR", PURPLE),
        ("5", "Local MUA shows\nfull message", NAVY),
    ]
    for i, (n, label, color) in enumerate(steps):
        x = 2 + i * 19.3
        ax.add_patch(FancyBboxPatch((x, 2), 17.2, 11, boxstyle="round,pad=0.010,rounding_size=1.2",
                                    linewidth=1.2, edgecolor=color, facecolor="white", zorder=2))
        ax.text(x + 1.4, 9.6, n, fontsize=9, fontweight="bold", color=color)
        ax.text(x + 3.6, 7.8, label, fontsize=7.4, va="top", color="#1f2937", linespacing=1.3)
        if i < len(steps) - 1:
            arrow(ax, (x + 17.4, 7.5), (x + 19.1, 7.5), GREY, lw=1.2)

    fig.savefig(FIG / "fig3_workflow_architecture.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 4 — topology
# ---------------------------------------------------------------------------
def fig_topology():
    fig = canvas(13.2, 6.4, "Simulated topology and security zones",
                 "Branch edge proxy on the LAN, a rate-limited VSAT hop, and the HQ maildrop behind a stateful firewall.")
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.845])
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

    ax.add_patch(FancyBboxPatch((1, 14), 26, 68, boxstyle="round,pad=0.012,rounding_size=1.6",
                                linewidth=1.3, edgecolor=BLUE, facecolor="#eff6ff", zorder=1))
    ax.text(14, 77.5, "BRANCH · 192.168.10.0/24", ha="center", fontsize=9,
            fontweight="bold", color=BLUE)
    box(ax, 3.2, 53, 21.5, 20, "MUA 192.168.10.50",
        ["mail client", "sees only LAN latency"], BLUE, 9.6, 8.0, 26)
    box(ax, 3.2, 26, 21.5, 21, "Edge gateway .1",
        ["Fetchmail + Dovecot cache", "Postfix outbound spool"], GREEN, 9.6, 8.0, 26)
    arrow(ax, (14, 52.8), (14, 47.4), BLUE)
    ax.text(15.2, 49.8, "gigabit LAN, <1 ms", fontsize=7.6, color=BLUE)

    ax.add_patch(FancyBboxPatch((31, 26), 34, 40, boxstyle="round,pad=0.012,rounding_size=1.6",
                                linewidth=1.3, edgecolor=AMBER, facecolor="#fffbeb", zorder=1))
    ax.text(48, 62.5, "SATELLITE / VSAT HOP", ha="center", fontsize=9,
            fontweight="bold", color=AMBER)
    ax.text(48, 46,
            "256 kbps token bucket\n450 ms RTT  ·  5 % drop\nTLS 1.3 + gzip on :995",
            ha="center", va="center", fontsize=8.8, color="#78350f", linespacing=1.8)
    arrow(ax, (24.9, 36), (30.8, 36), AMBER, lw=2)
    arrow(ax, (65.2, 44), (70.8, 44), AMBER, lw=2)

    ax.add_patch(FancyBboxPatch((70, 14), 29, 68, boxstyle="round,pad=0.012,rounding_size=1.6",
                                linewidth=1.3, edgecolor=NAVY, facecolor=LIGHT, zorder=1))
    ax.text(84.5, 77.5, "HQ DATA CENTRE · 10.0.0.0/24", ha="center", fontsize=9,
            fontweight="bold", color=NAVY)
    box(ax, 72, 54, 25, 20, "Stateful firewall / DMZ",
        ["inbound: 995/tcp from the branch IP", "everything else denied"], RED, 9.6, 7.9, 34)
    box(ax, 72, 31, 25, 21, "Mail servers 10.0.0.25",
        ["Dovecot POP3/POP3S · Postfix :587", "spool 5,803,004 B / 5 messages"], NAVY, 9.6, 7.9, 34)
    box(ax, 72, 13, 25, 16, "IdP / OAuth 2.0 10.0.0.10",
        ["short-lived tokens + MFA"], PURPLE, 8.6, 7.6, 40)

    ax.text(1, 7,
            "Capture point: loopback interface of the lab host. The tabulated stream is the client-side leg "
            "(ephemeral port → 1110). The proxy terminates TCP locally, so the handshake is\n"
            "sub-millisecond; the 450 ms applies to the POP3 command/response turn, which the emulator "
            "delays by 225 ms in each direction.",
            fontsize=7.9, color=GREY, va="top", linespacing=1.55)

    fig.savefig(FIG / "fig4_topology.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 5 — measured transfer timeline
# ---------------------------------------------------------------------------
def fig_capture_timeline():
    rows = subprocess.run(
        ["tshark", "-r", str(CAP), "-Y", "tcp.stream==0 && tcp.len>0",
         "-T", "fields", "-e", "frame.time_relative", "-e", "tcp.len"],
        capture_output=True, text=True, check=True).stdout.strip().splitlines()
    t, cum = [], []
    total = 0
    for row in rows:
        ts, ln = row.split("\t")
        ts, ln = float(ts), int(ln)
        if ts < 3.0:
            continue
        total += ln
        t.append(ts)
        cum.append(total / 1e6)

    fig = canvas(11.6, 5.6, "Measured RETR 4 transfer before the link blackout",
                 "1.89 MB message over a 256 kbps shaper, cut after 781 kB. Time is relative to the start of the capture.")
    ax = fig.add_axes([0.085, 0.15, 0.88, 0.64])
    ax.plot(t, cum, color=BLUE, linewidth=1.6, label="payload delivered (cumulative)")
    ax.axhline(1.887, color=GREY, linestyle=":", linewidth=1.2)
    ax.text(3.2, 1.92, "message size 1.887 MB", fontsize=8.4, color=GREY)
    ax.axvline(27.607, color=RED, linestyle="--", linewidth=1.2)
    ax.annotate("link blackout\n781 kB · 41.4 %", xy=(27.607, 0.78), xytext=(17.5, 1.30),
                fontsize=8.6, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))
    ax.plot([27.607, 62.2], [0.781, 1.887], color=AMBER, linestyle="--", linewidth=1.3,
            label="projected remainder at 256 kbps (≈62 s total)")
    ax.set_xlabel("capture time (s)")
    ax.set_ylabel("data delivered to the client (MB, 10⁶ bytes)")
    ax.set_xlim(0, 66); ax.set_ylim(0, 2.1)
    ax.grid(alpha=0.25, linestyle=":")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=8.4, loc="lower right")
    ax.text(0.99, 0.93,
            f"measured throughput: {SUMMARY['retr_kbps']:.1f} kbps of a 256 kbps line",
            transform=ax.transAxes, ha="right", fontsize=8.2, color=GREY)
    fig.savefig(FIG / "fig5_capture_timeline.png", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    fig_state_machine()
    fig_failure_modes()
    fig_workflow()
    fig_topology()
    if CAP.exists() and subprocess.run(["which", "tshark"], capture_output=True).returncode == 0:
        fig_capture_timeline()
    print("figures written to", FIG)
