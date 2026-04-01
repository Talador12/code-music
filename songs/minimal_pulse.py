"""minimal_pulse.py — Minimal techno. Am, 124 BPM. Less is more.

A hypnotic minimal techno piece built on repetition and subtle variation.
Single-note bass, sparse percussion, slowly evolving filtered pad.
Richie Hawtin / Ricardo Villalobos territory.

Style: Minimal techno, Am, 124 BPM.
"""

from code_music import Chord, Note, Song, Track, highpass, lfo_filter, reverb

song = Song(title="Minimal Pulse", bpm=124)

r = Note.rest

# ── Kick — four on the floor, unrelenting ────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
for _ in range(32):
    kick.extend([Note("C", 2, 1.0)] * 4)

# ── Hat — offbeat, minimal ───────────────────────────────────────────────
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.25))
for _ in range(32):
    hat.extend([r(0.5), Note("F#", 6, 0.5)] * 4)

# ── Rimshot — sparse accent every 4 bars ─────────────────────────────────
rim = song.add_track(Track(name="rim", instrument="drums_snare", volume=0.3))
for _ in range(8):
    rim.extend([r(1.0), Note("E", 5, 0.5, velocity=0.4), r(14.5)])

# ── Bass — single hypnotic note with slight variation ────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.6))
bass_patterns = [
    [
        Note("A", 2, 0.5),
        r(0.5),
        Note("A", 2, 0.5),
        r(0.5),
        Note("A", 2, 0.5),
        r(1.0),
        Note("A", 2, 0.5),
    ],
    [
        Note("A", 2, 0.5),
        r(0.5),
        Note("A", 2, 0.5),
        Note("A", 2, 0.5),
        r(0.5),
        Note("A", 2, 0.5),
        r(0.5),
        Note("E", 2, 0.5),
    ],
]
for i in range(32):
    bass.extend(bass_patterns[i % 2])

# ── Pad — slowly filtered wash ───────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3, pan=0.0))
for _ in range(32):
    pad.add(Chord("A", "min7", 3, duration=4.0))

# Fade pad in over first 16 bars, out over last 16
for i, track in enumerate(song.tracks):
    if track.name == "pad":
        song.tracks[i] = track.fade_in(beats=32.0).fade_out(beats=32.0)

song.effects = {
    "pad": lambda s, sr: lfo_filter(
        reverb(s, sr, room_size=0.7, wet=0.35), sr, rate=0.08, depth=0.6
    ),
    "bass": lambda s, sr: highpass(s, sr, cutoff_hz=60),
}
