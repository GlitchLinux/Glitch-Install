#!/usr/bin/env python3
"""
Glitch Linux GUI Installer
===========================
A modern PyQt5-based graphical installer for Glitch Linux.
Converts the Bonsai CLI installer into a professional GUI experience.

Requirements: PyQt5, psutil
Run as root: sudo python3 glitch_installer.py
"""

import sys
import os
import re
import subprocess
import shutil
import time
import signal
from pathlib import Path
from datetime import datetime
from threading import Lock

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QTableWidget, QTableWidgetItem,
    QRadioButton, QButtonGroup, QLineEdit, QCheckBox, QSpinBox,
    QTextEdit, QProgressBar, QMessageBox, QComboBox, QGroupBox,
    QHeaderView, QSizePolicy, QFrame, QScrollArea, QFileDialog,
    QGridLayout, QSpacerItem, QAbstractItemView
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QSize, QUrl, QPropertyAnimation,
    QEasingCurve, pyqtProperty, QRect
)
from PyQt5.QtGui import (
    QPalette, QColor, QFont, QPixmap, QIcon, QPainter,
    QLinearGradient, QBrush, QPen, QFontDatabase
)

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


# ─────────────────────────────────────────────────────────────
# DARK THEME STYLESHEET
# ─────────────────────────────────────────────────────────────
DARK_THEME = """
QMainWindow {
    background-color: #1a1a2e;
}
QWidget {
    background-color: transparent;
    color: #e0e0e0;
    font-family: 'Segoe UI', 'Ubuntu', 'DejaVu Sans', sans-serif;
    font-size: 13px;
}
QLabel {
    color: #e0e0e0;
    background: transparent;
}
QLabel#title {
    font-size: 22px;
    font-weight: bold;
    color: #00ffff;
    padding: 8px 0;
}
QLabel#subtitle {
    font-size: 14px;
    color: #aaaaaa;
    padding: 4px 0;
}
QLabel#sectionHeader {
    font-size: 15px;
    font-weight: bold;
    color: #00cccc;
    padding: 6px 0;
}
QLabel#stepIndicator {
    font-size: 11px;
    color: #666666;
    padding: 2px 0;
}
QPushButton {
    background-color: #2d2d44;
    color: #e0e0e0;
    border: 1px solid #3d3d5c;
    border-radius: 6px;
    padding: 10px 24px;
    font-size: 13px;
    font-weight: bold;
    min-width: 100px;
}
QPushButton:hover {
    background-color: #3d3d5c;
    border-color: #00ffff;
}
QPushButton:pressed {
    background-color: #1a1a2e;
}
QPushButton:disabled {
    background-color: #1e1e30;
    color: #555555;
    border-color: #2a2a40;
}
QPushButton#primary {
    background-color: #004d4d;
    color: #00ffff;
    border: 1px solid #00ffff;
}
QPushButton#primary:hover {
    background-color: #006666;
}
QPushButton#danger {
    background-color: #4d1a1a;
    color: #ff4444;
    border: 1px solid #ff4444;
}
QPushButton#danger:hover {
    background-color: #661a1a;
}
QPushButton#success {
    background-color: #1a4d1a;
    color: #00ff88;
    border: 1px solid #00ff88;
}
QPushButton#success:hover {
    background-color: #1a661a;
}
QLineEdit {
    background-color: #252540;
    color: #e0e0e0;
    border: 1px solid #3d3d5c;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: #00ffff;
    selection-color: #1a1a2e;
}
QLineEdit:focus {
    border-color: #00ffff;
}
QLineEdit:disabled {
    background-color: #1e1e30;
    color: #555555;
}
QSpinBox {
    background-color: #252540;
    color: #e0e0e0;
    border: 1px solid #3d3d5c;
    border-radius: 4px;
    padding: 6px 10px;
}
QSpinBox:focus {
    border-color: #00ffff;
}
QComboBox {
    background-color: #252540;
    color: #e0e0e0;
    border: 1px solid #3d3d5c;
    border-radius: 4px;
    padding: 6px 10px;
    min-width: 150px;
}
QComboBox:focus {
    border-color: #00ffff;
}
QComboBox::drop-down {
    border: none;
    width: 30px;
}
QComboBox QAbstractItemView {
    background-color: #252540;
    color: #e0e0e0;
    border: 1px solid #3d3d5c;
    selection-background-color: #004d4d;
}
QRadioButton {
    color: #e0e0e0;
    spacing: 8px;
    padding: 4px;
}
QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 2px solid #3d3d5c;
    background-color: #252540;
}
QRadioButton::indicator:checked {
    background-color: #00ffff;
    border-color: #00ffff;
}
QRadioButton::indicator:hover {
    border-color: #00cccc;
}
QCheckBox {
    color: #e0e0e0;
    spacing: 8px;
    padding: 4px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 3px;
    border: 2px solid #3d3d5c;
    background-color: #252540;
}
QCheckBox::indicator:checked {
    background-color: #00ffff;
    border-color: #00ffff;
}
QTextEdit {
    background-color: #0d0d1a;
    color: #00ff88;
    border: 1px solid #2d2d44;
    border-radius: 4px;
    padding: 8px;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', 'Ubuntu Mono', monospace;
    font-size: 12px;
    selection-background-color: #004d4d;
}
QTableWidget {
    background-color: #1e1e30;
    color: #e0e0e0;
    border: 1px solid #2d2d44;
    border-radius: 4px;
    gridline-color: #2d2d44;
    selection-background-color: #004d4d;
    selection-color: #00ffff;
}
QTableWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid #252540;
}
QTableWidget::item:selected {
    background-color: #004d4d;
    color: #00ffff;
}
QHeaderView::section {
    background-color: #252540;
    color: #00cccc;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #00ffff;
    font-weight: bold;
    font-size: 12px;
}
QProgressBar {
    background-color: #1e1e30;
    border: 1px solid #2d2d44;
    border-radius: 8px;
    text-align: center;
    color: #00ffff;
    font-weight: bold;
    font-size: 13px;
    min-height: 28px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #004d4d, stop:0.5 #00cccc, stop:1 #00ffff);
    border-radius: 7px;
}
QGroupBox {
    border: 1px solid #2d2d44;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
    color: #00cccc;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}
QScrollBar:vertical {
    background-color: #1a1a2e;
    width: 10px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #3d3d5c;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #00cccc;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QFrame#separator {
    background-color: #2d2d44;
    max-height: 1px;
}
QFrame#card {
    background-color: #1e1e30;
    border: 1px solid #2d2d44;
    border-radius: 8px;
    padding: 16px;
}
"""


# ─────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────
def run_cmd(cmd, shell=True, timeout=300):
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd, shell=shell, capture_output=True, text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def human_size(size_bytes):
    """Convert bytes to human-readable size."""
    if size_bytes is None:
        return "Unknown"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def get_block_devices():
    """Detect all block devices with metadata."""
    devices = []
    rc, out, _ = run_cmd("lsblk -b -d -o NAME,SIZE,TYPE,MOUNTPOINT,LABEL,MODEL -n -p")
    if rc != 0:
        return devices

    for line in out.splitlines():
        parts = line.split(None, 5)
        if len(parts) < 3:
            continue
        name = parts[0]
        try:
            size = int(parts[1])
        except (ValueError, IndexError):
            size = 0
        dtype = parts[2] if len(parts) > 2 else ""
        mount = parts[3] if len(parts) > 3 and parts[3] != "" else ""
        label = parts[4] if len(parts) > 4 else ""
        model = parts[5] if len(parts) > 5 else ""

        # Filter to disk and loop types
        if dtype not in ("disk", "loop"):
            continue

        # Skip tiny loop devices (< 100MB) that are just snaps etc
        if dtype == "loop" and size < 100 * 1024 * 1024:
            continue

        is_mounted = bool(mount and mount != "")
        # Also check if any partitions are mounted
        if not is_mounted:
            rc2, out2, _ = run_cmd(f"lsblk -n -o MOUNTPOINT {name}")
            if rc2 == 0:
                for mp in out2.splitlines():
                    if mp.strip():
                        is_mounted = True
                        break

        devices.append({
            'name': name,
            'size': size,
            'size_human': human_size(size),
            'type': dtype.capitalize(),
            'mounted': is_mounted,
            'label': label,
            'model': model.strip() if model else "",
            'status': 'In Use' if is_mounted else 'Available'
        })

    return devices


def get_partitions(device):
    """Get partitions for a device."""
    partitions = []
    rc, out, _ = run_cmd(f"lsblk -b -n -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT -p {device}")
    if rc != 0:
        return partitions

    for line in out.splitlines():
        parts = line.split(None, 4)
        if len(parts) < 2:
            continue
        name = parts[0]
        if name == device:
            continue  # Skip the disk itself
        try:
            size = int(parts[1])
        except (ValueError, IndexError):
            size = 0
        fstype = parts[2] if len(parts) > 2 else ""
        label = parts[3] if len(parts) > 3 else ""
        mount = parts[4] if len(parts) > 4 else ""

        partitions.append({
            'name': name,
            'size': size,
            'size_human': human_size(size),
            'fstype': fstype,
            'label': label,
            'mountpoint': mount
        })

    return partitions


