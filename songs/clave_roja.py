"""clave_roja.py — Latin jazz / salsa. Cm, 190 BPM. Fourth Clave album track.

Faster, more energetic than ipanema_hours. Salsa energy with trumpet.
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
    humanize,
    reverb,
)

song = Song(title="Clave Roja", bpm=190)
BAR = 4.0
r = Note.rest
E8 = EIGHTH
SWING = 0.48

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.85))
for _ in range(12):
    kick.extend([Note("C", 2, E8), r(E8 * 3), Note("C", 2, E8), r(E8), Note("C", 2, E8), r(E8)])

snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.72, swing=SWING))
for _ in range(12):
    snare.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)])

hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.38, swing=SWING))
hat.extend([Note("F", 5, E8, velocity=0.35)] * (12 * 8))

bass = song.add_track(Track(name="bass", instrument="contrabass", volume=0.78, swing=SWING))
walk = humanize(
    [
        Note("C", 2, 1.0),
        Note("D#", 2, 1.0),
        Note("G", 2, 1.0),
        Note("A#", 2, 1.0),
        Note("G", 2, 1.0),
        Note("F", 2, 1.0),
        Note("D#", 2, 1.0),
        Note("C", 2, 1.0),
    ]
    * 6,
    vel_spread=0.06,
    timing_spread=0.02,
)
bass.extend(walk)

tpt = song.add_track(
    Track(name="trumpet", instrument="trumpet", volume=0.72, pan=-0.2, swing=SWING)
)
tpt.extend([r(BAR)] * 4)
mel = humanize(
    [
        Note("C", 5, E8),
        Note("D#", 5, E8),
        Note("G", 5, E8),
        Note("C", 6, E8),
        Note("A#", 5, QUARTER),
        Note("G", 5, QUARTER),
        r(QUARTER),
        Note("F", 5, E8),
        Note("G", 5, E8),
        Note("A#", 5, QUARTER),
        Note("C", 6, HALF),
        r(HALF),
    ]
    * 2,
    vel_spread=0.07,
    timing_spread=0.02,
)
tpt.extend(mel)

comp = song.add_track(Track(name="comp", instrument="rhodes", volume=0.55, pan=0.2, swing=SWING))
for _ in range(12):
    comp.extend(
        [
            r(E8),
            Chord("C", "min7", 3, duration=E8, velocity=0.65),
            r(E8),
            Chord("C", "min7", 3, duration=E8, velocity=0.6),
            r(E8),
            Chord("G", "dom7", 3, duration=E8, velocity=0.62),
            r(E8),
            Chord("G", "dom7", 3, duration=E8, velocity=0.58),
        ]
    )

song.effects = {
    "trumpet": lambda s, sr: reverb(s, sr, room_size=0.35, wet=0.12),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.1),
}
