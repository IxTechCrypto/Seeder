"""
Seeder Flashing Engine: Port detection and esptool invocation.
"""

import sys
import os
import re
import threading
import time
import serial.tools.list_ports
import esptool

# Get base directory for bundled assets (supports PyInstaller --onefile)
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

KNOWN_HARDWARE = [
    # Espressif native USB-JTAG/CDC (ESP32-S3)
    {"vid": 0x303A, "pid": 0x1001, "target": "tdisplay-s3", "name": "LilyGO T-Display-S3 (USB-JTAG)"},
    {"vid": 0x303A, "pid": 0x0002, "target": "tdisplay-s3", "name": "ESP32-S3 CDC"},
    # Silicon Labs CP210x (TTGO T-Display)
    {"vid": 0x10C4, "pid": 0xEA60, "target": "tdisplay", "name": "LilyGO T-Display (CP210x)"},
    # WCH CH340 / CH9102 (T-Display & T-Display-S3 UART variants)
    {"vid": 0x1A86, "pid": 0x7523, "target": "tdisplay-s3", "name": "LilyGO USB-UART (CH340)"},
    {"vid": 0x1A86, "pid": 0x55D4, "target": "tdisplay-s3", "name": "LilyGO USB-UART (CH9102)"},
    {"vid": 0x1A86, "pid": 0x55D3, "target": "tdisplay-s3", "name": "LilyGO USB-UART (CH343)"},
]

class PortInfo:
    def __init__(self, port, desc, hwid, vid=None, pid=None, default_target="tdisplay-s3", is_known=False, display_name=""):
        self.port = port
        self.desc = desc
        self.hwid = hwid
        self.vid = vid
        self.pid = pid
        self.default_target = default_target
        self.is_known = is_known
        self.display_name = display_name or f"{port} - {desc}"

    def __repr__(self):
        return f"<PortInfo {self.port} {self.display_name} target={self.default_target}>"


def scan_ports():
    """Scans all available COM ports and prioritizes LilyGO / ESP32 hardware."""
    available = []
    for p in serial.tools.list_ports.comports():
        vid = p.vid
        pid = p.pid
        desc = p.description or "Unknown Serial Device"
        hwid = p.hwid or ""

        target = "tdisplay-s3"
        is_known = False
        display_name = f"{p.device}: {desc}"

        # Match known VIDs/PIDs
        for hw in KNOWN_HARDWARE:
            if vid == hw["vid"] and (hw["pid"] is None or pid == hw["pid"]):
                target = hw["target"]
                is_known = True
                display_name = f"{p.device}: {hw['name']}"
                break

        # Check description substrings if VID/PID didn't catch it
        if not is_known:
            d_lower = desc.lower()
            if "esp32-s3" in d_lower or "jtag" in d_lower:
                target = "tdisplay-s3"
                is_known = True
                display_name = f"{p.device}: LilyGO T-Display-S3"
            elif "cp210" in d_lower or "ch340" in d_lower or "ch9102" in d_lower or "uart" in d_lower or "usb-serial" in d_lower:
                is_known = True
                target = "tdisplay-s3"
                display_name = f"{p.device}: {desc}"

        info = PortInfo(p.device, desc, hwid, vid, pid, target, is_known, display_name)
        # Put known hardware first
        if is_known:
            available.insert(0, info)
        else:
            available.append(info)

    return available


