"""Ambient Drift — drone with evolving pad, Eno-style generative texture."""

from code_music import EffectsChain, Song, Track, delay, reverb
from code_music.theory import drone, evolving_pad

song = Song(title="Ambient Drift", bpm=40)

# Deep drone on D
drone_notes = drone("D", octave=2, duration=64.0, overtones=5)
bed = song.add_track(Track(name="bed", instrument="pad", volume=0.35, pan=0.0))
bed.extend(drone_notes)

# Evolving pad — slowly morphing cloud
cloud = evolving_pad("D", "major", duration=64.0, density=12, octave=5, seed=42)
pad = song.add_track(Track(name="pad", instrument="triangle", volume=0.3, pan=0.2))
pad.extend(cloud)

# Second cloud, different seed, panned opposite
cloud2 = evolving_pad("D", "major", duration=64.0, density=10, octave=4, seed=77)
pad2 = song.add_track(Track(name="pad2", instrument="triangle", volume=0.25, pan=-0.2))
pad2.extend(cloud2)

song.effects = {
    "bed": EffectsChain().add(reverb, room_size=0.95, wet=0.6),
    "pad": EffectsChain().add(delay, delay_ms=1200, feedback=0.4, wet=0.3),
    "pad2": EffectsChain().add(delay, delay_ms=800, feedback=0.35, wet=0.25),
}
