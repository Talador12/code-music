"""Example 16: Production Mastering Pipeline.

Make your songs release-ready with LUFS loudness normalization, true peak
limiting, dithering, and stereo imaging analysis.

Run:
    code-music examples/16_mastering.py --play
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    Track,
    delay,
    reverb,
)
from code_music.mastering import (
    master_audio,
    measure_lufs,
    stereo_analysis,
)

# ---------------------------------------------------------------------------
# Step 1: Build a song
# ---------------------------------------------------------------------------

song = Song(title="Mastering Demo", bpm=120, sample_rate=22050)

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
for _ in range(4):
    bass.add(Note("C", 2, 2.0))

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4, pan=-0.15))
pad.add(Chord("C", "min7", 3, duration=8.0))

lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.2))
for note in ["C", "Eb", "G", "Bb", "Ab", "G", "Eb", "C"]:
    lead.add(Note(note, 5, 1.0))

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.3),
    "lead": EffectsChain().add(delay, delay_ms=250, feedback=0.2, wet=0.15),
}

# ---------------------------------------------------------------------------
# Step 2: Render and analyze
# ---------------------------------------------------------------------------

audio = song.render()
sr = song.sample_rate

print(f"Pre-master LUFS: {measure_lufs(audio, sr):.1f}")
print(f"Pre-master stereo: {stereo_analysis(audio)}")

# ---------------------------------------------------------------------------
# Step 3: Master with the full chain
# ---------------------------------------------------------------------------

# Option A: Full chain in one call (recommended)
mastered = master_audio(audio, sr, target_lufs=-14.0, ceiling_db=-1.0, dither_bits=16)

print(f"Post-master LUFS: {measure_lufs(mastered, sr):.1f}")
print(f"Post-master stereo: {stereo_analysis(mastered)}")

# Option B: Step by step (for fine control)
# from code_music.mastering import normalize_lufs, true_peak_limit, dither
# step1 = normalize_lufs(audio, sr, target_lufs=-14.0)
# step2 = true_peak_limit(step1, sr, ceiling_db=-1.0)
# step3 = dither(step2, bit_depth=16)
