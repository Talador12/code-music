"""Taiko drum impact: cinematic percussion hits with pitch variation."""

from code_music import Note, Song, Track, reverb

song = Song(title="taiko_impact", bpm=90)
taiko = song.add_track(Track(name="taiko", instrument="taiko", volume=0.95))
djembe = song.add_track(Track(name="djembe", instrument="djembe", volume=0.75, pan=-0.3))
tabla = song.add_track(Track(name="tabla", instrument="tabla", volume=0.7, pan=0.3))

# Taiko: big hits on downbeats
taiko.extend(
    [
        Note("C", 2, 1.0, velocity=1.0),
        Note.rest(0.5),
        Note("C", 2, 0.5, velocity=0.8),
        Note("G", 2, 1.0, velocity=0.9),
        Note.rest(1.0),
        Note("C", 2, 0.5, velocity=1.0),
        Note("C", 2, 0.25, velocity=0.85),
        Note.rest(0.25),
        Note("F", 2, 2.0, velocity=0.95),
    ]
    * 2
)

# Djembe: syncopated fills
djembe.extend(
    [
        Note("G", 3, 0.5),
        Note("G", 3, 0.25),
        Note.rest(0.25),
        Note("G", 3, 0.5),
        Note.rest(0.5),
        Note("G", 3, 0.25),
        Note("G", 3, 0.25),
        Note("G", 3, 0.25),
        Note("G", 3, 0.25),
        Note("G", 3, 1.0),
        Note.rest(1.0),
    ]
    * 2
)

# Tabla: fast flourishes
tabla.extend(
    [Note("A", 4, 0.25)] * 4 + [Note.rest(4.0)] + [Note("A", 4, 0.25)] * 8 + [Note.rest(4.0)]
)

song._effects = {
    "taiko": lambda s, sr: reverb(s, sr, room_size=0.85, wet=0.35),
}
