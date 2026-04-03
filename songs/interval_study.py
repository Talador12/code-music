"""Interval Study — names all intervals from C."""

from code_music import EffectsChain, Note, Song, Track, reverb
from code_music.theory import interval_name

notes = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
for n in notes:
    print(f"C → {n}: {interval_name('C', n)}")
song = Song(title="Interval Study", bpm=80, sample_rate=44100)
song.add_track(Track(name="intervals", instrument="piano", volume=0.5)).extend(
    [Note(n, 4, 1.0) for n in notes]
)
song.effects = {}
