"""drill_sermon.py — UK drill. Cm, 140 BPM. Dark, sliding 808s, militant hats.

Classic UK drill production with half-time kick/snare, rapid hi-hat rolls,
sliding sub bass, and a minor key piano melody. 67 / Headie One territory.

Style: UK drill, Cm, 140 BPM (half-time feel).
"""

from code_music import (
    Chord,
    EffectsChain,
    Note,
    Song,
    Track,
    compress,
    highpass,
    lowpass,
    reverb,
)

song = Song(title="Drill Sermon", bpm=140)

r = Note.rest

# ── Drums — half-time bounce ─────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.85))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.6))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.4))

for _ in range(16):
    # Half-time: kick on 1, snare on 3
    kick.extend([Note("C", 2, 1.0), r(3.0)])
    snare.extend([r(2.0), Note("E", 4, 1.0), r(1.0)])
    # Rapid hat rolls with ghost accents
    hat.extend(
        [
            Note("F#", 6, 0.25),
            Note("F#", 6, 0.25, velocity=0.4),
            Note("F#", 6, 0.25),
            Note("F#", 6, 0.25, velocity=0.3),
            Note("F#", 6, 0.25),
            Note("F#", 6, 0.25, velocity=0.4),
            Note("F#", 6, 0.25),
            Note("F#", 6, 0.25),
            Note("F#", 6, 0.25),
            Note("F#", 6, 0.25, velocity=0.3),
            Note("F#", 6, 0.25),
            Note("F#", 6, 0.25, velocity=0.4),
            Note("F#", 6, 0.25),
            Note("F#", 6, 0.25),
            Note("F#", 6, 0.25),
            Note("F#", 6, 0.25, velocity=0.3),
        ]
    )

# ── 808 bass — sliding sub ───────────────────────────────────────────────
bass = song.add_track(Track(name="808", instrument="sine", volume=0.75, pan=0.0))
bass_pattern = [
    Note("C", 2, 1.5),
    Note("Eb", 2, 0.5),
    Note("C", 2, 1.0),
    r(1.0),
    Note("C", 2, 0.5),
    Note("Bb", 1, 0.5),
    Note("C", 2, 1.0),
    r(2.0),
]
for _ in range(8):
    bass.extend(bass_pattern)

# ── Piano — dark minor melody ────────────────────────────────────────────
piano = song.add_track(Track(name="piano", instrument="piano", volume=0.4, pan=0.1))
piano_riff = [
    Note("Eb", 5, 0.5),
    Note("D", 5, 0.5),
    Note("C", 5, 0.5),
    r(0.5),
    Note("G", 4, 0.5),
    Note("Ab", 4, 0.5),
    Note("G", 4, 1.0),
    Note("Eb", 5, 0.5),
    Note("D", 5, 0.5),
    Note("C", 5, 0.5),
    Note("Bb", 4, 0.5),
    Note("Ab", 4, 0.5),
    Note("G", 4, 0.5),
    r(1.0),
]
for _ in range(8):
    piano.extend(piano_riff)

# ── Pad — atmospheric tension ────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.2, pan=0.0))
for _ in range(8):
    pad.extend(
        [
            Chord("C", "min", 3, duration=4.0),
            Chord("Ab", "maj", 3, duration=4.0),
        ]
    )

song.effects = {
    "808": EffectsChain().add(lowpass, cutoff_hz=150).add(compress, threshold=0.4, ratio=6.0),
    "piano": EffectsChain().add(reverb, room_size=0.5, wet=0.2).add(highpass, cutoff_hz=300),
    "pad": EffectsChain().add(reverb, room_size=0.8, wet=0.4),
}
