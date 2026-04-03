"""Song #250 — quarter-thousand milestone. Uses 10+ features from the toolkit.

Retrograde rhythm, stretched melody, pedal point, parallel harmony, chord
voicings, euclidean drums, Markov continuation, SoundDesigner FM synthesis.
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Pattern,
    Song,
    SoundDesigner,
    Track,
    Wavetable,
    euclid,
    reverb,
)
from code_music.composition import continue_melody
from code_music.theory import (
    generate_bass_line,
    parallel_motion,
    pedal_point,
    retrograde_rhythm,
    stretch_melody,
)

# FM bell
bell = (
    SoundDesigner("bell")
    .fm("sine", mod_ratio=1.414, mod_index=6.0)
    .envelope(attack=0.001, decay=1.0, sustain=0.0, release=0.8)
)
# Wavetable pad
_wt = Wavetable.from_harmonics([1.0, 0.5, 0.0, 0.25])
wt_pad = (
    SoundDesigner("wt_pad")
    .add_wavetable(_wt, volume=0.4)
    .add_wavetable(_wt, volume=0.3, detune_cents=5)
    .envelope(attack=0.3, decay=0.2, sustain=0.5, release=0.6)
    .filter("lowpass", cutoff=2000, resonance=0.5)
)

song = Song(title="Two Fifty", bpm=110, sample_rate=44100, key_sig="Am")
song.register_instrument("bell", bell)
song.register_instrument("wt_pad", wt_pad)

# Theme
theme = [
    Note(n, 5, d)
    for n, d in [
        ("A", 0.5),
        ("C", 0.5),
        ("E", 1.0),
        ("G", 0.5),
        ("F", 0.5),
        ("E", 0.5),
        ("C", 0.5),
        ("A", 1.0),
    ]
]

# Variations
retro = retrograde_rhythm(theme)
slow = stretch_melody(theme, 1.5)
harmony = parallel_motion(theme, interval=4)

# Markov continuation
extended = continue_melody(theme, bars=2, key="A", mode="minor", seed_rng=250)

# Build
song.add_track(Track(name="theme", instrument="piano", volume=0.5)).extend(theme)
song.add_track(Track(name="retro", instrument="piano", volume=0.4, pan=0.15)).extend(retro)
song.add_track(Track(name="harmony", instrument="bell", volume=0.25, pan=-0.15)).extend(harmony)
song.add_track(Track(name="pad", instrument="wt_pad", volume=0.3)).extend(
    [Chord("A", "min7", 3, duration=8.0)]
)
song.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(
    pedal_point("A", 2, theme[:4])
)
song.add_track(Track(name="kick", instrument="drums_kick", volume=0.6)).extend(
    euclid(3, 8, "C", 2, 0.5) * 2
)
song.effects = {"pad": EffectsChain().add(reverb, room_size=0.7, wet=0.3)}
