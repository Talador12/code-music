"""Taiko Thunder - massive taiko drums with shamisen melody."""

from code_music import Chord, Note, Song, Track, scale
from code_music.sound_design import shamisen, taiko

song = Song(title="Taiko Thunder", bpm=90, sample_rate=44100)
song.register_instrument("taiko", taiko)
song.register_instrument("shamisen", shamisen)

# Taiko ensemble
drums = song.add_track(Track(name="taiko", instrument="taiko", volume=0.8))
pattern = [1, 0, 0, 1, 1, 0, 1, 0]
for _ in range(4):
    for hit in pattern:
        if hit:
            drums.add(Note("D", 2, 0.5, velocity=85))
        else:
            drums.add(Note.rest(0.5))

# Shamisen melody
sham = song.add_track(Track(name="shamisen", instrument="shamisen", volume=0.5, pan=0.15))
sham.extend(scale("D", "japanese", octave=5, length=16))

# Drone
drone = song.add_track(Track(name="drone", instrument="pad", volume=0.2))
drone.add(Chord("D", "sus2", 2, duration=16.0, velocity=30))
