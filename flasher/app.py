"""
Seeder Flasher - TRON: Legacy Inspired Hardware Installer
The Digital Grid / Identity Disc Interface with Authentic Photorealistic Neon Glow
"""

import sys
import os
import io
import math
import threading
import time
import ctypes
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageTk

# Provide fallback for sys.stdout/stderr in windowed mode
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

# Ensure flasher directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine

# Palette - TRON: Legacy Grid Theme
BG_VOID       = "#02050a"   # Deepest digital void
BG_PANEL      = "#040c18"   # Dark glass panel
BG_INPUT      = "#030810"   # Terminal and input recesses
BORDER_CYAN   = "#00f3ff"   # Luminescent ice blue / cyan
BORDER_DIM    = "#005566"   # Dim cyan circuit trace
NEON_CYAN     = "#00f3ff"   # Primary TRON cyan
NEON_WHITE    = "#ffffff"   # Specular white core
TEXT_CYAN     = "#00f3ff"   # High-visibility cyan readout
TEXT_WHITE    = "#f0f8ff"   # Ice white text
TEXT_MUTED    = "#5a7896"   # Telemetry blue-gray
LED_GREEN     = "#00ff9d"   # Link active green
LED_AMBER     = "#ffaa00"   # Warning state

# Typography helper
def get_font(family, size, weight="normal"):
    return (family, size, weight)


class TronPillButton(tk.Canvas):
    """Pill-shaped button with authentic multi-stage neon glow and hover feedback."""
    def __init__(self, parent, text, command, width=170, height=40, is_primary=True, **kwargs):
        super().__init__(parent, width=width, height=height, bg=BG_VOID, highlightthickness=0, **kwargs)
        self.text = text
        self.command = command
        self.w = width
        self.h = height
        self.is_primary = is_primary
        self.enabled = True
        self.hover = False
        self._photo = None

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
        im = Image.new("RGBA", (self.w, self.h), (2, 5, 10, 0))
        r = self.h // 2 - 2
        pad = 2

        if not self.enabled:
            border_col = (20, 45, 65, 180)
            fill_col = (4, 8, 14, 220)
            text_col = (40, 70, 95, 255)
            has_glow = False
        elif self.is_primary:
            if self.hover:
                glow_col = (0, 243, 255, 160)
                border_col = (255, 255, 255, 255)
                fill_col = (0, 80, 110, 240)
                text_col = (255, 255, 255, 255)
                has_glow = True
            else:
                glow_col = (0, 243, 255, 120)
                border_col = (0, 243, 255, 255)
                fill_col = (0, 45, 65, 230)
                text_col = (255, 255, 255, 255)
                has_glow = True
        else:
            if self.hover:
                glow_col = (0, 243, 255, 100)
                border_col = (0, 243, 255, 255)
                fill_col = (6, 25, 42, 220)
                text_col = (0, 243, 255, 255)
                has_glow = True
            else:
                glow_col = (0, 150, 200, 50)
                border_col = (0, 180, 220, 180)
                fill_col = (4, 14, 25, 200)
                text_col = (0, 243, 255, 220)
                has_glow = False

        # Draw outer bloom if enabled
        if has_glow:
            glow_img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
            gd = ImageDraw.Draw(glow_img)
            gd.rounded_rectangle([pad, pad, self.w - pad, self.h - pad], radius=r, outline=glow_col, width=4)
            glow_img = glow_img.filter(ImageFilter.GaussianBlur(3))
            im = Image.alpha_composite(im, glow_img)

        # Draw solid fill and crisp border
        cd = ImageDraw.Draw(im)
        cd.rounded_rectangle([pad, pad, self.w - pad, self.h - pad], radius=r, fill=fill_col, outline=border_col, width=2)

        # Draw specular top highlight
        if self.enabled and self.hover:
            cd.arc([pad + 4, pad + 2, self.w - pad - 4, pad + 14], start=180, end=0, fill=(255, 255, 255, 180), width=1)

        # Render centered text
        try:
            fnt = ImageFont.truetype("consolab.ttf", 11)
        except Exception:
            fnt = None

        if fnt:
            bbox = cd.textbbox((0, 0), self.text, font=fnt)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            tx = (self.w - tw) // 2
            ty = (self.h - th) // 2 - 1
            cd.text((tx, ty), self.text, fill=text_col, font=fnt)

        self._photo = ImageTk.PhotoImage(im)
        self.delete("all")
        self.create_image(0, 0, image=self._photo, anchor="nw")


