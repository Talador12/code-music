"""JSON Collab v2 — serialized song exchange with theory + analysis."""

from code_music import Chord, EffectsChain, Note, Song, Track, euclid, reverb
from code_music.composition import song_summary, to_lead_sheet
from code_music.serialization import song_from_json, song_to_json
from code_music.theory import analyze_harmony, generate_bass_line, generate_drums

# Build
original = Song(title="JSON Collab v2", bpm=120, sample_rate=44100, key_sig="Am")
prog = [("A", "min7"), ("D", "min7"), ("G", "dom7"), ("C", "maj7")]
original.add_track(Track(name="pad", instrument="pad", volume=0.35)).extend(
    [Chord(r, s, 3, duration=4.0) for r, s in prog]
)
original.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(
    generate_bass_line(prog, style="root_fifth")
)
drums = generate_drums("jazz", bars=4)
for name, notes in drums.items():
    instr = {"kick": "drums_kick", "snare": "drums_snare", "hat": "drums_hat"}[name]
    original.add_track(Track(name=name, instrument=instr, volume=0.4)).extend(notes)
original.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15)).extend(
    [
        Note(n, 5, 1.0)
        for n in ["A", "C", "E", "G", "F", "D", "G", "B", "E", "G", "B", "D", "C", "E", "G", "C"]
    ]
)

# Serialize → restore → analyze
song = song_from_json(song_to_json(original))
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
print(song_summary(song))
for a in analyze_harmony(song, key="C"):
    print(f"  {a['roman']}{a['quality']} ({a['function']})")
