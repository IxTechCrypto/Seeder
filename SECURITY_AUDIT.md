# SEEDER — Security Audit

**Scope:** full source audit of `src/`, vendored `lib/uBitcoin/`, `platformio.ini`,
`.github/workflows/build.yml`, the linked artifacts in `.pio/build/tdisplay-s3/`
(`firmware.map`, `partitions.bin`), and the security claims in `readme.md`,
`SECURITY.md`, `HARDWARE.md`, `TESTVECTORS.md`.

**Threat model assumed:** the user wants an air-gapped BIP-39 seed generator whose
headline guarantees are (a) no device-generated entropy, (b) the seed never touches
flash, (c) the seed is scrubbed from RAM on exit, (d) no radio, (e) no serial output.

**Verdict:** the *cryptographic core is correct* and the entropy model is sound. The
gaps are all in **remanence and in the gap between the README's "at a glance" claims
and what the firmware actually does**. Two findings (H-1, H-2/H-3 together) form a
realistic chain by which seed material can end up readable off a powered-down device.

---

## What checks out

Verified, not assumed:

- **BIP-39 math is correct.** All four vectors in `TESTVECTORS.md` were reproduced
  independently: `sha256('1'*50)` and `sha256('1'*99)` match, and re-deriving the
  words from the entropy with an independent BIP-39 implementation yields the exact
  published mnemonics for all four cases (12/24-word coin all-zero, 12/24-word dice).
- **The vendored wordlist is authentic.** `lib/uBitcoin/src/utility/trezor/bip39_english.h`
  contains 2048 words whose SHA-256 equals the official BIP-39 `english.txt`
  (`2f5eed53…24dbda`). No substituted or reordered word.
- **No RNG anywhere.** No `random()`, `esp_random()`, or `rand()` in `src/`. The
  "zero silicon entropy" claim holds.
- **Dice scheme is Coldcard-compatible** — `sha256` over the ASCII digits, first 16
  bytes for 12 words, all 32 for 24 (`btc.cpp:13`, `createSeed`).
- **No buffer overflows found in the seed path.** `createSeed` validates
  `len % 4 || len < 16 || len > 32`; coin bits are OR'd (never added) and cannot
  exceed `entropy[32]` because `maxBits ≤ 256` and the state changes at completion;
  `diceRolls[99+1]` cannot be overrun. QR buffers are sized for worst-case version 11
  while initialising at ≤ v9, and `qrcode_initBytes` independently rejects
  over-capacity data — the 24-word worst case is 215 chars against v9's 230-byte
  capacity.
- **Button handling is genuinely careful.** `LongClick` suppresses the click on
  release (`gpio.cpp:117,129`), so releasing part-way through the START-OVER warning
  cannot inject a coin flip or a dice roll the user had already decided to discard.
- **`USE_BIP39_CACHE=0` / `USE_BIP32_CACHE=0` are correctly applied** — confirmed
  against `lib/uBitcoin/src/utility/trezor/options.h`, which defaults both to 1.
  The BIP-39 seed cache is compiled out.
- **uBitcoin's key destructors do scrub.** `HDPrivateKey::~HDPrivateKey` and
  `PrivateKey::~PrivateKey` memzero `num` and `chainCode`. `SECURITY.md`'s claim
  about this is accurate.
- **`mnemonic_clear()` is called from `wipeSeed()`**, clearing the `mnemo[240]`
  static in `bip39.c` — the one library static the application can reach.
- **`SEEDER_DEBUG=0`** compiles `DBGLN` to `do{}while(0)`; even at debug level
  nothing prints the mnemonic or entropy.

---

## H-1 — Core dump to flash is enabled. A crash can write the seed to flash. (HIGH)

The single most serious finding, because it contradicts the headline guarantee:
*"Volatile RAM Only (Never Written to Flash) … no flash writes, and zero persistence
across power cycles."*

**Evidence (from the build outputs in `.pio/build/tdisplay-s3/`):**

- `partitions.bin` contains a **`coredump` partition, type 1 / subtype 0x03, at
  offset `0xFF0000`, 64 KB**.
