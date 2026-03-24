"""neon_prayer.py — Future bass / synth pop. Ab major, 145 BPM.

Where future_bass.py is driving, this one is more introspective.
Ab major sits in a strange harmonic space — bright but with all those
flats making it feel slightly unresolved. Supersaw chords, vibraphone
melody, choir pad underneath. The kind of song that plays over
an anime ending sequence when the credits start rolling.
"""

from code_music import (
    DOTTED_QUARTER,
    EIGHTH,
    HALF,
    QUARTER,
    WHOLE,
    Note,
    Song,
    Track,
    chorus,
    compress,
    crescendo,
    decrescendo,
    humanize,
    reverb,
    stereo_width,
    suggest_progression,
)

song = Song(title="Neon Prayer", bpm=145)

BAR = 4.0
r = Note.rest

PROG = suggest_progression("G#", mood="dreamy", octave=3, duration=BAR, velocity=0.6)

# ── Kick + hat ────────────────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=1.0))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.38))
kick.extend([r(BAR)] * 4)
kick.extend([Note("C", 2, 1.0)] * (24 * 4))
hat.extend([r(BAR)] * 4)
hat.extend([r(0.5), Note("F", 5, 0.5)] * (24 * 4))

# ── Supersaw pad ──────────────────────────────────────────────────────────
pad = song.add_track(Track(name="pad", instrument="supersaw", volume=0.48, pan=0.0))
for _ in range(7):
    pad.extend(PROG)

# ── Choir underneath ──────────────────────────────────────────────────────
choir = song.add_track(Track(name="choir", instrument="choir_ooh", volume=0.32, pan=0.1))
choir.extend([r(BAR)] * 8)
for _ in range(5):
    choir.extend(PROG)

# ── Vibraphone melody — the emotional center ──────────────────────────────
vib = song.add_track(Track(name="vibes", instrument="vibraphone", volume=0.65, pan=-0.1))
vib.extend([r(BAR)] * 4)

mel = humanize(
    crescendo(
        [
            Note("G#", 5, DOTTED_QUARTER),
            Note("A#", 5, EIGHTH),
            Note("C", 6, HALF),
            Note("A#", 5, QUARTER),
            Note("G#", 5, QUARTER),
            Note("F", 5, HALF),
            r(HALF),
            Note("D#", 5, DOTTED_QUARTER),
            Note("F", 5, EIGHTH),
            Note("G#", 5, HALF),
            Note("F", 5, QUARTER),
            Note("D#", 5, QUARTER),
            Note("C", 5, WHOLE),
            r(BAR),
            Note("A#", 5, HALF),
            Note("G#", 5, QUARTER),
            Note("F", 5, QUARTER),
            Note("D#", 5, HALF),
            Note("C", 5, WHOLE),
        ],
        0.4,
        0.9,
    ),
    vel_spread=0.06,
    timing_spread=0.04,
)
vib.extend(mel)
vib.extend(mel[: len(mel) // 2])
vib.extend(decrescendo(mel[len(mel) // 2 :], 0.8, 0.2))

# ── Bass ──────────────────────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.72))
bass.extend([r(BAR)] * 4)
for ch in PROG * 6:
    bass.add(Note(ch.root, ch.octave - 1, ch.duration * 0.5, velocity=0.75))
    bass.add(r(ch.duration * 0.5))

song._effects = {
    "pad": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.55, wet=0.22), width=1.7),
    "choir": lambda s, sr: stereo_width(reverb(s, sr, room_size=0.8, wet=0.4), width=1.8),
    "vibes": lambda s, sr: chorus(
        reverb(s, sr, room_size=0.65, wet=0.3), sr, rate_hz=0.35, wet=0.2
    ),
    "bass": lambda s, sr: compress(s, sr, threshold=0.5, ratio=4.0, makeup_gain=1.1),
}
