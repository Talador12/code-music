"""Mirror Melody — original + inversion played simultaneously."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import generate_variation

melody = [Note(n, 5, 0.5) for n in ["E", "G", "A", "B", "E", "D", "B", "A"]]
mirror = generate_variation(melody, "inversion")
song = Song(title="Mirror Melody", bpm=95, sample_rate=44100)
song.add_track(Track(name="original", instrument="piano", volume=0.5)).extend(melody)
song.add_track(Track(name="mirror", instrument="piano", volume=0.45, pan=0.2)).extend(mirror)
song.add_track(Track(name="pad", instrument="pad", volume=0.3)).add(
    Chord("E", "min", 3, duration=4.0)
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
