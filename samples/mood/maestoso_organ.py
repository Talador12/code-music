"""Pipe organ: Bach-style chorale, Dm, full registration, 76 BPM.

Powerful. An organ at full volume in a large stone room.
The air itself moves. You feel small in the right way —
not diminished, but placed. Part of something larger.
"""

from code_music import Chord, Note, Song, Track, crescendo, reverb, stereo_width

song = Song(title="pipe_organ", bpm=76)

org = song.add_track(Track(name="organ", instrument="organ", volume=0.88, pan=0.0))

# Four-part chorale: soprano, alto, tenor, bass all in one instrument
# Bach-style voice leading: Dm - Gm - A7 - Dm - Bb - F - A7 - Dm
progression = crescendo(
    [
        Chord("D", "min", 3, duration=2.0),
        Chord("G", "min", 3, duration=2.0),
        Chord("A", "dom7", 3, duration=2.0),
        Chord("D", "min", 3, duration=2.0),
        Chord("A#", "maj", 3, duration=2.0),
        Chord("F", "maj", 3, duration=2.0),
        Chord("A", "dom7", 3, duration=2.0),
        Chord("D", "min", 3, duration=4.0),
    ],
    start_vel=0.6,
    end_vel=1.0,
)

org.extend(progression)

# Pedal: the deep bass octave doubling
pedal = song.add_track(Track(name="pedal", instrument="organ", volume=0.9, pan=0.0))
bass_tones = [
    Note("D", 2, 2.0),
    Note("G", 2, 2.0),
    Note("A", 1, 2.0),
    Note("D", 2, 2.0),
    Note("A#", 1, 2.0),
    Note("F", 2, 2.0),
    Note("A", 1, 2.0),
    Note("D", 2, 4.0),
]
pedal.extend(crescendo(bass_tones, 0.6, 1.0))

song.effects = {
    "organ": lambda s, sr: stereo_width(
        reverb(s, sr, room_size=0.98, damping=0.1, wet=0.55), width=1.5
    ),
    "pedal": lambda s, sr: reverb(s, sr, room_size=0.98, damping=0.1, wet=0.5),
}
