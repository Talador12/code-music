"""late_shift.py — Neo-soul / R&B. Rhodes, walking bass, groove pocket. 88 BPM, Fm.

Structure:
  Bars 1-4:   Intro — Rhodes alone, sparse
  Bars 5-12:  Verse — bass enters, swung hats
  Bars 13-16: Pre-chorus — chord stabs thicken
  Bars 17-24: Chorus — full groove, melody peaks
  Bars 25-28: Bridge — stripped back, Rhodes solo
  Bars 29-36: Chorus out — full groove fades
"""

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    chorus,
    compress,
    delay,
    reverb,
)

song = Song(title="Low Light", bpm=88)

BAR = 4.0
SWING = 0.5
r = Note.rest


def bars(n):
    return [r(BAR)] * n


# ── Rhodes comp — the whole vibe ──────────────────────────────────────────
comp = song.add_track(Track(name="comp", instrument="rhodes", volume=0.68, pan=-0.1, swing=SWING))

# Sparse intro
intro_chords = [
    Chord("F", "min7", 3, duration=BAR * 2, velocity=0.55),
    Chord("C#", "maj7", 3, duration=BAR * 2, velocity=0.5),
] * 2
comp.extend(intro_chords)

# Verse: more rhythmic
verse_comp = [
    Chord("F", "min7", 3, duration=BAR, velocity=0.6),
    Chord("C#", "maj7", 3, duration=BAR, velocity=0.58),
    Chord("G#", "maj7", 3, duration=BAR, velocity=0.6),
    Chord("D#", "dom7", 3, duration=BAR, velocity=0.62),
]
comp.extend(verse_comp * 4)  # bars 5-20
comp.extend(verse_comp * 2)  # bridge thinner
comp.extend(verse_comp * 4)  # chorus out

# ── Wurlitzer melody voice — floats above comp ────────────────────────────
mel = song.add_track(Track(name="melody", instrument="wurlitzer", volume=0.7, pan=0.1, swing=SWING))
mel.extend(bars(4))  # intro: silent

phrase = [
    r(0.5),
    Note("F", 4, 0.5),
    Note("G#", 4, 0.5),
    Note("A#", 4, 0.5),
    Note("C", 5, 1.0),
    r(0.5),
    Note("A#", 4, 0.5),
    Note("G#", 4, 1.0),
    Note("F", 4, 0.5),
    r(0.5),
    r(BAR),
    Note("D#", 4, 0.5),
    Note("F", 4, 0.5),
    Note("G#", 4, 0.5),
    Note("A#", 4, 0.5),
    Note("C", 5, 1.0),
    r(1.0),
    Note("F", 5, 3.0),
    r(1.0),
]
mel.extend(phrase * 4)  # verse + chorus
mel.extend(
    [
        Note("F", 5, 2.0, velocity=0.45),
        r(2.0),
        Note("D#", 5, 1.5, velocity=0.4),
        Note("C", 5, 0.5),
        r(2.0),
        Note("A#", 4, 4.0, velocity=0.38),
        r(BAR),
    ]
)  # bridge
mel.extend(phrase * 2)  # chorus out

# ── Walking bass ──────────────────────────────────────────────────────────
bass = song.add_track(
    Track(name="bass", instrument="contrabass", volume=0.78, pan=0.05, swing=SWING)
)
bass.extend(bars(4))

walk = [
    Note("F", 2, 1.0),
    Note("G#", 2, 1.0),
    Note("C", 3, 1.0),
    Note("D#", 3, 1.0),
    Note("C#", 2, 1.0),
    Note("D#", 2, 1.0),
    Note("F", 2, 1.0),
    Note("G#", 2, 1.0),
    Note("G#", 1, 1.0),
    Note("A#", 1, 1.0),
    Note("C", 2, 1.0),
    Note("D#", 2, 1.0),
    Note("D#", 2, 1.0),
    Note("F", 2, 1.0),
    Note("G#", 2, 1.0),
    Note("C", 3, 1.0),
]
bass.extend(walk * 8)
bass.extend(bars(4))

# ── Drums — swung, pocket-locked ─────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.9))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.75))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.42, swing=SWING))
ride = song.add_track(Track(name="ride", instrument="drums_ride", volume=0.48, swing=SWING))

k = Note("C", 2, 1.0)
s = Note("D", 3, 1.0)
h = Note("F", 5, 0.5)

for _ in range(8):  # bars 5-36
    kick.extend([k, r(1.0), k, r(0.5), k, r(0.5)])  # funky kick
    snare.extend([r(1.0), s, r(1.0), s])
    hat.extend([h] * 8)
    ride.extend([h, h, r(0.5), h, h, r(0.5), h, r(0.5)])  # jazz ride feel

kick.extend(bars(4))
snare.extend(bars(4))
hat.extend(bars(4))
ride.extend(bars(4))

song._effects = {
    "comp": lambda s, sr: chorus(reverb(s, sr, room_size=0.4, wet=0.15), sr, rate_hz=0.5, wet=0.18),
    "melody": lambda s, sr: delay(
        reverb(s, sr, room_size=0.5, wet=0.18), sr, delay_ms=341.0, feedback=0.25, wet=0.15
    ),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.15),
}
