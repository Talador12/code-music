"""String chase: Vivaldi-speed string ostinato, E minor, 160 BPM.

Energizing. Strings running like something is at stake.
The kind of thing that plays in a film when the protagonist is
sprinting through a market. Forward. Always forward.
"""

from code_music import Note, Song, Track, compress, crescendo, humanize, reverb

song = Song(title="strings_chase", bpm=160)

# Cello drives the bass ostinato relentlessly
vc = song.add_track(Track(name="cello", instrument="cello", volume=0.75, pan=0.3))
ostinato = [
    Note("E", 3, 0.25),
    Note("B", 3, 0.25),
    Note("E", 3, 0.25),
    Note("B", 3, 0.25),
    Note("D", 3, 0.25),
    Note("A", 3, 0.25),
    Note("D", 3, 0.25),
    Note("A", 3, 0.25),
]
vc.extend(crescendo(ostinato * 12, start_vel=0.5, end_vel=0.92))

# Violin 1: running sixteenths in Em scale
vln1 = song.add_track(Track(name="vln1", instrument="violin", volume=0.7, pan=-0.4))
run = humanize(
    [
        Note("E", 5, 0.25),
        Note("F#", 5, 0.25),
        Note("G", 5, 0.25),
        Note("A", 5, 0.25),
        Note("B", 5, 0.25),
        Note("A", 5, 0.25),
        Note("G", 5, 0.25),
        Note("F#", 5, 0.25),
        Note("E", 5, 0.25),
        Note("D", 5, 0.25),
        Note("C", 5, 0.25),
        Note("B", 4, 0.25),
        Note("A", 4, 0.25),
        Note("B", 4, 0.25),
        Note("C", 5, 0.25),
        Note("D", 5, 0.25),
    ],
    vel_spread=0.05,
)
vln1.extend(crescendo(run * 6, start_vel=0.55, end_vel=0.95))

# Violin 2: harmonic support, offbeat
vln2 = song.add_track(Track(name="vln2", instrument="strings", volume=0.6, pan=-0.1))
counter = [
    Note("G", 4, 0.5),
    Note("B", 4, 0.5),
    Note("A", 4, 0.5),
    Note("F#", 4, 0.5),
    Note("G", 4, 0.5),
    Note("D", 4, 0.5),
    Note("E", 4, 1.0),
] * 3
vln2.extend(crescendo(counter, start_vel=0.45, end_vel=0.88))

song._effects = {
    "cello": lambda s, sr: compress(reverb(s, sr, room_size=0.6, wet=0.2), sr, ratio=3.0),
    "vln1": lambda s, sr: reverb(s, sr, room_size=0.65, wet=0.22),
    "vln2": lambda s, sr: reverb(s, sr, room_size=0.65, wet=0.22),
}
