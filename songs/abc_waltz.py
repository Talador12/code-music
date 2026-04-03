"""ABC Waltz — 3/4 time song with ABC notation export."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.composition import to_abc

song = Song(title="ABC Waltz", bpm=90, sample_rate=44100, key_sig="D", time_sig=(3, 4))
song.add_track(Track(name="melody", instrument="piano", volume=0.5)).extend(
    [
        Note(n, 5, d)
        for n, d in [
            ("D", 1.0),
            ("F#", 0.5),
            ("A", 0.5),
            ("D", 1.0),
            ("C#", 0.5),
            ("A", 0.5),
            ("B", 1.0),
            ("A", 0.5),
            ("G", 0.5),
            ("F#", 1.0),
            ("E", 0.5),
            ("D", 0.5),
        ]
    ]
)
song.add_track(Track(name="bass", instrument="bass", volume=0.45)).extend(
    [Note(n, 2, 3.0) for n in ["D", "A", "G", "D"]]
)
song.effects = {"melody": EffectsChain().add(reverb, room_size=0.5, wet=0.2)}
print(to_abc(song))
