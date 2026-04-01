"""new_wave.py — New wave. Dm, 132 BPM. Depeche Mode meets New Order.

Synth bass, arpeggiated pads, driving drums, and a cold melodic lead.
Post-punk meets electronic.

Style: New wave, Dm, 132 BPM.
"""

from code_music import EffectsChain, Note, Song, Track, chorus, delay, reverb

song = Song(title="New Wave", bpm=132)
r = Note.rest

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.75))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.55))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.3))
for _ in range(16):
    kick.extend([Note("C", 2, 1.0)] * 4)
    snare.extend([r(1.0), Note("E", 4, 1.0), r(1.0), Note("E", 4, 1.0)])
    hat.extend([Note("F#", 6, 0.5)] * 8)

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
for _ in range(16):
    bass.extend([Note("D", 2, 0.5), Note("D", 2, 0.5), Note("F", 2, 0.5), Note("A", 2, 0.5),
                 Note("G", 2, 0.5), Note("F", 2, 0.5), Note("D", 2, 0.5), Note("A", 1, 0.5)])

arp = song.add_track(Track(name="arp", instrument="triangle", volume=0.35, pan=0.25))
arp_bar = [Note("D", 4, 0.25), Note("F", 4, 0.25), Note("A", 4, 0.25), Note("D", 5, 0.25)] * 4
for _ in range(16):
    arp.extend(arp_bar)

lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.45, pan=-0.15))
for _ in range(8):
    lead.extend([Note("A", 5, 0.5), Note("G", 5, 0.5), Note("F", 5, 0.5), Note("D", 5, 0.5),
                 Note("C", 5, 1.0), Note("D", 5, 1.0), r(4.0)])

song.effects = {
    "arp": EffectsChain().add(chorus, rate=2.0, depth=0.3, wet=0.25).add(delay, delay_ms=227, feedback=0.25, wet=0.15),
    "lead": EffectsChain().add(reverb, room_size=0.5, wet=0.2),
}
