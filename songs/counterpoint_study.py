"""Counterpoint Study — melody with algorithmically-generated counterpoint."""

from code_music import EffectsChain, Note, Song, Track, reverb
from code_music.theory import generate_counterpoint

melody = [
    Note(n, 4, 1.0)
    for n in ["C", "D", "E", "F", "G", "A", "B", "C", "B", "A", "G", "F", "E", "D", "C", "C"]
]
cp = generate_counterpoint(melody, interval="third", seed=42)
song = Song(title="Counterpoint Study", bpm=90, sample_rate=44100)
song.add_track(Track(name="cantus", instrument="piano", volume=0.5)).extend(melody)
song.add_track(Track(name="counter", instrument="piano", volume=0.4, pan=0.2)).extend(cp)
song.effects = {"cantus": EffectsChain().add(reverb, room_size=0.5, wet=0.2)}