class RealtimeStream:
    """Intercepts esptool output and pushes lines to callbacks."""
    def __init__(self, log_cb, progress_cb):
        self.log_cb = log_cb
        self.progress_cb = progress_cb
        self.buffer = ""

    def write(self, s):
        if not s:
            return
        self.buffer += s
        while "\n" in self.buffer or "\r" in self.buffer:
            # Handle both CRLF and raw CR line updates (like esptool progress)
            n_idx = self.buffer.find("\n")
            r_idx = self.buffer.find("\r")
            
            if n_idx != -1 and (r_idx == -1 or n_idx < r_idx):
                line = self.buffer[:n_idx].strip()
                self.buffer = self.buffer[n_idx + 1:]
            elif r_idx != -1:
                line = self.buffer[:r_idx].strip()
                self.buffer = self.buffer[r_idx + 1:]
            else:
                break

            if line:
                self.log_cb(line)
                self._check_progress(line)

    def _check_progress(self, line):
        # Match "Writing at 0x... (5 %)"
        m1 = re.search(r'\((\d+)\s*%\)', line)
        if m1:
            pct = int(m1.group(1))
            self.progress_cb(pct, f"Writing flash... {pct}%")
            return

        # Match "Writing at ... 54.9% 160.00kB"
        m2 = re.search(r'(\d+(?:\.\d+)?)%', line)
        if m2:
            pct = int(float(m2.group(1)))
            self.progress_cb(pct, f"Writing flash... {pct}%")
            return

        # Stage checkpoints
        if "Connecting" in line:
            self.progress_cb(5, "Connecting to ESP32 bootloader...")
        elif "Chip type:" in line or "Detecting chip type" in line:
            self.progress_cb(10, f"Detected: {line}")
        elif "Erasing flash" in line:
            self.progress_cb(15, "Erasing flash partitions...")
        elif "Hash of data verified" in line:
            self.progress_cb(98, "Verifying cryptographic image hash...")
        elif "Hard resetting" in line:
            self.progress_cb(100, "Flash verified! Rebooting Seeder...")

    def flush(self):
        if self.buffer.strip():
            self.log_cb(self.buffer.strip())
            self.buffer = ""


def flash_firmware(port, target, progress_cb, log_cb):
    """
    Executes esptool flash for target ('tdisplay-s3' or 'tdisplay').
    Returns (success: bool, message: str).
    """
    firmware_dir = get_resource_path(os.path.join("firmware", target))
    if not os.path.exists(firmware_dir):
        return False, f"Firmware directory not found: {firmware_dir}"

    bootloader = os.path.join(firmware_dir, "bootloader.bin")
    partitions = os.path.join(firmware_dir, "partitions.bin")
    boot_app0  = os.path.join(firmware_dir, "boot_app0.bin")
    firmware   = os.path.join(firmware_dir, "firmware.bin")

    for f, desc in [(bootloader, "Bootloader"), (partitions, "Partition Table"), 
                    (boot_app0, "Boot App0"), (firmware, "Firmware App")]:
        if not os.path.exists(f):
            return False, f"Missing {desc} binary: {f}"

    if target == "tdisplay-s3":
        args = [
            "--chip", "esp32s3",
            "--port", port,
            "--baud", "115200",
            "--before", "default-reset",
            "--after", "hard-reset",
            "write-flash",
            "-z",
            "--flash-mode", "dio",
            "--flash-freq", "80m",
            "--flash-size", "16MB",
            "0x0000", bootloader,
            "0x8000", partitions,
            "0xe000", boot_app0,
            "0x10000", firmware
        ]
    else: # tdisplay (ESP32)
        args = [
            "--chip", "esp32",
            "--port", port,
            "--baud", "115200",
            "--before", "default-reset",
            "--after", "hard-reset",
            "write-flash",
            "-z",
            "--flash-mode", "dio",
            "--flash-freq", "80m",
            "--flash-size", "4MB",
            "0x1000", bootloader,
            "0x8000", partitions,
            "0xe000", boot_app0,
            "0x10000", firmware
        ]

    log_cb(f"[*] Initializing flash sequence for target: {target.upper()}")
    log_cb(f"[*] Target Port: {port} at 115200 baud")
    progress_cb(2, "Initializing flashing engine...")

    stream = RealtimeStream(log_cb, progress_cb)
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    sys.stdout = stream
    sys.stderr = stream

    success = False
    error_msg = ""
    try:
        esptool.main(args)
        stream.flush()
        success = True
        progress_cb(100, "Firmware flashed successfully!")
        log_cb("[✓] SUCCESS: Seeder firmware has been written and verified.")
        log_cb("[✓] Hardware reset completed. Board is now booting into Seeder!")
    except Exception as e:
        stream.flush()
        error_msg = str(e)
        log_cb(f"[!] ERROR: Flashing failed: {error_msg}")
        progress_cb(0, "Flashing failed!")
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    return success, error_msg
