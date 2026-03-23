"""Piano nocturne: Chopin-inflected, F# minor, rubato, 60 BPM.

Alluring. Night music. The left hand rolls arpeggios underneath
while the right hand sings. Both hands doing different time simultaneously.
A conversation between the low and the high.
"""

from code_music import Chord, Note, Song, Track, arp, chorus, humanize, reverb

song = Song(title="piano_nocturne", bpm=60)

# Left hand: rolling arpeggios
lh = song.add_track(Track(name="lh", instrument="piano", volume=0.55, pan=-0.05))
for ch, sh in [
    ("F#", "min7"),
    ("C#", "dom7"),
    ("B", "maj7"),
    ("G#", "min"),
    ("F#", "min"),
    ("D", "maj7"),
    ("C#", "dom7"),
    ("F#", "min"),
]:
    lh.extend(arp(Chord(ch, sh, 3, velocity=0.5), pattern="up", rate=0.25, octaves=2))

# Right hand: the singing melody
rh = song.add_track(Track(name="rh", instrument="piano", volume=0.8, pan=0.05))
nocturne = humanize(
    [
        Note("F#", 5, 1.5),
        Note("G#", 5, 0.5),
        Note("A", 5, 1.0),
        Note("C#", 6, 2.0),
        Note.rest(1.0),
        Note("B", 5, 1.0),
        Note("A", 5, 0.5),
        Note("G#", 5, 0.5),
        Note("F#", 5, 3.0),
        Note.rest(1.0),
        Note("E", 5, 0.5),
        Note("F#", 5, 0.5),
        Note("G#", 5, 1.0),
        Note("A", 5, 0.5),
        Note("B", 5, 0.5),
        Note("C#", 6, 1.0),
        Note("D", 6, 0.5),
        Note("C#", 6, 0.5),
        Note("B", 5, 0.5),
        Note("A", 5, 0.5),
        Note("G#", 5, 4.0),
    ],
    vel_spread=0.08,
    timing_spread=0.07,
)
rh.extend(nocturne)

song._effects = {
    "lh": lambda s, sr: reverb(s, sr, room_size=0.6, wet=0.2),
    "rh": lambda s, sr: chorus(
        reverb(s, sr, room_size=0.65, wet=0.25), sr, rate_hz=0.25, depth_ms=1.5, wet=0.06
    ),
}
