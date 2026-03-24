"""hollow_ground.py — Dark ambient / industrial. Bm, 72 BPM.

Not all music wants to make you feel good. Some music wants to make
you feel the weight of a large, indifferent structure. Slow, low,
processed. Tremolo strings, industrial percussion, a sub drone that
starts below hearing. The kind of thing that plays over surveillance
footage in documentaries.
"""

from code_music import (
    EIGHTH,
    HALF,
    QUARTER,
    Chord,
    Note,
    Song,
    Track,
    bitcrush,
    conv_reverb,
    crescendo,
    decrescendo,
    highpass,
    humanize,
    lowpass,
    reverb,
    stereo_width,
    tape_sat,
    tremolo,
)

song = Song(title="Hollow Ground", bpm=72)

BAR = 4.0
r = Note.rest

# ── Sub drone — B and F# ──────────────────────────────────────────────────
for pitch, oct, vol, pan_v in [("B", 1, 0.58, 0.0), ("F#", 1, 0.35, 0.05)]:
    d = song.add_track(Track(name=f"sub_{pitch}", instrument="sub_bass", volume=vol, pan=pan_v))
    for _ in range(24):
        d.add(Note(pitch, oct, BAR, velocity=0.6))

# ── Tremolo strings — unsettling ──────────────────────────────────────────
vln = song.add_track(Track(name="strings", instrument="strings", volume=0.45, pan=-0.2))
vln.extend([r(BAR)] * 4)
vln.extend(
    crescendo(
        humanize([Note("B", 4, 0.125)] * (20 * 16), vel_spread=0.08),
        start_vel=0.08,
        end_vel=0.6,
    )
)
vln.extend(
    decrescendo(
        humanize([Note("B", 4, 0.125)] * (4 * 16), vel_spread=0.1),
        start_vel=0.6,
        end_vel=0.05,
    )
)

# ── Industrial hit ────────────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.88))
kick.extend([r(BAR)] * 8)
hit_pat = crescendo(
    [
        Note("B", 2, HALF, velocity=0.5),
        r(HALF),
        r(BAR),
        r(BAR),
        Note("B", 2, QUARTER, velocity=0.65),
        r(BAR - QUARTER),
        r(BAR * 2),
        Note("B", 2, HALF, velocity=0.8),
        r(HALF),
        r(BAR),
        Note("B", 2, EIGHTH, velocity=0.9),
        r(EIGHTH),
        Note("B", 2, EIGHTH, velocity=0.85),
        r(BAR - QUARTER),
        r(BAR * 3),
    ],
    0.3,
    0.95,
)
kick.extend(hit_pat)
kick.extend(decrescendo([Note("B", 2, BAR, velocity=0.85)] * 4, 0.9, 0.2))

# ── Eerie chord pad ───────────────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.30, pan=0.2))
pad.extend([r(BAR)] * 8)
pad.extend(
    crescendo(
        [
            Chord("B", "min7", 3, duration=BAR * 4, velocity=0.3),
            Chord("G", "maj7", 3, duration=BAR * 4, velocity=0.28),
            Chord("D", "maj", 3, duration=BAR * 4, velocity=0.32),
            Chord("A", "dom7", 3, duration=BAR * 4, velocity=0.3),
            Chord("B", "min", 3, duration=BAR * 4, velocity=0.35),
        ],
        0.1,
        0.55,
    )
)

# ── Processed noise texture ───────────────────────────────────────────────
noise = song.add_track(Track(name="noise", instrument="noise_sweep", volume=0.18))
noise.extend([r(BAR)] * 12)
noise.extend(
    crescendo(
        [Note("B", 3, BAR, velocity=0.3)] * 12,
        start_vel=0.1,
        end_vel=0.45,
    )
)

song._effects = {
    "sub_B": lambda s, sr: lowpass(s, sr, cutoff_hz=80.0),
    "sub_F#": lambda s, sr: lowpass(s, sr, cutoff_hz=100.0),
    "strings": lambda s, sr: tremolo(
        conv_reverb(s, sr, room="cave", wet=0.5),
        sr,
        rate_hz=6.0,
        depth=0.4,
    ),
    "pad": lambda s, sr: stereo_width(
        tape_sat(conv_reverb(s, sr, room="cave", wet=0.45), sr, drive=2.0, warmth=0.3, wet=0.4),
        width=1.9,
    ),
    "kick": lambda s, sr: bitcrush(
        conv_reverb(s, sr, room="cave", wet=0.5),
        sr,
        bit_depth=8,
        downsample=2,
        wet=0.45,
    ),
    "noise": lambda s, sr: highpass(reverb(s, sr, room_size=0.8, wet=0.4), sr, cutoff_hz=2000.0),
}
