"""Serialized Symphony — built, serialized to JSON, restored, then rendered."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb
from code_music.serialization import song_from_json, song_to_json
from code_music.theory import generate_bass_line, generate_drums

original = Song(title="Serialized Symphony", bpm=100, sample_rate=44100)
prog = [("C", "min7"), ("Ab", "maj7"), ("Eb", "maj"), ("Bb", "dom7")]

original.add_track(Track(name="pad", instrument="pad", volume=0.4, pan=-0.1)).extend(
    [Chord(r, s, 3, duration=4.0) for r, s in prog]
)
original.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(
    generate_bass_line(prog, style="root_fifth")
)
drums = generate_drums("rock", bars=4)
for name, notes in drums.items():
    instr = {"kick": "drums_kick", "snare": "drums_snare", "hat": "drums_hat"}[name]
    original.add_track(Track(name=name, instrument=instr, volume=0.5)).extend(notes)
original.add_track(Track(name="lead", instrument="piano", volume=0.45, pan=0.15)).extend(
    [
        Note(n, 5, 1.0)
        for n in [
            "C",
            "Eb",
            "G",
            "Bb",
            "Ab",
            "G",
            "Eb",
            "C",
            "Bb",
            "Ab",
            "Eb",
            "Bb",
            "G",
            "Eb",
            "C",
            "Bb",
        ]
    ]
)

# Serialize + restore
song = song_from_json(song_to_json(original))
song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.3),
    "lead": EffectsChain().add(delay, delay_ms=250, feedback=0.2, wet=0.15),
}