class GlowingIdentityDisc(tk.Canvas):
    """The centerpiece TRON Identity Disc with authentic multi-layer neon bloom."""
    def __init__(self, parent, width=540, height=340, on_click=None, **kwargs):
        super().__init__(parent, width=width, height=height, bg=BG_VOID, highlightthickness=0, **kwargs)
        self.w = width
        self.h = height
        self.on_click = on_click
        self.percent = 0
        self.status_text = "READY TO FLASH"
        self.sub_text = "CLICK DISC OR BUTTON"
        self.is_flashing = False
        self.hover = False
        self._photo = None

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
        w, h = self.w, self.h
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        cx = w // 2
        cy = h // 2

        # Disc geometry
        r_outer_ticks = 152
        r_outer_ring  = 138
        r_track       = 114
        r_core        = 88

        # Ambient Glow behind disc
        glow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow_layer)

        # Soft blue/cyan atmospheric pool in center
        gd.ellipse([cx - r_core, cy - r_core, cx + r_core, cy + r_core], fill=(0, 210, 255, 35 if not self.hover else 60))
        gd.ellipse([cx - r_track, cy - r_track, cx + r_track, cy + r_track], fill=(0, 180, 240, 20))

        # Glowing Progress Arc / Ambient Ring Bloom
        if self.percent > 0:
            sweep = int((self.percent / 100.0) * 360)
            start_ang = -90
            end_ang = -90 + sweep
            # Wide soft bloom
            gd.arc([cx - r_track, cy - r_track, cx + r_track, cy + r_track],
                   start=start_ang, end=end_ang, fill=(0, 243, 255, 120), width=20)
            # Mid bloom
            gd.arc([cx - r_track, cy - r_track, cx + r_track, cy + r_track],
                   start=start_ang, end=end_ang, fill=(0, 243, 255, 200), width=10)
        else:
            # Subtle idle neon breathing ring
            idle_alpha = 90 if self.hover else 45
            gd.ellipse([cx - r_track, cy - r_track, cx + r_track, cy + r_track],
                       outline=(0, 243, 255, idle_alpha), width=10)

        # Outer decorative tracks bloom
        gd.ellipse([cx - r_outer_ring, cy - r_outer_ring, cx + r_outer_ring, cy + r_outer_ring],
                   outline=(0, 243, 255, 75), width=4)

        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(5))
        im = Image.alpha_composite(im, glow_layer)

        # Crisp Vector Pass
        cd = ImageDraw.Draw(im)

        # 1. Segmented Outer Tick Marks
        for a in range(0, 360, 8):
            rad = math.radians(a)
            is_major = (a % 24 == 0)
            col = (0, 243, 255, 255) if is_major else (0, 150, 200, 160)
            w_line = 2 if is_major else 1
            x1 = cx + (r_outer_ticks - 4) * math.cos(rad)
            y1 = cy + (r_outer_ticks - 4) * math.sin(rad)
            x2 = cx + (r_outer_ticks + 5) * math.cos(rad)
            y2 = cy + (r_outer_ticks + 5) * math.sin(rad)
            cd.line([(x1, y1), (x2, y2)], fill=col, width=w_line)

        # 2. Concentric Secondary Track Ring
        cd.ellipse([cx - r_outer_ring, cy - r_outer_ring, cx + r_outer_ring, cy + r_outer_ring],
                   outline=(0, 190, 240, 210), width=2)

        # 3. Background Track Groove
        cd.ellipse([cx - r_track, cy - r_track, cx + r_track, cy + r_track],
                   outline=(6, 28, 46, 240), width=9)

        # 4. Primary Intense Progress Arc
        if self.percent > 0:
            sweep = int((self.percent / 100.0) * 360)
            start_ang = -90
            end_ang = -90 + sweep
            # Saturated cyan neon body
            cd.arc([cx - r_track, cy - r_track, cx + r_track, cy + r_track],
                   start=start_ang, end=end_ang, fill=(0, 243, 255, 255), width=8)
            # Specular white hot core
            cd.arc([cx - r_track, cy - r_track, cx + r_track, cy + r_track],
                   start=start_ang, end=end_ang, fill=(255, 255, 255, 255), width=2)

            # Leading Energy Spark
            lead_rad = math.radians(end_ang)
            lx = cx + r_track * math.cos(lead_rad)
            ly = cy + r_track * math.sin(lead_rad)
            cd.ellipse([lx - 5, ly - 5, lx + 5, ly + 5], fill=(255, 255, 255, 255), outline=(0, 243, 255, 255), width=2)
        elif self.hover:
            cd.ellipse([cx - r_track, cy - r_track, cx + r_track, cy + r_track],
                       outline=(0, 243, 255, 200), width=3)

        # 5. Inner Core Glass Dish
        dish_fill = (2, 14, 26, 230) if not self.hover else (4, 22, 38, 240)
        cd.ellipse([cx - r_core, cy - r_core, cx + r_core, cy + r_core],
                   fill=dish_fill, outline=(0, 243, 255, 200), width=2)
        # Inner fine border
        cd.ellipse([cx - r_core + 4, cy - r_core + 4, cx + r_core - 4, cy + r_core - 4],
                   outline=(0, 100, 140, 100), width=1)

        # 6. Center Typography
        if self.percent > 0:
            pct_str = f"{int(self.percent)}%"
        else:
            pct_str = "READY"

        try:
            font_big = ImageFont.truetype("segoeuib.ttf", 36)
            font_status = ImageFont.truetype("consolab.ttf", 10)
            font_sub = ImageFont.truetype("consolab.ttf", 8)
        except Exception:
            font_big = font_status = font_sub = None

        if font_big:
            # Big text with drop glow
            bbox = cd.textbbox((0, 0), pct_str, font=font_big)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            tx = cx - tw // 2
            ty = cy - th // 2 - 14

            # Cyan shadow bloom
            cd.text((tx, ty - 1), pct_str, fill=(0, 243, 255, 180), font=font_big)
            cd.text((tx, ty + 1), pct_str, fill=(0, 243, 255, 180), font=font_big)
            cd.text((tx - 1, ty), pct_str, fill=(0, 243, 255, 180), font=font_big)
            cd.text((tx + 1, ty), pct_str, fill=(0, 243, 255, 180), font=font_big)
            # Crisp white core
            cd.text((tx, ty), pct_str, fill=(255, 255, 255, 255), font=font_big)

        if font_status:
            bbox = cd.textbbox((0, 0), self.status_text, font=font_status)
            tw = bbox[2] - bbox[0]
            cd.text((cx - tw // 2, cy + 18), self.status_text, fill=(0, 243, 255, 255), font=font_status)

        if font_sub:
            bbox = cd.textbbox((0, 0), self.sub_text, font=font_sub)
            tw = bbox[2] - bbox[0]
            cd.text((cx - tw // 2, cy + 33), self.sub_text, fill=(90, 130, 165, 240), font=font_sub)

        self._photo = ImageTk.PhotoImage(im)
        self.delete("all")
        self.create_image(0, 0, image=self._photo, anchor="nw")


class HardwareSchematic(tk.Canvas):
    """Glowing vector schematic of the LilyGO hardware and pinout."""
    def __init__(self, parent, width=310, height=125, **kwargs):
        super().__init__(parent, width=width, height=height, bg=BG_PANEL, highlightthickness=0, **kwargs)
        self.w = width
        self.h = height
        self._photo = None
        self.draw()

    def draw(self):
        w, h = self.w, self.h
        im = Image.new("RGBA", (w, h), (4, 12, 24, 0))

        glow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow_layer)

        bx, by, bw, bh = 18, 14, 120, 80
        # Glow around board outline
        gd.rounded_rectangle([bx, by, bx + bw, by + bh], radius=4, outline=(0, 243, 255, 100), width=3)
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(2))
        im = Image.alpha_composite(im, glow_layer)

        cd = ImageDraw.Draw(im)
        # Crisp board outline
        cd.rounded_rectangle([bx, by, bx + bw, by + bh], radius=4, fill=(3, 9, 18, 240), outline=(0, 243, 255, 255), width=2)

        # USB-C Port receptacle (Left edge)
        cd.rectangle([bx - 8, by + 26, bx, by + 54], fill=(2, 6, 12, 255), outline=(0, 243, 255, 255), width=2)
        cd.line([(bx - 14, by + 40), (bx - 8, by + 40)], fill=(0, 180, 220, 220), width=2)

        # LCD Display active screen area
        cd.rectangle([bx + 16, by + 12, bx + 104, by + 68], fill=(1, 5, 12, 255), outline=(0, 150, 200, 180), width=1)

        try:
            font_chip = ImageFont.truetype("consolab.ttf", 9)
            font_lbl = ImageFont.truetype("consola.ttf", 8)
            font_pin = ImageFont.truetype("consola.ttf", 7)
        except Exception:
            font_chip = font_lbl = font_pin = None

        if font_chip:
            cd.text((bx + 34, by + 34), '1.9" LCD', fill=(0, 243, 255, 255), font=font_chip)

        # Leader lines pointing right
        lx = bx + bw
        # 1: ESP32-S3
        cd.line([(lx, by + 20), (lx + 20, by + 20), (lx + 32, by + 14)], fill=(0, 160, 210, 200), width=1)
        cd.ellipse([lx + 32 - 2, by + 14 - 2, lx + 32 + 2, by + 14 + 2], fill=(255, 255, 255, 255))
        if font_chip:
            cd.text((lx + 38, by + 9), "ESP32-S3", fill=(255, 255, 255, 255), font=font_chip)

        # 2: ST7789V
        cd.line([(lx, by + 40), (lx + 32, by + 40)], fill=(0, 160, 210, 200), width=1)
        cd.ellipse([lx + 32 - 2, by + 40 - 2, lx + 32 + 2, by + 40 + 2], fill=(0, 243, 255, 255))
        if font_lbl:
            cd.text((lx + 38, by + 35), "ST7789V", fill=(90, 135, 175, 240), font=font_lbl)

        # 3: USB-JTAG
        cd.line([(lx, by + 60), (lx + 20, by + 60), (lx + 32, by + 66)], fill=(0, 160, 210, 200), width=1)
        cd.ellipse([lx + 32 - 2, by + 66 - 2, lx + 32 + 2, by + 66 + 2], fill=(0, 243, 255, 255))
        if font_lbl:
            cd.text((lx + 38, by + 61), "USB-JTAG", fill=(90, 135, 175, 240), font=font_lbl)

        # Bottom header pins
        for i in range(8):
            px = bx + 22 + i * 10
            cd.line([(px, by + bh), (px, by + bh + 8)], fill=(0, 160, 210, 220), width=1)
            cd.ellipse([px - 1, by + bh + 8 - 1, px + 1, by + bh + 8 + 1], fill=(0, 243, 255, 255))

        if font_pin:
            cd.text((bx + 40, by + bh + 12), "PINOUT 1:2", fill=(70, 105, 140, 220), font=font_pin)

        self._photo = ImageTk.PhotoImage(im)
        self.delete("all")
        self.create_image(0, 0, image=self._photo, anchor="nw")


class SeederFlasherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SEEDER FLASHER // TRON: LEGACY")
        self.w = 1000
        self.h = 640
        self.geometry(f"{self.w}x{self.h}")
        self.configure(bg=BG_VOID)
        self.resizable(False, False)

        # Make frameless with taskbar presence
        self.overrideredirect(True)
        self._setup_taskbar()

        # Center on screen
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - self.w) // 2
        y = (sh - self.h) // 2
        self.geometry(f"+{x}+{y}")

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
        self._drag_x = 0
        self._drag_y = 0

        self._build_ui()
        self._start_port_scanner()

    def _setup_taskbar(self):
        """Ensures the frameless window has a proper taskbar icon in Windows."""
        try:
            self.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            style = (style & ~0x00000080) | 0x00040000  # -WS_EX_TOOLWINDOW +WS_EX_APPWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
            self.wm_withdraw()
            self.after(10, self.wm_deiconify)
        except Exception:
            pass

    def _build_ui(self):
        # 1. Master Canvas for complete composite background
        self.bg_canvas = tk.Canvas(self, width=self.w, height=self.h, bg=BG_VOID, highlightthickness=0)
        self.bg_canvas.pack(fill=tk.BOTH, expand=True)

        self._render_master_background()

        # Title Bar Window Dragging
        self.bg_canvas.bind("<Button-1>", self._on_canvas_click)
        self.bg_canvas.bind("<B1-Motion>", self._on_canvas_drag)

        # 2. Window Control Buttons (Top Right: Minimize, Maximize, Close)
        pad = 12
        ctrl_x = self.w - pad - 26
        # Close Button 'X'
        self.close_btn = tk.Canvas(self, width=28, height=28, bg=BG_VOID, highlightthickness=0, cursor="hand2")
        self.close_btn.place(x=ctrl_x - 14, y=pad + 10)
        self._draw_close_btn(False)
        self.close_btn.bind("<Enter>", lambda e: self._draw_close_btn(True))
        self.close_btn.bind("<Leave>", lambda e: self._draw_close_btn(False))
        self.close_btn.bind("<Button-1>", lambda e: self.destroy())

        # Maximize Button '▢'
        self.max_btn = tk.Canvas(self, width=28, height=28, bg=BG_VOID, highlightthickness=0, cursor="hand2")
        self.max_btn.place(x=ctrl_x - 46, y=pad + 10)
        self._draw_max_btn(False)
        self.max_btn.bind("<Enter>", lambda e: self._draw_max_btn(True))
        self.max_btn.bind("<Leave>", lambda e: self._draw_max_btn(False))

        # Minimize Button '—'
        self.min_btn = tk.Canvas(self, width=28, height=28, bg=BG_VOID, highlightthickness=0, cursor="hand2")
        self.min_btn.place(x=ctrl_x - 78, y=pad + 10)
        self._draw_min_btn(False)
        self.min_btn.bind("<Enter>", lambda e: self._draw_min_btn(True))
        self.min_btn.bind("<Leave>", lambda e: self._draw_min_btn(False))
        self.min_btn.bind("<Button-1>", self._on_minimize)

        # 3. Left Panel (Device Configuration)
        l_x1, l_y1 = pad + 18, pad + 56
        l_w, l_h = 355, self.h - pad - 22 - l_y1

        self.left_frame = tk.Frame(self, bg=BG_PANEL, width=l_w, height=l_h)
        self.left_frame.place(x=l_x1 + 6, y=l_y1 + 6, width=l_w - 12, height=l_h - 12)

        # Panel Header & Status LEDs
        l_head = tk.Frame(self.left_frame, bg=BG_PANEL)
        l_head.pack(fill=tk.X, padx=14, pady=(12, 6))

        tk.Label(
            l_head, text="DEVICE CONFIGURATION",
            font=("Consolas", 10, "bold"), fg=TEXT_WHITE, bg=BG_PANEL
        ).pack(side=tk.LEFT)

        # LED status indicators
        self.led_canvas = tk.Canvas(l_head, width=38, height=16, bg=BG_PANEL, highlightthickness=0)
        self.led_canvas.pack(side=tk.RIGHT)
        self.led_canvas.create_oval(6, 4, 14, 12, fill=NEON_CYAN, outline="")
        self.led_canvas.create_oval(22, 4, 30, 12, fill=LED_GREEN, outline="")

        # Port Selection Row
        p_row = tk.Frame(self.left_frame, bg=BG_PANEL)
        p_row.pack(fill=tk.X, padx=14, pady=(2, 2))

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

        # Styled Combobox
        combo_style = ttk.Style()
        combo_style.theme_use('clam')
        combo_style.configure("Tron.TCombobox",
                              fieldbackground=BG_INPUT,
                              background=BG_PANEL,
                              foreground=NEON_CYAN,
                              darkcolor=BORDER_DIM,
                              lightcolor=BORDER_DIM,
                              arrowcolor=NEON_CYAN)

        self.port_combo = ttk.Combobox(self.left_frame, style="Tron.TCombobox", state="readonly", font=("Consolas", 9))
        self.port_combo.pack(fill=tk.X, padx=14, pady=(2, 6))
        self.port_combo.bind("<<ComboboxSelected>>", self._on_port_selected)

        # Device Metadata Readouts
        self.dev_lbl = tk.Label(
            self.left_frame, text="• DEVICE: LilyGO T-Display-S3",
            font=("Consolas", 9), fg=TEXT_WHITE, bg=BG_PANEL, anchor=tk.W
        )
        self.dev_lbl.pack(fill=tk.X, padx=14, pady=1)

        self.chip_lbl = tk.Label(
            self.left_frame, text="• CHIP: ESP32-S3 (16MB Flash · QIO)",
            font=("Consolas", 8), fg=TEXT_MUTED, bg=BG_PANEL, anchor=tk.W
        )
        self.chip_lbl.pack(fill=tk.X, padx=14, pady=1)

        self.driver_lbl = tk.Label(
            self.left_frame, text="• DRIVER: USB-Serial / JTAG CDC",
            font=("Consolas", 8), fg=TEXT_MUTED, bg=BG_PANEL, anchor=tk.W
        )
        self.driver_lbl.pack(fill=tk.X, padx=14, pady=(1, 6))

        # Hardware Vector Schematic
        self.schematic = HardwareSchematic(self.left_frame, width=310, height=115)
        self.schematic.pack(fill=tk.X, padx=14, pady=(2, 8))

        # Target Hardware Architecture
        model_box = tk.Frame(self.left_frame, bg=BG_PANEL)
        model_box.pack(fill=tk.X, padx=14, pady=(2, 0))

        tk.Label(
            model_box, text="TARGET HARDWARE ARCHITECTURE:",
            font=("Consolas", 8, "bold"), fg=BORDER_DIM, bg=BG_PANEL, anchor=tk.W
        ).pack(fill=tk.X, pady=(0, 2))

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

        # 4. Right Side: Identity Disc & Conduit Area
        r_x = 420
        # Operation Header
        op_frame = tk.Frame(self, bg=BG_VOID)
        op_frame.place(x=r_x + 10, y=pad + 58, width=540, height=38)

        tk.Label(
            op_frame, text="CURRENT OPERATION:",
            font=("Consolas", 8, "bold"), fg=BORDER_DIM, bg=BG_VOID
        ).pack(anchor=tk.W)

        self.op_lbl = tk.Label(
            op_frame, text="STANDBY // SCANNING DIGITAL GRID",
            font=("Consolas", 10, "bold"), fg=TEXT_WHITE, bg=BG_VOID
        )
        self.op_lbl.pack(anchor=tk.W)

        # Glowing Identity Disc Canvas
        self.disc = GlowingIdentityDisc(self, width=540, height=330, on_click=self._start_flash)
        self.disc.place(x=r_x + 10, y=pad + 98)

        # Bottom Telemetry Line
        self.telemetry_lbl = tk.Label(
            self,
            text="WRITING: firmware.bin (572 KB) | BAUD: 115200 | SEEDER SOVEREIGN WALLET",
            font=("Consolas", 8), fg=TEXT_MUTED, bg=BG_VOID, anchor=tk.W
        )
        self.telemetry_lbl.place(x=r_x + 10, y=self.h - pad - 68, width=540)

        # Action Buttons (Bottom Right)
        btn_y = self.h - pad - 48
        self.scan_btn = TronPillButton(
            self, text="RESCAN PORTS",
            command=self._manual_scan, width=140, height=38, is_primary=False
        )
        self.scan_btn.place(x=self.w - pad - 350, y=btn_y)

        self.flash_btn = TronPillButton(
            self, text="FLASH FIRMWARE",
            command=self._start_flash, width=180, height=38, is_primary=True
        )
        self.flash_btn.place(x=self.w - pad - 195, y=btn_y)

        # Toggle terminal button
        self.term_toggle = tk.Button(
            self, text="[+] TERMINAL TELEMETRY", font=("Consolas", 8),
            bg=BG_VOID, fg=BORDER_DIM, activebackground=BG_VOID, activeforeground=NEON_CYAN,
            bd=0, cursor="hand2", command=self._toggle_terminal
        )
        self.term_toggle.place(x=r_x + 10, y=btn_y + 8)

        # Collapsible Terminal Console (Drawer)
        self.term_frame = tk.Frame(self, bg=BG_INPUT, bd=1, relief=tk.SOLID, highlightthickness=1, highlightbackground=BORDER_DIM)
        self.term_visible = False

        self.log_text = tk.Text(
            self.term_frame, bg=BG_INPUT, fg="#7fa1c4", font=("Consolas", 8),
            insertbackground=NEON_CYAN, selectbackground="#003544",
            relief=tk.FLAT, wrap=tk.WORD, height=6
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        self._log("TRON: Seeder Flash Grid initialized.")
        self._log("I/O Conduit ready. Scanning USB serial devices...")

    def _render_master_background(self):
        """Renders the high-fidelity 3D perspective grid, cyber bezel, and circuit conduits."""
        w, h = self.w, self.h
        im = Image.new("RGBA", (w, h), (2, 5, 12, 255))

        horizon_y = int(h * 0.44)
        cx_disc = 700
        cy_disc = int(h * 0.45)
        pad = 12

        # 1. Atmospheric Glow behind Disc and Horizon
        glow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        gld = ImageDraw.Draw(glow_layer)
        gld.ellipse([cx_disc - 250, cy_disc - 250, cx_disc + 250, cy_disc + 250], fill=(0, 200, 255, 55))
        gld.ellipse([cx_disc - 130, cy_disc - 130, cx_disc + 130, cy_disc + 130], fill=(0, 230, 255, 75))
        gld.ellipse([50, horizon_y - 80, w - 50, horizon_y + 180], fill=(0, 160, 220, 30))
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(45))
        im = Image.alpha_composite(im, glow_layer)

        # 2. 3D Perspective Digital Cyber Grid Lines
        grid_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        grd = ImageDraw.Draw(grid_layer)
        for i in range(1, 18):
            t = (i / 17.0) ** 1.85
            y = int(horizon_y + (h - horizon_y) * t)
            alpha = int(18 + 75 * t)
            grd.line([(0, y), (w, y)], fill=(0, 215, 255, alpha), width=1)

        for i in range(-24, 28):
            bx = (w // 2) + i * (w // 16)
            alpha = max(12, int(75 - abs(i) * 2.2))
            grd.line([(w // 2 + i * 8, horizon_y), (bx, h)], fill=(0, 215, 255, alpha), width=1)

        grid_layer = grid_layer.filter(ImageFilter.GaussianBlur(0.5))
        im = Image.alpha_composite(im, grid_layer)

        # 3. Outer Cyber Bezel with Soft Bloom
        bezel_glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bezel_glow)
        r = 16
        bd.rounded_rectangle([pad, pad, w - pad, h - pad], radius=r, outline=(0, 243, 255, 95), width=6)
        bezel_glow = bezel_glow.filter(ImageFilter.GaussianBlur(4))
        im = Image.alpha_composite(im, bezel_glow)

        bd_crisp = ImageDraw.Draw(im)
        bd_crisp.rounded_rectangle([pad, pad, w - pad, h - pad], radius=r, outline=(0, 243, 255, 255), width=2)
        bd_crisp.rounded_rectangle([pad + 4, pad + 4, w - pad - 4, h - pad - 4], radius=r - 2, outline=(0, 90, 130, 140), width=1)

        # Title Bar Divider Line
        bd_crisp.line([(pad + 12, pad + 44), (w - pad - 12, pad + 44)], fill=(0, 120, 160, 180), width=1)

        # Title Emblem & Typography
        gx = pad + 24
        gy = pad + 14
        # Glowing 'S' Emblem
        bd_crisp.line([(gx, gy + 3), (gx + 18, gy + 3)], fill=(0, 243, 255, 255), width=3)
        bd_crisp.line([(gx, gy + 3), (gx, gy + 11)], fill=(0, 243, 255, 255), width=3)
        bd_crisp.line([(gx, gy + 11), (gx + 18, gy + 11)], fill=(255, 255, 255, 255), width=3)
        bd_crisp.line([(gx + 18, gy + 11), (gx + 18, gy + 19)], fill=(0, 243, 255, 255), width=3)
        bd_crisp.line([(gx, gy + 19), (gx + 18, gy + 19)], fill=(0, 243, 255, 255), width=3)

        try:
            font_title = ImageFont.truetype("segoeuib.ttf", 18)
            font_sub = ImageFont.truetype("consolab.ttf", 9)
        except Exception:
            font_title = font_sub = None

        if font_title:
            bd_crisp.text((gx + 28, gy - 2), "SEEDER FLASHER", fill=(0, 243, 255, 255), font=font_title)
        if font_sub:
            bd_crisp.text((gx + 205, gy + 5), "· THE DIGITAL GRID CONDUIT", fill=(90, 130, 170, 220), font=font_sub)

        # 4. Left Panel Glass Frame
        l_x1, l_y1, l_x2, l_y2 = pad + 18, pad + 56, pad + 18 + 355, h - pad - 22
        lp_glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        lpd = ImageDraw.Draw(lp_glow)
        lpd.rounded_rectangle([l_x1, l_y1, l_x2, l_y2], radius=12, fill=(4, 12, 24, 215), outline=(0, 243, 255, 90), width=4)
        lp_glow = lp_glow.filter(ImageFilter.GaussianBlur(3))
        im = Image.alpha_composite(im, lp_glow)

        lpd_crisp = ImageDraw.Draw(im)
        lpd_crisp.rounded_rectangle([l_x1, l_y1, l_x2, l_y2], radius=12, outline=(0, 243, 255, 230), width=2)
        lpd_crisp.rounded_rectangle([l_x1 + 2, l_y1 + 2, l_x2 - 2, l_y2 - 2], radius=10, outline=(0, 80, 120, 100), width=1)

        # 5. Circuit Conduits Connecting Left Panel and Disc
        circuit_glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ccd = ImageDraw.Draw(circuit_glow)
        r_disc_outer = 155

        routes_left = [
            (cy_disc - 75, l_x2 + 45, cy_disc - 55, cx_disc - r_disc_outer),
            (cy_disc - 38, l_x2 + 65, cy_disc - 28, cx_disc - r_disc_outer - 5),
            (cy_disc,      l_x2 + 85, cy_disc,      cx_disc - r_disc_outer - 10),
            (cy_disc + 38, l_x2 + 65, cy_disc + 28, cx_disc - r_disc_outer - 5),
            (cy_disc + 75, l_x2 + 45, cy_disc + 55, cx_disc - r_disc_outer),
        ]
        for sy, mx, ey, ex in routes_left:
            pts = [(l_x2, sy), (mx, sy), (mx + abs(ey - sy), ey), (ex, ey)]
            ccd.line(pts, fill=(0, 243, 255, 95), width=5)

        routes_right = [
            (cy_disc - 55, cx_disc + r_disc_outer, cy_disc - 75, w - pad - 18),
            (cy_disc,      cx_disc + r_disc_outer + 10, cy_disc, w - pad - 18),
            (cy_disc + 55, cx_disc + r_disc_outer, cy_disc + 75, w - pad - 18),
        ]
        for ey, sx, sy, mx in routes_right:
            pts = [(sx, ey), (sx + 35, ey), (sx + 35 + abs(ey - sy), sy), (mx, sy)]
            ccd.line(pts, fill=(0, 243, 255, 95), width=5)

        circuit_glow = circuit_glow.filter(ImageFilter.GaussianBlur(3))
        im = Image.alpha_composite(im, circuit_glow)

        ccd_crisp = ImageDraw.Draw(im)
        for sy, mx, ey, ex in routes_left:
            pts = [(l_x2, sy), (mx, sy), (mx + abs(ey - sy), ey), (ex, ey)]
            ccd_crisp.line(pts, fill=(0, 243, 255, 240), width=2)
            ccd_crisp.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=(255, 255, 255, 255))

        for ey, sx, sy, mx in routes_right:
            pts = [(sx, ey), (sx + 35, ey), (sx + 35 + abs(ey - sy), sy), (mx, sy)]
            ccd_crisp.line(pts, fill=(0, 243, 255, 240), width=2)
            ccd_crisp.ellipse([sx - 3, ey - 3, sx + 3, ey + 3], fill=(255, 255, 255, 255))

        self._master_bg_photo = ImageTk.PhotoImage(im)
        self.bg_canvas.delete("all")
        self.bg_canvas.create_image(0, 0, image=self._master_bg_photo, anchor="nw")

    def _draw_close_btn(self, hover):
        self.close_btn.delete("all")
        col = NEON_WHITE if hover else NEON_CYAN
        if hover:
            self.close_btn.create_oval(2, 2, 26, 26, fill="#33000a", outline="#ff2255", width=1)
            col = "#ff4466"
        self.close_btn.create_line(8, 8, 20, 20, fill=col, width=2)
        self.close_btn.create_line(8, 20, 20, 8, fill=col, width=2)

    def _draw_max_btn(self, hover):
        self.max_btn.delete("all")
        col = NEON_WHITE if hover else NEON_CYAN
        if hover:
            self.max_btn.create_oval(2, 2, 26, 26, fill="#002233", outline=NEON_CYAN, width=1)
        self.max_btn.create_rectangle(8, 8, 20, 20, outline=col, width=2)

    def _draw_min_btn(self, hover):
        self.min_btn.delete("all")
        col = NEON_WHITE if hover else NEON_CYAN
        if hover:
            self.min_btn.create_oval(2, 2, 26, 26, fill="#002233", outline=NEON_CYAN, width=1)
        self.min_btn.create_line(8, 14, 20, 14, fill=col, width=2)

    def _on_minimize(self, event=None):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            ctypes.windll.user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE
        except Exception:
            self.iconify()

    def _on_canvas_click(self, event):
        # Allow dragging window from title bar area
        if event.y <= 54:
            self._drag_x = event.x
            self._drag_y = event.y

    def _on_canvas_drag(self, event):
        if event.y <= 60:
            deltax = event.x - self._drag_x
            deltay = event.y - self._drag_y
            new_x = self.winfo_x() + deltax
            new_y = self.winfo_y() + deltay
            self.geometry(f"+{new_x}+{new_y}")

    def _log(self, text):
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)

    def _clear_log(self):
        self.log_text.delete("1.0", tk.END)

    def _toggle_terminal(self):
        if self.term_visible:
            self.term_frame.place_forget()
            self.term_toggle.config(text="[+] TERMINAL TELEMETRY", fg=BORDER_DIM)
            self.term_visible = False
        else:
            self.term_frame.place(x=420, y=self.h - 170, width=540, height=110)
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
