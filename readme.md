# SEEDER - Sovereign seed generator

A DIY device that allows you to create your own Bitcoin seeds in a matter of seconds, without depending on anyone or anything to safeguard your funds.

With SEEDER you can perform the **coin seed** process, generate entropy using **dice**, and **effortlessly calculate the final word of your seed (with checksum)**, as well as export it via a QR code.

All of this thanks to the brilliant idea of @Lunaticoin and my implementation.

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
