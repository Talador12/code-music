"""Blues Continuation — blues melody extended by Markov chain."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.composition import continue_melody

blues_seed = [
    Note("A", 4, 0.5),
    Note("C", 5, 0.5),
    Note("D", 5, 0.5),
    Note("Eb", 5, 0.25),
    Note("E", 5, 0.25),
    Note("G", 5, 0.5),
    Note("A", 5, 0.5),
]
melody = continue_melody(blues_seed, bars=4, key="A", mode="blues", seed_rng=55)

song = Song(title="Blues Continuation", bpm=85, sample_rate=44100)
song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15)).extend(melody)
song.add_track(Track(name="pad", instrument="pad", volume=0.35)).extend(
    [
        Chord("A", "dom7", 3, duration=4.0),
        Chord("D", "dom7", 3, duration=4.0),
        Chord("A", "dom7", 3, duration=4.0),
        Chord("E", "dom7", 3, duration=4.0),
    ]
)
song.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(
    [Note(n, 2, 4.0) for n in ["A", "D", "A", "E"]]
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.5, wet=0.2)}