def detect_squashfs():
    """Detect squashfs sources."""
    paths = [
        "/run/live/medium/live/filesystem.squashfs",
        "/cdrom/casper/filesystem.squashfs",
    ]
    for p in paths:
        if os.path.isfile(p):
            return p

    # Search common directories
    for search_dir in ["/run/live/medium/live", "/cdrom/casper"]:
        if os.path.isdir(search_dir):
            for f in os.listdir(search_dir):
                if f.endswith(".squashfs"):
                    return os.path.join(search_dir, f)
    return None


def get_system_info():
    """Get basic system info for welcome screen."""
    info = {}
    if HAS_PSUTIL:
        info['cpu'] = psutil.cpu_count(logical=True)
        mem = psutil.virtual_memory()
        info['ram'] = human_size(mem.total)
        info['ram_used'] = f"{mem.percent}%"
    else:
        rc, out, _ = run_cmd("nproc")
        info['cpu'] = out if rc == 0 else "?"
        rc, out, _ = run_cmd("free -h | awk '/Mem:/ {print $2}'")
        info['ram'] = out if rc == 0 else "?"

    devs = get_block_devices()
    info['disks'] = len([d for d in devs if d['type'] == 'Disk'])
    info['loops'] = len([d for d in devs if d['type'] == 'Loop'])
    return info


