"""
Seeder Flasher - Torii Cyberpunk Tactical UI for LilyGO Hardware
Neo-Tokyo / Cyber-Shrine Aesthetic (鳥居 Torii Gateway)
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

# Palette - Torii Cyber-Shrine Neo-Tokyo Theme
BG_VOID       = "#07080d"   # Deepest obsidian void
BG_CARD       = "#0f121a"   # Shinto obsidian card
BG_INPUT      = "#0a0c12"   # Recessed terminal input
BORDER_DARK   = "#1f2638"   # Subtle structural border
BORDER_GLOW   = "#2c364e"   # Card highlight
TORII_RED     = "#ff2a5f"   # Vibrant neon Torii vermilion / crimson
TORII_RED_DIM = "#80122e"   # Deep vermilion shadow
NEON_CYAN     = "#00f0ff"   # Holographic electric cyan
NEON_CYAN_DIM = "#00626b"   # Dim cyan conduit
CYBER_GOLD    = "#ffb700"   # Sacred cyber amber / gold
MATRIX_GREEN  = "#00ff9d"   # Quantum link verified green
TEXT_WHITE    = "#f0f6fc"   # High-contrast luminous white
TEXT_MUTED    = "#7a8498"   # Secondary telemetry gray
TEXT_CRIMSON  = "#ff5577"   # Warning crimson


class ToriiBanner(tk.Canvas):
    """Luminous Cyber-Shrine Torii Gate Header Banner."""
    def __init__(self, parent, width=700, height=84, **kwargs):
        super().__init__(parent, width=width, height=height, bg=BG_VOID, highlightthickness=0, **kwargs)
        self.w = width
        self.h = height
        self.status_text = "待機 // STANDBY"
        self.status_color = TEXT_MUTED
        self.draw()

    def set_status(self, text, color):
        self.status_text = text
        self.status_color = color
        self.draw()

    def draw(self):
        self.delete("all")
        # 1. Subtle background grid / scanlines
        for y in range(0, self.h, 6):
            self.create_line(0, y, self.w, y, fill="#0b0e16", width=1)

        # 2. Left side: Stylized Vector Torii Gate
        # Dimensions & anchor
        bx = 20
        by = 12

        # Kasagi (Top curved lintel with upturned tips)
        kasagi = [
            bx, by + 12,
            bx + 6, by + 5,
            bx + 40, by + 3,
            bx + 74, by + 5,
            bx + 80, by + 12,
            bx + 76, by + 16,
            bx + 40, by + 12,
            bx + 4, by + 16
        ]
        self.create_polygon(kasagi, fill=TORII_RED, outline="#ff7597", width=1)

        # Shimaki (Secondary lintel directly below Kasagi)
        self.create_polygon(
            bx + 10, by + 16,
            bx + 70, by + 16,
            bx + 68, by + 23,
            bx + 12, by + 23,
            fill=TORII_RED_DIM, outline=TORII_RED, width=1
        )

        # Hashira (Two main pillars)
        # Left pillar
        self.create_polygon(
            bx + 20, by + 21,
            bx + 27, by + 21,
            bx + 30, by + 68,
            bx + 19, by + 68,
            fill=TORII_RED, outline=NEON_CYAN_DIM, width=1
        )
        # Right pillar
        self.create_polygon(
            bx + 53, by + 21,
            bx + 60, by + 21,
            bx + 61, by + 68,
            bx + 50, by + 68,
            fill=TORII_RED, outline=NEON_CYAN_DIM, width=1
        )

        # Nuki (Tie-beam)
        self.create_rectangle(bx + 12, by + 32, bx + 68, by + 38, fill=TORII_RED, outline=NEON_CYAN, width=1)

        # Gakuzuka (Center tablet between lintel and tie-beam)
        self.create_rectangle(bx + 36, by + 22, bx + 44, by + 32, fill=BG_CARD, outline=NEON_CYAN, width=1)
        self.create_text(bx + 40, by + 27, text="門", fill=NEON_CYAN, font=("Segoe UI", 6, "bold"))

        # Portal Core (Center of Torii - glowing quantum diamond)
        diamond = [
            bx + 40, by + 42,
            bx + 47, by + 51,
            bx + 40, by + 60,
            bx + 33, by + 51
        ]
        self.create_polygon(diamond, fill="#00353d", outline=NEON_CYAN, width=1)
        self.create_line(bx + 40, by + 45, bx + 40, by + 57, fill=TEXT_WHITE, width=1)
        self.create_line(bx + 35, by + 51, bx + 45, by + 51, fill=TEXT_WHITE, width=1)

        # Pillar stone bases
        self.create_rectangle(bx + 16, by + 66, bx + 33, by + 72, fill="#1c2233", outline=BORDER_DARK, width=1)
        self.create_rectangle(bx + 47, by + 66, bx + 64, by + 72, fill="#1c2233", outline=BORDER_DARK, width=1)

        # 3. Typography: Title & Cyber-Shrine Subtitle
        tx = bx + 96
        self.create_text(
            tx, by + 18, anchor=tk.W,
            text="SEEDER // 鳥居",
            fill=TEXT_WHITE, font=("Consolas", 20, "bold")
        )
        self.create_text(
            tx + 185, by + 19, anchor=tk.W,
            text="TORII CYBER-GATEWAY",
            fill=TORII_RED, font=("Consolas", 11, "bold")
        )
        self.create_text(
            tx, by + 44, anchor=tk.W,
            text="「 SOVEREIGN COLD-STORAGE HARDWARE INSTALLER · 秘密鍵の聖域 」",
            fill=TEXT_MUTED, font=("Consolas", 9, "bold")
        )
        self.create_text(
            tx, by + 60, anchor=tk.W,
            text="STATUS: QUANTUM CONDUIT READY // 接続待機中",
            fill=NEON_CYAN_DIM, font=("Consolas", 8)
        )

        # 4. Right side: High-Tech Torii Status Badge
        badge_w = 210
        badge_h = 36
        badge_x = self.w - badge_w - 4
        badge_y = by + 14

        # Chamfered badge frame
        r = 6
        self.create_polygon(
            badge_x + r, badge_y,
            badge_x + badge_w - r, badge_y,
            badge_x + badge_w, badge_y + r,
            badge_x + badge_w, badge_y + badge_h - r,
            badge_x + badge_w - r, badge_y + badge_h,
            badge_x + r, badge_y + badge_h,
            badge_x, badge_y + badge_h - r,
            badge_x, badge_y + r,
            fill=BG_CARD, outline=self.status_color, width=1
        )
        # Pulsing beacon LED
        self.create_oval(badge_x + 14, badge_y + 13, badge_x + 24, badge_y + 23, fill=self.status_color, outline="")
        self.create_text(
            badge_x + 112, badge_y + 18,
            text=self.status_text, fill=self.status_color, font=("Consolas", 9, "bold")
        )


class ToriiCyberButton(tk.Canvas):
    """Chamfered Cyberpunk Action Button with Torii Vermilion and Cyan Neon."""
    def __init__(self, parent, text, command, width=692, height=52, **kwargs):
        super().__init__(parent, width=width, height=height, bg=BG_VOID, highlightthickness=0, **kwargs)
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
        c = 10  # 45-degree chamfer cut size

        if not self.enabled:
            bg_col = "#12151f"
            border_col = "#242c3d"
            text_col = "#505a70"
            bracket_col = "#30394d"
        elif self.hover:
            bg_col = "#2a0612"         # Deep glowing vermilion backing
            border_col = TORII_RED
            text_col = TEXT_WHITE
            bracket_col = NEON_CYAN
        else:
            bg_col = "#150810"         # Dark crimson obsidian
            border_col = TORII_RED_DIM
            text_col = TORII_RED
            bracket_col = TORII_RED

        # Chamfered main polygon
        poly = [
            c, 0,
            self.w - c, 0,
            self.w, c,
            self.w, self.h - c,
            self.w - c, self.h,
            c, self.h,
            0, self.h - c,
            0, c
        ]
        self.create_polygon(poly, fill=bg_col, outline=border_col, width=2)

        # High-tech Cyber Brackets on corners
        if self.enabled:
            # Top-left
            self.create_line(0, c + 4, 0, c, c, 0, c + 4, 0, fill=bracket_col, width=2)
            # Top-right
            self.create_line(self.w - (c + 4), 0, self.w - c, 0, self.w, c, self.w, c + 4, fill=bracket_col, width=2)
            # Bottom-right
            self.create_line(self.w, self.h - (c + 4), self.w, self.h - c, self.w - c, self.h, self.w - (c + 4), self.h, fill=bracket_col, width=2)
            # Bottom-left
            self.create_line(c + 4, self.h, c, self.h, 0, self.h - c, 0, self.h - (c + 4), fill=bracket_col, width=2)

            # Center neon energy line across bottom edge
            glow_line_col = NEON_CYAN if self.hover else TORII_RED_DIM
            self.create_line(c + 20, self.h - 3, self.w - (c + 20), self.h - 3, fill=glow_line_col, width=2)

        self.create_text(
            self.w // 2, self.h // 2,
            text=self.text, fill=text_col,
            font=("Consolas", 12, "bold")
        )


class ToriiProgressBar(tk.Canvas):
    """Cyber-Conduit Energy Progress Bar."""
    def __init__(self, parent, width=692, height=16, **kwargs):
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
        # Empty background grid ticks
        for x in range(16, self.w, 16):
            self.create_line(x, 0, x, self.h, fill="#121622", width=1)

        fill_w = int((self.w - 4) * (self.percent / 100.0))
        if fill_w > 0:
            # Dual gradient aesthetic: vermilion fading to electric cyan
            self.create_rectangle(2, 2, 2 + fill_w, self.h - 2, fill=NEON_CYAN, outline="")
            # Conduit tick marks
            for x in range(16, fill_w, 16):
                self.create_line(2 + x, 2, 2 + x, self.h - 2, fill="#004e54", width=1)
            # Leading energy spark
            self.create_line(2 + fill_w - 2, 2, 2 + fill_w - 2, self.h - 2, fill=TEXT_WHITE, width=2)


class SeederFlasherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SEEDER // 鳥居 TORII CYBER-GATEWAY")
        self.geometry("760x720")
        self.minsize(720, 680)
        self.configure(bg=BG_VOID)

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
        # 1. Torii Gate Header Banner
        self.banner = ToriiBanner(self, width=712, height=84)
        self.banner.pack(fill=tk.X, padx=24, pady=(16, 6))

        # Neon Divider Line
        div = tk.Frame(self, height=2, bg=BORDER_DARK)
        div.pack(fill=tk.X, padx=24, pady=(2, 10))

        # 2. Hardware Connection Card
        card = tk.Frame(self, bg=BG_CARD, bd=1, relief=tk.SOLID, highlightthickness=1, highlightbackground=BORDER_DARK)
        card.pack(fill=tk.X, padx=24, pady=6)

        card_pad = tk.Frame(card, bg=BG_CARD)
        card_pad.pack(fill=tk.X, padx=16, pady=12)

        card_title = tk.Label(
            card_pad, text="「 ⛩️ ポート検出 / HARDWARE CONNECTION GATEWAY 」",
            font=("Consolas", 10, "bold"), fg=TORII_RED, bg=BG_CARD
        )
        card_title.pack(anchor=tk.W, pady=(0, 8))

        # Port Selection Row
        port_row = tk.Frame(card_pad, bg=BG_CARD)
        port_row.pack(fill=tk.X, pady=4)

        p_lbl = tk.Label(
            port_row, text="TARGET PORT:",
            font=("Consolas", 9, "bold"), fg=NEON_CYAN, bg=BG_CARD, width=14, anchor=tk.W
        )
        p_lbl.pack(side=tk.LEFT)

        self.port_combo = ttk.Combobox(port_row, state="readonly", font=("Consolas", 10))
        self.port_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.port_combo.bind("<<ComboboxSelected>>", self._on_port_selected)

        self.refresh_btn = tk.Button(
            port_row, text="⟳ RESCAN // 再検出", font=("Consolas", 9, "bold"),
            bg="#1b2233", fg=TEXT_WHITE, activebackground=TORII_RED_DIM, activeforeground=TEXT_WHITE,
            bd=1, relief=tk.FLAT, padx=12, pady=4, cursor="hand2", command=self._manual_scan
        )
        self.refresh_btn.pack(side=tk.RIGHT)

        # Hardware Model Selection Row
        model_row = tk.Frame(card_pad, bg=BG_CARD)
        model_row.pack(fill=tk.X, pady=(10, 4))

        m_lbl = tk.Label(
            model_row, text="DEVICE MODEL:",
            font=("Consolas", 9, "bold"), fg=NEON_CYAN, bg=BG_CARD, width=14, anchor=tk.W
        )
        m_lbl.pack(side=tk.LEFT)

        self.rb_s3 = tk.Radiobutton(
            model_row, text="LilyGO T-Display-S3 (ESP32-S3 · 16MB · 320x170)",
            variable=self.target_var, value="tdisplay-s3",
            font=("Segoe UI", 9), fg=TEXT_WHITE, bg=BG_CARD, selectcolor=BG_INPUT,
            activebackground=BG_CARD, activeforeground=TORII_RED
        )
        self.rb_s3.pack(side=tk.LEFT, padx=(0, 16))

        self.rb_t = tk.Radiobutton(
            model_row, text="LilyGO TTGO T-Display (ESP32 · 4MB · 240x135)",
            variable=self.target_var, value="tdisplay",
            font=("Segoe UI", 9), fg=TEXT_WHITE, bg=BG_CARD, selectcolor=BG_INPUT,
            activebackground=BG_CARD, activeforeground=TORII_RED
        )
        self.rb_t.pack(side=tk.LEFT)

        # 3. Action Button
        action_frame = tk.Frame(self, bg=BG_VOID)
        action_frame.pack(fill=tk.X, padx=24, pady=(10, 8))

        self.flash_btn = ToriiCyberButton(
            action_frame,
            text="⚡ [ FLASH SEEDER FIRMWARE // 書込開始 ] ⚡",
            command=self._start_flash, width=712, height=52
        )
        self.flash_btn.pack(fill=tk.X)

        # 4. Progress Section
        prog_frame = tk.Frame(self, bg=BG_VOID)
        prog_frame.pack(fill=tk.X, padx=24, pady=(4, 8))

        self.prog_bar = ToriiProgressBar(prog_frame, width=712, height=16)
        self.prog_bar.pack(fill=tk.X)

        self.stage_lbl = tk.Label(
            prog_frame,
            text="STATUS: READY // Connect LilyGO hardware and initiate flash sequence",
            font=("Consolas", 9), fg=TEXT_MUTED, bg=BG_VOID
        )
        self.stage_lbl.pack(anchor=tk.W, pady=(5, 0))

        # 5. Terminal Console Card
        console_card = tk.Frame(self, bg=BG_CARD, bd=1, relief=tk.SOLID, highlightthickness=1, highlightbackground=BORDER_DARK)
        console_card.pack(fill=tk.BOTH, expand=True, padx=24, pady=(4, 18))

        c_pad = tk.Frame(console_card, bg=BG_CARD)
        c_pad.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        c_header = tk.Frame(c_pad, bg=BG_CARD)
        c_header.pack(fill=tk.X, pady=(0, 6))

        c_title = tk.Label(
            c_header, text="「 📡 テレメトリログ / TELEMETRY TERMINAL 」",
            font=("Consolas", 9, "bold"), fg=TORII_RED, bg=BG_CARD
        )
        c_title.pack(side=tk.LEFT)

        clear_btn = tk.Button(
            c_header, text="CLEAR // 消去", font=("Consolas", 8), bg=BG_CARD, fg=TEXT_MUTED,
            activebackground=BG_CARD, activeforeground=TEXT_WHITE, bd=0, cursor="hand2", command=self._clear_log
        )
        clear_btn.pack(side=tk.RIGHT)

        self.log_text = tk.Text(
            c_pad, bg=BG_INPUT, fg="#c9d1d9", font=("Consolas", 9),
            insertbackground=NEON_CYAN, selectbackground="#38101d",
            relief=tk.FLAT, wrap=tk.WORD, height=10
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._log("⛩️  ============================================================  ⛩️")
        self._log("    SEEDER // 鳥居 TORII CYBER-GATEWAY v2.0")
        self._log("    SOVEREIGN BITCOIN COLD-STORAGE HARDWARE CONDUIT")
        self._log("⛩️  ============================================================  ⛩️")
        self._log("[*] Quantum bus initialized. Scanning USB-Serial / JTAG matrix...")

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
                time.sleep(1.5)

        t = threading.Thread(target=scan_loop, daemon=True)
        t.start()

    def _scan_and_update(self):
        if self.flashing:
            return

        ports = engine.scan_ports()
        self.detected_ports = ports

        if not ports:
            self.port_combo['values'] = ["No COM devices detected"]
            self.port_combo.current(0)
            self.selected_port = None
            self.flash_btn.set_enabled(False)
            self.banner.set_status("待機 // NO DEVICE", TEXT_MUTED)
            self.stage_lbl.config(
                text="STATUS: NO HARDWARE DETECTED // Plug in LilyGO USB cable",
                fg=TEXT_MUTED
            )
            return

        display_values = [p.display_name for p in ports]
        self.port_combo['values'] = display_values

        # Auto-select best known LilyGO port
        selected_idx = 0
        for i, p in enumerate(ports):
            if p.is_known:
                selected_idx = i
                break

        current_text = self.port_combo.get()
        if current_text not in display_values:
            self.port_combo.current(selected_idx)
            self._on_port_selected()
        else:
            idx = display_values.index(current_text)
            self.selected_port = ports[idx]
            self._update_selection_state()

    def _on_port_selected(self, event=None):
        idx = self.port_combo.current()
        if idx >= 0 and idx < len(self.detected_ports):
            p = self.detected_ports[idx]
            self.selected_port = p
            self.target_var.set(p.default_target)
            self._update_selection_state()

    def _update_selection_state(self):
        if self.selected_port:
            p = self.selected_port
            if p.is_known:
                self.banner.set_status(f"接続 // {p.port} READY", MATRIX_GREEN)
                self.stage_lbl.config(
                    text=f"HARDWARE LINKED: {p.display_name} -> Ready to flash",
                    fg=MATRIX_GREEN
                )
            else:
                self.banner.set_status(f"接続 // {p.port}", CYBER_GOLD)
                self.stage_lbl.config(
                    text=f"GENERIC SERIAL PORT LINKED: {p.display_name}",
                    fg=CYBER_GOLD
                )
            self.flash_btn.set_enabled(True)

    def _start_flash(self):
        if not self.selected_port or self.flashing:
            return

        port = self.selected_port.port
        target = self.target_var.get()

        self.flashing = True
        self.flash_btn.set_enabled(False)
        self.flash_btn.set_text("⚡ [ FLASHING FIRMWARE // 書込処理中... ] ⚡")
        self.banner.set_status("書込中 // FLASHING", TORII_RED)
        self.refresh_btn.config(state=tk.DISABLED)
        self.port_combo.config(state=tk.DISABLED)
        self.prog_bar.set_percent(0)

        self._log("\n" + "=" * 60)
        self._log(f"⛩️ INITIATING TORII FLASH CONDUIT FOR [{target.upper()}] ON {port}")
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
        self.stage_lbl.config(text=f"STATUS [{pct}%]: {msg}", fg=NEON_CYAN)

    def _on_flash_complete(self, success, error_msg):
        self.flashing = False
        self.refresh_btn.config(state=tk.NORMAL)
        self.port_combo.config(state="readonly")

        if success:
            self.prog_bar.set_percent(100)
            self.banner.set_status("完了 // SUCCESS", MATRIX_GREEN)
            self.flash_btn.set_text("✓ [ FLASH VERIFIED // 書込完了 ] ✓")
            self.stage_lbl.config(
                text="FLASH COMPLETE: Device rebooted into sovereign Seeder cold storage!",
                fg=MATRIX_GREEN
            )
            self._log("\n⛩️ [✓] CONDUIT DISENGAGED: HARDWARE IS RUNNING SEEDER FIRMWARE!")
            messagebox.showinfo(
                "Torii Conduit Complete // 書込完了",
                "Firmware flashed and verified successfully!\n\n"
                "Your LilyGO device has reset and is now operating as a sovereign Seeder cold-storage wallet."
            )
        else:
            self.banner.set_status("障害 // FAILED", TORII_RED)
            self.flash_btn.set_text("⚠ [ FLASH FAILED // 再試行 ] ⚠")
            self.stage_lbl.config(
                text=f"FLASH FAILED: {error_msg}",
                fg=TEXT_CRIMSON
            )
            self._log(f"\n⛩️ [!] ERROR: Flashing failed: {error_msg}")
            messagebox.showerror(
                "Torii Flashing Error // エラー",
                f"Flashing encountered an error:\n\n{error_msg}\n\n"
                "Check USB cable connection or try holding the BOOT button while plugging in."
            )

        self.after(3000, self._reset_flash_btn)

    def _reset_flash_btn(self):
        if not self.flashing:
            self.flash_btn.set_text("⚡ [ FLASH SEEDER FIRMWARE // 書込開始 ] ⚡")
            self._update_selection_state()


def main():
    app = SeederFlasherApp()
    app.mainloop()


if __name__ == "__main__":
    main()
