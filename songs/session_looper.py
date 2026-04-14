"""Session Looper - Ableton-style session view with clip grid."""

from code_music import Chord, Clip, Note, Session, Track, scale

session = Session(bpm=120, sample_rate=44100)
session.add_track("kick", instrument="drums_kick", volume=0.8)
session.add_track("hat", instrument="drums_hat", volume=0.4)
session.add_track("bass", instrument="bass", volume=0.6)
session.add_track("pad", instrument="pad", volume=0.4)
session.add_track("lead", instrument="sawtooth", volume=0.5)

# Scene 0: intro (kick + hat only)
kick_intro = Track()
for _ in range(4):
    kick_intro.add(Note("C", 4, 1.0, velocity=80))
    kick_intro.add(Note.rest(1.0))
session.set_clip("kick", 0, Clip.from_track(kick_intro))

hat_pattern = Track()
hat_pattern.extend([Note("C", 6, 0.5, velocity=40)] * 16)
session.set_clip("hat", 0, Clip.from_track(hat_pattern))

# Scene 1: drop (everything)
kick_drop = Track()
for _ in range(4):
    kick_drop.add(Note("C", 4, 1.0, velocity=90))
    kick_drop.add(Note.rest(0.5))
    kick_drop.add(Note("C", 4, 0.5, velocity=60))
session.set_clip("kick", 1, Clip.from_track(kick_drop))
session.set_clip("hat", 1, Clip.from_track(hat_pattern))

bass_line = Track()
for root in ["A", "A", "D", "E"]:
    bass_line.add(Note(root, 2, 2.0, velocity=70))
session.set_clip("bass", 1, Clip.from_track(bass_line))

pad_chords = Track()
for root, shape in [("A", "min7"), ("D", "min7")]:
    pad_chords.add(Chord(root, shape, 3, duration=4.0, velocity=45))
session.set_clip("pad", 1, Clip.from_track(pad_chords))

mel = Track()
mel.extend(scale("A", "pentatonic_minor", octave=5, length=8))
session.set_clip("lead", 1, Clip.from_track(mel))

# Scene 2: breakdown (pad + lead only)
session.set_clip("pad", 2, Clip.from_track(pad_chords))
session.set_clip("lead", 2, Clip.from_track(mel))

# Render: intro x2 -> drop x4 -> breakdown x2 -> drop x2
song = session.render(scene_order=[0, 0, 1, 1, 1, 1, 2, 2, 1, 1], loops_per_scene=1)
