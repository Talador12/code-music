"""Custom Kit — a drum & bass track with every drum designed from scratch.

Fast breakbeat rhythm using only SoundDesigner instruments. No built-in
presets — kick, snare, hats, bass, and a reese lead all hand-crafted.
"""

from code_music import (
    EffectsChain,
    Note,
    Song,
    SoundDesigner,
    Track,
    delay,
    reverb,
)

# -- Custom drum kit ---------------------------------------------------------

dnb_kick = (
    SoundDesigner("dnb_kick")
    .add_osc("sine", volume=1.0)
    .envelope(attack=0.001, decay=0.25, sustain=0.0, release=0.1)
    .pitch_envelope(start_multiplier=5.0, end_multiplier=1.0, duration=0.02)
    .filter("lowpass", cutoff=220, resonance=0.8)
)

dnb_snare = (
    SoundDesigner("dnb_snare")
    .noise("white", volume=0.6, seed=44)
    .add_osc("triangle", volume=0.4)
    .envelope(attack=0.001, decay=0.1, sustain=0.05, release=0.08)
    .filter("bandpass", cutoff=3000, resonance=1.0)
)

dnb_hat_closed = (
    SoundDesigner("dnb_hat_cl")
    .noise("white", volume=0.9, seed=8)
    .envelope(attack=0.001, decay=0.03, sustain=0.0, release=0.02)
    .filter("highpass", cutoff=9000, resonance=0.6)
)

dnb_hat_open = (
    SoundDesigner("dnb_hat_op")
    .noise("white", volume=0.7, seed=9)
    .noise("pink", volume=0.2, seed=10)
    .envelope(attack=0.001, decay=0.12, sustain=0.05, release=0.08)
    .filter("highpass", cutoff=6000, resonance=0.5)
)

reese = (
    SoundDesigner("reese")
    .add_osc("sawtooth", detune_cents=0, volume=0.4)
    .add_osc("sawtooth", detune_cents=5, volume=0.35)
    .add_osc("sawtooth", detune_cents=-5, volume=0.35)
    .envelope(attack=0.01, decay=0.1, sustain=0.7, release=0.2)
    .filter("lowpass", cutoff=800, resonance=1.5)
    .lfo("filter_cutoff", rate=0.5, depth=0.5)
)

stab_lead = (
    SoundDesigner("stab_lead")
    .add_osc("square", volume=0.4, harmonics=8)
    .add_osc("sawtooth", detune_cents=7, volume=0.3)
    .envelope(attack=0.005, decay=0.08, sustain=0.4, release=0.2)
    .filter("lowpass", cutoff=4000, resonance=0.8)
)

# -- Song --------------------------------------------------------------------

song = Song(title="Custom Kit", bpm=174, sample_rate=44100)

for name, designer in [
    ("dnb_kick", dnb_kick),
    ("dnb_snare", dnb_snare),
    ("dnb_hat_cl", dnb_hat_closed),
    ("dnb_hat_op", dnb_hat_open),
    ("reese", reese),
    ("stab_lead", stab_lead),
]:
    song.register_instrument(name, designer)

# Classic amen-style breakbeat pattern (simplified)
# K = kick, S = snare, . = rest, h = closed hat, H = open hat
# Pattern per 2 bars: K.h.S.hH K.h.S.h. (8th note grid)
tr_kick = song.add_track(Track(name="kick", instrument="dnb_kick", volume=0.8))
tr_snare = song.add_track(Track(name="snare", instrument="dnb_snare", volume=0.6))
tr_hat = song.add_track(Track(name="hat", instrument="dnb_hat_cl", volume=0.35))

r = Note.rest
E = 0.5  # eighth note

# 4 repetitions of a 2-bar pattern
for _ in range(4):
    # Bar 1: K . h . S . h H
    tr_kick.add(Note("C", 2, E))
    tr_kick.add(r(E))
    tr_kick.add(r(E))
    tr_kick.add(r(E))
    tr_kick.add(r(E))
    tr_kick.add(r(E))
    tr_kick.add(r(E))
    tr_kick.add(r(E))

    tr_snare.add(r(E))
    tr_snare.add(r(E))
    tr_snare.add(r(E))
    tr_snare.add(r(E))
    tr_snare.add(Note("D", 4, E))
    tr_snare.add(r(E))
    tr_snare.add(r(E))
    tr_snare.add(r(E))

    tr_hat.add(r(E))
    tr_hat.add(r(E))
    tr_hat.add(Note("F#", 6, E))
    tr_hat.add(r(E))
    tr_hat.add(r(E))
    tr_hat.add(r(E))
    tr_hat.add(Note("F#", 6, E))
    tr_hat.add(Note("F#", 6, E))

    # Bar 2: K . h . S . h .
    tr_kick.add(Note("C", 2, E))
    tr_kick.add(r(E))
    tr_kick.add(r(E))
    tr_kick.add(r(E))
    tr_kick.add(r(E))
    tr_kick.add(r(E))
    tr_kick.add(r(E))
    tr_kick.add(Note("C", 2, E))

    tr_snare.add(r(E))
    tr_snare.add(r(E))
    tr_snare.add(r(E))
    tr_snare.add(r(E))
    tr_snare.add(Note("D", 4, E))
    tr_snare.add(r(E))
    tr_snare.add(r(E))
    tr_snare.add(r(E))

    tr_hat.add(r(E))
    tr_hat.add(r(E))
    tr_hat.add(Note("F#", 6, E))
    tr_hat.add(r(E))
    tr_hat.add(r(E))
    tr_hat.add(r(E))
    tr_hat.add(Note("F#", 6, E))
    tr_hat.add(r(E))

# Reese bass (half-time feel)
tr_bass = song.add_track(Track(name="bass", instrument="reese", volume=0.55))
bass_pattern = [("E", 2, 4.0), ("G", 2, 4.0), ("A", 2, 4.0), ("G", 2, 4.0)]
for _ in range(4):
    for note, oct, dur in bass_pattern:
        tr_bass.add(Note(note, oct, dur))

# Stab lead — sparse melodic hits
tr_lead = song.add_track(Track(name="lead", instrument="stab_lead", volume=0.4, pan=0.15))
lead_hits = [
    ("B", 5, 0.5),
    ("E", 5, 1.5),
    ("G", 5, 0.5),
    ("A", 5, 1.5),
    ("B", 5, 0.5),
    ("G", 5, 0.5),
    ("E", 5, 1.0),
    ("D", 5, 2.0),
]
for _ in range(8):
    for note, oct, dur in lead_hits:
        tr_lead.add(Note(note, oct, dur))

song.effects = {
    "snare": EffectsChain().add(reverb, room_size=0.3, wet=0.15),
    "bass": EffectsChain().add(reverb, room_size=0.2, wet=0.1),
    "lead": EffectsChain().add(delay, delay_ms=172, feedback=0.3, wet=0.2),
}
