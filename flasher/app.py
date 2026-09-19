"""
Seeder Flasher - Clean Cyberpunk Hardware Installer UI
Designed to match the high-tech Torii / Bitaxe clean cyber HUD aesthetic.
"""

import sys
import os
import io
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

# Provide fallback for sys.stdout/stderr in windowed mode
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

# Ensure flasher directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine

# Palette - Clean Torii Cyberpunk Theme
BG_MAIN       = "#06080e"   # Deep obsidian
BG_PANEL      = "#0b101a"   # Card container background
BG_TABLE      = "#080c14"   # Table background
BG_ROW_EVEN   = "#080c14"   # Alternating row
BG_ROW_ODD    = "#0b101a"   # Alternating row
BG_ROW_HOVER  = "#121b2c"   # Row hover state
BG_ROW_SEL    = "#15243c"   # Selected row background
BORDER_CYAN   = "#00f0ff"   # Electric neon cyan
BORDER_DARK   = "#182338"   # Subtle structural border
NEON_CYAN     = "#00f0ff"   # Primary cyan accent
NEON_CYAN_DIM = "#007a82"   # Dim cyan
TEXT_WHITE    = "#f0f6fc"   # Bright white text
TEXT_MUTED    = "#687792"   # Steel blue-gray
TEXT_DARK     = "#06080e"   # Dark button text
GREEN_ACTIVE  = "#00ff9d"   # Link verified green
AMBER_WARN    = "#ffaa00"   # Warning amber


class HeaderBanner(tk.Canvas):
    """Top banner with slanted slashes and bold glowing title."""
    def __init__(self, parent, width=800, height=64, **kwargs):
        super().__init__(parent, width=width, height=height, bg=BG_MAIN, highlightthickness=0, **kwargs)
        self.w = width
        self.h = height
        self.draw()

    def draw(self):
        self.delete("all")
        # 5 slanted slashes in top left
        for i in range(5):
            x = 24 + i * 11
            self.create_line(x, 24, x + 8, 12, fill=NEON_CYAN, width=3)

        # Micro icon: cyber chip
        cx = 24 + 5 * 11 + 16
        cy = 38
        self.create_rectangle(cx, cy - 10, cx + 18, cy + 8, outline=NEON_CYAN, width=2, fill="#0c1524")
        self.create_line(cx + 4, cy - 10, cx + 4, cy - 13, fill=NEON_CYAN, width=1)
        self.create_line(cx + 9, cy - 10, cx + 9, cy - 13, fill=NEON_CYAN, width=1)
        self.create_line(cx + 14, cy - 10, cx + 14, cy - 13, fill=NEON_CYAN, width=1)
        self.create_line(cx + 4, cy + 8, cx + 4, cy + 11, fill=NEON_CYAN, width=1)
        self.create_line(cx + 9, cy + 8, cx + 9, cy + 11, fill=NEON_CYAN, width=1)
        self.create_line(cx + 14, cy + 8, cx + 14, cy + 11, fill=NEON_CYAN, width=1)
        self.create_rectangle(cx + 6, cy - 4, cx + 12, cy + 2, fill=NEON_CYAN, outline="")

        # Title: SEEDER FLASHER
        self.create_text(
            cx + 28, cy - 1, anchor=tk.W,
            text="SEEDER FLASHER", fill=NEON_CYAN, font=("Segoe UI", 17, "bold")
        )


