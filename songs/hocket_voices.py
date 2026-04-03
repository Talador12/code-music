"""Hocket Voices — melody split across two interlocking voices."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import hocket

melody = [Note(n, 5, 0.5) for n in ["A", "B", "C", "D", "E", "F", "G", "A"]]
voices = hocket(melody, voices=2)
song = Song(title="Hocket Voices", bpm=110, sample_rate=44100)
song.add_track(Track(name="v1", instrument="piano", volume=0.5, pan=-0.3)).extend(voices[0])
song.add_track(Track(name="v2", instrument="piano", volume=0.5, pan=0.3)).extend(voices[1])
song.add_track(Track(name="pad", instrument="pad", volume=0.25)).add(
    Chord("A", "min", 3, duration=4.0)
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
