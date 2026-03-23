"""Harp and strings: Debussy-flavored, Db major, 66 BPM. Water. Reflection.

Alluring. Debussy avoided resolution — he preferred to let chords float.
Harp runs that blur into string harmonics. The kind of music that makes
you feel underwater, in the best way.
"""

from code_music import Chord, Note, Song, Track, arp, chorus, humanize, reverb, stereo_width

song = Song(title="harp_strings_impressionist", bpm=66)

# Harp: shimmering whole-tone runs
harp = song.add_track(Track(name="harp", instrument="harp", volume=0.65, pan=-0.1))
# Whole tone scale from Db: Db Eb F G A B
whole_tone = [
    Note("C#", 5, 0.25),
    Note("D#", 5, 0.25),
    Note("F", 5, 0.25),
    Note("G", 5, 0.25),
    Note("A", 5, 0.25),
    Note("B", 5, 0.25),
    Note("C#", 6, 0.25),
    Note("D#", 6, 0.25),
]
harp.extend(humanize(whole_tone * 4 + list(reversed(whole_tone)) * 2, vel_spread=0.07))
# Then slow rolled chords
for ch, sh in [("C#", "maj7"), ("G#", "maj7"), ("F", "maj7"), ("C#", "sus2")]:
    harp.extend(arp(Chord(ch, sh, 4, velocity=0.5), pattern="up", rate=0.5))

# Strings: sustained, barely there
for inst, pan_v, vel in [("violin", -0.4, 0.4), ("strings", 0.2, 0.38), ("cello", 0.45, 0.42)]:
    tr = song.add_track(Track(name=inst, instrument=inst, volume=0.55, pan=pan_v))
    tr.extend(
        [
            Chord("C#", "maj7", 3, duration=8.0, velocity=vel),
            Chord("G#", "maj7", 3, duration=8.0, velocity=vel),
            Chord("F", "maj7", 3, duration=8.0, velocity=vel),
        ]
    )

song._effects = {
    "harp": lambda s, sr: chorus(
        reverb(s, sr, room_size=0.78, wet=0.35), sr, rate_hz=0.3, wet=0.15
    ),
    "violin": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.85, wet=0.4), width=1.6),
    "strings": lambda s, sr: reverb(s, sr, room_size=0.85, wet=0.38),
    "cello": lambda s, sr: reverb(s, sr, room_size=0.85, wet=0.38),
}
