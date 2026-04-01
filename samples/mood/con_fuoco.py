"""Brass charge: trumpet + trombone + horn, Bb major, 140 BPM. Sport, battle, glory.

Energizing. The kind of thing that plays when the hero arrives.
Short stabs that punch you forward. No restraint.
"""

from code_music import Note, Song, Track, crescendo, reverb

song = Song(title="brass_charge", bpm=140)

for inst, oct, pan_v, vol in [
    ("trumpet", 4, -0.35, 0.88),
    ("trombone", 3, 0.35, 0.82),
    ("french_horn", 3, 0.0, 0.78),
    ("brass_section", 4, -0.1, 0.7),
]:
    tr = song.add_track(Track(name=inst, instrument=inst, volume=vol, pan=pan_v))
    charge = crescendo(
        [
            Note("A#", oct, 0.5),
            Note("D", oct + 1 if inst == "trumpet" else oct, 0.5),
            Note("F", oct, 0.5),
            Note("A#", oct, 1.0),
            Note.rest(0.5),
            Note("C", oct, 0.25),
            Note("D", oct, 0.25),
            Note("F", oct, 0.5),
            Note("A#", oct, 0.5),
            Note("D", oct + 1 if inst == "trumpet" else oct, 2.0),
            Note.rest(0.5),
            Note("A#", oct, 0.25),
            Note("C", oct, 0.25),
            Note("D", oct, 0.5),
            Note("F", oct, 0.5),
            Note("A#", oct, 0.5),
            Note("D", oct + 1 if inst == "trumpet" else oct, 4.0),
        ],
        start_vel=0.65,
        end_vel=1.0,
    )
    tr.extend(charge)

song.effects = {
    k: lambda s, sr: reverb(s, sr, room_size=0.75, wet=0.22)
    for k in ("trumpet", "trombone", "french_horn", "brass_section")
}
