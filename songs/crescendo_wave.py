"""Crescendo Wave — dynamics curve creates a crescendo then decrescendo."""

from code_music import EffectsChain, Note, Song, Track, reverb
from code_music.theory import dynamics_curve

melody = [Note(n, 5, 0.5) for n in ["A", "C", "E", "G", "F", "E", "C", "A"] * 2]
cresc = dynamics_curve(melody, start_vel=0.2, end_vel=0.9)
song = Song(title="Crescendo Wave", bpm=100, sample_rate=44100)
song.add_track(Track(name="cresc", instrument="piano", volume=0.5)).extend(cresc)
song.effects = {"cresc": EffectsChain().add(reverb, room_size=0.4, wet=0.15)}
