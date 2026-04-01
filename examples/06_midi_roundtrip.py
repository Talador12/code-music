"""06 — MIDI round-trip: export a song to MIDI, import it back, remix.

Run:  code-music examples/06_midi_roundtrip.py --play

This example:
1. Creates a simple song
2. Exports it to MIDI
3. Imports the MIDI back as a new Song
4. Changes the BPM and instruments (remix)
"""

import tempfile
from pathlib import Path

from code_music import Note, Song, Track
from code_music.midi import export_midi, import_midi

# Step 1: Create a song
original = Song(title="Original", bpm=120)
piano = original.add_track(Track(name="piano", instrument="piano"))
piano.extend(
    [
        Note("C", 4, 1.0),
        Note("E", 4, 1.0),
        Note("G", 4, 1.0),
        Note("C", 5, 1.0),
        Note("B", 4, 1.0),
        Note("G", 4, 1.0),
        Note("E", 4, 1.0),
        Note("C", 4, 1.0),
    ]
)
bass = original.add_track(Track(name="bass", instrument="bass"))
bass.extend([Note("C", 2, 2.0), Note("G", 2, 2.0), Note("A", 2, 2.0), Note("E", 2, 2.0)])

# Step 2: Export to MIDI
midi_path = Path(tempfile.gettempdir()) / "roundtrip_demo.mid"
export_midi(original, midi_path)
print(f"Exported to {midi_path}")

# Step 3: Import it back
imported = import_midi(midi_path, title="Remixed")
print(f"Imported: {imported.title}, {len(imported.tracks)} tracks, {imported.bpm} BPM")

# Step 4: Remix — slow it down and change the vibe
imported.bpm = 80  # slow it way down
for track in imported.tracks:
    if "drum" not in track.instrument:
        track.instrument = "pad"  # everything becomes a pad wash

# This is the song that gets rendered
song = imported
