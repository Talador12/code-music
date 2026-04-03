"""Parallel Fifths — melody harmonized in parallel perfect fifths."""

from code_music import EffectsChain, Note, Song, Track, reverb
from code_music.theory import parallel_motion

melody = [Note(n, 5, 0.5) for n in ["C", "D", "E", "F", "G", "A", "B", "C"]]
fifths = parallel_motion(melody, interval=7)
thirds = parallel_motion(melody, interval=4)
song = Song(title="Parallel Fifths", bpm=100, sample_rate=44100)
song.add_track(Track(name="melody", instrument="piano", volume=0.5)).extend(melody)
song.add_track(Track(name="fifths", instrument="piano", volume=0.4, pan=0.2)).extend(fifths)
song.add_track(Track(name="thirds", instrument="piano", volume=0.4, pan=-0.2)).extend(thirds)
song.effects = {"melody": EffectsChain().add(reverb, room_size=0.4, wet=0.15)}
