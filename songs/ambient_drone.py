"""Ambient Drone - long evolving pads with no drums."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb

song = Song(title="Ambient Drone", bpm=60, sample_rate=44100)

# Deep drone
drone = song.add_track(Track(name="drone", instrument="pad", volume=0.3, pan=0.0))
drone.add(Chord("D", "min", 2, duration=32.0, velocity=35))
drone.add(Chord("D", "min", 2, duration=32.0, velocity=30))

# Upper pad
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.25, pan=-0.2))
for root, shape in [("D", "min7"), ("F", "maj7"), ("A", "min7"), ("C", "maj7")]:
    pad.add(Chord(root, shape, 4, duration=16.0, velocity=30))

# Shimmer
shimmer = song.add_track(Track(name="shimmer", instrument="triangle", volume=0.15, pan=0.3))
for note in ["D", "F", "A", "D", "F", "A", "C", "E"]:
    shimmer.add(Note(note, 6, 8.0, velocity=20))

# Sub bass
sub = song.add_track(Track(name="sub", instrument="bass", volume=0.35))
sub.add(Note("D", 1, 64.0, velocity=50))

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.9, wet=0.5),
    "shimmer": EffectsChain().add(reverb, room_size=0.95, wet=0.6),
}
