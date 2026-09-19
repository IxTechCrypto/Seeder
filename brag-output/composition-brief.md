# Hyperframes Composition Brief: SEEDER

## Objective
Create a short, punchy, launch-style brag video for SEEDER (Sovereign Bitcoin Seed Generator).

## Output
- Composition directory: `brag-output/composition/`
- Rendered video: `brag-output/brag.mp4`
- Format: landscape — 1920x1080
- Duration: 20 seconds

## Source Material
- Project root: `d:\github\Seeder`
- Primary files read: `README.md`, `SECURITY.md`, `HARDWARE.md`, `preview/concept1_cyberpunk2077.jpg`, `Images/Seeder_cover.jpg`
- Product name: SEEDER
- Tagline / strongest claim: "Zero Silicon Entropy. If the words don't match your offline SHA-256 math, discard the device."
- Key UI or visual moment to recreate: Real hardware device running in 3D case with dice, glowing orange cards ("DICE SEED", "COIN SEED"), raw hexadecimal entropy stream, and terminal verification.
- Copy that must appear verbatim:
  - "NEVER TRUST SILICON TO GENERATE YOUR KEYS."
  - "Zero Silicon Entropy (No TRNG / PRNG)"
  - "The math happens right in front of you."
  - "Don't trust. Verify."

## Creative Direction
- Tone preset: `cinematic`
- Creative direction: Cyberpunk sovereign hardware trailer
- Interpretation: Deep obsidian black, electric Bitcoin orange glow, bold typography, tactile hardware photos, and synchronized dice audio.
- Angle: Exposing the blind trust of traditional hardware wallet RNGs and presenting SEEDER's pure physical entropy alternative.
- Hook: "NEVER TRUST SILICON TO GENERATE YOUR KEYS."
- Outro / punchline: "SEEDER • Sovereign Seed Generator • Don't trust. Roll the dice."
- Avoid:
  - Generic SaaS language
  - Abstract filler visuals
  - Unreadable micro-text

## Visual Identity
- Background: `#0A0D10` (Obsidian Dark)
- Card fills: `#141922`
- Text: `#FFFFFF` (Heading), `#CBD5E1` (Body)
- Accent: `#F7931A` (Bitcoin Orange), `#FF9E2C` (Glow Amber)
- Border / Glow: `rgba(247, 147, 26, 0.4)`
- Display font: `system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- Code / Monospace font: `"JetBrains Mono", "SF Mono", Consolas, monospace`

## Storyboard & Timing Contract
1. **Scene 1 (Hook)**: 0.0s - 4.0s
   - Massive headline: "NEVER TRUST SILICON TO GENERATE YOUR KEYS."
   - Subtitle: "Most hardware wallets generate entropy in a black box."
   - SFX: Dice shake at 0.1s.
2. **Scene 2 (Hardware)**: 4.0s - 9.0s
   - Real hardware photograph with 3D printed case, dice & coins.
   - 3 Floating badges: "NO TRNG" • "NO PRNG" • "100% PHYSICAL ENTROPY"
   - SFX: Dice throw at 4.2s.
3. **Scene 3 (Tactical UI & Math)**: 9.0s - 14.5s
   - Tactical HUD interface: "DICE SEED" / "COIN SEED" glowing cards.
   - Headline: "THE MATH HAPPENS RIGHT IN FRONT OF YOU."
   - Subtitle: "50 Rolls → Coldcard SHA-256 → 12 Words | 99 Rolls → 24 Words"
   - Hex stream preview: `0x7a3f89b42e...`
   - SFX: Card slide & chip click at 9.3s.
4. **Scene 4 (Verification & Outro)**: 14.5s - 20.0s
   - Terminal verification: `printf '314159...' | sha256sum`
   - Security badge: "VOLATILE RAM ONLY • ZERO RADIO • AIR-GAPPED"
   - Final logo reveal (17.0s - 20.0s): SEEDER logo + "Don't trust. Roll the dice."
   - Music fades out smoothly from 18.0s to 20.0s.

## Audio
- Audio role: Cinematic electronic support with tactile dice and mechanical click accents
- Music: `assets/music.mp3` (Happy Beats Vol. 10, Ende)
- SFX:
  - `assets/dice-shake.ogg`
  - `assets/dice-throw.ogg`
  - `assets/card-slide.ogg`
  - `assets/chip-lay.ogg`
