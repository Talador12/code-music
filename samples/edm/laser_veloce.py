"""Mord Fustang laser arp: 16th-note hoover arpeggio, cosmic disco, Eb, 128 BPM.

Mord Fustang signature: that neon-laser arpeggiated lead, euphoric major keys,
lush chord background, relentless energy.
"""

from code_music import Chord, Note, Song, Track

song = Song(title="mord_fustang_laser", bpm=128)

# Background pad
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4, pan=-0.3))
for root, shape in [("D#", "maj7"), ("C", "min7"), ("G#", "maj7"), ("A#", "dom7")] * 2:
    pad.add(Chord(root, shape, 3, duration=4.0, velocity=0.55))

# Laser arp — hoover in 16ths
arp = song.add_track(Track(name="laser", instrument="hoover", volume=0.6, pan=0.2))
eb_16 = [Note("D#", 5, 0.25), Note("G", 5, 0.25), Note("A#", 5, 0.25), Note("D#", 6, 0.25)]
cm_16 = [Note("C", 5, 0.25), Note("D#", 5, 0.25), Note("G", 5, 0.25), Note("C", 6, 0.25)]
ab_16 = [Note("G#", 4, 0.25), Note("C", 5, 0.25), Note("D#", 5, 0.25), Note("G#", 5, 0.25)]
bb_16 = [Note("A#", 4, 0.25), Note("D", 5, 0.25), Note("F", 5, 0.25), Note("A#", 5, 0.25)]
for pat in [eb_16, cm_16, ab_16, bb_16] * 2:
    arp.extend(pat * 4)  # 4 bars each
