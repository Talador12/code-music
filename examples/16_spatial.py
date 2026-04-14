"""Example 16: Spatial Audio - 3D positioning, orbiting, and ambisonics.

Demonstrates:
- spatial_pan: place sounds in 3D space (azimuth, elevation, distance)
- orbit: sounds circle the listener
- encode_bformat/decode_bformat: first-order ambisonics pipeline
- spatial_mix: render a Song with 3D track positions
- Track spatial attributes
"""

import numpy as np

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    decode_bformat,
    encode_bformat,
    orbit,
    scale,
    spatial_mix,
    spatial_pan,
    sum_bformat,
)

# --- 1. Basic spatial_pan: place a tone at 45 degrees right ---
print("1. Spatial pan demo")
t = np.linspace(0, 1.0, 22050)
tone = np.sin(2 * np.pi * 440 * t) * 0.3
right_45 = spatial_pan(tone, 22050, azimuth=45, elevation=0, distance=1.5)
print(f"   Input: mono {tone.shape}, Output: stereo {right_45.shape}")

# --- 2. Orbit: tone circles the listener ---
print("\n2. Orbit demo")
orbiting = orbit(tone, 22050, rate=0.5, radius=2.0)
print(f"   Orbiting at 0.5 Hz, radius 2.0: {orbiting.shape}")

# --- 3. Ambisonics: encode, sum, decode ---
print("\n3. Ambisonics pipeline")
# Two sources at different positions
src_a = np.sin(2 * np.pi * 440 * t) * 0.2
src_b = np.sin(2 * np.pi * 554 * t) * 0.2

bf_a = encode_bformat(src_a, azimuth=-30, elevation=0, distance=1.0)
bf_b = encode_bformat(src_b, azimuth=60, elevation=15, distance=2.0)
print(f"   Source A at -30 deg: B-format {bf_a.shape}")
print(f"   Source B at +60 deg: B-format {bf_b.shape}")

# Sum into one sound field
combined = sum_bformat(bf_a, bf_b)
print(f"   Combined B-format: {combined.shape}")

# Decode to various layouts
binaural = decode_bformat(combined, "binaural", 22050)
stereo = decode_bformat(combined, "stereo", 22050)
quad = decode_bformat(combined, "quad", 22050)
surround = decode_bformat(combined, "5.1", 22050)
print(f"   Binaural: {binaural.shape}")
print(f"   Stereo:   {stereo.shape}")
print(f"   Quad:     {quad.shape}")
print(f"   5.1:      {surround.shape}")

# --- 4. spatial_mix: render a Song with 3D positions ---
print("\n4. Spatial mix demo")
song = Song(title="Spatial Demo", bpm=120, sample_rate=22050)

# Piano at front-left
piano = song.add_track(
    Track(
        name="piano",
        instrument="piano",
        volume=0.5,
        spatial_azimuth=-30,
        spatial_distance=1.5,
    )
)
piano.extend(scale("C", "major", octave=4, length=8))

# Bass at center-behind
bass = song.add_track(
    Track(
        name="bass",
        instrument="bass",
        volume=0.6,
        spatial_azimuth=170,
        spatial_distance=2.0,
    )
)
for root in ["C", "G", "A", "F"]:
    bass.add(Note(root, 2, 2.0, velocity=65))

# Pad with no spatial (uses standard pan)
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3, pan=-0.2))
pad.add(Chord("C", "maj7", 3, duration=8.0, velocity=40))

audio = spatial_mix(song, 22050, layout="binaural")
print(f"   Song: {len(song.tracks)} tracks, binaural output: {audio.shape}")
print(f"   Peak amplitude: {np.max(np.abs(audio)):.3f}")
