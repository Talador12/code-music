"""Timbre Morph — two contrasting timbres and their spectral midpoint."""

from code_music import Chord, EffectsChain, Note, Song, SoundDesigner, Track, reverb
from code_music.sound_design import spectral_shift

bright = (
    SoundDesigner("bright")
    .add_osc("sawtooth", volume=0.5)
    .add_osc("sawtooth", detune_cents=8, volume=0.3)
    .envelope(attack=0.01, decay=0.1, sustain=0.6, release=0.3)
    .filter("lowpass", cutoff=5000, resonance=0.8)
)
dark = (
    SoundDesigner("dark")
    .add_osc("triangle", volume=0.5)
    .add_osc("sine", volume=0.3)
    .envelope(attack=0.3, decay=0.2, sustain=0.5, release=0.8)
    .filter("lowpass", cutoff=800, resonance=0.5)
)
shifted = (
    SoundDesigner("shifted")
    .add_osc("sawtooth", volume=0.4)
    .spectral(spectral_shift(-5.0))
    .envelope(attack=0.2, decay=0.2, sustain=0.5, release=0.5)
    .filter("lowpass", cutoff=2000, resonance=0.6)
)

# Analyze for the docstring
t_b = bright.analyze()
t_d = dark.analyze()
print(f"Bright: {t_b.to_dict()}")
print(f"Dark: {t_d.to_dict()}")
print(f"Distance: {t_b.distance(t_d):.3f}")

song = Song(title="Timbre Morph", bpm=85, sample_rate=44100)
for name, d in [("bright", bright), ("dark", dark), ("shifted", shifted)]:
    song.register_instrument(name, d)

tr_bright = song.add_track(Track(name="bright", instrument="bright", volume=0.5, pan=0.2))
for n in ["E", "G", "B", "E", "D", "B", "G", "E"]:
    tr_bright.add(Note(n, 5, 1.0))

tr_dark = song.add_track(Track(name="dark", instrument="dark", volume=0.4, pan=-0.2))
tr_dark.add(Chord("E", "min7", 3, duration=4.0))
tr_dark.add(Chord("C", "maj7", 3, duration=4.0))

tr_shifted = song.add_track(Track(name="shifted", instrument="shifted", volume=0.35))
tr_shifted.add(Note("E", 4, 4.0))
tr_shifted.add(Note("C", 4, 4.0))

song.effects = {
    "bright": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
    "dark": EffectsChain().add(reverb, room_size=0.8, wet=0.4),
}
