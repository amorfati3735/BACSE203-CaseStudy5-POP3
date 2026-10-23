#!/usr/bin/env python3
"""
create_diagrams.py
Generates clean, publication-quality diagrams for Person 1's POP3 case study report:
1. pop3_state_machine.png (RFC 1939 Finite State Machine)
2. pop3_bottlenecks.png (Architectural Failure Modes on Constrained WANs)
"""

import os
from PIL import Image, ImageDraw, ImageFont

def get_font(size=14, bold=False):
    # Try system fonts on macOS
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()

def draw_rounded_rect(draw, coords, radius, fill, outline, width=2):
    draw.rounded_rectangle(coords, radius=radius, fill=fill, outline=outline, width=width)

def create_state_machine_diagram(output_path="pop3_state_machine.png"):
    width, height = 1000, 520
    im = Image.new("RGB", (width, height), "#FFFFFF")
    draw = ImageDraw.Draw(im)

    font_title = get_font(20, bold=True)
    font_box_title = get_font(16, bold=True)
    font_box_sub = get_font(12, bold=False)
    font_cmd = get_font(12, bold=True)
    font_desc = get_font(11, bold=False)

    # Outer border / canvas background
    draw_rounded_rect(draw, (10, 10, width-10, height-10), 12, "#F8FAFC", "#CBD5E1", 1)

    # Title Banner
    draw.text((30, 24), "POP3 Protocol Finite State Machine (RFC 1939)", fill="#0F172A", font=font_title)
    draw.text((30, 52), "Sequential State Transitions, Permitted Command Verbs, and Terminal Commit Phases", fill="#64748B", font=font_desc)

    # 1. State: CLOSED (Initial)
    draw_rounded_rect(draw, (40, 140, 180, 260), 10, "#E2E8F0", "#94A3B8", 2)
    draw.text((65, 160), "CLOSED", fill="#334155", font=font_box_title)
    draw.text((55, 195), "• No TCP Socket\n• Disconnected\n• Mailbox Unlocked", fill="#475569", font=font_box_sub)

    # Arrow 1: Closed -> Authorization
    draw.line((180, 200, 260, 200), fill="#0284C7", width=3)
    draw.polygon([(265, 200), (255, 194), (255, 206)], fill="#0284C7")
    draw.text((188, 175), "TCP SYN/ACK", fill="#0369A1", font=font_cmd)
    draw.text((188, 208), "Port 110/995", fill="#64748B", font=font_desc)

    # 2. State: AUTHORIZATION
    draw_rounded_rect(draw, (270, 110, 480, 430), 12, "#EFF6FF", "#3B82F6", 2)
    draw_rounded_rect(draw, (280, 120, 470, 160), 6, "#3B82F6", "#2563EB", 1)
    draw.text((305, 130), "1. AUTHORIZATION", fill="#FFFFFF", font=font_box_title)
    
    auth_text = (
        "Server: +OK Dovecot ready\n"
        "Client Verbs:\n"
        "  • USER <username>\n"
        "  • PASS <password>\n"
        "  • APOP <name> <digest>\n"
        "  • STLS (Negotiate TLS)\n"
        "  • QUIT (Direct Exit)\n\n"
        "Action:\n"
        "Validates credentials;\n"
        "Locks maildrop exclusively."
    )
    draw.text((285, 175), auth_text, fill="#1E293B", font=font_desc)

    # Arrow 2: Authorization -> Transaction
    draw.line((480, 200, 560, 200), fill="#059669", width=3)
    draw.polygon([(565, 200), (555, 194), (555, 206)], fill="#059669")
    draw.text((490, 175), "+OK Logged in", fill="#047857", font=font_cmd)
    draw.text((490, 208), "Acquire Lock", fill="#64748B", font=font_desc)

    # 3. State: TRANSACTION
    draw_rounded_rect(draw, (570, 100, 780, 440), 12, "#ECFDF5", "#10B981", 2)
    draw_rounded_rect(draw, (580, 110, 770, 150), 6, "#10B981", "#059669", 1)
    draw.text((605, 120), "2. TRANSACTION", fill="#FFFFFF", font=font_box_title)

    trans_text = (
        "Mailbox In-Use (Locked)\n"
        "Client Verbs:\n"
        "  • STAT  (Count & Bytes)\n"
        "  • LIST  (Message sizes)\n"
        "  • RETR n (Download email)\n"
        "  • TOP n k (Headers + k lines)\n"
        "  • UIDL n (Unique ID token)\n"
        "  • DELE n (Mark for deletion)\n"
        "  • RSET  (Unmark deletes)\n"
        "  • NOOP  (Keepalive probe)\n\n"
        "Critical:\n"
        "DELE is stored in memory ONLY;\n"
        "No disk changes yet!"
    )
    draw.text((585, 160), trans_text, fill="#064E3B", font=font_desc)

    # Arrow 3: Transaction -> Update
    draw.line((780, 200, 850, 200), fill="#D97706", width=3)
    draw.polygon([(855, 200), (845, 194), (845, 206)], fill="#D97706")
    draw.text((790, 175), "QUIT", fill="#B45309", font=font_cmd)
    draw.text((790, 208), "Commit Phase", fill="#64748B", font=font_desc)

    # 4. State: UPDATE
    draw_rounded_rect(draw, (860, 120, 970, 420), 12, "#FFFBEB", "#F59E0B", 2)
    draw_rounded_rect(draw, (868, 130, 962, 170), 6, "#F59E0B", "#D97706", 1)
    draw.text((882, 140), "3. UPDATE", fill="#FFFFFF", font=font_box_title)

    update_text = (
        "Actions on Disk:\n"
        "1. Unlinks & purges\n"
        "   all DELE messages.\n"
        "2. Releases\n"
        "   exclusive lock.\n"
        "3. Sends +OK banner.\n"
        "4. Closes TCP socket.\n\n"
        "Abnormal Drop:\n"
        "If connection dies\n"
        "before QUIT, server\n"
        "ROLLS BACK deletes!"
    )
    draw.text((868, 180), update_text, fill="#78350F", font=font_desc)

    # Curved Arrow: Update -> Closed
    draw.line((915, 420, 915, 470), fill="#64748B", width=2)
    draw.line((915, 470, 110, 470), fill="#64748B", width=2)
    draw.line((110, 470, 110, 260), fill="#64748B", width=2)
    draw.polygon([(110, 260), (105, 270), (115, 270)], fill="#64748B")
    draw.text((450, 475), "TCP Teardown & Reset to CLOSED State", fill="#475569", font=font_desc)

    # Callout alert for Lockout
    draw_rounded_rect(draw, (40, 280, 240, 430), 8, "#FEF2F2", "#FCA5A5", 1)
    draw.text((50, 290), "FATAL FAILURE MODE:", fill="#991B1B", font=font_cmd)
    failure_msg = (
        "If WAN drops during\n"
        "TRANSACTION:\n"
        "• Half-open socket stays\n"
        "  alive on server.\n"
        "• Mailbox stays LOCKED.\n"
        "• Next login fails with:\n"
        "  -ERR [IN-USE] locked!\n"
        "• Duration: 15-30 mins."
    )
    draw.text((50, 310), failure_msg, fill="#7F1D1D", font=font_desc)

    im.save(output_path, "PNG", dpi=(300, 300))
    print(f"Saved: {output_path}")