- `firmware.map` links `core_dump_flash.c.obj` (99 references),
  `esp_core_dump_to_flash`, `esp_core_dump_init`, `esp_core_dump_image_erase`.
  `libespcoredump.a` contributes ~13 KB to the flashed image.
- `core_dump_uart.c.obj` is **not** linked — i.e. the build is configured for
  core-dump-**to-flash**, not to UART, not disabled.

**Mechanism.** On any panic — `abort()`, a load/store prohibited exception, an
interrupt watchdog, a task watchdog, a stack overflow — ESP-IDF's panic handler
writes the crashing task's stack and register set into that partition before
resetting. At the moment a seed is on screen, the `loopTask` stack is exactly where
the mnemonic lives: the QR encoder's VLAs in `ui::seedQr`, the `substring()`
temporaries in `ui::mnemonic`, and the derivation residue in H-2. A core dump is
written through the SPI flash driver and **survives the power cycle**.

**Why it is reachable off-device.** `SECURITY.md` states, correctly and
deliberately, that UART download mode is left enabled so users can run
`verify_flash`. The same access reads the dump back:

```
esptool.py --port COM3 read_flash 0xFF0000 0x10000 dump.bin
strings dump.bin
```

So the exposure is not theoretical: anyone who later gets the device — a buyer of a
resold unit, a border search, a thief — can read whatever the last panic captured.

**Plausibility of a panic while the seed is displayed.** Non-trivial. The seed
screens run the heaviest code in the firmware (QR encoding with stack VLAs, full-screen
redraws), the device is explicitly designed to run on a LiPo without a power switch,
and battery sag triggers brownout and watchdog paths. A user is also *encouraged* to
sit on the seed screens for minutes while copying 24 words by hand.

**Recommended fixes, strongest first:**

1. Ship a **custom partition CSV with no `coredump` partition** (`board_build.partitions`
   in `platformio.ini`). Without the partition the dump has nowhere to go.
2. **Erase the coredump region at boot** regardless — `esp_core_dump_image_erase()`
   early in `setup()` — so an image flashed over a device that already has a dump
   does not inherit one.
3. For provisioned units, move to an ESP-IDF build where
   `CONFIG_ESP_COREDUMP_ENABLE=n` compiles the whole thing out.

**Acceptance test:** build a variant that deliberately panics on the seed screen,
then `read_flash 0xFF0000 0x10000` and grep for the mnemonic words. Repeat after
the fix and confirm the region is `0xFF`.

---

## H-2 — Private key and seed material left on the stack after derivation (HIGH)

`readme.md` claims: *"Leaving the seed screens or holding OK to cancel triggers
active `memzero` zeroization across all mnemonic buffers, entropy arrays, key
structures, and internal cryptographic caches."*

`wipeSeed()` (`workflow.cpp:39`) clears the four `String`s, `entropy[]`,
`diceRolls[]`, `rollHist[]`, and `mnemo[]`. Every one of those is a global in `.bss`.
**It clears nothing on the stack**, and the stack is where the derivation happens:

| Location | Residue | Cleared? |
|---|---|---|
| `HDWallet.cpp:244` `HDPrivateKey::fromSeed` | `uint8_t raw[64]` = **master private key ‖ chain code** | **No** |
| `HDWallet.cpp:~441` `HDPrivateKey::child` | `uint8_t data[37]` = **the parent private key** on every hardened step | **No** |
| `HDWallet.cpp:~451` `HDPrivateKey::child` | `uint8_t raw[64]` = child tweak ‖ chain code | **No** |
| `Hash.h:125` `SHA512` | `HMAC_SHA512_CTX ctx` keyed with the **mnemonic** (`fromMnemonic`) and with the **chain code** (`child`) — no destructor, no memzero | **No** |
| `ui.cpp:721` `seedQr` | `buf[qrcode_getBufferSize(11)]` + qrcoded.c's `codewordBytes[]`, `isFunctionGridBytes[]` = **the full mnemonic, encoded** | **No** |

The derivation path `m/84'/0'/0'` is three hardened steps, so `data[1..32]` receives a
private key three times over. `secret[32]` at the end of `child()` *is* memzero'd,
which shows the intent was there — the surrounding buffers were just missed.

