"""tempo_drift.py — First song to actually use bpm_ramp rendering.

Starts at 140 BPM, ritardandos to 70 BPM over 8 bars. You can hear
the beats physically slow down. Uses Song.bpm_map wired to the synth.

Style: Progressive ambient, Dm, 140→70 BPM.
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    Track,
    bpm_ramp,
    reverb,
    stereo_width,
)

song = Song(title="Tempo Drift", bpm=140)

r = Note.rest

# 8 bars of material
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.35))
for _ in range(8):
    pad.add(Chord("D", "min7", 3, duration=4.0))

lead = song.add_track(Track(name="lead", instrument="piano", volume=0.5))
melody = [
    Note("D", 5, 0.5),
    Note("F", 5, 0.5),
    Note("A", 5, 0.5),
    Note("G", 5, 0.5),
    Note("F", 5, 1.0),
    Note("D", 5, 1.0),
]
for _ in range(8):
    lead.extend(melody)

bass = song.add_track(Track(name="bass", instrument="bass", volume=0.55))
for _ in range(8):
    bass.extend([Note("D", 2, 2.0), Note("A", 2, 2.0)])

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.7))
for _ in range(8):
    kick.extend([Note("C", 2, 1.0)] * 4)

# THE KEY FEATURE: gradual slowdown from 140 → 70 BPM over all 8 bars
song.bpm_map = bpm_ramp(140, 70, bars=8)

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.35).add(stereo_width, width=1.5),
    "lead": EffectsChain().add(reverb, room_size=0.5, wet=0.2),
}
