"""ambient_techno.py — Ambient techno. Fm, 118 BPM. Villalobos meets GAS.

Minimal four-on-the-floor with evolving filtered pads, deep sub pulses,
and barely-there percussive textures. Uses Track.stretch for the slow pad.

Style: Ambient techno, Fm, 118 BPM.
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    Track,
    lfo_filter,
    lowpass,
    reverb,
    stereo_width,
)

song = Song(title="Ambient Techno", bpm=118)
r = Note.rest

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.75))
for _ in range(32):
    kick.extend([Note("C", 2, 1.0)] * 4)

hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.2))
for _ in range(32):
    hat.extend([r(0.5), Note("F#", 6, 0.5)] * 4)

bass = song.add_track(Track(name="bass", instrument="sine", volume=0.55))
for _ in range(32):
    bass.extend([Note("F", 2, 2.0), r(1.0), Note("F", 2, 1.0)])

pad = Track(name="pad", instrument="pad", volume=0.25)
for _ in range(16):
    pad.extend([Chord("F", "min7", 3, duration=4.0), Chord("Db", "maj7", 3, duration=4.0)])
song.add_track(pad.stretch(1.1).fade_in(beats=32.0).fade_out(beats=32.0))

song.effects = {
    "pad": EffectsChain().add(lfo_filter, rate=0.06, depth=0.5).add(reverb, room_size=0.8, wet=0.45).add(stereo_width, width=1.7),
    "bass": EffectsChain().add(lowpass, cutoff_hz=150),
}
