"""Example 14: Pattern Language — TidalCycles-inspired note patterns.

Build note sequences from mini-notation strings, transform them with
reverse/every/degrade/polymeter, and convert directly to Tracks.

Run:
    code-music examples/14_patterns.py --play
"""

from code_music import (
    EffectsChain,
    Pattern,
    Song,
    Track,
    euclid,
    reverb,
)

# ---------------------------------------------------------------------------
# Step 1: Basic patterns from mini-notation
# ---------------------------------------------------------------------------

# Simple melody — spaces separate notes
melody = Pattern("C5 E5 G5 C6 G5 E5 D5 C5")

# Rests with ~
bass_line = Pattern("C3 ~ ~ C3 ~ Eb3 ~ G3")

# Repeat with *
hi_hat = Pattern("F#6*8")  # 8 hits in a row

# ---------------------------------------------------------------------------
# Step 2: Pattern transforms
# ---------------------------------------------------------------------------

# Reverse
melody_back = melody.reverse()

# Every 4th repetition, reverse the pattern (creates AAAB variation)
evolving = melody.every(4, lambda p: p.reverse())

# Degrade: randomly drop notes (50% survive)
sparse = melody.degrade(0.5, seed=42)

# ---------------------------------------------------------------------------
# Step 3: Polymeter — layer patterns of different lengths
# ---------------------------------------------------------------------------

# 3-note pattern cycles against a 4-note pattern → interesting phase
three = Pattern("C4 E4 G4")
four = Pattern("A3 B3 C4 D4")
poly = Pattern.polymeter(three, four)  # 12 steps (LCM of 3 and 4)

# ---------------------------------------------------------------------------
# Step 4: Build a song from patterns
# ---------------------------------------------------------------------------

song = Song(title="Pattern Language", bpm=120, sample_rate=22050)

# Lead: evolving pattern (melody + reversed every 4th cycle)
lead = song.add_track(Track(name="lead", instrument="piano", volume=0.6))
lead.extend(evolving.to_notes(0.5))

# Bass from pattern with rests
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
bass.extend(bass_line.to_notes(0.5))
bass.extend(bass_line.to_notes(0.5))

# Sparse melody (degraded)
ghost = song.add_track(Track(name="ghost", instrument="pad", volume=0.3, pan=0.2))
ghost.extend(sparse.to_notes(0.5))
ghost.extend(sparse.to_notes(0.5))

# Hi-hat
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.3))
hat.extend(hi_hat.to_notes(0.25))
hat.extend(hi_hat.to_notes(0.25))

# Kick: euclidean (still available alongside patterns)
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7))
for _ in range(4):
    kick.extend(euclid(3, 8, "C", 2, 0.5))

song.effects = {
    "ghost": EffectsChain().add(reverb, room_size=0.8, wet=0.4),
    "lead": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
}
