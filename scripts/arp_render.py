"""On-the-fly arpeggio renderer for any scale + key combination.

Each arpeggio uses chord tones: root (1), third (3), fifth (5) per octave,
plus the octave root at the top. Works correctly at 1, 2, 3, or more octaves.

Patterns are expressed as lambdas over the actual pool length, so they
stretch/compress naturally regardless of how many octaves are requested.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Callable

# Chord-tone scale-degree indices (0-based into the scale's interval list)
# 1st, 3rd, 5th of any diatonic scale — for shorter scales, all notes used.
CHORD_TONE_INDICES = [0, 2, 4]


def _pool_size(octaves: int, tones_per_oct: int) -> int:
    """Total pool size = (tones_per_octave × octaves) + 1 top root."""
    return tones_per_oct * octaves + 1


# Pattern functions: given pool_size n, return the list of indices to play.
# Using a dict of callables means every pattern works at any octave count.
def _up(n: int) -> list[int]:
    """All pool indices ascending: 0 1 2 3 … n-1."""
    return list(range(n))


def _arc(n: int) -> list[int]:
    """Clean arc: up to peak then mirror back, no repeated peak.
    1 oct (n=4): 0 1 2 3 2 1       → C E G C G E
    2 oct (n=7): 0 1 2 3 4 5 6 5 4 3 2 1
    """
    up = list(range(n))
    return up + list(range(n - 2, 0, -1))


ARP_PATTERN_FNS: dict[str, Callable[[int], list[int]]] = {
    # Straight up: 1 3 5 8 [10 12 15 ...]
    "up": _up,
    # Straight down: mirror of up
    "down": lambda n: list(range(n - 1, -1, -1)),
    # Clean arc — the classic arpeggio: up to top then back down, no double peak
    # 1 oct: 1 3 5 8 5 3      2 oct: 1 3 5 8 10 12 15 12 10 8 5 3
    "up_down": _arc,
    # Cascade: skip-note up (root → 5th → oct → ...) then mirror
    # 1 oct: 1 5 8 5      2 oct: 1 5 10 15 10 5
    "cascade": lambda n: (lambda ups: ups + ups[-2::-1])(
        [i for i in range(0, n, 2)] + ([n - 1] if (n - 1) % 2 != 0 else [])
    ),
    # Broken: interleave consecutive + skip (step-and-leap alternation)
    # 1 oct: 1 5 3 8      2 oct: 1 5 3 8 5 12 10 15
    "broken": lambda n: (
        [x for pair in zip(range(0, n - 1, 2), range(2, n, 2)) for x in pair] + [n - 1]
    ),
    # Alberti bass: low - high - mid - high (Mozart / Clementi)
    # Groups of 3 chord tones: root, oct, 3rd, oct, root, oct ...
    "alberti": lambda n: [
        x for i in range(0, n - 1, 2) for x in [i, n - 1, min(i + 1, n - 1), n - 1]
    ],
    # Outside-in: pinch from both ends toward middle
    # 1 oct: 1 8 3 5      2 oct: 1 15 3 12 5 10 8
    "outside_in": lambda n: [v for pair in zip(range(n), range(n - 1, -1, -1)) for v in pair][:n],
    # Inside-out: explode from the middle outward
    "inside_out": lambda n: sorted(range(n), key=lambda i: abs(i - (n - 1) / 2)),
    # Stride: root + big leap alternating, walking up
    # 1 oct: 1 8 3 8 5 8      2 oct: 1 15 3 15 5 15 8 15 ...
    "stride": lambda n: [x for i in range(n - 1) for x in [i, n - 1]] + [n - 1],
    # Rolling groups of 4, sliding up one step each time
    # Gives an overlapping, flowing feel
    "rolling": lambda n: (
        [i + j for i in range(max(1, n - 3)) for j in [0, 1, 2, 3] if i + j < n] + [n - 1]
    ),
    # Waltz: bass on 1, chord on 2 & 3 (3-note groupings)
    # Maps naturally to 3/4 time feel
    "waltz": lambda n: [
        v
        for i in range(0, n, max(1, (n - 1) // 3))
        for v in [0, min(i + 1, n - 1), min(i + 2, n - 1)]
    ],
    # Skip: every other note up then odd notes fill in going down
    "skip": lambda n: (lambda evens: evens + [i for i in range(n - 2, 0, -1) if i not in evens])(
        list(range(0, n, 2)) + ([n - 1] if (n - 1) % 2 != 0 else [])
    ),
}

# Human-readable descriptions
ARP_PATTERN_NAMES: dict[str, str] = {
    "up": "ascending",
    "down": "descending",
    "up_down": "up & back",
    "cascade": "1-5-oct ripple",
    "broken": "broken chord",
    "alberti": "Alberti bass",
    "outside_in": "pinch inward",
    "inside_out": "explode outward",
    "stride": "stride jumps",
    "rolling": "rolling groups",
    "waltz": "waltz (3/4)",
    "skip": "skip-step",
}


def render_arp(
    scale_key: str,
    pattern: str = "up_down",
    octaves: int = 2,
    bpm: float = 130.0,
    instrument: str = "piano",
    note_rate: float = 0.25,
) -> Path:
    """Render chord-tone arpeggios in all 12 keys to a temp WAV.

    Pool per key = (root, 3rd, 5th) × octaves + top root.
      octaves=1 → 4 notes  (C E G C)
      octaves=2 → 7 notes  (C E G C E G C)
      octaves=3 → 10 notes (C E G C E G C E G C)

    Pattern indices address this pool, so every pattern works at any octave.
    """
    from code_music.engine import SCALES, Note, Song, Track, note_name_to_midi

    CIRCLE = ["C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "F"]

    if scale_key not in SCALES:
        raise ValueError(f"Unknown scale: {scale_key!r}.\nAvailable: {sorted(SCALES.keys())}")

    intervals = SCALES[scale_key]
    # For short scales (pentatonic=5, blues=6) grab all tones
    tone_indices = CHORD_TONE_INDICES if len(intervals) > 4 else list(range(len(intervals)))

    pat_fn = ARP_PATTERN_FNS.get(pattern, ARP_PATTERN_FNS["up_down"])

    song = Song(title=f"{scale_key} arp", bpm=bpm)
    tr = song.add_track(Track(name="arp", instrument=instrument, volume=0.78))

    for root in CIRCLE:
        root_midi = note_name_to_midi(root, octave=4)

        # Build pool: chord tones across all octaves + top root
        pool: list[int] = []
        for oct_off in range(octaves):
            for ti in tone_indices:
                pool.append(root_midi + intervals[ti] + oct_off * 12)
        pool.append(root_midi + octaves * 12)  # top root

        n = len(pool)

        # Generate pattern indices for this pool size, clamp to valid range
        try:
            indices = [min(max(i, 0), n - 1) for i in pat_fn(n)]
        except Exception:
            indices = list(range(n))  # fallback to straight up

        for idx in indices:
            tr.add(Note(pitch=pool[idx], duration=note_rate, velocity=0.75))

        tr.add(Note.rest(note_rate * 2))  # pause between keys

    from code_music.export import export_wav
    from code_music.synth import Synth

    samples = Synth(sample_rate=44100).render_song(song)
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    export_wav(samples, tmp.name, sample_rate=44100)
    return Path(tmp.name)
