"""Physical Jazz — Karplus-Strong guitar + waveguide flute + theory bass."""

from code_music import Chord, EffectsChain, Note, Song, SoundDesigner, Track, delay, reverb
from code_music.theory import generate_bass_line, generate_chord_melody

guitar = (
    SoundDesigner("guitar")
    .physical_model("karplus_strong", volume=0.9, decay=0.998, brightness=0.5)
    .envelope(attack=0.001, decay=0.6, sustain=0.1, release=0.4)
)
flute = (
    SoundDesigner("flute")
    .physical_model("waveguide_pipe", volume=0.8, feedback=0.97, brightness=0.65)
    .envelope(attack=0.05, decay=0.1, sustain=0.7, release=0.3)
)

song = Song(title="Physical Jazz", bpm=110, sample_rate=44100)
for n, d in [("guitar", guitar), ("flute", flute)]:
    song.register_instrument(n, d)

prog = [("D", "min7"), ("G", "dom7"), ("C", "maj7"), ("A", "min7")]
song.add_track(Track(name="guitar", instrument="guitar", volume=0.5)).extend(
    generate_chord_melody(prog, contour="arch", seed=88)
)
song.add_track(Track(name="flute", instrument="flute", volume=0.4, pan=0.2)).extend(
    [
        Note(n, 5, 1.0)
        for n in ["D", "F", "A", "C", "B", "G", "D", "F", "E", "G", "C", "B", "A", "E", "C", "A"]
    ]
)
song.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(
    generate_bass_line(prog, style="walking", seed=88)
)
song.add_track(Track(name="pad", instrument="pad", volume=0.3)).extend(
    [Chord(r, s, 3, duration=4.0) for r, s in prog]
)
song.effects = {
    "guitar": EffectsChain().add(reverb, room_size=0.5, wet=0.2),
    "flute": EffectsChain().add(delay, delay_ms=200, feedback=0.15, wet=0.1),
}
