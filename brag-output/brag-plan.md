# Brag Plan: SEEDER

## What is this app?
SEEDER is an open-source, DIY sovereign Bitcoin seed generator on LilyGO ESP32 hardware that computes deterministic BIP-39 seeds with zero silicon entropy—relying 100% on physical coin flips and dice rolls.

## The angle
Cyberpunk sovereign hardware trailer. Most hardware wallets force you to trust black-box silicon RNGs. SEEDER flips the premise: zero random number generation on chip. You roll the dice, you flip the coin, SEEDER runs the math right in front of you—and if the raw hex entropy doesn't match offline SHA-256 calculation, you discard the device.

## Hook (first 2-3 seconds)
Obsidian black screen slams into glowing electric Bitcoin orange typography:
"NEVER TRUST SILICON TO GENERATE YOUR KEYS."
Backed by an ominous electronic swell and a crisp dice-shake sound effect.

## Key moments (the middle)
- **Zero Silicon Entropy**: Cut to real hardware shot (`Images/Seeder_cover.jpg`) with dice & coins, highlighting "100% Physical Entropy. No TRNG. No PRNG."
- **Sovereign Tactical UI**: Showcase the animated glowing cards ("DICE SEED", "COIN SEED", "12 WORDS", "24 WORDS") with smooth 60 FPS selection pill and air-gapped security badge.
- **Don't Trust, Verify**: Raw hexadecimal entropy displayed on screen. Re-verify offline on any terminal with `printf | sha256sum`.
- **Volatile RAM Only**: Active `memzero` memory scrubbing on power-down, zero RF emissions (WiFi/BLE uninitialized), zero flash writes.

## Outro / punchline
"SEEDER. Sovereign seed generation. Don't trust. Roll the dice."
Electric orange logo reveal, URL and GitHub repository link, clean beat cutoff.

## User flow worth showing
1. **Entry**: Boot into Sovereign Tactical UI → Select Dice Seed (50 or 99 rolls) or Coin Seed (128 or 256 flips).
2. **Key Action**: Physical entropy input with immediate visual feedback & real-time battery/power status.
3. **Result**: Raw entropy hex verified on screen → 12/24 BIP-39 mnemonic generated → Memory scrubbed to zero.

## Tone
- Preset: `cinematic`
- Creative direction: Cyberpunk sovereign hardware trailer
- Interpretation: Obsidian black, electric orange glow, confident declarative statements, tactical typography, and physical audio cues (dice & clicks).

## Format: landscape — 1920x1080
## Duration: 20 seconds

## Visual identity (from the project)
- Background: `#0A0D10` (Deep obsidian dark)
- Accent: `#F7931A` (Bitcoin Electric Orange) & `#FFB347` (Glow Amber)
- Secondary Accent: `#10B981` (Air-Gapped Shield Green)
- Text: `#FFFFFF` and `#E2E8F0`
- Display font: `system-ui, -apple-system, sans-serif`
- Body font: `ui-monospace, monospace` for cryptographic hex & terminal verification
- Strongest visual elements: Real hardware device photography, floating glowing double-border tactical cards, status badges.

## Share copy (draft)
Never trust silicon to generate your private keys. SEEDER turns physical dice rolls and coin flips into verifiable Bitcoin seeds on air-gapped DIY hardware.

## Audio direction
- Role: Cinematic electronic support with tactile physical accents
- Music: `happy-beats-business-moves-vol-10-by-ende-dot-app.mp3`
- Music treatment: Starts at 0.0s, steady energetic posture, smooth fade out from 18.5s to 20.0s under the final logo.
- Music cue guidance:
  - 0.00s - 0.30s: Initial beat drop & Hook line slam
  - 4.10s: Cut to Scene 2 (Hardware & Zero Entropy reveal)
  - 9.29s: Cut to Scene 3 (Tactical UI & Deterministic Math)
  - 14.73s: Cut to Scene 4 (Verification & Zero Persistence)
  - 18.01s: Outro logo and final tagline
- Audio-reactive treatment: Subtle ambient orange glow pulse reacting to bass presence.
- SFX posture: Tactile & physical (dice shake on hook, dice throw on hardware reveal, tactile UI click on card selection, digital confirmation beep on verification).
- Restraint rule: No generic cartoon whooshes; keep SFX strictly tied to physical hardware and cryptographic events.

## Storyboard

### Scene 1 — The Provocation (Hook) — 4.0s (0.0s - 4.0s)
- **Visual**: Full-screen obsidian field with glowing orange border accents. Massive centered headline fades and scales in: "NEVER TRUST SILICON TO GENERATE YOUR KEYS." Subtitle: "Most hardware wallets generate entropy in a black box."
- **Sequential**: Headline slams in (0.3s), subtitle reveals with glowing orange pill accent (1.5s).
- **Audio intent**: Dramatic attention grab.
- **Audio-coupled idea**: Dice shake SFX leading into sharp impact beat.
- **Transition**: Fast optical flash cut → Scene 2.

### Scene 2 — The Physical Hardware — 5.0s (4.0s - 9.0s)
- **Visual**: High-res photograph of SEEDER hardware running in its 3D printed case flanked by physical dice and coins. Side badge: "100% PHYSICAL ENTROPY".
- **Sequential**: Image floats in with glowing card frame; 3 tactical pills slide in: "NO TRNG" (4.5s) → "NO PRNG" (5.2s) → "ZERO PERSISTENCE" (6.0s).
- **Audio intent**: Confident hardware showcase.
- **Audio-coupled idea**: Dice roll / throw SFX as the hardware settles.
- **Transition**: Smooth horizontal slide → Scene 3.

### Scene 3 — The Sovereign UI & Math — 5.5s (9.0s - 14.5s)
- **Visual**: Cyberpunk Tactical HUD showcase. Floating cards displaying "DICE SEED" and "COIN SEED" with 60 FPS selection highlight, battery gauge, and raw hexadecimal entropy stream.
- **Copy**: "THE MATH HAPPENS RIGHT IN FRONT OF YOU."
- **Sub-copy**: "50 Rolls → Coldcard SHA-256 → 12 Words | 99 Rolls → 24 Words"
- **Audio intent**: Technical mastery and precision.
- **Audio-coupled idea**: Fast tactile card slide / chip click on UI card transition.
- **Transition**: Quick zoom-in cut → Scene 4.

### Scene 4 — Don't Trust. Verify. (Outro) — 5.5s (14.5s - 20.0s)
- **Visual**: Terminal verification box (`printf '314159...' | sha256sum`) and air-gapped security badge ("VOLATILE RAM ONLY • ZERO RADIO • AIR-GAPPED").
- **Final Reveal (17.5s)**: Bold SEEDER logo in electric orange: "SEEDER / Sovereign Seed Generator" with tagline "Don't trust. Roll the dice."
- **Audio intent**: Victorious and definitive payoff.
- **Audio-coupled idea**: Confirmation chime, music fades smoothly to silence.

**Music mood for this video:** Upbeat, sharp electronic tech beat.
**Audio summary:** Propulsive synth beat punctuated by physical dice rolls and tactical clicks, resolving into a clean air-gapped security signoff.
