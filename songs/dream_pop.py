"""dream_pop.py — Dream pop. Emaj, 98 BPM. Beach House meets Cocteau Twins.

Shimmering guitars, ethereal vocals-as-pad, and a gentle pulse.
Everything drenched in reverb and chorus.

Style: Dream pop, E major, 98 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, chorus, delay, reverb, stereo_width

song = Song(title="Dream Pop", bpm=98)
r = Note.rest

guitar = song.add_track(Track(name="guitar", instrument="pluck", volume=0.4, pan=0.2))
arp = [Note("E", 4, 0.5), Note("G#", 4, 0.5), Note("B", 4, 0.5), Note("E", 5, 0.5)] * 4
for _ in range(12):
    guitar.extend(arp)

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3))
for _ in range(6):
    pad.extend([Chord("E", "maj7", 3, duration=4.0), Chord("C#", "min7", 3, duration=4.0),
                Chord("A", "maj7", 3, duration=4.0), Chord("B", "maj", 3, duration=4.0)])

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.45))
for _ in range(12):
    bass.extend([Note("E", 2, 2.0), Note("C#", 2, 2.0)])

lead = song.add_track(Track(name="lead", instrument="triangle", volume=0.35, pan=-0.15))
for _ in range(6):
    lead.extend([Note("G#", 5, 1.0), Note("E", 5, 0.5), Note("B", 4, 0.5), Note("C#", 5, 1.0), r(1.0),
                 r(4.0)])

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.5))
for _ in range(12):
    kick.extend([Note("C", 2, 2.0), r(2.0)])

song.effects = {
    "guitar": EffectsChain().add(chorus, rate=1.5, depth=0.3, wet=0.3).add(delay, delay_ms=306, feedback=0.3, wet=0.2).add(reverb, room_size=0.75, wet=0.4),
    "pad": EffectsChain().add(reverb, room_size=0.85, wet=0.5).add(stereo_width, width=1.8),
    "lead": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
}
