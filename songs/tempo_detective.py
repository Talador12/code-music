"""Tempo Detective — renders and detects the BPM."""

from code_music import Chord, EffectsChain, Note, Song, Track, euclid, reverb
from code_music.theory import detect_tempo

song = Song(title="Tempo Detective", bpm=128, sample_rate=44100)
song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7)).extend(
    euclid(4, 8, "C", 2, 1.0) * 4
)
song.add_track(Track(name="pad", instrument="pad", volume=0.35)).extend(
    [Chord("E", "min7", 3, duration=16.0), Chord("A", "min7", 3, duration=16.0)]
)
song.add_track(Track(name="lead", instrument="piano", volume=0.5)).extend(
    [Note(n, 5, 1.0) for n in "E G B D C B G E D E G B A G E D".split()]
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
audio = song.render()
print(f"Set BPM: 128, Detected: {detect_tempo(audio, 44100)}")
