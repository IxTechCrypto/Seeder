"""
Seeder Flasher - TRON: Legacy Inspired Hardware Installer
The Digital Grid / Identity Disc Interface
"""

import sys
import os
import io
import math
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

# Palette - TRON: Legacy Grid Theme
BG_VOID       = "#020408"   # Deepest obsidian void
BG_PANEL      = "#050a14"   # Dark glass panel
BG_INPUT      = "#03060c"   # Terminal and input recesses
GRID_LINE     = "#081b2e"   # Subtle digital grid line
BORDER_CYAN   = "#00f3ff"   # Luminescent ice blue / cyan
BORDER_DIM    = "#005566"   # Dim cyan circuit trace
NEON_CYAN     = "#00f3ff"   # Primary TRON cyan
NEON_WHITE    = "#ffffff"   # Pure specular core
NEON_ORANGE   = "#ff7700"   # Secondary program orange
TEXT_CYAN     = "#00f3ff"   # High-visibility cyan readout
TEXT_WHITE    = "#f0f8ff"   # Ice white text
TEXT_MUTED    = "#5a7896"   # Telemetry blue-gray
LED_GREEN     = "#00ff9d"   # Link active green
LED_AMBER     = "#ffaa00"   # Warning state


class TronButton(tk.Canvas):
    """Sleek luminescent TRON chamfered pill button."""
    def __init__(self, parent, text, command, width=170, height=38, is_primary=True, **kwargs):
        super().__init__(parent, width=width, height=height, bg=BG_VOID, highlightthickness=0, **kwargs)
        self.text = text
        self.command = command
        self.w = width
        self.h = height
        self.is_primary = is_primary
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
        c = 6  # chamfer corner cut

        if not self.enabled:
            bg_col = "#040810"
            border_col = "#0c1828"
            text_col = "#2a425a"
        elif self.is_primary:
            if self.hover:
                bg_col = "#00404d"
                border_col = NEON_WHITE
                text_col = NEON_WHITE
            else:
                bg_col = "#001e26"
                border_col = NEON_CYAN
                text_col = NEON_CYAN
        else:
            if self.hover:
                bg_col = "#091728"
                border_col = NEON_CYAN
                text_col = NEON_CYAN
            else:
                bg_col = "#050d18"
                border_col = BORDER_DIM
                text_col = TEXT_MUTED

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
        self.create_polygon(poly, fill=bg_col, outline=border_col, width=1)

        # Subtle glowing corner ticks
        if self.enabled and (self.hover or self.is_primary):
            self.create_line(0, c, c, 0, fill=NEON_WHITE if self.hover else NEON_CYAN, width=2)
            self.create_line(self.w - c, 0, self.w, c, fill=NEON_WHITE if self.hover else NEON_CYAN, width=2)
            self.create_line(self.w, self.h - c, self.w - c, self.h, fill=NEON_WHITE if self.hover else NEON_CYAN, width=2)
            self.create_line(c, self.h, 0, self.h - c, fill=NEON_WHITE if self.hover else NEON_CYAN, width=2)

        self.create_text(
            self.w // 2, self.h // 2,
            text=self.text, fill=text_col, font=("Consolas", 10, "bold")
        )