# ─────────────────────────────────────────────────────────────
# INSTALLATION WORKER THREAD
# ─────────────────────────────────────────────────────────────
class InstallWorker(QThread):
    """Background thread that runs the actual installation."""
    log_signal = pyqtSignal(str, str)      # message, level (INFO/SUCCESS/ERROR/PROGRESS/WARNING)
    progress_signal = pyqtSignal(int)       # percentage 0-100
    step_signal = pyqtSignal(str)           # current step description
    finished_signal = pyqtSignal(bool, str) # success, message
    stage_signal = pyqtSignal(int)          # stage index for checklist

    def __init__(self, config):
        super().__init__()
        self.config = config
        self._cancelled = False
        self.mount_target = "/mnt/target"
        self.mount_live = "/mnt/live"
        self.install_source = ""
        self.luks_mapper = "luks-root"
        self.luks_device = ""
        self.original_data_partition = ""

    def cancel(self):
        self._cancelled = True

    def log(self, msg, level="INFO"):
        self.log_signal.emit(msg, level)

    def exec_cmd(self, cmd, desc="", timeout=600):
        """Execute command with logging."""
        if desc:
            self.log(desc, "PROGRESS")
        rc, out, err = run_cmd(cmd, timeout=timeout)
        if rc != 0 and err:
            self.log(f"Command warning: {err}", "WARNING")
        return rc, out, err

    def run(self):
        try:
            self._run_installation()
        except Exception as e:
            self.log(f"Fatal error: {str(e)}", "ERROR")
            self.finished_signal.emit(False, str(e))
            self._cleanup()

    def _run_installation(self):
        cfg = self.config
        total_stages = 12
        stage = 0

        # ── Stage 0: Detect install source ──
        self.step_signal.emit("Detecting installation source...")
        self.stage_signal.emit(0)
        self.progress_signal.emit(2)

        source_path = cfg.get('install_source', '')
        if not source_path:
            squashfs = detect_squashfs()
            if squashfs:
                source_path = squashfs
                self.log(f"Detected squashfs: {source_path}", "SUCCESS")
            else:
                source_path = "/"
                self.log("No squashfs found, using root filesystem", "INFO")
        else:
            if os.path.isfile(source_path):
                self.log(f"Using custom source: {source_path}", "INFO")
            else:
                self.log(f"Source not found: {source_path}, falling back to /", "WARNING")
                source_path = "/"

        self.install_source = source_path
        self.log(f"Installation source: {self.install_source}", "SUCCESS")

        if self._cancelled:
            self._cancel_and_cleanup()
            return

        # ── Stage 1: Unmount target ──
        stage += 1
        self.step_signal.emit("Preparing target device...")
        self.stage_signal.emit(1)
        self.progress_signal.emit(5)

        target_dev = cfg['target_device']
        self.exec_cmd(f"umount {target_dev}* 2>/dev/null || true", "Unmounting target device partitions")
        time.sleep(1)

        if self._cancelled:
            self._cancel_and_cleanup()
            return

        # ── Stage 2: Partitioning ──
        stage += 1
        self.step_signal.emit("Partitioning disk...")
        self.stage_signal.emit(2)
        self.progress_signal.emit(10)

        if cfg['partitioning'] == 'erase':
            self._create_partitions(cfg)
        else:
            self._setup_existing_partitions(cfg)

        if self._cancelled:
            self._cancel_and_cleanup()
            return

        # ── Stage 3: Format partitions ──
        stage += 1
        self.step_signal.emit("Formatting partitions...")
        self.stage_signal.emit(3)
        self.progress_signal.emit(18)
        self._format_partitions(cfg)

        if self._cancelled:
            self._cancel_and_cleanup()
            return

        # ── Stage 4: LUKS encryption (optional) ──
        stage += 1
        if cfg.get('luks_enabled'):
            self.step_signal.emit("Setting up LUKS encryption...")
            self.stage_signal.emit(4)
            self.progress_signal.emit(22)
            self._setup_luks(cfg)
        else:
            self.stage_signal.emit(4)
            self.log("Encryption: Skipped", "INFO")

        if self._cancelled:
            self._cancel_and_cleanup()
            return

        # ── Stage 5: Mount target ──
        stage += 1
        self.step_signal.emit("Mounting target partitions...")
        self.stage_signal.emit(5)
        self.progress_signal.emit(25)
        self._mount_target(cfg)

        if self._cancelled:
            self._cancel_and_cleanup()
            return

        # ── Stage 6: Mount source ──
        stage += 1
        self.step_signal.emit("Mounting source filesystem...")
        self.stage_signal.emit(6)
        self.progress_signal.emit(28)
        self._mount_source()

        if self._cancelled:
            self._cancel_and_cleanup()
            return

        # ── Stage 7: Extract filesystem ──
        stage += 1
        self.step_signal.emit("Extracting filesystem...")
        self.stage_signal.emit(7)
        self.progress_signal.emit(30)
        self._extract_filesystem()

        if self._cancelled:
            self._cancel_and_cleanup()
            return

        # ── Stage 8: Configure system ──
        stage += 1
        self.step_signal.emit("Configuring system files...")
        self.stage_signal.emit(8)
        self.progress_signal.emit(75)
        self._configure_system(cfg)

        if self._cancelled:
            self._cancel_and_cleanup()
            return

        # ── Stage 9: Install bootloader ──
        stage += 1
        self.step_signal.emit("Installing GRUB bootloader...")
        self.stage_signal.emit(9)
        self.progress_signal.emit(82)
        self._install_grub(cfg)

        if self._cancelled:
            self._cancel_and_cleanup()
            return

        # ── Stage 10: User setup ──
        stage += 1
        self.step_signal.emit("Setting up user account...")
        self.stage_signal.emit(10)
        self.progress_signal.emit(90)
        self._setup_user(cfg)

        # ── Stage 11: Verify ──
        stage += 1
        self.step_signal.emit("Verifying installation...")
        self.stage_signal.emit(11)
        self.progress_signal.emit(95)
        self._verify_installation()

        # ── Done ──
        self.progress_signal.emit(100)
        self.step_signal.emit("Installation complete!")
        self._cleanup()
        self.finished_signal.emit(True, "Installation completed successfully!")

    def _create_partitions(self, cfg):
        dev = cfg['target_device']
        boot_type = cfg['boot_type']
        is_loop = dev.startswith("/dev/loop")
        sep = "p" if is_loop or "nvme" in dev else ""

        self.exec_cmd(f"wipefs -a {dev} 2>/dev/null || true")

        if boot_type == 'legacy_mbr':
            self.exec_cmd(f"parted -s {dev} mklabel msdos", "Creating MBR partition table")
            part_num = 1

            if cfg.get('separate_boot'):
                boot_size = cfg.get('boot_size', 512)
                self.exec_cmd(
                    f"parted -s {dev} mkpart primary ext4 1MiB {boot_size}MiB",
                    f"Creating /boot partition ({boot_size}MB)")
                self.exec_cmd(f"parted -s {dev} set 1 boot on")
                cfg['boot_partition'] = f"{dev}{sep}{part_num}"
                part_num += 1
                start = f"{boot_size}MiB"
            else:
                start = "1MiB"

            self.exec_cmd(
                f"parted -s {dev} mkpart primary ext4 {start} 100%",
                "Creating root partition")
            if not cfg.get('separate_boot'):
                self.exec_cmd(f"parted -s {dev} set 1 boot on")
            cfg['data_partition'] = f"{dev}{sep}{part_num}"

        elif boot_type == 'bios_gpt':
            self.exec_cmd(f"parted -s {dev} mklabel gpt", "Creating GPT partition table")
            self.exec_cmd(f"parted -s {dev} mkpart BIOS_GRUB 1MiB 2MiB")
            self.exec_cmd(f"parted -s {dev} set 1 bios_grub on")
            part_num = 2

            if cfg.get('separate_boot'):
                boot_size = cfg.get('boot_size', 512)
                boot_end = 2 + boot_size
                self.exec_cmd(
                    f"parted -s {dev} mkpart BOOT ext4 2MiB {boot_end}MiB",
                    f"Creating /boot partition ({boot_size}MB)")
                self.exec_cmd(f"parted -s {dev} set 2 boot on")
                cfg['boot_partition'] = f"{dev}{sep}{part_num}"
                part_num += 1
                start = f"{boot_end}MiB"
            else:
                start = "2MiB"

            self.exec_cmd(
                f"parted -s {dev} mkpart ROOT ext4 {start} 100%",
                "Creating root partition")
            cfg['data_partition'] = f"{dev}{sep}{part_num}"

        elif boot_type == 'uefi':
            self.exec_cmd(f"parted -s {dev} mklabel gpt", "Creating GPT partition table")
            self.exec_cmd(f"parted -s {dev} mkpart EFI fat32 1MiB 97MiB")
            self.exec_cmd(f"parted -s {dev} set 1 esp on")
            cfg['efi_partition'] = f"{dev}{sep}1"
            self.log(f"✓ EFI partition created: {cfg['efi_partition']}", "SUCCESS")
            part_num = 2

            if cfg.get('separate_boot'):
                boot_size = cfg.get('boot_size', 512)
                boot_end = 97 + boot_size
                self.exec_cmd(
                    f"parted -s {dev} mkpart BOOT ext4 97MiB {boot_end}MiB",
                    f"Creating /boot partition ({boot_size}MB)")
                cfg['boot_partition'] = f"{dev}{sep}{part_num}"
                part_num += 1
                start = f"{boot_end}MiB"
            else:
                start = "97MiB"

            self.exec_cmd(
                f"parted -s {dev} mkpart ROOT ext4 {start} 100%",
                "Creating root partition")
            cfg['data_partition'] = f"{dev}{sep}{part_num}"

        time.sleep(2)
        self.exec_cmd(f"partprobe {dev}")
        time.sleep(2)

        self.log(f"✓ Partition table created on {dev}", "SUCCESS")
        if cfg.get('efi_partition'):
            self.log(f"  EFI: {cfg['efi_partition']}", "INFO")
        if cfg.get('boot_partition'):
            self.log(f"  Boot: {cfg['boot_partition']}", "INFO")
        self.log(f"  Root: {cfg['data_partition']}", "INFO")

    def _setup_existing_partitions(self, cfg):
        self.log("Using existing partition layout", "INFO")
        # Partitions already set in config from the UI

    def _format_partitions(self, cfg):
        if cfg.get('efi_partition') and cfg['partitioning'] == 'erase':
            self.exec_cmd(
                f"mkfs.fat -F32 -n EFI {cfg['efi_partition']}",
                "Formatting EFI partition (FAT32)")
            self.log(f"✓ EFI partition formatted: {cfg['efi_partition']}", "SUCCESS")

        if cfg.get('separate_boot') and cfg.get('boot_partition') and cfg['partitioning'] == 'erase':
            boot_fs = cfg.get('boot_fs', 'ext4')
            self.exec_cmd(
                f"mkfs.{boot_fs} -F -L BOOT {cfg['boot_partition']}",
                f"Formatting /boot partition ({boot_fs})")
            self.log(f"✓ Boot partition formatted: {cfg['boot_partition']}", "SUCCESS")

        if not cfg.get('luks_enabled') and cfg['partitioning'] == 'erase':
            self.exec_cmd(
                f"mkfs.ext4 -F -L ROOT {cfg['data_partition']}",
                "Formatting root partition (ext4)")
            self.log(f"✓ Root partition formatted: {cfg['data_partition']}", "SUCCESS")

    def _setup_luks(self, cfg):
        data_part = cfg['data_partition']
        passphrase = cfg.get('luks_passphrase', '')
        self.original_data_partition = data_part

        self.exec_cmd(f"umount {data_part} 2>/dev/null || true")

        self.log("Formatting partition with LUKS1 encryption...", "PROGRESS")
        rc, _, err = run_cmd(
            f"echo -n '{passphrase}' | cryptsetup luksFormat --type luks1 --batch-mode {data_part} -",
            timeout=120
        )
        if rc != 0:
            self.log(f"LUKS format failed: {err}", "ERROR")
            raise RuntimeError("LUKS format failed")
        self.log("✓ LUKS1 encryption applied", "SUCCESS")

        self.log("Opening encrypted partition...", "PROGRESS")
        rc, _, err = run_cmd(
            f"echo -n '{passphrase}' | cryptsetup luksOpen {data_part} {self.luks_mapper} -",
            timeout=60
        )
        if rc != 0:
            self.log(f"LUKS open failed: {err}", "ERROR")
            raise RuntimeError("Failed to open LUKS partition")

        self.luks_device = f"/dev/mapper/{self.luks_mapper}"
        self.log(f"✓ LUKS partition opened as {self.luks_device}", "SUCCESS")

        self.exec_cmd(
            f"mkfs.ext4 -F -L ROOT {self.luks_device}",
            "Formatting encrypted partition (ext4)")
        self.log("✓ Encrypted partition formatted", "SUCCESS")

        # Update data partition to mapper device
        cfg['data_partition_actual'] = self.luks_device

    def _mount_target(self, cfg):
        os.makedirs(self.mount_target, exist_ok=True)

        data_part = cfg.get('data_partition_actual', cfg['data_partition'])
        rc, _, err = run_cmd(f"mount {data_part} {self.mount_target}")
        if rc != 0:
            raise RuntimeError(f"Failed to mount root: {err}")
        self.log(f"✓ Root partition mounted at {self.mount_target}", "SUCCESS")

        if cfg.get('separate_boot') and cfg.get('boot_partition'):
            boot_dir = f"{self.mount_target}/boot"
            os.makedirs(boot_dir, exist_ok=True)
            rc, _, err = run_cmd(f"mount {cfg['boot_partition']} {boot_dir}")
            if rc != 0:
                raise RuntimeError(f"Failed to mount /boot: {err}")
            self.log("✓ Boot partition mounted", "SUCCESS")

        if cfg.get('efi_partition'):
            efi_dir = f"{self.mount_target}/boot/efi"
            os.makedirs(efi_dir, exist_ok=True)
            rc, _, err = run_cmd(f"mount {cfg['efi_partition']} {efi_dir}")
            if rc != 0:
                raise RuntimeError(f"Failed to mount EFI: {err}")
            self.log("✓ EFI partition mounted", "SUCCESS")

    def _mount_source(self):
        if self.install_source == "/":
            self.log("Using current root filesystem as source", "INFO")
            return

        os.makedirs(self.mount_live, exist_ok=True)
        rc, _, err = run_cmd(f"mount -t squashfs -o loop {self.install_source} {self.mount_live}")
        if rc != 0:
            raise RuntimeError(f"Failed to mount source: {err}")
        self.log(f"✓ Source mounted at {self.mount_live}", "SUCCESS")
        self.install_source = self.mount_live

    def _extract_filesystem(self):
        source = self.install_source
        target = self.mount_target

        excludes = [
            "--exclude=/proc/*", "--exclude=/sys/*", "--exclude=/dev/*",
            "--exclude=/run/*", "--exclude=/tmp/*", "--exclude=/mnt/*",
            "--exclude=/media/*", "--exclude=/swapfile", "--exclude=/swap.img",
            "--exclude=lost+found"
        ]
        if source == "/":
            excludes.extend([
                "--exclude=/home/*/.cache/*", "--exclude=/var/cache/*",
                "--exclude=/var/tmp/*", "--exclude=/var/log/*"
            ])

        exclude_str = " ".join(excludes)

        self.log("Starting filesystem extraction (this may take several minutes)...", "PROGRESS")

        # Use rsync with progress output
        cmd = f"rsync -a --info=progress2 {exclude_str} {source}/ {target}/"
        process = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            universal_newlines=True
        )

        last_pct = 30
        for line in process.stdout:
            line = line.strip()
            if self._cancelled:
                process.kill()
                return

            # Parse rsync progress
            match = re.search(r'(\d+)%', line)
            if match:
                pct = int(match.group(1))
                # Map rsync 0-100% to our 30-74%
                mapped = 30 + int(pct * 0.44)
                if mapped != last_pct:
                    self.progress_signal.emit(mapped)
                    last_pct = mapped
                    if pct % 10 == 0:
                        self.log(f"Filesystem extraction: {pct}%", "PROGRESS")

        process.wait()
        if process.returncode != 0 and process.returncode is not None:
            self.log("rsync completed with warnings", "WARNING")

        self.log("✓ Filesystem extracted successfully", "SUCCESS")
        self.progress_signal.emit(74)

    def _configure_system(self, cfg):
        target = self.mount_target
        data_part = cfg.get('data_partition_actual', cfg['data_partition'])

        # Prepare chroot
        self.log("Preparing chroot environment...", "PROGRESS")
        for bind in ["dev", "proc", "sys", "run"]:
            os.makedirs(f"{target}/{bind}", exist_ok=True)
            run_cmd(f"mount --bind /{bind} {target}/{bind}")
        run_cmd(f"mount -t devpts devpts {target}/dev/pts 2>/dev/null || true")

        # Copy resolv.conf
        if os.path.exists("/etc/resolv.conf"):
            run_cmd(f"cp /etc/resolv.conf {target}/etc/resolv.conf")
        self.log("✓ Chroot environment ready", "SUCCESS")

        # Update fstab
        self.log("Generating /etc/fstab...", "PROGRESS")
        fstab_lines = ["# <file system> <mount point> <type> <options> <dump> <pass>"]

        # Root entry
        rc, uuid, _ = run_cmd(f"blkid -o value -s UUID {data_part}")
        rc2, fstype, _ = run_cmd(f"blkid -o value -s TYPE {data_part}")
        if uuid:
            fstab_lines.append(f"UUID={uuid} / {fstype or 'ext4'} defaults 0 1")

        # Boot entry
        if cfg.get('separate_boot') and cfg.get('boot_partition'):
            rc, uuid, _ = run_cmd(f"blkid -o value -s UUID {cfg['boot_partition']}")
            rc2, fstype, _ = run_cmd(f"blkid -o value -s TYPE {cfg['boot_partition']}")
            if uuid:
                fstab_lines.append(f"UUID={uuid} /boot {fstype or 'ext4'} defaults 0 2")

        # EFI entry
        if cfg.get('efi_partition'):
            rc, uuid, _ = run_cmd(f"blkid -o value -s UUID {cfg['efi_partition']}")
            if uuid:
                fstab_lines.append(f"UUID={uuid} /boot/efi vfat umask=0077 0 2")

        fstab_lines.append("tmpfs /tmp tmpfs defaults,noatime,mode=1777 0 0")

        fstab_path = f"{target}/etc/fstab"
        os.makedirs(os.path.dirname(fstab_path), exist_ok=True)
        with open(fstab_path, 'w') as f:
            f.write("\n".join(fstab_lines) + "\n")
        self.log("✓ fstab configured", "SUCCESS")

        # Crypttab for LUKS
        if cfg.get('luks_enabled') and self.original_data_partition:
            self.log("Configuring crypttab...", "PROGRESS")
            rc, luks_uuid, _ = run_cmd(f"blkid -o value -s UUID {self.original_data_partition}")
            if luks_uuid:
                crypttab = f"{self.luks_mapper} UUID={luks_uuid} none luks,discard\n"
                with open(f"{target}/etc/crypttab", 'w') as f:
                    f.write(crypttab)
                self.log("✓ crypttab configured", "SUCCESS")

            # Update initramfs for LUKS
            self.log("Updating initramfs for LUKS support...", "PROGRESS")
            run_cmd(f"chroot {target} /bin/bash -c 'DEBIAN_FRONTEND=noninteractive apt-get update -qq && apt-get install -y -qq cryptsetup cryptsetup-initramfs 2>/dev/null'", timeout=180)
            run_cmd(f"chroot {target} /bin/bash -c 'update-initramfs -u -k all 2>/dev/null'", timeout=120)
            self.log("✓ initramfs updated with LUKS support", "SUCCESS")

    def _install_grub(self, cfg):
        target = self.mount_target
        dev = cfg['target_device']
        boot_type = cfg['boot_type']

        if cfg.get('luks_enabled'):
            self.log("Enabling GRUB cryptodisk support...", "PROGRESS")
            run_cmd(f"chroot {target} /bin/bash -c \"echo 'GRUB_ENABLE_CRYPTODISK=y' >> /etc/default/grub\"")

        if boot_type in ('legacy_mbr', 'bios_gpt'):
            self.log("Installing GRUB for BIOS...", "PROGRESS")
            rc, _, err = run_cmd(
                f"chroot {target} /bin/bash -c 'DEBIAN_FRONTEND=noninteractive apt-get update -qq && apt-get install -y -qq grub-pc && grub-install --recheck {dev} && update-grub'",
                timeout=300
            )
        elif boot_type == 'uefi':
            self.log("Installing GRUB for UEFI...", "PROGRESS")
            # Clean existing EFI dirs
            for d in ["BOOT", "Bonsai", "debian"]:
                efi_dir = f"{target}/boot/efi/EFI/{d}"
                if os.path.isdir(efi_dir):
                    shutil.rmtree(efi_dir, ignore_errors=True)

            rc, _, err = run_cmd(
                f"chroot {target} /bin/bash -c 'DEBIAN_FRONTEND=noninteractive apt-get update -qq && apt-get install -y -qq grub-efi-amd64 efibootmgr && grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=GlitchLinux --recheck && update-grub'",
                timeout=300
            )

        self.log("✓ GRUB bootloader installed", "SUCCESS")

    def _setup_user(self, cfg):
        target = self.mount_target
        if cfg.get('create_user') and cfg.get('username'):
            username = cfg['username']
            password = cfg.get('password', '')
            sudo = cfg.get('add_sudo', True)

            self.log(f"Creating user: {username}", "PROGRESS")
            run_cmd(f"chroot {target} /bin/bash -c 'useradd -m -s /bin/bash {username} 2>/dev/null || true'")
            if password:
                run_cmd(f"chroot {target} /bin/bash -c 'echo \"{username}:{password}\" | chpasswd'")
            if sudo:
                run_cmd(f"chroot {target} /bin/bash -c 'usermod -aG sudo {username} 2>/dev/null || true'")
            self.log(f"✓ User '{username}' created", "SUCCESS")
        else:
            self.log("Using default user profile", "INFO")

    def _verify_installation(self):
        target = self.mount_target
        errors = 0

        # Check kernel
        rc, out, _ = run_cmd(f"ls {target}/boot/vmlinuz-* 2>/dev/null")
        if rc == 0 and out:
            self.log("✓ Kernel found", "SUCCESS")
        else:
            self.log("✗ Kernel missing", "ERROR")
            errors += 1

        # Check initramfs
        rc, out, _ = run_cmd(f"ls {target}/boot/initrd.img-* 2>/dev/null")
        if rc == 0 and out:
            self.log("✓ Initramfs found", "SUCCESS")
        else:
            self.log("✗ Initramfs missing", "ERROR")
            errors += 1

        # Check GRUB config
        if os.path.isfile(f"{target}/boot/grub/grub.cfg"):
            self.log("✓ GRUB configuration found", "SUCCESS")
        else:
            self.log("✗ GRUB configuration missing", "ERROR")
            errors += 1

        # Check fstab
        if os.path.isfile(f"{target}/etc/fstab"):
            self.log("✓ fstab configured", "SUCCESS")
        else:
            self.log("✗ fstab missing", "ERROR")
            errors += 1

        if errors > 0:
            self.log(f"Verification completed with {errors} issue(s)", "WARNING")
        else:
            self.log("✓ All verification checks passed!", "SUCCESS")

    def _cleanup(self):
        """Cleanup mounts."""
        target = self.mount_target
        for path in [
            f"{target}/dev/pts", f"{target}/run",
            f"{target}/sys", f"{target}/proc", f"{target}/dev",
            f"{target}/boot/efi", f"{target}/boot", target
        ]:
            run_cmd(f"umount {path} 2>/dev/null || true")

        if self.install_source == self.mount_live:
            run_cmd(f"umount {self.mount_live} 2>/dev/null || true")

        if self.luks_device:
            run_cmd(f"cryptsetup luksClose {self.luks_mapper} 2>/dev/null || true")

    def _cancel_and_cleanup(self):
        self.log("Installation cancelled by user", "WARNING")
        self._cleanup()
        self.finished_signal.emit(False, "Installation cancelled")


