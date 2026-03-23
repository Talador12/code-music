"""prog_rock.py — a prog-rock inspired piece in D Dorian.

Structure:
    - Intro: solo organ riff (bars 1-2)
    - Verse: bass + sawtooth lead over Dm7 vamp (bars 3-6)
    - Chorus: full texture, chord stabs + melodic peak (bars 7-8)
    - Outro: decay back to organ solo (bars 9-10)

Run:
    code-music examples/prog_rock.py
"""

from code_music import Chord, Note, Song, Track

song = Song(title="Prog Rock", bpm=130)

# ---- Intro organ riff (Dorian feel: D E F G A B C) ----
organ = song.add_track(Track(name="organ", instrument="organ", volume=0.7))
dorian_riff = [
    Note("D", 4, 0.5),
    Note("E", 4, 0.5),
    Note("F", 4, 0.5),
    Note("G", 4, 0.5),
    Note("A", 4, 1.0),
    Note("B", 4, 0.5),
    Note("A", 4, 0.5),
    Note("G", 4, 0.5),
    Note("F", 4, 0.5),
    Note("E", 4, 1.0),
    Note.rest(1.0),
]
organ.extend(dorian_riff)  # bars 1-2

# ---- Bass ostinato ----
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.85))
bass_ostinato = [
    Note("D", 2, 0.5),
    Note("D", 2, 0.5),
    Note("A", 2, 0.5),
    Note("C", 3, 0.5),
    Note("D", 2, 0.5),
    Note("F", 2, 0.5),
    Note("G", 2, 0.5),
    Note("A", 2, 0.5),
]
bass.extend([Note.rest(8.0)])  # rest during intro
for _ in range(4):  # bars 3-6 verse
    bass.extend(bass_ostinato)
for _ in range(2):  # bars 7-8 chorus (drive it)
    bass.extend(bass_ostinato)
bass.extend([Note.rest(8.0)])  # outro rest

# ---- Lead (sawtooth) verse melody ----
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.6))
verse_melody = [
    Note.rest(0.5),
    Note("A", 4, 0.5),
    Note("G", 4, 0.5),
    Note("F", 4, 0.5),
    Note("E", 4, 1.0),
    Note("D", 4, 0.5),
    Note.rest(0.5),
    Note("C", 4, 0.5),
    Note("D", 4, 0.5),
    Note("F", 4, 1.0),
    Note.rest(0.5),
]
lead.extend([Note.rest(8.0)])  # silence during intro
for _ in range(4):
    lead.extend(verse_melody)

# ---- Chorus chord stabs ----
chords = song.add_track(Track(name="chords", instrument="square", volume=0.55))
chords.extend([Note.rest(8.0)])  # intro
chords.extend([Note.rest(16.0)])  # verse
chorus_stabs = [
    Chord("D", "min7", 3, duration=1.0),
    Note.rest(1.0),
    Chord("G", "dom7", 3, duration=1.0),
    Note.rest(1.0),
    Chord("C", "maj7", 3, duration=1.0),
    Note.rest(1.0),
    Chord("A", "min7", 3, duration=1.0),
    Note.rest(1.0),
]
for _ in range(2):
    chords.extend(chorus_stabs)

# ---- Chorus high melody peak ----
peak = song.add_track(Track(name="peak", instrument="sine", volume=0.7))
peak.extend([Note.rest(24.0)])  # intro + verse
chorus_peak = [
    Note("D", 5, 1.0),
    Note("C", 5, 1.0),
    Note("B", 4, 0.5),
    Note("A", 4, 0.5),
    Note("G", 4, 1.0),
    Note("A", 4, 0.5),
    Note("B", 4, 0.5),
    Note("C", 5, 1.0),
    Note("D", 5, 2.0),
]
peak.extend(chorus_peak)
peak.extend(chorus_peak)

# ---- Outro: organ returns ----
organ.extend([Note.rest(32.0)])  # skip verse + chorus
organ.extend(dorian_riff)
organ.extend(dorian_riff)
