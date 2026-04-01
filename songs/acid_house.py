"""acid_house.py — Acid house. Am, 126 BPM. TB-303 squelch.

Classic 303 acid bassline with the signature filter sweep, four-on-the-floor
kick, and open hats. Uses EffectsChain with lfo_filter for the squelch.

Style: Acid house, Am, 126 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, lfo_filter, reverb

song = Song(title="Acid House", bpm=126)
r = Note.rest

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.3))
for _ in range(24):
    kick.extend([Note("C", 2, 1.0)] * 4)
    hat.extend([r(0.5), Note("F#", 6, 0.5)] * 4)

acid_bar = Track(name="acid", instrument="sawtooth", volume=0.55)
acid_bar.extend([
    Note("A", 2, 0.25), Note("A", 2, 0.25), Note("C", 3, 0.25), Note("A", 2, 0.25),
    Note("E", 3, 0.25), Note("A", 2, 0.25), Note("C", 3, 0.25), Note("E", 3, 0.25),
    Note("A", 2, 0.25), Note("G", 2, 0.25), Note("A", 2, 0.25), Note("C", 3, 0.25),
    Note("A", 2, 0.5), Note("E", 2, 0.5),
])
song.add_track(acid_bar.loop(24))

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.2))
for _ in range(12):
    pad.extend([Chord("A", "min7", 3, duration=4.0), Chord("G", "min7", 3, duration=4.0)])

song.effects = {
    "acid": EffectsChain().add(lfo_filter, rate=0.5, depth=0.7),
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
}
