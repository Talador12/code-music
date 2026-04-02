"""Harmonic Spectrum — exploring wavetable + FM fusion.

Combines wavetable-designed pads with FM leads and euclidean percussion.
A showcase of all three v7.0 features working together.
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    SoundDesigner,
    Track,
    Wavetable,
    delay,
    euclid,
    reverb,
)

# -- Hybrid instruments (wavetable + FM combined) ----------------------------

# Wavetable pad with harmonic overtones
_wt_lush = Wavetable.from_harmonics([1.0, 0.6, 0.4, 0.3, 0.2, 0.15, 0.1, 0.05])
lush_pad = (
    SoundDesigner("lush_pad")
    .add_wavetable(_wt_lush, volume=0.35)
    .add_wavetable(_wt_lush, volume=0.25, detune_cents=5)
    .add_wavetable(_wt_lush, volume=0.25, detune_cents=-5)
    .fm("sine", mod_ratio=2.0, mod_index=0.5, volume=0.15)  # subtle FM warmth
    .envelope(attack=0.5, decay=0.3, sustain=0.5, release=1.0)
    .filter("lowpass", cutoff=2000, resonance=0.5)
    .lfo("filter_cutoff", rate=0.15, depth=0.35)
)

# FM lead with wavetable sub-oscillator
_wt_sub = Wavetable.from_wave("sine")
fm_lead = (
    SoundDesigner("fm_lead")
    .fm("sine", mod_ratio=2.0, mod_index=4.0, volume=0.6)
    .fm("sine", mod_ratio=5.0, mod_index=1.5, volume=0.2)
    .add_wavetable(_wt_sub, volume=0.2)  # sub for body
    .envelope(attack=0.01, decay=0.1, sustain=0.6, release=0.3)
    .filter("lowpass", cutoff=4000, resonance=1.0)
    .lfo("filter_cutoff", rate=3.0, depth=0.2)
)

# Wavetable bass
_wt_bass = Wavetable.from_wave("sawtooth").morph(Wavetable.from_wave("square"), 0.3)
thick_bass = (
    SoundDesigner("thick_bass")
    .add_wavetable(_wt_bass, volume=0.6)
    .add_wavetable(_wt_bass, volume=0.4, detune_cents=-5)
    .envelope(attack=0.005, decay=0.2, sustain=0.5, release=0.15)
    .filter("lowpass", cutoff=500, resonance=1.2)
)

# FM percussion: metallic click
click = (
    SoundDesigner("click")
    .fm("sine", mod_ratio=5.0, mod_index=12.0, volume=0.8)
    .noise("white", volume=0.2, seed=77)
    .envelope(attack=0.001, decay=0.03, sustain=0.0, release=0.02)
    .filter("highpass", cutoff=4000, resonance=0.5)
)

# -- Song --------------------------------------------------------------------

song = Song(title="Harmonic Spectrum", bpm=118, sample_rate=44100)

for name, designer in [
    ("lush_pad", lush_pad),
    ("fm_lead", fm_lead),
    ("thick_bass", thick_bass),
    ("click", click),
]:
    song.register_instrument(name, designer)

E = 0.5  # eighth note

# Pad: slow chord progression
tr_pad = song.add_track(Track(name="pad", instrument="lush_pad", volume=0.35, pan=-0.1))
tr_pad.add(Chord("A", "min7", 3, duration=8.0))
tr_pad.add(Chord("F", "maj7", 3, duration=8.0))
tr_pad.add(Chord("C", "maj7", 3, duration=8.0))
tr_pad.add(Chord("G", "dom7", 3, duration=8.0))

# Bass: euclidean (5 in 16)
tr_bass = song.add_track(Track(name="bass", instrument="thick_bass", volume=0.5))
for root in ["A", "F", "C", "G"]:
    tr_bass.extend(euclid(5, 16, root, 2, E))

# Click: euclidean (7 in 16)
tr_click = song.add_track(Track(name="click", instrument="click", volume=0.25))
for _ in range(4):
    tr_click.extend(euclid(7, 16, "C", 7, E))

# Kick: four-on-the-floor
tr_kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.65))
for _ in range(16):
    tr_kick.add(Note("C", 2, 2.0))

# FM lead melody
tr_lead = song.add_track(Track(name="lead", instrument="fm_lead", volume=0.4, pan=0.15))
melody = [
    ("A", 5),
    ("C", 6),
    ("E", 6),
    ("D", 6),
    ("C", 6),
    ("A", 5),
    ("G", 5),
    ("A", 5),
    ("F", 5),
    ("A", 5),
    ("C", 6),
    ("E", 6),
    ("D", 6),
    ("C", 6),
    ("B", 5),
    ("G", 5),
    ("C", 5),
    ("E", 5),
    ("G", 5),
    ("B", 5),
    ("A", 5),
    ("G", 5),
    ("E", 5),
    ("C", 5),
    ("G", 5),
    ("B", 5),
    ("D", 6),
    ("F", 6),
    ("E", 6),
    ("D", 6),
    ("B", 5),
    ("G", 5),
]
for note_name, oct in melody:
    tr_lead.add(Note(note_name, oct, 1.0))

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.8, wet=0.4),
    "lead": EffectsChain().add(delay, delay_ms=254, feedback=0.25, wet=0.18),
    "click": EffectsChain().add(reverb, room_size=0.2, wet=0.1),
}
