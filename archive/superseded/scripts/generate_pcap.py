#!/usr/bin/env python3
"""
generate_pcap.py
Generates a valid binary .pcap file (pop3_wireshark_capture.pcap) containing
the exact simulated POP3 dialogue:
1. TCP 3-Way Handshake
2. Plaintext USER/PASS authentication
3. Mailbox interrogation (STAT, LIST)
4. Streaming RETR payload
5. Simulated satellite drop & TCP retransmission
6. Reconnect attempt triggering -ERR [IN-USE]
"""

import struct
import socket

def checksum(data):
    if len(data) % 2 != 0:
        data += b'\x00'
    s = sum(struct.unpack(f"!{len(data)//2}H", data))
    while s >> 16:
        s = (s & 0xFFFF) + (s >> 16)
    return ~s & 0xFFFF

def make_ethernet(src_mac, dst_mac, ethertype=0x0800):
    return dst_mac + src_mac + struct.pack("!H", ethertype)

def make_ip(src_ip, dst_ip, payload_len, protocol=6, ttl=64, ident=1):
    src = socket.inet_aton(src_ip)
    dst = socket.inet_aton(dst_ip)
    ihl_ver = (4 << 4) | 5
    tos = 0
    tot_len = 20 + payload_len
    flags_frag = 0x4000 # Don't fragment
    hdr_without_cksum = struct.pack("!BBHHHBBH4s4s",
        ihl_ver, tos, tot_len, ident, flags_frag, ttl, protocol, 0, src, dst
    )
    cksum = checksum(hdr_without_cksum)
    return struct.pack("!BBHHHBBH4s4s",
        ihl_ver, tos, tot_len, ident, flags_frag, ttl, protocol, cksum, src, dst
    )

def make_tcp(src_port, dst_port, seq, ack, flags, payload=b"", src_ip="192.168.10.50", dst_ip="10.0.0.25", win=65535):
    data_offset = (5 << 4) # 5 words = 20 bytes
    tcp_hdr_no_ck = struct.pack("!HHIIBBHHH",
        src_port, dst_port, seq, ack, data_offset, flags, win, 0, 0
    )
    # Pseudo header for TCP checksum
    src = socket.inet_aton(src_ip)
    dst = socket.inet_aton(dst_ip)
    tcp_len = len(tcp_hdr_no_ck) + len(payload)
    pseudo = struct.pack("!4s4sBBH", src, dst, 0, 6, tcp_len)
    cksum = checksum(pseudo + tcp_hdr_no_ck + payload)
    
    tcp_hdr = struct.pack("!HHIIBBHHH",
        src_port, dst_port, seq, ack, data_offset, flags, win, cksum, 0
    )
    return tcp_hdr + payload

def build_packet(src_mac, dst_mac, src_ip, dst_ip, src_port, dst_port, seq, ack, flags, payload=b"", ident=1):
    tcp_seg = make_tcp(src_port, dst_port, seq, ack, flags, payload, src_ip, dst_ip)
    ip_pkt = make_ip(src_ip, dst_ip, len(tcp_seg), protocol=6, ident=ident)
    eth_frame = make_ethernet(src_mac, dst_mac) + ip_pkt + tcp_seg
    return eth_frame

