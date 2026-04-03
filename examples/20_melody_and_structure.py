"""Example 20: Melody Continuation, Song Structure, and Lead Sheets.

Three composition tools:
- continue_melody(): extend a melodic fragment using Markov chains
- Verse/Chorus/Bridge: named section types for arrangement
- to_lead_sheet(): render a song as ASCII chord + melody notation

Run:
    code-music examples/20_melody_and_structure.py --play
"""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.composition import Chorus, Verse, continue_melody, to_lead_sheet

# ---------------------------------------------------------------------------
# Step 1: Melody continuation — extend a seed phrase
# ---------------------------------------------------------------------------

seed = [Note("C", 5, 0.5), Note("E", 5, 0.5), Note("G", 5, 0.5), Note("A", 5, 0.5)]
melody = continue_melody(seed, bars=4, key="C", mode="major", seed_rng=42)
print(f"Seed: {len(seed)} notes → Extended: {len(melody)} notes")

# ---------------------------------------------------------------------------
# Step 2: Named sections — organize your arrangement
# ---------------------------------------------------------------------------

verse = Verse(bars=8)
verse.add_track("lead", melody[:16])
verse.add_track("pad", [Chord("C", "min7", 3, duration=8.0)])

chorus = Chorus(bars=8)
chorus.add_track("lead", melody[16:32] if len(melody) > 16 else melody)
chorus.add_track("pad", [Chord("Ab", "maj7", 3, duration=8.0)])

print(f"Verse: {verse}")
print(f"Chorus: {chorus}")

# ---------------------------------------------------------------------------
# Step 3: Build a song from sections
# ---------------------------------------------------------------------------

song = Song(title="Melody & Structure", bpm=120, sample_rate=22050)

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4, pan=-0.15))
pad.add(Chord("C", "min7", 3, duration=8.0))
pad.add(Chord("Ab", "maj7", 3, duration=8.0))

lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.2))
lead.extend(melody)

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
bass.add(Note("C", 2, 8.0))
bass.add(Note("Ab", 1, 8.0))

song.effects = {"pad": EffectsChain().add(reverb, room_size=0.7, wet=0.3)}

# ---------------------------------------------------------------------------
# Step 4: Lead sheet
# ---------------------------------------------------------------------------

print(f"\n{to_lead_sheet(song)}")
