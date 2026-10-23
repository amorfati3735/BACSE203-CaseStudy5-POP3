#!/usr/bin/env python3
"""
generate_team_charter_pdf.py
Generates an executive, beautifully styled PDF Team Work-Split Charter
for BACSE203 Computer Networks - Case Study 5.
"""

import sys
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Canvas that adds running header and 'Page X of Y' footer."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#475569"))
        
        # Running Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(36, 810, "BACSE203: Computer Networks — Case Study 5 Team Execution Charter")
            self.drawRightString(559, 810, "POP3 Mailbox Access in Low-Bandwidth Branch")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.75)
            self.line(36, 804, 559, 804)
        
        # Running Footer (all pages)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.75)
        self.line(36, 38, 559, 38)
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(36, 26, "Confidential — For Internal Team Distribution Only • Target: 100/100 Marks")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(559, 26, page_str)
        self.restoreState()

def build_pdf(filename="Case_Study_5_Team_Work_Split_Charter.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    # Define bespoke palette
    c_primary = colors.HexColor("#0F172A")    # Deep Navy Slate
    c_accent = colors.HexColor("#0284C7")     # Sky Blue Accent
    c_teal = colors.HexColor("#0D9488")       # Deep Teal
    c_dark = colors.HexColor("#1E293B")       # Dark Charcoal
    c_muted = colors.HexColor("#475569")      # Slate
    c_bg_light = colors.HexColor("#F8FAFC")   # Off-white / Ice Grey
    c_card_bg = colors.HexColor("#F1F5F9")    # Light Card
    c_border = colors.HexColor("#E2E8F0")     # Light Border
    c_gold = colors.HexColor("#D97706")       # Amber Accent

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_primary,
        alignment=0,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=c_accent,
        alignment=0,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=c_teal,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_dark,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=c_dark,
        leftIndent=14,
        spaceAfter=3
    )

    badge_style = ParagraphStyle(
        'Badge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    tbl_header_style = ParagraphStyle(
        'TblHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )

    tbl_cell_bold = ParagraphStyle(
        'TblCellB',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=c_primary
    )

    tbl_cell_text = ParagraphStyle(
        'TblCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_dark
    )

    callout_title = ParagraphStyle(
        'CalloutT',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#92400E")
    )

    callout_body = ParagraphStyle(
        'CalloutB',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#78350F")
    )

    story = []

    # =========================================================================
    # HEADER BANNER & TITLE
    # =========================================================================
    banner_data = [
        [
            Paragraph("<b>VELLORE INSTITUTE OF TECHNOLOGY</b> • School of Computer Science & Engineering (SCOPE)<br/>"
                      "<b>BACSE203: Computer Networks</b> • Fall Semester 2026–27 • Class ID: VL2026270101686 / 1688", 
                      ParagraphStyle('Banner', fontName='Helvetica-Bold', fontSize=8, leading=11, textColor=colors.HexColor("#475569")))
        ]
    ]
    banner_table = Table(banner_data, colWidths=[523])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("CASE STUDY 5: TEAM WORK-SPLIT & EXECUTION CHARTER", title_style))
    story.append(Paragraph("<b>Scenario:</b> POP3 Mailbox Access in a Low-Bandwidth Branch • <b>Framework:</b> 5-Member Equitable Task Distribution", subtitle_style))
    
    # Overview Callout
    intro_html = (
        "<b>Notice to All Team Members:</b> This document provides the official task delegation, individual deliverables, "
        "and grading rubric alignment for our 5-member team on Case Study 5. A complete, high-quality master report "
        "(<i>'Case Study 5 - POP3 Mailbox Access in a Low-Bandwidth Branch.docx'</i>) has already been drafted. Use this charter "
        "to understand your assigned ownership, master your section for faculty viva/cross-questioning, and guarantee top marks (100/100)."
    )
    intro_table = Table([[Paragraph(intro_html, body_style)]], colWidths=[523])
    intro_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BFDBFE")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(intro_table)
    story.append(Spacer(1, 12))

    # =========================================================================
    # SECTION 1: EXECUTIVE RESPONSIBILITY MATRIX (TABLE)
    # =========================================================================
    story.append(Paragraph("1. Executive Team Responsibility Matrix", h1_style))
    story.append(Paragraph("Direct mapping of each member to report sections, key deliverables, and viva specialization:", body_style))

    matrix_data = [
        [
            Paragraph("Member", tbl_header_style),
            Paragraph("Designated Role", tbl_header_style),
            Paragraph("Sections Owned", tbl_header_style),
            Paragraph("Core Deliverables & Tasks", tbl_header_style),
            Paragraph("Viva Focus", tbl_header_style)
        ],
        [
            Paragraph("<b>Member 1</b><br/>(Team Lead)", tbl_cell_bold),
            Paragraph("<b>Lead Protocol Analyst</b><br/>& FSM Architect", tbl_cell_bold),
            Paragraph("• Section 1 (Overview)<br/>• Section 6.1 (Question a)", tbl_cell_text),
            Paragraph("• RFC 1939 Protocol Architecture & FSM states<br/>• Deconstruct POP3 limitations (monolithic transfer, lack of resume, flag loss)<br/>• Lead coordination & master doc merge", tbl_cell_text),
            Paragraph("RFC 1939 FSM, POP3 3-phase lifecycle, broken RETR mechanics", tbl_cell_text)
        ],
        [
            Paragraph("<b>Member 2</b>", tbl_cell_bold),
            Paragraph("<b>WAN Systems &</b><br/>Workflow Architect", tbl_cell_bold),
            Paragraph("• Section 1.1–1.4<br/>• Section 6.2 (Question b)", tbl_cell_text),
            Paragraph("• WAN link model (256 kbps, 450ms RTT, satellite)<br/>• 5-Tier Resilient Email Access Workflow<br/>• Store-and-forward edge proxy & TOP pre-fetch<br/>• Workflow ASCII sequence diagram", tbl_cell_text),
            Paragraph("Why raw IMAP fails on VSAT, 5-Tier edge workflow, header pre-fetching", tbl_cell_text)
        ],
        [
            Paragraph("<b>Member 3</b>", tbl_cell_bold),
            Paragraph("<b>Simulation & Packet</b><br/>Capture Specialist", tbl_cell_bold),
            Paragraph("• Section 5 (All)<br/>• Table 4 (Setup)<br/>• Subsections 5.1–5.3", tbl_cell_text),
            Paragraph("• Wireshark trace breakdown (Port 110 vs 995)<br/>• Packet-level proof of -ERR [IN-USE] lockout<br/>• Python socket emulation script verification<br/>• Network topology diagram", tbl_cell_text),
            Paragraph("Wireshark trace frames, TCP 3-way handshake, keepalive lockouts", tbl_cell_text)
        ],
        [
            Paragraph("<b>Member 4</b>", tbl_cell_bold),
            Paragraph("<b>Cybersecurity &</b><br/>Threat Analyst", tbl_cell_bold),
            Paragraph("• Section 6.3 (Question c)<br/>• Threat Modeling<br/>• Hardening Plan", tbl_cell_text),
            Paragraph("• Threat analysis of legacy mail (sniffing, MITM)<br/>• Cryptographic failure of APOP (MD5 collisions)<br/>• Hardening blueprint: TLS 1.3, SASL OAuth 2.0<br/>• Reliability failure modes (lock freezes, PST loss)", tbl_cell_text),
            Paragraph("Cleartext port 110 sniffing, APOP MD5 weakness, OAuth2/TLS 1.3", tbl_cell_text)
        ],
        [
            Paragraph("<b>Member 5</b>", tbl_cell_bold),
            Paragraph("<b>Quality, Benchmarks</b><br/>& Standards Lead", tbl_cell_bold),
            Paragraph("• Sections 2, 3 (Tables)<br/>• Section 4 (Findings)<br/>• Section 5.4, 7 & 8", tbl_cell_text),
            Paragraph("• Populate Table 2 (Protocols) & Table 3 (RFCs)<br/>• Section 5.4 Comparative Performance Table<br/>• Base64 37% MIME expansion calculations<br/>• Section 7 Conclusion & IEEE Reference audit", tbl_cell_text),
            Paragraph("Base64 37% penalty, POP3 vs IMAP benchmarks, RFC citations", tbl_cell_text)
        ]
    ]

    matrix_table = Table(matrix_data, colWidths=[55, 95, 85, 178, 110])
    matrix_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
    ]))
    story.append(matrix_table)
    story.append(Spacer(1, 14))
    story.append(PageBreak())

    # =========================================================================
    # SECTION 2: DETAILED MEMBER BREAKDOWNS
    # =========================================================================
    story.append(Paragraph("2. Individual Role Profiles & Actionable Tasks", h1_style))
    story.append(Paragraph("Each member must read and fully understand their designated technical area:", body_style))

    # MEMBER 1
    m1_box = [
        Paragraph("<b>MEMBER 1: LEAD PROTOCOL ANALYST & FSM ARCHITECT</b>", ParagraphStyle('M1H', fontName='Helvetica-Bold', fontSize=10, textColor=c_primary)),
        Paragraph("<b>Primary Ownership:</b> Section 1 (Case Study Overview: Background, Problem Statement, Objectives, Scope, Key Concepts) & Section 6.1 (Question a: Explain POP3 and Its Limitations).", body_style),
        Paragraph("<b>Specific Actionable Tasks:</b>", ParagraphStyle('SubB', fontName='Helvetica-Bold', fontSize=8.5, textColor=c_teal)),
        Paragraph("• <b>Deconstruct RFC 1939 Architecture:</b> Explain client-server text-based dialogue over TCP port 110/995, command verbs (STAT, LIST, RETR, DELE, TOP, UIDL, QUIT), and +OK / -ERR reply tokens.", bullet_style),
        Paragraph("• <b>Map the 3-State Finite State Machine:</b> Detail AUTHORIZATION (USER/PASS/APOP), TRANSACTION (mailbox interrogation), and UPDATE (commit deletions upon QUIT).", bullet_style),
        Paragraph("• <b>Analyze Core Protocol Limitations:</b> Explain why monolithic retrieval chokes narrow pipes, why RETR cannot resume broken byte offsets, and why abrupt disconnects trigger non-atomic deletion rollbacks (causing duplicate emails).", bullet_style),
        Paragraph("• <b>Team Leadership:</b> Ensure all team members' details are entered into Table 1 of the Word document, conduct final integration, and monitor milestone deadlines.", bullet_style)
    ]
    t_m1 = Table([[m1_box]], colWidths=[523])
    t_m1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
        ('BOX', (0,0), (-1,-1), 0.75, c_border),
        ('LINELEFT', (0,0), (-1,-1), 3, c_accent),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_m1)
    story.append(Spacer(1, 8))

    # MEMBER 2
    m2_box = [
        Paragraph("<b>MEMBER 2: WAN SYSTEMS & WORKFLOW ARCHITECT</b>", ParagraphStyle('M2H', fontName='Helvetica-Bold', fontSize=10, textColor=c_primary)),
        Paragraph("<b>Primary Ownership:</b> Section 1.1–1.4 (WAN Impairment Modeling) & Section 6.2 (Question b: Design an Appropriate Email-Access Workflow).", body_style),
        Paragraph("<b>Specific Actionable Tasks:</b>", ParagraphStyle('SubB', fontName='Helvetica-Bold', fontSize=8.5, textColor=c_teal)),
        Paragraph("• <b>Model Constrained WAN Environment:</b> Quantify transmission latency over geostationary satellite (VSAT) links (450–700 ms RTT, 256 kbps throughput, 5% random packet loss, rain fade).", bullet_style),
        Paragraph("• <b>Design the 5-Tier Resilient Email Architecture:</b>", bullet_style),
        Paragraph("   - <i>Tier 1 (LAN Isolation):</i> Deploy local branch edge mail gateway (Dovecot/Fetchmail proxy) providing instant LAN speeds.<br/>"
                  "   - <i>Tier 2 (Header Pre-Fetch):</i> Use <code>TOP msg 0</code> to triage subject, sender, and size without pulling payloads (&lt;15 KB sync).<br/>"
                  "   - <i>Tier 3 (Attachment Throttling):</i> Auto-sync &lt;100 KB text; hold &gt;100 KB MIME attachments at HQ until on-demand click.<br/>"
                  "   - <i>Tier 4 (Wire Compression):</i> Implement zlib/gzip tunnel compression, slashing text/MIME payloads by 65%.<br/>"
                  "   - <i>Tier 5 (Outbound Spooling):</i> Local Postfix relay queuing outbound mail with exponential backoff retry timers.", bullet_style),
        Paragraph("• <b>Illustrate Workflow Sequence:</b> Walk through the ASCII flowchart showing Client MUA &lt;--&gt; Local Proxy &lt;--&gt; WAN &lt;--&gt; HQ Mail Server.", bullet_style)
    ]
    t_m2 = Table([[m2_box]], colWidths=[523])
    t_m2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
        ('BOX', (0,0), (-1,-1), 0.75, c_border),
        ('LINELEFT', (0,0), (-1,-1), 3, c_teal),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_m2)
    story.append(Spacer(1, 8))

    # MEMBER 3
    m3_box = [
        Paragraph("<b>MEMBER 3: SIMULATION & PACKET CAPTURE SPECIALIST</b>", ParagraphStyle('M3H', fontName='Helvetica-Bold', fontSize=10, textColor=c_primary)),
        Paragraph("<b>Primary Ownership:</b> Section 5 (Implementation / Simulation / Demonstration), Table 4, Subsections 5.1 (Topology), 5.2 (Wireshark Trace), and 5.3 (Python Socket Verification).", body_style),
        Paragraph("<b>Specific Actionable Tasks:</b>", ParagraphStyle('SubB', fontName='Helvetica-Bold', fontSize=8.5, textColor=c_teal)),
        Paragraph("• <b>Configure Simulation Parameters (Table 4):</b> Document tools (Wireshark v4.2.x, Python 3.12 socket/poplib, Ubuntu Linux <code>tc-netem</code>) and experimental setup (192.168.10.50 MUA &lt;--&gt; 256 kbps WAN &lt;--&gt; 10.0.0.25 HQ server).", bullet_style),
        Paragraph("• <b>Analyze Wireshark Protocol Traces:</b> Break down frame-by-frame interactions: TCP 3-way handshake (452ms RTT), cleartext PASS exposure in Frame 07, streaming RETR 4, simulated link severance, and TCP RTO backoff.", bullet_style),
        Paragraph("• <b>Demonstrate Mailbox Lock Contention:</b> Highlight Frame 94 showing reconnection failure: <code>-ERR [IN-USE] Mailbox is locked by another session</code> due to orphaned half-open TCP sockets.", bullet_style),
        Paragraph("• <b>Verify Python Socket Harness:</b> Explain how the Python socket script successfully extracts headers via <code>TOP 4 0</code> in 820 bytes, saving 1.88 MB of WAN transfer.", bullet_style)
    ]
    t_m3 = Table([[m3_box]], colWidths=[523])
    t_m3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
        ('BOX', (0,0), (-1,-1), 0.75, c_border),
        ('LINELEFT', (0,0), (-1,-1), 3, colors.HexColor("#6366F1")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_m3)
    story.append(Spacer(1, 8))

    story.append(PageBreak())  # Clean break to Page 2

    # MEMBER 4
    m4_box = [
        Paragraph("<b>MEMBER 4: CYBERSECURITY & THREAT ANALYST</b>", ParagraphStyle('M4H', fontName='Helvetica-Bold', fontSize=10, textColor=c_primary)),
        Paragraph("<b>Primary Ownership:</b> Section 6.3 (Question c: Analyze Security and Reliability Concerns of Legacy Mail Access) & Hardening Blueprint.", body_style),
        Paragraph("<b>Specific Actionable Tasks:</b>", ParagraphStyle('SubB', fontName='Helvetica-Bold', fontSize=8.5, textColor=c_teal)),
        Paragraph("• <b>Audit Security Vulnerabilities:</b> Detail cleartext sniffing on TCP port 110, credential theft, man-in-the-middle (MITM) tampering, and lack of message integrity verification.", bullet_style),
        Paragraph("• <b>Cryptographic Breakdown of APOP:</b> Explain why RFC 1939 APOP is obsolete—MD5 hash collisions, length-extension vulnerabilities, and susceptibility to offline rainbow tables.", bullet_style),
        Paragraph("• <b>Identify Operational Failure Modes:</b> Explain exclusive lock freezing (half-open TCP sessions keeping dotlock/flock engaged for 15–30 mins), duplicate delivery storms, and local PST/mbox file corruption risks.", bullet_style),
        Paragraph("• <b>Formulate Enterprise Hardening Plan:</b> Detail mandatory migration to POP3S (Port 995 over TLS 1.3 with <code>TLS_AES_256_GCM_SHA384</code>), SASL XOAUTH2 token-based authentication (MFA integration), and DMZ perimeter firewall access lists.", bullet_style)
    ]
    t_m4 = Table([[m4_box]], colWidths=[523])
    t_m4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
        ('BOX', (0,0), (-1,-1), 0.75, c_border),
        ('LINELEFT', (0,0), (-1,-1), 3, colors.HexColor("#EF4444")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_m4)
    story.append(Spacer(1, 8))

    # MEMBER 5
    m5_box = [
        Paragraph("<b>MEMBER 5: QUALITY, BENCHMARKS & STANDARDS LEAD</b>", ParagraphStyle('M5H', fontName='Helvetica-Bold', fontSize=10, textColor=c_primary)),
        Paragraph("<b>Primary Ownership:</b> Section 2 (Technologies Table), Section 3 (Standards/RFC Table), Section 4 (Research Findings), Section 5.4 (Benchmark Matrix), Section 7 (Conclusion), and Section 8 (References).", body_style),
        Paragraph("<b>Specific Actionable Tasks:</b>", ParagraphStyle('SubB', fontName='Helvetica-Bold', fontSize=8.5, textColor=c_teal)),
        Paragraph("• <b>Complete Table 2 & Table 3:</b> Rigorously define POP3, IMAP4, SMTP, POP3S, and MIME; verify RFC citations (RFC 1939, RFC 2595, RFC 3501, RFC 5321, RFC 8446, RFC 7628) with valid URLs and access dates.", bullet_style),
        Paragraph("• <b>Calculate MIME Bandwidth Penalties:</b> Provide mathematical proof of Base64 encoding overhead (3 binary bytes $\\rightarrow$ 4 ASCII characters = 33.33% inflation, ~37% with CRLF wrapping). Show why a 3 MB attachment inflates to 4.11 MB.", bullet_style),
        Paragraph("• <b>Evaluate Performance Benchmarks (Table 5):</b> Contrast Legacy POP3 (3.15 MB / 118s) vs IMAP4 (480 KB / 42s) vs Proposed Edge Workflow (14 KB / 1.9s) across bandwidth, completion time, and recovery.", bullet_style),
        Paragraph("• <b>Synthesize Conclusion & References:</b> Detail the 3-phase strategic roadmap (Immediate proxy $\\rightarrow$ Offline IMAP $\\rightarrow$ SD-WAN with FEC) and ensure IEEE citation formatting compliance.", bullet_style)
    ]
    t_m5 = Table([[m5_box]], colWidths=[523])
    t_m5.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
        ('BOX', (0,0), (-1,-1), 0.75, c_border),
        ('LINELEFT', (0,0), (-1,-1), 3, colors.HexColor("#F59E0B")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_m5)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 3: STEP-BY-STEP PROCEDURE & TIMELINE
    # =========================================================================
    story.append(Paragraph("3. Step-by-Step Procedure & Execution Timeline", h1_style))
    story.append(Paragraph("Follow this structured 4-phase timeline to guarantee seamless collaboration without overlapping work:", body_style))

    timeline_data = [
        [
            Paragraph("Phase & Timeline", tbl_header_style),
            Paragraph("Core Objectives", tbl_header_style),
            Paragraph("Actionable Steps & Milestone Checks", tbl_header_style),
            Paragraph("Responsible", tbl_header_style)
        ],
        [
            Paragraph("<b>PHASE 1</b><br/>Day 1 (Kick-off)", tbl_cell_bold),
            Paragraph("Task Alignment & Background Research", tbl_cell_text),
            Paragraph("• Hold 20-min team briefing to confirm role assignments.<br/>• Everyone reviews their assigned RFCs & syllabus concepts.<br/>• Open the master DOCX report and read assigned sections.", tbl_cell_text),
            Paragraph("All 5 Members<br/>(Lead by M1)", tbl_cell_text)
        ],
        [
            Paragraph("<b>PHASE 2</b><br/>Day 2 (Evidence)", tbl_cell_bold),
            Paragraph("Simulation & Data Verification", tbl_cell_text),
            Paragraph("• M3 reviews Wireshark traces, packet timings & socket logs.<br/>• M2 & M5 verify bandwidth calculations (37% Base64 inflation).<br/>• M4 finalizes security vulnerability matrix & cipher suites.", tbl_cell_text),
            Paragraph("M2, M3, M4, M5", tbl_cell_text)
        ],
        [
            Paragraph("<b>PHASE 3</b><br/>Day 3 (Integration)", tbl_cell_bold),
            Paragraph("Master Document Personalization", tbl_cell_text),
            Paragraph("• Enter all 5 team member names, registration numbers & roles in Table 1.<br/>• Enter Course Instructor name and Team Number on cover.<br/>• Ensure all sub-bullet points and diagrams render cleanly.", tbl_cell_text),
            Paragraph("M1 (Lead) &<br/>M5 (Review)", tbl_cell_text)
        ],
        [
            Paragraph("<b>PHASE 4</b><br/>Day 4 (Defense)", tbl_cell_bold),
            Paragraph("Peer Review & Viva Preparation", tbl_cell_text),
            Paragraph("• Conduct internal mock viva using Section 4 questions.<br/>• Verify full compliance with 100-mark evaluation rubric.<br/>• Export final PDF alongside DOCX for LMS submission.", tbl_cell_text),
            Paragraph("All 5 Members", tbl_cell_text)
        ]
    ]

    t_timeline = Table(timeline_data, colWidths=[80, 115, 238, 90])
    t_timeline.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
    ]))
    story.append(t_timeline)
    story.append(Spacer(1, 10))
    story.append(PageBreak())

    # =========================================================================
    # SECTION 4: VIVA & FACULTY DEFENSE CHEAT-SHEET
    # =========================================================================
    story.append(Paragraph("4. Faculty Viva & Defense Cheat-Sheet (High-Probability Questions)", h1_style))
    story.append(Paragraph("Every member must memorize the bulletproof answer to their question for cross-examination:", body_style))

    viva_qas = [
        ("Member 1 Question", "Why can't standard POP3 resume an interrupted download if the link drops at 90%?",
         "POP3 (RFC 1939) specifies the RETR command without byte-offset parameters, unlike HTTP Range headers. Furthermore, message state commits exclusively during the UPDATE phase upon a clean QUIT. A sudden TCP drop rolls back uncommitted flags, forcing the client to re-request the entire payload from byte zero."),
        
        ("Member 2 Question", "Why not simply switch the branch to IMAP4 instead of building a store-and-forward proxy?",
         "Standard IMAP4 is a highly chatty protocol requiring multiple bidirectional round-trips for mailbox state and flag synchronization. Over a geostationary satellite link with 450–700 ms RTT, this causes severe UI lag and consumes continuous airtime. Our edge store-and-forward proxy combines offline local caching with selective header-only WAN fetching via TOP, cutting WAN sync traffic by over 98%."),
        
        ("Member 3 Question", "What packet-level evidence proves that POP3 causes denial of service after link disruption?",
         "In Frame 86 of our Wireshark capture, an ungraceful link disconnect leaves a half-open TCP socket without sending FIN/RST. The server daemon retains an exclusive file lock (dotlock/flock). In Frame 94, when the user reconnects, the server rejects authentication with '-ERR [IN-USE] Mailbox is locked' until the TCP keepalive timer expires (15–30 mins)."),
         
        ("Member 4 Question", "Why is APOP considered cryptographically obsolete despite not sending plaintext passwords?",
         "APOP relies on an MD5 challenge-response digest: MD5(timestamp + shared_secret). MD5 is cryptographically compromised due to practical collision and length-extension attacks. Moreover, APOP cannot authenticate the server, lacks PFS (Perfect Forward Secrecy), and cannot support modern Multi-Factor Authentication or OAuth 2.0 tokens."),
         
        ("Member 5 Question", "How does MIME Base64 encoding penalize bandwidth in a 256 kbps branch network?",
         "Base64 converts 3 binary octets (24 bits) into 4 ASCII characters (32 bits), creating an inherent 33.33% data inflation. When RFC 2045 line wrapping (CRLF every 76 characters) is included, expansion reaches ~37%. A 3 MB PDF attachment expands to 4.11 MB, monopolizing a 256 kbps link for 147 seconds under ideal conditions.")
    ]

    for label, q_text, a_text in viva_qas:
        qa_content = [
            Paragraph(f"<b>[{label}]</b> <b>Q:</b> <i>{q_text}</i>", ParagraphStyle('QStyle', fontName='Helvetica-Bold', fontSize=8.5, leading=12, textColor=c_primary)),
            Spacer(1, 2),
            Paragraph(f"<b>A (30-Second Bulletproof Defense):</b> {a_text}", ParagraphStyle('AStyle', fontName='Helvetica', fontSize=8, leading=11.5, textColor=c_dark))
        ]
        t_qa = Table([[qa_content]], colWidths=[523])
        t_qa.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEF3C7")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#FDE68A")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t_qa)
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 6))

    # =========================================================================
    # SECTION 5: RUBRIC MAPPING & FINAL SUBMISSION CHECKLIST
    # =========================================================================
    story.append(Paragraph("5. Evaluation Rubric & Pre-Submission Checklist", h1_style))
    
    rubric_data = [
        [
            Paragraph("Assessment Rubric Criteria", tbl_header_style),
            Paragraph("Marks", tbl_header_style),
            Paragraph("How Our Team Secures Maximum Marks", tbl_header_style),
            Paragraph("Lead Owner", tbl_header_style)
        ],
        [
            Paragraph("Conceptual Understanding & Application", tbl_cell_bold),
            Paragraph("20", tbl_cell_bold),
            Paragraph("Deep explanation of POP3 FSM, client-server mail architecture, and TCP transport behavior over degraded links.", tbl_cell_text),
            Paragraph("Member 1", tbl_cell_text)
        ],
        [
            Paragraph("Quality & Relevance of Research", tbl_cell_bold),
            Paragraph("15", tbl_cell_bold),
            Paragraph("Direct citations of RFC 1939, 2595, 3501, 5321, 8446 with exact URLs, access dates, and vendor docs (Dovecot/Postfix).", tbl_cell_text),
            Paragraph("Member 5", tbl_cell_text)
        ],
        [
            Paragraph("Security & Technical Analysis", tbl_cell_bold),
            Paragraph("20", tbl_cell_bold),
            Paragraph("Exhaustive threat model of Port 110 sniffing, APOP MD5 collision attacks, lock freezes, and TLS 1.3 / OAuth2 hardening.", tbl_cell_text),
            Paragraph("Member 4", tbl_cell_text)
        ],
        [
            Paragraph("Architecture, Design & Packet Evidence", tbl_cell_bold),
            Paragraph("20", tbl_cell_bold),
            Paragraph("5-tier edge proxy workflow design + frame-by-frame Wireshark packet capture trace + Python socket emulation log.", tbl_cell_text),
            Paragraph("Member 2 & 3", tbl_cell_text)
        ],
        [
            Paragraph("Justification and Conclusions", tbl_cell_bold),
            Paragraph("15", tbl_cell_bold),
            Paragraph("Quantitative benchmark table (Table 5) proving 98% bandwidth reduction + 3-phase strategic modernization roadmap.", tbl_cell_text),
            Paragraph("Member 5", tbl_cell_text)
        ],
        [
            Paragraph("Presentation, Diagrams & Formatting", tbl_cell_bold),
            Paragraph("10", tbl_cell_bold),
            Paragraph("Strict adherence to SCOPE DOCX template, Times New Roman typography, clear ASCII topologies, and zero placeholders.", tbl_cell_text),
            Paragraph("Member 1 & 5", tbl_cell_text)
        ],
        [
            Paragraph("<b>TOTAL EVALUATION SCORE</b>", tbl_cell_bold),
            Paragraph("<b>100</b>", tbl_cell_bold),
            Paragraph("<b>Converted to 10 Marks in Final Academic Weightage</b>", tbl_cell_bold),
            Paragraph("<b>ALL TEAM</b>", tbl_cell_bold)
        ]
    ]

    t_rubric = Table(rubric_data, colWidths=[130, 40, 273, 80])
    t_rubric.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#E2E8F0")),
    ]))
    story.append(t_rubric)
    story.append(Spacer(1, 10))

    # Final Checklist Box
    chk_text = (
        "<b>FINAL SUBMISSION CHECKLIST (BEFORE UPLOADING TO LMS):</b><br/>"
        " [  ] <b>Master File:</b> <i>'Case Study 5 - POP3 Mailbox Access in a Low-Bandwidth Branch.docx'</i> is ready in workspace.<br/>"
        " [  ] <b>Table 1 (Team Details):</b> All 5 student registration numbers, names, and assigned roles are entered.<br/>"
        " [  ] <b>Table 0 (Cover Block):</b> Course Instructor name and Team Number are completed.<br/>"
        " [  ] <b>Readiness:</b> Every member has reviewed their assigned viva defense question above.<br/>"
        " [  ] <b>File Export:</b> Both DOCX and PDF versions are exported for group sharing and submission."
    )
    t_chk = Table([[Paragraph(chk_text, body_style)]], colWidths=[523])
    t_chk.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0FDF4")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#86EFAC")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_chk)

    # Build the document
    print(f"Generating PDF: {filename}...")
    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF generated successfully!")

if __name__ == "__main__":
    build_pdf()
