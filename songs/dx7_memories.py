"""DX7 Memories — a retro FM synthesis tribute.

Every sound is pure FM — the technique that defined the 1980s. Multi-operator
stacks create electric piano, bass, brass stabs, and crystalline bells.
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

# -- Multi-operator FM instruments ------------------------------------------

# 3-operator electric piano (warm, vintage)
dx_piano = (
    SoundDesigner("dx_piano")
    .fm("sine", mod_ratio=1.0, mod_index=2.5, volume=0.5)
    .fm("sine", mod_ratio=2.0, mod_index=4.0, volume=0.35)
    .fm("sine", mod_ratio=4.0, mod_index=1.0, volume=0.15)
    .envelope(attack=0.003, decay=0.6, sustain=0.1, release=0.5)
    .filter("lowpass", cutoff=6000, resonance=0.2)
)

# FM slap bass
dx_bass = (
    SoundDesigner("dx_bass")
    .fm("sine", mod_ratio=1.0, mod_index=6.0, volume=0.8)
    .fm("sine", mod_ratio=3.0, mod_index=2.0, volume=0.2)
    .envelope(attack=0.001, decay=0.2, sustain=0.3, release=0.15)
    .filter("lowpass", cutoff=800, resonance=1.2)
)

# FM brass stab
dx_brass = (
    SoundDesigner("dx_brass")
    .fm("sine", mod_ratio=1.0, mod_index=5.0, volume=0.5)
    .fm("sine", mod_ratio=3.0, mod_index=3.5, volume=0.3)
    .add_osc("sawtooth", volume=0.1)
    .envelope(attack=0.02, decay=0.1, sustain=0.6, release=0.25)
    .filter("lowpass", cutoff=3500, resonance=0.6)
)

# Crystal bell
dx_bell = (
    SoundDesigner("dx_bell")
    .fm("sine", mod_ratio=1.414, mod_index=10.0, volume=0.5)
    .fm("sine", mod_ratio=2.236, mod_index=4.0, volume=0.3)
    .fm("sine", mod_ratio=5.0, mod_index=1.0, volume=0.2)
    .envelope(attack=0.001, decay=1.2, sustain=0.0, release=0.8)
)

# -- Song --------------------------------------------------------------------

song = Song(title="DX7 Memories", bpm=96, sample_rate=44100)

for name, designer in [
    ("dx_piano", dx_piano),
    ("dx_bass", dx_bass),
    ("dx_brass", dx_brass),
    ("dx_bell", dx_bell),
]:
    song.register_instrument(name, designer)

# Piano: chord progression
tr_piano = song.add_track(Track(name="piano", instrument="dx_piano", volume=0.5))
prog = [("E", "min7"), ("A", "min7"), ("D", "dom7"), ("G", "maj7")]
for root, shape in prog:
    tr_piano.add(Chord(root, shape, 4, duration=2.0))
    tr_piano.add(Note.rest(0.5))
    tr_piano.add(Chord(root, shape, 4, duration=1.5))
    tr_piano.add(Note.rest(4.0))

# Slap bass: euclidean (5 in 16)
tr_bass = song.add_track(Track(name="bass", instrument="dx_bass", volume=0.55))
for root in ["E", "A", "D", "G"]:
    tr_bass.extend(euclid(5, 16, root, 2, 0.5))

# Brass stabs: syncopated
tr_brass = song.add_track(Track(name="brass", instrument="dx_brass", volume=0.4, pan=-0.15))
for root, shape in prog:
    tr_brass.add(Note.rest(2.0))
    tr_brass.add(Chord(root, shape, 4, duration=0.5))
    tr_brass.add(Note.rest(5.5))

# Bell accents
tr_bell = song.add_track(Track(name="bell", instrument="dx_bell", volume=0.2, pan=0.25))
bell_melody = [("E", 6), ("G", 6), ("B", 6), ("A", 6), ("F#", 6), ("D", 6), ("G", 6), ("E", 6)]
for note_name, oct in bell_melody:
    tr_bell.add(Note(note_name, oct, 2.0))
    tr_bell.add(Note.rest(2.0))

song.effects = {
    "piano": EffectsChain().add(delay, delay_ms=313, feedback=0.2, wet=0.12),
    "bell": EffectsChain().add(reverb, room_size=0.9, wet=0.5),
    "brass": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
}
