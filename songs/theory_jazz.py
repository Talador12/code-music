"""Theory Jazz — ii-V-I with walking bass and jazz drums from generators."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb
from code_music.theory import generate_bass_line, generate_drums

song = Song(title="Theory Jazz", bpm=130, sample_rate=44100)
prog = [("D", "min7"), ("G", "dom7"), ("C", "maj7"), ("A", "min7")]

pad = song.add_track(Track(name="pad", instrument="piano", volume=0.45))
for root, shape in prog:
    pad.add(Chord(root, shape, 4, duration=4.0))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
bass.extend(generate_bass_line(prog, style="walking", seed=42))

drums = generate_drums("jazz", bars=4)
for name, notes in drums.items():
    instr = {"kick": "drums_kick", "snare": "drums_snare", "hat": "drums_hat"}[name]
    song.add_track(Track(name=name, instrument=instr, volume=0.4)).extend(notes)

lead = song.add_track(Track(name="lead", instrument="piano", volume=0.4, pan=0.15))
for n in ["D", "F", "A", "C", "B", "D", "G", "F", "E", "G", "C", "B", "A", "C", "E", "G"]:
    lead.add(Note(n, 5, 1.0))

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.5, wet=0.2),
    "lead": EffectsChain().add(delay, delay_ms=230, feedback=0.15, wet=0.1),
}
