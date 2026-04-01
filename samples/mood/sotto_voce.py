"""Diminished whisper: vibraphone + bass clarinet, B diminished, 60 BPM.

Alluring. Diminished chords are unstable by nature — every note
wants to move somewhere else. The vibraphone's natural sustain
makes each note shimmer and pull. You hold your breath.
"""

from code_music import Note, Song, Track, chorus, delay, humanize, reverb

song = Song(title="diminished_whisper", bpm=60)

# Vibraphone: sparse, each note ringing into the next
vib = song.add_track(Track(name="vibes", instrument="vibraphone", volume=0.72, pan=-0.2))
fragments = humanize(
    [
        Note("B", 5, 1.5),
        Note.rest(0.5),
        Note("D", 6, 1.0),
        Note("F", 6, 2.0),
        Note.rest(1.0),
        Note("G#", 5, 1.5),
        Note("B", 5, 0.5),
        Note.rest(1.0),
        Note("D", 6, 3.0),
        Note.rest(1.0),
        Note("F", 5, 1.0),
        Note("G#", 5, 0.5),
        Note.rest(0.5),
        Note("B", 5, 2.0),
        Note.rest(2.0),
        Note("D", 5, 4.0),
    ],
    vel_spread=0.07,
    timing_spread=0.04,
)
vib.extend(fragments)

# Bass clarinet: deep, dark, searching in the low register
bcl = song.add_track(Track(name="bcl", instrument="clarinet", volume=0.6, pan=0.2))
bass_line = humanize(
    [
        Note.rest(2.0),
        Note("B", 3, 3.0),
        Note.rest(1.0),
        Note("F", 3, 2.0),
        Note("G#", 3, 1.0),
        Note.rest(1.0),
        Note("D", 3, 4.0),
        Note.rest(2.0),
        Note("G#", 2, 2.0),
        Note("B", 2, 2.0),
        Note("F", 2, 6.0),
    ],
    vel_spread=0.05,
    timing_spread=0.03,
)
bcl.extend(bass_line)

song.effects = {
    "vibes": lambda s, sr: chorus(
        reverb(s, sr, room_size=0.75, wet=0.4), sr, rate_hz=0.35, depth_ms=3.0, wet=0.25
    ),
    "bcl": lambda s, sr: delay(
        reverb(s, sr, room_size=0.6, wet=0.25), sr, delay_ms=500.0, feedback=0.3, wet=0.15
    ),
}
