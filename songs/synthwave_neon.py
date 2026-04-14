"""synthwave_neon.py - 80s synthwave. Am, 118 BPM.

Neon-drenched arpeggios over a pumping kick, lush pad,
and a sawtooth lead dripping with reverb. Midnight cruise material.

Style: Synthwave, Am, 118 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb

song = Song(title="Synthwave Neon", bpm=118, sample_rate=44100)
r = Note.rest

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.5))
for _ in range(16):
    kick.extend([Note("C", 2, 1.0)] * 4)
    snare.extend([r(1.0), Note("E", 4, 1.0)] * 2)

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
for _ in range(16):
    bass.extend([Note("A", 2, 1.5), Note("A", 2, 0.5), Note("E", 2, 1.0), Note("G", 2, 1.0)])

arp = song.add_track(Track(name="arp", instrument="triangle", volume=0.35, pan=0.25))
arp_pattern = [Note("A", 4, 0.25), Note("C", 5, 0.25), Note("E", 5, 0.25), Note("A", 5, 0.25)]
for _ in range(16):
    arp.extend(arp_pattern * 4)

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3, pan=-0.2))
for _ in range(8):
    pad.extend([Chord("A", "min7", 3, duration=4.0), Chord("F", "maj7", 3, duration=4.0)])

lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.45))
lead_phrase = [
    Note("E", 5, 1.0),
    Note("A", 5, 0.5),
    Note("G", 5, 0.5),
    Note("F", 5, 1.0),
    Note("E", 5, 1.0),
]
for _ in range(8):
    lead.extend(lead_phrase + [r(4.0)])

song.effects = {
    "arp": EffectsChain().add(delay, delay_ms=254, feedback=0.3, wet=0.25),
    "pad": EffectsChain().add(reverb, room_size=0.75, wet=0.4),
    "lead": EffectsChain().add(reverb, room_size=0.5, wet=0.25),
}
