"""Complete Toolkit — demonstrates analyze, intro, outro, HTML, ABC, lead sheet, tab, map, summary."""

from code_music import Chord, EffectsChain, Note, Song, Track, euclid, reverb
from code_music.composition import (
    song_summary,
)

song = Song(title="Complete Toolkit", bpm=110, sample_rate=44100, key_sig="Am")
song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7)).extend(
    euclid(4, 8, "C", 2, 1.0) * 2
)
song.add_track(Track(name="pad", instrument="pad", volume=0.35)).extend(
    [Chord("A", "min7", 3, duration=8.0), Chord("F", "maj7", 3, duration=8.0)]
)
song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15)).extend(
    [
        Note(n, 5, 1.0)
        for n in ["A", "C", "E", "G", "F", "E", "C", "A", "G", "A", "C", "E", "D", "C", "A", "G"]
    ]
)
song.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(
    [Note(n, 2, 4.0) for n in ["A", "A", "F", "F"]]
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
# Use every analysis tool
print(song_summary(song))
