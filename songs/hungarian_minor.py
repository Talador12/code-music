"""Hungarian Minor - exotic scale with dramatic character."""

from code_music import Chord, Note, Song, Track, scale

song = Song(title="Hungarian Minor", bpm=90, sample_rate=44100)

lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.5, pan=0.15))
lead.extend(scale("D", "hungarian_minor", octave=5, length=16))

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3, pan=-0.15))
for root, shape in [("D", "min"), ("Bb", "maj"), ("A", "dom7"), ("D", "min")] * 2:
    pad.add(Chord(root, shape, 3, duration=4.0, velocity=40))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.45))
for root in ["D", "Bb", "A", "D"] * 2:
    bass.add(Note(root, 2, 4.0, velocity=55))
