"""Harmonic Pace — fast vs slow chord changes."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import harmonic_rhythm

song = Song(title="Harmonic Pace", bpm=120, sample_rate=44100)
song.add_track(Track(name="fast", instrument="pad", volume=0.4, pan=-0.2)).extend(
    [Chord(r, "maj", 3, duration=1.0) for r in ["C", "G", "Am", "F"] * 2]
)
song.add_track(Track(name="slow", instrument="pad", volume=0.4, pan=0.2)).extend(
    [Chord(r, "maj", 3, duration=4.0) for r in ["C", "G"]]
)
song.add_track(Track(name="lead", instrument="piano", volume=0.5)).extend(
    [
        Note(n, 5, 0.5)
        for n in ["C", "E", "G", "B", "A", "G", "E", "C", "G", "B", "D", "F", "E", "D", "C", "C"]
    ]
)
song.effects = {"fast": EffectsChain().add(reverb, room_size=0.5, wet=0.2)}
h = harmonic_rhythm(song)
print(f"Chords: {h['total_chords']}, changes/bar: {h['changes_per_bar']}")
