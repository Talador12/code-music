"""Granular Clouds - ambient clouds from granular synthesis."""

from code_music import EffectsChain, Note, Song, SoundDesigner, Track, reverb

cloud = (
    SoundDesigner("cloud")
    .granular(grain_size=0.05, density=18, scatter=0.7, seed=42)
    .envelope(attack=0.3, decay=0.1, sustain=0.8, release=0.8)
    .filter("lowpass", cutoff=3000, resonance=0.3)
)

shimmer = (
    SoundDesigner("shimmer")
    .granular(grain_size=0.02, density=30, scatter=0.9, seed=77)
    .envelope(attack=0.5, decay=0.2, sustain=0.6, release=1.0)
    .filter("lowpass", cutoff=5000, resonance=0.4)
)

song = Song(title="Granular Clouds", bpm=60, sample_rate=44100)
song.register_instrument("cloud", cloud)
song.register_instrument("shimmer", shimmer)

pad = song.add_track(Track(name="pad", instrument="cloud", volume=0.4))
for note in ["D", "A", "F", "C"]:
    pad.add(Note(note, 4, 8.0, velocity=40))

high = song.add_track(Track(name="shimmer", instrument="shimmer", volume=0.25, pan=0.3))
for note in ["A", "D", "F", "A"]:
    high.add(Note(note, 6, 8.0, velocity=25))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.35))
bass.add(Note("D", 1, 32.0, velocity=45))

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.9, wet=0.5),
    "shimmer": EffectsChain().add(reverb, room_size=0.95, wet=0.6),
}
