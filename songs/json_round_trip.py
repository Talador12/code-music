"""JSON Round Trip — song serialized and restored to prove round-trip fidelity."""

from code_music import Chord, EffectsChain, Note, Song, SoundDesigner, Track, reverb
from code_music.serialization import song_from_json, song_to_json

# Build original
original = Song(title="JSON Round Trip", bpm=110, sample_rate=44100)
sd = (
    SoundDesigner("warm")
    .add_osc("triangle", volume=0.5)
    .add_osc("sine", detune_cents=3, volume=0.3)
    .envelope(attack=0.2, decay=0.1, sustain=0.6, release=0.5)
    .filter("lowpass", cutoff=2000, resonance=0.5)
)
original.register_instrument("warm", sd)
tr = original.add_track(Track(name="lead", instrument="warm", volume=0.5))
for n in ["A", "C", "E", "G", "F", "E", "C", "A"]:
    tr.add(Note(n, 5, 1.0))
tr_pad = original.add_track(Track(name="pad", instrument="pad", volume=0.35))
tr_pad.add(Chord("A", "min7", 3, duration=8.0))

# Serialize and restore
data = song_to_json(original)
song = song_from_json(data)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.7, wet=0.3)}
print(f"Round-tripped: {song.title}, {len(song.tracks)} tracks")