This material persists in DRAM until unrelated activity happens to overwrite it, and
`wipeSeed()` gives the user an explicit, false assurance that it is gone. **It is
also precisely what H-1 captures into flash.**

**Fix.** The libraries are vendored specifically so they can be patched — do it:

- `memzero(raw, sizeof(raw))` at the end of `fromSeed` and `child`;
  `memzero(data, sizeof(data))` at the end of `child`.
- Add `~SHA512()`/`~SHA256()` destructors that `memzero(&ctx, sizeof(ctx))`.
- `memzero(buf, sizeof(buf))` at the end of `seedQr` and `seedZpub`.
- Additionally, have `wipeSeed()` **paint the stack**: take the address of a local,
  walk down 8–16 KB toward the task stack base, and zero it. This catches residue
  from compiler temporaries and register spills that no targeted `memzero` reaches.

---

## H-3 — `String` is the wrong container for a mnemonic; freed heap copies are never zeroed (HIGH)

`myWallet.mnemonic`, `entropyHex`, `xpub` and `firstAddress` are Arduino `String`.
`wipeString()` (`workflow.cpp:31`) zeroes the buffer a `String` is *currently*
holding. Every intermediate `String` is freed **without** being zeroed:

- **`ui::mnemonic()` allocates one heap `String` per word** — `mn.substring(start, sp)`
  inside the render loop — **every time the page is drawn**. Twelve heap blocks, each
  containing one seed word, freed on scope exit without scrubbing. Page back and forth
  through the seed a few times while copying it down and the heap accumulates dozens of
  such blocks.
- **`ui::seedEntropy()`** does `hex.substring(i*2, i*2+2)` per byte — same pattern.
- **`ui::seedAddress()`** and **`seedZpub()`** do the same with `substring()`.
- **`createSeed()`**: `String mn = mnemonicFromEntropy(...)` then `myWallet.mnemonic = mn`.
  If the target's capacity is insufficient, `String::operator=` reallocates and frees
  a buffer containing the full mnemonic. The explicit wipe at `btc.cpp:40` covers `mn`
  but not any buffer already freed by that assignment.
- **`account.xpub()`** and **`.address()`** build their results by concatenation;
  each growth step reallocates and frees the previous contents.

**Net effect: after `wipeSeed()` returns, the heap still contains multiple readable
copies of the seed words.** This is the second direct contradiction of the "active
memory scrubbing" claim, and unlike H-2 it is trivially demonstrable.

**Fix.** Hold the mnemonic as a fixed `static char mnemonic[24*10]` in `.bss` and
render from it with pointer + length — no `substring()` in a render path that touches
seed data. Where a `String` API is unavoidable, reuse one stack buffer per call and
`memzero` it before returning.

**Acceptance test for H-2 and H-3 together:** add a debug-only command that, after
`wipeSeed()`, scans all of DRAM for the first word of the just-wiped mnemonic and
reports the hit count. Target: zero. That single test is the honest measure of the
README's scrubbing claim, and it should be in CI as a QEMU or on-device check before
that claim is made again.

---

## M-1 — The radios are not "powered off at the hardware register level" (MEDIUM — claim accuracy)

`main.cpp:16-17`:

```cpp
esp_wifi_stop();
esp_bt_controller_disable();
```

Both are **no-ops here, and their return values are discarded.** `esp_wifi_stop()`
returns `ESP_ERR_WIFI_NOT_INIT` when WiFi was never initialised; `esp_bt_controller_disable()`
returns `ESP_ERR_INVALID_STATE` when the controller is not enabled. Neither touches
the PHY, and neither performs the "hardware register level" power-down the README
describes. The radios are off — but because they are *never started*, which is the
better reason, not the one the code claims.

Measured from `firmware.map`, the flashed image nonetheless contains **~70 KB of
radio code**: `libnet80211.a` 46.7 KB, `libpp.a` 15.8 KB, `libphy.a` 4.9 KB,
`libcoexist.a` 1.3 KB, plus `libbt.a`/`libbtdm_app.a`/`libesp_wifi.a`/`libesp_phy.a`.

