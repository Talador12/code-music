"""Orchestra hit: full tutti crash, Cm, fortissimo. The wall of sound.

Powerful. Every instrument at once. The kind of hit that makes you
flinch. Then the silence after is its own thing.
"""

from code_music import Chord, Note, Song, Track, reverb

song = Song(title="orchestra_hit", bpm=80)

PITCH = "C"
r = Note.rest

# Strings — all sections, massive
for inst, pan_v, oct in [
    ("violin", -0.5, 5),
    ("strings", -0.2, 4),
    ("cello", 0.3, 3),
    ("contrabass", 0.5, 2),
]:
    tr = song.add_track(Track(name=inst, instrument=inst, volume=0.8, pan=pan_v))
    tr.add(Chord(PITCH, "min", oct, duration=0.5, velocity=0.8))
    tr.add(Note(PITCH, oct, 6.0, velocity=1.0))
    tr.add(r(2.0))

# Brass — all hitting together
for inst, pan_v, oct in [
    ("trumpet", -0.3, 4),
    ("trombone", 0.3, 3),
    ("french_horn", 0.0, 3),
    ("tuba", 0.45, 2),
]:
    tr = song.add_track(Track(name=inst, instrument=inst, volume=0.88, pan=pan_v))
    tr.add(Note(PITCH, oct, 0.5, velocity=1.0))
    tr.add(Note(PITCH, oct, 5.5, velocity=0.95))
    tr.add(r(2.5))

# Timpani crash
timp = song.add_track(Track(name="timp", instrument="timpani", volume=1.0))
timp.extend([Note("C", 2, 0.25, velocity=1.0)] * 2 + [Note("C", 2, 6.0, velocity=0.9), r(2.0)])

# Cymbal
cymb = song.add_track(Track(name="cymb", instrument="cymbals", volume=0.85))
cymb.add(Note("C", 5, 0.5, velocity=1.0))
cymb.add(Note("C", 5, 8.0, velocity=0.5))

# Taiko
taiko = song.add_track(Track(name="taiko", instrument="taiko", volume=1.0))
taiko.add(Note("C", 2, 0.5, velocity=1.0))
taiko.add(Note("C", 2, 8.0, velocity=0.2))

song.effects = {
    k: lambda s, sr: reverb(s, sr, room_size=0.95, damping=0.2, wet=0.4)
    for k in (
        "violin",
        "strings",
        "cello",
        "contrabass",
        "trumpet",
        "trombone",
        "french_horn",
        "tuba",
        "timp",
    )
}
