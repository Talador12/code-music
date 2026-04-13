"""Rootless Voicings — jazz piano without root notes (bass handles it)."""

from code_music import EffectsChain, Song, Track, reverb
from code_music.theory import generate_bass_line, generate_chord_voicing

song = Song(title="Rootless Voicings", bpm=95, sample_rate=44100)
prog = [("A", "min7"), ("D", "dom7"), ("G", "maj7"), ("C", "maj7")]
tr_piano = song.add_track(Track(name="piano", instrument="piano", volume=0.45))
for root, shape in prog:
    tr_piano.extend(generate_chord_voicing(root, shape, voicing="rootless"))
song.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(
    generate_bass_line(prog, style="root_fifth")
)
song.effects = {"piano": EffectsChain().add(reverb, room_size=0.5, wet=0.2)}
