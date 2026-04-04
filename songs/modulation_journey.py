"""Modulation Journey — pivot modulation from C through G to D."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb
from code_music.theory import direct_modulation, pivot_modulation

song = Song(title="Modulation Journey", bpm=100)

# Phase 1: C major → G major via pivot modulation
phase1 = pivot_modulation("C", "G")

# Phase 2: G major → D major via direct (truck driver) modulation
phase2 = direct_modulation("G", "D")

# Combine progressions
full_prog = phase1 + phase2

# Chord pad
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4, pan=-0.15))
for root, shape in full_prog:
    pad.add(Chord(root, shape, 3, duration=4.0))

# Melody that follows the modulations
lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.15))
# C major melody
lead.extend([Note("E", 5, 1.0), Note("G", 5, 1.0), Note("C", 6, 1.0), Note("B", 5, 1.0)])
# Pivot area
lead.extend([Note("G", 5, 1.0), Note("A", 5, 1.0), Note("B", 5, 1.0), Note("D", 6, 1.0)])
# G major melody
lead.extend([Note("D", 6, 1.0), Note("B", 5, 1.0), Note("G", 5, 1.0), Note("A", 5, 1.0)])
# Truck driver up to D major
lead.extend([Note("D", 5, 1.0), Note("F#", 5, 1.0), Note("A", 5, 2.0)])
# D major landing
lead.extend([Note("D", 6, 2.0), Note("A", 5, 1.0), Note("F#", 5, 1.0)])

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
    "lead": EffectsChain().add(delay, delay_ms=300, feedback=0.2, wet=0.15),
}
