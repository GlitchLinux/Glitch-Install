#!/bin/bash
# ═══════════════════════════════════════════════════════
#  Glitch Linux GUI Installer - Launcher
#  Installs dependencies, fetches latest installer, runs it
# ═══════════════════════════════════════════════════════

set -e

CYAN='\033[0;96m'
GREEN='\033[0;92m'
RED='\033[0;91m'
YELLOW='\033[1;33m'
WHITE='\033[1;37m'
NC='\033[0m'

INSTALLER_URL="https://raw.githubusercontent.com/GlitchLinux/Glitch-GUI-Installer/refs/heads/main/glitch_installer.py"
INSTALLER_PATH="/tmp/glitch_installer.py"
LOG_FILE="/tmp/glitch_installer_launch.log"

rm 

print_banner() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════╗"
    echo "║   Glitch Linux Installer - Launcher   ║"
    echo "╚═══════════════════════════════════════╝"
    echo -e "${NC}"
}

log()  { echo -e "${WHITE}[*]${NC} $1"; }
ok()   { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
fail() { echo -e "${RED}[✗]${NC} $1"; exit 1; }

# ── Root check ──
check_root() {
    if [[ $EUID -ne 0 ]]; then
        fail "This script must be run as root (sudo)"
    fi
}

# ── Install dependencies ──
install_deps() {
    log "Checking dependencies..."

    local missing=()
    for pkg in python3-pyqt5 python3-psutil wget; do
        if ! dpkg -s "$pkg" &>/dev/null; then
            missing+=("$pkg")
        fi
    done

    if [[ ${#missing[@]} -gt 0 ]]; then
        log "Installing: ${missing[*]}"
        apt-get update -qq >> "$LOG_FILE" 2>&1
        apt-get install -y -qq "${missing[@]}" >> "$LOG_FILE" 2>&1
        ok "Dependencies installed"
    else
        ok "All dependencies already installed"
    fi
}

# ── Fetch installer ──
fetch_installer() {
    log "Fetching latest installer..."
    if wget -q -O "$INSTALLER_PATH" "$INSTALLER_URL"; then
        chmod +x "$INSTALLER_PATH"
        ok "Installer downloaded → $INSTALLER_PATH"
    else
        fail "Failed to download installer from GitHub"
    fi
}

# ── Launch ──
launch_installer() {
    log "Launching Glitch Linux Installer (separate PID)..."
    nohup python3 "$INSTALLER_PATH" >> "$LOG_FILE" 2>&1 &
    local pid=$!
    disown "$pid"
    echo
    ok "Installer running — PID: ${CYAN}${pid}${NC}"
    echo -e "   ${WHITE}Log:${NC}  $LOG_FILE"
    echo -e "   ${WHITE}Kill:${NC} kill $pid"
    echo
}

# ── Main ──
print_banner
check_root
install_deps
fetch_installer
launch_installer
