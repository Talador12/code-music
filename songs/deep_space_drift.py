"""deep_space_drift.py — ambient / space music.

Style: slow-evolving drones, wide stereo pads, sparse plucked notes that drift
in and out of the texture like stars. Inspired by Brian Eno, Moby, Jon Hopkins.

No drums. No sharp attacks. Just space.

Structure (all very loose, 60 BPM):
  - Layer 1: root drone (sine, very slow swell) — whole track
  - Layer 2: pad chords that change every 8 bars (Dm → Bb → F → C)
  - Layer 3: high plucked notes, sparse and random-feeling, bars 5+
  - Layer 4: mid counter-melody (triangle), enters bar 9
  - Layer 5: sub bass swell, bars 17-24
"""

from code_music import Chord, Note, Song, Track, chorus, delay, lowpass, reverb

song = Song(title="Deep Space Drift", bpm=60)

BAR = 4.0
r = Note.rest


def bars(n):
    return [r(BAR)] * n


# ── Root drone — sine, D2, panned center ──────────────────────────────────────
# Break into 1-bar notes so synth never allocates a 128s buffer at once
drone = song.add_track(Track(name="drone", instrument="sine", volume=0.35, pan=0.0))
for _ in range(32):
    drone.add(Note("D", 2, duration=BAR, velocity=0.5))

# ── Pad chords — slow 8-bar changes, wide stereo pair ─────────────────────────
pad_l = song.add_track(Track(name="pad_l", instrument="pad", volume=0.45, pan=-0.6))
pad_r = song.add_track(Track(name="pad_r", instrument="pad", volume=0.45, pan=0.6))

# Dm9 → Bbmaj7 → Fmaj7 → Csus2, 8 bars each — 1-bar notes for synth efficiency
PAD_ROOTS = [("D", "min7"), ("A#", "maj7"), ("F", "maj7"), ("C", "sus2")]
for pad in (pad_l, pad_r):
    for root, shape in PAD_ROOTS:
        for _ in range(8):
            pad.add(Chord(root, shape, 3, duration=BAR, velocity=0.6))

# ── Sparse plucks — stars drifting in ─────────────────────────────────────────
pluck_l = song.add_track(Track(name="pluck_l", instrument="pluck", volume=0.3, pan=-0.4))
pluck_r = song.add_track(Track(name="pluck_r", instrument="pluck", volume=0.3, pan=0.4))

# Intentionally sparse: long rests between notes, asymmetric L/R
pluck_l.extend(bars(4))
pluck_l.extend(
    [
        Note("A", 4, 0.5, velocity=0.5),
        r(3.5),
        r(BAR),
        Note("F", 4, 0.5, velocity=0.4),
        r(3.5),
        Note("D", 5, 0.5, velocity=0.55),
        r(1.5),
        Note("C", 5, 0.5, velocity=0.4),
        r(1.5),
        r(BAR),
        Note("A", 4, 0.5, velocity=0.45),
        r(BAR + 3.5),
        Note("G", 4, 0.5, velocity=0.5),
        r(3.5),
        r(BAR),
        r(BAR),
        Note("F", 5, 0.5, velocity=0.35),
        r(3.5),
        r(BAR),
        Note("D", 5, 0.5, velocity=0.4),
        r(3.5),
        Note("A", 4, 1.0, velocity=0.5),
        r(BAR + 3.0),
        r(BAR * 4),  # silence before outro
    ]
)

pluck_r.extend(bars(6))
pluck_r.extend(
    [
        Note("D", 5, 0.5, velocity=0.45),
        r(3.5),
        r(BAR),
        Note("C", 5, 0.5, velocity=0.5),
        r(3.5),
        Note("A", 5, 0.5, velocity=0.4),
        r(1.5),
        Note("F", 4, 0.5, velocity=0.35),
        r(1.5),
        r(BAR),
        Note("G", 4, 0.5, velocity=0.5),
        r(BAR + 3.5),
        Note("D", 5, 0.5, velocity=0.4),
        r(3.5),
        r(BAR),
        Note("C", 5, 0.5, velocity=0.45),
        r(3.5),
        r(BAR),
        Note("A", 4, 0.5, velocity=0.35),
        r(3.5),
        Note("F", 5, 1.0, velocity=0.4),
        r(BAR + 3.0),
        r(BAR * 3),
    ]
)

# ── Counter-melody — triangle, enters bar 9 ───────────────────────────────────
counter = song.add_track(Track(name="counter", instrument="triangle", volume=0.4, pan=0.05))
counter.extend(bars(8))
# Slow, breath-like phrases with lots of space
counter.extend(
    [
        Note("D", 4, 2.0, velocity=0.5),
        Note("F", 4, 1.0, velocity=0.45),
        r(1.0),
        Note("A", 4, 3.0, velocity=0.55),
        r(1.0),
        Note("C", 5, 1.0, velocity=0.5),
        Note("A", 4, 1.0, velocity=0.45),
        r(2.0),
        Note("F", 4, 4.0, velocity=0.4),
        r(BAR),
        Note("A", 3, 2.0, velocity=0.45),
        Note("C", 4, 1.0, velocity=0.4),
        r(1.0),
        Note("D", 4, 4.0, velocity=0.5),
        Note("C", 4, 2.0, velocity=0.45),
        r(2.0),
        r(BAR * 2),
        Note("F", 4, 2.0, velocity=0.4),
        Note("G", 4, 1.0, velocity=0.35),
        r(1.0),
        Note("A", 4, 3.0, velocity=0.45),
        r(1.0),
        Note("D", 5, 4.0, velocity=0.5),
        r(BAR * 4),
    ]
)

# ── Sub swell — very slow sine sub, bars 17-24 ────────────────────────────────
sub = song.add_track(Track(name="sub", instrument="sine", volume=0.3, pan=0.0))
sub.extend(bars(16))
sub.extend(
    [
        *[Note("D", 1, BAR, velocity=0.6)] * 8,
        *[Note("F", 1, BAR, velocity=0.4)] * 4,
        *[Note("C", 1, BAR, velocity=0.35)] * 4,
    ]
)

# ── Effects ───────────────────────────────────────────────────────────────────
song._effects = {
    "drone": lambda s, sr: lowpass(
        reverb(s, sr, room_size=0.9, damping=0.6, wet=0.5), sr, cutoff_hz=400.0
    ),
    "pad_l": lambda s, sr: reverb(s, sr, room_size=0.85, damping=0.55, wet=0.4),
    "pad_r": lambda s, sr: reverb(s, sr, room_size=0.85, damping=0.55, wet=0.4),
    "pluck_l": lambda s, sr: delay(
        reverb(s, sr, room_size=0.7, wet=0.35), sr, delay_ms=500.0, feedback=0.45, wet=0.4
    ),
    "pluck_r": lambda s, sr: delay(
        reverb(s, sr, room_size=0.7, wet=0.35),
        sr,
        delay_ms=750.0,
        feedback=0.4,
        wet=0.4,
        ping_pong=True,
    ),
    "counter": lambda s, sr: chorus(
        reverb(s, sr, room_size=0.75, wet=0.3), sr, rate_hz=0.4, depth_ms=4.0, wet=0.3
    ),
    "sub": lambda s, sr: lowpass(s, sr, cutoff_hz=120.0, q=0.5),
}
