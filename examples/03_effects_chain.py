"""03 — EffectsChain: add reverb, delay, compression, and more.

Run:  code-music examples/03_effects_chain.py --play
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    Track,
    compress,
    delay,
    reverb,
    stereo_width,
)

song = Song(title="Effects Demo", bpm=110)

# Build tracks
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.4))
for _ in range(4):
    pad.add(Chord("D", "min7", 3, duration=4.0))

lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.5))
lead.extend(
    [
        Note("D", 5, 0.5),
        Note("F", 5, 0.5),
        Note("A", 5, 0.5),
        Note("G", 5, 0.5),
        Note("F", 5, 1.0),
        Note("D", 5, 1.0),
    ]
    * 4
)

# EffectsChain: ordered, per-step wet/dry, bypass toggle
# Each .add() appends an effect with its parameters
song.effects = {
    "pad": (
        EffectsChain()
        .add(reverb, room_size=0.7, wet=0.35)  # big reverb
        .add(stereo_width, width=1.6)  # wide stereo
    ),
    "lead": (
        EffectsChain()
        .add(delay, delay_ms=250, feedback=0.3, wet=0.2)  # quarter-note echo
        .add(reverb, room_size=0.4, wet=0.15)  # touch of room
        .add(compress, threshold=0.5, ratio=3.0)  # tame peaks
    ),
}

# You can also toggle effects at runtime:
# song.effects["lead"].set_bypass(0, True)   # mute the delay
# song.effects["lead"].set_wet(1, 0.5)       # pull reverb to 50%
