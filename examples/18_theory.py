"""Example 18: Music Theory Intelligence.

Chord-scale theory, available tensions, smart bass line and drum generation,
and song diffing for collaboration.

Run:
    code-music examples/18_theory.py --play
"""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import (
    available_tensions,
    chord_scale,
    generate_bass_line,
    generate_drums,
    song_diff,
)

# ---------------------------------------------------------------------------
# Step 1: Chord-scale theory
# ---------------------------------------------------------------------------

print("Chord-scale analysis:")
for root, shape in [("C", "min7"), ("G", "dom7"), ("F", "maj7")]:
    scales = chord_scale(root, shape)
    tensions = available_tensions(root, shape)
    print(f"  {root}{shape}: scales={scales}, tensions={tensions}")

# ---------------------------------------------------------------------------
# Step 2: Generate a bass line from chords
# ---------------------------------------------------------------------------

progression = [("A", "min7"), ("D", "min7"), ("G", "dom7"), ("C", "maj7")]
bass_notes = generate_bass_line(progression, style="walking", seed=42)
print(f"\nWalking bass: {len(bass_notes)} notes")

# ---------------------------------------------------------------------------
# Step 3: Generate drums for a genre
# ---------------------------------------------------------------------------

drums = generate_drums("jazz", bars=4)
print(
    f"Jazz drums: kick={len(drums['kick'])}, snare={len(drums['snare'])}, hat={len(drums['hat'])}"
)

# ---------------------------------------------------------------------------
# Step 4: Build a song using theory-generated parts
# ---------------------------------------------------------------------------

song = Song(title="Theory Demo", bpm=120, sample_rate=22050)

# Chords
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4, pan=-0.15))
for root, shape in progression:
    pad.add(Chord(root, shape, 3, duration=4.0))

# Theory-generated bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
bass.extend(bass_notes)

# Theory-generated drums
for name, notes in drums.items():
    instr = {"kick": "drums_kick", "snare": "drums_snare", "hat": "drums_hat"}[name]
    tr = song.add_track(Track(name=name, instrument=instr, volume=0.5))
    tr.extend(notes)

# Lead melody
lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.2))
for note in ["A", "C", "E", "G", "F", "E", "D", "C", "B", "D", "F", "A", "G", "E", "C", "B"]:
    lead.add(Note(note, 5, 1.0))

song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}

# ---------------------------------------------------------------------------
# Step 5: Song diffing
# ---------------------------------------------------------------------------

song2 = Song(title="Theory Demo v2", bpm=130, sample_rate=22050)
song2.add_track(Track(name="pad", instrument="pad", volume=0.5))
song2.add_track(Track(name="synth", instrument="sawtooth", volume=0.4))

changes = song_diff(song, song2)
print(f"\nSong diff ({len(changes)} changes):")
for c in changes:
    print(f"  {c}")