**Traced honestly:** this is **not** caused by the two calls in `main.cpp`.
The map's archive-inclusion table shows `libesp_wifi.a(wifi_init.c.obj)` pulled in by
`libesp_event.a(default_event_loop.c.obj)` referencing `WIFI_EVENT`, and
`libbt.a(bt.c.obj)` pulled in by `libFrameworkArduino.a(esp32-hal-misc.c.o)`
referencing `esp_bt_controller_mem_release`. **Deleting the two calls will not remove
the radio stacks** — the Arduino framework links them regardless. Removing the calls
is still worth doing, because they are dead code that asserts a guarantee they do not
provide.

**What to fix is the documentation.** `SECURITY.md` is already honest — it lists
"a tampered firmware that leaks over WiFi or BLE" as an uncovered risk and says the
only real defence is building and flashing it yourself. The README's *"RF Radios
Permanently Disabled … explicitly powered off at the hardware register level during
boot"* overstates what `SECURITY.md` carefully states, in the section a reader skims
first. Bring the README in line: *never initialised; the radio driver code is present
in the image because of the Arduino framework; the only real defence is building it
yourself.*

If a genuine hardware action is wanted, the real fix is an ESP-IDF build with WiFi
and Bluetooth excluded from the component list — which also removes the 70 KB.

---

## M-2 — ESP32-S3: USB-Serial-JTAG exposes a debug port over the power connector (MEDIUM)

`HWCDC` appears 293× in `firmware.map` — USB CDC-on-boot is active on the S3 build,
and `gpio.cpp:143` includes `hal/usb_serial_jtag_ll.h` and reads the SOF register for
the battery indicator, so the USB-Serial-JTAG peripheral is live by design.

On the ESP32-S3 that peripheral also presents a **JTAG debug access port to the USB
host** unless the `DIS_USB_JTAG` eFuse is burned. A host with OpenOCD can halt the
CPU and read RAM — including a displayed mnemonic — with no firmware cooperation, so
"Zero Serial Output" does not cover it.

The realistic path: a user powers the device from their laptop with the same USB-C
cable they flashed it with, which is the most natural thing to do. `readme.md`
recommends a power bank or a data-blocked cable in the body text, but the **"Core
Security Model at a Glance"** bullet says "Air-Gapped Operation" without that caveat.

**Fix:** promote the power-only-cable requirement into the at-a-glance list as a
hard requirement, not a suggestion. For provisioned units, evaluate burning
`DIS_USB_JTAG` — confirm first that it does not affect UART download mode, so it does
not conflict with the deliberate `verify_flash` recovery policy.

---

## M-3 — No sanity check on coin-mode entropy (MEDIUM)

Coin mode uses the raw bits with no hashing. That is a deliberate and defensible
design choice — it is what lets a user enter pre-existing entropy and have SEEDER
compute the checksum word — but it means a degenerate input becomes a degenerate seed
with **no warning at all**. 128 taps of the OK button produces
`abandon … about`, a seed whose funds are swept by bots within seconds of receiving
them. `TESTVECTORS.md` invites the user to do exactly that keystroke sequence, and the
device gives the same confident UI for it as for a real seed. Dice mode is protected
by the SHA-256; this is coin-only.

The device cannot judge randomness, but it can cheaply refuse the obvious:

- Flag all-zero, all-ones, and strict alternation.
- Flag an extreme bit balance — e.g. fewer than 40 or more than 88 ones out of 128
  is roughly 4σ and will essentially never occur with a fair coin.

Make it a non-blocking **`WEAK ENTROPY`** banner on the seed screen rather than a hard
refusal, so the published test vectors still work and the "device does not overrule
you" philosophy is preserved.

---

## Low / informational

**L-1 — Buttons configured without pull-ups.** `gpio.cpp:80,84` use `pinMode(pin, INPUT)`.
Both supported boards have external pull-ups so this works, but a floating input would
produce phantom coin flips *indistinguishable from real ones*. Use `INPUT_PULLUP` where
the pin allows; GPIO35 on the classic T-Display is input-only and cannot, so document
that it depends on the board's external pull-up.

