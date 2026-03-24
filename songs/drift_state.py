"""drift_state.py — Ambient generative. 50 BPM, D major, Lydian mode.

Generative ambient: each track uses generate_melody() with a different seed
so the parts evolve independently without a fixed relationship. The result
sounds like it was composed but also like it emerged. Lydian (#4) keeps
everything floating — no note creates tension that demands resolution.

No drums. No rhythm. Notes arrive when they arrive.
Let it run. Each playthrough is slightly different via humanize().
"""

from code_music import (
    WHOLE,
    Chord,
    Note,
    Song,
    Track,
    chorus,
    delay,
    generate_melody,
    humanize,
    lowpass,
    reverb,
    stereo_width,
)

song = Song(title="Drift State", bpm=50)

BAR = 4.0

# ── Sustained drone — the floor ───────────────────────────────────────────
for inst, pan_v, vol, oct in [
    ("sub_bass", 0.0, 0.35, 1),
    ("sine", -0.1, 0.28, 2),
]:
    tr = song.add_track(Track(name=f"drone_{inst}", instrument=inst, volume=vol, pan=pan_v))
    for _ in range(16):
        tr.add(Note("D", oct, BAR, velocity=0.5))

# ── Pad layer — slow chord changes ────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.38, pan=0.0))
# Lydian: D maj7 → A maj7 → E add9 → G# aug (very Lydian)
for ch, sh, dur in [
    ("D", "maj7", 8.0),
    ("A", "maj7", 8.0),
    ("E", "add9", 8.0),
    ("G#", "aug", 8.0),
    ("D", "maj7", 16.0),  # hold longer at the end
    ("A", "sus2", 16.0),
]:
    pad.add(Chord(ch, sh, 3, duration=dur, velocity=0.45))

# ── Generative piano — seed varies the melody each time ──────────────────
piano = song.add_track(Track(name="piano", instrument="piano", volume=0.58, pan=-0.15))
mel = generate_melody("D", scale_mode="lydian", octave=5, bars=16, density=0.35, seed=42)
piano.extend(humanize(mel, vel_spread=0.1, timing_spread=0.06))

# ── Vibraphone — different seed, independent evolution ────────────────────
vib = song.add_track(Track(name="vibes", instrument="vibraphone", volume=0.5, pan=0.25))
vib_mel = generate_melody("D", scale_mode="lydian", octave=5, bars=16, density=0.25, seed=137)
vib.extend(humanize(vib_mel, vel_spread=0.09, timing_spread=0.07))

# ── Harp — third independent voice ───────────────────────────────────────
harp = song.add_track(Track(name="harp", instrument="harp_ks", volume=0.45, pan=0.1))
harp_mel = generate_melody("D", scale_mode="lydian", octave=4, bars=16, density=0.2, seed=999)
harp.extend(humanize(harp_mel, vel_spread=0.12, timing_spread=0.08))

# ── Strings — slow melodic arc ────────────────────────────────────────────
strings = song.add_track(Track(name="strings", instrument="strings", volume=0.4, pan=-0.3))
strings.extend(
    humanize(
        [
            Note("D", 4, WHOLE, velocity=0.3),
            Note("A", 4, WHOLE, velocity=0.32),
            Note("F#", 4, WHOLE, velocity=0.35),
            Note("E", 4, WHOLE * 2, velocity=0.38),
            Note("D", 4, WHOLE, velocity=0.35),
            Note("C#", 5, WHOLE * 2, velocity=0.4),
            Note("A", 4, WHOLE * 2, velocity=0.35),
            Note("D", 4, WHOLE * 4, velocity=0.25),
        ],
        vel_spread=0.04,
        timing_spread=0.05,
    )
)

song._effects = {
    "drone_sub_bass": lambda s, sr: lowpass(s, sr, cutoff_hz=100.0),
    "drone_sine": lambda s, sr: reverb(s, sr, room_size=0.95, wet=0.55),
    "pad": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.92, wet=0.5), width=1.9),
    "piano": lambda s, sr: delay(
        reverb(s, sr, room_size=0.75, wet=0.35), sr, delay_ms=720.0, feedback=0.45, wet=0.3
    ),
    "vibes": lambda s, sr: chorus(reverb(s, sr, room_size=0.8, wet=0.4), sr, rate_hz=0.3, wet=0.2),
    "harp": lambda s, sr: reverb(s, sr, room_size=0.85, wet=0.4),
    "strings": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.9, wet=0.38), width=1.5),
}
