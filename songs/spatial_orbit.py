"""Spatial Orbit - sounds circle the listener's head in 3D."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb, scale
from code_music.effects import orbit

song = Song(title="Spatial Orbit", bpm=80, sample_rate=44100)

# Center drone (no spatial)
drone = song.add_track(Track(name="drone", instrument="pad", volume=0.3))
drone.add(Chord("D", "min", 3, duration=32.0, velocity=35))

# Orbiting lead (applied via effects)
lead = song.add_track(Track(name="orbit_lead", instrument="triangle", volume=0.4))
lead.extend(scale("D", "pentatonic_minor", octave=5, length=32))

# Static spatial positions: bass behind-left, shimmer above-right
bass = song.add_track(
    Track(
        name="bass",
        instrument="bass",
        volume=0.5,
        spatial_azimuth=-135,
        spatial_distance=2.0,
    )
)
for root in ["D"] * 8:
    bass.add(Note(root, 2, 4.0, velocity=55))

shimmer = song.add_track(
    Track(
        name="shimmer",
        instrument="sine",
        volume=0.2,
        spatial_azimuth=60,
        spatial_elevation=30,
        spatial_distance=3.0,
    )
)
for note in ["A", "D", "F", "A"] * 4:
    shimmer.add(Note(note, 6, 2.0, velocity=25))

# Apply orbit to the lead via effects
song.effects = {
    "orbit_lead": lambda samples, sr: orbit(samples, sr, rate=0.2, radius=1.5),
    "drone": EffectsChain().add(reverb, room_size=0.9, wet=0.4),
}
