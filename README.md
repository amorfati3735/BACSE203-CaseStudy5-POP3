# BACSE203 — Computer Networks · Case Study 5
## POP3 Mailbox Access in a Low-Bandwidth Branch

**School of Computer Science and Engineering (SCOPE), Vellore Institute of Technology**  
Class ID `VL2026270101688` (B2 + TB2) · Fall Semester 2026–27

The final deliverable is **[`FINAL_REPORT.md`](./FINAL_REPORT.md)** — the complete report in the official template order, with five figures, ten tables, IEEE-style references and a reproducible experiment. Convert it to DOCX with `pandoc` (see below).

---

## What the case study shows

A branch on a 256 kbps satellite link with 450 ms RTT and 5 % loss cannot use POP3 as designed:

| Finding | Value |
| :--- | :--- |
| Base64 inflation of a 3 MiB PDF | 4.11 MiB on the wire (+36.84 %), ≈138 s at 256 kbps |
| TCP throughput at 5 % loss (Mathis) | ≈116 kbps, 45 % of line rate → 4.30 MB needs ≈297 s |
| Measured `RETR 4` throughput in the lab | 255.0 kbps |
| Link blackout in the run | after 781 kB = 41.4 % of the message |
| Header-only `TOP 4 0` reply | **366 bytes** (99.98 % less than `RETR`) |
| Error after reconnect | `-ERR [IN-USE] Mailbox is locked by another session!` |

The proposed five-tier workflow moves the interactive path onto the branch LAN and leaves the WAN with small, compressed, encrypted and deferrable traffic.

---

## Repository layout

```
FINAL_REPORT.md              the deliverable
figures/                     5 figures, regenerated from the measured data
captures/
  pop3_wan_capture.pcapng    1,239-packet capture from the real lab run
  run_summary.json           machine-readable results
simulation/
  pop3_wan_lab.py            POP3 server + 256 kbps / 450 ms emulator + failure injection
  make_figures.py            regenerates every figure from the capture and summary
  make_windows_screenshots.py  drives the Wireshark GUI (pywinauto) to re-take the evidence set
screenshots/
  win01–win04                full-screen Wireshark 4.6 (Windows) evidence set — see below
  lab01–lab05                original run's screenshots, kept for provenance
docs/
  BACSE203 case study brief  assignment and rubric
  Case Study CN template     official DOCX template
  Team work-split charter    role allocation and viva questions
  TEAM_AGENT_HANDOFF.md      per-member briefs (numbers superseded — see note)
  AGENT_PROGRESS_LOG.md      project history, including the audit in Turn 16
archive/superseded/          earlier drafts and their evidence, kept for provenance
```

---

## Reproduce the experiment

Requirements: Python 3, `tshark` (Wireshark CLI). No root, no packages beyond the standard library.

```bash
python3 simulation/pop3_wan_lab.py        # runs the lab and writes captures/
python3 simulation/make_figures.py        # regenerates figures/
```

Inspect the capture in Wireshark: open `captures/pop3_wan_capture.pcapng`, then
**Decode As → TCP port 1110 → POP**, and filter `tcp.port == 1110`.

On the command line:

```bash
tshark -r captures/pop3_wan_capture.pcapng -d tcp.port==1110,pop -Y "tcp.port==1110"
```

The lab emulates the link at the application level: 225 ms one-way delay per control turn (≈450 ms POP3 RTT) and a 256 kbps token bucket on the data path. The TCP handshake itself terminates on loopback, so it is sub-millisecond; the report states this limitation explicitly.

### Wireshark evidence screenshots

`screenshots/win01–win04` are full-screen captures of the Wireshark 4.6 GUI analyzing `captures/pop3_wan_capture.pcapng`, produced by GUI automation (`simulation/make_windows_screenshots.py`, needs `pip install pywinauto pillow`):

| Screenshot | View | Verified against |
| :--- | :--- | :--- |
| `win01_pop_dialogue.png` | `pop` display filter — the decoded USER/PASS/STAT/LIST/UIDL/TOP/RETR exchange | status bar: Displayed 556 (= `tshark -Y pop`) |
| `win02_syn_handshake.png` | `tcp.flags.syn == 1 && tcp.port == 1110` — both sessions' handshakes | Displayed 4 |
| `win03_follow_stream_session1_retr_blackout.png` | Follow TCP Stream, stream 0 — login, `TOP 4 0`, `RETR 4` cut off at 41.4 % | dialog text contains `RETR` |
| `win04_follow_stream_session2_lockout.png` | Follow TCP Stream, stream 2 — reconnect rejected | dialog text contains `IN-USE` |

---

## Produce the DOCX

```bash
pandoc FINAL_REPORT.md -o "Case Study 5 - POP3 Mailbox Access in a Low-Bandwidth Branch.docx" \
  --reference-doc="docs/Case Study CN - Template-final (1).docx"
```

Fill in the team table, the instructor name and the team number before submission. The pandoc output embeds all five figures.

---

## Team split

| Member | Role | Owns |
| :--- | :--- | :--- |
| 25BCE0344 · Arunya Srivastava | Protocol theory and report preparation | §1 overview, §6.1 (a) protocol and limitations |
| 25BCE0401 · Adarsh Kumar Singh | Workflow design | §4.2 transport model, §5.4 and §6.2 (b) workflow |
| 25BCE0337 · Pratik Ambastha | Simulation and packet analysis | §5.1–5.3 lab, capture and frame evidence |
| 25BCE0998 · Pranjal Paul | Security analysis | §4.5, §6.3 (c) threats and hardening |
| 25BCE2004 · Bhavya Singh | Standards and references | §2, §3, §4.1, §5.5, §7, §8 |
| 25BBS0046 · Shriyansh Gangwar | Testing and documentation | verification, formatting and proofreading |

> **Note on `docs/TEAM_AGENT_HANDOFF.md`:** the per-member prompts were written before the experiment was rebuilt. They quote 820 bytes for `TOP`, 147 s for the 3 MB transfer, a 3.15 MB spool and a "Dovecot" banner produced by a mock server. The authoritative values are **366 bytes**, **≈138 s**, **5,803,004 B (5.53 MiB)** and a **lab POP3 server**; see `FINAL_REPORT.md` §5.3.

Prepared for academic assessment. All external sources are cited with access dates in §8.
