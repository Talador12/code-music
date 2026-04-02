"""Spectral Dreams — all three spectral processors combined in one track."""

from code_music import Chord, EffectsChain, Note, Song, SoundDesigner, Track, reverb
from code_music.sound_design import spectral_freeze, spectral_shift, spectral_smear

# Triple-processed: freeze + shift + smear
dream = (
    SoundDesigner("dream")
    .add_osc("sawtooth", volume=0.3)
    .add_osc("triangle", detune_cents=3, volume=0.3)
    .spectral(spectral_freeze(0.7))
    .spectral(spectral_shift(5.0))
    .spectral(spectral_smear(0.4))
    .envelope(attack=0.5, decay=0.3, sustain=0.4, release=1.0)
    .filter("lowpass", cutoff=3000, resonance=0.5)
)
crystal = (
    SoundDesigner("crystal")
    .add_osc("sine", volume=0.5)
    .spectral(spectral_shift(12.0))
    .envelope(attack=0.005, decay=0.5, sustain=0.0, release=0.3)
)
deep = (
    SoundDesigner("deep")
    .add_osc("sawtooth", volume=0.5)
    .spectral(spectral_shift(-7.0))
    .envelope(attack=0.1, decay=0.2, sustain=0.5, release=0.4)
    .filter("lowpass", cutoff=500, resonance=1.0)
)

song = Song(title="Spectral Dreams", bpm=65, sample_rate=44100)
for name, d in [("dream", dream), ("crystal", crystal), ("deep", deep)]:
    song.register_instrument(name, d)

tr_dream = song.add_track(Track(name="dream", instrument="dream", volume=0.3))
tr_dream.add(Chord("D", "min9", 3, duration=8.0))
tr_dream.add(Chord("Bb", "maj7", 3, duration=8.0))

tr_crystal = song.add_track(Track(name="crystal", instrument="crystal", volume=0.25, pan=0.2))
for n, o, d in [
    ("D", 6, 2.0),
    ("F", 6, 1.5),
    ("A", 6, 2.5),
    ("G", 6, 2.0),
    ("F", 6, 1.5),
    ("D", 6, 2.0),
    ("C", 6, 2.5),
    ("D", 6, 2.0),
]:
    tr_crystal.add(Note(n, o, d))

tr_deep = song.add_track(Track(name="deep", instrument="deep", volume=0.4))
tr_deep.add(Note("D", 2, 8.0))
tr_deep.add(Note("Bb", 1, 8.0))

song.effects = {
    "dream": EffectsChain().add(reverb, room_size=0.95, wet=0.6),
    "crystal": EffectsChain().add(reverb, room_size=0.85, wet=0.45),
}
