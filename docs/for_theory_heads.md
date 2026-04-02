# For Theory Heads

Full reference. Assumes you know what a tritone substitution is.

## Note durations

```python
from code_music import (
    WHOLE, HALF, QUARTER, EIGHTH, SIXTEENTH, THIRTY_SECOND, SIXTY_FOURTH,
    DOTTED_WHOLE, DOTTED_HALF, DOTTED_QUARTER, DOTTED_EIGHTH,
    DOUBLE_DOTTED_HALF, DOUBLE_DOTTED_QUARTER,
)
# All relative to one beat (quarter note = 1.0 at any BPM)
```

## Tuplets

```python
from code_music import triplet, tuplet, triplets, tuplets, QUARTER, HALF

# Single duration value
triplet(QUARTER)      # 0.667 — one note of a quarter-note triplet
tuplet(QUARTER, 5)    # 0.200 — quintuplet
tuplet(HALF, 7)       # 0.286 — septuplet over a half note

# Build note lists
triplets(["C","E","G"], octave=4, base=QUARTER)    # 3 triplet 8ths in one beat
tuplets(["C","D","E","F","G"], n=5, base=QUARTER)  # quintuplet
```

## Ornaments

All ornaments return a `list[Note]` — add them with `tr.extend(...)`.
Duration is redistributed: ornament notes steal time from the main note.

```python
from code_music import (
    trill, mordent, upper_mordent, turn,
    grace_note, doit, fall, flip, shake,
    QUARTER, EIGHTH, THIRTY_SECOND,
)

trill(Note("A", 4, HALF), semitones=1, speed=THIRTY_SECOND, count=8)
mordent(Note("E", 5, QUARTER), semitones=1)         # lower mordent
upper_mordent(Note("E", 5, QUARTER), semitones=1)   # Pralltriller
turn(Note("G", 5, QUARTER), semitones=1)            # ~
grace_note("B", Note("C", 5, QUARTER))              # acciaccatura
doit(Note("Bb", 4, QUARTER), semitones=2, steps=4)  # jazz bend up
fall(Note("G",  5, QUARTER), semitones=3, steps=4)  # jazz fall
flip(Note("D",  5, QUARTER), semitones=2)           # upward scoop
shake(Note("Bb",4, HALF),   semitones=2, count=6)   # wide brass trill
```

## Articulations

```python
from code_music import staccato, legato, pizzicato

staccato(notes, factor=0.5)    # shorten to 50%, fill with rest
legato(notes, overlap=0.1)     # extend each note by 0.1 beats
pizzicato(notes)                # staccato at 15% — plucked strings
```

## Scales reference (full set)

```python
from code_music import scale, SCALES

# All available modes
print(sorted(SCALES.keys()))

# Usage: scale(root, mode, octave, octaves=N)
scale("C", "major",           4, octaves=2)
scale("D", "dorian",          4, octaves=1)
scale("E", "phrygian",        4)
scale("F", "lydian",          4)
scale("G", "mixolydian",      4)
scale("A", "aeolian",         4)    # same as "minor"
scale("B", "locrian",         4)
scale("A", "harmonic_minor",  4)
scale("A", "melodic_minor",   4)    # jazz stays raised both ways
scale("E", "phrygian_dominant", 4)  # Spanish/flamenco
scale("C", "whole_tone",      4)    # 6-note, fully symmetric
scale("D", "diminished",      4)    # H-W, 8-note
scale("D", "diminished_hw",   4)    # W-H
scale("C", "augmented",       4)    # m3 + h alternating
scale("Bb","bebop_dominant",  4)    # Mixolydian + maj7 passing tone
scale("F", "lydian_dominant", 4)    # #4 + b7 — fusion
scale("C", "super_locrian",   4)    # altered scale, V7alt
scale("A", "pentatonic",      4)    # major pentatonic
scale("A", "pentatonic_minor",4)
scale("A", "blues",           4)    # minor pentatonic + b5
scale("G", "hungarian_minor", 4)    # two aug 2nds
scale("E", "arabic",          4)    # double harmonic
scale("D", "japanese",        4)    # Hirajoshi
scale("E", "in_sen",          4)
scale("C", "persian",         4)

# Reference path (special ordering helper)
# make play-scale-circle_of_fifths
```

