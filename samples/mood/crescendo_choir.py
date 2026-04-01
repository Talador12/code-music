"""Choir swell: SATB + organ, C minor → C major, fortissimo resolution.

Powerful. The major chord resolution after minor is one of the oldest
emotional tricks in music. Here it arrives like light through clouds.
That moment when the minor third lifts to major is the whole thing.
"""

from code_music import Chord, Note, Song, Track, crescendo, reverb, stereo_width

song = Song(title="choir_swell", bpm=70)

# Organ: long held chords underneath everything
organ = song.add_track(Track(name="organ", instrument="organ", volume=0.45, pan=0.0))
organ_chords = crescendo(
    [
        Chord("C", "min", 3, duration=4.0),
        Chord("G", "min", 3, duration=4.0),
        Chord("D#", "maj", 3, duration=4.0),
        Chord("G", "dom7", 3, duration=4.0),
        Chord("C", "maj", 3, duration=8.0),  # the resolution
    ],
    start_vel=0.3,
    end_vel=0.8,
)
organ.extend(organ_chords)

# Soprano: high, pure
sop = song.add_track(Track(name="sop", instrument="choir_ooh", volume=0.65, pan=-0.1))
sop.extend(
    crescendo(
        [
            Note("C", 5, 4.0),
            Note("D", 5, 2.0),
            Note("D#", 5, 2.0),
            Note("D", 5, 4.0),
            Note("D#", 5, 2.0),
            Note("G", 5, 2.0),
            Note("E", 5, 8.0),  # the major 3rd — this is the moment
        ],
        0.25,
        0.95,
    )
)

# Alto: warmth beneath soprano
alt = song.add_track(Track(name="alt", instrument="choir_aah", volume=0.62, pan=0.1))
alt.extend(
    crescendo(
        [
            Note("G", 4, 4.0),
            Note("A#", 4, 4.0),
            Note("A#", 4, 2.0),
            Note("D", 5, 2.0),
            Note("C", 5, 8.0),
        ],
        0.25,
        0.9,
    )
)

# Tenor: middle harmony
ten = song.add_track(Track(name="ten", instrument="choir_ooh", volume=0.6, pan=-0.15))
ten.extend(
    crescendo(
        [
            Note("D#", 4, 4.0),
            Note("G", 4, 4.0),
            Note("G", 4, 4.0),
            Note("G", 4, 8.0),
        ],
        0.2,
        0.88,
    )
)

# Bass: the foundation
bss = song.add_track(Track(name="bass_v", instrument="choir_aah", volume=0.65, pan=0.15))
bss.extend(
    crescendo(
        [
            Note("C", 3, 4.0),
            Note("G", 2, 4.0),
            Note("D#", 3, 4.0),
            Note("G", 2, 4.0),
            Note("C", 3, 8.0),
        ],
        0.3,
        0.92,
    )
)

song.effects = {
    k: lambda s, sr: stereo_width(reverb(s, sr, room_size=0.95, damping=0.3, wet=0.5), width=1.7)
    for k in ("sop", "alt", "ten", "bass_v", "organ")
}
