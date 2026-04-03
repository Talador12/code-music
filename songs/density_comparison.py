"""Density Comparison — sparse vs dense rhythms side by side."""

from code_music import EffectsChain, Note, Song, Track, reverb
from code_music.theory import rhythmic_density

sparse = [Note("C", 5, 2.0), Note("E", 5, 2.0), Note("G", 5, 2.0), Note("C", 6, 2.0)]
dense = [Note(n, 5, 0.25) for n in ["C", "D", "E", "F", "G", "A", "B", "C"] * 4]
print(f"Sparse: {rhythmic_density(sparse)}")
print(f"Dense: {rhythmic_density(dense)}")
song = Song(title="Density Comparison", bpm=120, sample_rate=44100)
song.add_track(Track(name="sparse", instrument="piano", volume=0.5, pan=-0.2)).extend(sparse)
song.add_track(Track(name="dense", instrument="piano", volume=0.4, pan=0.2)).extend(dense)
song.effects = {"sparse": EffectsChain().add(reverb, room_size=0.5, wet=0.2)}
