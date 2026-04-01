"""fade_to_dawn.py — Ambient piece showcasing Track.fade_in / fade_out.

A slow ambient wash that fades in over the first 16 beats, sustains,
then fades out over the last 16 beats. Three layers with staggered fades
create a breathing texture.

Style: Brian Eno ambient, E major, 72 BPM.
"""

from code_music import Chord, EffectsChain, Note, Song, Track, reverb, stereo_width

song = Song(title="Fade to Dawn", bpm=72)

TOTAL_BARS = 16
BAR = 4.0
r = Note.rest

# ── Pad layer — slow wash ──────────────────────────────────────────────────
pad = Track(name="pad", instrument="pad", volume=0.5, pan=0.0)
for _ in range(TOTAL_BARS):
    pad.add(Chord("E", "maj7", 3, duration=BAR))

# ── High shimmer — enters late, exits early ────────────────────────────────
shimmer = Track(name="shimmer", instrument="triangle", volume=0.3, pan=0.3)
melody = [Note("B", 5, 2.0), Note("G#", 5, 1.0), Note("E", 5, 1.0)]
for _ in range(TOTAL_BARS):
    shimmer.extend(melody)

# ── Sub drone — constant anchor ────────────────────────────────────────────
drone = Track(name="drone", instrument="sine", volume=0.35, pan=-0.1)
for _ in range(TOTAL_BARS):
    drone.add(Note("E", 2, BAR))

# Apply staggered fades
song.add_track(pad.fade_in(beats=16.0).fade_out(beats=16.0))
song.add_track(shimmer.fade_in(beats=24.0).fade_out(beats=24.0))
song.add_track(drone.fade_in(beats=8.0).fade_out(beats=8.0))

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.85, wet=0.45).add(stereo_width, width=1.8),
    "shimmer": EffectsChain().add(reverb, room_size=0.7, wet=0.35),
}
