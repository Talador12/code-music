"""Canon Round — same melody in 3 voices, each entering 4 beats later."""

from code_music import EffectsChain, Note, Song, Track, reverb
from code_music.theory import canon

melody = [Note(n, 5, 0.5) for n in ["C", "D", "E", "F", "G", "A", "B", "C"]]
voices = canon(melody, delay_beats=4.0, voices=3)
song = Song(title="Canon Round", bpm=100, sample_rate=44100)
for i, v in enumerate(voices):
    song.add_track(
        Track(name=f"voice_{i}", instrument="piano", volume=0.45, pan=(i - 1) * 0.3)
    ).extend(v)
song.effects = {"voice_0": EffectsChain().add(reverb, room_size=0.4, wet=0.15)}
