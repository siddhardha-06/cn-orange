# 🔍 Traffic Classification System

> **Real-time network packet classification using Mininet + POX SDN Controller**

![Python](https://img.shields.io/badge/Python-3.6--3.9-blue?style=flat-square&logo=python)
![Mininet](https://img.shields.io/badge/Mininet-2.3+-green?style=flat-square)
![POX](https://img.shields.io/badge/POX-0.7.0-orange?style=flat-square)
![OpenFlow](https://img.shields.io/badge/OpenFlow-1.0-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)

---

## 📌 Overview

This project implements a **Traffic Classification System** using Software-Defined Networking (SDN). It captures every packet flowing through a virtual Mininet network, classifies it by protocol type, and displays live statistics directly in the terminal.

```
  h1 (10.0.0.1) ──┐
  h2 (10.0.0.2) ──┤── s1 (OVS Switch) ──── POX Controller
  h3 (10.0.0.3) ──┤        OpenFlow 1.0     (traffic_classifier.py)
  h4 (10.0.0.4) ──┘        127.0.0.1:6633
```

Every packet is intercepted, analyzed, and classified as **TCP / UDP / ICMP / OTHER** with real-time statistics shown in the terminal.

---

## ✨ Features

- 🟦 **Protocol Classification** — Identifies TCP, UDP, ICMP, and OTHER packets
- 📊 **Live Statistics** — Packet count, bytes transferred, and percentage distribution per protocol
- 📈 **ASCII Bar Charts** — Visual distribution displayed directly in terminal
- 🪵 **Packet Log** — Rolling log of last 10 classified packets with IP, port, and size details
- ⚡ **Real-time Updates** — Terminal redraws on every packet arrival
- 🌐 **SDN Architecture** — Uses OpenFlow 1.0, POX controller, Open vSwitch

---

## 🗂️ Project Structure

```
traffic_classifier/
├── traffic_classifier.py   # POX controller — core classification engine
├── topology.py             # Mininet topology (4 hosts, 1 switch)
└── setup.sh                # Automated setup script
```

---

## ⚙️ Requirements

| Tool | Version | Install |
|------|---------|---------|
| Ubuntu / Debian | 20.04+ | — |
| Python | 3.6 – 3.9 | pre-installed |
| Mininet | 2.3+ | `sudo apt install mininet` |
| Open vSwitch | 2.x+ | `sudo apt install openvswitch-switch` |
| POX Controller | 0.7.0 | `git clone https://github.com/noxrepo/pox.git` |
| iperf | any | `sudo apt install iperf` |

> ⚠️ POX works best with **Python 3.6–3.9**. On Python 3.10+ you may see version warnings, but it still functions.

> ❌ **Wireshark is NOT required.** POX captures packets directly via OpenFlow `PacketIn` events.

---

## 🚀 Setup & Run

### 1. Clone / Download the project

```bash
git clone https://github.com/yourusername/traffic-classifier.git
cd traffic-classifier
```

### 2. Install POX (if not already installed)

```bash
git clone https://github.com/noxrepo/pox.git ~/pox
```

### 3. Copy the controller into POX

```bash
cp traffic_classifier.py ~/pox/pox/misc/
```

### 4. Clean up before every session

```bash
sudo pkill -f pox.py && sudo mn -c && sleep 3
```

### 5. Terminal 1 — Start the POX Controller

```bash
cd ~/pox && python3 pox.py misc.traffic_classifier
```

Expected output:
```
✓ Switch connected: 00-00-00-00-00-01
✓ All packets will now be sent to controller
```

### 6. Terminal 2 — Start the Mininet Topology

```bash
sudo python3 topology.py
```

### 7. Generate Traffic inside Mininet CLI

```bash
# ICMP traffic
h1 ping -c 5 h2

# TCP traffic
h1 iperf -s &
h2 iperf -c 10.0.0.1

# UDP traffic
h3 iperf -u -s &
h4 iperf -u -c 10.0.0.3

# Auto-generate mixed traffic
run_demo

# Test all-pairs connectivity
pingall
```

---

## 🖥️ Terminal Output

The POX terminal clears and redraws on every packet, showing:

```
══════════════════════════════════════════════════════════════
   TRAFFIC CLASSIFICATION SYSTEM  │  POX + Mininet
══════════════════════════════════════════════════════════════
  Uptime: 42s   Total Packets: 87   Time: 22:14:35
──────────────────────────────────────────────────────────────

  PROTOCOL    PACKETS        BYTES      %   DISTRIBUTION
  ──────────────────────────────────────────────────────────
  TCP              45       61440   51.7%  ████████░░░░░░░░░░
  UDP              28       39200   32.1%  █████░░░░░░░░░░░░░
  ICMP             12         984   13.8%  ██░░░░░░░░░░░░░░░░
  OTHER             2         220    2.4%  ░░░░░░░░░░░░░░░░░░

  LAST 10 CLASSIFIED PACKETS
  ──────────────────────────────────────────────────────────
  TIME      PROTO   SRC IP          DST IP          SP     DP     SIZE
  22:14:35  TCP     10.0.0.2        10.0.0.1        5201   5201   1460B
  22:14:35  TCP     10.0.0.1        10.0.0.2        5201   58432  64B
  22:14:34  UDP     10.0.0.4        10.0.0.3        5201   5201   1470B
  22:14:33  ICMP    10.0.0.1        10.0.0.2        -      -      84B
  ...

  Latest:  [TCP]  10.0.0.2:5201  →  10.0.0.1:58432  (64B)
══════════════════════════════════════════════════════════════
```

---

## 🧠 How It Works

### SDN Architecture

In a traditional network, each switch decides how to forward packets independently. In SDN, a **central controller** (POX) makes all the decisions and pushes rules to switches via the **OpenFlow protocol**.

### Packet Classification Flow

```
Packet arrives at switch
        │
        ▼
  Table-miss rule fires
  (no matching flow rule)
        │
        ▼
  PacketIn event → POX controller
        │
        ▼
  Inspect layers:
  Ethernet → IPv4? ──No──→ OTHER
        │
       Yes
        │
        ▼
  TCP layer? ──Yes──→ TCP (extract ports)
        │
       No
        ▼
  UDP layer? ──Yes──→ UDP (extract ports)
        │
       No
        ▼
  ICMP layer? ─Yes──→ ICMP
        │
       No
        ▼
      OTHER
        │
        ▼
  Update stats + redraw terminal
        │
        ▼
  PacketOut flood (traffic continues normally)
```

### Why Every Packet Reaches the Controller

On switch connection, the controller installs a **table-miss rule** (lowest priority, match-all) that sends every packet to the controller. Unlike a learning switch that caches flow rules (causing packets to bypass the controller after the first one), this system intentionally avoids caching — ensuring **every single packet** is classified.

---

## 🐛 Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `Address already in use (port 6633)` | Old POX instance still running | `sudo pkill -f pox.py && sleep 3` |
| `RTNETLINK: File exists` | Mininet not cleaned up properly | `sudo mn -c` |
| `Module not found: misc.traffic_classifier` | Controller not copied to POX | `cp traffic_classifier.py ~/pox/pox/misc/` |
| Packets not updating in Terminal 1 | Old flood flow rule cached in switch | `sh ovs-ofctl del-flows s1` in Mininet CLI |
| `No stats file found` | Expected — stats are terminal-only | Look at Terminal 1 (POX), not Mininet terminal |

---

## 📚 Key Concepts

**SDN (Software-Defined Networking)** — Separates the control plane from the data plane. POX is the brain; OVS is the muscle.

**OpenFlow** — The protocol POX uses to communicate with the OVS switch. `PacketIn` = packet sent to controller. `PacketOut` / `flow_mod` = controller instructs the switch.

**Mininet** — Emulates a real network on one Linux machine using Linux network namespaces and Open vSwitch.

**Table-miss rule** — A match-all, lowest-priority flow rule that sends unmatched packets to the controller, ensuring every packet is inspected.

---



<p align="center">
  Built with 🐍 Python &nbsp;|&nbsp; Mininet &nbsp;|&nbsp; POX SDN &nbsp;|&nbsp; OpenFlow 1.0
</p>
