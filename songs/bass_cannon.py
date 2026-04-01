"""bass_cannon.py — Dubstep. Fm, 142 BPM. Fourth Half Step album track.

Heavier wobble, longer drop section, more aggressive than heavy_wobble.
"""

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    compress,
    lowpass,
    reverb,
    stereo_width,
)

song = Song(title="Bass Cannon", bpm=142)
BAR = 4.0
r = Note.rest

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=1.0))
kick.extend([r(BAR)] * 4)
kick.extend([Note("C", 2, 1.0)] * (20 * 4))

snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.88))
snare.extend([r(BAR)] * 4)
snare.extend([r(2.0), Note("D", 3, 1.0), r(1.0)] * 20)

wobble = song.add_track(Track(name="wobble", instrument="wobble", volume=0.9))
wobble.extend([r(BAR)] * 4)
drop = [Note("F", 2, 0.5, velocity=0.95)] * 8
wobble.extend(drop * 10)

sub = song.add_track(Track(name="sub", instrument="sub_bass", volume=0.85))
sub.extend([r(BAR)] * 4)
sub.extend([Note("F", 1, BAR, velocity=0.75)] * 20)

pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3))
for _ in range(6):
    pad.extend([Chord("F", "min7", 3, duration=BAR, velocity=0.4)] * 4)

song.effects = {
    "sub": lambda s, sr: lowpass(s, sr, cutoff_hz=90.0),
    "pad": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.7, wet=0.3), width=1.8),
    "wobble": lambda s, sr: compress(s, sr, threshold=0.5, ratio=5.0, makeup_gain=1.2),
}
