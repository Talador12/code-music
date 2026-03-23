"""Daft Punk-style chord stab: funky filtered house stabs, Em, 124 BPM.

Daft Punk signature: sampled-feel chord hits, robot vocoders implied,
tight funk groove. Stab + bass lock.
"""

from code_music import Chord, Note, Song, Track

song = Song(title="daft_punk_stab", bpm=124)
r = Note.rest

# Chord stabs — square wave, tight attack
stabs = song.add_track(Track(name="stabs", instrument="stab", volume=0.8, pan=-0.1))
# Classic Em funk groove stabs
pattern = [
    Chord("E", "min7", 3, duration=0.5),
    r(0.25),
    Chord("E", "min7", 3, duration=0.25),
    r(0.5),
    Chord("G", "maj", 3, duration=0.25),
    r(0.25),
    Chord("A", "min7", 3, duration=0.5),
    r(0.5),
    Chord("D", "dom7", 3, duration=0.5),
    r(1.5),
]
for _ in range(4):
    stabs.extend(pattern)

# Funky bass line
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.85, pan=0.1))
bass_pat = [
    Note("E", 2, 0.25),
    Note("E", 2, 0.25),
    Note("G", 2, 0.25),
    Note("E", 2, 0.25),
    Note("A", 2, 0.25),
    Note("E", 2, 0.25),
    Note.rest(0.5),
    Note("D", 2, 0.5),
    Note.rest(0.5),
    Note("E", 2, 0.5),
    Note.rest(0.5),
]
for _ in range(4):
    bass.extend(bass_pat)