class IdentityDisc(tk.Canvas):
    """The iconic TRON Identity Disc concentric progress ring."""
    def __init__(self, parent, width=380, height=360, on_click=None, **kwargs):
        super().__init__(parent, width=width, height=height, bg=BG_VOID, highlightthickness=0, **kwargs)
        self.w = width
        self.h = height
        self.on_click = on_click
        self.percent = 0
        self.status_text = "READY TO FLASH"
        self.sub_text = "CLICK DISC TO INITIATE"
        self.is_flashing = False
        self.hover = False
        self.angle_offset = 0

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click_event)
        self.draw()

    def set_progress(self, pct, status="FLASHING FIRMWARE...", sub="TRANSFERRING DATA"):
        self.percent = max(0, min(100, pct))
        self.status_text = status
        self.sub_text = sub
        self.is_flashing = (0 < pct < 100)
        self.draw()

    def set_state_text(self, status, sub):
        self.status_text = status
        self.sub_text = sub
        self.draw()

    def _on_enter(self, event):
        self.hover = True
        self.draw()

    def _on_leave(self, event):
        self.hover = False
        self.draw()

    def _on_click_event(self, event):
        if self.on_click:
            self.on_click()

    def draw(self):
        self.delete("all")
        cx = self.w // 2
        cy = self.h // 2

        # 1. Horizontal circuit breakout lines
        self.create_line(0, cy, cx - 145, cy, fill=BORDER_DIM, width=1)
        self.create_line(cx + 145, cy, self.w, cy, fill=BORDER_DIM, width=1)
        # Vertical alignment nodes
        self.create_line(cx - 145, cy - 14, cx - 145, cy + 14, fill=BORDER_DIM, width=1)
        self.create_line(cx + 145, cy - 14, cx + 145, cy + 14, fill=BORDER_DIM, width=1)

        # 2. Outer decorative track ring
        r_outer = 135
        self.create_oval(cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer, outline="#051726", width=1)

        # Segmented perimeter tick marks
        for a in range(0, 360, 15):
            rad = math.radians(a)
            x1 = cx + (r_outer - 4) * math.cos(rad)
            y1 = cy + (r_outer - 4) * math.sin(rad)
            x2 = cx + (r_outer + 4) * math.cos(rad)
            y2 = cy + (r_outer + 4) * math.sin(rad)
            col = "#004455" if a % 45 == 0 else "#082030"
            self.create_line(x1, y1, x2, y2, fill=col, width=1)

        # 3. Secondary concentric track
        r_mid = 115
        self.create_oval(cx - r_mid, cy - r_mid, cx + r_mid, cy + r_mid, outline="#08283a", width=2)

        # 4. Primary Glowing Identity Disc Arc
        r_track = 100
        # Background track
        self.create_oval(cx - r_track, cy - r_track, cx + r_track, cy + r_track, outline="#061f2e", width=7)

        # Dynamic glowing progress arc
        if self.percent > 0:
            sweep = - (self.percent / 100.0) * 360.0
            # Outer cyan glow
            self.create_arc(
                cx - r_track, cy - r_track, cx + r_track, cy + r_track,
                start=90, extent=sweep, style=tk.ARC, outline=NEON_CYAN, width=7
            )
            # Inner white specular core line
            self.create_arc(
                cx - r_track, cy - r_track, cx + r_track, cy + r_track,
                start=90, extent=sweep, style=tk.ARC, outline=NEON_WHITE, width=2
            )
            # Leading spark point
            lead_rad = math.radians(90 - (self.percent / 100.0) * 360.0)
            lx = cx + r_track * math.cos(lead_rad)
            ly = cy - r_track * math.sin(lead_rad)
            self.create_oval(lx - 4, ly - 4, lx + 4, ly + 4, fill=NEON_WHITE, outline=NEON_CYAN, width=2)
        elif self.hover:
            # Subtle hover ring glow when ready
            self.create_oval(cx - r_track, cy - r_track, cx + r_track, cy + r_track, outline=BORDER_DIM, width=4)

        # 5. Inner Core Disc
        r_core = 78
        core_bg = "#001c24" if self.hover else "#030c17"
        self.create_oval(cx - r_core, cy - r_core, cx + r_core, cy + r_core, fill=core_bg, outline=BORDER_DIM, width=2)

        # 6. Center Telemetry Typography
        if self.percent > 0:
            pct_str = f"{int(self.percent)}%"
        else:
            pct_str = "READY"

        self.create_text(
            cx, cy - 14,
            text=pct_str, fill=NEON_WHITE if self.percent == 100 else NEON_CYAN,
            font=("Segoe UI", 28, "bold")
        )
        self.create_text(
            cx, cy + 22,
            text=self.status_text, fill=TEXT_CYAN,
            font=("Consolas", 8, "bold")
        )
        self.create_text(
            cx, cy + 36,
            text=self.sub_text, fill=TEXT_MUTED,
            font=("Consolas", 7)
        )


