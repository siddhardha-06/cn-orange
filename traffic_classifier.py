"""
Traffic Classification System - POX Controller
Classifies TCP, UDP, ICMP packets and displays stats in terminal.
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.revent import *
import time
import os

log = core.getLogger()

# ANSI colors
R  = "\033[0;31m"
G  = "\033[0;32m"
Y  = "\033[1;33m"
C  = "\033[0;36m"
M  = "\033[0;35m"
B  = "\033[1;34m"
W  = "\033[1;37m"
DIM= "\033[2m"
NC = "\033[0m"
BOLD="\033[1m"

def clear():
    os.system("clear")

def fmt_bytes(b):
    if b < 1024: return f"{b} B"
    if b < 1048576: return f"{b/1024:.1f} KB"
    return f"{b/1048576:.2f} MB"

def bar(count, total, width=20, color=W):
    filled = int((count / total) * width) if total > 0 else 0
    return color + "█" * filled + DIM + "░" * (width - filled) + NC

class TrafficClassifier(EventMixin):
    def __init__(self):
        self.listenTo(core.openflow)
        self.stats = {
            "TCP":   {"count": 0, "bytes": 0},
            "UDP":   {"count": 0, "bytes": 0},
            "ICMP":  {"count": 0, "bytes": 0},
            "OTHER": {"count": 0, "bytes": 0},
        }
        self.packet_log = []
        self.start_time = time.time()
        self._print_banner()

    def _print_banner(self):
        clear()
        print(f"{C}{'═'*62}{NC}")
        print(f"{BOLD}{C}   ██████ TRAFFIC CLASSIFICATION SYSTEM ██████{NC}")
        print(f"{DIM}{C}          Mininet + POX SDN Controller{NC}")
        print(f"{C}{'═'*62}{NC}")
        print(f"{Y}  Waiting for switch connection and packets...{NC}\n")

    def _display(self, proto, src_ip, dst_ip, src_port, dst_port, size):
        total = sum(v["count"] for v in self.stats.values())
        uptime = int(time.time() - self.start_time)

        PROTO_COLORS = {"TCP": C, "UDP": Y, "ICMP": G, "OTHER": M}
        col = PROTO_COLORS.get(proto, W)

        clear()

        # ── Header ──────────────────────────────────────────────
        print(f"{C}{'═'*62}{NC}")
        print(f"{BOLD}{C}      TRAFFIC CLASSIFICATION SYSTEM  │  POX + Mininet{NC}")
        print(f"{C}{'═'*62}{NC}")
        print(f"  {DIM}Uptime:{NC} {W}{uptime}s{NC}   "
              f"{DIM}Total Packets:{NC} {W}{total}{NC}   "
              f"{DIM}Time:{NC} {W}{time.strftime('%H:%M:%S')}{NC}")
        print(f"{C}{'─'*62}{NC}")

        # ── Statistics Table ─────────────────────────────────────
        print(f"\n  {BOLD}{W}{'PROTOCOL':<10} {'PACKETS':>8} {'BYTES':>12} {'%':>6}  {'DISTRIBUTION'}{NC}")
        print(f"  {'─'*58}")

        COLORS = {"TCP": C, "UDP": Y, "ICMP": G, "OTHER": M}
        for p, c in COLORS.items():
            s = self.stats[p]
            pct = (s["count"] / total * 100) if total > 0 else 0
            b = bar(s["count"], total, width=18, color=c)
            print(f"  {c}{BOLD}{p:<10}{NC} {W}{s['count']:>8}{NC} "
                  f"{DIM}{fmt_bytes(s['bytes']):>12}{NC} "
                  f"{c}{pct:>5.1f}%{NC}  {b}")

        # ── Byte Distribution ─────────────────────────────────────
        total_bytes = sum(v["bytes"] for v in self.stats.values())
        print(f"\n  {BOLD}{W}{'BYTES DISTRIBUTION'}{NC}")
        print(f"  {'─'*58}")
        for p, c in COLORS.items():
            s = self.stats[p]
            bpct = (s["bytes"] / total_bytes * 100) if total_bytes > 0 else 0
            b = bar(s["bytes"], total_bytes, width=18, color=c)
            print(f"  {c}{BOLD}{p:<10}{NC} {DIM}{fmt_bytes(s['bytes']):>12}{NC} "
                  f"{c}{bpct:>5.1f}%{NC}  {b}")

        # ── Live Packet Log ───────────────────────────────────────
        print(f"\n  {BOLD}{W}LAST 10 CLASSIFIED PACKETS{NC}")
        print(f"  {C}{'─'*58}{NC}")
        print(f"  {DIM}{'TIME':<9} {'PROTO':<7} {'SRC IP':<15} {'DST IP':<15} {'SPORT':<7} {'DPORT':<7} {'SIZE'}{NC}")
        for entry in self.packet_log[-10:]:
            ec = PROTO_COLORS.get(entry["proto"], W)
            print(f"  {DIM}{entry['time']:<9}{NC}"
                  f"{ec}{BOLD}{entry['proto']:<7}{NC}"
                  f"{W}{entry['src']:<15}{NC}"
                  f"{DIM}{entry['dst']:<15}{NC}"
                  f"{DIM}{entry['sport']:<7}{NC}"
                  f"{DIM}{entry['dport']:<7}{NC}"
                  f"{DIM}{entry['size']} B{NC}")

        # ── Current Packet Highlight ──────────────────────────────
        print(f"\n  {C}{'─'*58}{NC}")
        print(f"  {BOLD}Latest:{NC}  "
              f"{col}[{proto}]{NC}  "
              f"{W}{src_ip}:{src_port}{NC}  {DIM}→{NC}  "
              f"{W}{dst_ip}:{dst_port}{NC}  "
              f"{DIM}({size} bytes){NC}")
        print(f"{C}{'═'*62}{NC}")

    def _classify_packet(self, packet):
        proto = "OTHER"
        src_ip = dst_ip = src_port = dst_port = "-"

        ip_pkt = packet.find("ipv4")
        if ip_pkt:
            src_ip = str(ip_pkt.srcip)
            dst_ip = str(ip_pkt.dstip)
            tcp_pkt = packet.find("tcp")
            udp_pkt = packet.find("udp")
            icmp_pkt = packet.find("icmp")

            if tcp_pkt:
                proto = "TCP"
                src_port = str(tcp_pkt.srcport)
                dst_port = str(tcp_pkt.dstport)
            elif udp_pkt:
                proto = "UDP"
                src_port = str(udp_pkt.srcport)
                dst_port = str(udp_pkt.dstport)
            elif icmp_pkt:
                proto = "ICMP"

        return proto, src_ip, dst_ip, src_port, dst_port

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if not packet.parsed:
            return

        proto, src_ip, dst_ip, src_port, dst_port = self._classify_packet(packet)
        size = len(event.data)

        self.stats[proto]["count"] += 1
        self.stats[proto]["bytes"] += size

        self.packet_log.append({
            "time": time.strftime("%H:%M:%S"),
            "proto": proto,
            "src": src_ip,
            "dst": dst_ip,
            "sport": src_port,
            "dport": dst_port,
            "size": size,
        })
        if len(self.packet_log) > 100:
            self.packet_log.pop(0)

        self._display(proto, src_ip, dst_ip, src_port, dst_port, size)

        # Flood rule
        msg = of.ofp_flow_mod()
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        event.connection.send(msg)

    def _handle_ConnectionUp(self, event):
        clear()
        print(f"{C}{'═'*62}{NC}")
        print(f"{BOLD}{G}   SWITCH CONNECTED: {dpid_to_str(event.dpid)}{NC}")
        print(f"{C}{'═'*62}{NC}")
        print(f"  {Y}Ready to classify traffic. Generate packets in Mininet.{NC}\n")
        print(f"  Examples:")
        print(f"    {G}mininet> h1 ping h2{NC}              {DIM}# ICMP{NC}")
        print(f"    {G}mininet> h1 iperf -s &{NC}           {DIM}# TCP server{NC}")
        print(f"    {G}mininet> h2 iperf -c 10.0.0.1{NC}   {DIM}# TCP client{NC}")
        print(f"    {G}mininet> h3 iperf -u -s &{NC}        {DIM}# UDP server{NC}")
        print(f"    {G}mininet> h4 iperf -u -c 10.0.0.3{NC} {DIM}# UDP client{NC}")
        print(f"    {G}mininet> run_demo{NC}                 {DIM}# auto demo{NC}")
        print(f"{C}{'─'*62}{NC}\n")

def launch():
    core.registerNew(TrafficClassifier)
