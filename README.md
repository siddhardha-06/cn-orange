# Traffic Classification System
### Mininet + POX SDN | Network Traffic Analyzer

---

## Project Overview

This system classifies network traffic by protocol type (TCP, UDP, ICMP, OTHER) using:
- **Mininet** — Software-defined network emulator
- **POX** — Python-based OpenFlow SDN controller
- **Dashboard** — Live HTML visualization of traffic stats

---

## File Structure

```
traffic_classifier/
├── pox_controller/
│   └── traffic_classifier.py   ← POX controller (core logic)
├── topology.py                  ← Mininet topology (4 hosts, 1 switch)
├── dashboard.html               ← Live traffic dashboard
├── setup_and_run.sh             ← Automated setup script
└── README.md
```

---

## How It Works

```
  h1 ──┐
  h2 ──┤── s1 (OVS Switch) ──── POX Controller
  h3 ──┤        OpenFlow         (traffic_classifier.py)
  h4 ──┘
```

1. Hosts send packets → OVS switch → POX receives `PacketIn` events
2. Controller inspects each packet's L3/L4 headers
3. Classifies as TCP / UDP / ICMP / OTHER
4. Maintains cumulative statistics (count + bytes per protocol)
5. Writes stats to `/tmp/traffic_stats.json` every packet
6. Dashboard reads the JSON and updates in real time

---

## Requirements

| Tool | Install |
|------|---------|
| Mininet | `sudo apt install mininet` |
| POX | `git clone https://github.com/noxrepo/pox.git` |
| Open vSwitch | `sudo apt install openvswitch-switch` |
| Python 3 | Pre-installed on Ubuntu |

---

## Step-by-Step Setup

### Step 1 — Install POX (if not already)
```bash
cd ~
git clone https://github.com/noxrepo/pox.git
```

### Step 2 — Copy the Controller
```bash
cp pox_controller/traffic_classifier.py ~/pox/pox/misc/
```

### Step 3 — Start POX Controller (Terminal 1)
```bash
cd ~/pox
python3 pox.py misc.traffic_classifier
```

You should see:
```
INFO:traffic_classifier:Traffic Classifier module loaded
INFO:openflow.of_01:Listening on 0.0.0.0:6633
```

### Step 4 — Start Mininet Topology (Terminal 2)
```bash
sudo python3 topology.py
```

You should see the Mininet CLI:
```
*** Network is ready ***
mininet>
```

### Step 5 — Generate Traffic

Inside the Mininet CLI:

```bash
# Auto-generate mixed traffic (ICMP + TCP + UDP)
mininet> run_demo

# Or manually:
mininet> h1 ping h2              # ICMP
mininet> h1 iperf -s &           # TCP server
mininet> h2 iperf -c 10.0.0.1   # TCP client
mininet> h3 iperf -u -s &        # UDP server
mininet> h4 iperf -u -c 10.0.0.3 # UDP client

# Show statistics in CLI
mininet> show_stats
```

### Step 6 — View Dashboard

Open `dashboard.html` in a browser, OR serve it locally:
```bash
cd traffic_classifier/
python3 -m http.server 8080
# Open http://localhost:8080/dashboard.html
```

---

## Statistics Output

The controller writes `/tmp/traffic_stats.json`:

```json
{
  "stats": {
    "TCP":   { "count": 142, "bytes": 189320 },
    "UDP":   { "count": 87,  "bytes": 124500 },
    "ICMP":  { "count": 30,  "bytes": 2520   },
    "OTHER": { "count": 5,   "bytes": 380    }
  },
  "packet_log": [...],
  "uptime": 45.2,
  "total_packets": 264,
  "timestamp": "14:32:01"
}
```

---

## Dashboard Features

| Feature | Description |
|---------|-------------|
| Protocol Cards | Live count + bytes per protocol |
| Bar Charts | Packet and byte distribution |
| Donut Chart | Protocol share (%) |
| Sparkline | Packet rate over time |
| Packet Log | Last 20 classified packets with IP/port details |

---

## Topology Details

| Host | IP Address |
|------|------------|
| h1 | 10.0.0.1/24 |
| h2 | 10.0.0.2/24 |
| h3 | 10.0.0.3/24 |
| h4 | 10.0.0.4/24 |

- Switch: `s1` (Open vSwitch, OpenFlow 1.0)
- Controller: POX on `127.0.0.1:6633`
- Link bandwidth: 10 Mbps, delay: 5ms

---

## Troubleshooting

**"Connection refused" in POX**
→ Make sure Mininet is using `RemoteController` and POX is running first.

**No stats file created**
→ Check `/tmp/traffic_stats.json` exists; ensure POX has write permission to `/tmp`.

**Dashboard not updating**
→ The dashboard uses demo mode if the file isn't accessible over HTTP. Serve with `python3 -m http.server`.

**Mininet cleanup**
```bash
sudo mn -c
```
