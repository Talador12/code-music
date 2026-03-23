"""Rain on a window: ambient piano, barely-there pad, long notes, Dm.

Chill. The kind of thing you'd have on while reading. Notes fall
slowly like drops. Nothing forces itself.
"""

from code_music import Chord, Note, Song, Track, delay, reverb, stereo_width

song = Song(title="rain_window", bpm=58)

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3, pan=0.0))
for ch, sh in [("D", "min7"), ("A#", "maj7"), ("F", "maj7"), ("C", "sus2")] * 2:
    pad.add(Chord(ch, sh, 3, duration=4.0, velocity=0.45))

piano = song.add_track(Track(name="piano", instrument="piano", volume=0.6, pan=-0.1))
drops = [
    Note("A", 4, 1.5),
    Note.rest(0.5),
    Note("F", 4, 1.0),
    Note.rest(1.0),
    Note("D", 5, 2.0),
    Note.rest(2.0),
    Note("C", 5, 0.5),
    Note("A", 4, 0.5),
    Note.rest(1.0),
    Note("G", 4, 2.0),
    Note.rest(4.0),
    Note("D", 4, 1.0),
    Note.rest(0.5),
    Note("F", 4, 0.5),
    Note("A", 4, 1.5),
    Note.rest(0.5),
    Note("C", 5, 3.0),
    Note.rest(4.0),
    Note("A#", 4, 2.0),
    Note("G", 4, 1.0),
    Note.rest(1.0),
    Note("A", 4, 4.0),
]
piano.extend(drops)

song._effects = {
    "pad": lambda s, sr: stereo_width(
        reverb(s, sr, room_size=0.9, damping=0.6, wet=0.5), width=1.9
    ),
    "piano": lambda s, sr: delay(
        reverb(s, sr, room_size=0.6, wet=0.25), sr, delay_ms=500.0, feedback=0.35, wet=0.2
    ),
}
