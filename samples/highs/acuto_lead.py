"""Bright lead: sawtooth in E major pentatonic, high octave, for solos."""

from code_music import Song, Track, scale

song = Song(title="bright_lead", bpm=140)
tr = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.7))
notes = scale("E", "pentatonic", octave=5, length=10)
for n in notes:
    n.duration = 0.5
tr.extend(notes)
tr.extend(list(reversed(notes)))
