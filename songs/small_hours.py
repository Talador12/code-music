"""small_hours.py — Lo-fi hip-hop. 85 BPM, Fm. Second track for Small Hours album.

Slower and more melancholic than lo_fi_loop. Fm instead of Am.
Fewer drums — just brushed snare and sparse kick. The piano does more work.
That 4am feeling when you've been up too long and your thoughts go honest.
"""

from code_music import (
    Chord,
    Note,
    Song,
    Track,
    chorus,
    compress,
    delay,
    reverb,
)

song = Song(title="Ember", bpm=85)

BAR = 4.0
SWING = 0.5
r = Note.rest


def bars(n):
    return [r(BAR)] * n


# ── Sparse kick — not on every beat ──────────────────────────────────────
kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.75))
# Irregular pattern — feels human, not programmed
kick_pat = [
    Note("C", 2, 1.0),
    r(1.0),
    r(1.0),
    Note("C", 2, 0.5),
    r(0.5),
    r(1.0),
    Note("C", 2, 1.0),
    r(0.5),
    Note("C", 2, 0.5),
    r(1.0),
]
kick.extend(kick_pat * 8)

# ── Brushed snare — like a whisper ───────────────────────────────────────
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.42, swing=SWING))
snare.extend(
    [r(1.0), Note("D", 3, 1.0, velocity=0.35), r(1.0), Note("D", 3, 1.0, velocity=0.3)] * 10
)

# ── Hi-hat — very sparse, 8th notes ──────────────────────────────────────
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.28, swing=SWING))
hat.extend([Note("F", 5, 0.5, velocity=0.3)] * (10 * 8))

# ── Piano — carries the whole track ──────────────────────────────────────
piano = song.add_track(Track(name="piano", instrument="piano", volume=0.72, swing=SWING))
melody = [
    Note("F", 4, 1.5),
    Note("G#", 4, 0.5),
    Note("A#", 4, 1.0),
    r(0.5),
    Note("C", 5, 0.5),
    Note("F", 4, 2.0),
    r(BAR),
    Note("D#", 4, 1.0),
    Note("F", 4, 0.5),
    Note("G#", 4, 0.5),
    Note("A#", 4, 1.5),
    Note("G#", 4, 0.5),
    Note("F", 4, 2.0),
    r(BAR),
    Note("C", 5, 1.0),
    Note("A#", 4, 0.5),
    Note("G#", 4, 0.5),
    Note("F", 4, 1.0),
    Note("D#", 4, 1.0),
    Note("F", 4, 4.0),
    r(BAR),
]
piano.extend(melody * 2)
piano.extend(melody[: len(melody) // 2])

# ── Chord comp — sparse, Rhodes-ish ──────────────────────────────────────
comp = song.add_track(Track(name="comp", instrument="rhodes", volume=0.45, pan=-0.1, swing=SWING))
prog = [
    Chord("F", "min7", 3, duration=BAR * 2, velocity=0.45),
    Chord("C#", "maj7", 3, duration=BAR * 2, velocity=0.42),
    Chord("G#", "maj7", 3, duration=BAR * 2, velocity=0.45),
    Chord("D#", "dom7", 3, duration=BAR * 2, velocity=0.43),
]
comp.extend(prog * 5)

# ── Bass — subtle, melodic ────────────────────────────────────────────────
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.58, swing=SWING))
bass.extend(
    [
        Note("F", 2, 2.0),
        Note("C#", 2, 2.0),
        Note("G#", 1, 2.0),
        Note("D#", 2, 2.0),
    ]
    * 5
)

song._effects = {
    "piano": lambda s, sr: delay(
        reverb(s, sr, room_size=0.55, wet=0.22), sr, delay_ms=353.0, feedback=0.28, wet=0.18
    ),
    "comp": lambda s, sr: chorus(
        reverb(s, sr, room_size=0.45, wet=0.15), sr, rate_hz=0.4, wet=0.12
    ),
    "bass": lambda s, sr: compress(s, sr, threshold=0.55, ratio=3.0, makeup_gain=1.1),
}
