"""Repeat Finder — detects repeated sections in a song."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import detect_repeated_sections

song = Song(title="Repeat Finder", bpm=120, sample_rate=44100)
tr = song.add_track(Track(name="lead", instrument="piano", volume=0.5))
# Deliberately repeat a 4-note pattern
for _ in range(4):
    for n in ["A", "C", "E", "G"]:
        tr.add(Note(n, 5, 0.5))
song.add_track(Track(name="pad", instrument="pad", volume=0.35)).add(
    Chord("A", "min7", 3, duration=8.0)
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
for s in detect_repeated_sections(song):
    print(f"  {s['track']}: {s['bars']} bars repeated {s['repeat_count']}x at bars {s['at_bars']}")