## All chord shapes

```python
from code_music import CHORD_SHAPES

# Triads
Chord("C", "maj")    Chord("C", "min")    Chord("C", "dim")    Chord("C", "aug")

# 7ths
Chord("C", "maj7")   Chord("C", "min7")   Chord("C", "dom7")   Chord("C", "min7b5")

# Extended
Chord("C", "9")      Chord("C", "min9")   Chord("C", "maj9")
Chord("C", "11")     Chord("C", "13")
Chord("C", "6")      Chord("C", "min6")   Chord("C", "6/9")

# Suspended
Chord("C", "sus2")   Chord("C", "sus4")

# Special
Chord("C", "power")  Chord("C", "aug7")   Chord("C", "flat5")

# Custom interval offsets
Chord("C", [0, 4, 7, 11, 14])   # Cmaj9 by hand
```

## Composition helpers

```python
from code_music import (
    arp, chord_prog, crescendo, decrescendo,
    transpose, humanize, repeat, generate_melody, prob,
)

# Arp patterns: up, down, up_down, cascade, broken, alberti,
#               outside_in, inside_out, stride, pinky
arp(Chord("A","min7",4), pattern="up_down", rate=0.25, octaves=2)

# Chord progression shorthand
chord_prog(["D","G","A","E"], ["min7","maj7","dom7","min7"],
           octave=3, duration=4.0)

# Dynamics
crescendo(notes, start_vel=0.2, end_vel=0.95)    # works on Notes and Chords
decrescendo(notes, start_vel=0.9, end_vel=0.15)
transpose(notes, semitones=7)                     # up a fifth
humanize(notes, vel_spread=0.08, timing_spread=0.02)

# Generative
generate_melody("A", scale_mode="dorian", octave=4, bars=8,
                density=0.65, seed=42)
prob(Note("A",4,QUARTER), p=0.7)   # plays 70% of the time
```

## Time signatures

```python
song = Song(title="Waltz", bpm=138, time_sig=(3, 4))   # 3/4
song = Song(title="Odd",   bpm=160, time_sig=(7, 8))   # 7/8
song = Song(title="Cut",   bpm=100, time_sig=(2, 2))   # cut time
song.key_sig = "Bb"    # for sheet music export
song.composer = "K. Adler"
```

## EffectsChain (v1.7+)

```python
from code_music import EffectsChain, reverb, delay, compress, stereo_width

# Build an ordered chain — each step has its own wet/dry and bypass
chain = (
    EffectsChain()
    .add(reverb, room_size=0.7, wet=0.3)
    .add(delay, delay_ms=375, feedback=0.3, wet=0.25)
    .add(compress, threshold=0.6, ratio=4.0)
)

song.effects["pad"] = chain              # assign to a track
processed = chain(samples, sample_rate)  # or call directly

chain.set_bypass(1, True)   # mute the delay step
chain.set_wet(0, 0.5)       # pull reverb to 50% wet
len(chain)                   # 3 steps
repr(chain)                  # inspectable
```

## All effects

```python
from code_music import (
    reverb, delay, chorus, flanger, phaser,
    distortion, compress, limiter,
    lowpass, highpass, bandpass,
    tremolo, vibrato, lfo_filter,
    gate, sidechain, stereo_width, noise_sweep, pan,
)

# All take (stereo_array, sample_rate, **kwargs) → stereo_array
reverb(s, sr, room_size=0.7, damping=0.4, wet=0.3)
delay(s, sr, delay_ms=375.0, feedback=0.35, wet=0.25, ping_pong=True)
chorus(s, sr, rate_hz=0.8, depth_ms=3.0, wet=0.4)
flanger(s, sr, rate_hz=0.3, depth_ms=5.0, feedback=0.5, wet=0.5)
phaser(s, sr, rate_hz=0.5, depth=0.7, stages=4, wet=0.5)
distortion(s, drive=3.0, tone=0.5, wet=0.6)
gate(s, sr, rate_hz=4.0, shape="trapezoid", duty=0.5)  # trance gate
lfo_filter(s, sr, rate_hz=0.5, min_cutoff=200.0, max_cutoff=8000.0)
sidechain(target, trigger, sr, threshold=0.3, ratio=8.0, release_ms=80.0)
stereo_width(s, width=1.7)   # M/S widening; 1.0=unchanged, 2.0=very wide
tremolo(s, sr, rate_hz=5.0, depth=0.3)
vibrato(s, sr, rate_hz=5.5, depth_cents=25.0)
```

