"""Example 19: JSON Serialization — save and load songs as JSON.

Full round-trip: Song → JSON → Song. Includes tracks, notes, chords,
custom instruments, and metadata. Enables collaboration, web export,
and version control.

Run:
    code-music examples/19_json_export.py --play
"""

import json

from code_music import Chord, EffectsChain, Note, Song, SoundDesigner, Track, reverb
from code_music.serialization import song_from_json, song_to_json

# ---------------------------------------------------------------------------
# Step 1: Build a song with custom instruments
# ---------------------------------------------------------------------------

supersaw = (
    SoundDesigner("supersaw")
    .add_osc("sawtooth", volume=0.3)
    .add_osc("sawtooth", detune_cents=10, volume=0.25)
    .add_osc("sawtooth", detune_cents=-10, volume=0.25)
    .envelope(attack=0.02, decay=0.1, sustain=0.7, release=0.4)
    .filter("lowpass", cutoff=4000, resonance=0.6)
)

song = Song(title="JSON Demo", bpm=128, sample_rate=22050)
song.register_instrument("supersaw", supersaw)

lead = song.add_track(Track(name="lead", instrument="supersaw", volume=0.5, pan=0.2))
for note in ["C", "Eb", "G", "Bb", "Ab", "G", "Eb", "C"]:
    lead.add(Note(note, 5, 1.0))

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4, pan=-0.15))
pad.add(Chord("C", "min7", 3, duration=8.0))

# ---------------------------------------------------------------------------
# Step 2: Serialize to JSON
# ---------------------------------------------------------------------------

data = song_to_json(song)
print(f"Serialized: {len(json.dumps(data))} bytes")
print(f"Title: {data['title']}")
print(f"Tracks: {len(data['tracks'])}")
print(f"Custom instruments: {list(data['custom_instruments'].keys())}")

# As a string
json_str = song_to_json(song, as_string=True)
print(f"\nJSON string: {len(json_str)} chars")

# ---------------------------------------------------------------------------
# Step 3: Restore from JSON
# ---------------------------------------------------------------------------

restored = song_from_json(data)
print(f"\nRestored: {restored.title}, {len(restored.tracks)} tracks")
print(f"Custom instruments: {list(restored._custom_instruments.keys())}")

# The restored song renders identically
audio = restored.render()
print(f"Rendered: {audio.shape[0]} samples")

restored.effects = {"pad": EffectsChain().add(reverb, room_size=0.7, wet=0.3)}

# Use restored as the final song variable (for smoke test compatibility)
song = restored
