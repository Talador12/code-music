"""Mute Solo Mix - Session with mute/solo mix controls."""

from code_music import Chord, Clip, Note, Session, Track, scale

session = Session(bpm=100, sample_rate=44100)

# Add tracks
session.add_track("drums", instrument="drums_kick", volume=0.8)
session.add_track("bass", instrument="bass", volume=0.6)
session.add_track("keys", instrument="piano", volume=0.5)
session.add_track("lead", instrument="sawtooth", volume=0.45)

# Build clips
kick_pat = Track()
for _ in range(4):
    kick_pat.add(Note("C", 4, 1.0, velocity=80))
    kick_pat.add(Note.rest(1.0))

bass_pat = Track()
for root in ["E", "A", "D", "B"]:
    bass_pat.add(Note(root, 2, 2.0, velocity=65))

keys_pat = Track()
for root, shape in [("E", "min7"), ("A", "min7"), ("D", "maj7"), ("B", "min7")]:
    keys_pat.add(Chord(root, shape, 4, duration=2.0, velocity=50))

lead_pat = Track()
lead_pat.extend(scale("E", "pentatonic_minor", octave=5, length=8))

# Fill scene 0 with all clips
for name, pat in [("drums", kick_pat), ("bass", bass_pat), ("keys", keys_pat), ("lead", lead_pat)]:
    session.set_clip(name, 0, Clip.from_track(pat))

# Scene 1: same but solo the bass for a breakdown
for name, pat in [("drums", kick_pat), ("bass", bass_pat), ("keys", keys_pat), ("lead", lead_pat)]:
    session.set_clip(name, 1, Clip.from_track(pat))

# Pan the mix
session.set_pan("keys", -0.3)
session.set_pan("lead", 0.3)

# Render: full mix -> solo bass -> full mix
# For the solo section, we use a separate render
full_mix = session.render(scene_order=[0, 0, 0, 0], loops_per_scene=1)
session.solo("bass")
solo_section = session.render(scene_order=[1, 1], loops_per_scene=1)
session.unsolo("bass")
final = session.render(scene_order=[0, 0], loops_per_scene=1)

# Combine using song_append
from code_music.automation import song_append

song = song_append(song_append(full_mix, solo_section), final)
