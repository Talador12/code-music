"""Pedal Bass — sustained pedal note alternating with melody."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import pedal_point

melody = [Note(n, 4, 0.5) for n in ["E", "F", "G", "A", "B", "C", "D", "E"]]
bass = pedal_point("C", 2, melody)
song = Song(title="Pedal Bass", bpm=100, sample_rate=44100)
song.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(bass)
song.add_track(Track(name="melody", instrument="piano", volume=0.45, pan=0.15)).extend(melody)
song.add_track(Track(name="pad", instrument="pad", volume=0.3)).add(
    Chord("C", "maj7", 3, duration=8.0)
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
