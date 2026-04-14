"""Chiptune Adventure - 8-bit square wave retro game music."""

from code_music import Note, Song, SoundDesigner, Track, scale

chip = (
    SoundDesigner("chip")
    .add_osc("square", volume=0.5)
    .add_osc("square", detune_cents=5, volume=0.3)
    .envelope(attack=0.005, decay=0.05, sustain=0.4, release=0.1)
    .filter("lowpass", cutoff=2500, resonance=0.5)
)

song = Song(title="Chiptune Adventure", bpm=150, sample_rate=44100)
song.register_instrument("chip", chip)

lead = song.add_track(Track(name="lead", instrument="chip", volume=0.5, pan=0.1))
lead.extend(scale("C", "major", octave=5, length=16))
lead.extend(scale("C", "major", octave=5, length=16))

bass = song.add_track(Track(name="bass", instrument="chip", volume=0.4))
for root in ["C", "G", "A", "F"] * 4:
    bass.add(Note(root, 3, 2.0, velocity=60))

# Arpeggio
arp = song.add_track(Track(name="arp", instrument="chip", volume=0.3, pan=-0.2))
for root in ["C", "E", "G", "C", "B", "G", "E", "C"] * 4:
    arp.add(Note(root, 5, 0.5, velocity=45))