class HardwareSchematic(tk.Canvas):
    """Glowing vector schematic of the LilyGO hardware and pinout."""
    def __init__(self, parent, width=310, height=130, **kwargs):
        super().__init__(parent, width=width, height=height, bg=BG_PANEL, highlightthickness=0, **kwargs)
        self.w = width
        self.h = height
        self.draw()

    def draw(self):
        self.delete("all")
        # Board main rectangular outline
        bx, by, bw, bh = 20, 16, 120, 84
        self.create_rectangle(bx, by, bx + bw, by + bh, outline=NEON_CYAN, width=2, fill="#040e1a")

        # USB-C Port receptacle (Left edge)
        self.create_rectangle(bx - 8, by + 28, bx, by + 56, outline=NEON_CYAN, width=2, fill="#03070f")
        self.create_line(bx - 14, by + 42, bx - 8, by + 42, fill=BORDER_DIM, width=2)

        # LCD Display active screen area
        self.create_rectangle(bx + 18, by + 12, bx + 106, by + 72, outline=BORDER_DIM, width=1, fill="#02060e")
        self.create_text(bx + 62, by + 42, text="1.9\" LCD", fill=NEON_CYAN, font=("Consolas", 8, "bold"))

        # Right side schematic leader lines
        # Line 1: ESP32-S3
        self.create_line(bx + bw, by + 22, bx + bw + 20, by + 22, fill=BORDER_DIM, width=1)
        self.create_line(bx + bw + 20, by + 22, bx + bw + 35, by + 15, fill=BORDER_DIM, width=1)
        self.create_text(bx + bw + 42, by + 15, anchor=tk.W, text="ESP32-S3", fill=TEXT_WHITE, font=("Consolas", 8, "bold"))

        # Line 2: 1.9" LCD
        self.create_line(bx + bw, by + 42, bx + bw + 35, by + 42, fill=BORDER_DIM, width=1)
        self.create_text(bx + bw + 42, by + 42, anchor=tk.W, text="ST7789V", fill=TEXT_MUTED, font=("Consolas", 8))

        # Line 3: USB-C
        self.create_line(bx + bw, by + 62, bx + bw + 20, by + 62, fill=BORDER_DIM, width=1)
        self.create_line(bx + bw + 20, by + 62, bx + bw + 35, by + 68, fill=BORDER_DIM, width=1)
        self.create_text(bx + bw + 42, by + 68, anchor=tk.W, text="USB-JTAG", fill=TEXT_MUTED, font=("Consolas", 8))

        # Bottom header pins
        for i in range(8):
            px = bx + 24 + i * 10
            self.create_line(px, by + bh, px, by + bh + 8, fill=BORDER_DIM, width=1)
        self.create_text(bx + 60, by + bh + 16, text="PINOUT 1:2", fill=TEXT_MUTED, font=("Consolas", 7))


class SeederFlasherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SEEDER FLASHER // TRON: LEGACY")
        self.geometry("980x620")
        self.minsize(940, 580)
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
        # 1. Outer TRON Window Frame
        outer = tk.Frame(self, bg=BG_VOID, highlightthickness=2, highlightbackground=BORDER_CYAN)
        outer.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        # Header Bar
        head_frame = tk.Frame(outer, bg=BG_VOID)
        head_frame.pack(fill=tk.X, padx=20, pady=(16, 8))

        # S Glyph + SEEDER FLASHER Title
        title_box = tk.Frame(head_frame, bg=BG_VOID)
        title_box.pack(side=tk.LEFT)

        s_canvas = tk.Canvas(title_box, width=32, height=32, bg=BG_VOID, highlightthickness=0)
        s_canvas.pack(side=tk.LEFT, padx=(0, 10))
        # Draw glowing 'S' glyph
        s_canvas.create_line(4, 6, 26, 6, fill=NEON_CYAN, width=3)
        s_canvas.create_line(4, 6, 4, 16, fill=NEON_CYAN, width=3)
        s_canvas.create_line(4, 16, 26, 16, fill=NEON_WHITE, width=3)
        s_canvas.create_line(26, 16, 26, 26, fill=NEON_CYAN, width=3)
        s_canvas.create_line(4, 26, 26, 26, fill=NEON_CYAN, width=3)

        title_lbl = tk.Label(
            title_box, text="SEEDER FLASHER",
            font=("Segoe UI", 18, "bold"), fg=NEON_CYAN, bg=BG_VOID
        )
        title_lbl.pack(side=tk.LEFT)

        sub_title = tk.Label(
            title_box, text=" · THE DIGITAL GRID CONDUIT",
            font=("Consolas", 9, "bold"), fg=TEXT_MUTED, bg=BG_VOID
        )
        sub_title.pack(side=tk.LEFT, pady=(4, 0))

        # 2. Main Dual-Column Content Split
        main_split = tk.Frame(outer, bg=BG_VOID)
        main_split.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)

        # ========================================================
        # LEFT COLUMN: DEVICE CONFIGURATION
        # ========================================================
        left_col = tk.Frame(main_split, bg=BG_PANEL, bd=1, relief=tk.SOLID, highlightthickness=1, highlightbackground=BORDER_CYAN, width=340)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 14))
        left_col.pack_propagate(False)

        l_pad = tk.Frame(left_col, bg=BG_PANEL)
        l_pad.pack(fill=tk.BOTH, expand=True, padx=16, pady=14)

        # Card Title with indicator LEDs
        l_head = tk.Frame(l_pad, bg=BG_PANEL)
        l_head.pack(fill=tk.X, pady=(0, 10))

        card_title = tk.Label(
            l_head, text="DEVICE CONFIGURATION",
            font=("Consolas", 10, "bold"), fg=TEXT_WHITE, bg=BG_PANEL
        )
        card_title.pack(side=tk.LEFT)

        # LED status indicators
        self.led_canvas = tk.Canvas(l_head, width=36, height=16, bg=BG_PANEL, highlightthickness=0)
        self.led_canvas.pack(side=tk.RIGHT)
        self.led_canvas.create_oval(6, 4, 14, 12, fill=NEON_CYAN, outline="")
        self.led_canvas.create_oval(20, 4, 28, 12, fill=LED_GREEN, outline="")

        # Port Selection Row
        p_row = tk.Frame(l_pad, bg=BG_PANEL)
        p_row.pack(fill=tk.X, pady=(4, 2))

        self.port_bullet = tk.Label(
            p_row, text="• PORT:", font=("Consolas", 9, "bold"),
            fg=NEON_CYAN, bg=BG_PANEL
        )
        self.port_bullet.pack(side=tk.LEFT)

        self.port_status_lbl = tk.Label(
            p_row, text="SCANNING...", font=("Consolas", 8, "bold"),
            fg=LED_GREEN, bg=BG_PANEL
        )
        self.port_status_lbl.pack(side=tk.RIGHT)

        self.port_combo = ttk.Combobox(l_pad, state="readonly", font=("Consolas", 9))
        self.port_combo.pack(fill=tk.X, pady=(2, 8))
        self.port_combo.bind("<<ComboboxSelected>>", self._on_port_selected)

        # Device info readouts
        self.dev_lbl = tk.Label(
            l_pad, text="• DEVICE: LilyGO T-Display-S3",
            font=("Consolas", 9), fg=TEXT_WHITE, bg=BG_PANEL, anchor=tk.W
        )
        self.dev_lbl.pack(fill=tk.X, pady=2)

        self.chip_lbl = tk.Label(
            l_pad, text="• CHIP: ESP32-S3 (16MB Flash · QIO)",
            font=("Consolas", 8), fg=TEXT_MUTED, bg=BG_PANEL, anchor=tk.W
        )
        self.chip_lbl.pack(fill=tk.X, pady=1)

        self.driver_lbl = tk.Label(
            l_pad, text="• DRIVER: USB-Serial / JTAG CDC",
            font=("Consolas", 8), fg=TEXT_MUTED, bg=BG_PANEL, anchor=tk.W
        )
        self.driver_lbl.pack(fill=tk.X, pady=(1, 8))

        # Vector Schematic
        self.schematic = HardwareSchematic(l_pad, width=300, height=110)
        self.schematic.pack(fill=tk.X, pady=(4, 10))

        # Hardware Model Selection
        model_box = tk.Frame(l_pad, bg=BG_PANEL)
        model_box.pack(fill=tk.X, pady=(4, 0))

        tk.Label(
            model_box, text="TARGET HARDWARE ARCHITECTURE:",
            font=("Consolas", 8, "bold"), fg=BORDER_DIM, bg=BG_PANEL, anchor=tk.W
        ).pack(fill=tk.X, pady=(0, 4))

        self.rb_s3 = tk.Radiobutton(
            model_box, text="LilyGO T-Display-S3 (ESP32-S3)",
            variable=self.target_var, value="tdisplay-s3",
            font=("Consolas", 8), fg=TEXT_WHITE, bg=BG_PANEL, selectcolor=BG_INPUT,
            activebackground=BG_PANEL, activeforeground=NEON_CYAN
        )
        self.rb_s3.pack(anchor=tk.W)

        self.rb_t = tk.Radiobutton(
            model_box, text="LilyGO TTGO T-Display (ESP32)",
            variable=self.target_var, value="tdisplay",
            font=("Consolas", 8), fg=TEXT_WHITE, bg=BG_PANEL, selectcolor=BG_INPUT,
            activebackground=BG_PANEL, activeforeground=NEON_CYAN
        )
        self.rb_t.pack(anchor=tk.W)

        # ========================================================
        # RIGHT COLUMN: THE DIGITAL GRID & IDENTITY DISC
        # ========================================================
        right_col = tk.Frame(main_split, bg=BG_VOID)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Operation Header
        op_frame = tk.Frame(right_col, bg=BG_VOID)
        op_frame.pack(fill=tk.X, pady=(4, 2))

        tk.Label(
            op_frame, text="CURRENT OPERATION:",
            font=("Consolas", 8, "bold"), fg=BORDER_DIM, bg=BG_VOID
        ).pack(anchor=tk.W)

        self.op_lbl = tk.Label(
            op_frame, text="SYSTEM STANDBY // LINK ESTABLISHED",
            font=("Consolas", 11, "bold"), fg=TEXT_WHITE, bg=BG_VOID
        )
        self.op_lbl.pack(anchor=tk.W)

        # Identity Disc
        self.disc = IdentityDisc(right_col, width=540, height=330, on_click=self._start_flash)
        self.disc.pack(fill=tk.BOTH, expand=True)

        # Bottom Telemetry Line
        self.telemetry_lbl = tk.Label(
            right_col,
            text="WRITING: firmware.bin (572 KB) | BAUD: 115200 | SEEDER SOVEREIGN WALLET",
            font=("Consolas", 8), fg=TEXT_MUTED, bg=BG_VOID
        )
        self.telemetry_lbl.pack(fill=tk.X, pady=(2, 6))

        # Bottom Action Bar
        action_bar = tk.Frame(right_col, bg=BG_VOID)
        action_bar.pack(fill=tk.X, pady=(4, 0))

        self.scan_btn = TronButton(
            action_bar, text="RESCAN PORTS",
            command=self._manual_scan, width=130, height=36, is_primary=False
        )
        self.scan_btn.pack(side=tk.RIGHT, padx=(8, 0))

        self.flash_btn = TronButton(
            action_bar, text="FLASH FIRMWARE",
            command=self._start_flash, width=170, height=36, is_primary=True
        )
        self.flash_btn.pack(side=tk.RIGHT)

        # Toggle terminal button
        self.term_toggle = tk.Button(
            action_bar, text="[+] TERMINAL TELEMETRY", font=("Consolas", 8),
            bg=BG_VOID, fg=BORDER_DIM, activebackground=BG_VOID, activeforeground=NEON_CYAN,
            bd=0, cursor="hand2", command=self._toggle_terminal
        )
        self.term_toggle.pack(side=tk.LEFT)

        # 3. Collapsible Terminal Console (Bottom)
        self.term_frame = tk.Frame(outer, bg=BG_INPUT, bd=1, relief=tk.SOLID, highlightthickness=1, highlightbackground="#0c1828")
        self.term_visible = False

        self.log_text = tk.Text(
            self.term_frame, bg=BG_INPUT, fg="#7fa1c4", font=("Consolas", 8),
            insertbackground=NEON_CYAN, selectbackground="#003544",
            relief=tk.FLAT, wrap=tk.WORD, height=5
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        self._log("TRON: Seeder Flash Grid initialized.")
        self._log("I/O Conduit ready. Scanning USB serial devices...")

    def _log(self, text):
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)

    def _clear_log(self):
        self.log_text.delete("1.0", tk.END)

    def _toggle_terminal(self):
        if self.term_visible:
            self.term_frame.pack_forget()
            self.term_toggle.config(text="[+] TERMINAL TELEMETRY", fg=BORDER_DIM)
            self.term_visible = False
        else:
            self.term_frame.pack(fill=tk.X, padx=20, pady=(6, 12))
            self.term_toggle.config(text="[-] HIDE TERMINAL", fg=NEON_CYAN)
            self.term_visible = True

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

        if not ports:
            self.port_combo['values'] = ["No Ports Detected"]
            self.port_combo.current(0)
            self.selected_port = None
            self.port_status_lbl.config(text="DISCONNECTED", fg=LED_AMBER)
            self.op_lbl.config(text="STANDBY // CONNECT LILYGO USB CABLE", fg=TEXT_MUTED)
            self.disc.set_progress(0, status="NO DEVICE", sub="PLUG IN USB CABLE")
            self.flash_btn.set_enabled(False)
            return

        display_values = [f"{p.port} - {p.product}" for p in ports]
        self.port_combo['values'] = display_values

        selected_idx = 0
        for i, p in enumerate(ports):
            if p.status == "flash-candidate":
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
        if 0 <= idx < len(self.detected_ports):
            p = self.detected_ports[idx]
            self.selected_port = p
            self.target_var.set(p.default_target)
            self._update_selection_state()

    def _update_selection_state(self):
        if self.selected_port:
            p = self.selected_port
            is_cand = (p.status == "flash-candidate")
            self.port_status_lbl.config(
                text="OPEN // READY" if is_cand else "SERIAL LINK",
                fg=LED_GREEN if is_cand else NEON_CYAN
            )
            self.dev_lbl.config(text=f"• DEVICE: {p.product}")
            self.op_lbl.config(text=f"READY // TARGET: {p.port} [{self.target_var.get().upper()}]", fg=TEXT_WHITE)
            self.disc.set_progress(0, status="READY TO FLASH", sub="CLICK DISC OR BUTTON")
            self.flash_btn.set_enabled(True)
            self.flash_btn.set_text("FLASH FIRMWARE")

    def _start_flash(self):
        if not self.selected_port or self.flashing:
            return

        port = self.selected_port.port
        target = self.target_var.get()

        self.flashing = True
        self.flash_btn.set_enabled(False)
        self.flash_btn.set_text("FLASHING...")
        self.scan_btn.set_enabled(False)
        self.port_combo.config(state=tk.DISABLED)

        self.op_lbl.config(text=f"ERASE & WRITE FLASH // {port} [{target.upper()}]", fg=NEON_CYAN)
        self.disc.set_progress(1, status="INITIALIZING CONDUIT...", sub=f"{port} AT 115200")

        self._log("\n" + "=" * 60)
        self._log(f"TRON CONDUIT ENGAGED: TARGET [{target.upper()}] ON {port}")
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
        self.disc.set_progress(pct, status="FLASHING FIRMWARE...", sub=msg[:28])
        self.telemetry_lbl.config(
            text=f"CONDUIT ACTIVE: {pct}% | {msg} | SEEDER FIRMWARE",
            fg=NEON_CYAN
        )

    def _on_flash_complete(self, success, error_msg):
        self.flashing = False
        self.scan_btn.set_enabled(True)
        self.port_combo.config(state="readonly")

        if success:
            self.disc.set_progress(100, status="FLASH COMPLETE", sub="HARDWARE REBOOTED")
            self.op_lbl.config(text="OPERATION COMPLETE // VERIFIED SUCCESS", fg=LED_GREEN)
            self.flash_btn.set_text("FLASH VERIFIED")
            self.telemetry_lbl.config(
                text="CONDUIT CLOSED: 100% | Firmware verified and rebooted into Seeder cold-storage!",
                fg=LED_GREEN
            )
            self._log("\n[✓] CONDUIT CLOSED: Hardware reset completed. Board running Seeder!")
            messagebox.showinfo(
                "TRON Grid Link Complete",
                f"Firmware flash verified on {self.selected_port.port}!\n\n"
                "Your LilyGO device has reset and is now operating as a sovereign Seeder cold-storage wallet."
            )
        else:
            self.disc.set_progress(0, status="FLASH FAILED", sub=error_msg[:24])
            self.op_lbl.config(text=f"FLASH FAILED // {error_msg}", fg="#ff4455")
            self.flash_btn.set_text("RETRY FLASH")
            self._log(f"\n[!] ERROR: Flashing failed: {error_msg}")
            messagebox.showerror(
                "Grid Transfer Error",
                f"Flashing failed on {self.selected_port.port}:\n\n{error_msg}"
            )

        self.after(4000, self._reset_flash_btn)

    def _reset_flash_btn(self):
        if not self.flashing and self.selected_port:
            self.flash_btn.set_enabled(True)
            self.flash_btn.set_text("FLASH FIRMWARE")


def main():
    app = SeederFlasherApp()
    app.mainloop()


if __name__ == "__main__":
    main()
