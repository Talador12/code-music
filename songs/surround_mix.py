"""Surround Mix - 5.1 surround sound via ambisonics pipeline."""

from code_music import Note, Song, Track, scale

song = Song(title="Surround Mix", bpm=110, sample_rate=44100)

# Front-left piano
piano = song.add_track(
    Track(
        name="piano",
        instrument="piano",
        volume=0.5,
        spatial_azimuth=-30,
        spatial_elevation=0,
        spatial_distance=1.5,
    )
)
piano.extend(scale("C", "major", octave=4, length=16))

# Front-right strings
strings = song.add_track(
    Track(
        name="strings",
        instrument="pad",
        volume=0.35,
        spatial_azimuth=30,
        spatial_elevation=0,
        spatial_distance=2.0,
    )
)
from code_music import Chord

for root, shape in [("C", "maj7"), ("F", "maj7"), ("G", "dom7"), ("C", "maj")] * 2:
    strings.add(Chord(root, shape, 4, duration=4.0, velocity=40))

# Rear-left ambient
ambient = song.add_track(
    Track(
        name="ambient",
        instrument="triangle",
        volume=0.2,
        spatial_azimuth=135,
        spatial_elevation=10,
        spatial_distance=3.0,
    )
)
for note in ["E", "G", "B", "D"] * 4:
    ambient.add(Note(note, 6, 2.0, velocity=20))

# Center bass
bass = song.add_track(
    Track(
        name="bass",
        instrument="bass",
        volume=0.55,
        spatial_azimuth=0,
        spatial_distance=1.0,
    )
)
for root in ["C", "C", "F", "G"] * 2:
    bass.add(Note(root, 2, 2.0, velocity=65))

# Standard stereo drums (no spatial)
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7))
for _ in range(16):
    kick.add(Note("C", 4, 1.0, velocity=80))
    kick.add(Note.rest(1.0))
