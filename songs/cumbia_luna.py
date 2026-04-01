"""cumbia_luna.py — Cumbia. G minor, 96 BPM. Colombian coastal groove.

A traditional cumbia with the signature guacharaca scrape, conga pattern,
accordion melody, and walking bass. Lucho Bermudez meets Celso Piña.

Style: Colombian cumbia, Gm, 96 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb

song = Song(title="Cumbia Luna", bpm=96)

r = Note.rest

# ── Drums — cumbia pattern ───────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7))
snare = song.add_track(Track(name="conga", instrument="drums_snare", volume=0.45))
hat = song.add_track(Track(name="guacharaca", instrument="drums_hat", volume=0.35))

for _ in range(16):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)])
    snare.extend(
        [
            r(0.5),
            Note("E", 4, 0.5),
            Note("E", 4, 0.5),
            r(0.5),
            Note("E", 4, 0.5),
            r(0.5),
            Note("E", 4, 0.5),
            r(0.5),
        ]
    )
    hat.extend([Note("F#", 6, 0.25)] * 16)

# ── Bass — walking root movement ─────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6, pan=-0.1))
bass_riff = [
    Note("G", 2, 1.0),
    Note("Bb", 2, 0.5),
    Note("C", 3, 0.5),
    Note("D", 3, 1.0),
    Note("C", 3, 0.5),
    Note("Bb", 2, 0.5),
]
for _ in range(16):
    bass.extend(bass_riff)

# ── Accordion — cumbia melody ────────────────────────────────────────────
acc = song.add_track(Track(name="accordion", instrument="organ", volume=0.5, pan=0.15))
melody_a = [
    Note("G", 4, 0.5),
    Note("Bb", 4, 0.5),
    Note("D", 5, 0.5),
    Note("C", 5, 0.5),
    Note("Bb", 4, 1.0),
    Note("G", 4, 1.0),
]
melody_b = [
    Note("F", 5, 0.5),
    Note("Eb", 5, 0.5),
    Note("D", 5, 0.5),
    Note("C", 5, 0.5),
    Note("Bb", 4, 0.5),
    Note("G", 4, 0.5),
    Note("A", 4, 1.0),
]
for _ in range(8):
    acc.extend(melody_a + melody_b)

# ── Pad — chord bed ──────────────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.2))
for _ in range(8):
    pad.extend(
        [
            Chord("G", "min", 3, duration=4.0),
            Chord("C", "min", 3, duration=4.0),
        ]
    )

song.effects = {
    "accordion": EffectsChain().add(reverb, room_size=0.4, wet=0.18),
    "pad": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
}
