#!/usr/bin/env python3
"""
Traffic Classification System - Mininet Topology
4 hosts + 1 switch, controlled by POX Traffic Classifier.

Usage:
  sudo python3 topology.py
"""

from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import time, threading, os, json

R  = "\033[0;31m"
G  = "\033[0;32m"
Y  = "\033[1;33m"
C  = "\033[0;36m"
M  = "\033[0;35m"
W  = "\033[1;37m"
DIM= "\033[2m"
NC = "\033[0m"
BOLD="\033[1m"

def fmt_bytes(b):
    if b < 1024: return f"{b} B"
    if b < 1048576: return f"{b/1024:.1f} KB"
    return f"{b/1048576:.2f} MB"

def print_banner():
    os.system("clear")
    print(f"{C}{'═'*62}{NC}")
    print(f"{BOLD}{C}      TRAFFIC CLASSIFICATION SYSTEM  │  Mininet{NC}")
    print(f"{C}{'═'*62}{NC}")

def print_topology():
    print(f"""
  {W}Network Topology:{NC}

    {G}h1{NC} (10.0.0.1) ──┐
    {G}h2{NC} (10.0.0.2) ──┤── {Y}s1{NC} ──── {C}POX Controller{NC}
    {G}h3{NC} (10.0.0.3) ──┤      {DIM}OpenFlow 1.0{NC}
    {G}h4{NC} (10.0.0.4) ──┘      {DIM}127.0.0.1:6633{NC}

  {DIM}Link: 10 Mbps, 5ms delay{NC}
""")

def create_topology():
    print_banner()
    print_topology()

    net = Mininet(
        controller=RemoteController,
        switch=OVSSwitch,
        link=TCLink,
        autoSetMacs=True
    )

    info(f"{C}[*] Adding controller...{NC}\n")
    c0 = net.addController("c0", controller=RemoteController,
                           ip="127.0.0.1", port=6633)

    info(f"{C}[*] Adding switch and hosts...{NC}\n")
    s1 = net.addSwitch("s1")
    h1 = net.addHost("h1", ip="10.0.0.1/24")
    h2 = net.addHost("h2", ip="10.0.0.2/24")
    h3 = net.addHost("h3", ip="10.0.0.3/24")
    h4 = net.addHost("h4", ip="10.0.0.4/24")

    for h in [h1, h2, h3, h4]:
        net.addLink(h, s1, bw=10, delay="5ms")

    info(f"{C}[*] Starting network...{NC}\n")
    net.start()

    print(f"{G}{'═'*62}{NC}")
    print(f"{BOLD}{G}  ✓  Network is UP — Mininet CLI ready{NC}")
    print(f"{G}{'═'*62}{NC}")
    print(f"""
  {BOLD}Available CLI commands:{NC}

    {Y}run_demo{NC}      — auto-generate TCP + UDP + ICMP traffic
    {Y}show_stats{NC}    — print traffic stats from the controller
    {Y}pingall{NC}       — test all-pairs ICMP connectivity
    {Y}h1 ping h2{NC}    — manual ICMP
    {Y}h1 iperf -s &{NC} + {Y}h2 iperf -c h1{NC}   — TCP
    {Y}h3 iperf -u -s &{NC} + {Y}h4 iperf -u -c h3{NC} — UDP
""")

    class CustomCLI(CLI):
        def do_run_demo(self, _):
            "Auto-generate mixed TCP/UDP/ICMP traffic for 30 seconds"
            print(f"\n{C}{'─'*50}{NC}")
            print(f"{BOLD}{Y}  Starting traffic demo...{NC}")
            print(f"{C}{'─'*50}{NC}")

            def go():
                print(f"  {G}[ICMP]{NC} h1 → h2  &  h3 → h4")
                h1.cmd("ping -c 8 10.0.0.2 &")
                h3.cmd("ping -c 8 10.0.0.4 &")
                time.sleep(2)

                print(f"  {C}[TCP]{NC}  h1 (server) ← h2 (client)")
                h1.cmd("iperf -s &")
                time.sleep(1)
                h2.cmd("iperf -c 10.0.0.1 -t 10 &")
                time.sleep(2)

                print(f"  {Y}[UDP]{NC}  h3 (server) ← h4 (client)")
                h3.cmd("iperf -u -s &")
                time.sleep(1)
                h4.cmd("iperf -u -c 10.0.0.3 -t 10 &")
                time.sleep(2)

                print(f"  {G}[ICMP]{NC} h2 → h4 (burst)")
                h2.cmd("ping -c 15 10.0.0.4 &")
                time.sleep(15)

                print(f"\n{G}  ✓ Demo complete!{NC} Use {Y}show_stats{NC} to view summary.\n")

            threading.Thread(target=go, daemon=True).start()

        def do_show_stats(self, _):
            "Display traffic statistics from the POX controller"
            stats_file = "/tmp/traffic_stats.json"
            if not os.path.exists(stats_file):
                print(f"\n{R}  No stats file found.{NC} "
                      f"Make sure the POX controller is running.\n")
                return

            with open(stats_file) as f:
                data = json.load(f)

            stats = data["stats"]
            total = data["total_packets"]
            COLORS = {"TCP": C, "UDP": Y, "ICMP": G, "OTHER": M}

            print(f"\n{C}{'═'*55}{NC}")
            print(f"{BOLD}{W}  TRAFFIC STATISTICS SUMMARY{NC}")
            print(f"{C}{'═'*55}{NC}")
            print(f"  {DIM}Uptime:{NC} {W}{data['uptime']}s{NC}  "
                  f"{DIM}Total Packets:{NC} {W}{total}{NC}  "
                  f"{DIM}Time:{NC} {W}{data['timestamp']}{NC}")
            print(f"{C}{'─'*55}{NC}")
            print(f"  {BOLD}{'PROTO':<8} {'PACKETS':>8} {'BYTES':>12} {'%':>7}{NC}")
            print(f"  {'─'*45}")

            total_bytes = sum(v["bytes"] for v in stats.values())
            for p, col in COLORS.items():
                s = stats[p]
                pct = (s["count"] / total * 100) if total > 0 else 0
                print(f"  {col}{BOLD}{p:<8}{NC} {W}{s['count']:>8}{NC} "
                      f"{DIM}{fmt_bytes(s['bytes']):>12}{NC} "
                      f"{col}{pct:>6.1f}%{NC}")

            print(f"{C}{'─'*55}{NC}")
            print(f"  {BOLD}{'TOTAL':<8} {total:>8} {fmt_bytes(total_bytes):>12}{NC}")
            print(f"{C}{'═'*55}{NC}")

            print(f"\n  {BOLD}Last 5 packets:{NC}")
            print(f"  {DIM}{'TIME':<9} {'PROTO':<7} {'SRC':<15} {'DST':<15} {'SIZE'}{NC}")
            for p in data.get("packet_log", [])[-5:]:
                col = COLORS.get(p["proto"], W)
                print(f"  {DIM}{p['time']:<9}{NC}{col}{BOLD}{p['proto']:<7}{NC}"
                      f"{W}{p['src']:<15}{NC}{DIM}{p['dst']:<15}{NC}"
                      f"{DIM}{p['size']} B{NC}")
            print()

    CustomCLI(net)

    info(f"{Y}[*] Stopping network...{NC}\n")
    net.stop()

if __name__ == "__main__":
    setLogLevel("warning")
    create_topology()
