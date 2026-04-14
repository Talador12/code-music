"""Enigmatic Scale - Verdi's mysterious and chromatic scale."""

from code_music import Chord, Note, Song, Track, scale

song = Song(title="Enigmatic Scale", bpm=70, sample_rate=44100)

lead = song.add_track(Track(name="lead", instrument="triangle", volume=0.45, pan=0.15))
lead.extend(scale("C", "enigmatic", octave=5, length=14))

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3))
pad.add(Chord("C", "aug", 3, duration=8.0, velocity=35))
pad.add(Chord("C", "aug", 3, duration=6.0, velocity=30))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.4))
bass.add(Note("C", 2, 14.0, velocity=45))
