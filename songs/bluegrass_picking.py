"""bluegrass_picking.py — Bluegrass. G major, 140 BPM. Flatpicking and fiddle.

Fast flatpicking runs, walking bass, and a fiddle melody over classic
I-IV-V-I bluegrass changes. Uses Track.loop for the repeating banjo roll.

Style: Bluegrass, G major, 140 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb

song = Song(title="Bluegrass Picking", bpm=140)
r = Note.rest

banjo_bar = Track(name="banjo", instrument="pluck", volume=0.5, pan=0.2)
banjo_bar.extend([
    Note("G", 4, 0.25), Note("B", 4, 0.25), Note("D", 5, 0.25), Note("G", 5, 0.25),
    Note("B", 4, 0.25), Note("D", 5, 0.25), Note("G", 4, 0.25), Note("B", 4, 0.25),
    Note("D", 5, 0.25), Note("G", 5, 0.25), Note("D", 5, 0.25), Note("B", 4, 0.25),
    Note("G", 4, 0.25), Note("D", 4, 0.25), Note("G", 4, 0.25), Note("B", 4, 0.25),
])
song.add_track(banjo_bar.loop(16))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.55))
for _ in range(8):
    bass.extend([Note("G", 2, 1.0), Note("B", 2, 1.0), Note("D", 3, 1.0), Note("B", 2, 1.0),
                 Note("C", 2, 1.0), Note("E", 2, 1.0), Note("G", 2, 1.0), Note("E", 2, 1.0)])

fiddle = song.add_track(Track(name="fiddle", instrument="sawtooth", volume=0.45, pan=-0.2))
for _ in range(4):
    fiddle.extend([
        Note("G", 5, 0.5), Note("A", 5, 0.5), Note("B", 5, 0.5), Note("D", 6, 0.5),
        Note("B", 5, 1.0), Note("G", 5, 1.0),
        Note("A", 5, 0.5), Note("G", 5, 0.5), Note("E", 5, 0.5), Note("D", 5, 0.5),
        Note("G", 5, 2.0),
        r(8.0),
    ])

chords = song.add_track(Track(name="guitar", instrument="pluck", volume=0.3, pan=-0.1))
for _ in range(8):
    chords.extend([
        Chord("G", "maj", 3, duration=4.0), Chord("C", "maj", 3, duration=4.0),
    ])

song.effects = {
    "fiddle": EffectsChain().add(reverb, room_size=0.35, wet=0.15),
    "banjo": EffectsChain().add(reverb, room_size=0.3, wet=0.1),
}
