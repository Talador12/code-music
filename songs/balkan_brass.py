"""balkan_brass.py — Balkan brass band. D Phrygian dominant, 138 BPM. Guca festival.

A high-energy Balkan brass piece with the characteristic Phrygian dominant scale,
oom-pah bass, and staccato trumpet melodies. Boban Markovic territory.

Style: Balkan brass, D Phrygian dominant, 138 BPM.
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    Track,
    compress,
    reverb,
)

song = Song(title="Balkan Brass", bpm=138)

r = Note.rest

# ── Tuba — oom-pah bass ──────────────────────────────────────────────────
tuba = song.add_track(Track(name="tuba", instrument="bass", volume=0.6, pan=-0.15))
tuba_pattern = [
    Note("D", 2, 1.0),
    r(1.0),
    Note("A", 2, 1.0),
    r(1.0),
    Note("Bb", 2, 1.0),
    r(1.0),
    Note("A", 2, 1.0),
    r(1.0),
]
for _ in range(12):
    tuba.extend(tuba_pattern)

# ── Snare — driving 2-and-4 ──────────────────────────────────────────────
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.55))
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7))
for _ in range(24):
    snare.extend([r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)])
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)])

# ── Trumpet 1 — melody in D Phrygian dominant ────────────────────────────
tp1 = song.add_track(Track(name="tp1", instrument="trumpet", volume=0.55, pan=0.2))
melody_a = [
    Note("D", 5, 0.5),
    Note("Eb", 5, 0.5),
    Note("F#", 5, 0.5),
    Note("G", 5, 0.5),
    Note("A", 5, 1.0),
    Note("Bb", 5, 0.5),
    Note("A", 5, 0.5),
]
melody_b = [
    Note("G", 5, 0.5),
    Note("F#", 5, 0.5),
    Note("Eb", 5, 0.5),
    Note("D", 5, 0.5),
    Note("Eb", 5, 0.5),
    Note("F#", 5, 0.5),
    Note("D", 5, 1.0),
]
melody_c = [
    Note("A", 5, 0.5),
    Note("Bb", 5, 0.5),
    Note("A", 5, 0.5),
    Note("G", 5, 0.5),
    Note("F#", 5, 1.0),
    Note("D", 5, 1.0),
]
phrase = melody_a + melody_b + melody_c + [r(4.0)]
for _ in range(4):
    tp1.extend(phrase)

# ── Trumpet 2 — harmony a third below ────────────────────────────────────
tp2 = song.add_track(Track(name="tp2", instrument="trumpet", volume=0.45, pan=-0.2))
harmony_a = [
    Note("Bb", 4, 0.5),
    Note("C", 5, 0.5),
    Note("D", 5, 0.5),
    Note("Eb", 5, 0.5),
    Note("F#", 5, 1.0),
    Note("G", 5, 0.5),
    Note("F#", 5, 0.5),
]
harmony_b = [
    Note("Eb", 5, 0.5),
    Note("D", 5, 0.5),
    Note("C", 5, 0.5),
    Note("Bb", 4, 0.5),
    Note("C", 5, 0.5),
    Note("D", 5, 0.5),
    Note("Bb", 4, 1.0),
]
harmony_c = [
    Note("F#", 5, 0.5),
    Note("G", 5, 0.5),
    Note("F#", 5, 0.5),
    Note("Eb", 5, 0.5),
    Note("D", 5, 1.0),
    Note("Bb", 4, 1.0),
]
harmony = harmony_a + harmony_b + harmony_c + [r(4.0)]
for _ in range(4):
    tp2.extend(harmony)

# ── Pad — brass section chord bed ────────────────────────────────────────
brass_pad = song.add_track(Track(name="brass_pad", instrument="pad", volume=0.25))
for _ in range(6):
    brass_pad.extend(
        [
            Chord("D", "min", 3, duration=8.0),
            Chord("Bb", "maj", 3, duration=4.0),
            Chord("A", "dom7", 3, duration=4.0),
        ]
    )

song.effects = {
    "tp1": EffectsChain()
    .add(reverb, room_size=0.35, wet=0.15)
    .add(compress, threshold=0.5, ratio=3.0),
    "tp2": EffectsChain()
    .add(reverb, room_size=0.35, wet=0.15)
    .add(compress, threshold=0.5, ratio=3.0),
    "brass_pad": EffectsChain().add(reverb, room_size=0.5, wet=0.25),
}
