"""Portable Preset — custom SoundDesigner survives JSON serialization."""

from code_music import Chord, EffectsChain, Note, Song, SoundDesigner, Track, reverb
from code_music.serialization import song_from_json, song_to_json

fm_piano = (
    SoundDesigner("fm_piano")
    .fm("sine", mod_ratio=2.0, mod_index=3.5, volume=0.8)
    .fm("sine", mod_ratio=1.0, mod_index=0.5, volume=0.2)
    .envelope(attack=0.005, decay=0.4, sustain=0.2, release=0.5)
    .filter("lowpass", cutoff=4000, resonance=0.3)
)

original = Song(title="Portable Preset", bpm=90, sample_rate=44100)
original.register_instrument("fm_piano", fm_piano)

tr = original.add_track(Track(name="piano", instrument="fm_piano", volume=0.5))
for n, o in [("D", 4), ("F", 4), ("A", 4), ("D", 5), ("C", 5), ("A", 4), ("F", 4), ("D", 4)]:
    tr.add(Note(n, o, 1.0))
tr_pad = original.add_track(Track(name="pad", instrument="pad", volume=0.3))
tr_pad.add(Chord("D", "min7", 3, duration=8.0))

# Serialize, restore, render
song = song_from_json(song_to_json(original))
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.7, wet=0.3)}
print(f"Preset preserved: {'fm_piano' in song._custom_instruments}")
