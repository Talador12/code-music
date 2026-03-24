"""Hip-hop template — 90 BPM, Am, lo-fi beat, Rhodes chords, swung hats.

Copy and rename: cp songs/_template_hiphop.py songs/my_hiphop_track.py
Then edit and: make play-my_hiphop_track
"""

from code_music import (
    EIGHTH,
    HALF,
    QUARTER,
    Chord,
    Note,
    Song,
    Track,
    compress,
    reverb,
    tape_sat,
)

song = Song(title="My Hip-Hop Track", bpm=90, key_sig="A")

BAR = 4.0
SWING = 0.5
r = Note.rest

# ── Drums ──────────────────────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.9))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.72))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.38, swing=SWING))

for _ in range(8):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 0.5), r(0.5), r(1.0)])
    snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)])
    hat.extend([Note("F", 5, EIGHTH)] * 8)

# ── Rhodes comp — change these chords ─────────────────────────────────────
comp = song.add_track(Track(name="comp", instrument="rhodes", volume=0.55, swing=SWING, pan=-0.1))
comp.extend(
    [
        Chord("A", "min7", 3, duration=BAR, velocity=0.55),
        Chord("F", "maj7", 3, duration=BAR, velocity=0.52),
        Chord("C", "maj7", 3, duration=BAR, velocity=0.55),
        Chord("G", "dom7", 3, duration=BAR, velocity=0.52),
    ]
    * 2
)

# ── Bass ───────────────────────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.72, swing=SWING))
bass.extend(
    [
        Note("A", 2, HALF),
        r(QUARTER),
        Note("G", 2, QUARTER),
        Note("F", 2, HALF),
        r(HALF),
        Note("C", 3, HALF),
        Note("G", 2, HALF),
        Note("G", 2, HALF),
        r(HALF),
    ]
    * 2
)

# ── Melody — write yours here ─────────────────────────────────────────────
mel = song.add_track(Track(name="melody", instrument="piano", volume=0.65, swing=SWING, pan=0.1))
mel.extend([r(BAR)] * 4)
# TODO: add your melody here
mel.extend([r(BAR)] * 4)

song._effects = {
    "comp": lambda s, sr: tape_sat(
        reverb(s, sr, room_size=0.4, wet=0.15), sr, drive=1.5, warmth=0.4, wet=0.3
    ),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.1),
}
