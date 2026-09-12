# Upstream Security & Remanence Issues Report

This document outlines the security vulnerabilities, memory remanence gaps, and documentation discrepancies identified and patched in this fork. These write-ups can be submitted directly as GitHub Issues or Pull Requests to the upstream [BitMaker-hub/Seeder](https://github.com/BitMaker-hub/Seeder) repository.

---

## Issue 1: [HIGH] Core dump to flash enabled by default allows extracting mnemonic after a crash via UART

### Summary
The default partition tables used in PlatformIO (`esp32dev` and `lilygo-t-display-s3`) include a 64 KB `coredump` partition. In addition, Arduino-ESP32's precompiled libraries enable `CONFIG_ESP_COREDUMP_ENABLE_TO_FLASH=1`. If a hardware or software panic occurs while a seed is on-screen (e.g. brownout on battery, watchdog timeout, abort), ESP-IDF's panic handler dumps the task's stack and CPU registers to flash. 

Because UART download mode is intentionally enabled for `verify_flash`, an attacker with physical access to the device can dump this partition over USB using `esptool.py` and extract the seed, directly breaking the *"Volatile RAM Only (Never Written to Flash)"* guarantee.

### Technical Evidence
* **Partition Tables:**
  * LilyGO T-Display-S3 (`default_16MB.csv`): 64 KB `coredump` partition at `0xFF0000` (type 0x01, subtype 0x03).
  * TTGO T-Display (`default.csv`): 64 KB `coredump` partition at `0x3F0000` (type 0x01, subtype 0x03).
* **Linker Map (`firmware.map`):**
  * Links `libespcoredump.a(core_dump_flash.c.obj)` with symbols `esp_core_dump_to_flash`, `esp_core_dump_init`.
* **Exploitability:**
  ```bash
  esptool.py --port COM3 read_flash 0xFF0000 0x10000 dump.bin
  strings dump.bin
  ```

### Proposed Fix
1. Provide custom partition tables (`partitions_tdisplay.csv` and `partitions_tdisplay_s3.csv`) that completely remove the `coredump` partition.
2. In `platformio.ini`, explicitly set `board_build.partitions`.
3. In `src/main.cpp`, invoke `esp_core_dump_image_erase()` during `setup()` to actively wipe any stale coredump partition residue from older flashes.

---

## Issue 2: [HIGH] Stack residue in vendored `uBitcoin` leaves master key and parent private keys unscrubbed

### Summary
`wipeSeed()` in `src/workflow.cpp` clears `.bss` global variables, but derivation occurs on the stack. In the vendored `lib/uBitcoin`, temporary HMAC buffers and parent private key buffers are never zeroized upon return. During the 3 hardened derivation steps (`m/84'/0'/0'/`), parent private keys and child tweaks remain in stack memory until accidentally overwritten.

### Technical Evidence
1. **Master Key / Chaincode in `fromSeed()` (`HDWallet.cpp:244`):**
   `uint8_t raw[64]` receives the 512-bit HMAC output (master private key `num` + master chaincode `chainCode`). It is returned without calling `memzero(raw, sizeof(raw))`.
2. **Hardened Derivation in `child()` (`HDWallet.cpp:442, 451`):**
   `uint8_t data[37]` holds `0x00` + parent secret (32 bytes) + index (4 bytes).
   `uint8_t raw[64]` holds child HMAC output.
   While line 464 calls `memzero(secret, 32);`, neither `data` nor `raw` is wiped before returning.
3. **HMAC Contexts (`Hash.h`):**
   `SHA256` and `SHA512` classes contain `HMAC_SHA256_CTX` / `HMAC_SHA512_CTX` members without destructors, leaving key/pad material on the stack frame when local hash objects go out of scope.

### Proposed Fix
1. Add `memzero(raw, sizeof(raw))` in `HDPrivateKey::fromSeed()`.
2. Add `memzero(data, sizeof(data))` and `memzero(raw, sizeof(raw))` in `HDPrivateKey::child()`.
3. Add virtual destructors `~SHA256()` and `~SHA512()` in `Hash.h` to call `memzero(&ctx, sizeof(ctx))`.
4. Implement a `paintStack()` helper in `workflow.cpp` to overwrite 3 KB of stack depth during `wipeSeed()`.

---

## Issue 3: [HIGH] Heap fragmentation and unscrubbed word copies from Arduino `String` allocations

### Summary
`sWallet` stores `mnemonic`, `entropyHex`, `xpub`, and `firstAddress` as Arduino dynamic `String` objects. Furthermore, `ui::mnemonic()` calls `mn.substring(start, sp)` in a loop across each displayed word on every page redraw.

Because Arduino's `String` allocates from dynamic heap memory and its destructor only calls `free()` without scrubbing the underlying buffer, dozens of unscrubbed plaintext seed words accumulate in heap DRAM. `wipeSeed()`'s `wipeString()` only clears the current buffer, missing all previously allocated and freed heap chunks.

### Technical Evidence
* In `src/ui/ui.cpp:649`:
  ```cpp
  const String w = (sp < 0) ? mn.substring(start) : mn.substring(start, sp);
  ```
  Allocates 12 heap `String`s per render.
* Similar allocations occur in `seedEntropy`, `seedAddress`, and `seedZpub`.

### Proposed Fix
1. Convert `sWallet` members (`mnemonic`, `entropyHex`, `xpub`, `firstAddress`) into fixed `.bss` character arrays (e.g. `char mnemonic[240]`, `char firstAddress[96]`).
2. Update UI render functions (`ui::mnemonic`, `ui::seedAddress`, etc.) to take `const char*` and use stack-bounded slicing with pointer offsets instead of `String.substring()`.
3. Scrub temporary stack buffers before exiting UI functions.
4. Update `wipeSeed()` to zero fixed arrays with deterministic `memzero()` calls.

---

## Issue 4: [MEDIUM] `esp_wifi_stop()` and `esp_bt_controller_disable()` in `setup()` are no-ops and documentation claims register-level shutdown

### Summary
[`src/main.cpp:16-17`](file:///d:/github/Seeder/src/main.cpp#L16-L17) calls:
```cpp
esp_wifi_stop();
esp_bt_controller_disable();
```
Because neither radio subsystem was ever initialized, `esp_wifi_stop()` returns `ESP_ERR_WIFI_NOT_INIT` (0x3001) and `esp_bt_controller_disable()` returns `ESP_ERR_INVALID_STATE` (0x103). Neither function performs any hardware register manipulation or power-down of the PHY.

Meanwhile, `readme.md` claims:
> *"RF Radios Permanently Disabled: Wi-Fi and Bluetooth basebands are explicitly powered off at the hardware register level during boot (`esp_wifi_stop()`, `esp_bt_controller_disable()`)"*

This overstates firmware security guarantees. While the radios are indeed inactive because they are never started, the driver code is still compiled in by the Arduino framework (pulled in by `libesp_event` and `esp32-hal-misc.c`).

### Proposed Fix
1. Remove the dead calls from `src/main.cpp`.
2. Update the README bullet to accurately state:
   *"RF Radios Uninitialized: Wi-Fi and Bluetooth controllers are never initialized, started, or configured by the firmware. No networking, no OTA updates, and no radio emissions."*
   This aligns the README with the honest assessment already present in `SECURITY.md`.

---

## Issue 5: [LOW / BUG] Native Segwit address generation fails when buffer length < 76 bytes

### Summary
In `lib/uBitcoin/src/Bitcoin.cpp:336`, `PublicKey::segwitAddress()` contains a guard:
```cpp
if (len < 76) {
    return 0;
}
```
If a caller passes a buffer smaller than 76 bytes (even though a native SegWit `bc1q...` address is only 42–44 characters), `uBitcoin` zeroes the destination buffer and returns 0. Any struct holding `firstAddress` with a capacity under 76 bytes will silently receive an empty string.

### Proposed Fix
Ensure all `firstAddress` destination buffers provide at least 76 (recommended: 96 or 128) bytes of capacity.