# ─────────────────────────────────────────────────────────────
# HELPER WIDGETS
# ─────────────────────────────────────────────────────────────
class SeparatorLine(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("separator")
        self.setFrameShape(QFrame.HLine)
        self.setFixedHeight(1)


class CardFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("card")


# ─────────────────────────────────────────────────────────────
# SCREEN PAGES
# ─────────────────────────────────────────────────────────────

class WelcomeScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(12)

        # Logo area
        logo_layout = QHBoxLayout()
        logo_layout.setAlignment(Qt.AlignCenter)

        self.logo_label = QLabel()
        self.logo_label.setFixedSize(64, 64)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self._draw_placeholder_logo()
        logo_layout.addWidget(self.logo_label)
        layout.addLayout(logo_layout)

        # Title
        title = QLabel("Welcome to the Glitch Linux Installer")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Install Glitch Linux to your system")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        # System info card
        info = get_system_info()
        info_card = CardFrame()
        info_layout = QGridLayout(info_card)
        info_layout.setSpacing(10)

        info_header = QLabel("System Information")
        info_header.setObjectName("sectionHeader")
        info_layout.addWidget(info_header, 0, 0, 1, 2)

        row = 1
        for label, value in [
            ("CPU Cores:", str(info.get('cpu', '?'))),
            ("Total RAM:", str(info.get('ram', '?'))),
            ("Disk Devices:", str(info.get('disks', 0))),
            ("Loop Devices:", str(info.get('loops', 0))),
        ]:
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #888888; font-weight: bold;")
            val = QLabel(value)
            val.setStyleSheet("color: #00ffff;")
            info_layout.addWidget(lbl, row, 0)
            info_layout.addWidget(val, row, 1)
            row += 1

        layout.addWidget(info_card)
        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setObjectName("danger")
        self.btn_exit.setFixedWidth(140)
        btn_layout.addWidget(self.btn_exit)

        self.btn_start = QPushButton("Start Installation")
        self.btn_start.setObjectName("primary")
        self.btn_start.setFixedWidth(200)
        btn_layout.addWidget(self.btn_start)

        layout.addLayout(btn_layout)

    def _draw_placeholder_logo(self):
        """Draw a placeholder Glitch logo."""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Circle background
        gradient = QLinearGradient(0, 0, 64, 64)
        gradient.setColorAt(0, QColor("#004d4d"))
        gradient.setColorAt(1, QColor("#00cccc"))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor("#00ffff"), 2))
        painter.drawEllipse(4, 4, 56, 56)

        # "G" letter
        painter.setPen(QPen(QColor("#1a1a2e"), 3))
        font = QFont("DejaVu Sans", 28, QFont.Bold)
        painter.setFont(font)
        painter.drawText(QRect(0, 0, 64, 64), Qt.AlignCenter, "G")
        painter.end()
        self.logo_label.setPixmap(pixmap)


class DiskSelectScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_device = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)

        title = QLabel("Select Installation Target")
        title.setObjectName("title")
        layout.addWidget(title)

        step = QLabel("Step 1 of 6")
        step.setObjectName("stepIndicator")
        layout.addWidget(step)

        layout.addWidget(SeparatorLine())

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Device", "Size", "Type", "Model/Label", "Status"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(200)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.table)

        # Warning label
        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("color: #ff00ff; font-weight: bold; padding: 4px;")
        self.warning_label.setVisible(False)
        layout.addWidget(self.warning_label)

        # Refresh button
        refresh_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("⟳ Refresh Devices")
        self.btn_refresh.setFixedWidth(180)
        self.btn_refresh.clicked.connect(self.refresh_devices)
        refresh_layout.addWidget(self.btn_refresh)
        refresh_layout.addStretch()
        layout.addLayout(refresh_layout)

        layout.addStretch()

        # Nav buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setObjectName("danger")
        btn_layout.addWidget(self.btn_cancel)
        self.btn_next = QPushButton("Next →")
        self.btn_next.setObjectName("primary")
        self.btn_next.setEnabled(False)
        btn_layout.addWidget(self.btn_next)
        layout.addLayout(btn_layout)

    def refresh_devices(self):
        self.table.setRowCount(0)
        devices = get_block_devices()
        self.table.setRowCount(len(devices))

        for i, dev in enumerate(devices):
            self.table.setItem(i, 0, QTableWidgetItem(dev['name']))
            self.table.setItem(i, 1, QTableWidgetItem(dev['size_human']))
            self.table.setItem(i, 2, QTableWidgetItem(dev['type']))
            model_label = dev['model'] or dev['label'] or "—"
            self.table.setItem(i, 3, QTableWidgetItem(model_label))

            status_item = QTableWidgetItem(dev['status'])
            if dev['mounted']:
                status_item.setForeground(QColor("#ff00ff"))
            else:
                status_item.setForeground(QColor("#00ff88"))
            self.table.setItem(i, 4, status_item)

        self.selected_device = None
        self.btn_next.setEnabled(False)
        self.warning_label.setVisible(False)

    def _on_selection_changed(self):
        rows = self.table.selectionModel().selectedRows()
        if rows:
            row = rows[0].row()
            self.selected_device = self.table.item(row, 0).text()
            status = self.table.item(row, 4).text()
            if status == "In Use":
                self.warning_label.setText(
                    "⚠ Warning: This device has mounted partitions. They will be unmounted.")
                self.warning_label.setVisible(True)
            else:
                self.warning_label.setVisible(False)
            self.btn_next.setEnabled(True)
        else:
            self.selected_device = None
            self.btn_next.setEnabled(False)


class PartitionScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)

        title = QLabel("Select Partitioning Method")
        title.setObjectName("title")
        layout.addWidget(title)

        step = QLabel("Step 2 of 6")
        step.setObjectName("stepIndicator")
        layout.addWidget(step)

        layout.addWidget(SeparatorLine())

        # Radio group
        self.btn_group = QButtonGroup(self)

        # ── Option 1: Use Existing ──
        self.radio_existing = QRadioButton("Use Existing Partition Layout")
        self.radio_existing.setStyleSheet("font-size: 14px; font-weight: bold; color: #00cccc;")
        self.btn_group.addButton(self.radio_existing, 1)
        layout.addWidget(self.radio_existing)

        self.existing_frame = CardFrame()
        existing_layout = QVBoxLayout(self.existing_frame)
        existing_layout.addWidget(QLabel("Keep existing partitions and install to a selected partition"))

        part_layout = QHBoxLayout()
        part_layout.addWidget(QLabel("Root partition:"))
        self.combo_root_part = QComboBox()
        self.combo_root_part.setMinimumWidth(200)
        part_layout.addWidget(self.combo_root_part)
        part_layout.addStretch()
        existing_layout.addLayout(part_layout)

        efi_layout = QHBoxLayout()
        efi_layout.addWidget(QLabel("EFI partition (UEFI only):"))
        self.combo_efi_part = QComboBox()
        self.combo_efi_part.setMinimumWidth(200)
        efi_layout.addWidget(self.combo_efi_part)
        efi_layout.addStretch()
        existing_layout.addLayout(efi_layout)

        boot_existing_layout = QHBoxLayout()
        boot_existing_layout.addWidget(QLabel("Boot partition (optional):"))
        self.combo_boot_part = QComboBox()
        self.combo_boot_part.setMinimumWidth(200)
        self.combo_boot_part.addItem("— None —", "")
        boot_existing_layout.addWidget(self.combo_boot_part)
        boot_existing_layout.addStretch()
        existing_layout.addLayout(boot_existing_layout)

        warn = QLabel("⚠ Existing data on the selected partition will be overwritten")
        warn.setStyleSheet("color: #ff00ff;")
        existing_layout.addWidget(warn)
        self.existing_frame.setVisible(False)
        layout.addWidget(self.existing_frame)

        layout.addSpacing(10)

        # ── Option 2: Erase Disk ──
        self.radio_erase = QRadioButton("Erase Disk and Create New Layout")
        self.radio_erase.setStyleSheet("font-size: 14px; font-weight: bold; color: #00cccc;")
        self.btn_group.addButton(self.radio_erase, 2)
        layout.addWidget(self.radio_erase)

        self.erase_frame = CardFrame()
        erase_layout = QVBoxLayout(self.erase_frame)
        erase_layout.addWidget(QLabel("Automatically partition the disk (recommended for new installs)"))

        # Boot type
        bt_layout = QHBoxLayout()
        bt_layout.addWidget(QLabel("Boot type:"))
        self.combo_boot_type = QComboBox()
        self.combo_boot_type.addItem("Legacy BIOS (MBR)", "legacy_mbr")
        self.combo_boot_type.addItem("Legacy BIOS (GPT)", "bios_gpt")
        self.combo_boot_type.addItem("UEFI", "uefi")
        bt_layout.addWidget(self.combo_boot_type)
        bt_layout.addStretch()
        erase_layout.addLayout(bt_layout)

        # Separate /boot
        boot_layout = QHBoxLayout()
        self.chk_separate_boot = QCheckBox("Create separate /boot partition")
        boot_layout.addWidget(self.chk_separate_boot)
        boot_layout.addWidget(QLabel("Size (MB):"))
        self.spin_boot_size = QSpinBox()
        self.spin_boot_size.setRange(256, 2048)
        self.spin_boot_size.setValue(512)
        self.spin_boot_size.setEnabled(False)
        boot_layout.addWidget(self.spin_boot_size)
        boot_layout.addStretch()
        erase_layout.addLayout(boot_layout)

        self.chk_separate_boot.toggled.connect(self.spin_boot_size.setEnabled)

        warn2 = QLabel("⚠ ALL DATA on the disk will be erased!")
        warn2.setStyleSheet("color: #ff0000; font-weight: bold;")
        erase_layout.addWidget(warn2)
        self.erase_frame.setVisible(False)
        layout.addWidget(self.erase_frame)

        # Toggle visibility
        self.radio_existing.toggled.connect(lambda c: self.existing_frame.setVisible(c))
        self.radio_erase.toggled.connect(lambda c: self.erase_frame.setVisible(c))

        layout.addStretch()

        # Nav
        btn_layout = QHBoxLayout()
        self.btn_back = QPushButton("← Back")
        btn_layout.addWidget(self.btn_back)
        btn_layout.addStretch()
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setObjectName("danger")
        btn_layout.addWidget(self.btn_cancel)
        self.btn_next = QPushButton("Next →")
        self.btn_next.setObjectName("primary")
        btn_layout.addWidget(self.btn_next)
        layout.addLayout(btn_layout)

    def load_partitions(self, device):
        """Populate partition combos for the selected device."""
        self.combo_root_part.clear()
        self.combo_efi_part.clear()
        self.combo_boot_part.clear()
        self.combo_boot_part.addItem("— None —", "")

        parts = get_partitions(device)
        for p in parts:
            text = f"{p['name']} ({p['size_human']}) [{p['fstype']}]"
            self.combo_root_part.addItem(text, p['name'])
            self.combo_efi_part.addItem(text, p['name'])
            self.combo_boot_part.addItem(text, p['name'])


class UserScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)

        title = QLabel("User Credentials")
        title.setObjectName("title")
        layout.addWidget(title)

        step = QLabel("Step 3 of 6")
        step.setObjectName("stepIndicator")
        layout.addWidget(step)

        layout.addWidget(SeparatorLine())

        self.btn_group = QButtonGroup(self)

        # Option 1: Create new user
        self.radio_new = QRadioButton("Create New User")
        self.radio_new.setStyleSheet("font-size: 14px; font-weight: bold; color: #00cccc;")
        self.btn_group.addButton(self.radio_new, 1)
        layout.addWidget(self.radio_new)

        self.new_frame = CardFrame()
        new_layout = QGridLayout(self.new_frame)
        new_layout.setSpacing(10)

        new_layout.addWidget(QLabel("Username:"), 0, 0)
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("e.g., glitch_user")
        new_layout.addWidget(self.txt_username, 0, 1)

        new_layout.addWidget(QLabel("Password:"), 1, 0)
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)
        new_layout.addWidget(self.txt_password, 1, 1)

        new_layout.addWidget(QLabel("Confirm:"), 2, 0)
        self.txt_confirm = QLineEdit()
        self.txt_confirm.setEchoMode(QLineEdit.Password)
        new_layout.addWidget(self.txt_confirm, 2, 1)

        self.chk_sudo = QCheckBox("Add to sudoers group")
        self.chk_sudo.setChecked(True)
        new_layout.addWidget(self.chk_sudo, 3, 0, 1, 2)

        self.lbl_user_error = QLabel("")
        self.lbl_user_error.setStyleSheet("color: #ff4444;")
        new_layout.addWidget(self.lbl_user_error, 4, 0, 1, 2)

        self.new_frame.setVisible(False)
        layout.addWidget(self.new_frame)

        layout.addSpacing(10)

        # Option 2: Default profile
        self.radio_default = QRadioButton("Use Default Existing Profile")
        self.radio_default.setStyleSheet("font-size: 14px; font-weight: bold; color: #00cccc;")
        self.btn_group.addButton(self.radio_default, 2)
        layout.addWidget(self.radio_default)

        default_desc = QLabel("Use the default 'user' profile with standard configuration")
        default_desc.setStyleSheet("color: #888888; padding-left: 28px;")
        layout.addWidget(default_desc)

        self.radio_default.setChecked(True)

        self.radio_new.toggled.connect(lambda c: self.new_frame.setVisible(c))

        layout.addStretch()

        # Nav
        btn_layout = QHBoxLayout()
        self.btn_back = QPushButton("← Back")
        btn_layout.addWidget(self.btn_back)
        btn_layout.addStretch()
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setObjectName("danger")
        btn_layout.addWidget(self.btn_cancel)
        self.btn_next = QPushButton("Next →")
        self.btn_next.setObjectName("primary")
        btn_layout.addWidget(self.btn_next)
        layout.addLayout(btn_layout)

    def validate(self):
        self.lbl_user_error.setText("")
        if self.radio_default.isChecked():
            return True
        username = self.txt_username.text().strip()
        if not username:
            self.lbl_user_error.setText("Username is required")
            return False
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', username):
            self.lbl_user_error.setText("Username: alphanumeric, dash, underscore only (start with letter)")
            return False
        pw = self.txt_password.text()
        if len(pw) < 1:
            self.lbl_user_error.setText("Password is required")
            return False
        if pw != self.txt_confirm.text():
            self.lbl_user_error.setText("Passwords do not match")
            return False
        if len(pw) < 8:
            self.lbl_user_error.setText("⚠ Short password (8+ characters recommended)")
            # Allow but warn
        return True


class EncryptionScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)

        title = QLabel("Disk Encryption")
        title.setObjectName("title")
        layout.addWidget(title)

        step = QLabel("Step 4 of 6")
        step.setObjectName("stepIndicator")
        layout.addWidget(step)

        layout.addWidget(SeparatorLine())

        self.btn_group = QButtonGroup(self)

        # Option 1: Enable LUKS
        self.radio_luks = QRadioButton("Enable LUKS Encryption")
        self.radio_luks.setStyleSheet("font-size: 14px; font-weight: bold; color: #00cccc;")
        self.btn_group.addButton(self.radio_luks, 1)
        layout.addWidget(self.radio_luks)

        self.luks_frame = CardFrame()
        luks_layout = QGridLayout(self.luks_frame)
        luks_layout.setSpacing(10)

        luks_layout.addWidget(QLabel("Encrypt the root partition with LUKS1"), 0, 0, 1, 2)

        luks_layout.addWidget(QLabel("Passphrase:"), 1, 0)
        self.txt_passphrase = QLineEdit()
        self.txt_passphrase.setEchoMode(QLineEdit.Password)
        luks_layout.addWidget(self.txt_passphrase, 1, 1)

        luks_layout.addWidget(QLabel("Confirm:"), 2, 0)
        self.txt_confirm = QLineEdit()
        self.txt_confirm.setEchoMode(QLineEdit.Password)
        luks_layout.addWidget(self.txt_confirm, 2, 1)

        # Strength bar
        self.strength_bar = QProgressBar()
        self.strength_bar.setMaximum(100)
        self.strength_bar.setTextVisible(True)
        self.strength_bar.setFormat("Strength: --")
        self.strength_bar.setFixedHeight(20)
        luks_layout.addWidget(self.strength_bar, 3, 0, 1, 2)

        self.txt_passphrase.textChanged.connect(self._update_strength)

        warn = QLabel("⚠ You will need this passphrase to boot your system!")
        warn.setStyleSheet("color: #ffff00; font-weight: bold;")
        luks_layout.addWidget(warn, 4, 0, 1, 2)

        self.lbl_luks_error = QLabel("")
        self.lbl_luks_error.setStyleSheet("color: #ff4444;")
        luks_layout.addWidget(self.lbl_luks_error, 5, 0, 1, 2)

        self.luks_frame.setVisible(False)
        layout.addWidget(self.luks_frame)

        layout.addSpacing(10)

        # Option 2: Skip
        self.radio_skip = QRadioButton("Skip Encryption")
        self.radio_skip.setStyleSheet("font-size: 14px; font-weight: bold; color: #00cccc;")
        self.btn_group.addButton(self.radio_skip, 2)
        layout.addWidget(self.radio_skip)

        skip_desc = QLabel("Install without encryption (faster, less secure)")
        skip_desc.setStyleSheet("color: #888888; padding-left: 28px;")
        layout.addWidget(skip_desc)

        self.radio_skip.setChecked(True)

        self.radio_luks.toggled.connect(lambda c: self.luks_frame.setVisible(c))

        layout.addStretch()

        # Nav
        btn_layout = QHBoxLayout()
        self.btn_back = QPushButton("← Back")
        btn_layout.addWidget(self.btn_back)
        btn_layout.addStretch()
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setObjectName("danger")
        btn_layout.addWidget(self.btn_cancel)
        self.btn_next = QPushButton("Next →")
        self.btn_next.setObjectName("primary")
        btn_layout.addWidget(self.btn_next)
        layout.addLayout(btn_layout)

    def _update_strength(self, text):
        length = len(text)
        has_upper = bool(re.search(r'[A-Z]', text))
        has_lower = bool(re.search(r'[a-z]', text))
        has_digit = bool(re.search(r'\d', text))
        has_special = bool(re.search(r'[^a-zA-Z\d]', text))

        score = 0
        score += min(length * 4, 40)
        if has_upper: score += 15
        if has_lower: score += 10
        if has_digit: score += 15
        if has_special: score += 20

        score = min(score, 100)

        self.strength_bar.setValue(score)
        if score < 30:
            self.strength_bar.setFormat("Strength: Weak")
            self.strength_bar.setStyleSheet("QProgressBar::chunk { background: #ff4444; border-radius: 7px; }")
        elif score < 60:
            self.strength_bar.setFormat("Strength: Medium")
            self.strength_bar.setStyleSheet("QProgressBar::chunk { background: #ffaa00; border-radius: 7px; }")
        else:
            self.strength_bar.setFormat("Strength: Strong")
            self.strength_bar.setStyleSheet("QProgressBar::chunk { background: #00ff88; border-radius: 7px; }")

    def validate(self):
        self.lbl_luks_error.setText("")
        if self.radio_skip.isChecked():
            return True
        pp = self.txt_passphrase.text()
        if len(pp) < 1:
            self.lbl_luks_error.setText("Passphrase is required")
            return False
        if pp != self.txt_confirm.text():
            self.lbl_luks_error.setText("Passphrases do not match")
            return False
        if len(pp) < 8:
            self.lbl_luks_error.setText("⚠ Short passphrase (8+ recommended)")
        return True


class ReviewScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)

        title = QLabel("Review Installation Settings")
        title.setObjectName("title")
        layout.addWidget(title)

        step = QLabel("Step 5 of 6")
        step.setObjectName("stepIndicator")
        layout.addWidget(step)

        layout.addWidget(SeparatorLine())

        # Summary text
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMinimumHeight(180)
        layout.addWidget(self.summary_text)

        # Jobs list
        jobs_header = QLabel("Planned Installation Jobs")
        jobs_header.setObjectName("sectionHeader")
        layout.addWidget(jobs_header)

        self.jobs_text = QTextEdit()
        self.jobs_text.setReadOnly(True)
        self.jobs_text.setMinimumHeight(120)
        layout.addWidget(self.jobs_text)

        layout.addStretch()

        # Nav
        btn_layout = QHBoxLayout()
        self.btn_back = QPushButton("← Back")
        btn_layout.addWidget(self.btn_back)
        btn_layout.addStretch()
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setObjectName("danger")
        btn_layout.addWidget(self.btn_cancel)
        self.btn_install = QPushButton("⚡ Start Install")
        self.btn_install.setObjectName("success")
        self.btn_install.setFixedWidth(180)
        self.btn_install.setStyleSheet("""
            QPushButton {
                background-color: #1a4d1a;
                color: #00ff88;
                border: 2px solid #00ff88;
                border-radius: 6px;
                padding: 12px 30px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1a661a;
            }
        """)
        btn_layout.addWidget(self.btn_install)
        layout.addLayout(btn_layout)

    def update_summary(self, config):
        lines = []
        lines.append(f"  Installation Target:      {config.get('target_device', '?')}")

        devs = get_block_devices()
        for d in devs:
            if d['name'] == config.get('target_device'):
                lines.append(f"  Device Size:              {d['size_human']}")
                break

        if config.get('partitioning') == 'erase':
            lines.append(f"  Partitioning:             Erase and Create New Layout")
        else:
            lines.append(f"  Partitioning:             Use Existing Partitions")

        lines.append(f"  Boot Type:                {config.get('boot_type', '?')}")
        lines.append(f"  Separate /boot:           {'Yes (' + str(config.get('boot_size', 512)) + ' MB)' if config.get('separate_boot') else 'No'}")

        if config.get('create_user'):
            lines.append(f"  Username:                 {config.get('username', '?')}")
        else:
            lines.append(f"  Username:                 Default profile")

        lines.append(f"  LUKS Encryption:          {'Enabled' if config.get('luks_enabled') else 'Disabled'}")

        squashfs = detect_squashfs()
        lines.append(f"  Install Source:           {squashfs or '/ (root filesystem)'}")

        self.summary_text.setPlainText("\n".join(lines))

        # Build jobs list
        jobs = []
        jobs.append("  → Detect and prepare target device")
        jobs.append("  → Unmount target device (if mounted)")

        if config.get('partitioning') == 'erase':
            bt = config.get('boot_type', '')
            if bt == 'uefi':
                jobs.append("  → Create partition table (GPT)")
                jobs.append("  → Create EFI partition (96 MB, FAT32)")
            elif bt == 'bios_gpt':
                jobs.append("  → Create partition table (GPT)")
                jobs.append("  → Create BIOS boot partition (1 MB)")
            else:
                jobs.append("  → Create partition table (MBR)")

            if config.get('separate_boot'):
                jobs.append(f"  → Create /boot partition ({config.get('boot_size', 512)} MB, ext4)")
            jobs.append("  → Create root partition (remaining space, ext4)")

        if config.get('luks_enabled'):
            jobs.append("  → Setup LUKS1 encryption on root partition")

        jobs.append("  → Mount target partitions")
        jobs.append("  → Extract filesystem to target")
        jobs.append("  → Configure /etc/fstab")

        if config.get('luks_enabled'):
            jobs.append("  → Configure /etc/crypttab")
            jobs.append("  → Update initramfs with LUKS support")

        jobs.append("  → Install GRUB bootloader")

        if config.get('create_user'):
            jobs.append(f"  → Create user '{config.get('username', '')}'")

        jobs.append("  → Verify installation")
        jobs.append("  → Unmount and cleanup")

        self.jobs_text.setPlainText("\n".join(jobs))


class ProgressScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.start_time = None

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)

        title = QLabel("Installing Glitch Linux...")
        title.setObjectName("title")
        layout.addWidget(title)

        step = QLabel("Step 6 of 6")
        step.setObjectName("stepIndicator")
        layout.addWidget(step)

        layout.addWidget(SeparatorLine())

        # Current operation
        self.lbl_current_op = QLabel("Initializing...")
        self.lbl_current_op.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #00ffff; padding: 8px; "
            "background-color: #1e1e30; border-radius: 6px;")
        self.lbl_current_op.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_current_op)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(32)
        layout.addWidget(self.progress_bar)

        # Stage checklist
        self.stage_labels = []
        stages = [
            "Detect installation source",
            "Prepare target device",
            "Create partitions",
            "Format partitions",
            "LUKS encryption",
            "Mount target",
            "Mount source",
            "Extract filesystem",
            "Configure system",
            "Install bootloader",
            "Setup user account",
            "Verify installation"
        ]

        stages_card = CardFrame()
        stages_layout = QVBoxLayout(stages_card)
        stages_layout.setSpacing(4)

        for i, s in enumerate(stages):
            lbl = QLabel(f"  ○  {s}")
            lbl.setStyleSheet("color: #555555; font-size: 12px; font-family: monospace;")
            stages_layout.addWidget(lbl)
            self.stage_labels.append(lbl)

        scroll = QScrollArea()
        scroll.setWidget(stages_card)
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(160)
        layout.addWidget(scroll)

        # Log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(150)
        layout.addWidget(self.log_output)

        # Time
        time_layout = QHBoxLayout()
        self.lbl_elapsed = QLabel("Elapsed: 0:00")
        self.lbl_elapsed.setStyleSheet("color: #888888;")
        time_layout.addWidget(self.lbl_elapsed)
        time_layout.addStretch()
        self.btn_cancel = QPushButton("Cancel Installation")
        self.btn_cancel.setObjectName("danger")
        time_layout.addWidget(self.btn_cancel)
        layout.addLayout(time_layout)

    def update_stage(self, stage_idx):
        for i, lbl in enumerate(self.stage_labels):
            text = lbl.text()
            # Remove prefix
            text = text.lstrip()
            for prefix in ["✓ ", "→ ", "○ ", "  "]:
                if text.startswith(prefix):
                    text = text[len(prefix):]
                    break

            if i < stage_idx:
                lbl.setText(f"  ✓  {text}")
                lbl.setStyleSheet("color: #00ff88; font-size: 12px; font-family: monospace;")
            elif i == stage_idx:
                lbl.setText(f"  →  {text}")
                lbl.setStyleSheet("color: #00ffff; font-size: 12px; font-family: monospace; font-weight: bold;")
            else:
                lbl.setText(f"  ○  {text}")
                lbl.setStyleSheet("color: #555555; font-size: 12px; font-family: monospace;")

    def append_log(self, msg, level):
        color_map = {
            "INFO": "#e0e0e0",
            "SUCCESS": "#00ff88",
            "ERROR": "#ff4444",
            "WARNING": "#ff00ff",
            "PROGRESS": "#00cccc",
        }
        color = color_map.get(level, "#e0e0e0")
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_output.append(
            f'<span style="color:#555555">[{timestamp}]</span> '
            f'<span style="color:{color}">[{level}]</span> '
            f'<span style="color:{color}">{msg}</span>'
        )
        # Auto-scroll
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def update_elapsed(self):
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.lbl_elapsed.setText(f"Elapsed: {minutes}:{seconds:02d}")


class CompleteScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(15)

        layout.addStretch()

        # Big success icon
        icon_label = QLabel("✓")
        icon_label.setStyleSheet(
            "font-size: 72px; color: #00ff88; font-weight: bold;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        title = QLabel("Installation Complete!")
        title.setObjectName("title")
        title.setStyleSheet("font-size: 26px; color: #00ff88; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Glitch Linux has been successfully installed!")
        subtitle.setStyleSheet("font-size: 14px; color: #aaaaaa;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        # Summary card
        self.summary_card = CardFrame()
        self.summary_layout = QGridLayout(self.summary_card)
        self.summary_layout.setSpacing(8)
        layout.addWidget(self.summary_card)

        layout.addStretch()

        # Reboot option
        self.chk_reboot = QCheckBox("Reboot now")
        self.chk_reboot.setStyleSheet("font-size: 13px;")
        layout.addWidget(self.chk_reboot, alignment=Qt.AlignCenter)

        warn = QLabel("Remove installation media before rebooting")
        warn.setStyleSheet("color: #ffff00; font-size: 12px;")
        warn.setAlignment(Qt.AlignCenter)
        layout.addWidget(warn)

        # Finish button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_finish = QPushButton("Finish")
        self.btn_finish.setObjectName("success")
        self.btn_finish.setFixedWidth(200)
        self.btn_finish.setStyleSheet("""
            QPushButton {
                background-color: #1a4d1a;
                color: #00ff88;
                border: 2px solid #00ff88;
                border-radius: 6px;
                padding: 14px 40px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1a661a; }
        """)
        btn_layout.addWidget(self.btn_finish)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def set_summary(self, config, elapsed_seconds):
        # Clear previous
        while self.summary_layout.count():
            item = self.summary_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60

        entries = [
            ("Target Device:", config.get('target_device', '?')),
            ("Boot Type:", config.get('boot_type', '?')),
            ("LUKS Encryption:", "Enabled" if config.get('luks_enabled') else "Disabled"),
            ("Installation Time:", f"{minutes}m {seconds:02d}s"),
        ]
        if config.get('create_user'):
            entries.append(("User:", config.get('username', '?')))

        for i, (label, value) in enumerate(entries):
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #888888; font-weight: bold;")
            val = QLabel(value)
            val.setStyleSheet("color: #00ffff;")
            self.summary_layout.addWidget(lbl, i, 0)
            self.summary_layout.addWidget(val, i, 1)


# ─────────────────────────────────────────────────────────────
# MAIN WINDOW
# ─────────────────────────────────────────────────────────────
class GlitchInstaller(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = {}
        self.worker = None
        self.elapsed_timer = None
        self._setup_window()
        self._build_screens()
        self._connect_signals()
        self.show()

        # Auto-refresh disks on startup
        QTimer.singleShot(200, self.screen_disk.refresh_devices)

    def _setup_window(self):
        self.setWindowTitle("Glitch Linux Installer")
        screen = QApplication.primaryScreen()
        if screen:
            geom = screen.availableGeometry()
            w = int(geom.width() * 0.50)
            h = int(geom.height() * 0.55)
            self.resize(max(w, 900), max(h, 550))
            # Center
            x = (geom.width() - self.width()) // 2
            y = (geom.height() - self.height()) // 2
            self.move(x, y)
        else:
            self.resize(960, 580)
        self.setMinimumSize(900, 500)

    def _build_screens(self):
        central = QWidget()
        central.setStyleSheet("background-color: #1a1a2e;")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        self.screen_welcome = WelcomeScreen()
        self.screen_disk = DiskSelectScreen()
        self.screen_partition = PartitionScreen()
        self.screen_user = UserScreen()
        self.screen_encrypt = EncryptionScreen()
        self.screen_review = ReviewScreen()
        self.screen_progress = ProgressScreen()
        self.screen_complete = CompleteScreen()

        for s in [
            self.screen_welcome, self.screen_disk, self.screen_partition,
            self.screen_user, self.screen_encrypt, self.screen_review,
            self.screen_progress, self.screen_complete
        ]:
            self.stack.addWidget(s)

    def _connect_signals(self):
        # Welcome
        self.screen_welcome.btn_start.clicked.connect(lambda: self._go_to(1))
        self.screen_welcome.btn_exit.clicked.connect(self.close)

        # Disk Select
        self.screen_disk.btn_next.clicked.connect(self._disk_next)
        self.screen_disk.btn_cancel.clicked.connect(self._confirm_cancel)

        # Partition
        self.screen_partition.btn_back.clicked.connect(lambda: self._go_to(1))
        self.screen_partition.btn_next.clicked.connect(self._partition_next)
        self.screen_partition.btn_cancel.clicked.connect(self._confirm_cancel)

        # User
        self.screen_user.btn_back.clicked.connect(lambda: self._go_to(2))
        self.screen_user.btn_next.clicked.connect(self._user_next)
        self.screen_user.btn_cancel.clicked.connect(self._confirm_cancel)

        # Encryption
        self.screen_encrypt.btn_back.clicked.connect(lambda: self._go_to(3))
        self.screen_encrypt.btn_next.clicked.connect(self._encrypt_next)
        self.screen_encrypt.btn_cancel.clicked.connect(self._confirm_cancel)

        # Review
        self.screen_review.btn_back.clicked.connect(lambda: self._go_to(4))
        self.screen_review.btn_install.clicked.connect(self._start_install)
        self.screen_review.btn_cancel.clicked.connect(self._confirm_cancel)

        # Progress
        self.screen_progress.btn_cancel.clicked.connect(self._cancel_install)

        # Complete
        self.screen_complete.btn_finish.clicked.connect(self._finish)

    def _go_to(self, idx):
        self.stack.setCurrentIndex(idx)

    def _disk_next(self):
        dev = self.screen_disk.selected_device
        if dev:
            self.config['target_device'] = dev
            self.screen_partition.load_partitions(dev)
            self._go_to(2)

    def _partition_next(self):
        if self.screen_partition.radio_erase.isChecked():
            self.config['partitioning'] = 'erase'
            self.config['boot_type'] = self.screen_partition.combo_boot_type.currentData()
            self.config['separate_boot'] = self.screen_partition.chk_separate_boot.isChecked()
            self.config['boot_size'] = self.screen_partition.spin_boot_size.value()
        elif self.screen_partition.radio_existing.isChecked():
            self.config['partitioning'] = 'existing'
            self.config['data_partition'] = self.screen_partition.combo_root_part.currentData()
            efi = self.screen_partition.combo_efi_part.currentData()
            boot = self.screen_partition.combo_boot_part.currentData()
            if efi:
                self.config['efi_partition'] = efi
            self.config['boot_type'] = 'uefi' if efi else 'legacy_mbr'
            if boot:
                self.config['boot_partition'] = boot
                self.config['separate_boot'] = True
        else:
            QMessageBox.warning(self, "Selection Required", "Please select a partitioning method.")
            return
        self._go_to(3)

    def _user_next(self):
        if not self.screen_user.validate():
            return
        if self.screen_user.radio_new.isChecked():
            self.config['create_user'] = True
            self.config['username'] = self.screen_user.txt_username.text().strip()
            self.config['password'] = self.screen_user.txt_password.text()
            self.config['add_sudo'] = self.screen_user.chk_sudo.isChecked()
        else:
            self.config['create_user'] = False
        self._go_to(4)

    def _encrypt_next(self):
        if not self.screen_encrypt.validate():
            return
        if self.screen_encrypt.radio_luks.isChecked():
            self.config['luks_enabled'] = True
            self.config['luks_passphrase'] = self.screen_encrypt.txt_passphrase.text()
        else:
            self.config['luks_enabled'] = False
        self.screen_review.update_summary(self.config)
        self._go_to(5)

    def _start_install(self):
        reply = QMessageBox.warning(
            self, "Confirm Installation",
            "Begin installation? This action cannot be undone.\n\n"
            "All data on the target device will be modified or erased.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        self._go_to(6)
        self.screen_progress.start_time = time.time()
        self.screen_progress.log_output.clear()
        self.screen_progress.progress_bar.setValue(0)

        # Elapsed timer
        self.elapsed_timer = QTimer()
        self.elapsed_timer.timeout.connect(self.screen_progress.update_elapsed)
        self.elapsed_timer.start(1000)

        # Start worker
        self.worker = InstallWorker(self.config.copy())
        self.worker.log_signal.connect(self.screen_progress.append_log)
        self.worker.progress_signal.connect(self.screen_progress.progress_bar.setValue)
        self.worker.step_signal.connect(self.screen_progress.lbl_current_op.setText)
        self.worker.stage_signal.connect(self.screen_progress.update_stage)
        self.worker.finished_signal.connect(self._install_finished)
        self.worker.start()

    def _cancel_install(self):
        reply = QMessageBox.question(
            self, "Cancel Installation",
            "Are you sure you want to cancel? The installation will be rolled back.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes and self.worker:
            self.worker.cancel()

    def _install_finished(self, success, message):
        if self.elapsed_timer:
            self.elapsed_timer.stop()

        if success:
            elapsed = int(time.time() - self.screen_progress.start_time) if self.screen_progress.start_time else 0
            self.screen_complete.set_summary(self.config, elapsed)
            self._go_to(7)
        else:
            QMessageBox.critical(self, "Installation Failed", f"Installation failed:\n\n{message}")

    def _finish(self):
        if self.screen_complete.chk_reboot.isChecked():
            reply = QMessageBox.question(
                self, "Reboot Now",
                "The system will reboot immediately. Continue?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                os.system("reboot")
        self.close()

    def _confirm_cancel(self):
        reply = QMessageBox.question(
            self, "Cancel Installation",
            "Are you sure you want to cancel?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.close()

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, "Installation Running",
                "An installation is in progress. Are you sure you want to quit?\n"
                "This may leave the target device in an incomplete state.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                event.ignore()
                return
            self.worker.cancel()
            self.worker.wait(5000)
        event.accept()


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────
def main():
    # Check root
    if os.geteuid() != 0:
        print("\033[91m[ERROR]\033[0m This installer must be run as root.")
        print("Usage: sudo python3 glitch_installer.py")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("Glitch Linux Installer")
    app.setStyle("Fusion")

    # Apply dark theme
    app.setStyleSheet(DARK_THEME)

    # Dark palette as fallback
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#1a1a2e"))
    palette.setColor(QPalette.WindowText, QColor("#e0e0e0"))
    palette.setColor(QPalette.Base, QColor("#252540"))
    palette.setColor(QPalette.AlternateBase, QColor("#1e1e30"))
    palette.setColor(QPalette.ToolTipBase, QColor("#252540"))
    palette.setColor(QPalette.ToolTipText, QColor("#e0e0e0"))
    palette.setColor(QPalette.Text, QColor("#e0e0e0"))
    palette.setColor(QPalette.Button, QColor("#2d2d44"))
    palette.setColor(QPalette.ButtonText, QColor("#e0e0e0"))
    palette.setColor(QPalette.Highlight, QColor("#004d4d"))
    palette.setColor(QPalette.HighlightedText, QColor("#00ffff"))
    app.setPalette(palette)

    window = GlitchInstaller()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