def create_bottlenecks_diagram(output_path="pop3_bottlenecks.png"):
    width, height = 1000, 480
    im = Image.new("RGB", (width, height), "#FFFFFF")
    draw = ImageDraw.Draw(im)

    font_title = get_font(20, bold=True)
    font_box_title = get_font(15, bold=True)
    font_cmd = get_font(12, bold=True)
    font_desc = get_font(11, bold=False)

    # Canvas border
    draw_rounded_rect(draw, (10, 10, width-10, height-10), 12, "#F8FAFC", "#CBD5E1", 1)

    # Title
    draw.text((30, 24), "POP3 Architectural Failure Modes Across Low-Bandwidth Satellite Links", fill="#0F172A", font=font_title)
    draw.text((30, 52), "Deconstruction of Why Unmanaged POP3 Fails on Intermittent 256 kbps WAN Connections", fill="#64748B", font=font_desc)

    # 4 Bottleneck Cards
    bottlenecks = [
        (
            "1. Monolithic Download",
            "RETR forces whole email + attachment",
            "• RFC 1939 has no selective MIME parsing.\n• Cannot download body without attachment.\n• Base64 expands binary by ~37%.\n• 3 MB PDF inflates to 4.11 MB.\n• 256 kbps pipe choked for 147 seconds!",
            "#EFF6FF", "#3B82F6", "#1E3A8A"
        ),
        (
            "2. No Resume on Drop",
            "Byte-Range offset unsupported",
            "• RETR lacks offset range parameters.\n• Unlike HTTP Range or FTP REST.\n• If link flaps at 98% of 4 MB transfer,\n  entire progress is discarded.\n• Upon reconnect, restarts from byte 0!\n• Creates infinite download loops.",
            "#FEF2F2", "#EF4444", "#991B1B"
        ),
        (
            "3. Exclusive Lockouts",
            "Dotlock retention during disconnects",
            "• Server acquires exclusive lock in Transaction.\n• Sudden link severance sends no TCP FIN/RST.\n• Server socket stays in TCP_ESTABLISHED.\n• Lock held until keepalive expires (15-30m).\n• User blocked: -ERR [IN-USE] locked!",
            "#FFFBEB", "#F59E0B", "#92400E"
        ),
        (
            "4. Duplicate Mail Floods",
            "Non-Atomic Deletion Rollback",
            "• DELE only stages deletion in memory.\n• Permanent deletion requires clean QUIT.\n• Link interruption aborts session.\n• Server rolls back all DELE flags.\n• Reconnect causes re-downloading same\n  emails, flooding user inbox!",
            "#F5F3FF", "#8B5CF6", "#5B21B6"
        )
    ]

    card_width = 225
    for i, (title, sub, body, bg_col, border_col, text_col) in enumerate(bottlenecks):
        x1 = 30 + i * (card_width + 15)
        y1 = 90
        x2 = x1 + card_width
        y2 = 450
        draw_rounded_rect(draw, (x1, y1, x2, y2), 10, bg_col, border_col, 2)
        draw_rounded_rect(draw, (x1+5, y1+5, x2-5, y1+42), 6, border_col, border_col, 1)
        draw.text((x1+10, y1+12), title, fill="#FFFFFF", font=font_box_title)
        draw.text((x1+10, y1+50), sub, fill=text_col, font=font_cmd)
        draw.line((x1+10, y1+72, x2-10, y1+72), fill=border_col, width=1)
        draw.text((x1+10, y1+85), body, fill="#1E293B", font=font_desc)

    im.save(output_path, "PNG", dpi=(300, 300))
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    create_state_machine_diagram()
    create_bottlenecks_diagram()
