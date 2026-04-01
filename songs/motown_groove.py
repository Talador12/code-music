"""motown_groove.py — Motown soul. G major, 108 BPM. Stevie Wonder energy.

Walking Motown bass, tambourine backbeat, and a sweet soul lead.
Classic 60s Detroit production style.

Style: Motown soul, G major, 108 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, compress, reverb

song = Song(title="Motown Groove", bpm=108)
r = Note.rest

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.75))
tamb = song.add_track(Track(name="tamb", instrument="drums_hat", volume=0.35))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.5))
for _ in range(16):
    kick.extend([Note("C", 2, 1.0), r(1.0), Note("C", 2, 1.0), r(1.0)])
    snare.extend([r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)])
    tamb.extend([Note("F#", 6, 0.5)] * 8)

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
for _ in range(16):
    bass.extend([Note("G", 2, 0.5), Note("B", 2, 0.5), Note("D", 3, 0.5), Note("G", 3, 0.5),
                 Note("D", 3, 0.5), Note("B", 2, 0.5), Note("G", 2, 0.5), Note("D", 2, 0.5)])

keys = song.add_track(Track(name="keys", instrument="piano", volume=0.45, pan=0.15))
for _ in range(8):
    keys.extend([Chord("G", "maj", 3, duration=4.0), Chord("C", "maj", 3, duration=4.0)])

lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.5, pan=-0.15))
for _ in range(8):
    lead.extend([Note("B", 4, 0.5), Note("D", 5, 0.5), Note("G", 5, 1.0),
                 Note("F#", 5, 0.5), Note("D", 5, 0.5), Note("B", 4, 1.0),
                 r(4.0)])

song.effects = {
    "keys": EffectsChain().add(reverb, room_size=0.4, wet=0.15),
    "lead": EffectsChain().add(reverb, room_size=0.45, wet=0.2).add(compress, threshold=0.5, ratio=3.0),
}
