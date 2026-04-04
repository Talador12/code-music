"""Motif Development — a single 4-note motif through augmentation, diminution, fragmentation."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import augment, diminish, fragment

song = Song(title="Motif Development", bpm=100)

# The motif — Beethoven-simple, 4 notes
motif = [Note("G", 5, 0.5), Note("G", 5, 0.5), Note("G", 5, 0.5), Note("Eb", 5, 2.0)]

# Original statement
lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5, pan=0.1))
lead.extend(motif)
lead.add(Note.rest(1.0))

# Augmented (grand, spacious)
lead.extend(augment(motif, factor=2.0))
lead.add(Note.rest(1.0))

# Diminished (urgent, compressed)
lead.extend(diminish(motif, factor=2.0))
lead.add(Note.rest(1.0))

# Fragment — just the head
lead.extend(fragment(motif, 2))
lead.extend(fragment(motif, 2))
lead.extend(fragment(motif, 2))
lead.add(Note.rest(1.0))

# Full motif to close
lead.extend(motif)

# Pad
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.35, pan=-0.1))
pad.add(Chord("C", "min", 3, duration=8.0))
pad.add(Chord("Ab", "maj", 3, duration=8.0))
pad.add(Chord("Eb", "maj", 3, duration=4.0))
pad.add(Chord("G", "dom7", 3, duration=4.0))
pad.add(Chord("C", "min", 3, duration=8.0))

song.effects = {
    "lead": EffectsChain().add(reverb, room_size=0.5, wet=0.25),
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
}
