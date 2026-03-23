"""lo_fi_loop.py — a chill lo-fi hip-hop loop in Am.

Structure:
    - Bass: walking Am bassline (sawtooth)
    - Chords: jazz voicings (pad synth, lazy rhythm)
    - Melody: pentatonic wander (piano)
    - Drums: kick + snare + hat pattern (4/4, 90 BPM)

Run:
    code-music examples/lo_fi_loop.py
"""

from code_music import Chord, Note, Song, Track

BARS = 4  # repeat the pattern this many times

song = Song(title="Lo-Fi Loop", bpm=90)

# ---- Bass ----
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.7))
bassline = [
    Note("A", 2, duration=1.0),
    Note("A", 2, duration=0.5),
    Note("C", 3, duration=0.5),
    Note("E", 3, duration=1.0),
    Note("G", 3, duration=1.0),
    Note("A", 2, duration=1.0),
    Note("G", 3, duration=0.5),
    Note("F", 3, duration=0.5),
    Note("E", 3, duration=2.0),
]
for _ in range(BARS):
    bass.extend(bassline)

# ---- Chords ----
chords = song.add_track(Track(name="chords", instrument="pad", volume=0.5))
chord_prog = [
    Chord("A", "min7", 3, duration=4.0),
    Chord("F", "maj7", 3, duration=4.0),
    Chord("C", "maj", 3, duration=2.0),
    Chord("G", "dom7", 3, duration=2.0),
]
for _ in range(BARS):
    chords.extend(chord_prog)

# ---- Melody ----
melody = song.add_track(Track(name="melody", instrument="piano", volume=0.65))
pentatonic_phrase = [
    Note("A", 4, 0.5),
    Note("C", 5, 0.5),
    Note("E", 5, 1.0),
    Note.rest(0.5),
    Note("G", 5, 0.5),
    Note("E", 5, 0.5),
    Note("C", 5, 0.5),
    Note("A", 4, 1.0),
    Note.rest(1.0),
    Note("G", 4, 0.5),
    Note("A", 4, 0.5),
    Note("C", 5, 0.5),
    Note("E", 5, 0.5),
    Note.rest(0.5),
    Note("A", 4, 1.5),
    Note.rest(0.5),
]
for _ in range(BARS):
    melody.extend(pentatonic_phrase)

# ---- Drums ----
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.9))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.75))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.5))

# 4/4: kick on 1+3, snare on 2+4, hat every 8th note (0.5 beat)
kick_beat = [Note("C", 2, 1.0), Note.rest(1.0), Note("C", 2, 1.0), Note.rest(1.0)]
snare_beat = [Note.rest(1.0), Note("D", 3, 1.0), Note.rest(1.0), Note("D", 3, 1.0)]
hat_beat = [Note("F", 5, 0.5)] * 8  # 8 eighth notes

for _ in range(BARS):
    kick.extend(kick_beat)
    snare.extend(snare_beat)
    hat.extend(hat_beat)
