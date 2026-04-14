"""Example 15: Automation, EnvFollower, and Clip Looping.

Demonstrates:
- Automation curves for volume fades
- EnvFollower for sidechain ducking (kick ducks the pad)
- ModMatrix routing
- Clip extraction and looping
- Song overlay composition
"""

from code_music import (
    Chord,
    Clip,
    EnvFollower,
    Note,
    Song,
    Track,
    scale,
)
from code_music.automation import Automation, ModMatrix

# --- Song setup ---
song = Song(title="Automation Demo", bpm=120, sample_rate=22050)

# --- Drums: build a 2-bar pattern, then clip-loop it ---
drums = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
for _ in range(2):
    drums.add(Note("C", 4, 1.0, velocity=90))
    drums.add(Note.rest(1.0))
    drums.add(Note("C", 4, 1.0, velocity=70))
    drums.add(Note.rest(1.0))

# Extract the 2-bar pattern as a Clip, loop it 4x for 8 bars total
kick_clip = Clip.from_track(drums, 0, 8)
looped_kicks = kick_clip.loop(3)  # 3 more repetitions (4 total with original)
drums.extend(looped_kicks.to_events())

# --- Hi-hat: clip from a short pattern ---
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.4))
for _ in range(4):
    hat.add(Note("C", 6, 0.5, velocity=50))
hat_clip = Clip.from_track(hat, 0, 4)
hat.extend(hat_clip.loop(7).to_events())  # loop to fill 8 bars

# --- Pad: sustained chords that will get ducked ---
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.5, pan=-0.2))
for root, shape in [("A", "min7"), ("D", "min7"), ("G", "dom7"), ("C", "maj7")]:
    pad.add(Chord(root, shape, 3, duration=8.0, velocity=50))

# --- Bass ---
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
for root in ["A", "A", "D", "D", "G", "G", "C", "C"]:
    bass.add(Note(root, 2, 4.0, velocity=70))

# --- Lead with volume automation (fade in over 4 bars) ---
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.5, pan=0.3))
melody = scale("A", "pentatonic_minor", octave=5, length=32)
lead.extend(melody)

# Automation curve: fade in from 0 to full over 16 beats (4 bars)
vol_auto = Automation([(0, 0.0), (16, 0.8), (24, 0.5), (32, 0.3)])

# Sample the curve (for documentation - in practice, effects apply at render)
values = vol_auto.sample(bpm=120, sr=22050, duration_beats=32)
print(f"  Volume automation: {len(values)} samples")
print(f"  Start: {values[0]:.2f}, Peak: {max(values):.2f}, End: {values[-1]:.2f}")

# --- ModMatrix: LFO on pad pan ---
mm = ModMatrix()
mm.connect("lfo1", "pad.pan", amount=0.4, rate=0.25)
print(f"  ModMatrix: {mm}")

# --- EnvFollower: kick ducks the pad ---
env = EnvFollower(attack_ms=5, release_ms=150)
print(f"  EnvFollower: attack={env.attack_ms}ms, release={env.release_ms}ms")

# Wire into ModMatrix
mm.connect_env_follower(
    "pad.volume", sidechain_audio=None or __import__("numpy").zeros(1000), amount=-0.7
)
print(f"  ModMatrix with envelope follower: {mm}")

# --- Clip operations demo ---
print("\n  Clip operations:")
clip = Clip.from_track(drums, 0, 4)
print(f"  Original: {clip}")
print(f"  Looped 4x: {clip.loop(4)}")
print(f"  Reversed: {clip.reverse()}")
print(f"  Trimmed [1:3]: {clip.trim(1, 3)}")
print(f"  Duration: {clip.duration} beats")

print(f"\n  Song: '{song.title}', {len(song.tracks)} tracks, {song.bpm} BPM")
