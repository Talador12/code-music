"""Hemiola Waltz — 3-against-2 rhythmic illusion over a waltz pad."""

from code_music import Chord, EffectsChain, Song, Track, reverb
from code_music.theory import hemiola

song = Song(title="Hemiola Waltz", bpm=108, time_sig=(3, 4))

# Pad — straight 3/4
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4, pan=-0.1))
for _ in range(4):
    pad.add(Chord("D", "min7", 3, duration=6.0))  # 2 bars of 3/4
    pad.add(Chord("G", "dom7", 3, duration=6.0))

# Hemiola: voice in 3 vs voice in 2
v3, v2 = hemiola("D", octave=4, bars=8, duration=1.0)

low = song.add_track(Track(name="low", instrument="pluck", volume=0.5, pan=-0.2))
low.extend(v3)

high = song.add_track(Track(name="high", instrument="triangle", volume=0.45, pan=0.2))
high.extend(v2)

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
    "high": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
}
