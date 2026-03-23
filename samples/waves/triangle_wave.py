"""Triangle wave demo: G major scale, shows soft mellow timbre."""

from code_music import Song, Track, scale

song = Song(title="triangle_wave", bpm=100)
tr = song.add_track(Track(name="tri", instrument="triangle", volume=0.75))
notes = scale("G", "major", octave=4)
for n in notes:
    n.duration = 0.75
tr.extend(notes)
