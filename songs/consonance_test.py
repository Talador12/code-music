"""Consonance Test — compares consonant vs dissonant intervals."""

from code_music import EffectsChain, Note, Song, Track, reverb
from code_music.theory import consonance_score

consonant = [Note("C", 4, 1.0), Note("G", 4, 1.0), Note("C", 5, 1.0), Note("E", 5, 1.0)]
dissonant = [Note("C", 4, 1.0), Note("F#", 4, 1.0), Note("B", 4, 1.0), Note("F", 5, 1.0)]
print(f"Consonant: {consonance_score(consonant):.3f}")
print(f"Dissonant: {consonance_score(dissonant):.3f}")
song = Song(title="Consonance Test", bpm=80, sample_rate=44100)
song.add_track(Track(name="consonant", instrument="piano", volume=0.5, pan=-0.2)).extend(consonant)
song.add_track(Track(name="dissonant", instrument="piano", volume=0.5, pan=0.2)).extend(dissonant)
song.effects = {"consonant": EffectsChain().add(reverb, room_size=0.4, wet=0.15)}
