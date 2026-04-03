"""Inverted Chords — root position vs first and second inversions."""

from code_music import EffectsChain, Note, Song, Track, reverb
from code_music.theory import generate_chord_voicing, invert_chord

root = generate_chord_voicing("C", "maj", voicing="close")
first = invert_chord(root, 1)
second = invert_chord(root, 2)
song = Song(title="Inverted Chords", bpm=80, sample_rate=44100)
song.add_track(Track(name="root", instrument="piano", volume=0.5, pan=-0.2)).extend(root)
song.add_track(Track(name="first", instrument="piano", volume=0.5)).extend(first)
song.add_track(Track(name="second", instrument="piano", volume=0.5, pan=0.2)).extend(second)
song.effects = {"root": EffectsChain().add(reverb, room_size=0.4, wet=0.15)}