**L-2 — Simultaneous press silently swallows a bit.** `doCoinSeed` (`workflow.cpp:179-187`)
reads both buttons; if both report `SingleClick` in one iteration only one bit is
recorded (`coin = (mv == SingleClick) ? 1 : 0`). Not a randomness defect — the
bits-left counter is authoritative and on screen — but worth a comment so a future
refactor does not turn it into one.

**L-3 — Dead crypto code with an unscrubbed static.** `mnemonic_to_seed()` and its
`static CONFIDENTIAL PBKDF2_HMAC_SHA512_CTX pctx` (`bip39.c:188,208`) are linked
(`.text.mnemonic_to_seed`, `.bss.pctx$2705` in the map) although SEEDER derives the
seed through uBitcoin's own PBKDF2 loop in `HDPrivateKey::fromMnemonic`. Unreached
today, so `pctx` is never populated. But that struct holds `f[8]` — **the derived
BIP-39 seed itself** — plus `idig`/`odig` keyed with the mnemonic, it is **never
zeroized**, and `wipeSeed()` does not know it exists. Any future change that routes
through `mnemonic_to_seed` silently creates a permanent copy of the seed in `.bss`.
Delete it from the vendored copy, or add `memzero(&pctx, sizeof(pctx))` after
`pbkdf2_hmac_sha512_Final`.

**L-4 — Latent overflow in vendored `mnemonic_to_entropy`.** `bip39.c` ends with
`memcpy(entropy, bits, sizeof(bits))` — 33 bytes into a caller-supplied buffer with no
length parameter. Safe as called (`mnemonicToEntropy` passes `uint8_t res[33]`) and
SEEDER never calls it, but it is a trap for any future caller. Vendored-code hygiene.

**L-5 — Documentation drift in `HARDWARE.md`.** It states the GPIO34 battery divider
"no lo usamos", but `gpio.cpp` now reads it (`PIN_BAT_ADC 34`). More importantly, its
`PWR_EN = GPIO14` power-off snippet applies to the **classic T-Display only** — on the
T-Display-S3, GPIO14 is the MOVE button (`boards/tdisplay_s3.h:217`). Add an explicit
board banner so nobody copies that snippet onto an S3.

**L-6 — Stale prebuilt binary in the working tree.** `seeder-tdisplay-s3-merged.bin`
(554 KB, 2026-09-11) sits in the repo root. It is **untracked** — `.gitignore` has
`*.bin` and `git ls-files` returns nothing — so it will not ship. Keep it that way: a
binary in the repo that CI did not produce is exactly the artifact a user would flash
without checking `SHA256SUMS`.

**L-7 — NVS is present in the image.** `libnvs_flash.a` contributes ~10 KB and the
partition table has a 20 KB `nvs` partition, which Arduino's `initArduino()`
initialises at boot. The device therefore does write to flash — NVS metadata, never
seed material. `SECURITY.md`'s "no hay NVS" is true of SEEDER's own code, not of the
image. A precision issue in a document whose whole value is precision.

**L-8 — Emissions, stated rather than silent.** The S3 drives its panel over an 8-bit
parallel bus, which radiates considerably more than the classic board's SPI, and it
does so while rendering the mnemonic. `SECURITY.md` declares side channels out of
scope and no practical attack is being claimed here — but given that the document's
physical guidance is "generate somewhere without cameras", one sentence noting that
the two boards are not equivalent on this axis is more honest than silence.

---

## Priority

1. **H-1** — remove the coredump partition and erase the region at boot. Highest
   severity/effort ratio in the whole list: a partition-table change.
2. **H-3** — get `String` out of the mnemonic path. Most demonstrable contradiction
   of the README.
3. **H-2** — patch the vendored uBitcoin `memzero`s, add hash-context destructors,
   paint the stack in `wipeSeed()`.
4. **M-1, M-2** — correct the README's "at a glance" claims so they match what
   `SECURITY.md` already says honestly, and promote the power-only-cable requirement.
5. **M-3** — weak-entropy banner for coin mode.
6. Lows as convenient.

**Before re-publishing the "Active Memory Scrubbing" and "Never Written to Flash"
bullets, put the DRAM-scan and post-panic flash-read tests in CI.** Right now those
two bullets are the strongest claims in the README and the two that the code does not
support.
