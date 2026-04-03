"""Tabbed Melody — guitar melody with ASCII tab output."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.composition import to_tab

song = Song(title="Tabbed Melody", bpm=90, sample_rate=44100)
song.add_track(Track(name="guitar", instrument="pluck", volume=0.5)).extend(
    [
        Note(n, o, 1.0)
        for n, o in [("E", 4), ("G", 4), ("A", 4), ("B", 4), ("E", 5), ("D", 5), ("B", 4), ("A", 4)]
    ]
)
song.add_track(Track(name="pad", instrument="pad", volume=0.35)).extend(
    [Chord("E", "min", 3, duration=4.0), Chord("G", "maj", 3, duration=4.0)]
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.7, wet=0.3)}
print(to_tab(song, tuning="guitar", track_name="guitar"))
