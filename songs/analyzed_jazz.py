"""Analyzed Jazz — jazz song with full analysis report printed."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb
from code_music.composition import song_summary
from code_music.theory import generate_bass_line

song = Song(title="Analyzed Jazz", bpm=130, sample_rate=44100, key_sig="C")
prog = [("D", "min7"), ("G", "dom7"), ("C", "maj7"), ("A", "min7")]
song.add_track(Track(name="pad", instrument="piano", volume=0.45)).extend(
    [Chord(r, s, 4, duration=4.0) for r, s in prog]
)
song.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(
    generate_bass_line(prog, style="walking", seed=42)
)
song.add_track(Track(name="lead", instrument="piano", volume=0.4, pan=0.15)).extend(
    [
        Note(n, 5, 1.0)
        for n in ["D", "F", "A", "C", "B", "D", "G", "F", "E", "G", "C", "B", "A", "C", "E", "G"]
    ]
)
song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.5, wet=0.2),
    "lead": EffectsChain().add(delay, delay_ms=230, feedback=0.15, wet=0.1),
}
print(song_summary(song))
