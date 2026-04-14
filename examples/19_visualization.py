"""Example 19: Visualization - all 6 SVG visualization types.

Demonstrates:
- to_piano_roll(): note rectangles on pitch x time grid
- to_svg_waveform(): amplitude envelope of rendered audio
- to_track_waveforms(): stacked per-track waveforms
- to_harmonic_rhythm(): chord change timeline
- to_spectrogram(): STFT frequency x time heat map
- to_sheet_music(): traditional staff notation
"""

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    scale,
    to_harmonic_rhythm,
    to_piano_roll,
    to_sheet_music,
    to_spectrogram,
    to_svg_waveform,
    to_track_waveforms,
)

# Build a song to visualize
song = Song(title="Visualization Demo", bpm=120, sample_rate=22050)

lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15))
lead.extend(scale("C", "major", octave=5, length=16))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root in ["C", "C", "F", "G"] * 2:
    bass.add(Note(root, 2, 2.0, velocity=65))

chords = song.add_track(Track(name="chords", instrument="pad", volume=0.35, pan=-0.1))
for root, shape in [("C", "maj7"), ("F", "maj"), ("G", "dom7"), ("C", "maj")] * 2:
    chords.add(Chord(root, shape, 4, duration=4.0, velocity=45))

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7))
for _ in range(16):
    kick.add(Note("C", 4, 1.0, velocity=75))

# --- 1. Piano Roll ---
print("1. Piano Roll")
svg = to_piano_roll(song)
print(f"   {len(svg)} chars SVG, note rectangles on pitch x time grid")

# --- 2. Waveform ---
print("\n2. Waveform")
svg = to_svg_waveform(song)
print(f"   {len(svg)} chars SVG, amplitude envelope")

# --- 3. Per-Track Waveforms ---
print("\n3. Per-Track Waveforms")
svg = to_track_waveforms(song)
print(f"   {len(svg)} chars SVG, {len(song.tracks)} stacked tracks")

# --- 4. Harmonic Rhythm ---
print("\n4. Harmonic Rhythm")
svg = to_harmonic_rhythm(song)
print(f"   {len(svg)} chars SVG, chord change timeline")

# --- 5. Spectrogram ---
print("\n5. Spectrogram")
svg = to_spectrogram(song)
print(f"   {len(svg)} chars SVG, STFT frequency x time heat map")

# --- 6. Sheet Music ---
print("\n6. Sheet Music")
svg = to_sheet_music(song, track_index=0)
print(f"   {len(svg)} chars SVG, staff notation for '{song.tracks[0].name}'")

print(f"\nAll 6 visualization types generated for '{song.title}'")
