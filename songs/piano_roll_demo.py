"""Piano Roll Demo - generates a song and exports its piano roll SVG."""

from code_music import Chord, Note, Song, Track, scale
from code_music.composition import to_piano_roll

song = Song(title="Piano Roll Demo", bpm=120, sample_rate=44100)

# Lead melody
lead = song.add_track(Track(name="lead", instrument="piano", volume=0.55, pan=0.15))
lead.extend(scale("C", "major", octave=5, length=16))

# Bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
for root in ["C", "C", "F", "G"] * 2:
    bass.add(Note(root, 2, 2.0, velocity=65))

# Chords
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.35, pan=-0.1))
for root, shape in [("C", "maj7"), ("F", "maj"), ("G", "dom7"), ("C", "maj")] * 2:
    pad.add(Chord(root, shape, 4, duration=4.0, velocity=45))

# Generate piano roll (SVG written to dist/ if desired)
svg = to_piano_roll(song)
print(f"  Piano roll: {len(svg)} chars SVG")
