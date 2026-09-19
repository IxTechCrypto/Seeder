# SEEDER - Sovereign seed generator

A DIY device that allows you to create your own Bitcoin seeds in a matter of seconds, without depending on anyone or anything to safeguard your funds.

With SEEDER you can perform the **coin seed** process, generate entropy using **dice**, and **effortlessly calculate the final word of your seed (with checksum)**, as well as export it via a QR code.

All of this thanks to the brilliant idea of @Lunaticoin and my implementation.

## ⚡ IxTech Sovereign Edition — Repo Updates & Enhancements

This repository ([`IxTechCrypto/Seeder`](https://github.com/IxTechCrypto/Seeder)) is an enhanced sovereign edition of the original [BitMaker-hub/Seeder](https://github.com/BitMaker-hub/Seeder) firmware, engineered with dual-button power management and auto-sleep, a standalone TRON: Legacy desktop flasher GUI, an ambidextrous interface, an overhauled Bitcoin Orange tactical UI, and hardened memory zeroization.

### 🚀 Major Enhancements in this Repository

* **🔋 Advanced Power Architecture & Deep Sleep (Zero Hardware Mods Required)**:
  * **Dual-Button Power-Off (2.0s Hold)**: Holding both physical buttons (`MOVE` + `OK`) simultaneously from any screen brings up an interactive TRON progress modal (`HOLD TO POWER OFF`) with a live 2.0s countdown. Releasing early cleanly cancels shutdown and suppresses accidental clicks. Holding for 2.0s triggers a retro CRT-collapse animation, puts the ST7789 display controller into low-power sleep (`SLPIN` + `DISPOFF`), isolates the power rails (`PIN_POWER_ON` / backlight = `LOW`), and puts the ESP32 into deep sleep (**~35–50 µA** standby draw).
  * **Pocket-Proof Power-On (1.5s Hold)**: Wakes from deep sleep on either button via `EXT1`. In `setup()`, the firmware verifies whether **both** buttons remain held continuously for **1.5 seconds**. Accidental bumps in a pocket or bag immediately abort back to deep sleep in **< 30 ms** without lighting the screen.
  * **Inactivity Auto-Sleep**: Automatically powers down to deep sleep after **3 minutes** of inactivity to safeguard LiPo battery life.
  * **Instant USB Wake**: Connecting a USB-C power source or pressing the hardware reset button powers on immediately.

* **💻 Standalone TRON: Legacy Desktop Flasher GUI (`SeederFlasher`)**:
  * Bundled standalone desktop GUI (`flasher/` and executable `dist/SeederFlasher.exe`) for effortless, zero-command-line firmware installation.
  * Styled in an authentic TRON: Legacy cyberpunk aesthetic with animated glowing Identity Disc, 3D perspective grid, and high-contrast cyan telemetry cards.
  * **Auto COM Port Detection**: Automatically scans and enumerates plugged-in USB-to-UART controllers (CH340, CP210x, native ESP32-S3 USB CDC).
  * **One-Click Multi-Board Flashing**: Pre-configured flashing engine for both **LilyGO TTGO T-Display (ESP32)** and **LilyGO T-Display-S3 (ESP32-S3)** with automatic chip identification, baud rate selection (up to 921600 baud), and live terminal output logs.

* **🎨 Sovereign Tactical UI & Bitcoin Orange Overhaul**:
  * Overhauled the color palette to Bitcoin Electric Orange (`#F7931A` / `0xFD00`) on deep obsidian black (`#000000`) with elevated card fills and ambient glow halos (`0x9340`).
  * **Floating Glowing Cards**: Modernized menu options into rounded floating cards with double-border glow halos.
  * **Smooth 60 FPS Sliding Animations**: Pressing **MOVE** smoothly translates the vertical orange selection pill between cards (~95ms duration) while seamlessly transitioning card border glow without screen flicker.
  * **Crisp Vector Typography**: Converted blocky 5×7 pixel text to crisp vector sans-serif typography using Adafruit GFX `FreeSansBold 9pt` (`FSSB9`) and `FreeSansBold 12pt` (`FSSB12`).
  * **Modernized High-DPI Iconography**: Enlarged and bolder vector status icons (+35% visual weight) with rounded geometry, strain relief, and 3D isometric dice/coin graphics.
  * **Tactical 3D Branding**: Integrated `ixtech.xyz` glowing banner and tactical security badges.

* **⚡ Real-Time Hardware Battery & USB Status Gauge**:
  * Uses the board's built-in factory resistor divider (`GPIO 4` on T-Display-S3, `GPIO 34` on classic T-Display) along with native USB SOF detection and ripple-filtering.
  * **USB Plug Indicator**: Displayed automatically in the top header whenever the device is powered via USB-C or actively charging.
  * **Segmented Battery Gauge**: When running on battery power alone (unplugged from USB), automatically switches to a 3-segment pill battery gauge with real-time color-coding (Electric Orange $>45\%$, Amber $20-45\%$, Alert Red $\le 20\%$).

* **🔄 Ambidextrous Ergonomics (Left-Handed & Right-Handed Mode)**:
  * Added an interactive boot prompt immediately following the splash screen allowing users to choose between **Right Hand** (default, buttons on right) and **Left Hand** (device rotated 180°, buttons on left).
  * In Left-Handed mode, the display rotates 180° (`setRotation(3)`), and physical buttons are automatically remapped so that the **physical top button is always MOVE** and the **physical bottom button is always OK**.
  * Tactical navigation rails and chevrons dynamically mirror to the left margin in left-handed mode so button indicators remain directly adjacent to the user's thumb.
  * Preserves the strict zero-flash security model: the handedness selection lives purely in RAM for the duration of the session and is prompted fresh on each boot cycle with zero flash writes.

* **🛡️ Hardened Memory & Anti-Remanence Security Architecture**:
  * **Strict Zero-Silicon Entropy**: 100% user-supplied via physical coin flips or Coldcard-compatible dice rolls. The device silicon TRNG/PRNG is never used.
  * **Volatile RAM Only**: Mnemonic phrases, raw entropy, and keys exist exclusively in RAM; NVS and EEPROM persistence are disabled.
  * **Active `memzero` Scrubbing**: Exiting seed screens or holding OK to cancel immediately zeroizes all mnemonic buffers, entropy arrays, key structures, and cryptographic caches.
  * **RF Radio Isolation**: Wi-Fi and Bluetooth hardware controllers are completely uninitialized and kept powered down.
  * **Silent Serial**: UART output disabled in production (`SEEDER_DEBUG=0`).
  * **Coredump & Crash Dump Prevention**: Disabled flash coredump handlers to ensure crash states never persist secret material to SPI flash.

* **🖨️ 3D Printable Tactical Enclosure**:
  * Parametric snap-fit rugged enclosure designs in `3d files/Carcasa_Tactica_v1/` featuring tactile button extensions, USB-C clearance, and lanyard loop.

* **🎬 Launch Video & Social Media Kit**:
  * Includes the `/brag` launch package (`brag-output/`): 1080p demo video (`brag.mp4`), poster frame (`brag.jpg`), storyboard, and ready-to-publish launch copy (`social-posts.md`) for Twitter/X, Facebook, TikTok, and YouTube Shorts.

## 🔒 Core Security Model at a Glance

SEEDER is engineered around a strict **"don't trust, verify"** security architecture:

* **Zero Silicon Entropy (No TRNG / PRNG)**: The device **never** generates random numbers on its own silicon. 100% of the entropy is provided by you via physical coin flips or dice rolls. SEEDER only computes the deterministic BIP-39 math right in front of you.
* **100% Independently Verifiable**: The `Entropy (hex)` screen displays the exact raw bytes used to derive your words. You can cross-check the math offline on an air-gapped machine using `sha256sum` and any independent BIP-39 tool. If the words do not match, discard the device.
* **Volatile RAM Only (Never Written to Flash)**: Your mnemonic, private keys, and entropy exist solely in volatile RAM. No NVS, no EEPROM, no flash writes, and zero persistence across power cycles.
* **Active Memory Scrubbing on Exit**: Leaving the seed screens or holding OK to cancel triggers active `memzero` zeroization across all mnemonic buffers, entropy arrays, key structures, and internal cryptographic caches.
* **RF Radios Uninitialized**: Wi-Fi and Bluetooth controllers are never initialized, started, or configured by the firmware. No networking, no OTA updates, and no radio emissions.
* **Zero Serial Output**: The UART/Serial interface is completely disabled in release builds (`SEEDER_DEBUG=0`). Keys and entropy are never printed or transmitted over USB.
* **Air-Gapped Operation**: Designed to be operated disconnected from computers using a standalone USB power bank or a data-blocked (power-only) cable.

![SEEDER, generates offline seeds](Images/Seeder_cover.jpg)

## SEEDER does not generate entropy

This is what sets v2 apart: **the device does not have a random number generator (RNG)**. You provide the entropy yourself, using a coin or a die, and SEEDER simply performs the BIP39 math right in front of you.

And you can verify that math independently on your own machine. SEEDER displays the entropy in hexadecimal on the `Entropy (hex)` screen. Using that hex value and any offline BIP39 tool, you obtain the exact same words. If they do not match, discard the device.

| Mode | Input | Entropy |
|---|---|---|
| Coin | 128 flips (12 words) / 256 flips (24 words) | Raw bits, as-is, without passing through any hash |
| Dice | 50 rolls (12 words) / 99 rolls (24 words) | `SHA-256` of the ASCII digits |

The dice mode uses the exact same scheme as Coldcard, so you can verify it directly from a terminal:

```bash
printf '3141592653...' | sha256sum
```

For 24 words, all 32 bytes of the hash are used; for 12 words, only the **first 16 bytes** (the first 32 hex characters) are used. This is identical to Coldcard's methodology.

And coin mode does not apply any hashing: the bits you flip **are** the entropy. This also allows you to input pre-existing entropy and let SEEDER compute the final word along with its checksum.

## Requirements

Either of the two supported boards:

| Board | Display | Binary |
|---|---|---|
| LilyGO TTGO T-Display (ESP32) | 240x135 | `seeder-tdisplay-merged.bin` |
| LilyGO T-Display-S3 (ESP32-S3) | 320x170 | `seeder-tdisplay-s3-merged.bin` |

Along with a USB-C cable.

Optionally, it accepts a LiPo battery via the JST connector. The board does not include a physical power switch, but **it can be powered down via firmware**: how to do this, and what to expect regarding standby power consumption, is detailed in [HARDWARE.md](HARDWARE.md).

## Installation

Everything is available in the [latest release](https://github.com/BitMaker-hub/Seeder/releases).
There are two paths: convenient, or fully verifiable. Choose based on your risk tolerance.

### Quick route — via browser

Download `seeder-firmware-merged.bin` (or the board-specific merged binary) and flash it using [esptool-js](https://espressif.github.io/esptool-js/) at offset **0x0**.
A single file, nothing to install.

> Convenient, but you are trusting that the web page served you the correct binary.
> For an actual production seed holding real funds, perform the terminal verification below as well.

### Manual route — via terminal, fully verifiable

Download the complete release, including `SHA256SUMS`, and verify that what you downloaded matches what CI published:

```bash
sha256sum -c SHA256SUMS
```

Flash:

```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x0 seeder-tdisplay-merged.bin
```

And verify that the chip flash genuinely matches that binary:

```bash
esptool.py --port /dev/ttyUSB0 --no-stub verify_flash 0x0 seeder-tdisplay-merged.bin
```

On Windows, the port will be `COM3` or similar. That last step is what matters most and is explained in [SECURITY.md](SECURITY.md): with `--no-stub`, the SEEDER application code does not even execute—the ESP32 mask-ROM bootloader responds directly, meaning a compromised firmware cannot spoof flash verification.

## Building from source

Using PlatformIO:

```bash
# For LilyGO TTGO T-Display (ESP32)
pio run -e tdisplay

# For LilyGO T-Display-S3 (ESP32-S3)
pio run -e tdisplay-s3
```

The libraries (`uBitcoin`, `TFT_eSPI`) are vendored inside `lib/` by design: a seed generator must compile identically today or five years from now without breaking upstream dependencies.

## Controls

Two buttons and nothing more. **MOVE** is the top button, and **OK** is the bottom button.

| Context | MOVE | OK |
|---|---|---|
| Handedness / orientation selection | Toggle Right / Left hand | Confirm selection |
| Menu & word count selection | Change selection | Confirm selection |
| Flipping coin | Heads (1) | Tails (0) |
| Rolling dice | Cycle 1 → 6 | Confirm roll |
| Reading seed | Next page | Previous page |
| Last page (`Exit`) | Return to first page | Hold to exit and wipe memory |

During input capture, **holding OK for 3 seconds returns to the menu** and clears all captured entropy: if you made a mistake on roll 40 of 99, you do not need to unplug the device. At ~1.2s, a progress bar appears; releasing before it fills will not record an inadvertent flip or roll.


## Verification

Do not blindly trust SEEDER: verify it. The `Entropy (hex)` screen shows you the exact raw bytes that generated your words. Using that hex value and any **offline** BIP39 tool, you can recompute the seed words. If they do not match, do not use the device.

Always do this with **your own entropy**, not with published test vectors: malicious firmware could recognize hardcoded test inputs and behave honestly only during testing.

For the complete threat model and limitations, see [SECURITY.md](SECURITY.md).

> The seed never leaves the device and is never written to flash: it only resides in volatile RAM and disappears upon disconnection. The firmware outputs nothing over the serial UART.

## TUTORIAL

Complete video tutorial on YouTube:

[![Watch video here](https://img.youtube.com/vi/2K7ztWxtyY8/0.jpg)](https://youtu.be/2K7ztWxtyY8)
