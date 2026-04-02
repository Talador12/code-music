"""Frozen Harmonics — spectral freeze creates infinite sustain from short sounds."""

from code_music import Chord, EffectsChain, Note, Song, SoundDesigner, Track, reverb
from code_music.sound_design import spectral_freeze

frozen_string = (
    SoundDesigner("frozen_string")
    .physical_model("karplus_strong", volume=0.8, decay=0.998)
    .spectral(spectral_freeze(0.95))
    .envelope(attack=0.001, decay=0.5, sustain=0.4, release=0.8)
)
frozen_bell = (
    SoundDesigner("frozen_bell")
    .fm("sine", mod_ratio=1.414, mod_index=6.0)
    .spectral(spectral_freeze(0.9))
    .envelope(attack=0.001, decay=1.0, sustain=0.3, release=1.0)
)
sub = (
    SoundDesigner("sub")
    .add_osc("sine", volume=1.0)
    .envelope(attack=0.01, decay=0.3, sustain=0.6, release=0.3)
    .filter("lowpass", cutoff=200, resonance=0.8)
)

song = Song(title="Frozen Harmonics", bpm=60, sample_rate=44100)
for name, d in [("frozen_string", frozen_string), ("frozen_bell", frozen_bell), ("sub", sub)]:
    song.register_instrument(name, d)

# Frozen strings — normally plucked sounds now sustain forever
tr_str = song.add_track(Track(name="string", instrument="frozen_string", volume=0.4))
for n, o in [("C", 4), ("E", 4), ("G", 4), ("C", 5), ("B", 4), ("G", 4), ("E", 4), ("C", 4)]:
    tr_str.add(Note(n, o, 2.0))

# Frozen bell — metallic partials suspended in time
tr_bell = song.add_track(Track(name="bell", instrument="frozen_bell", volume=0.25, pan=0.2))
tr_bell.add(Note("C", 6, 8.0))
tr_bell.add(Note("G", 5, 8.0))

# Sub bass foundation
tr_sub = song.add_track(Track(name="sub", instrument="sub", volume=0.5))
tr_sub.add(Note("C", 2, 8.0))
tr_sub.add(Note("G", 1, 8.0))

song.effects = {
    "string": EffectsChain().add(reverb, room_size=0.85, wet=0.4),
    "bell": EffectsChain().add(reverb, room_size=0.9, wet=0.5),
}
