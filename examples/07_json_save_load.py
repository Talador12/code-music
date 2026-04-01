"""07 — JSON save/load: serialize a song to disk and reload it.

Run:  code-music examples/07_json_save_load.py --play

This example:
1. Creates a song with effects
2. Saves it to JSON
3. Loads it back
4. Proves the round-trip works by rendering the loaded version
"""

import tempfile
from pathlib import Path

from code_music import Chord, EffectsChain, Note, Song, Track, reverb

# Step 1: Build a song
original = Song(title="Serializable Song", bpm=100)
pad = original.add_track(Track(name="pad", instrument="pad", volume=0.4))
for _ in range(4):
    pad.extend([Chord("F", "min7", 3, duration=4.0), Chord("Db", "maj7", 3, duration=4.0)])

lead = original.add_track(Track(name="lead", instrument="piano", volume=0.5))
lead.extend(
    [
        Note("F", 5, 1.0),
        Note("Ab", 5, 0.5),
        Note("C", 6, 0.5),
        Note("Bb", 5, 1.0),
        Note("Ab", 5, 1.0),
    ]
    * 4
)

original.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35, label="reverb"),
}

# Step 2: Save to JSON
json_path = Path(tempfile.gettempdir()) / "saved_song.json"
original.export_json(json_path)
print(f"Saved to {json_path} ({json_path.stat().st_size} bytes)")

# Step 3: Load it back
loaded = Song.load_json(json_path)
print(f"Loaded: {loaded.title}, {len(loaded.tracks)} tracks, {loaded.bpm} BPM")
print(f"Effects restored: {list(loaded.effects.keys())}")

# Step 4: The loaded song renders identically
song = loaded
