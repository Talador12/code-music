"""Pivot Chord Study — demonstrating smooth modulations through pivot chords."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import find_pivot_chords, pivot_modulation

song = Song(title="Pivot Chord Study", bpm=84)

# Show pivot chords between C and Eb (a distant modulation)
pivots = find_pivot_chords("C", "Eb")
mod_prog = pivot_modulation("C", "Eb")

# Pad for harmonic bed
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4, pan=-0.1))
for root, shape in mod_prog:
    pad.add(Chord(root, shape, 3, duration=8.0))

# Now modulate from Eb to Ab
mod_prog2 = pivot_modulation("Eb", "Ab")
for root, shape in mod_prog2:
    pad.add(Chord(root, shape, 3, duration=8.0))

# Melody tracking the key centers
lead = song.add_track(Track(name="lead", instrument="triangle", volume=0.5, pan=0.15))
# C major phrase
lead.extend([Note("C", 5, 2.0), Note("E", 5, 2.0), Note("G", 5, 2.0), Note("C", 6, 2.0)])
# Transition
lead.extend([Note("Bb", 5, 2.0), Note("G", 5, 2.0), Note("Eb", 5, 2.0), Note("D", 5, 2.0)])
# Eb major phrase
lead.extend([Note("Eb", 5, 2.0), Note("G", 5, 2.0), Note("Bb", 5, 2.0), Note("Eb", 6, 2.0)])
# Continue to Ab
lead.extend([Note("Ab", 5, 2.0), Note("C", 6, 2.0), Note("Eb", 6, 2.0), Note("Ab", 5, 2.0)])
lead.extend([Note("Ab", 5, 2.0), Note("Bb", 5, 2.0), Note("C", 6, 2.0), Note("Eb", 6, 2.0)])
lead.extend([Note("Ab", 5, 4.0), Note("Eb", 5, 4.0)])

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.8, wet=0.4),
    "lead": EffectsChain().add(reverb, room_size=0.5, wet=0.25),
}
