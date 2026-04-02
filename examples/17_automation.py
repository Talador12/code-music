"""Example 17: Parameter Automation and Modulation Matrix.

Automate volume, pan, and filter parameters over time. Route LFO
modulation to multiple destinations through a mod matrix.

Run:
    code-music examples/17_automation.py --play
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    Track,
    reverb,
)
from code_music.automation import Automation, ModMatrix

# ---------------------------------------------------------------------------
# Step 1: Automation — keyframed parameter curves
# ---------------------------------------------------------------------------

# Volume fade in over 4 beats, sustain, then fade out
vol_curve = Automation([(0, 0.0), (4, 0.8), (12, 0.8), (16, 0.0)])

# Pan sweep left to right
pan_curve = Automation([(0, -0.8), (8, 0.8), (16, -0.8)])

# Sample the curves into per-sample arrays
sr = 22050
bpm = 120
vol_values = vol_curve.sample(bpm, sr, duration_beats=16)
pan_values = pan_curve.sample(bpm, sr, duration_beats=16)

print(f"Volume curve: {vol_curve}")
print(f"Pan curve: {pan_curve}")
print(f"Sampled {len(vol_values)} volume values, {len(pan_values)} pan values")

# ---------------------------------------------------------------------------
# Step 2: Modulation Matrix
# ---------------------------------------------------------------------------

mm = ModMatrix()
mm.connect("lfo1", "pad.volume", amount=0.3, rate=0.5)
mm.connect("lfo2", "lead.pan", amount=0.4, rate=0.25)
mm.connect("random", "lead.volume", amount=0.1)

print(f"\n{mm}")
for route in mm.routes:
    print(f"  {route['source']} → {route['dest']} (amount={route['amount']})")

# Generate mod signals
lfo_signal = mm.generate_mod_signal("lfo1", sr * 4, sr, rate=0.5)
print(
    f"\nLFO signal: {len(lfo_signal)} samples, range [{lfo_signal.min():.2f}, {lfo_signal.max():.2f}]"
)

# ---------------------------------------------------------------------------
# Step 3: Build a song (automation would be applied during render in future)
# ---------------------------------------------------------------------------

song = Song(title="Automation Demo", bpm=bpm, sample_rate=sr)

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.5, pan=-0.2))
pad.add(Chord("A", "min7", 3, duration=8.0))
pad.add(Chord("F", "maj7", 3, duration=8.0))

lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.2))
for note in ["A", "C", "E", "G", "F", "E", "C", "A", "G", "A", "C", "E", "D", "C", "A", "G"]:
    lead.add(Note(note, 5, 1.0))

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7))
for _ in range(16):
    kick.add(Note("C", 2, 1.0))

song.effects = {"pad": EffectsChain().add(reverb, room_size=0.7, wet=0.3)}
