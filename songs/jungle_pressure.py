"""jungle_pressure.py — Jungle / breakbeat. Am, 170 BPM. Amen break energy.

A chopped-up breakbeat jungle track with reese bass, ragga-style stabs,
and filtered pad washes. Shy FX / Congo Natty territory.

Style: Jungle, Am, 170 BPM.
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    Track,
    delay,
    highpass,
    lowpass,
    reverb,
    stereo_width,
)

song = Song(title="Jungle Pressure", bpm=170)

r = Note.rest

# ── Drums — chopped breakbeat ────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.8))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.6))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.35))

break_kick = [
    Note("C", 2, 0.5),
    r(0.25),
    Note("C", 2, 0.25),
    r(0.5),
    Note("C", 2, 0.5),
    r(0.5),
    Note("C", 2, 0.25),
    r(0.25),
    Note("C", 2, 0.5),
    r(0.5),
]
break_snare = [
    r(1.0),
    Note("E", 4, 0.5),
    r(0.5),
    Note("E", 4, 0.25),
    r(0.25),
    Note("E", 4, 0.5),
    r(0.5),
    Note("E", 4, 0.5),
    r(0.25),
    Note("E", 4, 0.25),
]
for _ in range(24):
    kick.extend(break_kick)
    snare.extend(break_snare)
    hat.extend([Note("F#", 6, 0.25)] * 16)

# ── Reese bass — dark sub ────────────────────────────────────────────────
bass = song.add_track(Track(name="reese", instrument="bass", volume=0.65, pan=0.0))
bass_line = [
    Note("A", 2, 2.0),
    Note("A", 2, 1.0),
    Note("E", 2, 1.0),
    Note("A", 2, 1.0),
    Note("G", 2, 0.5),
    Note("A", 2, 0.5),
    r(1.0),
]
for _ in range(12):
    bass.extend(bass_line)

# ── Stab — ragga chord hit ───────────────────────────────────────────────
stab = song.add_track(Track(name="stab", instrument="pluck", volume=0.4, pan=0.2))
stab_riff = [
    r(0.5),
    Chord("A", "min", 4, duration=0.5),
    r(1.0),
    Chord("G", "min", 4, duration=0.5),
    r(0.5),
    Chord("A", "min", 4, duration=0.5),
    r(0.5),
]
for _ in range(12):
    stab.extend(stab_riff)

# ── Pad — filtered atmosphere ────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.25, pan=0.0))
for _ in range(12):
    pad.extend(
        [
            Chord("A", "min7", 3, duration=4.0),
            Chord("G", "min7", 3, duration=4.0),
        ]
    )

for i, track in enumerate(song.tracks):
    if track.name == "pad":
        song.tracks[i] = track.fade_in(beats=16.0).fade_out(beats=16.0)

song.effects = {
    "reese": EffectsChain().add(lowpass, cutoff_hz=200),
    "stab": EffectsChain()
    .add(delay, delay_ms=176, feedback=0.25, wet=0.18)
    .add(highpass, cutoff_hz=400),
    "pad": EffectsChain().add(reverb, room_size=0.75, wet=0.4).add(stereo_width, width=1.7),
}
