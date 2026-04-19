#!/bin/bash
# Traffic Classification System - Quick Setup
# Usage: bash setup.sh

C='\033[0;36m' Y='\033[1;33m' G='\033[0;32m' R='\033[0;31m' NC='\033[0m' W='\033[1;37m'

clear
echo -e "${C}══════════════════════════════════════════════════════${NC}"
echo -e "${W}   Traffic Classification System — Setup${NC}"
echo -e "${C}══════════════════════════════════════════════════════${NC}\n"

# Find POX
POX_DIR=""
for d in ~/pox /opt/pox /usr/local/pox; do
  [ -d "$d" ] && POX_DIR="$d" && break
done

if [ -z "$POX_DIR" ]; then
  echo -e "${Y}[1/3] Installing POX...${NC}"
  git clone https://github.com/noxrepo/pox.git ~/pox
  POX_DIR=~/pox
  echo -e "${G}  ✓ POX installed at ~/pox${NC}"
else
  echo -e "${G}[1/3] POX found at $POX_DIR${NC}"
fi

echo -e "${Y}[2/3] Installing controller into POX...${NC}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cp "$SCRIPT_DIR/pox_controller/traffic_classifier.py" "$POX_DIR/pox/misc/"
echo -e "${G}  ✓ Controller installed${NC}"

echo -e "${Y}[3/3] Ready!${NC}\n"
echo -e "${C}══════════════════════════════════════════════════════${NC}"
echo -e "${W}  HOW TO RUN:${NC}\n"
echo -e "  ${Y}Terminal 1${NC} — Start POX controller:"
echo -e "  ${G}  cd $POX_DIR && python3 pox.py misc.traffic_classifier${NC}\n"
echo -e "  ${Y}Terminal 2${NC} — Start Mininet:"
echo -e "  ${G}  sudo python3 $SCRIPT_DIR/topology.py${NC}\n"
echo -e "  Inside Mininet CLI:"
echo -e "  ${G}  mininet> run_demo${NC}     ← auto traffic"
echo -e "  ${G}  mininet> show_stats${NC}   ← print stats"
echo -e "${C}══════════════════════════════════════════════════════${NC}\n"
