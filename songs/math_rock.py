"""math_rock.py — Math rock. Em, 156 BPM, 7/8 time. Odd meters and tapping.

Complex rhythms in 7/8 with tapping-style guitar arpeggios and punchy drums.
TTNG / Hella territory.

Style: Math rock, Em, 7/8 time, 156 BPM.
"""

from code_music import EffectsChain, Note, Song, Track, compress, reverb

song = Song(title="Math Rock", bpm=156, time_sig=(7, 8))
r = Note.rest
BAR = 3.5

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.75))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.55))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.35))
for _ in range(24):
    kick.extend([Note("C", 2, 0.5), r(0.5), Note("C", 2, 0.5), r(0.5), Note("C", 2, 0.5), r(0.5), Note("C", 2, 0.5)])
    snare.extend([r(1.0), Note("E", 4, 0.5), r(1.0), Note("E", 4, 0.5), r(0.5)])
    hat.extend([Note("F#", 6, 0.25)] * 14)

guitar_bar = Track(name="guitar", instrument="pluck", volume=0.5, pan=0.2)
guitar_bar.extend([
    Note("E", 4, 0.25), Note("G", 4, 0.25), Note("B", 4, 0.25), Note("E", 5, 0.25),
    Note("D", 5, 0.25), Note("B", 4, 0.25), Note("G", 4, 0.25),
    Note("A", 4, 0.25), Note("C", 5, 0.25), Note("E", 5, 0.25), Note("A", 5, 0.25),
    Note("G", 5, 0.25), Note("E", 5, 0.25), Note("C", 5, 0.25),
])
song.add_track(guitar_bar.loop(24))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
for _ in range(24):
    bass.extend([Note("E", 2, 1.0), Note("G", 2, 0.5), Note("B", 2, 0.5), Note("A", 2, 0.5),
                 Note("E", 2, 0.5), Note("B", 2, 0.5)])

song.effects = {
    "guitar": EffectsChain().add(reverb, room_size=0.35, wet=0.12).add(compress, threshold=0.5, ratio=3.0),
}
