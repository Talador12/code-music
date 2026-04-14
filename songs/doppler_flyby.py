"""Doppler Flyby - ambulance siren passing by with Doppler pitch shift."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.effects import doppler

song = Song(title="Doppler Flyby", bpm=100, sample_rate=44100)

# Siren tone (will get Doppler-shifted)
siren = song.add_track(Track(name="siren", instrument="sine", volume=0.5))
for _ in range(16):
    siren.add(Note("A", 5, 1.0, velocity=70))
    siren.add(Note("E", 5, 1.0, velocity=70))

# Pad background
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.25))
pad.add(Chord("A", "min", 3, duration=32.0, velocity=30))

# Bass drone
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.4))
bass.add(Note("A", 2, 32.0, velocity=50))

# Apply Doppler to the siren (car at 30 m/s passing 2m away)
song.effects = {
    "siren": lambda samples, sr: doppler(
        samples, sr, speed=30, direction="pass_by", closest_distance=2.0
    ),
    "pad": EffectsChain().add(reverb, room_size=0.8, wet=0.4),
}
