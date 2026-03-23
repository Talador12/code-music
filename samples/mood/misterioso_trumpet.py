"""Noir trumpet: Miles Davis cool, Dm, muted, 72 BPM. 2am. A secret.

Alluring. The trumpet plays like it knows something you don't.
Long rests that are almost uncomfortable. Notes that bend down
at the end, unresolved. You lean in.
"""

from code_music import Chord, Note, Song, Track, delay, humanize, reverb

song = Song(title="noir_trumpet", bpm=72)

# Sparse, dark piano underneath
piano = song.add_track(Track(name="piano", instrument="rhodes", volume=0.42, pan=-0.25, swing=0.5))
changes = [
    Chord("D", "min7", 3, duration=4.0, velocity=0.45),
    Chord("G", "dim", 3, duration=4.0, velocity=0.4),
    Chord("E", "min7", 3, duration=4.0, velocity=0.42),
    Chord("A", "dom7", 3, duration=4.0, velocity=0.45),
]
piano.extend(changes * 2)

# Bass: walking, slow, reluctant
bass = song.add_track(Track(name="bass", instrument="contrabass", volume=0.6, pan=0.15, swing=0.5))
bass.extend(
    [
        Note("D", 2, 2.0),
        Note.rest(1.0),
        Note("A", 1, 1.0),
        Note("G", 1, 1.5),
        Note("F#", 1, 0.5),
        Note.rest(2.0),
        Note("E", 2, 2.0),
        Note("D", 2, 1.0),
        Note.rest(1.0),
        Note("A", 1, 2.0),
        Note("D", 2, 2.0),
    ]
    * 2
)

# Trumpet: barely there, full of silence
tpt = song.add_track(Track(name="trumpet", instrument="trumpet", volume=0.65, pan=0.05, swing=0.5))
solo = humanize(
    [
        Note.rest(2.0),
        Note("A", 4, 0.75),
        Note("F", 4, 0.25),
        Note.rest(1.0),
        Note("D", 5, 2.0),
        Note.rest(2.0),
        Note("C", 5, 0.5),
        Note("A", 4, 0.5),
        Note("G", 4, 1.0),
        Note.rest(2.0),
        Note("F", 4, 1.0),
        Note.rest(1.5),
        Note("E", 4, 0.5),
        Note.rest(1.0),
        Note("A", 4, 4.0),
        Note.rest(2.0),
        Note("G", 4, 0.5),
        Note("A", 4, 0.25),
        Note("C", 5, 0.25),
        Note("D", 5, 1.5),
        Note.rest(0.5),
        Note("C", 5, 0.5),
        Note("A", 4, 0.5),
        Note("D", 4, 4.0),
    ],
    vel_spread=0.07,
    timing_spread=0.06,
)
tpt.extend(solo)

song._effects = {
    "trumpet": lambda s, sr: delay(
        reverb(s, sr, room_size=0.45, wet=0.18), sr, delay_ms=333.0, feedback=0.2, wet=0.1
    ),
    "piano": lambda s, sr: reverb(s, sr, room_size=0.5, wet=0.2),
    "bass": lambda s, sr: reverb(s, sr, room_size=0.4, wet=0.12),
}
