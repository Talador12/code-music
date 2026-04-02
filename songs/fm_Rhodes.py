"""FM Rhodes — warm electric piano ballad built entirely with FM synthesis.

DX7-inspired electric piano chords, FM bass, and bell accents.
Every instrument uses frequency modulation — no subtractive synthesis.
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    SoundDesigner,
    Track,
    delay,
    euclid,
    reverb,
)

# -- FM instruments ----------------------------------------------------------

rhodes = (
    SoundDesigner("rhodes")
    .fm("sine", mod_ratio=2.0, mod_index=3.0, volume=0.7)
    .fm("sine", mod_ratio=1.0, mod_index=0.8, volume=0.3)
    .envelope(attack=0.003, decay=0.5, sustain=0.15, release=0.6)
    .filter("lowpass", cutoff=5000, resonance=0.3)
)

fm_bass = (
    SoundDesigner("fm_bass")
    .fm("sine", mod_ratio=1.0, mod_index=3.5, volume=0.9)
    .envelope(attack=0.005, decay=0.3, sustain=0.4, release=0.2)
    .filter("lowpass", cutoff=600, resonance=0.8)
)

fm_bell = (
    SoundDesigner("fm_bell")
    .fm("sine", mod_ratio=1.414, mod_index=6.0, volume=0.6)
    .fm("sine", mod_ratio=3.5, mod_index=1.5, volume=0.4)
    .envelope(attack=0.001, decay=0.8, sustain=0.0, release=0.5)
)

fm_pad = (
    SoundDesigner("fm_pad")
    .fm("sine", mod_ratio=2.0, mod_index=1.5, volume=0.5)
    .fm("sine", mod_ratio=3.0, mod_index=0.5, volume=0.3)
    .fm("sine", mod_ratio=1.0, mod_index=0.3, volume=0.2)
    .envelope(attack=0.4, decay=0.2, sustain=0.5, release=0.8)
    .filter("lowpass", cutoff=2500, resonance=0.4)
)

# -- Song --------------------------------------------------------------------

song = Song(title="FM Rhodes", bpm=72, sample_rate=44100)

for name, designer in [
    ("rhodes", rhodes),
    ("fm_bass", fm_bass),
    ("fm_bell", fm_bell),
    ("fm_pad", fm_pad),
]:
    song.register_instrument(name, designer)

# Pad: long sustained chords
tr_pad = song.add_track(Track(name="pad", instrument="fm_pad", volume=0.3, pan=-0.1))
tr_pad.add(Chord("D", "min9", 3, duration=8.0))
tr_pad.add(Chord("G", "dom7", 3, duration=8.0))
tr_pad.add(Chord("C", "maj7", 3, duration=8.0))
tr_pad.add(Chord("A", "min7", 3, duration=8.0))

# Rhodes: chords on beats
tr_rhodes = song.add_track(Track(name="rhodes", instrument="rhodes", volume=0.5))
for root, shape in [("D", "min9"), ("G", "dom7"), ("C", "maj7"), ("A", "min7")]:
    tr_rhodes.add(Chord(root, shape, 4, duration=2.0))
    tr_rhodes.add(Note.rest(2.0))
    tr_rhodes.add(Chord(root, shape, 4, duration=1.5))
    tr_rhodes.add(Note.rest(2.5))

# Bass: euclidean (5 in 16)
tr_bass = song.add_track(Track(name="bass", instrument="fm_bass", volume=0.55))
for root in ["D", "G", "C", "A"]:
    tr_bass.extend(euclid(5, 16, root, 2, 0.5))

# Bell accents
tr_bell = song.add_track(Track(name="bell", instrument="fm_bell", volume=0.25, pan=0.2))
bell_notes = [("D", 6), ("F", 6), ("A", 6), ("G", 6), ("B", 5), ("D", 6), ("C", 6), ("E", 6)]
for note_name, oct in bell_notes:
    tr_bell.add(Note(note_name, oct, 2.0))
    tr_bell.add(Note.rest(2.0))

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.85, wet=0.4),
    "rhodes": EffectsChain().add(delay, delay_ms=417, feedback=0.2, wet=0.15),
    "bell": EffectsChain().add(reverb, room_size=0.9, wet=0.5),
}
