"""Bass drop: supersaw wall + 808 + kick + choir stab. Pure impact.

Powerful. The moment everything hits at once. The sub frequencies
you feel in your chest before you hear them. No subtlety here.
"""

from code_music import Chord, Note, Song, Track, reverb, stereo_width

song = Song(title="bass_drop", bpm=128)

r = Note.rest

# Four-bar build-up then the drop
# Kick
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=1.0))
kick.extend([Note("C", 2, 1.0)] * 16)

# 808 sub — the physical weight
sub = song.add_track(Track(name="sub", instrument="drums_808", volume=0.95))
for p, o, dur in [("A", 1, 2), ("F", 1, 2), ("C", 1, 2), ("G", 1, 2)] * 2:
    sub.add(Note(p, o, float(dur), velocity=0.9))

# Supersaw chord wall
pad = song.add_track(Track(name="pad", instrument="supersaw", volume=0.6, pan=0.0))
for ch, sh in [("A", "min7"), ("F", "maj7"), ("C", "maj"), ("G", "dom7")] * 2:
    pad.add(Chord(ch, sh, 3, duration=2.0, velocity=0.8))

# Choir stab on beat 1 of each bar — the impact
choir = song.add_track(Track(name="choir", instrument="choir_aah", volume=0.65, pan=0.0))
for _ in range(4):
    choir.add(Chord("A", "min", 3, duration=0.5, velocity=1.0))
    choir.add(Note.rest(3.5))

# Crash on bar 1
crash = song.add_track(Track(name="crash", instrument="drums_crash", volume=0.9))
crash.add(Note("C", 5, 8.0, velocity=1.0))
crash.add(Note.rest(8.0))

# Clap on 2 & 4
clap = song.add_track(Track(name="clap", instrument="drums_clap", volume=0.8))
clap.extend([r(1.0), Note("D", 3, 1.0), r(1.0), Note("D", 3, 1.0)] * 4)

song.effects = {
    "pad": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.4, wet=0.15), width=1.8),
    "choir": lambda s, sr: reverb(s, sr, room_size=0.6, wet=0.25),
}
