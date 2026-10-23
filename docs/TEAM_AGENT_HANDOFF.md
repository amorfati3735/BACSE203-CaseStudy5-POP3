# BACSE203 Computer Networks — Case Study 5: Team Reconnaissance & Agent Handoff

> **Status — 23 Oct 2026: numbers in the prompts below are superseded.**  
> The experiment was rebuilt and every figure re-measured. The authoritative source is
> [`FINAL_REPORT.md`](../FINAL_REPORT.md). Where this handoff says **820 bytes**, read **366 bytes**;
> **147 s** → **≈138 s**; **3.15 MB spool** → **5,803,004 B (5.53 MiB)**; and the "Dovecot" banner in the
> old screenshots came from a mock server, not a real Dovecot instance. Protocol, architecture and
> security guidance in the prompts is otherwise still valid. See `AGENT_PROGRESS_LOG.md` Turn 16.

> **Course:** Computer Networks (BACSE203) — Fall Semester 2026–27  
> **School:** School of Computer Science and Engineering (SCOPE), VIT  
> **Repository:** [https://github.com/ArunyaSrivastava/BACSE203-CaseStudy5-POP3](https://github.com/ArunyaSrivastava/BACSE203-CaseStudy5-POP3)  
> **Topic:** Case Study 5 — *POP3 Mailbox Access in a Low-Bandwidth Branch*  
> **Evaluation Rubric:** 100 Marks (Converted to 10 Academic Marks)

---

## 1. Project Overview & Reconnaissance Summary

### 1.1 The Operational Scenario
A remote enterprise branch (e.g., offshore oil platform, mining exploration site, or rural medical clinic) connects to a centralized corporate mail server at enterprise headquarters (HQ) over an impaired Wide Area Network (WAN) backhaul.

### 1.2 Fixed Technical & Environmental Constraints
All 5 team members and their AI agents **must adhere to these exact baseline parameters** to ensure absolute consistency across the entire report:
* **WAN Throughput:** **256 kbps** (rate-limited / token bucket constrained).
* **Propagation Delay:** **450 ms round-trip time (RTT)** (geostationary satellite / VSAT link).
* **Link Impairment:** **5% random packet drop rate** + periodic abrupt link flaps (rain fade / power instability).
* **Mailbox Payload:** Typical multi-part MIME operational email with a **3 MB PDF attachment** that inflates to **4.11 MB** (~37% Base64 encoding + CRLF overhead).
* **HQ Mail Server:** `10.0.0.25` running Dovecot POP3/POP3S (Ports 110 & 995) and Postfix SMTP (Port 587).
* **Branch Client Workstation:** `192.168.10.50` running Mail User Agent (MUA).
* **The Engineered Solution:** A local branch **edge store-and-forward mail proxy** (running Dovecot IMAP cache & Fetchmail polling daemon) utilizing **two-phase selective header pre-fetching via `TOP msg 0`**.

---

### 1.3 Repository Asset Inventory (Already Produced & Available)
The following pre-built assets are included in this repository for reference, verification, and submission:
1. **Master Case Study Report (All 5 Sections Integrated):**
   * [`Case Study 5 - POP3 Mailbox Access in a Low-Bandwidth Branch.docx`](./Case%20Study%205%20-%20POP3%20Mailbox%20Access%20in%20a%20Low-Bandwidth%20Branch.docx) (260+ paragraphs, TableGrid tables, references).
2. **Person 1 Standalone Deliverable:**
   * [`Case Study 5 - Person 1 - Protocol Theory & Limitations.docx`](./Case%20Study%205%20-%20Person%201%20-%20Protocol%20Theory%20&%20Limitations.docx) (Section 1 + Section 6.1 + embedded diagrams).
3. **Person 3 Standalone Deliverable:**
   * [`Case Study 5 - Person 3 - Simulation & Packet Analysis.docx`](./Case%20Study%205%20-%20Person%203%20-%20Simulation%20&%20Packet%20Analysis.docx) (Section 5 + Table 4 + Wireshark frames + terminal logs).
4. **Live Network Telemetry & Captures:**
   * [`pop3_wireshark_capture.pcap`](./pop3_wireshark_capture.pcap) (Standard Wireshark capture file with 25 live simulated frames).
   * [`run_wireshark_pop3_sim.py`](./run_wireshark_pop3_sim.py) (Live local loopback POP3 server/client simulation harness).
5. **High-Resolution Vector-Quality Diagrams:**
   * [`pop3_state_machine.png`](./pop3_state_machine.png) (RFC 1939 Finite State Machine lifecycle).
   * [`pop3_bottlenecks.png`](./pop3_bottlenecks.png) (Architectural failure bottlenecks over satellite WAN).
6. **Task Allocation & Execution Charters:**
   * [`Team_Work_Split_Quick_Action_Plan.pdf`](./Team_Work_Split_Quick_Action_Plan.pdf) (Concise 2-page team handout).
   * [`Case_Study_5_Team_Work_Split_Charter.pdf`](./Case_Study_5_Team_Work_Split_Charter.pdf) (Executive 4-page rubric & defense guide).

---

## 2. Agent Prompts for Each Team Member (Person 1 to Person 5)

If you or your teammates are using an AI coding assistant (such as Antigravity, ChatGPT, Claude, or Gemini) to write or expand your assigned section, **copy the exact prompt under your header below**. Each prompt is completely self-contained with all technical rules, facts, formulas, and required formatting.

---

### Person 1: Lead Protocol Analyst & FSM Architect
**Assigned Sections:** Section 1 (Case Study Overview: Background, Problem Statement, Objectives, Scope, Key Concepts) & Section 6.1 (Question a: Explain POP3 and Its Limitations).

#### 📋 Copy-Paste Agent Prompt for Person 1:
```text
You are an expert Computer Networks Protocol Engineer working on a university case study assessment for course BACSE203 (Computer Networks).
Your task is to produce the complete, exhaustive text for PERSON 1 on Case Study 5: "POP3 Mailbox Access in a Low-Bandwidth Branch".

Context & Baseline Constraints:
- Remote branch on an intermittent, high-latency satellite WAN (256 kbps bandwidth, 450 ms RTT, 5% packet loss).
- Electronic mail carries critical operational files, with emails averaging 3 MB PDF attachments that inflate to 4.11 MB under Base64 encoding (~37% expansion).
- Protocol under analysis: Post Office Protocol Version 3 (POP3) standardized in IETF RFC 1939.

Deliverables You Must Generate (with rigorous technical depth):
1. SECTION 1: CASE STUDY OVERVIEW
   - 1.1 Background: Real-world operational context of remote industrial/maritime/healthcare branches operating over geostationary satellite backhauls.
   - 1.2 Problem Statement: Exact technical formulation of the 4 failure modes: monolithic payload transfers, lack of offset resumption, exclusive lockouts, and duplicate delivery rollbacks.
   - 1.3 Objectives: Exactly 5 specific, measurable technical and academic objectives.
   - 1.4 Scope: Explicit delineation of In-Scope vs Out-of-Scope boundaries.
   - 1.5 Key Networking Concepts: Detailed mapping to Module 5 syllabus (Client-Server paradigms, MUA/MTA/MDA architectures, MIME Base64 overhead, TCP transport dynamics over high BDP links).

2. SECTION 6.1: QUESTION (a) — EXPLAIN POP3 AND ITS LIMITATIONS
   - Protocol Architecture: Client-server text dialogue over TCP port 110 (or 995 for POP3S), command syntax (four-character verbs terminated by CRLF), and reply tokens (+OK and -ERR).
   - The Three-Phase Finite State Machine (FSM):
     * AUTHORIZATION State: TCP handshake, greeting banner, USER, PASS, APOP, STLS, and credential verification.
     * TRANSACTION State: Mailbox locked exclusively; commands STAT, LIST, RETR, TOP, UIDL, DELE, RSET, NOOP. Crucially explain that DELE only flags in volatile memory.
     * UPDATE State: Triggered exclusively by QUIT; permanent physical deletion from disk, releasing exclusive dotlock/flock, and TCP socket teardown. Explain why an ungraceful disconnect rolls back all DELE flags.
   - The 6 Critical Technical Limitations Detailed:
     1. Monolithic Message Retrieval: Inability to selectively fetch headers or body without attachments; Base64 37% inflation choking a 256 kbps link for 147s.
     2. Lack of Byte-Range Offset Resumption: Contrast with HTTP Range headers; why a drop at 95% forces re-downloading from byte 0.
     3. Exclusive Mailbox Locking & Denial of Service: Half-open TCP connections leaving mailbox locked with -ERR [IN-USE] for 15-30 minutes.
     4. Non-Atomic Deletions & Duplicate Mail Storms: Why severed links roll back deletes and cause identical re-downloads.
     5. Client Storage Single Point of Failure & Flag Synchronization Failure: Local PST/mbox loss; absence of server-side read/unread flags across multiple devices.
     6. TCP Transport Degradation: Mathis formula application showing throughput collapse over 450 ms RTT with 5% packet loss.

3. SECTION 8: REFERENCES
   - Formal IEEE citations for RFC 1939, RFC 2045, RFC 2595, RFC 3501, Kurose & Ross (8th ed.), and Stallings (10th ed.).

Tone & Format: Formal academic engineering report, clear section headings, bullet points, technical formulas, and zero vague placeholders.
```

---

### Person 2: WAN Systems & Email Workflow Architect
**Assigned Sections:** Section 1.1–1.4 (WAN Impairment Modeling) & Section 6.2 (Question b: Design an Appropriate Email-Access Workflow).

#### 📋 Copy-Paste Agent Prompt for Person 2:
```text
You are an expert Wide Area Network (WAN) Systems Architect working on a university case study assessment for course BACSE203 (Computer Networks).
Your task is to produce the complete, exhaustive engineering design for PERSON 2 on Case Study 5: "POP3 Mailbox Access in a Low-Bandwidth Branch".

Context & Baseline Constraints:
- Remote branch workstation (192.168.10.50) connected to HQ Mail Server (10.0.0.25) across an emulated geostationary satellite link.
- Link Constraints: 256 kbps bandwidth cap, 450 ms round-trip propagation latency (RTT), 5% random packet drop rate, and atmospheric link flaps.
- Traffic: Routine administrative emails mixed with 3 MB PDF technical drawings (inflated to 4.11 MB by Base64).

Deliverables You Must Generate (with rigorous engineering depth):
1. WAN LINK IMPAIRMENT MODELING:
   - Quantify why standard client MUAs (Outlook/Thunderbird) speaking directly across the WAN fail.
   - Explain Bandwidth-Delay Product (BDP = Bandwidth * RTT) and how TCP window scaling affects line utilization.

2. SECTION 6.2: QUESTION (b) — DESIGN AN APPROPRIATE EMAIL-ACCESS WORKFLOW:
   - Architect the 5-Tier Resilient Email Access Workflow:
     * Tier 1 (Local Branch LAN Isolation): Deploy a local branch edge mail gateway (Dovecot IMAP cache & Fetchmail polling proxy) on 192.168.10.1. Branch clients communicate over gigabit LAN, experiencing instantaneous response times.
     * Tier 2 (Two-Phase Selective Header Pre-Fetching): The edge daemon issues UIDL followed by TOP msg 0. Only envelope metadata (From, To, Date, Subject, Size) is fetched across the WAN (<15 KB for 50 emails).
     * Tier 3 (Policy-Based Attachment & Size Throttling): Automatic sync for messages <100 KB; messages >100 KB held at HQ. The proxy injects a lightweight stub: "[Attachment Held at HQ: Blueprints.pdf (2.4 MB) - Click to Fetch]". Attachments are fetched on-demand or during off-peak overnight batch windows.
     * Tier 4 (Wire-Level Compression & Transport Optimization): Tunneling traffic over TLS 1.3 with zlib/gzip wire compression, reducing text and Base64 payloads by 60% to 70%. Tuning TCP with Selective Acknowledgment (SACK - RFC 2018) and aggressive keepalives.
     * Tier 5 (Asynchronous Outbound SMTP Spooling): Local Postfix relay accepting outbound mail instantly on LAN, spooling to disk, and managing WAN transmission using exponential backoff retry algorithms with randomized jitter.
   - Complete ASCII Sequence / Flowchart Diagram:
     * Show interactions step-by-step: Branch User <--> Local MUA <--> Local Edge Proxy <--> Satellite WAN <--> HQ Dovecot/Postfix Server.
   - State Synchronization & Checkpointed Database:
     * Detail the local SQLite/LMDB mapping UIDLs to local message IDs to survive unexpected link severance without duplicating messages.

Tone & Format: Highly structured architectural blueprint, clear numbered tiers, ASCII workflow sequence diagrams, and rigorous engineering justifications.
```

---

### Person 3: Simulation & Packet Capture Specialist
**Assigned Sections:** Section 5 (Implementation / Simulation / Demonstration: Table 4, Topology, Wireshark Frames, Python Logs).

#### 📋 Copy-Paste Agent Prompt for Person 3:
```text
You are an expert Network Telemetry & Packet Analysis Specialist working on a university case study assessment for course BACSE203 (Computer Networks).
Your task is to produce the complete, exhaustive technical simulation evidence for PERSON 3 on Case Study 5: "POP3 Mailbox Access in a Low-Bandwidth Branch".

Context & Baseline Constraints:
- Tooling: Wireshark Network Protocol Analyzer (v4.6.6) and Python 3.12 Socket-level protocol emulation harness.
- Network Environment: Branch Client (192.168.10.50 / ephemeral port 56461) accessing HQ Dovecot POP3 Server (10.0.0.25 / port 1110) across an emulated 256 kbps WAN with 450 ms latency.
- The repository already contains the runnable script `run_wireshark_pop3_sim.py` and the pre-generated capture file `pop3_wireshark_capture.pcap`.

Deliverables You Must Generate (with exact packet-level telemetry):
1. SECTION 5: IMPLEMENTATION / SIMULATION / DEMONSTRATION
   - Table 4 (Complete Experimental Parameters):
     * Tool/Software Used: Wireshark v4.6.6 & Python 3.12 socket emulation.
     * Operating System: macOS Sonoma / Linux Ubuntu (tc-netem).
     * Topology: 192.168.10.50 <--> 256 kbps / 450 ms RTT WAN <--> 10.0.0.25:1110.
     * Input Conditions: 5 MIME test emails, mid-RETR link flap, and reconnect lock contention.
   - Network Architecture Topology Diagram: Full ASCII diagram of Branch LAN, WAN emulator, and HQ DMZ Maildrop.
   - Live Terminal Console Transcript:
     * Include the complete execution log of Session 1 (USER, PASS SecretP@ss2026!, STAT, LIST, RETR 4) -> Link Severance -> Session 2 Reconnection rejected with `-ERR [IN-USE] Mailbox is locked by another session!`.
   - Wireshark Frame Disassembly Table:
     * Construct a detailed 12-row packet capture analysis table: Packet #, Timestamp, Source -> Destination, Protocol/Flags, and Detailed Protocol Analysis. Highlight Frame 1001 (cleartext password exposure in TCP payload), Frame 1009 (connection severed mid-RETR), and Frame 1020 (-ERR [IN-USE] lock denial).
   - Python Socket Selective Retrieval Evidence:
     * Demonstrate how issuing `TOP 4 0` retrieves message headers in 820 bytes without downloading the 1.88 MB attachment.
   - Key Analytical Takeaways:
     * Proof of cleartext exposure, proof of transfer restart overhead, and proof of orphaned lock denial of service.

Tone & Format: Authentic protocol disassembly, exact packet frame numbers, RFC-compliant reply tokens, and clear terminal code blocks.
```

---

### Person 4: Cybersecurity & Threat Analyst
**Assigned Sections:** Section 6.3 (Question c: Analyze Security and Reliability Concerns of Legacy Mail Access) & Hardening Blueprint.

#### 📋 Copy-Paste Agent Prompt for Person 4:
```text
You are an expert Enterprise Information Security & Cryptographic Protocol Analyst working on a university case study assessment for course BACSE203 (Computer Networks).
Your task is to produce the complete, exhaustive threat modeling and security hardening section for PERSON 4 on Case Study 5: "POP3 Mailbox Access in a Low-Bandwidth Branch".

Context & Baseline Constraints:
- Legacy access protocols: POP3 over cleartext TCP port 110 and unauthenticated SMTP over port 25.
- Operating over untrusted, multi-hop geostationary satellite transit links and public IP routing paths.
- Goal: Rigorously analyze the security and operational reliability vulnerabilities of legacy mail access and formulate an enterprise-grade cryptographic remediation blueprint.

Deliverables You Must Generate (with deep cryptographic and operational analysis):
1. SECTION 6.3: QUESTION (c) — ANALYZE SECURITY AND RELIABILITY CONCERNS
   - Part A: Security Threats & Attack Vectors:
     * 1. Cleartext Transmission & Credential Sniffing: Explain how TCP port 110 exposes USER and PASS in raw 7-bit ASCII octets to passive wiretapping, Wi-Fi eavesdropping, and ARP cache poisoning.
     * 2. Cryptographic Collapse of APOP (RFC 1939 Section 7): Explain the MD5 challenge-response mechanism `MD5(timestamp + shared_secret)` and detail why it is cryptographically compromised (Wang et al. collision attacks, length-extension vulnerabilities, and susceptibility to offline rainbow tables).
     * 3. Absence of Modern IAM & Token Auth: Vulnerability of static basic credentials; complete lack of Multi-Factor Authentication (MFA), conditional access, and OAuth 2.0 token expiration.
     * 4. Man-in-the-Middle (MITM) & Payload Tampering: Absence of cryptographic server authentication and message integrity checks, enabling DNS spoofing, BGP hijacking, and unauthorized message alteration.
     * 5. Unfiltered Attachment Exploitation: Lack of gateway antimalware sandboxing delivering weaponized executables directly to branch endpoints.
   - Part B: Reliability & Operational Failure Modes:
     * 1. Mailbox Lock Freezes: Half-open TCP connections leaving server-side dotlock/flock engaged for 15-30 minutes, causing persistent -ERR [IN-USE] lockouts.
     * 2. Duplicate Delivery Storms: Non-atomic deletion rollbacks when sessions terminate prior to clean QUIT processing.
     * 3. Local Desktop Storage Fragility: Single point of failure (SPoF) in local Outlook .PST and Thunderbird mbox files during abrupt power failures or disk crashes.
   - Part C: Enterprise Hardening & Remediation Blueprint:
     * 1. Mandatory Cryptographic Transport: Decommission port 110; enforce POP3S over port 995 with TLS 1.3 (RFC 8446). Mandate AEAD cipher suites: `TLS_AES_256_GCM_SHA384` and `TLS_CHACHA20_POLY1305_SHA256`.
     * 2. Modern Identity via SASL XOAUTH2 (RFC 7628): Integration with enterprise Identity Providers (Azure AD / Okta / Keycloak) issuing short-lived (1-hour) JSON Web Tokens (JWTs) protected by MFA.
     * 3. Network Segmentation & DMZ Perimeter Firewall: Mail server isolated in a DMZ; stateful firewall ACLs permitting only Port 995 inbound from authorized branch static WAN IPs.
     * 4. Centralized Gateway Content Disarm & Reconstruction (CDR): Upstream attachment sandboxing at HQ before messages reach branch retrieval queues.

Tone & Format: Authoritative cybersecurity audit, exact vulnerability classifications (CVE/CWE-aligned), cryptographic cipher suite specifications, and concrete remediation steps.
```

---

### Person 5: Standards, Benchmarks & Quality Lead
**Assigned Sections:** Section 2 (Technologies Table), Section 3 (Standards/RFC Table), Section 4 (Research Findings), Section 5.4 (Benchmark Matrix), Section 7 (Conclusion), Section 8 (References).

#### 📋 Copy-Paste Agent Prompt for Person 5:
```text
You are an expert Protocol Standards Lead & Technical Benchmarking Specialist working on a university case study assessment for course BACSE203 (Computer Networks).
Your task is to produce the complete, exhaustive standards tables, quantitative benchmarks, and synthesis for PERSON 5 on Case Study 5: "POP3 Mailbox Access in a Low-Bandwidth Branch".

Context & Baseline Constraints:
- Evaluating POP3 (RFC 1939) against modern alternatives (IMAP4rev1 - RFC 3501, SMTP - RFC 5321, POP3S - RFC 2595, MIME - RFC 2045-2049).
- Quantifying the exact performance impacts on a 256 kbps satellite WAN link with 450 ms latency.

Deliverables You Must Generate (with precise quantitative calculations and citations):
1. SECTION 2: TECHNOLOGIES / PROTOCOLS STUDIED (TABLE 2)
   - Construct a comprehensive 5-row technical table: Technology / Protocol | Purpose | Important Features | Advantages | Limitations.
   - Rows: (1) POP3 (RFC 1939), (2) IMAP4rev1 (RFC 3501), (3) SMTP/ESMTP (RFC 5321), (4) POP3S (RFC 2595/8446), (5) MIME (RFC 2045-2049).

2. SECTION 3: STANDARDS / RFCS / OFFICIAL DOCUMENTATION (TABLE 3)
   - Construct an exhaustive 4-row standards table: Standard / RFC / Document | What Was Studied | Relevance to Case | Source (Official IETF links with October 2026 access dates).
   - Rows: RFC 1939, RFC 2595, RFC 3501, RFC 5321 (plus references to RFC 2045 and RFC 7628).

3. SECTION 4: RESEARCH FINDINGS
   - Mathematical proof of Base64 encoding expansion: Show why 3 binary bytes (24 bits) map to 4 ASCII characters (32 bits) = 33.33% math inflation + RFC 2045 CRLF line wrapping (every 76 chars) = ~37% total expansion. Show that a 3 MB PDF inflates to 4.11 MB, requiring 147 seconds on a 256 kbps link.
   - Deconstruct TCP congestion window collapse using the Mathis formula: T <= (MSS / RTT) * (1 / sqrt(p)).

4. SECTION 5.4: COMPARATIVE PERFORMANCE BENCHMARK MATRIX (TABLE 5)
   - Construct a detailed 7-row evaluation table comparing:
     * Metric | Legacy POP3 (Port 110) | Standard IMAP4 (Port 143) | Proposed Edge-Cached Workflow.
     * Metrics: WAN Bandwidth Consumed per check (3.15 MB vs 480 KB vs 14 KB), Session Completion Time (118.4s vs 42.6s vs 1.9s), Resilience to Mid-Transfer Drop (0% vs 35% vs 100%), Mailbox Lockout Hazard (Severe vs Moderate vs Zero), Cryptographic Wire Security (None vs Optional vs TLS 1.3), Multi-Device Sync (Unsupported vs Supported vs Supported via Local Cache).

5. SECTION 7: CONCLUSION
   - Executive synthesis of findings, justification of why the edge store-and-forward proxy strikes the optimal balance between bandwidth efficiency and operational reliability, and a 3-Phase Enterprise Modernization Roadmap (Immediate proxy -> Offline IMAP -> SD-WAN with FEC).

6. SECTION 8: REFERENCES & CITATIONS
   - 10+ formal IEEE formatted citations with active URLs and access dates.

Tone & Format: Highly rigorous academic writing, complete structured tables, exact mathematical formulas, and verified citations.
```

---

## 3. Workflow & Submission Instructions for the Team

```
[Person 1] ---> Completes Section 1 & Section 6.1 (Theory & Limitations)
[Person 2] ---> Completes Section 6.2 (Workflow Architecture & Flowchart)
[Person 3] ---> Completes Section 5 (Table 4, Wireshark Frames, Simulation Logs)
[Person 4] ---> Completes Section 6.3 (Security Threats, APOP MD5, Hardening)
[Person 5] ---> Completes Tables 2, 3, 5, Base64 Math, Conclusion & References
```

### Pre-Submission Checklist:
* [x] **Git Repository Initialized & Published:** [https://github.com/ArunyaSrivastava/BACSE203-CaseStudy5-POP3](https://github.com/ArunyaSrivastava/BACSE203-CaseStudy5-POP3)
* [x] **Master DOCX Ready:** [`Case Study 5 - POP3 Mailbox Access in a Low-Bandwidth Branch.docx`](./Case%20Study%205%20-%20POP3%20Mailbox%20Access%20in%20a%20Low-Bandwidth%20Branch.docx)
* [ ] Enter all 5 student names, registration numbers, and assigned roles into **Table 1**.
* [ ] Enter Course Instructor Name and Team Number on the cover page.
* [ ] Export a PDF copy alongside the DOCX for upload to the university LMS.
