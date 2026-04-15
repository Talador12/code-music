"""Symphony sketch - demonstrating the multi-movement orchestral system."""

from code_music import (
    Note,
    Chord,
    scale,
    crescendo,
    decrescendo,
    PP,
    P,
    MP,
    MF,
    F,
    FF,
    dynamics,
    octave_up,
    octave_down,
)
from code_music.symphony import Symphony, orchestrate

# Create a three-movement symphony
sym = Symphony(
    title="Symphony No. 1 in C",
    composer="code-music",
)

# --- Movement I: Allegro ---
mvt1 = sym.add_movement("I. Allegro", bpm=132, time_sig=(4, 4), key="C")

# Strings
vln1 = mvt1.add_part("violin_1", "violin", volume=0.6, pan=-0.3)
vln2 = mvt1.add_part("violin_2", "violin", volume=0.5, pan=-0.15)
vla = mvt1.add_part("viola", "viola", volume=0.5, pan=0.0)
vc = mvt1.add_part("cello", "cello", volume=0.55, pan=0.15)
cb = mvt1.add_part("contrabass", "contrabass", volume=0.45, pan=0.25)

# Woodwinds
fl = mvt1.add_part("flute", "flute", volume=0.45, pan=-0.2)
ob = mvt1.add_part("oboe", "oboe", volume=0.4, pan=0.1)

# Theme A: bold ascending figure in C major
theme_a = dynamics(scale("C", "major", 5, length=8), F)
theme_a_harmony = dynamics(scale("C", "major", 4, length=8), MF)
bass_line = dynamics(octave_down(scale("C", "major", 3, length=8)), MF)

vln1.extend(theme_a * 2)
vln2.extend(theme_a_harmony * 2)
vla.extend(dynamics([Chord("C", "maj", 4, duration=4.0)] * 4, MP))
vc.extend(bass_line * 2)
cb.extend(dynamics(octave_down(bass_line), P) * 2)
fl.extend(theme_a * 2)
ob.extend(dynamics(scale("E", "major", 5, length=8), MP) * 2)

# --- Movement II: Andante ---
mvt2 = sym.add_movement("II. Andante", bpm=72, time_sig=(3, 4), key="F")

vln1_2 = mvt2.add_part("violin_1", "violin", volume=0.5, pan=-0.3)
vc_2 = mvt2.add_part("cello", "cello", volume=0.5, pan=0.15)

# Slow, lyrical melody
slow_melody = [
    Note("F", 5, 2.0, velocity=MP),
    Note("A", 5, 1.0, velocity=P),
    Note("G", 5, 2.0, velocity=MP),
    Note("F", 5, 1.0, velocity=P),
    Note("E", 5, 1.5, velocity=MF),
    Note("D", 5, 1.5, velocity=MP),
    Note("C", 5, 3.0, velocity=P),
]
vln1_2.extend(slow_melody * 2)
vc_2.extend(
    [
        Chord("F", "maj", 3, duration=3.0, velocity=P),
        Chord("C", "dom7", 3, duration=3.0, velocity=P),
        Chord("Bb", "maj", 3, duration=3.0, velocity=P),
        Chord("F", "maj", 3, duration=3.0, velocity=P),
    ]
    * 2
)

# --- Movement III: Finale ---
mvt3 = sym.add_movement("III. Finale: Allegro vivace", bpm=152, time_sig=(4, 4), key="C")

vln1_3 = mvt3.add_part("violin_1", "violin", volume=0.7, pan=-0.3)
brass = mvt3.add_part("trumpet", "trumpet", volume=0.6, pan=0.1)
timp = mvt3.add_part("timpani", "timpani", volume=0.65, pan=0.0)

# Fast, triumphant finale theme
finale_theme = dynamics(scale("C", "major", 5, length=16), FF)
vln1_3.extend(finale_theme)
brass.extend(
    dynamics(
        [
            Note("C", 5, 2.0),
            Note("E", 5, 1.0),
            Note("G", 5, 1.0),
            Note("C", 6, 4.0),
        ]
        * 2,
        F,
    )
)
timp.extend(
    dynamics(
        [
            Note("C", 3, 1.0),
            Note.rest(1.0),
            Note("G", 3, 1.0),
            Note.rest(1.0),
        ]
        * 4,
        FF,
    )
)

# Render the full symphony
song = sym.render()
