"""Articulation showcase: staccato, legato, pizzicato on the same phrase."""

from code_music import Note, Song, Track, legato, reverb, staccato

phrase = [
    Note("C", 4, 1.0),
    Note("D", 4, 1.0),
    Note("E", 4, 1.0),
    Note("F", 4, 1.0),
    Note("G", 4, 2.0),
    Note.rest(2.0),
]

song = Song(title="articulations", bpm=100)

# Legato (connected, smooth)
leg = song.add_track(Track(name="legato", instrument="violin", volume=0.7, pan=-0.5))
leg.extend(legato(phrase, overlap=0.1))

# Normal
normal = song.add_track(Track(name="normal", instrument="violin", volume=0.7, pan=0.0))
normal.extend(phrase)

# Staccato (detached)
stacc = song.add_track(Track(name="staccato", instrument="violin", volume=0.7, pan=0.5))
stacc.extend(staccato(phrase, factor=0.4))

song._effects = {
    k: lambda s, sr: reverb(s, sr, room_size=0.6, wet=0.2) for k in ("legato", "normal", "staccato")
}
