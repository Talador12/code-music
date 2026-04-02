"""Spectral Cathedral — frozen and smeared textures in a vast reverberant space."""

from code_music import Chord, EffectsChain, Note, Song, SoundDesigner, Track, reverb
from code_music.sound_design import spectral_freeze, spectral_smear

frozen = (
    SoundDesigner("frozen")
    .add_osc("sawtooth", volume=0.4)
    .add_osc("sawtooth", detune_cents=5, volume=0.3)
    .spectral(spectral_freeze(0.9))
    .envelope(attack=0.5, decay=0.3, sustain=0.5, release=1.0)
    .filter("lowpass", cutoff=2000, resonance=0.4)
)
ghost = (
    SoundDesigner("ghost")
    .add_osc("square", volume=0.3)
    .noise("pink", volume=0.1, seed=7)
    .spectral(spectral_smear(0.7))
    .envelope(attack=0.8, decay=0.3, sustain=0.3, release=1.5)
)
bell = (
    SoundDesigner("bell")
    .fm("sine", mod_ratio=1.414, mod_index=6.0)
    .envelope(attack=0.001, decay=1.5, sustain=0.0, release=1.0)
)

song = Song(title="Spectral Cathedral", bpm=50, sample_rate=44100)
for name, d in [("frozen", frozen), ("ghost", ghost), ("bell", bell)]:
    song.register_instrument(name, d)

song.add_track(Track(name="drone", instrument="frozen", volume=0.3)).add(Note("C", 3, 24.0))
tr_pad = song.add_track(Track(name="pad", instrument="ghost", volume=0.25, pan=-0.2))
tr_pad.add(Chord("C", "min7", 3, duration=12.0))
tr_pad.add(Chord("Ab", "maj7", 3, duration=12.0))
tr_bell = song.add_track(Track(name="bell", instrument="bell", volume=0.2, pan=0.2))
for n, o in [("C", 6), ("Eb", 6), ("G", 6), ("Bb", 6), ("Ab", 6), ("G", 6)]:
    tr_bell.add(Note(n, o, 4.0))

song.effects = {
    "drone": EffectsChain().add(reverb, room_size=0.95, wet=0.6),
    "pad": EffectsChain().add(reverb, room_size=0.9, wet=0.55),
    "bell": EffectsChain().add(reverb, room_size=0.85, wet=0.45),
}
