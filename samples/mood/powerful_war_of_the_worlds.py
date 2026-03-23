"""War of the worlds: low brass + taiko + tremolo strings, Am, 92 BPM.

Powerful. Something arriving. Something vast and indifferent.
The feeling of scale — that whatever is happening is larger than you.
Low, slow, inevitable.
"""

from code_music import Note, Song, Track, crescendo, lowpass, reverb

song = Song(title="war_of_the_worlds", bpm=92)

r = Note.rest

# Sub drone: pure sine, barely there, just felt
sub = song.add_track(Track(name="sub", instrument="sub_bass", volume=0.65, pan=0.0))
sub.extend([Note("A", 1, 4.0, velocity=0.7)] * 8)

# Tuba/trombone pedal: low brass breathing
for inst, oct, pan_v, vol in [("tuba", 2, 0.3, 0.82), ("trombone", 3, -0.3, 0.78)]:
    tr = song.add_track(Track(name=inst, instrument=inst, volume=vol, pan=pan_v))
    tr.extend(
        crescendo(
            [
                Note("A", oct, 6.0),
                r(2.0),
                Note("G", oct, 4.0),
                Note("A", oct, 4.0),
                Note("A", oct, 8.0),
            ],
            start_vel=0.2,
            end_vel=0.95,
        )
    )

# Taiko: the footsteps of something enormous
taiko = song.add_track(Track(name="taiko", instrument="taiko", volume=1.0))
steps = crescendo(
    [
        Note("A", 2, 2.0),
        r(2.0),
        Note("A", 2, 2.0),
        r(1.0),
        Note("A", 2, 1.0),
        r(4.0),
        Note("A", 2, 1.0),
        Note("A", 2, 1.0),
        r(2.0),
        Note("A", 2, 2.0),
        r(2.0),
        Note("A", 2, 4.0),
    ],
    start_vel=0.3,
    end_vel=1.0,
)
taiko.extend(steps)

# Tremolo strings: the fear
vln = song.add_track(Track(name="vln", instrument="violin", volume=0.6, pan=-0.3))
tremolo_notes = crescendo(
    [Note("A", 4, 0.125)] * 128,  # 16 bars of 16th note tremolo
    start_vel=0.1,
    end_vel=0.85,
)
vln.extend(tremolo_notes)

# French horn: distant call
horn = song.add_track(Track(name="horn", instrument="french_horn", volume=0.7, pan=0.1))
horn.extend([r(8.0)])
horn.extend(
    crescendo(
        [
            Note("E", 4, 3.0),
            r(1.0),
            Note("A", 3, 4.0),
            Note("C", 4, 2.0),
            Note("D", 4, 2.0),
            Note("E", 4, 8.0),
        ],
        start_vel=0.3,
        end_vel=0.9,
    )
)

song._effects = {
    "sub": lambda s, sr: lowpass(s, sr, cutoff_hz=80.0),
    "tuba": lambda s, sr: reverb(s, sr, room_size=0.92, wet=0.4),
    "trombone": lambda s, sr: reverb(s, sr, room_size=0.92, wet=0.4),
    "taiko": lambda s, sr: reverb(s, sr, room_size=0.9, damping=0.2, wet=0.35),
    "vln": lambda s, sr: reverb(s, sr, room_size=0.88, wet=0.32),
    "horn": lambda s, sr: reverb(s, sr, room_size=0.9, wet=0.38),
}
