"""Rock template — 120 BPM, Em, electric guitar + bass + drums.

Copy and rename: cp songs/_template_rock.py songs/my_rock_track.py
Then edit and: make play-my_rock_track
"""

from code_music import (
    EIGHTH,
    HALF,
    Chord,
    Note,
    Song,
    Track,
    compress,
    distortion,
    reverb,
)

song = Song(title="My Rock Track", bpm=120, key_sig="E")

BAR = 4.0
r = Note.rest

# ── Drums ──────────────────────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.95))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.82))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.4))

for _ in range(8):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)])
    snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)])
    hat.extend([Note("F", 5, EIGHTH)] * 8)

# ── Bass ───────────────────────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.78))
bass.extend(
    [
        Note("E", 2, HALF),
        Note("G", 2, HALF),
        Note("A", 2, HALF),
        Note("B", 2, HALF),
    ]
    * 4
)

# ── Guitar — change these chords ──────────────────────────────────────────
gtr = song.add_track(Track(name="guitar", instrument="guitar_electric", volume=0.7, pan=-0.15))
gtr.extend(
    [
        Chord("E", "min", 3, duration=HALF, velocity=0.75),
        Chord("G", "maj", 3, duration=HALF, velocity=0.72),
        Chord("A", "min", 3, duration=HALF, velocity=0.75),
        Chord("B", "dom7", 3, duration=HALF, velocity=0.78),
    ]
    * 4
)

# ── Lead melody — write yours here ────────────────────────────────────────
lead = song.add_track(Track(name="lead", instrument="guitar_electric", volume=0.6, pan=0.2))
lead.extend([r(BAR)] * 4)
# TODO: add your melody here
lead.extend([r(BAR)] * 4)

song._effects = {
    "guitar": lambda s, sr: distortion(
        reverb(s, sr, room_size=0.35, wet=0.1), drive=2.0, tone=0.55, wet=0.35
    ),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.1),
}
