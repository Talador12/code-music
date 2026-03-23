"""Cello adagio: solo cello, Bm, largo tempo. The most human sound.

Alluring. A single cello voice, nothing else. Played at 52 BPM so
each note breathes. The gaps are not silence — they're tension.
"""

from code_music import Note, Song, Track, crescendo, decrescendo, humanize, reverb

song = Song(title="cello_adagio", bpm=52)

vc = song.add_track(Track(name="cello", instrument="cello", volume=0.85, pan=0.0))

phrase_a = crescendo(
    [
        Note("B", 3, 2.0),
        Note("D", 4, 1.0),
        Note("F#", 4, 1.0),
        Note("A", 4, 3.0),
        Note.rest(1.0),
        Note("G", 4, 1.5),
        Note("F#", 4, 0.5),
        Note("E", 4, 1.0),
        Note("D", 4, 4.0),
    ],
    start_vel=0.3,
    end_vel=0.85,
)

phrase_b = decrescendo(
    [
        Note("F#", 4, 1.0),
        Note("G", 4, 0.5),
        Note("A", 4, 0.5),
        Note("B", 4, 2.0),
        Note("A", 4, 1.0),
        Note.rest(1.0),
        Note("G", 4, 1.5),
        Note("F#", 4, 0.5),
        Note("E", 4, 1.0),
        Note("D", 4, 4.0),
    ],
    start_vel=0.9,
    end_vel=0.2,
)

vc.extend(humanize(phrase_a, vel_spread=0.04, timing_spread=0.03))
vc.extend(humanize(phrase_b, vel_spread=0.04, timing_spread=0.03))

song._effects = {
    "cello": lambda s, sr: reverb(s, sr, room_size=0.85, damping=0.35, wet=0.35),
}
