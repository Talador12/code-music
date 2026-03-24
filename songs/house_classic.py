"""house_classic.py — Classic house. Cm, 122 BPM. Chicago 1987.

The original house sound: Roland TR-909 kick and hat, off-beat open hat,
simple chord stab, piano riff. Frankie Knuckles, Larry Heard, Marshall
Jefferson. Before EDM was a genre name — just dance music.
"""

from code_music import (
    EIGHTH,
    HALF,
    QUARTER,
    Chord,
    Note,
    Song,
    Track,
    chorus,
    compress,
    reverb,
)

song = Song(title="House Classic", bpm=122)
BAR = 4.0
r = Note.rest
E8 = EIGHTH

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=1.0))
kick.extend([Note("C", 2, 1.0)] * (16 * 4))

hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.42))
hat.extend([r(0.5), Note("F", 5, 0.5)] * (16 * 4))

clap = song.add_track(Track(name="clap", instrument="drums_clap", volume=0.75))
clap.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)] * 16)

# ── Piano riff — the Larry Heard sound ─────────────────────────────────────
piano = song.add_track(Track(name="piano", instrument="piano", volume=0.62, pan=-0.1))
riff = [
    Chord("C", "min7", 3, duration=E8, velocity=0.72),
    r(E8),
    Chord("C", "min7", 3, duration=E8, velocity=0.65),
    r(QUARTER + E8),
    Chord("G#", "maj7", 3, duration=E8, velocity=0.70),
    r(E8),
    Chord("G#", "maj7", 3, duration=E8, velocity=0.62),
    r(QUARTER + E8),
]
piano.extend(riff * 8)

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.78))
bass.extend([Note("C", 2, HALF), Note("G#", 1, HALF)] * 16)

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.32))
for _ in range(4):
    pad.extend(
        [
            Chord("C", "min7", 3, duration=BAR * 2, velocity=0.4),
            Chord("G#", "maj7", 3, duration=BAR * 2, velocity=0.38),
        ]
    )

song._effects = {
    "piano": lambda s, sr: chorus(
        reverb(s, sr, room_size=0.4, wet=0.15), sr, rate_hz=0.5, wet=0.12
    ),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.1),
}
