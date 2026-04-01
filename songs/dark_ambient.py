"""dark_ambient.py — Dark ambient. Bbm, 60 BPM. Lustmord-style depth.

Ultra-slow, oppressive atmosphere with subsonic drones, reversed-sounding
pads, and sparse metallic accents. Uses Track.stretch + fade for glacial pacing.

Style: Dark ambient, Bbm, 60 BPM.
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    Track,
    distortion,
    lowpass,
    reverb,
    stereo_width,
)

song = Song(title="Dark Ambient", bpm=60)
r = Note.rest

drone = Track(name="drone", instrument="sine", volume=0.4)
for _ in range(8):
    drone.add(Note("Bb", 1, 8.0))
song.add_track(drone.fade_in(beats=16.0).fade_out(beats=16.0))

pad = Track(name="pad", instrument="pad", volume=0.25)
for _ in range(8):
    pad.extend([Chord("Bb", "min", 2, duration=8.0)])
song.add_track(pad.stretch(1.5).fade_in(beats=24.0).fade_out(beats=24.0))

accent = Track(name="accent", instrument="pluck", volume=0.2, pan=0.3)
accent.extend([r(16.0), Note("Db", 6, 0.5), r(15.5), Note("F", 6, 0.5), r(15.5),
               Note("Ab", 5, 0.5), r(15.5)])
song.add_track(accent)

sub = song.add_track(Track(name="sub", instrument="sine", volume=0.5))
for _ in range(16):
    sub.add(Note("Bb", 1, 4.0))

song.effects = {
    "drone": EffectsChain().add(distortion, drive=1.5, tone=0.2, wet=0.3).add(reverb, room_size=0.9, wet=0.5),
    "pad": EffectsChain().add(reverb, room_size=0.95, wet=0.6).add(stereo_width, width=2.0),
    "accent": EffectsChain().add(reverb, room_size=0.85, wet=0.5),
    "sub": EffectsChain().add(lowpass, cutoff_hz=80),
}
