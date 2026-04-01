"""Vibraphone meditation: Am pentatonic, 55 BPM, motor on (slow vibrato).

Chill. The vibraphone's metal bars sustain beautifully, and its
built-in tremolo motor creates gentle pulsing. Pentatonic means
every note sounds good with every other note — pure texture.
"""

from code_music import Note, Song, Track, chorus, humanize, reverb, tremolo

song = Song(title="vibraphone_meditation", bpm=55)

vib = song.add_track(Track(name="vibes", instrument="vibraphone", volume=0.75, pan=0.0))

# Pentatonic: A C D E G — no wrong notes
pent = humanize(
    [
        Note("A", 4, 2.0),
        Note.rest(0.5),
        Note("C", 5, 1.5),
        Note("E", 5, 3.0),
        Note.rest(1.0),
        Note("D", 5, 1.5),
        Note("A", 4, 0.5),
        Note.rest(1.0),
        Note("G", 4, 2.0),
        Note.rest(1.0),
        Note("C", 5, 1.0),
        Note("E", 5, 1.0),
        Note("A", 5, 4.0),
        Note.rest(2.0),
        Note("G", 5, 1.5),
        Note("E", 5, 0.5),
        Note.rest(1.0),
        Note("D", 5, 2.0),
        Note("A", 4, 2.0),
        Note("E", 4, 6.0),
    ],
    vel_spread=0.06,
    timing_spread=0.05,
)
vib.extend(pent)

song.effects = {
    "vibes": lambda s, sr: tremolo(
        chorus(reverb(s, sr, room_size=0.72, wet=0.38), sr, rate_hz=0.35, wet=0.22),
        sr,
        rate_hz=4.2,
        depth=0.18,
    ),
}
