"""Swing Jazz — straight eighth notes transformed to swing feel."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import swing_notes

straight = [Note(n, 5, 0.5) for n in ["C", "D", "E", "F", "G", "A", "B", "C"]]
swung = swing_notes(straight, amount=0.67)
song = Song(title="Swing Jazz", bpm=140, sample_rate=44100)
song.add_track(Track(name="swung", instrument="piano", volume=0.5)).extend(swung)
song.add_track(Track(name="pad", instrument="pad", volume=0.3)).add(
    Chord("C", "maj7", 3, duration=4.0)
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.5, wet=0.2)}