class StepperBar(tk.Canvas):
    """4-step workflow indicator bar."""
    def __init__(self, parent, width=800, height=44, **kwargs):
        super().__init__(parent, width=width, height=height, bg=BG_MAIN, highlightthickness=0, **kwargs)
        self.w = width
        self.h = height
        self.active_step = 1
        self.draw()

    def set_step(self, step):
        self.active_step = step
        self.draw()

    def draw(self):
        self.delete("all")
        # Card container with dark border
        pad_x = 24
        cw = self.w - pad_x * 2
        ch = 38
        y = 2

        self.create_rectangle(pad_x, y, pad_x + cw, y + ch, fill=BG_PANEL, outline=BORDER_DARK, width=1)

        steps = [
            (1, "DISCOVERY"),
            (2, "CONFIGURE & REVIEW"),
            (3, "DEPLOYING"),
            (4, "MONITOR")
        ]

        total_steps = len(steps)
        step_width = cw / total_steps

        for i, (num, label) in enumerate(steps):
            cx = pad_x + step_width * i + step_width / 2
            cy = y + ch / 2

            is_active = (self.active_step >= num)
            is_current = (self.active_step == num)

            col = NEON_CYAN if (is_current or is_active) else TEXT_MUTED

            # Number badge
            num_str = {1: "①", 2: "②", 3: "③", 4: "④"}.get(num, str(num))
            self.create_text(
                cx - 42, cy,
                text=num_str, fill=col, font=("Segoe UI", 11, "bold")
            )

            # Step title
            self.create_text(
                cx + 8, cy,
                text=label, fill=col, font=("Consolas", 9, "bold")
            )

            # Connecting line to next step
            if i < total_steps - 1:
                lx1 = pad_x + step_width * (i + 1) - 24
                lx2 = pad_x + step_width * (i + 1) + 24
                line_col = NEON_CYAN_DIM if (self.active_step > num) else "#182338"
                self.create_line(lx1, cy, lx2, cy, fill=line_col, width=1)


class CyberTable(tk.Frame):
    """Clean cyber data table displaying connected devices with selectable rows."""
    def __init__(self, parent, on_select_callback, **kwargs):
        super().__init__(parent, bg=BG_TABLE, bd=1, relief=tk.SOLID, highlightthickness=1, highlightbackground=BORDER_DARK, **kwargs)
        self.on_select_callback = on_select_callback
        self.rows_data = []
        self.row_cells = []  # list of lists of labels
        self.selected_idx = -1

        # Configure columns
        self.columnconfigure(0, minsize=90)
        self.columnconfigure(1, minsize=120)
        self.columnconfigure(2, minsize=180)
        self.columnconfigure(3, weight=1, minsize=240)
        self.columnconfigure(4, minsize=140)

        self._build_header()

    def _build_header(self):
        cols = [
            (0, "PORT"),
            (1, "VID:PID"),
            (2, "MANUFACTURER"),
            (3, "PRODUCT"),
            (4, "STATUS")
        ]
        for col_idx, name in cols:
            lbl = tk.Label(
                self, text=name,
                font=("Consolas", 9, "bold"), fg=NEON_CYAN, bg="#0d1422",
                anchor=tk.W, padx=12, pady=7
            )
            lbl.grid(row=0, column=col_idx, sticky="nsew")

        # Thin header underline
        div = tk.Frame(self, height=1, bg="#19253b")
        div.grid(row=1, column=0, columnspan=5, sticky="ew")

    def set_data(self, ports):
        self.rows_data = ports

        # Remove old data rows (rows >= 2)
        for slave in self.grid_slaves():
            info = slave.grid_info()
            if int(info.get("row", 0)) >= 2:
                slave.destroy()

        self.row_cells = []

        if not ports:
            empty_lbl = tk.Label(
                self, text="No serial devices detected. Connect a USB device and click 'DETECT USB DEVICES'.",
                font=("Consolas", 9), fg=TEXT_MUTED, bg=BG_TABLE, pady=24
            )
            empty_lbl.grid(row=2, column=0, columnspan=5, sticky="ew")
            return

        for idx, p in enumerate(ports):
            r_num = 2 + idx
            bg = BG_ROW_EVEN if idx % 2 == 0 else BG_ROW_ODD

            vals = [
                (0, p.port, TEXT_WHITE),
                (1, p.vid_str, TEXT_WHITE),
                (2, p.manufacturer, TEXT_WHITE),
                (3, p.product, TEXT_WHITE),
                (4, p.status, NEON_CYAN if p.status == "flash-candidate" else TEXT_MUTED)
            ]

            cells = []
            for col_idx, text, col in vals:
                lbl = tk.Label(
                    self, text=text, font=("Consolas", 9),
                    fg=col, bg=bg, anchor=tk.W, padx=12, pady=7,
                    cursor="hand2"
                )
                lbl.grid(row=r_num, column=col_idx, sticky="nsew")
                cells.append(lbl)

                # Event bindings
                lbl.bind("<Button-1>", lambda e, i=idx: self._select_row(i))
                lbl.bind("<Enter>", lambda e, i=idx: self._on_hover(i, True))
                lbl.bind("<Leave>", lambda e, i=idx: self._on_hover(i, False))

            self.row_cells.append(cells)

        # Auto-select the first candidate or first row
        if self.selected_idx < 0 or self.selected_idx >= len(ports):
            best_idx = 0
            for i, p in enumerate(ports):
                if p.status == "flash-candidate":
                    best_idx = i
                    break
            self._select_row(best_idx, fire_callback=True)
        else:
            self._highlight_selected()

    def _on_hover(self, idx, entering):
        if idx == self.selected_idx or idx >= len(self.row_cells):
            return
        bg = BG_ROW_HOVER if entering else (BG_ROW_EVEN if idx % 2 == 0 else BG_ROW_ODD)
        for l in self.row_cells[idx]:
            l.config(bg=bg)

    def _select_row(self, idx, fire_callback=True):
        self.selected_idx = idx
        self._highlight_selected()
        if fire_callback and 0 <= idx < len(self.rows_data):
            self.on_select_callback(self.rows_data[idx])

    def _highlight_selected(self):
        for i, cells in enumerate(self.row_cells):
            bg = BG_ROW_SEL if (i == self.selected_idx) else (BG_ROW_EVEN if i % 2 == 0 else BG_ROW_ODD)
            for l in cells:
                l.config(bg=bg)


