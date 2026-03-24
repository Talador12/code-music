"""Jazz template — 160 BPM, Bb, swung 8ths, walking bass, Rhodes comp, ride cymbal.

Copy and rename: cp songs/_template_jazz.py songs/my_jazz_track.py
Then edit and: make play-my_jazz_track
"""

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    chorus,
    humanize,
    reverb,
)

song = Song(title="My Jazz Track", bpm=160, key_sig="Bb")

BAR = 4.0
SWING = 0.52
r = Note.rest

# ── Change these chords to taste (ii-V-I in Bb) ──────────────────────────
CHANGES = [
    Chord("C", "min7", 3, duration=BAR, velocity=0.6),
    Chord("F", "dom7", 3, duration=BAR, velocity=0.62),
    Chord("A#", "maj7", 3, duration=BAR * 2, velocity=0.6),
]

# ── Rhodes comp ────────────────────────────────────────────────────────────
comp = song.add_track(Track(name="comp", instrument="rhodes", volume=0.6, swing=SWING, pan=-0.15))
comp.extend(CHANGES * 4)

# ── Walking bass ──────────────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="contrabass", volume=0.78, swing=SWING))
walk = humanize(
    [
        Note("C", 2, 1.0),
        Note("D", 2, 1.0),
        Note("D#", 2, 1.0),
        Note("F", 2, 1.0),
        Note("F", 2, 1.0),
        Note("G", 2, 1.0),
        Note("A", 2, 1.0),
        Note("C", 3, 1.0),
        Note("A#", 1, 1.0),
        Note("C", 2, 1.0),
        Note("D", 2, 1.0),
        Note("F", 2, 1.0),
        Note("A#", 1, 4.0),
    ],
    vel_spread=0.06,
    timing_spread=0.02,
)
bass.extend(walk * 4)

# ── Ride cymbal ────────────────────────────────────────────────────────────
ride = song.add_track(Track(name="ride", instrument="drums_ride", volume=0.42, swing=SWING))
ride.extend([Note("F", 5, 0.5), Note("F", 5, 0.25), Note("F", 5, 0.25)] * 32)

# ── Melody — write yours here (sax, trumpet, flute) ───────────────────────
mel = song.add_track(Track(name="melody", instrument="saxophone", volume=0.7, swing=SWING, pan=0.1))
mel.extend([r(BAR)] * 4)
# TODO: add your melody here
mel.extend([r(BAR)] * 4)

song._effects = {
    "comp": lambda s, sr: chorus(reverb(s, sr, room_size=0.35, wet=0.1), sr, rate_hz=0.5, wet=0.12),
}