## All 60 instrument presets

**Waveforms:** sine, square, sawtooth, triangle  
**Keys:** piano, organ, harpsichord, rhodes, wurlitzer, celesta  
**Strings:** strings, violin, cello, contrabass, pizzicato  
**Brass:** trumpet, trombone, french_horn, tuba, brass_section  
**Woodwinds:** flute, oboe, clarinet, bassoon, saxophone, piccolo  
**Plucked:** guitar_acoustic, guitar_electric, harp, marimba, vibraphone, xylophone  
**Orch perc:** timpani, gong, snare_orch, cymbals  
**Choir:** choir_aah, choir_ooh, vox_pad  
**EDM:** bass, pad, pluck, supersaw, reese_bass, acid, hoover, stab, lead_edm, wobble  
**Synth:** formant_a, formant_o, formant_e, fm_bell, moog_bass, sub_bass, portamento  
**Drums:** drums_kick, drums_snare, drums_hat, drums_clap, drums_tom, drums_ride, drums_crash, drums_808  

## Per-note LFO filter (wobble bass)

The `wobble` preset applies an LFO-swept LP filter per note automatically.
Access/override the preset directly:

```python
from code_music.synth import Synth
Synth.PRESETS["wobble"]["lfo_rate"]       = 4.0     # faster wobble
Synth.PRESETS["wobble"]["lfo_min_cutoff"] = 60.0
Synth.PRESETS["wobble"]["lfo_max_cutoff"] = 5000.0
```

## Style profiles

```python
from styles.progressive_house import PROFILE
from styles.bebop_jazz         import PROFILE
from styles.cinematic_orchestral import PROFILE
from styles.big_room_electro   import PROFILE
from styles.cosmic_electro_disco import PROFILE
from styles.liquid_dnb         import PROFILE
from styles.ambient            import PROFILE

# Each profile contains:
PROFILE["bpm_typical"]          # int
PROFILE["scales"]               # list of scale mode names
PROFILE["chord_progressions"]   # list of (root, shape, octave, bars) tuples
PROFILE["instruments"]          # dict of role → preset name
PROFILE["effects"]              # dict of role → effect settings
PROFILE["notes"]                # free-form theory analysis string
```

## Sheet music export

```python
from code_music.notation import export_lilypond, export_abc, export_musicxml

export_lilypond(song, "my_song.ly")   # compile: lilypond my_song.ly → PDF
export_abc(song, "my_song.abc")       # web preview: abc.rectanglered.com
export_musicxml(song, "my_song.xml")  # MuseScore, Sibelius, Dorico, Finale
```

## MIDI export

```python
from code_music.midi import export_midi
export_midi(song, "my_song.mid")   # SMF type 1, GM programs, channel 10 drums
```

## MIDI import (v1.8+)

```python
from code_music import import_midi

# Parse any .mid file into a Song
song = import_midi("existing.mid")
song.bpm = 140                     # re-tempo
play(song)                         # listen immediately

# Override instrument mapping
song = import_midi("piano_piece.mid", instrument="pad")

# CLI: render a .mid directly to WAV
# code-music dummy.py --import-midi existing.mid -o remix.wav
```

## Sound design (v6.0+)

Build instruments from oscillators, noise, filters, LFOs, and envelopes:

