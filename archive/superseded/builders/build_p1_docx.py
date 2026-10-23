#!/usr/bin/env python3
"""
build_p1_docx.py
Generates the comprehensive, standalone Word document for Person 1 (P1):
'Case Study 5 - Person 1 - Protocol Theory & Limitations.docx'
Complete with all text, tables, and embedded high-resolution diagrams.
"""

import os
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_shading(cell, color_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def format_cell(cell, text, bold=False, italic=False, size_pt=10.5, font_name="Times New Roman", align=WD_ALIGN_PARAGRAPH.LEFT):
    p = cell.paragraphs[0]
    p.text = ''
    p.alignment = align
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(text)
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    return run

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(14)
    run.bold = True
    run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(13)
    run.bold = True
    run.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
    return p

def add_heading_3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(9)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run.bold = True
    run.italic = True
    run.font.color.rgb = RGBColor(0x0D, 0x94, 0x88)
    return p

def add_body_p(doc, text, bold_prefix=None, italic_prefix=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_bold = p.add_run(bold_prefix)
        r_bold.font.name = "Times New Roman"
        r_bold.font.size = Pt(12)
        r_bold.bold = True
    if italic_prefix:
        r_it = p.add_run(italic_prefix)
        r_it.font.name = "Times New Roman"
        r_it.font.size = Pt(12)
        r_it.italic = True
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    return p

def add_bullet_p(doc, text, bold_prefix=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent = Inches(0.3)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    r_bullet = p.add_run("•  ")
    r_bullet.font.name = "Times New Roman"
    r_bullet.font.size = Pt(12)
    r_bullet.bold = True
    if bold_prefix:
        r_bold = p.add_run(bold_prefix)
        r_bold.font.name = "Times New Roman"
        r_bold.font.size = Pt(12)
        r_bold.bold = True
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    return p

def add_image_with_caption(doc, image_path, caption_text, width_inches=6.2):
    if os.path.exists(image_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(10)
        p_img.paragraph_format.space_after = Pt(4)
        run = p_img.add_run()
        run.add_picture(image_path, width=Inches(width_inches))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(0)
        p_cap.paragraph_format.space_after = Pt(10)
        p_cap.paragraph_format.keep_with_next = True
        r_cap = p_cap.add_run(f"Figure: {caption_text}")
        r_cap.font.name = "Times New Roman"
        r_cap.font.size = Pt(10)
        r_cap.italic = True
        r_cap.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

def main():
    doc = docx.Document()

    # Set page layout to standard A4 with 1-inch margins
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

    # -------------------------------------------------------------------------
    # COVER / TITLE BLOCK
    # -------------------------------------------------------------------------
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run("SCHOOL OF COMPUTER SCIENCE AND ENGINEERING (SCOPE)\nCOMPUTER NETWORKS (BACSE203)")
    r_inst.font.name = "Arial"
    r_inst.font.size = Pt(13)
    r_inst.bold = True
    r_inst.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(6)
    p_title.paragraph_format.space_after = Pt(2)
    r_title = p_title.add_run("CASE STUDY REPORT: PERSON 1 MODULE")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(16)
    r_title.bold = True

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(14)
    r_sub = p_sub.add_run("Topic: POP3 Protocol Architecture, Operational Mechanics & Technical Limitations\nFall Semester 2026–27")
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(11)
    r_sub.italic = True
    r_sub.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    # Metadata Table
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.style = 'TableGrid'
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    meta_fields = [
        ("Case Study Number", "Case Study 5"),
        ("Case Study Title", "POP3 Mailbox Access in a Low-Bandwidth Branch"),
        ("Assigned Member & Role", "Person 1 — Lead Protocol Analyst & FSM Architect"),
        ("Sections Completed", "Section 1 (Case Study Overview) & Section 6.1 (Question a)")
    ]
    for i, (k, v) in enumerate(meta_fields):
        cell_k = meta_table.rows[i].cells[0]
        cell_v = meta_table.rows[i].cells[1]
        set_cell_shading(cell_k, "F1F5F9")
        set_cell_margins(cell_k, 70, 70, 100, 100)
        set_cell_margins(cell_v, 70, 70, 100, 100)
        format_cell(cell_k, k, bold=True, size_pt=10.5)
        format_cell(cell_v, v, bold=False, size_pt=10.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # -------------------------------------------------------------------------
    # SECTION 1: CASE STUDY OVERVIEW
    # -------------------------------------------------------------------------
    add_heading_1(doc, "1. Case Study Overview")

    add_heading_2(doc, "1.1 Background")
    add_body_p(doc,
        "Modern enterprise communications increasingly encompass remote, geographically isolated branch facilities such as "
        "offshore drilling platforms, mining extraction sites, maritime transport vessels, regional logistics warehouses, and rural "
        "healthcare outposts. These branch locations are physically constrained by their Wide Area Network (WAN) backhaul links—most "
        "notably geostationary satellite (VSAT) connections, narrowband cellular links (3G/4G), or high-latency wireless microwave links. "
        "In these environments, total available bandwidth is strictly capped (typically between 64 kbps and 512 kbps), round-trip "
        "propagation delay (RTT) is elevated (spanning 450 ms to 800 ms), and link availability is intermittent due to rain fade, atmospheric "
        "interference, and satellite orbital handoffs.")

    add_body_p(doc,
        "Despite these adverse transport characteristics, electronic mail remains the operational backbone for enterprise coordination, "
        "carrying safety protocols, supply-chain documentation, engineering manifests, and administrative orders. Historically, "
        "branches deployed the Post Office Protocol Version 3 (POP3), formalized in RFC 1939, to allow branch Mail User Agents (MUAs) "
        "to pull incoming messages from a central enterprise mail server located at corporate headquarters (HQ). However, while POP3 "
        "was architected in the 1980s and 1990s for intermittent dial-up terminal sessions, its design assumptions diverge sharply "
        "from the requirements of modern, attachment-heavy email traffic across high-latency, loss-prone satellite links.")

    add_heading_2(doc, "1.2 Problem Statement")
    add_body_p(doc,
        "The technical problem investigated in this case study is the fundamental protocol incompatibility between legacy POP3 "
        "mailbox retrieval and the physical constraints of low-bandwidth, intermittent WAN connections. The operational failure modes "
        "manifest across four specific areas:")
    
    add_bullet_p(doc,
        "POP3 treats every email as an indivisible monolithic payload. When a user requests an email, the server streams the entire "
        "message body along with all Base64-encoded MIME attachments. A single 3 MB attachment inflates to 4.11 MB on the wire, monopolizing "
        "the 256 kbps WAN connection for over two minutes and blocking all concurrent operational traffic.",
        bold_prefix="Monolithic Payload Retrieval: ")

    add_bullet_p(doc,
        "POP3 lacks any byte-range offset resumption mechanism (unlike HTTP Range headers). If an intermittent satellite connection "
        "drops at 95% of a 4 MB file download, the TCP session aborts, the client discards the partial bytes, and upon reconnecting, "
        "POP3 restarts the transfer from byte zero, creating infinite re-download loops.",
        bold_prefix="Lack of Offset Resumption: ")

    add_bullet_p(doc,
        "During the POP3 Transaction phase, the server places an exclusive lock on the mail spool. When a link severs abruptly without "
        "a clean TCP FIN/RST handshake, the server retains a half-open TCP socket. The mailbox remains locked until server-side keepalive "
        "timers expire (15–30 minutes), rejecting subsequent user logins with '-ERR [IN-USE] Mailbox is locked'.",
        bold_prefix="Exclusive Mailbox Locking & Denial of Service: ")

    add_bullet_p(doc,
        "POP3 deletion commands (DELE) are non-atomic and staged only in volatile server memory. Deletions are only permanently committed "
        "during the UPDATE state upon receiving a clean QUIT. When intermittent links sever mid-session, the server rolls back all staged "
        "deletions, causing the client to re-download identical messages upon reconnection, flooding the inbox.",
        bold_prefix="Non-Atomic Deletion Rollback & Duplicate Mail Flooding: ")

    add_heading_2(doc, "1.3 Objectives of the Case Study")
    add_body_p(doc, "This case study pursues five specific academic and technical objectives:")
    add_bullet_p(doc, "Analyze the finite state machine (FSM), command syntax, and protocol transitions of POP3 under RFC 1939 specifications.", bold_prefix="Objective 1: ")
    add_bullet_p(doc, "Investigate transport-layer (TCP) and application-layer failure dynamics across high-latency, loss-prone satellite WAN links.", bold_prefix="Objective 2: ")
    add_bullet_p(doc, "Architect an optimized, bandwidth-efficient email access workflow integrating local caching, header pre-fetching via TOP, and compression.", bold_prefix="Objective 3: ")
    add_bullet_p(doc, "Assess security and reliability risks of legacy mail access (cleartext exposure, APOP MD5 collision vulnerabilities, lack of MFA).", bold_prefix="Objective 4: ")
    add_bullet_p(doc, "Provide empirical evidence through Wireshark packet capture trace disassembly and Python socket protocol emulation.", bold_prefix="Objective 5: ")

    add_heading_2(doc, "1.4 Scope of Study")
    add_body_p(doc,
        "The scope of this report is explicitly defined across technical and operational boundaries:",
        italic_prefix="Delineation of Scope: ")
    add_bullet_p(doc, "Application-layer mail retrieval protocols (POP3, POP3S, IMAP4rev1); MIME Base64 overhead; TCP congestion window behavior across high-latency links; protocol state transitions; and mailbox locking mechanisms.", bold_prefix="In-Scope: ")
    add_bullet_p(doc, "Physical-layer satellite RF transceiver alignment; orbital transponder forward error correction (FEC) hardware engineering; proprietary Microsoft Exchange MAPI/ActiveSync internals; and desktop client GUI source code development.", bold_prefix="Out-of-Scope: ")

    add_heading_2(doc, "1.5 Key Networking Concepts (Module 5 Mapping)")
    add_body_p(doc,
        "This case study synthesizes and demonstrates core networking concepts from Module 5 of the BACSE203 Computer Networks curriculum:")
    add_bullet_p(doc, "Client-server architecture, stateful protocol transitions, command-response token exchange (+OK, -ERR), and ASCII stream parsing.", bold_prefix="Application Layer Paradigms: ")
    add_bullet_p(doc, "Separation of Mail User Agents (MUAs), Mail Transfer Agents (MTAs - SMTP push), and Mail Delivery/Access Agents (MDAs - POP3 pull).", bold_prefix="Electronic Mail Architecture: ")
    add_bullet_p(doc, "RFC 2045 Base64 encoding mechanics converting 3 binary octets into 4 ASCII characters, resulting in a mandatory 33.3% raw mathematical data expansion (~37% with CRLF wrapping).", bold_prefix="MIME Encoding & Data Overhead: ")
    add_bullet_p(doc, "TCP three-way handshake, TCP Slow Start, Retransmission Timeouts (RTO), and the severe throughput collapse of TCP Cubic over high Bandwidth-Delay Product (BDP) links with packet drop.", bold_prefix="Transport Layer Dynamics: ")
    add_bullet_p(doc, "Transport Layer Security (TLS 1.3), cipher suites (AES-256-GCM), public-key digital certificates, and Simple Authentication and Security Layer (SASL) OAuth2 token integration.", bold_prefix="Network Security & Cryptography: ")

    # -------------------------------------------------------------------------
    # SECTION 6.1: QUESTION (a) — EXPLAIN POP3 AND ITS LIMITATIONS
    # -------------------------------------------------------------------------
    add_heading_1(doc, "2. Question (a): Explain POP3 and Its Limitations")

    add_heading_2(doc, "2.1 POP3 Protocol Architecture & Operational Mechanics (RFC 1939)")
    add_body_p(doc,
        "Post Office Protocol Version 3 (POP3), standardized in RFC 1939 by the Internet Engineering Task Force (IETF), is an "
        "application-layer client-server protocol engineered to allow an endpoint workstation (Mail User Agent - MUA) to interrogate "
        "and retrieve messages spooled inside a remote user maildrop. POP3 operates over the Transmission Control Protocol (TCP) on "
        "well-known port 110 (or dedicated port 995 for cryptographically encapsulated POP3S).")

    add_body_p(doc,
        "POP3 is designed as a text-based, stateful, command-response protocol. The client sends four-character ASCII command verbs "
        "terminated by a Carriage Return / Line Feed (CRLF) sequence. In response, the server issues a single-line status indicator: "
        "either '+OK' indicating successful command execution, or '-ERR' indicating a syntax, authentication, or state violation.")

    # Embed Diagram 1: State Machine
    add_image_with_caption(doc, "pop3_state_machine.png", "POP3 Protocol Finite State Machine (RFC 1939) showing Authorization, Transaction, and Update phases.")

    add_heading_2(doc, "2.2 The Three-Phase Finite State Machine Lifecycle")
    add_body_p(doc,
        "Under RFC 1939, a POP3 session transitions sequentially through three distinct operational states, bounded by initial and final CLOSED states:")

    add_heading_3(doc, "State 1: AUTHORIZATION")
    add_body_p(doc,
        "The session initiates when the client completes a standard TCP three-way handshake on port 110. The server responds with a greeting "
        "banner (e.g., '+OK Dovecot ready'). At this stage, the session enters the AUTHORIZATION state. The client must identify itself and "
        "provide valid authentication credentials before gaining access to the maildrop.")
    add_bullet_p(doc, "Specifies the plaintext username of the mailbox account.", bold_prefix="USER <username>: ")
    add_bullet_p(doc, "Supplies the unencrypted password string immediately following a successful USER command.", bold_prefix="PASS <password>: ")
    add_bullet_p(doc, "An optional challenge-response command where the client hashes a server-provided timestamp with a shared secret using MD5, avoiding plaintext transmission.", bold_prefix="APOP <name> <digest>: ")
    add_bullet_p(doc, "Aborts the session immediately and returns the TCP connection to the CLOSED state without inspecting mail.", bold_prefix="QUIT: ")
    add_body_p(doc,
        "Transition Condition: Once credentials are authenticated successfully, the server acquires an exclusive lock (flock/dotlock) "
        "on the user's mailbox spool, replies with '+OK Logged in', and transitions the session into the TRANSACTION state.")

    add_heading_3(doc, "State 2: TRANSACTION")
    add_body_p(doc,
        "In the TRANSACTION state, the client queries mailbox contents, reads messages, and marks items for removal. The server maildrop "
        "is exclusively locked to prevent external alterations by incoming MTAs or concurrent sessions.")
    add_bullet_p(doc, "Returns positive status followed by two integers: total message count and aggregate mailbox size in octets (bytes).", bold_prefix="STAT: ")
    add_bullet_p(doc, "Lists message numbers alongside their individual octet sizes. Can be queried for a single message or the entire spool.", bold_prefix="LIST [msg]: ")
    add_bullet_p(doc, "Instructs the server to transmit the entire specified message (headers, body, and all MIME multi-part attachments) as a multi-line data stream terminated by a single dot on a line (CRLF.CRLF).", bold_prefix="RETR <msg>: ")
    add_bullet_p(doc, "Optional command that transmits all RFC 822/MIME headers plus the top 'n' lines of the message body. This command is pivotal for bandwidth-saving header inspection.", bold_prefix="TOP <msg> <lines>: ")
    add_bullet_p(doc, "Returns unique, persistent alphanumeric identifier strings assigned to messages, allowing MUAs to track messages across distinct sessions.", bold_prefix="UIDL [msg]: ")
    add_bullet_p(doc, "Flags the specified message for deletion. Crucially, the message is NOT deleted from disk during this state; it is merely flagged in server volatile memory.", bold_prefix="DELE <msg>: ")
    add_bullet_p(doc, "Resets session state, unmarking all messages previously flagged by DELE during the active session.", bold_prefix="RSET: ")
    add_bullet_p(doc, "No-operation keepalive probe; server simply responds with '+OK'.", bold_prefix="NOOP: ")

    add_heading_3(doc, "State 3: UPDATE")
    add_body_p(doc,
        "The UPDATE state is entered exclusively when the client transmits the QUIT command while in the TRANSACTION state. In this state, "
        "the server commits all staged session modifications:")
    add_bullet_p(doc, "The server physically deletes and unlinks from the file system all messages marked with the DELE flag.", bold_prefix="Permanent Message Purging: ")
    add_bullet_p(doc, "The server releases the exclusive dotlock/fcntl file lock on the maildrop, allowing other delivery agents to access the spool.", bold_prefix="Lock Release: ")
    add_bullet_p(doc, "The server transmits a farewell status banner ('+OK Dovecot logging out') and closes the TCP transport socket.", bold_prefix="Connection Teardown: ")
    add_body_p(doc,
        "Abnormal Termination Behavior: If a network disconnection, timeout, or link failure occurs before the QUIT command is processed, "
        "the session NEVER enters the UPDATE state. The server automatically rolls back all staged DELE flags, preserving all original messages.",
        italic_prefix="Critical FSM Rule: ")

    # Embed Diagram 2: Bottlenecks
    add_image_with_caption(doc, "pop3_bottlenecks.png", "Architectural Failure Modes of POP3 across Bandwidth-Constrained WAN Links.")

    add_heading_2(doc, "2.3 In-Depth Analysis of POP3 Technical Limitations")
    add_body_p(doc,
        "While POP3 provided an effective lightweight solution for early 1990s dial-up personal computing, its architectural design "
        "exhibits fatal technical limitations when subjected to modern enterprise traffic over low-bandwidth, high-latency WAN links:")

    add_heading_3(doc, "Limitation 1: Monolithic Message Retrieval (Absence of MIME Granularity)")
    add_body_p(doc,
        "POP3's RETR command is strictly non-selective: it streams the complete message payload in a single, uninterrupted transmission. "
        "POP3 has no protocol mechanism to parse MIME boundaries server-side or download body text while omitting binary attachments. "
        "Because legacy email transport is restricted to 7-bit ASCII, binary attachments (PDFs, spreadsheets, images) must be encoded "
        "via Base64 under RFC 2045. Base64 maps 3 binary bytes (24 bits) into 4 ASCII characters (32 bits), introducing an inherent 33.33% "
        "mathematical data expansion. When MIME boundary delimiters and mandatory CRLF line wraps (every 76 characters) are added, the effective "
        "expansion reaches ~37%. On a 256 kbps link (effective throughput ~28 KB/s), a single 3 MB PDF inflates to 4.11 MB, monopolizing "
        "the line for 147 seconds and causing severe Head-of-Line (HoL) blocking for all other business communications.")

    add_heading_3(doc, "Limitation 2: Lack of Byte-Range Offset Resumption")
    add_body_p(doc,
        "Unlike HTTP/1.1 (which supports the 'Range: bytes=start-end' header under RFC 7233) or FTP (which provides the REST offset command), "
        "POP3 RETR provides no offset parameters. If an intermittent satellite connection severs at 95% of a 4 MB download, the underlying "
        "TCP session terminates. The client MUA receives no valid message, and the server commits no state. Upon reconnecting, the MUA has "
        "no choice but to re-issue RETR and download the entire 4 MB payload from byte zero. In environments with frequent link flaps "
        "(Mean Time Between Failures < 3 minutes), large messages can become trapped in an infinite re-download loop that continuously "
        "exhausts satellite data allowances without ever reaching the user's inbox.")

    add_heading_3(doc, "Limitation 3: Exclusive Mailbox Locking & Denial of Service")
    add_body_p(doc,
        "RFC 1939 mandates that upon successful authentication, the server daemon must acquire an exclusive lock (flock, fcntl, or dotlock) "
        "on the user's mail spool to guarantee transactional consistency. When an intermittent WAN connection abruptly drops, the remote "
        "workstation cannot send the TCP FIN or RST packets needed for an orderly socket teardown. Consequently, the HQ mail server retains "
        "the orphaned half-open TCP connection in the TCP_ESTABLISHED state, keeping the exclusive lock engaged. The lock is only released "
        "when the operating system's TCP keepalive timer (defaulting to 7200 seconds / 2 hours, or tuned to 15–30 minutes) detects a dead peer. "
        "If the branch link recovers and the user attempts to re-authenticate, the server immediately rejects the session with "
        "'-ERR [IN-USE] Mailbox is locked by another session', creating an artificial denial of service that paralyzes branch productivity.")

    add_heading_3(doc, "Limitation 4: Non-Atomic Deletions & Duplicate Mail Storms")
    add_body_p(doc,
        "The strict separation between the TRANSACTION state and the UPDATE state means that issuing DELE marks messages for removal "
        "only in temporary server memory. Disk unlinking occurs exclusively upon processing QUIT. When a WAN connection abruptly drops "
        "after a client has successfully downloaded an email but before QUIT is acknowledged, the server executes a full rollback of all "
        "deletion flags to prevent message loss. Upon the next connection, the server re-offers the identical emails that the user already "
        "retrieved. The client MUA re-downloads these messages, generating duplicate emails in the local inbox and consuming redundant WAN bandwidth.")

    add_heading_3(doc, "Limitation 5: Client Storage Single Point of Failure & Flag Synchronization Failure")
    add_body_p(doc,
        "POP3 was conceived around a 'download-and-delete' operational paradigm where messages are transferred to local client storage "
        "(e.g., an Outlook .PST or Thunderbird Mbox file) and purged from the central server. If a branch desktop experiences a local hard "
        "drive failure or database corruption, all historical enterprise correspondence is permanently destroyed without centralized backup. "
        "Furthermore, if users configure 'leave messages on server', POP3 lacks message state flags (Read, Unread, Answered, Flagged). Flags "
        "are tracked only within the local MUA client, causing divergent, conflicting mailbox views across multiple devices (e.g., smartphone vs workstation).")

    add_heading_3(doc, "Limitation 6: Transport-Layer TCP Performance Degradation")
    add_body_p(doc,
        "Standard TCP congestion control algorithms (such as TCP Reno and Cubic) interpret dropped packets as evidence of buffer overflow "
        "rather than wireless or satellite bit corruption. Over a geostationary satellite link with an RTT of 500 ms and a 5% random packet "
        "drop rate, the Mathis throughput formula (T <= (MSS / RTT) * (1 / sqrt(p))) limits effective TCP throughput to less than 20% of "
        "the theoretical link capacity. Because POP3 enforces a synchronous, lock-step command-response exchange (each command requires a "
        "full 500 ms round trip to receive +OK), the protocol experiences severe latency penalties before payload transmission even begins.")

    # -------------------------------------------------------------------------
    # REFERENCES
    # -------------------------------------------------------------------------
    add_heading_1(doc, "3. References & Academic Citations")
    
    refs = [
        ("Myers, J., & Rose, M. (1996). ", "RFC 1939: Post Office Protocol - Version 3. ", "Internet Engineering Task Force (IETF). https://datatracker.ietf.org/doc/html/rfc1939 (Accessed: Oct 2026)"),
        ("Freed, N., & Borenstein, N. (1996). ", "RFC 2045: Multipurpose Internet Mail Extensions (MIME) Part One: Format of Internet Message Bodies. ", "IETF. https://datatracker.ietf.org/doc/html/rfc2045 (Accessed: Oct 2026)"),
        ("Newman, C. (1999). ", "RFC 2595: Using TLS with IMAP, POP3 and ACAP. ", "Internet Engineering Task Force (IETF). https://datatracker.ietf.org/doc/html/rfc2595 (Accessed: Oct 2026)"),
        ("Crispin, M. (2003). ", "RFC 3501: Internet Message Access Protocol - Version 4rev1. ", "Internet Engineering Task Force (IETF). https://datatracker.ietf.org/doc/html/rfc3501 (Accessed: Oct 2026)"),
        ("Kurose, J. F., & Ross, K. W. (2021). ", "Computer Networking: A Top-Down Approach (8th ed.). ", "Pearson. Chapter 2: Application Layer (Electronic Mail in the Internet, pp. 120-136)."),
        ("Stallings, W. (2017). ", "Data and Computer Communications (10th ed.). ", "Pearson. Chapter 24: Electronic Mail and Directory Service, pp. 782-805.")
    ]
    for auth, tit, pub in refs:
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.left_indent = Inches(0.4)
        p_ref.paragraph_format.first_line_indent = Inches(-0.4)
        p_ref.paragraph_format.space_before = Pt(0)
        p_ref.paragraph_format.space_after = Pt(4)
        p_ref.paragraph_format.line_spacing = 1.15
        
        r1 = p_ref.add_run(auth)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(11)
        r2 = p_ref.add_run(tit)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(11)
        r2.italic = True
        r3 = p_ref.add_run(pub)
        r3.font.name = "Times New Roman"
        r3.font.size = Pt(11)

    output_path = "Case Study 5 - Person 1 - Protocol Theory & Limitations.docx"
    print(f"Saving Person 1 Word Document to: {output_path}...")
    doc.save(output_path)
    print("Person 1 Word Document created successfully!")

if __name__ == "__main__":
    main()
