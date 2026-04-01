"""Rhodes blue: Herbie Hancock / Kind of Blue feel. Fm7, 84 BPM, cool.

Alluring. Rhodes has this electric glow that no acoustic piano has.
A note struck on a Rhodes sustains and shimmers. This is sparse,
cool jazz in a minor key. The silence is as important as the notes.
"""

from code_music import Chord, Note, Song, Track, chorus, delay, humanize, reverb

song = Song(title="rhodes_blue", bpm=84)

rh = song.add_track(Track(name="rhodes", instrument="rhodes", volume=0.72, pan=0.0, swing=0.5))

# Sparse comping: long gaps, unexpected voicings
comp = [
    Chord("F", "min7", 3, duration=3.0, velocity=0.55),
    Note.rest(1.0),
    Chord("D#", "maj7", 3, duration=2.0, velocity=0.5),
    Chord("G", "dom7", 3, duration=2.0, velocity=0.52),
    Note.rest(2.0),
    Chord("C", "min7", 3, duration=2.5, velocity=0.54),
    Note.rest(1.5),
    Chord("F", "min", 3, duration=4.0, velocity=0.5),
]
rh.extend(comp)

# Single melodic notes floating on top
mel = song.add_track(Track(name="mel", instrument="rhodes", volume=0.65, pan=0.05, swing=0.5))
melody = humanize(
    [
        Note.rest(1.5),
        Note("F", 5, 0.5),
        Note.rest(0.5),
        Note("G#", 5, 1.5),
        Note.rest(1.5),
        Note("D#", 5, 0.5),
        Note("F", 5, 0.5),
        Note.rest(1.0),
        Note("C", 5, 2.0),
        Note.rest(1.0),
        Note("D#", 5, 0.5),
        Note.rest(0.5),
        Note("F", 5, 0.5),
        Note("G#", 5, 0.5),
        Note("A#", 5, 4.0),
    ],
    vel_spread=0.08,
    timing_spread=0.06,
)
mel.extend(melody)

song.effects = {
    "rhodes": lambda s, sr: chorus(
        reverb(s, sr, room_size=0.45, wet=0.15), sr, rate_hz=0.5, wet=0.18
    ),
    "mel": lambda s, sr: delay(
        reverb(s, sr, room_size=0.5, wet=0.18), sr, delay_ms=357.0, feedback=0.28, wet=0.15
    ),
}
