"""Tension Arc — a progression designed to trace a complete tension curve."""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb
from code_music.theory import tension_curve

song = Song(title="Tension Arc", bpm=72)

# Build a progression that rises in tension then resolves
prog = [
    ("C", "maj"),  # rest (tonic)
    ("A", "min"),  # gentle tonic function
    ("D", "min7"),  # subdominant — building
    ("F#", "dim7"),  # chromatic — peak tension
    ("G", "dom7"),  # dominant — hanging on the edge
    ("C", "maj"),  # resolution — home
]

# Calculate and print tension values (embedded in the song for reference)
curve = tension_curve(prog, key="C")

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4, pan=-0.1))
for root, shape in prog:
    pad.add(Chord(root, shape, 3, duration=8.0))

# Melody that follows the tension: higher notes at higher tension
lead = song.add_track(Track(name="lead", instrument="triangle", volume=0.5, pan=0.15))
for i, (root, _) in enumerate(prog):
    t = curve[i]
    # Map tension to pitch height: low tension = C5, high tension = G6
    oct = 5 + int(t * 1.5)
    lead.extend(
        [
            Note("C", oct, 2.0),
            Note("E", oct, 2.0),
            Note("G", oct, 2.0),
            Note("C", oct, 2.0),
        ]
    )

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.8, wet=0.4),
    "lead": EffectsChain().add(reverb, room_size=0.5, wet=0.25),
}
