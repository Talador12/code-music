"""Release Ready — a fully mastered ambient track ready for Spotify."""

from code_music import Chord, EffectsChain, Note, Song, SoundDesigner, Track, reverb

warm = (
    SoundDesigner("warm")
    .add_osc("sine", volume=0.4)
    .add_osc("triangle", detune_cents=3, volume=0.3)
    .add_osc("triangle", detune_cents=-3, volume=0.3)
    .envelope(attack=0.5, decay=0.3, sustain=0.5, release=1.0)
    .filter("lowpass", cutoff=1500, resonance=0.4)
    .lfo("filter_cutoff", rate=0.1, depth=0.3)
)
bell = (
    SoundDesigner("bell")
    .fm("sine", mod_ratio=1.414, mod_index=5.0)
    .envelope(attack=0.001, decay=0.8, sustain=0.0, release=0.6)
)

song = Song(title="Release Ready", bpm=60, sample_rate=44100)
for name, d in [("warm", warm), ("bell", bell)]:
    song.register_instrument(name, d)

tr_pad = song.add_track(Track(name="pad", instrument="warm", volume=0.4, pan=-0.1))
tr_pad.add(Chord("A", "min7", 3, duration=8.0))
tr_pad.add(Chord("F", "maj7", 3, duration=8.0))

tr_bell = song.add_track(Track(name="bell", instrument="bell", volume=0.25, pan=0.2))
for n, o in [("A", 5), ("C", 6), ("E", 6), ("D", 6), ("C", 6), ("A", 5), ("G", 5), ("A", 5)]:
    tr_bell.add(Note(n, o, 2.0))

tr_bass = song.add_track(Track(name="bass", instrument="bass", volume=0.4))
tr_bass.add(Note("A", 2, 8.0))
tr_bass.add(Note("F", 2, 8.0))

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.85, wet=0.45),
    "bell": EffectsChain().add(reverb, room_size=0.8, wet=0.4),
}
