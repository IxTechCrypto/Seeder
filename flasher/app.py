"""
Seeder Flasher - Cyberpunk Tactical UI for LilyGO Hardware
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

# Palette
BG_DARK      = "#0a0c10"
BG_CARD      = "#12161f"
BG_INPUT     = "#080a0e"
BORDER_DARK  = "#212836"
NEON_CYAN    = "#00f0ff"
NEON_CYAN_DIM= "#007a82"
AMBER_ORANGE = "#ff9900"
TEXT_WHITE   = "#f0f6fc"
TEXT_MUTED   = "#7d8590"
TEXT_GREEN   = "#39d353"
TEXT_RED     = "#ff5555"

class CyberpunkButton(tk.Canvas):
    """Custom styled glowing button."""
    def __init__(self, parent, text, command, width=320, height=48, **kwargs):
        super().__init__(parent, width=width, height=height, bg=BG_CARD, highlightthickness=0, **kwargs)
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
            bg_col = "#1a1f29"
            border_col = "#2a3240"
            text_col = "#505868"
        elif self.hover:
            bg_col = "#004d54"
            border_col = NEON_CYAN
            text_col = TEXT_WHITE
        else:
            bg_col = "#00282c"
            border_col = NEON_CYAN_DIM
            text_col = NEON_CYAN

        # Draw outer rounded chamfered button
        r = 6
        self.create_polygon(
            r, 0, self.w - r, 0, self.w, r, self.w, self.h - r,
            self.w - r, self.h, r, self.h, 0, self.h - r, 0, r,
            fill=bg_col, outline=border_col, width=2
        )

        # Corner accents if active
        if self.enabled and self.hover:
            self.create_line(0, r+2, r+2, 0, fill=NEON_CYAN, width=2)
            self.create_line(self.w-(r+2), 0, self.w, r+2, fill=NEON_CYAN, width=2)
            self.create_line(self.w, self.h-(r+2), self.w-(r+2), self.h, fill=NEON_CYAN, width=2)
            self.create_line(r+2, self.h, 0, self.h-(r+2), fill=NEON_CYAN, width=2)

        self.create_text(self.w // 2, self.h // 2, text=self.text, fill=text_col, font=("Consolas", 12, "bold"))


class CyberProgressBar(tk.Canvas):
    """Sleek segmented progress bar with neon cyan fill."""
    def __init__(self, parent, width=640, height=20, **kwargs):
        super().__init__(parent, width=width, height=height, bg=BG_INPUT, highlightthickness=1, highlightbackground=BORDER_DARK, **kwargs)
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
                self.create_line(2 + x, 2, 2 + x, self.h - 2, fill="#006670", width=1)


class SeederFlasherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SEEDER // LilyGO Hardware Flasher")
        self.geometry("740x680")
        self.minsize(700, 640)
        self.configure(bg=BG_DARK)

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
        # 1. Header Banner
        header = tk.Frame(self, bg=BG_DARK)
        header.pack(fill=tk.X, padx=24, pady=(20, 10))

        title_frame = tk.Frame(header, bg=BG_DARK)
        title_frame.pack(side=tk.LEFT)

        title_lbl = tk.Label(title_frame, text="⚡ SEEDER // FLASHER", font=("Consolas", 20, "bold"), fg=AMBER_ORANGE, bg=BG_DARK)
        title_lbl.pack(anchor=tk.W)

        sub_lbl = tk.Label(title_frame, text="SOVEREIGN BITCOIN SEED GENERATOR · HARDWARE INSTALLER", font=("Segoe UI", 9, "bold"), fg=TEXT_MUTED, bg=BG_DARK)
        sub_lbl.pack(anchor=tk.W, pady=(2, 0))

        # Status Badge (Top Right)
        self.badge_canvas = tk.Canvas(header, width=190, height=36, bg=BG_DARK, highlightthickness=0)
        self.badge_canvas.pack(side=tk.RIGHT, pady=4)
        self._update_badge("SEARCHING...", TEXT_MUTED)

        # Divider
        div = tk.Frame(self, height=1, bg=BORDER_DARK)
        div.pack(fill=tk.X, padx=24, pady=8)

        # 2. Hardware Detection Card
        card = tk.Frame(self, bg=BG_CARD, bd=1, relief=tk.SOLID, highlightthickness=1, highlightbackground=BORDER_DARK)
        card.pack(fill=tk.X, padx=24, pady=10)

        card_pad = tk.Frame(card, bg=BG_CARD)
        card_pad.pack(fill=tk.X, padx=16, pady=14)

        card_title = tk.Label(card_pad, text="HARDWARE CONNECTION", font=("Consolas", 10, "bold"), fg=NEON_CYAN, bg=BG_CARD)
        card_title.pack(anchor=tk.W, pady=(0, 8))

        # Port Selection Row
        port_row = tk.Frame(card_pad, bg=BG_CARD)
        port_row.pack(fill=tk.X, pady=4)

        p_lbl = tk.Label(port_row, text="TARGET PORT:", font=("Segoe UI", 10, "bold"), fg=TEXT_WHITE, bg=BG_CARD, width=14, anchor=tk.W)
        p_lbl.pack(side=tk.LEFT)

        self.port_combo = ttk.Combobox(port_row, state="readonly", font=("Consolas", 10))
        self.port_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.port_combo.bind("<<ComboboxSelected>>", self._on_port_selected)

        self.refresh_btn = tk.Button(
            port_row, text="⟳ RESCAN", font=("Segoe UI", 9, "bold"),
            bg="#1c2330", fg=TEXT_WHITE, activebackground=NEON_CYAN_DIM, activeforeground=TEXT_WHITE,
            bd=0, padx=10, pady=4, cursor="hand2", command=self._manual_scan
        )
        self.refresh_btn.pack(side=tk.RIGHT)

        # Hardware Model Selection Row
        model_row = tk.Frame(card_pad, bg=BG_CARD)
        model_row.pack(fill=tk.X, pady=(10, 4))

        m_lbl = tk.Label(model_row, text="DEVICE MODEL:", font=("Segoe UI", 10, "bold"), fg=TEXT_WHITE, bg=BG_CARD, width=14, anchor=tk.W)
        m_lbl.pack(side=tk.LEFT)

        self.rb_s3 = tk.Radiobutton(
            model_row, text="LilyGO T-Display-S3 (ESP32-S3 · 320x170)",
            variable=self.target_var, value="tdisplay-s3",
            font=("Segoe UI", 9), fg=TEXT_WHITE, bg=BG_CARD, selectcolor=BG_INPUT,
            activebackground=BG_CARD, activeforeground=NEON_CYAN
        )
        self.rb_s3.pack(side=tk.LEFT, padx=(0, 14))

        self.rb_t = tk.Radiobutton(
            model_row, text="LilyGO TTGO T-Display (ESP32 · 240x135)",
            variable=self.target_var, value="tdisplay",
            font=("Segoe UI", 9), fg=TEXT_WHITE, bg=BG_CARD, selectcolor=BG_INPUT,
            activebackground=BG_CARD, activeforeground=NEON_CYAN
        )
        self.rb_t.pack(side=tk.LEFT)

        # 3. Action Button
        action_frame = tk.Frame(self, bg=BG_DARK)
        action_frame.pack(fill=tk.X, padx=24, pady=(10, 8))

        self.flash_btn = CyberpunkButton(action_frame, text="⚡ FLASH SEEDER FIRMWARE", command=self._start_flash, width=692, height=48)
        self.flash_btn.pack(fill=tk.X)

        # 4. Progress Section
        prog_frame = tk.Frame(self, bg=BG_DARK)
        prog_frame.pack(fill=tk.X, padx=24, pady=(6, 8))

        self.prog_bar = CyberProgressBar(prog_frame, width=692, height=14)
        self.prog_bar.pack(fill=tk.X)

        self.stage_lbl = tk.Label(prog_frame, text="READY: Plug in device and click Flash", font=("Consolas", 9), fg=TEXT_MUTED, bg=BG_DARK)
        self.stage_lbl.pack(anchor=tk.W, pady=(4, 0))

        # 5. Terminal Console Card
        console_card = tk.Frame(self, bg=BG_CARD, bd=1, relief=tk.SOLID, highlightthickness=1, highlightbackground=BORDER_DARK)
        console_card.pack(fill=tk.BOTH, expand=True, padx=24, pady=(4, 20))

        c_pad = tk.Frame(console_card, bg=BG_CARD)
        c_pad.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        c_header = tk.Frame(c_pad, bg=BG_CARD)
        c_header.pack(fill=tk.X, pady=(0, 6))

        c_title = tk.Label(c_header, text="TERMINAL LOG", font=("Consolas", 9, "bold"), fg=TEXT_MUTED, bg=BG_CARD)
        c_title.pack(side=tk.LEFT)

        clear_btn = tk.Button(
            c_header, text="CLEAR", font=("Segoe UI", 8), bg=BG_CARD, fg=TEXT_MUTED,
            activebackground=BG_CARD, activeforeground=TEXT_WHITE, bd=0, cursor="hand2", command=self._clear_log
        )
        clear_btn.pack(side=tk.RIGHT)

        self.log_text = tk.Text(
            c_pad, bg=BG_INPUT, fg="#c9d1d9", font=("Consolas", 9),
            insertbackground=NEON_CYAN, selectbackground="#00505c",
            relief=tk.FLAT, wrap=tk.WORD, height=10
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._log("=== SEEDER FLASHER INITIALIZED ===")
        self._log("System ready. Connect LilyGO device via USB to proceed.")

    def _update_badge(self, text, color):
        self.badge_canvas.delete("all")
        # Draw background pill
        w, h = 180, 32
        self.badge_canvas.create_rectangle(0, 0, w, h, fill=BG_CARD, outline=BORDER_DARK, width=1)
        # Dot
        self.badge_canvas.create_oval(14, 11, 24, 21, fill=color, outline="")
        self.badge_canvas.create_text(98, 16, text=text, fill=color, font=("Consolas", 9, "bold"))

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
                time.sleep(1.8)

        t = threading.Thread(target=scan_loop, daemon=True)
        t.start()

    def _scan_and_update(self):
        ports = engine.scan_ports()
        self.detected_ports = ports

        port_strings = [p.display_name for p in ports]
        current = self.port_combo.get()

        self.port_combo["values"] = port_strings

        if not ports:
            self.port_combo.set("No devices found (plug in LilyGO)")
            self._update_badge("NO HARDWARE", TEXT_RED)
            self.flash_btn.set_enabled(False)
            self.selected_port = None
        else:
            # If current selection is still in list, keep it; otherwise pick top
            match = next((p for p in ports if p.display_name == current), None)
            if not match:
                match = ports[0]
                self.port_combo.set(match.display_name)
                self.target_var.set(match.default_target)

            self.selected_port = match
            badge_text = "DEVICE READY" if match.is_known else "SERIAL DETECTED"
            badge_color = NEON_CYAN if match.is_known else AMBER_ORANGE
            self._update_badge(badge_text, badge_color)
            if not self.flashing:
                self.flash_btn.set_enabled(True)

    def _on_port_selected(self, event):
        idx = self.port_combo.current()
        if 0 <= idx < len(self.detected_ports):
            self.selected_port = self.detected_ports[idx]
            self.target_var.set(self.selected_port.default_target)

    def _start_flash(self):
        if not self.selected_port:
            messagebox.showwarning("No Port Selected", "Please select a connected COM port first.")
            return

        port = self.selected_port.port
        target = self.target_var.get()

        self.flashing = True
        self.flash_btn.set_enabled(False)
        self.refresh_btn.config(state=tk.DISABLED)
        self.port_combo.config(state=tk.DISABLED)
        self.prog_bar.set_percent(0)
        self._update_badge("FLASHING...", AMBER_ORANGE)

        def worker():
            def progress_callback(pct, text):
                self.after(0, lambda: self._on_progress(pct, text))

            def log_callback(msg):
                self.after(0, lambda: self._log(msg))

            success, err = engine.flash_firmware(port, target, progress_callback, log_callback)

            def done():
                self.flashing = False
                self.refresh_btn.config(state=tk.NORMAL)
                self.port_combo.config(state="readonly")
                self.flash_btn.set_enabled(True)
                if success:
                    self._update_badge("FLASH SUCCESS", TEXT_GREEN)
                    messagebox.showinfo("Success", "Seeder firmware has been successfully flashed!\nYour LilyGO is rebooting into Seeder now.")
                else:
                    self._update_badge("FLASH FAILED", TEXT_RED)
                    messagebox.showerror("Flashing Error", f"Flashing encountered an error:\n\n{err}")

            self.after(0, done)

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _on_progress(self, pct, text):
        self.prog_bar.set_percent(pct)
        self.stage_lbl.config(text=text, fg=NEON_CYAN if pct < 100 else TEXT_GREEN)


if __name__ == "__main__":
    app = SeederFlasherApp()
    app.mainloop()
