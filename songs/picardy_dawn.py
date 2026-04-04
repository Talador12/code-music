"""Picardy Dawn — minor piece that ends on a surprise major chord."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb, scale
from code_music.theory import picardy_third

song = Song(title="Picardy Dawn", bpm=66)

# Dark pad — C minor atmosphere
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4, pan=-0.2))
pad.add(Chord("C", "min7", 3, duration=8.0))
pad.add(Chord("Ab", "maj7", 3, duration=8.0))
pad.add(Chord("Eb", "maj", 3, duration=8.0))
pad.add(Chord("G", "dom7", 3, duration=4.0))
# Picardy third — the dawn breaks
pad.extend(picardy_third("C", octave=3, duration=8.0))

# Melody over the minor progression
lead = song.add_track(Track(name="lead", instrument="triangle", volume=0.5, pan=0.15))
lead.extend(scale("C", "minor", octave=5, length=8))
lead.extend(scale("Ab", "major", octave=5, length=8))
lead.extend([Note("Eb", 5, 2.0), Note("G", 5, 2.0), Note("Bb", 5, 2.0), Note("Eb", 6, 2.0)])
lead.extend([Note("D", 5, 2.0), Note("B", 4, 2.0)])
# Final phrase: E natural (major 3rd) — the Picardy surprise
lead.extend([Note("C", 5, 2.0), Note("E", 5, 2.0), Note("G", 5, 2.0), Note("C", 6, 2.0)])

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.9, wet=0.5),
    "lead": EffectsChain().add(reverb, room_size=0.6, wet=0.3),
}