def main(output_file="pop3_wireshark_capture.pcap"):
    client_mac = b"\x00\x1a\x2b\x3c\x4d\x5e"
    server_mac = b"\x00\x98\x76\x54\x32\x10"
    client_ip = "192.168.10.50"
    server_ip = "10.0.0.25"
    client_port = 54100
    server_port = 110

    # TCP Flags
    FIN = 0x01
    SYN = 0x02
    RST = 0x04
    PSH = 0x08
    ACK = 0x10

    frames = []
    
    # 1. TCP 3-Way Handshake
    # Frame 1: SYN (Client -> Server)
    c_seq = 1000
    s_seq = 5000
    p1 = build_packet(client_mac, server_mac, client_ip, server_ip, client_port, server_port, c_seq, 0, SYN, ident=1)
    frames.append((0.0, p1))
    c_seq += 1

    # Frame 2: SYN, ACK (Server -> Client, 452ms latency)
    p2 = build_packet(server_mac, client_mac, server_ip, client_ip, server_port, client_port, s_seq, c_seq, SYN | ACK, ident=2)
    frames.append((0.452, p2))
    s_seq += 1

    # Frame 3: ACK (Client -> Server)
    p3 = build_packet(client_mac, server_mac, client_ip, server_ip, client_port, server_port, c_seq, s_seq, ACK, ident=3)
    frames.append((0.453, p3))

    # 2. Server Banner
    banner = b"+OK Dovecot POP3 server ready (HQ Enterprise Maildrop)\r\n"
    p4 = build_packet(server_mac, client_mac, server_ip, client_ip, server_port, client_port, s_seq, c_seq, PSH | ACK, banner, ident=4)
    frames.append((0.905, p4))
    s_seq += len(banner)

    # 3. USER branch_user1
    user_cmd = b"USER branch_user1\r\n"
    p5 = build_packet(client_mac, server_mac, client_ip, server_ip, client_port, server_port, c_seq, s_seq, PSH | ACK, user_cmd, ident=5)
    frames.append((0.906, p5))
    c_seq += len(user_cmd)

    user_resp = b"+OK User accepted\r\n"
    p6 = build_packet(server_mac, client_mac, server_ip, client_ip, server_port, client_port, s_seq, c_seq, PSH | ACK, user_resp, ident=6)
    frames.append((1.358, p6))
    s_seq += len(user_resp)

    # 4. PASS SecretP@ss2026! (Cleartext!)
    pass_cmd = b"PASS SecretP@ss2026!\r\n"
    p7 = build_packet(client_mac, server_mac, client_ip, server_ip, client_port, server_port, c_seq, s_seq, PSH | ACK, pass_cmd, ident=7)
    frames.append((1.359, p7))
    c_seq += len(pass_cmd)

    pass_resp = b"+OK Logged in. Mailbox spool locked exclusively.\r\n"
    p8 = build_packet(server_mac, client_mac, server_ip, client_ip, server_port, client_port, s_seq, c_seq, PSH | ACK, pass_resp, ident=8)
    frames.append((1.811, p8))
    s_seq += len(pass_resp)

    # 5. STAT
    stat_cmd = b"STAT\r\n"
    p9 = build_packet(client_mac, server_mac, client_ip, server_ip, client_port, server_port, c_seq, s_seq, PSH | ACK, stat_cmd, ident=9)
    frames.append((1.812, p9))
    c_seq += len(stat_cmd)

    stat_resp = b"+OK 5 3145728\r\n"
    p10 = build_packet(server_mac, client_mac, server_ip, client_ip, server_port, client_port, s_seq, c_seq, PSH | ACK, stat_resp, ident=10)
    frames.append((2.264, p10))
    s_seq += len(stat_resp)

    # 6. LIST
    list_cmd = b"LIST\r\n"
    p11 = build_packet(client_mac, server_mac, client_ip, server_ip, client_port, server_port, c_seq, s_seq, PSH | ACK, list_cmd, ident=11)
    frames.append((2.265, p11))
    c_seq += len(list_cmd)

    list_resp = b"+OK 5 messages (3145728 octets)\r\n1 12288\r\n2 87040\r\n3 460800\r\n4 1887436\r\n5 3355440\r\n.\r\n"
    p12 = build_packet(server_mac, client_mac, server_ip, client_ip, server_port, client_port, s_seq, c_seq, PSH | ACK, list_resp, ident=12)
    frames.append((2.717, p12))
    s_seq += len(list_resp)

    # 7. RETR 4 (Large message)
    retr_cmd = b"RETR 4\r\n"
    p13 = build_packet(client_mac, server_mac, client_ip, server_ip, client_port, server_port, c_seq, s_seq, PSH | ACK, retr_cmd, ident=13)
    frames.append((2.718, p13))
    c_seq += len(retr_cmd)

    retr_resp_chunk = (
        b"+OK 1887436 octets\r\n"
        b"From: engineering-hq@enterprise.com\r\n"
        b"To: branch_user1@enterprise.com\r\n"
        b"Subject: CRITICAL: Q4 Structural Blueprints Attachment\r\n"
        b"Date: Wed, 21 Oct 2026 08:15:00 +0000\r\n"
        b"Content-Type: multipart/mixed; boundary=\"====Boundary_1234====\"\r\n\r\n"
        b"--====Boundary_1234====\r\n"
        b"Content-Type: application/pdf; name=\"blueprints.pdf\"\r\n"
        b"Content-Transfer-Encoding: base64\r\n\r\n"
        b"JVBERi0xLjUKJfb1978KMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFI... [DATA STREAMING]"
    )
    p14 = build_packet(server_mac, client_mac, server_ip, client_ip, server_port, client_port, s_seq, c_seq, PSH | ACK, retr_resp_chunk, ident=14)
    frames.append((3.170, p14))
    s_seq += len(retr_resp_chunk)

    # 8. Link Disruption Simulated: Client TCP Retransmission timeouts
    p15 = build_packet(client_mac, server_mac, client_ip, server_ip, client_port, server_port, c_seq, s_seq, ACK, ident=15)
    frames.append((5.170, p15)) # RTO backoff
    p16 = build_packet(client_mac, server_mac, client_ip, server_ip, client_port, server_port, c_seq, s_seq, ACK, ident=16)
    frames.append((9.170, p16)) # Exponential backoff

    # 9. Session 2: Immediate Reconnect on new port (54102)
    c2_port = 54102
    c2_seq = 2000
    s2_seq = 8000

    # SYN / SYN-ACK / ACK
    p17 = build_packet(client_mac, server_mac, client_ip, server_ip, c2_port, server_port, c2_seq, 0, SYN, ident=17)
    frames.append((12.000, p17))
    c2_seq += 1

    p18 = build_packet(server_mac, client_mac, server_ip, client_ip, server_port, c2_port, s2_seq, c2_seq, SYN | ACK, ident=18)
    frames.append((12.452, p18))
    s2_seq += 1

    p19 = build_packet(client_mac, server_mac, client_ip, server_ip, c2_port, server_port, c2_seq, s2_seq, ACK, ident=19)
    frames.append((12.453, p19))

    # Banner
    p20 = build_packet(server_mac, client_mac, server_ip, client_ip, server_port, c2_port, s2_seq, c2_seq, PSH | ACK, banner, ident=20)
    frames.append((12.905, p20))
    s2_seq += len(banner)

    # USER
    p21 = build_packet(client_mac, server_mac, client_ip, server_ip, c2_port, server_port, c2_seq, s2_seq, PSH | ACK, user_cmd, ident=21)
    frames.append((12.906, p21))
    c2_seq += len(user_cmd)

    p22 = build_packet(server_mac, client_mac, server_ip, client_ip, server_port, c2_port, s2_seq, c2_seq, PSH | ACK, user_resp, ident=22)
    frames.append((13.358, p22))
    s2_seq += len(user_resp)

    # PASS -> REJECTED WITH -ERR [IN-USE]!
    p23 = build_packet(client_mac, server_mac, client_ip, server_ip, c2_port, server_port, c2_seq, s2_seq, PSH | ACK, pass_cmd, ident=23)
    frames.append((13.359, p23))
    c2_seq += len(pass_cmd)

    lock_err = b"-ERR [IN-USE] Mailbox is locked by another session! (Orphaned dotlock active)\r\n"
    p24 = build_packet(server_mac, client_mac, server_ip, client_ip, server_port, c2_port, s2_seq, c2_seq, PSH | ACK, lock_err, ident=24)
    frames.append((13.811, p24))
    s2_seq += len(lock_err)

    # Reset
    p25 = build_packet(server_mac, client_mac, server_ip, client_ip, server_port, c2_port, s2_seq, c2_seq, RST | ACK, ident=25)
    frames.append((13.820, p25))

    # Write PCAP file
    # Global header (24 bytes): magic, v_maj, v_min, zone, sigfigs, snaplen, network (1 = Ethernet)
    pcap_hdr = struct.pack("!IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)
    
    with open(output_file, "wb") as f:
        f.write(pcap_hdr)
        for ts_sec, pkt_data in frames:
            sec = int(ts_sec)
            usec = int((ts_sec - sec) * 1000000)
            pkt_len = len(pkt_data)
            # Packet header (16 bytes): sec, usec, caplen, origlen
            pkt_hdr = struct.pack("!IIII", sec, usec, pkt_len, pkt_len)
            f.write(pkt_hdr)
            f.write(pkt_data)

    print(f"Generated valid PCAP file with {len(frames)} packets: {output_file}")

if __name__ == "__main__":
    main("/Users/arunyasrivastava/CNP/pop3_wireshark_capture.pcap")
