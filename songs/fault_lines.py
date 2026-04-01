"""fault_lines.py — Prog metal / metal. 152 BPM, Bm, 7/8 time. Second Fault Line track.

Tool influence: odd time, space between riffs, bass does independent work.
7/8 time signature means every bar is 7 eighth notes — one beat short of 4/4.
The asymmetry is the point. Your body keeps expecting the downbeat and it
keeps arriving one eighth note early. That tension IS the music.
"""

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    compress,
    crescendo,
    distortion,
    highpass,
    reverb,
)
from code_music.engine import EIGHTH

song = Song(title="Fault Lines", bpm=152, time_sig=(7, 8))

# In 7/8: 1 beat = 1 eighth note = 0.5 beats in quarter-note terms
# BAR = 7 eighth notes = 3.5 quarter-note beats
BAR = 3.5
r = Note.rest

E8 = EIGHTH  # 0.5 beats


def bars(n):
    return [r(BAR)] * n


# ── Riff — the main guitar motif, 7/8 pattern ─────────────────────────────
gtr = song.add_track(Track(name="guitar", instrument="guitar_electric", volume=0.78, pan=-0.2))

# 7/8 riff: 2+2+3 grouping (the Tool approach)
riff = [
    Note("B", 2, E8),
    Note("B", 2, E8),  # group of 2
    Note("B", 2, E8),
    Note("B", 2, E8),  # group of 2
    Note("B", 2, E8),
    Note("D", 3, E8),
    Note("A", 2, E8),  # group of 3
]
# Verse: just the riff
gtr.extend(riff * 4)
# Variation: shift pitches up
riff_var = [
    Note("D", 3, E8),
    Note("D", 3, E8),
    Note("D", 3, E8),
    Note("D", 3, E8),
    Note("D", 3, E8),
    Note("F", 3, E8),
    Note("C", 3, E8),
]
gtr.extend(riff_var * 4)
# Climax: full chords
for ch, sh in [("B", "min"), ("G", "maj"), ("D", "maj"), ("A", "maj")] * 2:
    gtr.add(Chord(ch, sh, 2, duration=BAR, velocity=0.88))
# Bridge: sparse
gtr.extend(
    crescendo(
        [
            Note("B", 2, BAR * 2),
            Note("F#", 2, BAR * 2),
            Note("G", 2, BAR * 2),
            Note("A", 2, BAR * 2),
        ],
        0.4,
        0.9,
    )
)
# Return riff
gtr.extend(riff * 4)
gtr.extend(riff_var * 2)

# ── Bass — independent voice, sometimes contradicts guitar ───────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.82, pan=0.1))
# Bass plays against the riff — holding on notes guitar skips over
bass_line = [
    Note("B", 1, E8 * 3),
    Note("A", 1, E8 * 2),
    Note("G", 1, E8 * 2),
] * 4
bass.extend(bass_line)
bass_var = [
    Note("D", 2, E8 * 3),
    Note("C", 2, E8 * 2),
    Note("B", 1, E8 * 2),
] * 4
bass.extend(bass_var)
# Climax: root locked
for p, dur in [("B", BAR * 2), ("G", BAR * 2), ("D", BAR * 2), ("A", BAR * 2)] * 2:
    bass.add(Note(p, 1, dur, velocity=0.9))
# Bridge
bass.extend(
    [
        Note("B", 1, BAR * 4),
        Note("F#", 1, BAR * 4),
        Note("G", 1, BAR * 2),
        Note("A", 1, BAR * 2),
    ]
)
# Return
bass.extend(bass_line + bass_var[: len(bass_var) // 2])

# ── Drums — 7/8 kit ───────────────────────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.98))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.82))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.45))

# 7/8 drum pattern: accent 1, 3, 6 (2+2+3)
drum_pat = [
    Note("C", 2, E8),
    r(E8),  # beat 1 (kick)
    Note("C", 2, E8),
    Note("D", 3, E8),  # beat 3 (kick+snare)
    r(E8),
    r(E8),
    Note("D", 3, E8),  # beat 6 (snare on 3rd of final group)
]
hat_pat = [Note("F", 5, E8)] * 7

for _ in range(16):
    kick.extend([Note("C", 2, E8), r(E8), Note("C", 2, E8), r(E8), r(E8), r(E8), Note("C", 2, E8)])
    snare.extend([r(E8), r(E8), r(E8), Note("D", 3, E8), r(E8), Note("D", 3, E8), r(E8)])
    hat.extend(hat_pat)

# Climax: double kick
for _ in range(8):
    kick.extend([Note("C", 2, E8)] * 7)
    snare.extend([r(E8), r(E8), r(E8), Note("D", 3, E8), r(E8), Note("D", 3, E8), r(E8)])
    hat.extend(hat_pat)

# Bridge: half time feel
for _ in range(8):
    kick.extend([Note("C", 2, E8 * 3), r(E8 * 2), r(E8 * 2)])
    snare.extend([r(E8 * 3), Note("D", 3, E8 * 2), r(E8 * 2)])
    hat.extend([Note("F", 5, E8), r(E8)] * 3 + [Note("F", 5, E8)])

# Return
for _ in range(8):
    kick.extend([Note("C", 2, E8), r(E8), Note("C", 2, E8), r(E8), r(E8), r(E8), Note("C", 2, E8)])
    snare.extend([r(E8), r(E8), r(E8), Note("D", 3, E8), r(E8), Note("D", 3, E8), r(E8)])
    hat.extend(hat_pat)

song.effects = {
    "guitar": lambda s, sr: distortion(
        reverb(s, sr, room_size=0.35, wet=0.1), drive=3.5, tone=0.65, wet=0.7
    ),
    "bass": lambda s, sr: compress(
        highpass(s, sr, cutoff_hz=60.0), sr, threshold=0.5, ratio=5.0, makeup_gain=1.2
    ),
}
