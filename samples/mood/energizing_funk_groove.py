"""Funk groove: slap bass + electric piano + clap, Em, 108 BPM, heavy swing.

Energizing. Can't sit still. The bass locks into the kick and you are
no longer in control of your head. James Brown-level insistence.
"""

from code_music import Chord, Note, Song, Track, chorus, compress, reverb

song = Song(title="funk_groove", bpm=108)

# Bass: the whole show — moog for that fat bottom
bass = song.add_track(Track(name="bass", instrument="moog_bass", volume=0.88, pan=0.0, swing=0.52))
groove = [
    Note("E", 2, 0.25),
    Note("E", 2, 0.25),
    Note.rest(0.25),
    Note("G", 2, 0.25),
    Note("E", 2, 0.25),
    Note.rest(0.25),
    Note("A", 2, 0.25),
    Note("E", 2, 0.25),
    Note("G", 2, 0.5),
    Note.rest(0.25),
    Note("E", 2, 0.25),
    Note("E", 2, 0.5),
    Note("D", 2, 0.25),
    Note("E", 2, 0.25),
]
bass.extend(groove * 4)

# Rhodes comp: tight, percussive, on the 2-and-4 of each bar
comp = song.add_track(Track(name="comp", instrument="rhodes", volume=0.62, pan=-0.2, swing=0.52))
stabs = [
    Note.rest(1.0),
    Chord("E", "min7", 3, duration=0.25, velocity=0.8),
    Note.rest(0.75),
    Note.rest(0.5),
    Chord("E", "min7", 3, duration=0.25, velocity=0.75),
    Note.rest(0.25),
    Chord("D", "dom7", 3, duration=0.25, velocity=0.7),
    Note.rest(0.75),
    Note.rest(1.0),
]
comp.extend(stabs * 4)

# Kick on 1 and 3, tight
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.95))
kick.extend([Note("C", 2, 1.0), Note.rest(1.0), Note("C", 2, 1.0), Note.rest(1.0)] * 4)

# Clap: snaps on 2 and 4
clap = song.add_track(Track(name="clap", instrument="drums_clap", volume=0.8, swing=0.52))
clap.extend([Note.rest(1.0), Note("D", 3, 1.0), Note.rest(1.0), Note("D", 3, 1.0)] * 4)

# Hat: 16th note push
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.38, swing=0.52))
hat.extend([Note("F", 5, 0.25)] * 64)

song._effects = {
    "bass": lambda s, sr: compress(s, sr, threshold=0.45, ratio=5.0, makeup_gain=1.2),
    "comp": lambda s, sr: chorus(reverb(s, sr, room_size=0.3, wet=0.12), sr, rate_hz=0.6, wet=0.12),
}
