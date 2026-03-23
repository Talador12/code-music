"""Sawtooth wave demo: C chromatic scale showing sawtooth timbre evolution."""

from code_music import Song, Track, scale

song = Song(title="sawtooth_demo", bpm=100)
tr = song.add_track(Track(name="saw", instrument="sawtooth", volume=0.65))
notes = scale("C", "chromatic", octave=3, length=13)
for n in notes:
    n.duration = 0.5
tr.extend(notes)
