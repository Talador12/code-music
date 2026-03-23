"""Pulse: driving synth arp + kick, Am pentatonic, 128 BPM. Pure forward motion.

Energizing. The arp never stops. Your body wants to move by bar 2.
Supersaw wall behind it keeps the energy pressurized.
"""

from code_music import Chord, Note, Song, Track, arp, chord_prog, reverb, stereo_width

song = Song(title="pulse", bpm=128)

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=1.0))
kick.extend([Note("C", 2, 1.0)] * 32)

pad = song.add_track(Track(name="pad", instrument="supersaw", volume=0.45, pan=0.0))
for ch in chord_prog(["A", "F", "C", "G"], ["min7", "maj7", "maj", "dom7"], duration=4.0):
    pad.extend([ch] * 2)

arp_tr = song.add_track(Track(name="arp", instrument="pluck", volume=0.55, pan=0.2))
for ch, sh in [("A", "min"), ("F", "maj"), ("C", "maj"), ("G", "maj")] * 2:
    arp_tr.extend(arp(Chord(ch, sh, 5), pattern="up_down", rate=0.25, octaves=2))

hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.4))
hat.extend([Note.rest(0.5), Note("F", 5, 0.5)] * 32)

song._effects = {
    "pad": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.4, wet=0.15), width=1.7),
    "arp": lambda s, sr: reverb(s, sr, room_size=0.35, wet=0.12),
}
