"""stutter_step.py — Glitchy IDM track using filter + stretch + split.

A melody is filtered to keep only loud notes, then the gaps create a
stuttery pattern. The second half is time-stretched for a slowdown glitch.

Style: IDM / glitch, Am, 135 BPM.
"""

import random

from code_music import Chord, EffectsChain, Note, Song, Track, delay, distortion, reverb

song = Song(title="Stutter Step", bpm=135)

r = Note.rest

# ── Build a dense melody with varied velocities ──────────────────────────
dense = Track(name="glitch", instrument="square", volume=0.5)
rng = random.Random(42)
pitches = ["A", "C", "D", "E", "G"]
for _ in range(64):
    p = pitches[rng.randint(0, len(pitches) - 1)]
    v = rng.choice([0.3, 0.5, 0.7, 0.9, 0.2, 0.8])
    dense.add(Note(p, rng.choice([4, 5]), 0.5, velocity=v))

# Filter: keep only loud hits (velocity > 0.6) — creates stuttery gaps
stuttered = dense.filter(lambda e: e.velocity > 0.6)

# Split at halfway, stretch the second half for glitch slowdown
first_half, second_half = stuttered.split(at_beat=16.0)
glitched = first_half.concat(second_half.stretch(1.5))
song.add_track(glitched)

# ── Bass — simple anchor ────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
for _ in range(12):
    bass.extend([Note("A", 2, 2.0), Note("E", 2, 2.0)])

# ── Drums ────────────────────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.3))
for _ in range(12):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)])
    hat.extend([Note("F#", 6, 0.25)] * 16)

# ── Pad ──────────────────────────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.2))
for _ in range(12):
    pad.add(Chord("A", "min7", 3, duration=4.0))

song.effects = {
    "glitch": EffectsChain()
    .add(distortion, drive=1.5, tone=0.6, wet=0.3)
    .add(delay, delay_ms=185, feedback=0.3, wet=0.2),
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
}
