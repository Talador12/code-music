"""Hip-Hop Theory — boom-bap drums + root bass from theory generators."""

from code_music import Chord, EffectsChain, Note, Song, SoundDesigner, Track, reverb
from code_music.theory import generate_bass_line, generate_drums

sub = (
    SoundDesigner("sub")
    .add_osc("sine", volume=1.0)
    .envelope(attack=0.001, decay=0.3, sustain=0.0, release=0.2)
    .pitch_envelope(start_multiplier=3.0, end_multiplier=1.0, duration=0.03)
    .filter("lowpass", cutoff=150, resonance=0.8)
)

song = Song(title="Hip-Hop Theory", bpm=90, sample_rate=44100)
song.register_instrument("sub", sub)

prog = [("C", "min7"), ("Ab", "maj7"), ("Eb", "maj"), ("Bb", "dom7")]

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3, pan=-0.1))
for root, shape in prog:
    pad.add(Chord(root, shape, 3, duration=4.0))

bass = song.add_track(Track(name="bass", instrument="sub", volume=0.6))
bass.extend(generate_bass_line(prog, style="root"))

drums = generate_drums("hiphop", bars=4)
for name, notes in drums.items():
    instr = {"kick": "drums_kick", "snare": "drums_snare", "hat": "drums_hat"}[name]
    song.add_track(Track(name=name, instrument=instr, volume=0.5)).extend(notes)

lead = song.add_track(Track(name="lead", instrument="piano", volume=0.4, pan=0.2))
for n in ["C", "Eb", "G", "Bb", "Ab", "G", "Eb", "C", "Bb", "Ab", "Eb", "Bb", "G", "Eb", "C", "Bb"]:
    lead.add(Note(n, 5, 1.0))

song.effects = {"pad": EffectsChain().add(reverb, room_size=0.6, wet=0.3)}
