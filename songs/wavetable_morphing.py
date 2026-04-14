"""Wavetable Morphing - scanning wavetable banks for evolving timbres."""

from code_music import Chord, Note, Song, SoundDesigner, Track, scale
from code_music.sound_design import Wavetable

song = Song(title="Wavetable Morphing", bpm=100, sample_rate=44100)

# Build a wavetable bank: sine -> saw -> square -> triangle
bank = [
    Wavetable.from_wave("sine"),
    Wavetable.from_wave("sawtooth"),
    Wavetable.from_wave("square"),
    Wavetable.from_wave("triangle"),
]

# Slow-scanning lead: timbre evolves over 2 seconds per sweep
slow_scan = (
    SoundDesigner("slow_scan")
    .wavetable_scan(bank, scan_rate=0.25, volume=0.7)
    .envelope(attack=0.05, decay=0.2, sustain=0.7, release=0.4)
    .filter("lowpass", cutoff=4500, resonance=0.5)
    .lfo("filter_cutoff", rate=0.3, depth=0.4)
)
song.register_instrument("slow_scan", slow_scan)

# Fast-scanning pad: rapid timbre flutter
fast_scan = (
    SoundDesigner("fast_scan")
    .wavetable_scan(bank[:3], scan_rate=3.0, volume=0.5)
    .envelope(attack=0.3, decay=0.1, sustain=0.8, release=0.6)
    .filter("lowpass", cutoff=3000, resonance=0.4)
)
song.register_instrument("fast_scan", fast_scan)

# Harmonic bank from custom harmonics
harmonic_bank = [
    Wavetable.from_harmonics([1.0]),
    Wavetable.from_harmonics([1.0, 0.5, 0.25]),
    Wavetable.from_harmonics([1.0, 0.5, 0.25, 0.125, 0.0625]),
    Wavetable.from_harmonics([1.0, 0.3, 0.1, 0.3, 0.1, 0.05]),
]
rich_scan = (
    SoundDesigner("rich_scan")
    .wavetable_scan(harmonic_bank, scan_rate=0.5, volume=0.6)
    .envelope(attack=0.1, decay=0.2, sustain=0.6, release=0.3)
    .filter("lowpass", cutoff=5000, resonance=0.6)
)
song.register_instrument("rich_scan", rich_scan)

# Tracks
lead = song.add_track(Track(name="lead", instrument="slow_scan", volume=0.55, pan=0.2))
lead.extend(scale("D", "pentatonic_minor", octave=5, length=16))

pad = song.add_track(Track(name="pad", instrument="fast_scan", volume=0.35, pan=-0.2))
for root, shape in [("D", "min7"), ("G", "min7"), ("A", "min7"), ("D", "min7")] * 2:
    pad.add(Chord(root, shape, 3, duration=4.0, velocity=45))

shimmer = song.add_track(Track(name="shimmer", instrument="rich_scan", volume=0.3, pan=0.0))
for note in scale("D", "major", octave=6, length=8):
    shimmer.add(Note(note.pitch, note.octave, 4.0, velocity=35))

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root in ["D", "D", "G", "A"] * 2:
    bass.add(Note(root, 2, 4.0, velocity=60))
