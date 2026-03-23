"""Taiko war drums: Japanese-inspired battle percussion, Dm, primal energy.

Powerful. Before language there was rhythm. This is the sound of
something ancient and unstoppable. Taiko + djembe + timpani.
"""

from code_music import Note, Song, Track, crescendo, humanize, reverb

song = Song(title="taiko_war", bpm=112)

r = Note.rest

# Primary taiko — the heartbeat
taiko = song.add_track(Track(name="taiko", instrument="taiko", volume=1.0))
beat = [
    Note("D", 2, 0.5, velocity=1.0),
    Note("D", 2, 0.5, velocity=0.7),
    Note("D", 2, 0.5, velocity=0.85),
    r(0.5),
    Note("D", 2, 0.5, velocity=1.0),
    Note("D", 2, 0.25, velocity=0.75),
    Note("D", 2, 0.25, velocity=0.9),
    Note("D", 2, 1.0, velocity=1.0),
    r(1.0),
]
taiko.extend(crescendo(beat * 4, start_vel=0.4, end_vel=1.0))

# Djembe — syncopated fills between the big hits
djembe = song.add_track(Track(name="djembe", instrument="djembe", volume=0.75, pan=-0.3))
fill = [
    r(1.0),
    Note("G", 4, 0.25),
    Note("G", 4, 0.25),
    r(0.5),
    Note("G", 4, 0.25),
    r(0.25),
    Note("G", 4, 0.5),
    r(0.25),
    Note("G", 4, 0.25),
    r(0.5),
    Note("G", 4, 0.5),
    r(1.0),
]
djembe.extend(humanize(fill * 4, vel_spread=0.12))

# Timpani — low thunder under everything
timp = song.add_track(Track(name="timp", instrument="timpani", volume=0.85, pan=0.3))
thunder = crescendo(
    [
        Note("D", 2, 2.0),
        Note("A", 1, 1.0),
        r(1.0),
        Note("D", 2, 1.5),
        Note("D", 2, 0.5),
        Note("A", 1, 2.0),
        Note("D", 2, 4.0),
    ],
    start_vel=0.3,
    end_vel=1.0,
)
timp.extend(thunder)
timp.extend(decrescendo := thunder[::-1])  # reverse echo

song._effects = {
    "taiko": lambda s, sr: reverb(s, sr, room_size=0.8, damping=0.3, wet=0.3),
    "timp": lambda s, sr: reverb(s, sr, room_size=0.85, wet=0.35),
}
