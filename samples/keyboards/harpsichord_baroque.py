"""Harpsichord baroque: Bach-style invention, D minor, 120 BPM. Precise and alive.

Energizing. Harpsichord has no dynamics — every note is the same volume.
The energy comes entirely from rhythm and voice leading. Pure forward motion.
The baroque counterpoint style where two voices chase each other.
"""

from code_music import Note, Song, Track, humanize, reverb

song = Song(title="harpsichord_baroque", bpm=120)

hpd_r = song.add_track(Track(name="right", instrument="harpsichord", volume=0.78, pan=-0.15))
hpd_l = song.add_track(Track(name="left", instrument="harpsichord", volume=0.72, pan=0.15))

# Right hand: subject
subject = [
    Note("D", 5, 0.25),
    Note("E", 5, 0.25),
    Note("F", 5, 0.25),
    Note("G", 5, 0.25),
    Note("A", 5, 0.5),
    Note("G", 5, 0.25),
    Note("F", 5, 0.25),
    Note("E", 5, 0.25),
    Note("D", 5, 0.25),
    Note("C#", 5, 0.25),
    Note("D", 5, 0.25),
    Note("A", 4, 1.0),
]
answer = [Note(n.pitch, n.octave - 1, n.duration) for n in subject]

hpd_r.extend(humanize(subject * 2 + answer, vel_spread=0.04, timing_spread=0.015))

# Left hand: answer a fifth below, offset by one bar
left_subject = [Note(n.pitch, n.octave - 1, n.duration) for n in subject]
hpd_l.extend(
    humanize(
        [Note.rest(2.0)] + left_subject + subject + left_subject,
        vel_spread=0.04,
        timing_spread=0.015,
    )
)

song._effects = {
    "right": lambda s, sr: reverb(s, sr, room_size=0.45, wet=0.12),
    "left": lambda s, sr: reverb(s, sr, room_size=0.45, wet=0.12),
}