```python
from code_music import SoundDesigner
from code_music.sound_design import PRESETS  # 5 built-in designs

# Multi-oscillator with detuning + filter + LFO
wobble = (
    SoundDesigner("wobble")
    .add_osc("sawtooth", detune_cents=0, volume=0.4)
    .add_osc("sawtooth", detune_cents=5, volume=0.3)
    .add_osc("sawtooth", detune_cents=-5, volume=0.3)
    .noise("pink", volume=0.1)                         # noise layer
    .envelope(attack=0.2, decay=0.1, sustain=0.6, release=0.5)
    .filter("lowpass", cutoff=2000, resonance=1.5)
    .lfo("filter_cutoff", rate=0.4, depth=0.6)         # wobble the filter
)

# Pitch envelope for kick/808 sounds
kick = (
    SoundDesigner("kick")
    .add_osc("sine", volume=1.0)
    .envelope(attack=0.001, decay=0.3, sustain=0.0, release=0.15)
    .pitch_envelope(start_multiplier=6.0, end_multiplier=1.0, duration=0.03)
)

# Register and use in a song
song.register_instrument("wobble", wobble)
tr = song.add_track(Track(instrument="wobble"))

# Render standalone
audio = wobble.render(freq=440.0, duration=2.0, sr=44100)  # mono float64

# Serialize / restore
data = wobble.to_dict()           # JSON-compatible dict
restored = SoundDesigner.from_dict(data)

# Export to WAV
wobble.to_wav("wobble_c4.wav", freq=261.63, duration=2.0)
```

Built-in presets: `supersaw`, `sub_808`, `metallic_hit`, `vocal_pad`, `plucked_string`,
`fm_electric_piano`, `fm_bell`, `fm_brass`, `fm_bass`, `wt_organ`, `wt_bright_lead`, `wt_morph_pad`

## FM synthesis (v7.0+)

```python
# Frequency modulation: modulator oscillator modulates carrier frequency
epiano = SoundDesigner("epiano").fm("sine", mod_ratio=2.0, mod_index=3.5)

# Multi-operator (stack .fm() calls like DX7 operators)
bell = (
    SoundDesigner("bell")
    .fm("sine", mod_ratio=1.414, mod_index=8.0, volume=0.7)   # inharmonic = metallic
    .fm("sine", mod_ratio=3.0, mod_index=2.0, volume=0.3)
)

# mod_ratio: modulator/carrier freq ratio. Integer = harmonic, non-integer = metallic.
# mod_index: modulation depth. 0 = pure carrier, 5+ = rich harmonics.
```

## Wavetable synthesis (v7.0+)

```python
from code_music import Wavetable

# Build from harmonic amplitudes (additive → single cycle)
wt = Wavetable.from_harmonics([1.0, 0.5, 0.0, 0.25])

# Build from named wave shape
wt_saw = Wavetable.from_wave("sawtooth")

# Morph between two wavetables
hybrid = wt_saw.morph(Wavetable.from_wave("square"), 0.4)

# Use as oscillator in SoundDesigner
sd = SoundDesigner("custom").add_wavetable(wt, volume=0.6, detune_cents=5)
```

## Euclidean rhythms (v7.0+)

```python
from code_music import euclid

# Bjorklund algorithm: distribute N hits across M slots
tr.extend(euclid(3, 8, "C", 4, 0.5))           # tresillo [x..x..x.]
tr.extend(euclid(5, 8, "C", 4, 0.5))           # West African
tr.extend(euclid(5, 16, "C", 4, 0.25))         # son clave
tr.extend(euclid(3, 8, "C", 4, 0.5, rotation=2))  # rotated pattern
```

Oscillators: `sine`, `sawtooth`, `square`, `triangle`
Noise: `white`, `pink` (1/f), `brown` (cumulative)
Filters: `lowpass`, `highpass`, `bandpass` (biquad, scipy-free)
LFO targets: `filter_cutoff`, `pitch`, `volume`

## Voice synthesis

```python
from code_music import VoiceClip, VoiceTrack

song.add_voice_track(
    VoiceTrack("vox").add(
        VoiceClip("aaah", voice="Cellos", backend="say", rate=80, pan=-0.3),
        beat_offset=0.0
    )
)
# backends: "say" (macOS, zero deps), "bark" (AI), "elevenlabs", "openai"
# optional per-clip pacing: pause_short_sec / pause_terminal_sec
# (override punctuation pause timing used for voice timeline estimation)
# convenience constructors:
#   VoiceClip.narration("...")  # slower, more pauses
#   VoiceClip.rap("...")        # faster, tighter pauses

# voice-only timeline note:
# estimated duration uses text length + clip rate + punctuation pauses
# (commas, semicolons, colons, and sentence endings) so render length
# better matches natural phrasing before synthesis runs.
```

---

*Engine internals and extension points → [For Developers](for_developers.md)*
