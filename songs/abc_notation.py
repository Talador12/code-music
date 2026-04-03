"""ABC Notation — song exported as ABC for musicians and notation tools."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.composition import to_abc

song = Song(title="ABC Notation", bpm=120, sample_rate=44100, key_sig="G")
song.add_track(Track(name="lead", instrument="piano", volume=0.5)).extend(
    [Note(n, 5, 1.0) for n in ["G", "A", "B", "D", "C", "B", "A", "G"]]
)
song.add_track(Track(name="pad", instrument="pad", volume=0.35)).extend(
    [Chord("G", "maj7", 3, duration=4.0), Chord("D", "dom7", 3, duration=4.0)]
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.25)}
print(to_abc(song))
