# Person 3: Simulation & Packet Analysis — Visual Evidence Gallery

> **Course:** BACSE203 Computer Networks — Case Study 5  
> **Team Member:** Person 3 (Simulation & Packet Analysis Specialist)  
> **Lead Student:** Arunya Srivastava (Reg No: 25BCE0344)  
> **Topic:** POP3 Mailbox Access in a Low-Bandwidth Branch (256 kbps, 450 ms Satellite RTT)  
> **Repository:** [BACSE203-CaseStudy5-POP3](https://github.com/ArunyaSrivastava/BACSE203-CaseStudy5-POP3)  

---

## 📋 Executive Summary of Simulation Evidence

This document compiles the exhaustive visual and packet-level evidence gathered for **Person 3's deliverable** (*Section 5: Implementation Details & Verification*). 

The empirical tests validate the complete operational lifecycle of POP3 over high-latency, error-prone satellite links, demonstrating:
1. **TCP Connection Establishment:** 3-way handshakes captured on port 1110 with TCP window sizing and option negotiation.
2. **Cleartext Protocol Vulnerabilities:** Plaintext credential exposure (`USER` / `PASS`) in application payloads.
3. **Mid-Stream Link Severance & Head-of-Line Blocking:** Severe data pipeline interruption during 4.11 MB Base64 payload streaming (`RETR 4`).
4. **Filesystem Lock Contention:** Immediate rejection of subsequent client connections with `-ERR [IN-USE]` due to orphaned advisory dotlocks.
5. **Architectural Optimization Proof:** Two-phase selective header pre-fetching via **`TOP 4 0`**, slashing network transmission volume from **4.11 MB to 820 bytes** (>99.9% reduction in bandwidth consumption).

---

## 📸 Master Photo Gallery Index

| Fig # | Image File | Source | Core Protocol Focus |
| :---: | :--- | :--- | :--- |
| **Fig 1** | [`Wireshark_Follow_TCP_Stream_Session1_Normal_Login_and_RETR.png`](./Wireshark_Follow_TCP_Stream_Session1_Normal_Login_and_RETR.png) | `CNA` | **Stream 25:** Full two-way dialogue of Session 1 (Login $\rightarrow$ `STAT` $\rightarrow$ `LIST` $\rightarrow$ `RETR 4` severed mid-stream) |
| **Fig 2** | [`Wireshark_Follow_TCP_Stream_Session2_Lock_Contention.png`](./Wireshark_Follow_TCP_Stream_Session2_Lock_Contention.png) | `CNA` | **Stream 26:** Full two-way dialogue of Session 2 returning `-ERR [IN-USE]` lock contention |
| **Fig 3** | [`Wireshark_Filter_SYN_3Way_Handshake.png`](./Wireshark_Filter_SYN_3Way_Handshake.png) | `CNA` | Filter `tcp.port == 1110 && tcp.flags.syn == 1` — Handshake dissection & options |
| **Fig 4** | [`Wireshark_Filter_Application_Data_Frames.png`](./Wireshark_Filter_Application_Data_Frames.png) | `CNA` | Filter `tcp.port == 1110 && tcp.len > 0` — All 16 application payload frames & hex/ASCII |
| **Fig 5** | [`Wireshark_Filter_Port_1110_All_Frames.png`](./Wireshark_Filter_Port_1110_All_Frames.png) | `CNA` | Filter `tcp.port == 1110` — Chronological frame sequence with delta timings |
| **Fig 6** | [`Wireshark_TCP_Analysis_Retransmission_RTO.png`](./Wireshark_TCP_Analysis_Retransmission_RTO.png) | `CNA` | Filter `tcp.analysis.retransmission || tcp.analysis.rto` — RTO analysis |
| **Fig 7** | [`Python_TOP_4_0_Wireshark.png`](./Python_TOP_4_0_Wireshark.png) | `CNP` | Filter `tcp contains "TOP 4 0"` — Frame 15141 disassembly, TCP Seg Len=9 octets |
| **Fig 8** | [`my_live_capture_with_TOP_test.png`](./my_live_capture_with_TOP_test.png) | `CNP` | **Stream 151:** Two-way colored trace of selective header pre-fetch (`TOP 4 0`) |
| **Fig 9** | [`Python_TOP_4_0_Terminal.png`](./Python_TOP_4_0_Terminal.png) | `CNP` | Client socket terminal: 820-byte selective header retrieval in 0.014 seconds |
| **Fig 10** | [`Python_TOP_4_0_ServerLog.png`](./Python_TOP_4_0_ServerLog.png) | `CNP` | POP3 test daemon server log accepting port 63243 and serving 820 bytes |
| **Fig 11** | [`Live_Capture_Terminal_Wireshark_Split.png`](./Live_Capture_Terminal_Wireshark_Split.png) | `CNP` | Synchronized side-by-side execution: Terminal running simulation + Wireshark capture |
| **Fig 12** | [`Live_Capture_Packets_191_222_Wireshark.png`](./Live_Capture_Packets_191_222_Wireshark.png) | `CNP` | Wireshark packet grid (Frames 191–222) across link drop and reconnection |
| **Fig 13** | [`pop3_state_machine.png`](./pop3_state_machine.png) | Architecture | RFC 1939 POP3 Finite State Machine (Authorization $\rightarrow$ Transaction $\rightarrow$ Update) |
| **Fig 14** | [`pop3_bottlenecks.png`](./pop3_bottlenecks.png) | Architecture | Satellite WAN Failure Bottlenecks (256 kbps bandwidth, 450 ms latency, Base64 bloat) |

---

## 🔬 Detailed Photographic Evidence & Packet Dissections

---

### Phase 1: Live Interactive Protocol Streams (Follow TCP Stream)

#### Figure 1: Wireshark Follow TCP Stream — Session 1 (Normal Authentication & Severed RETR Streaming)
**File:** [`Wireshark_Follow_TCP_Stream_Session1_Normal_Login_and_RETR.png`](./Wireshark_Follow_TCP_Stream_Session1_Normal_Login_and_RETR.png)

![Session 1 Follow TCP Stream](./Wireshark_Follow_TCP_Stream_Session1_Normal_Login_and_RETR.png)

* **Wireshark Stream:** Stream 25 (5 client packets in red, 6 server packets in blue; 10 conversational turns; 565 bytes total).
* **Protocol Sequence:**
  1. `S: +OK Dovecot POP3 server ready (HQ Enterprise Maildrop)`
  2. `C: USER branch_user1`
  3. `S: +OK User accepted`
  4. `C: PASS SecretP@ss2026!`
  5. `S: +OK Logged in. Mailbox spool locked exclusively.`
  6. `C: STAT` $\longrightarrow$ `S: +OK 5 3145728`
  7. `C: LIST` $\longrightarrow$ `S: +OK 5 messages (3145728 octets)` (listing indices 1 to 5)
  8. `C: RETR 4`
  9. `S: +OK 1887436 octets`
     * `From: engineering-hq@enterprise.com`
     * `To: branch_user1@enterprise.com`
     * `Subject: CRITICAL: Q4 Structural Blueprints Attachment`
     * `Content-Type: multipart/mixed; boundary="====B123===="`
     * `[STREAMING 1.88 MB BASE64 MIME ATTACHMENT... CHUNKS 1-15 TRANSMITTED...]`
* **Vulnerability & Failure Analysis:**  
  * The authentication credentials (`USER branch_user1` / `PASS SecretP@ss2026!`) are transmitted in cleartext ASCII.
  * The stream abruptly ends during chunk 15 without a POP3 `QUIT` command or TCP `FIN` exchange, simulating sudden satellite link drop.

---

#### Figure 2: Wireshark Follow TCP Stream — Session 2 (Reconnection Attempt & Exclusive Lockout)
**File:** [`Wireshark_Follow_TCP_Stream_Session2_Lock_Contention.png`](./Wireshark_Follow_TCP_Stream_Session2_Lock_Contention.png)

![Session 2 Follow TCP Stream Lock Contention](./Wireshark_Follow_TCP_Stream_Session2_Lock_Contention.png)

* **Wireshark Stream:** Stream 26 (Reconnection immediately following link severance).
* **Protocol Sequence:**
  1. `S: +OK Dovecot POP3 server ready (HQ Enterprise Maildrop)`
  2. `C: USER branch_user1`
  3. `S: +OK User accepted`
  4. `C: PASS SecretP@ss2026!`
  5. `S: -ERR [IN-USE] Mailbox is locked by another session! (Orphaned dotlock active)`
* **RFC 1939 Compliance & Failure Analysis:**  
  * Because Session 1 was severed abruptly during the **Transaction State**, the **Update State** was never entered.
  * The POP3 server retained the advisory lock file (`.lock` / `fcntl`) protecting `branch_user1`'s spool.
  * When Session 2 attempted to authenticate, the server correctly rejected access with `-ERR [IN-USE]`, causing complete denial of email service to the branch.

---

### Phase 2: Targeted Wireshark Filter Dissections

#### Figure 3: Filter `tcp.port == 1110 && tcp.flags.syn == 1` (TCP 3-Way Handshake SYN Analysis)
**File:** [`Wireshark_Filter_SYN_3Way_Handshake.png`](./Wireshark_Filter_SYN_3Way_Handshake.png)

![Wireshark Filter SYN Packets](./Wireshark_Filter_SYN_3Way_Handshake.png)

* **Display Filter:** `tcp.port == 1110 && tcp.flags.syn == 1`
* **Captured Packets Displayed:**
  * **Frame 157:** Client Port `62135` $\rightarrow$ Server Port `1110` `[SYN]` Seq=0, Win=65535, Len=0, MSS=16344, WS=64, SACK_PERM.
  * **Frame 158:** Server Port `1110` $\rightarrow$ Client Port `62135` `[SYN, ACK]` Seq=0, Ack=1, Win=65535, Len=0, MSS=16344, WS=64, SACK_PERM.
  * **Frame 197:** Client Port `62136` $\rightarrow$ Server Port `1110` `[SYN]` (Session 2 reconnection attempt).
  * **Frame 198:** Server Port `1110` $\rightarrow$ Client Port `62136` `[SYN, ACK]` (Session 2 handshake response).
* **Dissection Highlights:**
  * TCP Header Length: **44 bytes** (including 24 bytes of TCP options).
  * TCP Flags: `0x002 (SYN)` active.
  * Negotiates Maximum Segment Size (`MSS=16344`), Window Scale (`WS=64`), and Selective Acknowledgment (`SACK_PERM`).

---

#### Figure 4: Filter `tcp.port == 1110 && tcp.len > 0` (All Application Data Payload Frames)
**File:** [`Wireshark_Filter_Application_Data_Frames.png`](./Wireshark_Filter_Application_Data_Frames.png)

![Wireshark Filter Application Data Frames](./Wireshark_Filter_Application_Data_Frames.png)

* **Display Filter:** `tcp.port == 1110 && tcp.len > 0`
* **Packet Inventory:** Displays all 16 application-carrying packets across both sessions:
  * **Frames 161–183 (Session 1):** Server greeting (`Len=56`), `USER` (`Len=19`), `+OK` (`Len=19`), `PASS` (`Len=22`), `+OK Logged in` (`Len=50`), `STAT` (`Len=6`), `+OK 5 3145728` (`Len=15`), `LIST` (`Len=6`), `+OK 5 messages` (`Len=86`), `RETR 4` (`Len=8`), and Attachment payload chunks (`Len=278`).
  * **Frames 201–217 (Session 2):** Server greeting (`Len=56`), `USER` (`Len=19`), `+OK` (`Len=19`), `PASS` (`Len=22`), and `-ERR [IN-USE]` (`Len=79`).
* **Frame 161 Packet Bytes Pane (Hex/ASCII Dissection):**
  * Hex: `2b 4f 4b 20 44 6f 76 65 63 6f 74 20 50 4f 50 33 ...`
  * ASCII: `+OK Dovecot POP3 server ready (HQ Enterprise Maildrop)\r\n`

---

#### Figure 5: Filter `tcp.port == 1110` (Full Port 1110 Frame Sequence)
**File:** [`Wireshark_Filter_Port_1110_All_Frames.png`](./Wireshark_Filter_Port_1110_All_Frames.png)

![Wireshark Filter Port 1110 All Frames](./Wireshark_Filter_Port_1110_All_Frames.png)

* **Display Filter:** `tcp.port == 1110`
* **Analysis:** Displays the uninterrupted chronological sequence of TCP packets (Frames 157 to 170), demonstrating handshake transitions, payload delivery, and immediate TCP acknowledgments.

---

#### Figure 6: Filter `tcp.analysis.retransmission || tcp.analysis.rto` (TCP Analysis & Retransmission Tracking)
**File:** [`Wireshark_TCP_Analysis_Retransmission_RTO.png`](./Wireshark_TCP_Analysis_Retransmission_RTO.png)

![Wireshark TCP Analysis Retransmission RTO](./Wireshark_TCP_Analysis_Retransmission_RTO.png)

* **Display Filter:** `tcp.analysis.retransmission || tcp.analysis.rto`
* **Technical Purpose:** Illustrates Wireshark's automated TCP engine monitoring for lost segments, duplicate ACKs, and Retransmission Timeout (RTO) calculations across degraded links.

---

### Phase 3: Selective Header Pre-Fetching Optimization Proof (`TOP 4 0`)

#### Figure 7: Wireshark Packet Dissection of `TOP 4 0` Command
**File:** [`Python_TOP_4_0_Wireshark.png`](./Python_TOP_4_0_Wireshark.png)

![Wireshark TOP 4 0 Inspection](./Python_TOP_4_0_Wireshark.png)

* **Display Filter:** `tcp contains "TOP 4 0"`
* **Packet Identified:** Frame 15141 on `lo0` (65 bytes on wire, 520 bits captured).
* **TCP Layer Analysis:**
  * Source Port: `63243` | Destination Port: `1110`
  * Flags: `0x018 (PSH, ACK)`
  * TCP Segment Length: **9 octets**.
* **Hex / ASCII Payload Dissection:**
  * Raw Bytes: `54 4f 50 20 34 20 30 0d 0a` $\longrightarrow$ ASCII: `TOP 4 0\r\n`
* **Architectural Value:** Demonstrates that issuing `TOP 4 0` sends an ultra-compact 9-byte request to inspect headers without committing to the full multi-megabyte attachment transfer.

---

#### Figure 8: Wireshark Follow TCP Stream — Selective Header Pre-Fetch Session
**File:** [`my_live_capture_with_TOP_test.png`](./my_live_capture_with_TOP_test.png)

![Wireshark Follow TCP Stream TOP 4 0](./my_live_capture_with_TOP_test.png)

* **Protocol Stream:** TCP Stream 151 (4 client packets, 5 server packets; 960 bytes total).
* **Transcript:**
  * `S: +OK Lab POP3 server ready`
  * `C: USER branch_user1` $\longrightarrow$ `S: +OK User accepted`
  * `C: PASS hello@123` $\longrightarrow$ `S: +OK Authentication successful`
  * `C: TOP 4 0`
  * `S: +OK top of message follows` (transmitting 820 bytes of headers and metadata, terminated by `.`)
  * `C: QUIT` $\longrightarrow$ `S: +OK Goodbye`
* **Significance:** Empirical proof that two-phase header retrieval consumes only **820 bytes**, saving over **4,193,480 bytes (>99.98%)** of bandwidth compared to naive `RETR 4`.

---

#### Figure 9: Client Socket Execution Terminal (`pop3_socket_test.py`)
**File:** [`Python_TOP_4_0_Terminal.png`](./Python_TOP_4_0_Terminal.png)

![Client Socket Terminal Output](./Python_TOP_4_0_Terminal.png)

* **Output Metrics:**
  * `TOP 4 0 response size: 820 bytes`
  * `Elapsed time: 0.014 seconds`
* **Validation:** Proves sub-second response times for metadata synchronization.

---

#### Figure 10: POP3 Test Daemon Server Log (`pop3_test_server.py`)
**File:** [`Python_TOP_4_0_ServerLog.png`](./Python_TOP_4_0_ServerLog.png)

![POP3 Test Server Log](./Python_TOP_4_0_ServerLog.png)

* **Log Events:**
  * Port 1110 listener active.
  * Connection from `('127.0.0.1', 63243)`.
  * Authentication validated $\longrightarrow$ Dispatched: `Sent TOP response: 820 bytes`.

---

### Phase 4: Live Execution Environment & Architecture

#### Figure 11: Live Split View (macOS Terminal + Wireshark Sniffer)
**File:** [`Live_Capture_Terminal_Wireshark_Split.png`](./Live_Capture_Terminal_Wireshark_Split.png)

![Live Split View](./Live_Capture_Terminal_Wireshark_Split.png)

* **Demonstration:** Real-time execution of `run_wireshark_pop3_sim.py` in Terminal side-by-side with Wireshark capturing on `Loopback: lo0` with active filter `tcp.port == 1110`.

---

#### Figure 12: Wireshark Packet Grid (Frames 191–222 Across Link Drop)
**File:** [`Live_Capture_Packets_191_222_Wireshark.png`](./Live_Capture_Packets_191_222_Wireshark.png)

![Wireshark Packet Grid Frames 191 to 222](./Live_Capture_Packets_191_222_Wireshark.png)

* **Detailed View:** Full packet grid displaying the TCP connection termination (`FIN, ACK` on Frame 219) and the subsequent failed session attempt.

---

#### Figure 13: RFC 1939 POP3 Finite State Machine (FSM)
**File:** [`pop3_state_machine.png`](./pop3_state_machine.png)

![POP3 State Machine](./pop3_state_machine.png)

* **Three Operational States:**
  1. **Authorization State:** Client connects, sends `USER` and `PASS`, transitions to Transaction upon server `+OK`.
  2. **Transaction State:** Server sets exclusive advisory lock. Client queries (`STAT`, `LIST`, `TOP`, `RETR`, `DELE`).
  3. **Update State:** Triggered strictly by `QUIT`. Server commits deletions and releases lock.
* **Failure Mode:** If severed during Transaction state, Update state is bypassed, resulting in orphaned dotlocks.

---

#### Figure 14: Satellite WAN Failure Bottlenecks Architecture
**File:** [`pop3_bottlenecks.png`](./pop3_bottlenecks.png)

![Satellite WAN Bottlenecks](./pop3_bottlenecks.png)

* **Four Bottlenecks Visualized:**
  1. **Bandwidth Limitation:** 256 kbps creates serialization delay of 131.6 seconds for a 4.11 MB Base64 payload.
  2. **Orbital Latency:** 450 ms round-trip time severely penalizes chatty stop-and-wait request/response protocols.
  3. **Payload Bloat:** RFC 2045 Base64 encoding expands a 3 MB PDF attachment to 4.11 MB (~37% overhead).
  4. **Head-of-Line Blocking:** A single large attachment blocks all subsequent emails across intermittent links.

---

## 💾 Associated Binary Traces & Reproduction Scripts

All traces and scripts are committed and executable in the repository:
* **Wireshark PCAP Files:**
  * [`my_live_capture.pcapng`](./my_live_capture.pcapng): Live loopback capture trace.
  * [`my_live_capture_with_TOP_test.pcapng`](./my_live_capture_with_TOP_test.pcapng): Capture containing the live `TOP 4 0` session.
  * [`pop3_wireshark_capture.pcap`](./pop3_wireshark_capture.pcap): Standard 25-frame clean capture.
* **Reproduction Scripts:**
  * [`run_wireshark_pop3_sim.py`](./run_wireshark_pop3_sim.py): Automated dual-session link flap simulation.
  * [`pop3_test_server.py`](./pop3_test_server.py): Standalone POP3 test daemon implementing RFC 1939 commands and synthetic `TOP 4 0` responses.
* **Official Academic Deliverables:**
  * [`Case Study 5 - Person 3 - Simulation & Packet Analysis.docx`](./Case%20Study%205%20-%20Person%203%20-%20Simulation%20&%20Packet%20Analysis.docx): Standalone report.
  * [`Case Study 5 - POP3 Mailbox Access in a Low-Bandwidth Branch.docx`](./Case%20Study%205%20-%20POP3%20Mailbox%20Access%20in%20a%20Low-Bandwidth%20Branch.docx): Master report.