class CleanCyberButton(tk.Canvas):
    """High-tech solid cyan action button matching the USB DEVICE FLASH button."""
    def __init__(self, parent, text, command, width=752, height=44, **kwargs):
        super().__init__(parent, width=width, height=height, bg=BG_MAIN, highlightthickness=0, **kwargs)
        self.text = text
        self.command = command
        self.w = width
        self.h = height
        self.enabled = True
        self.hover = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.draw()

    def set_enabled(self, enabled):
        self.enabled = enabled
        self.draw()

    def set_text(self, text):
        self.text = text
        self.draw()

    def _on_enter(self, event):
        if self.enabled:
            self.hover = True
            self.draw()

    def _on_leave(self, event):
        self.hover = False
        self.draw()

    def _on_click(self, event):
        if self.enabled and self.command:
            self.command()

    def draw(self):
        self.delete("all")
        if not self.enabled:
            bg_col = "#141c2c"
            text_col = "#506078"
            outline_col = "#182338"
        elif self.hover:
            bg_col = "#33f5ff"
            text_col = TEXT_DARK
            outline_col = "#ffffff"
        else:
            bg_col = NEON_CYAN
            text_col = TEXT_DARK
            outline_col = NEON_CYAN

        # Clean rounded block
        r = 5
        self.create_polygon(
            r, 0, self.w - r, 0, self.w, r, self.w, self.h - r,
            self.w - r, self.h, r, self.h, 0, self.h - r, 0, r,
            fill=bg_col, outline=outline_col, width=1
        )
        self.create_text(
            self.w // 2, self.h // 2,
            text=self.text, fill=text_col, font=("Segoe UI", 11, "bold")
        )


