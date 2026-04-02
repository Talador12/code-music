"""Grain Cathedral — ambient granular textures with physical modeling accents."""

from code_music import EffectsChain, Note, Song, SoundDesigner, Track, reverb

cloud = (
    SoundDesigner("cloud")
    .add_osc("sine", volume=0.2)
    .granular(grain_size=0.08, density=18, scatter=0.8, volume=0.8, seed=42)
    .envelope(attack=0.8, decay=0.3, sustain=0.4, release=1.5)
    .filter("lowpass", cutoff=2000, resonance=0.4)
)
guitar = (
    SoundDesigner("guitar")
    .physical_model("karplus_strong", volume=0.9, decay=0.998, brightness=0.4)
    .envelope(attack=0.001, decay=0.6, sustain=0.1, release=0.4)
)
gong = (
    SoundDesigner("gong")
    .physical_model("modal", volume=0.8)
    .envelope(attack=0.001, decay=2.0, sustain=0.05, release=1.5)
)

song = Song(title="Grain Cathedral", bpm=55, sample_rate=44100)
for name, d in [("cloud", cloud), ("guitar", guitar), ("gong", gong)]:
    song.register_instrument(name, d)

song.add_track(Track(name="cloud", instrument="cloud", volume=0.3)).add(Note("C", 4, 24.0))
tr_g = song.add_track(Track(name="guitar", instrument="guitar", volume=0.45))
for n in ["C", "E", "G", "C", "B", "G", "E", "C", "D", "F", "A", "D"]:
    tr_g.add(Note(n, 4, 2.0))
tr_gong = song.add_track(Track(name="gong", instrument="gong", volume=0.2, pan=-0.2))
tr_gong.add(Note("C", 3, 6.0))
tr_gong.add(Note.rest(6.0))
tr_gong.add(Note("G", 3, 6.0))
tr_gong.add(Note.rest(6.0))

song.effects = {
    "cloud": EffectsChain().add(reverb, room_size=0.95, wet=0.6),
    "gong": EffectsChain().add(reverb, room_size=0.9, wet=0.5),
}
