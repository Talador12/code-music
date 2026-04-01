"""Minor jazz at midnight: saxophone alone over diminished chords, Dm, slow.

Alluring. This is the music playing in the bar you weren't supposed
to walk into. The saxophone says things words can't.
"""

from code_music import Chord, Note, Song, Track, delay, reverb

song = Song(title="minor_jazz_midnight", bpm=88)

# Dark, diminished chord voicings underneath
pad = song.add_track(Track(name="pad", instrument="rhodes", volume=0.45, pan=-0.2, swing=0.5))
prog = [
    Chord("D", "min7", 3, duration=4.0, velocity=0.5),
    Chord("G", "dom7", 3, duration=4.0, velocity=0.48),
    Chord("E", "dim", 3, duration=4.0, velocity=0.45),
    Chord("A", "dom7", 3, duration=4.0, velocity=0.5),
]
for _ in range(2):
    pad.extend(prog)

# Contrabass: low, arco, brooding
bass = song.add_track(Track(name="bass", instrument="contrabass", volume=0.65, pan=0.15, swing=0.5))
for p, o, dur in [
    ("D", 2, 2),
    ("A", 1, 1),
    ("G", 1, 1),
    ("F#", 1, 2),
    ("G", 1, 2),
    ("E", 2, 2),
    ("F", 2, 1),
    ("E", 2, 1),
    ("A", 1, 2),
    ("D", 2, 2),
]:
    bass.add(Note(p, o, float(dur), velocity=0.6))

# Saxophone solo — searching, not finding
sax = song.add_track(Track(name="sax", instrument="saxophone", volume=0.8, pan=0.05, swing=0.52))
solo = [
    Note.rest(1.5),
    Note("A", 4, 0.5),
    Note("C", 5, 0.5),
    Note("D", 5, 1.0),
    Note("F", 5, 0.5),
    Note.rest(0.5),
    Note("E", 5, 0.5),
    Note("D", 5, 0.5),
    Note("C", 5, 2.0),
    Note.rest(1.0),
    Note("G", 4, 0.5),
    Note("A", 4, 0.25),
    Note("A#", 4, 0.25),
    Note("C", 5, 0.5),
    Note("E", 5, 0.5),
    Note("D", 5, 1.5),
    Note.rest(0.5),
    Note("F", 5, 0.5),
    Note("E", 5, 0.5),
    Note("D", 5, 0.5),
    Note("C", 5, 0.5),
    Note("A", 4, 4.0),
]
sax.extend(solo)

song.effects = {
    "sax": lambda s, sr: delay(
        reverb(s, sr, room_size=0.4, wet=0.15), sr, delay_ms=272.0, feedback=0.25, wet=0.12
    ),
    "pad": lambda s, sr: reverb(s, sr, room_size=0.55, wet=0.2),
    "bass": lambda s, sr: reverb(s, sr, room_size=0.4, wet=0.12),
}
