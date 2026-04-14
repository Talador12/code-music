"""Binaural Jazz - each instrument positioned in 3D space."""

from code_music import Chord, Note, Song, Track
from code_music.effects import spatial_pan

song = Song(title="Binaural Jazz", bpm=140, sample_rate=44100)

# Piano: slightly left
piano = song.add_track(
    Track(
        name="piano",
        instrument="piano",
        volume=0.45,
        spatial_azimuth=-25,
        spatial_distance=1.5,
    )
)
for root, shape in [("D", "min7"), ("G", "dom7"), ("C", "maj7"), ("A", "dom7")] * 4:
    piano.add(Chord(root, shape, 4, duration=2.0, velocity=50))

# Bass: center, slightly behind
bass = song.add_track(
    Track(
        name="bass",
        instrument="bass",
        volume=0.55,
        spatial_azimuth=0,
        spatial_distance=2.0,
    )
)
for root in ["D", "G", "C", "A"] * 8:
    bass.add(Note(root, 2, 1.0, velocity=65))

# Drums: slightly right
drums = song.add_track(
    Track(
        name="drums",
        instrument="drums_hat",
        volume=0.3,
        spatial_azimuth=15,
        spatial_distance=1.8,
    )
)
for _ in range(64):
    drums.add(Note("C", 6, 0.5, velocity=35))

# Sax (sawtooth): right
sax = song.add_track(
    Track(
        name="sax",
        instrument="sawtooth",
        volume=0.4,
        spatial_azimuth=40,
        spatial_distance=1.5,
        spatial_elevation=5,
    )
)
from code_music import scale

sax.extend(scale("D", "dorian", octave=5, length=32))

# Apply spatial positioning as effects
song.effects = {
    name: (
        lambda az=tr.spatial_azimuth, el=tr.spatial_elevation, d=tr.spatial_distance: (
            lambda samples, sr: spatial_pan(samples, sr, azimuth=az, elevation=el, distance=d)
        )
    )()
    for name, tr in [(t.name, t) for t in song.tracks]
    if tr.spatial_azimuth is not None
}