class SegmentedProgressBar(tk.Canvas):
    """Sleek segmented progress bar in glowing cyan."""
    def __init__(self, parent, width=752, height=14, **kwargs):
        super().__init__(parent, width=width, height=height, bg="#080c14", highlightthickness=1, highlightbackground=BORDER_DARK, **kwargs)
        self.w = width
        self.h = height
        self.percent = 0
        self.draw()

    def set_percent(self, pct):
        self.percent = max(0, min(100, pct))
        self.draw()

    def draw(self):
        self.delete("all")
        fill_w = int((self.w - 4) * (self.percent / 100.0))
        if fill_w > 0:
            self.create_rectangle(2, 2, 2 + fill_w, self.h - 2, fill=NEON_CYAN, outline="")
            # Segment ticks
            for x in range(16, fill_w, 16):
                self.create_line(2 + x, 2, 2 + x, self.h - 2, fill="#005057", width=1)


class SeederFlasherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SEEDER FLASHER")
        self.geometry("860x780")
        self.minsize(820, 720)
        self.configure(bg=BG_MAIN)

        icon_path = engine.get_resource_path("icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        # State
        self.flashing = False
        self.detected_ports = []
        self.selected_port = None
        self.target_var = tk.StringVar(value="tdisplay-s3")

        self._build_ui()
        self._start_port_scanner()

    def _build_ui(self):
        # Outer Border Container matching the Torii cyber frame aesthetic
        outer = tk.Frame(self, bg=BG_MAIN, highlightthickness=2, highlightbackground=BORDER_CYAN)
        outer.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # 1. Top Header Banner
        self.header = HeaderBanner(outer, width=812, height=54)
        self.header.pack(fill=tk.X, padx=18, pady=(12, 2))

        # 2. Stepper Bar
        self.stepper = StepperBar(outer, width=812, height=44)
        self.stepper.pack(fill=tk.X, padx=18, pady=(4, 10))

        # 3. Sub-Navigation Tabs Row
        tab_row = tk.Frame(outer, bg=BG_MAIN)
        tab_row.pack(fill=tk.X, padx=18, pady=(0, 10))

        # Inactive LAN Miner Scan Tab
        lan_btn = tk.Label(
            tab_row, text="LAN MINER SCAN", font=("Segoe UI", 9, "bold"),
            fg=TEXT_MUTED, bg="#0c121e", padx=16, pady=8, bd=1, relief=tk.SOLID
        )
        lan_btn.pack(side=tk.LEFT, padx=(0, 8))

        # Active USB Device Flash Tab (Solid Cyan)
        usb_tab = tk.Label(
            tab_row, text="USB DEVICE FLASH", font=("Segoe UI", 9, "bold"),
            fg=TEXT_DARK, bg=NEON_CYAN, padx=16, pady=8, bd=1, relief=tk.SOLID
        )
        usb_tab.pack(side=tk.LEFT)

        # 4. Action Button Row: DETECT USB DEVICES
        action_row = tk.Frame(outer, bg=BG_MAIN)
        action_row.pack(fill=tk.X, padx=18, pady=(4, 6))

        self.detect_btn = tk.Button(
            action_row, text="DETECT USB DEVICES", font=("Segoe UI", 9, "bold"),
            fg=NEON_CYAN, bg="#101726", activebackground=NEON_CYAN, activeforeground=TEXT_DARK,
            bd=1, relief=tk.SOLID, padx=14, pady=6, cursor="hand2", command=self._manual_scan
        )
        self.detect_btn.pack(side=tk.LEFT)

        # 5. Explanatory Subtext
        subtext = (
            '"flash-candidate" devices match the ESP32-S3\'s generic default USB identity (LilyGO / AxeOS). '
            '"raw-installed" devices are running custom firmware. Click any device to flash or re-flash.'
        )
        sub_lbl = tk.Label(
            outer, text=subtext, font=("Consolas", 8),
            fg=TEXT_MUTED, bg=BG_MAIN, justify=tk.LEFT, anchor=tk.W, wraplength=800
        )
        sub_lbl.pack(fill=tk.X, padx=18, pady=(2, 8))

        # 6. Interactive Device Table
        self.table = CyberTable(outer, on_select_callback=self._on_table_row_selected)
        self.table.pack(fill=tk.X, padx=18, pady=(0, 10))

        # 7. Hardware Profile Selection
        profile_frame = tk.Frame(outer, bg=BG_PANEL, bd=1, relief=tk.SOLID, highlightthickness=1, highlightbackground=BORDER_DARK)
        profile_frame.pack(fill=tk.X, padx=18, pady=(0, 8))

        p_pad = tk.Frame(profile_frame, bg=BG_PANEL)
        p_pad.pack(fill=tk.X, padx=14, pady=8)

        prof_lbl = tk.Label(
            p_pad, text="FIRMWARE TARGET:", font=("Consolas", 9, "bold"),
            fg=NEON_CYAN, bg=BG_PANEL
        )
        prof_lbl.pack(side=tk.LEFT, padx=(0, 14))

        self.rb_s3 = tk.Radiobutton(
            p_pad, text="LilyGO T-Display-S3 (ESP32-S3 · 16MB Flash · 320x170)",
            variable=self.target_var, value="tdisplay-s3",
            font=("Segoe UI", 9), fg=TEXT_WHITE, bg=BG_PANEL, selectcolor="#080d16",
            activebackground=BG_PANEL, activeforeground=NEON_CYAN
        )
        self.rb_s3.pack(side=tk.LEFT, padx=(0, 16))

        self.rb_t = tk.Radiobutton(
            p_pad, text="LilyGO TTGO T-Display (ESP32 · 4MB Flash · 240x135)",
            variable=self.target_var, value="tdisplay",
            font=("Segoe UI", 9), fg=TEXT_WHITE, bg=BG_PANEL, selectcolor="#080d16",
            activebackground=BG_PANEL, activeforeground=NEON_CYAN
        )
        self.rb_t.pack(side=tk.LEFT)

        # 8. Flash Action Button
        action_box = tk.Frame(outer, bg=BG_MAIN)
        action_box.pack(fill=tk.X, padx=18, pady=(4, 6))

        self.flash_btn = CleanCyberButton(
            action_box, text="⚡ FLASH SELECTED DEVICE",
            command=self._start_flash, width=812, height=44
        )
        self.flash_btn.pack(fill=tk.X)

        # 9. Progress Bar & Status Line
        prog_box = tk.Frame(outer, bg=BG_MAIN)
        prog_box.pack(fill=tk.X, padx=18, pady=(2, 6))

        self.prog_bar = SegmentedProgressBar(prog_box, width=812, height=12)
        self.prog_bar.pack(fill=tk.X)

        self.status_lbl = tk.Label(
            prog_box, text="READY: Select a device row above to begin flashing.",
            font=("Consolas", 9), fg=TEXT_MUTED, bg=BG_MAIN
        )
        self.status_lbl.pack(anchor=tk.W, pady=(4, 0))

        # 10. Terminal Console Card
        console_card = tk.Frame(outer, bg=BG_PANEL, bd=1, relief=tk.SOLID, highlightthickness=1, highlightbackground=BORDER_DARK)
        console_card.pack(fill=tk.BOTH, expand=True, padx=18, pady=(4, 12))

        c_pad = tk.Frame(console_card, bg=BG_PANEL)
        c_pad.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        c_head = tk.Frame(c_pad, bg=BG_PANEL)
        c_head.pack(fill=tk.X, pady=(0, 4))

        c_title = tk.Label(c_head, text="TERMINAL OUTPUT", font=("Consolas", 9, "bold"), fg=TEXT_MUTED, bg=BG_PANEL)
        c_title.pack(side=tk.LEFT)

        clear_btn = tk.Button(
            c_head, text="CLEAR", font=("Consolas", 8), bg=BG_PANEL, fg=TEXT_MUTED,
            activebackground=BG_PANEL, activeforeground=TEXT_WHITE, bd=0, cursor="hand2", command=self._clear_log
        )
        clear_btn.pack(side=tk.RIGHT)

        self.log_text = tk.Text(
            c_pad, bg="#05070c", fg="#cbd5e1", font=("Consolas", 9),
            insertbackground=NEON_CYAN, selectbackground="#162947",
            relief=tk.FLAT, wrap=tk.WORD, height=6
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._log("Seeder Flasher initialized. Scanning serial ports...")

    def _log(self, text):
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)

    def _clear_log(self):
        self.log_text.delete("1.0", tk.END)

    def _manual_scan(self):
        self._scan_and_update()

    def _start_port_scanner(self):
        def scan_loop():
            while True:
                if not self.flashing:
                    self.after(0, self._scan_and_update)
                time.sleep(2.0)

        t = threading.Thread(target=scan_loop, daemon=True)
        t.start()

    def _scan_and_update(self):
        if self.flashing:
            return

        ports = engine.scan_ports()
        self.detected_ports = ports
        self.table.set_data(ports)

    def _on_table_row_selected(self, port_info):
        self.selected_port = port_info
        self.target_var.set(port_info.default_target)
        self.stepper.set_step(2)
        self.flash_btn.set_enabled(True)
        self.flash_btn.set_text(f"⚡ FLASH SELECTED DEVICE ({port_info.port})")
        self.status_lbl.config(
            text=f"SELECTED: {port_info.port} [{port_info.product}] -> Ready to flash.",
            fg=NEON_CYAN
        )

    def _start_flash(self):
        if not self.selected_port or self.flashing:
            return

        port = self.selected_port.port
        target = self.target_var.get()

        self.flashing = True
        self.stepper.set_step(3)
        self.flash_btn.set_enabled(False)
        self.flash_btn.set_text(f"⚡ FLASHING FIRMWARE TO {port}...")
        self.detect_btn.config(state=tk.DISABLED)
        self.prog_bar.set_percent(0)

        self._log("\n" + "=" * 60)
        self._log(f"INITIATING FIRMWARE FLASH: TARGET [{target.upper()}] ON {port}")
        self._log("=" * 60)

        def worker():
            def progress_callback(pct, msg):
                self.after(0, lambda: self._on_progress(pct, msg))

            def log_callback(line):
                self.after(0, lambda: self._log(line))

            success, error_msg = engine.flash_firmware(port, target, progress_callback, log_callback)
            self.after(0, lambda: self._on_flash_complete(success, error_msg))

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _on_progress(self, pct, msg):
        self.prog_bar.set_percent(pct)
        self.status_lbl.config(text=f"PROGRESS [{pct}%]: {msg}", fg=NEON_CYAN)

    def _on_flash_complete(self, success, error_msg):
        self.flashing = False
        self.detect_btn.config(state=tk.NORMAL)

        if success:
            self.prog_bar.set_percent(100)
            self.stepper.set_step(4)
            self.flash_btn.set_text("✓ FLASH COMPLETED & VERIFIED")
            self.status_lbl.config(
                text="SUCCESS: Firmware verified. Device rebooted into Seeder cold-storage!",
                fg=GREEN_ACTIVE
            )
            self._log("\n[✓] FLASH SUCCESSFUL: Device rebooted into sovereign Seeder wallet.")
            messagebox.showinfo(
                "Flashing Complete",
                f"Seeder firmware flashed successfully to {self.selected_port.port}!\n\n"
                "The board has rebooted and is now running Seeder."
            )
        else:
            self.flash_btn.set_text("⚠ FLASH FAILED - CLICK TO RETRY")
            self.status_lbl.config(
                text=f"ERROR: Flashing failed: {error_msg}",
                fg="#ff5555"
            )
            self._log(f"\n[!] ERROR: Flashing failed: {error_msg}")
            messagebox.showerror(
                "Flashing Error",
                f"Failed to flash {self.selected_port.port}:\n\n{error_msg}"
            )

        self.after(3000, self._reset_flash_btn)

    def _reset_flash_btn(self):
        if not self.flashing and self.selected_port:
            self.flash_btn.set_enabled(True)
            self.flash_btn.set_text(f"⚡ FLASH SELECTED DEVICE ({self.selected_port.port})")


def main():
    app = SeederFlasherApp()
    app.mainloop()


if __name__ == "__main__":
    main()
