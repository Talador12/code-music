"""orchestral_waltz.py - Orchestral waltz. D major, 180 BPM (3/4 feel).

A Strauss-flavored waltz with string-like pads, plucked pizzicato,
and a classic oom-pah-pah bass pattern. One two three, one two three.

Style: Waltz, D major, 180 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb

song = Song(title="Orchestral Waltz", bpm=180, sample_rate=44100)
r = Note.rest

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.55))
pizz = song.add_track(Track(name="pizz", instrument="pluck", volume=0.4, pan=0.2))
roots = [("D", "D"), ("A", "A"), ("G", "G"), ("A", "A")]
for _ in range(8):
    for low, high in roots:
        bass.extend([Note(low, 2, 1.0), r(1.0), r(1.0)])
        pizz.extend([r(1.0), Note(high, 4, 1.0), Note(high, 4, 1.0)])

strings = song.add_track(Track(name="strings", instrument="pad", volume=0.4))
waltz_chords = [
    Chord("D", "maj", 4, duration=3.0),
    Chord("A", "dom7", 3, duration=3.0),
    Chord("G", "maj", 3, duration=3.0),
    Chord("A", "dom7", 3, duration=3.0),
]
for _ in range(8):
    strings.extend(waltz_chords)

melody = song.add_track(Track(name="melody", instrument="triangle", volume=0.45, pan=-0.1))
phrase = [
    Note("D", 5, 1.0),
    Note("F#", 5, 0.5),
    Note("A", 5, 0.5),
    Note("D", 6, 1.0),
    Note("C#", 6, 1.0),
    Note("B", 5, 1.0),
    Note("A", 5, 1.0),
    Note("G", 5, 1.0),
    Note("F#", 5, 0.5),
    Note("E", 5, 0.5),
    Note("D", 5, 1.0),
]
for _ in range(8):
    melody.extend(phrase + [r(3.0)])

song.effects = {
    "strings": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
    "melody": EffectsChain().add(reverb, room_size=0.5, wet=0.25),
}
