"""Blues Box — generated blues licks over a 12-bar structure."""

from code_music import Chord, EffectsChain, Song, Track, reverb
from code_music.theory import blues_lick

song = Song(title="Blues Box", bpm=95, sample_rate=44100)
song.add_track(Track(name="lick1", instrument="piano", volume=0.5)).extend(blues_lick("A", seed=42))
song.add_track(Track(name="lick2", instrument="piano", volume=0.45, pan=0.2)).extend(
    blues_lick("A", seed=99)
)
song.add_track(Track(name="pad", instrument="pad", volume=0.3)).add(
    Chord("A", "dom7", 3, duration=4.0)
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.5, wet=0.2)}
