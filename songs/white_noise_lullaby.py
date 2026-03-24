"""white_noise_lullaby.py — Experimental / noise ambient. 50 BPM. Texture only.

Not a song in the conventional sense — no melody, no chords, no rhythm.
Just layered textures: granular-processed pad, bitcrushed drone,
ring-modulated noise. The most experimental thing in the library.
Merzbow it ain't, but it's in that direction.
"""

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    bitcrush,
    granular,
    lowpass,
    reverb,
    ring_mod,
    stereo_width,
)

song = Song(title="White Noise Lullaby", bpm=50)
BAR = 4.0

# ── Drone — sine, barely moving ────────────────────────────────────────────
drone = song.add_track(Track(name="drone", instrument="sine", volume=0.35))
for _ in range(16):
    drone.add(Note("C", 2, BAR, velocity=0.5))

# ── Pad — granular texture ─────────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.3))
for _ in range(4):
    pad.add(Chord("C", "sus2", 3, duration=BAR * 4, velocity=0.4))

# ── Noise layer ────────────────────────────────────────────────────────────
noise = song.add_track(Track(name="noise", instrument="noise_sweep", volume=0.2))
for _ in range(16):
    noise.add(Note("C", 4, BAR, velocity=0.35))

# ── High texture — bitcrushed triangle ─────────────────────────────────────
hi = song.add_track(Track(name="hi", instrument="triangle", volume=0.15, pan=0.4))
for _ in range(16):
    hi.add(Note("G", 6, BAR, velocity=0.25))

song._effects = {
    "drone": lambda s, sr: lowpass(reverb(s, sr, room_size=0.95, wet=0.6), sr, cutoff_hz=200.0),
    "pad": lambda s, sr: stereo_width(
        granular(
            reverb(s, sr, room_size=0.9, wet=0.5),
            sr,
            grain_size_ms=100.0,
            scatter=0.5,
            pitch_spread=0.4,
            wet=0.7,
        ),
        width=1.95,
    ),
    "noise": lambda s, sr: ring_mod(
        reverb(s, sr, room_size=0.8, wet=0.4), sr, freq_hz=220.0, wet=0.5
    ),
    "hi": lambda s, sr: bitcrush(
        reverb(s, sr, room_size=0.7, wet=0.3), sr, bit_depth=6, downsample=4, wet=0.6
    ),
}
