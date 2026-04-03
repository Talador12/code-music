"""Velocity Layers — same melody at different humanization levels."""

from code_music import EffectsChain, Note, Song, Track, reverb
from code_music.theory import humanize_velocity

melody = [Note(n, 5, 0.5) for n in ["A", "C", "E", "G", "F", "E", "C", "A"]]
subtle = humanize_velocity(melody, amount=0.05, seed=42)
moderate = humanize_velocity(melody, amount=0.15, seed=42)
extreme = humanize_velocity(melody, amount=0.35, seed=42)
song = Song(title="Velocity Layers", bpm=100, sample_rate=44100)
song.add_track(Track(name="subtle", instrument="piano", volume=0.5, pan=-0.2)).extend(subtle)
song.add_track(Track(name="moderate", instrument="piano", volume=0.5)).extend(moderate)
song.add_track(Track(name="extreme", instrument="piano", volume=0.5, pan=0.2)).extend(extreme)
song.effects = {"moderate": EffectsChain().add(reverb, room_size=0.4, wet=0.15)}
