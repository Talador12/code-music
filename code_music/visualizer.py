"""Real-time CLI music visualizer.

Custom ANSI animation engine. No rich, no textual, no new dependencies —
just stdlib + numpy (already required by the synth). Same DIY ethos as
SoundDesigner: build it from raw primitives.

What you get while a song plays:
    - Animated gradient title bar with BPM, bar/beat counter, time
    - Per-track scrolling piano-roll lanes (notes glide right-to-left
      through a "now" line, currently-sounding notes flare bright)
    - Per-track VU meters with exponential decay on note onsets
    - 12-band log-spaced spectrum analyzer pulled from a real FFT of
      the rendered audio
    - Truecolor gradients across an evenly-distributed HSL palette so
      every track gets a distinct color

Usage::

    from code_music import Song, Track, Note
    from code_music.visualizer import play_visual

    song = Song(title="Demo", bpm=120)
    tr = song.add_track(Track(instrument="piano"))
    tr.extend([Note("C", 4, 1.0), Note("E", 4, 1.0), Note("G", 4, 1.0)])

    play_visual(song)

CLI::

    code-music my_song.py --visualize
"""

from __future__ import annotations

import math
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from .engine import Song


# ─── ANSI primitives ──────────────────────────────────────────────────
CSI = "\x1b["
RESET = f"{CSI}0m"
HIDE_CURSOR = f"{CSI}?25l"
SHOW_CURSOR = f"{CSI}?25h"
CLEAR_SCREEN = f"{CSI}2J"
HOME = f"{CSI}H"
ALT_SCREEN_ON = f"{CSI}?1049h"
ALT_SCREEN_OFF = f"{CSI}?1049l"


def _truecolor(r: int, g: int, b: int) -> str:
    """Build a 24-bit foreground color escape sequence."""
    return f"{CSI}38;2;{int(r)};{int(g)};{int(b)}m"


def _hsl_to_rgb(h: float, s: float, lightness: float) -> tuple[int, int, int]:
    """HSL→RGB. h,s,l in [0,1]. Returns 0-255 ints."""
    if s == 0:
        v = int(lightness * 255)
        return v, v, v

    def _h2rgb(p: float, q: float, t: float) -> float:
        t = t % 1.0
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6
        return p

    q = lightness * (1 + s) if lightness < 0.5 else lightness + s - lightness * s
    p = 2 * lightness - q
    r = _h2rgb(p, q, h + 1 / 3)
    g = _h2rgb(p, q, h)
    b = _h2rgb(p, q, h - 1 / 3)
    return int(r * 255), int(g * 255), int(b * 255)


def _track_palette(n: int) -> list[tuple[int, int, int]]:
    """Evenly spaced HSL hues for N tracks, mid-bright saturated."""
    if n <= 0:
        return []
    return [_hsl_to_rgb((i / n + 0.05) % 1.0, 0.75, 0.62) for i in range(n)]


def _supports_color() -> bool:
    """Detect if the current TTY accepts ANSI escape codes."""
    if os.environ.get("NO_COLOR"):
        return False
    if not sys.stdout.isatty():
        return False
    return True


# ─── Frame buffer ─────────────────────────────────────────────────────
@dataclass
class Frame:
    """A 2D grid of (char, fg_rgb_or_None) cells, rendered to one ANSI string.

    Color reuse: render() only emits a new color escape when the cell color
    differs from the previous cell, keeping the per-frame byte count low.
    """

    w: int
    h: int
    grid: list[list[tuple[str, tuple[int, int, int] | None]]] = field(init=False)

    def __post_init__(self) -> None:
        self.grid = [[(" ", None) for _ in range(self.w)] for _ in range(self.h)]

    def put(
        self,
        x: int,
        y: int,
        ch: str,
        color: tuple[int, int, int] | None = None,
    ) -> None:
        """Place a single character at (x, y) if in bounds."""
        if 0 <= x < self.w and 0 <= y < self.h and len(ch) == 1:
            self.grid[y][x] = (ch, color)

    def text(
        self,
        x: int,
        y: int,
        s: str,
        color: tuple[int, int, int] | None = None,
    ) -> None:
        """Write a string starting at (x, y). Clips at right edge."""
        for i, ch in enumerate(s):
            self.put(x + i, y, ch, color)

    def hline(
        self,
        x: int,
        y: int,
        width: int,
        ch: str = "─",
        color: tuple[int, int, int] | None = None,
    ) -> None:
        """Draw a horizontal line of ch from (x, y) for width cells."""
        for i in range(width):
            self.put(x + i, y, ch, color)

    def render(self) -> str:
        """Flatten the grid into a single ANSI-escaped string."""
        out: list[str] = []
        cur: tuple[int, int, int] | None = None
        for row in self.grid:
            for ch, color in row:
                if color != cur:
                    out.append(RESET if color is None else _truecolor(*color))
                    cur = color
                out.append(ch)
            out.append(RESET)
            out.append("\n")
            cur = None
        if out and out[-1] == "\n":
            out.pop()
        return "".join(out)


# ─── Timeline extraction ──────────────────────────────────────────────
@dataclass
class _Onset:
    """One note or chord event with absolute timing in seconds.

    `midi` holds a single representative pitch (root for chords, the note
    itself for Notes; None only when neither is available). `midis` holds
    every pitch the event sounds — one entry for Notes, multiple for Chords.
    `duration_beats` preserves the source duration in beats so notation
    rendering can pick the right symbol regardless of tempo (a quarter note
    is always 1 beat, whether the song is at 60 BPM or 240 BPM).
    """

    track_idx: int
    start: float
    end: float
    label: str
    midi: int | None
    velocity: float
    midis: list[int] = field(default_factory=list)
    duration_beats: float = 1.0


def _format_chord_label(root: str, shape: object) -> str:
    """Render a chord as e.g. 'Cmin7' or 'A' (no shape)."""
    if isinstance(shape, str):
        return f"{root}{shape}"
    return f"{root}*"


def _build_timeline(song: "Song") -> tuple[list[list[_Onset]], float]:
    """Walk every track and convert beats into absolute-time onsets.

    Returns (per_track_onsets, total_duration_sec). Rests are skipped
    but still advance beat_pos so subsequent notes land at the right time.
    """
    from .engine import Chord, Note

    spb = 60.0 / max(song.bpm, 1.0)
    per_track: list[list[_Onset]] = []
    end_max = 0.0
    for ti, track in enumerate(song.tracks):
        onsets: list[_Onset] = []
        beat_pos = 0.0
        for beat in track.beats:
            event = beat.event
            dur_beats = getattr(event, "duration", 1.0) if event is not None else 1.0
            start = beat_pos * spb
            end = (beat_pos + dur_beats) * spb
            if isinstance(event, Note) and event.pitch is not None:
                label = (
                    f"{event.pitch}{event.octave}"
                    if isinstance(event.pitch, str)
                    else f"midi{event.pitch}"
                )
                m = event.midi
                onsets.append(
                    _Onset(
                        ti,
                        start,
                        end,
                        label,
                        m,
                        event.velocity,
                        midis=[m] if m is not None else [],
                        duration_beats=dur_beats,
                    )
                )
                end_max = max(end_max, end)
            elif isinstance(event, Chord):
                # Expand the chord into its actual MIDI pitches for the
                # live chord identifier and any pitch-aware visualizers.
                try:
                    chord_midis = [n.midi for n in event.notes if n.midi is not None]
                except Exception:
                    chord_midis = []
                onsets.append(
                    _Onset(
                        ti,
                        start,
                        end,
                        _format_chord_label(event.root, event.shape),
                        chord_midis[0] if chord_midis else None,
                        getattr(event, "velocity", 0.7),
                        midis=chord_midis,
                        duration_beats=dur_beats,
                    )
                )
                end_max = max(end_max, end)
            beat_pos += dur_beats
        per_track.append(onsets)
    total = max(end_max, song.duration_sec)
    return per_track, total


# ─── Spectrum precomputation ──────────────────────────────────────────
def _precompute_spectrum(
    samples: np.ndarray,
    sample_rate: int,
    n_bands: int = 12,
    hop_sec: float = 0.05,
) -> np.ndarray:
    """FFT-based log-binned spectrum, one column per hop.

    samples can be mono (N,) or stereo (N, 2). Returned shape is
    (n_hops, n_bands), values normalized to [0, 1].
    """
    if samples.ndim == 2:
        mono = samples.mean(axis=1)
    else:
        mono = samples
    hop = max(1, int(hop_sec * sample_rate))
    win = max(hop, 1024)
    n_hops = max(1, (len(mono) - win) // hop + 1)
    if n_hops < 1:
        return np.zeros((1, n_bands), dtype=np.float32)
    # Log-spaced band edges from ~40 Hz to Nyquist
    nyquist = sample_rate / 2
    edges = np.logspace(np.log10(40.0), np.log10(max(nyquist, 80.0)), n_bands + 1)
    fft_freqs = np.fft.rfftfreq(win, d=1.0 / sample_rate)
    out = np.zeros((n_hops, n_bands), dtype=np.float32)
    window = np.hanning(win)
    for i in range(n_hops):
        start = i * hop
        chunk = mono[start : start + win]
        if len(chunk) < win:
            chunk = np.pad(chunk, (0, win - len(chunk)))
        spec = np.abs(np.fft.rfft(chunk * window))
        for b in range(n_bands):
            mask = (fft_freqs >= edges[b]) & (fft_freqs < edges[b + 1])
            out[i, b] = float(spec[mask].mean()) if mask.any() else 0.0
    # Normalize per-band so each column reaches near-1 when its band is hot
    col_max = out.max(axis=0, keepdims=True)
    col_max[col_max < 1e-9] = 1.0
    out = out / col_max
    # Compress dynamic range so quiet stuff is still visible
    out = np.power(out, 0.55)
    return np.clip(out, 0.0, 1.0)


# ─── Rendering primitives ─────────────────────────────────────────────
_BLOCK_LEVELS = " ▁▂▃▄▅▆▇█"  # 9 levels for VU/EQ bars
_NOW_FILL = "█"
_FUTURE_FILL = "▓"
_PAST_FILL = "░"
_STAFF_HEIGHT = 7  # 1 above-staff row + 5 staff lines + 1 below-staff row
_SPARKLE_GLYPHS = ("✦", "✧", "·")  # high → low intensity for onset bursts
_SPARKLE_WINDOW = 0.22  # seconds — sparkle decays over this window
_NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
# Standard chord shapes the live readout will identify. Excludes academic
# voicings (clusters, polychords, slash bass, harmonic series, messiaen
# modes, register-specific voicings) so the readout stays readable.
_VISUALIZER_CHORD_NAMES = frozenset(
    {
        "maj",
        "min",
        "dim",
        "aug",
        "maj7",
        "min7",
        "dom7",
        "sus2",
        "sus4",
        "min7b5",
        "dim7",
        "maj6",
        "min6",
        "7sus4",
        "maj9",
        "min9",
        "dom9",
        "7b9",
        "7#9",
        "9",
        "add9",
        "maj_add9",
        "min_maj7",
        "min_add9",
        "6",
        "6/9",
        "power",
        "flat5",
        "aug7",
        "dim_maj7",
        "aug_maj7",
        "7b5",
        "7#5",
        "mu",
        "7sus2",
        "9sus4",
        "min11",
        "11",
        "13",
        "7#11",
        "maj7#11",
    }
)


def _vu_chars(level: float, width: int) -> str:
    """Render a 0..1 level as a horizontal bar of `width` block chars."""
    level = max(0.0, min(1.0, level))
    full = int(level * width)
    frac = (level * width) - full
    bar = _NOW_FILL * full
    if full < width:
        idx = int(frac * (len(_BLOCK_LEVELS) - 1))
        bar += _BLOCK_LEVELS[idx]
        bar += " " * (width - full - 1)
    return bar[:width]


def _vbar_char(level: float) -> str:
    """Single block char for a 0..1 vertical level."""
    level = max(0.0, min(1.0, level))
    return _BLOCK_LEVELS[int(level * (len(_BLOCK_LEVELS) - 1))]


def _scale_color(color: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    """Multiply an RGB triple by `factor`, clamped to [0, 255]."""
    r, g, b = color
    f = max(0.0, factor)
    return (
        max(0, min(255, int(r * f))),
        max(0, min(255, int(g * f))),
        max(0, min(255, int(b * f))),
    )


# ─── Live chord identification ────────────────────────────────────────
def _identify_chord(midis: list[int]) -> str:
    """Identify the chord name from a set of currently sounding MIDI pitches.

    Strategy: reduce to unique pitch classes, prefer the chord whose root
    matches the bass note (lowest sounding MIDI), then fall back to the
    first matching shape regardless of root. Resolves Amin7 vs C6 style
    ambiguities the way a listener would: by hearing the bass.
    """
    if not midis:
        return ""
    from .engine import CHORD_SHAPES

    pcs = sorted({m % 12 for m in midis})
    if len(pcs) == 1:
        return _NOTE_NAMES[pcs[0]]

    # Sort shapes shortest first so simpler matches (triads) win over extensions.
    # Restrict to the standard set so the live readout doesn't surface academic
    # cluster / polychord / slash-bass labels.
    shapes_sorted = sorted(
        (
            (name, shape)
            for name, shape in CHORD_SHAPES.items()
            if isinstance(shape, list) and name in _VISUALIZER_CHORD_NAMES
        ),
        key=lambda p: (len(p[1]), p[0]),
    )

    bass_pc = min(midis) % 12

    def _format(root_pc: int, name: str) -> str:
        root_name = _NOTE_NAMES[root_pc]
        return root_name if name == "maj" else f"{root_name}{name}"

    # Pass 1: prefer chords whose root matches the bass note
    for name, intervals in shapes_sorted:
        target = sorted({(bass_pc + iv) % 12 for iv in intervals})
        if target == pcs:
            return _format(bass_pc, name)

    # Pass 2: try every other root
    for root_pc in range(12):
        if root_pc == bass_pc:
            continue
        for name, intervals in shapes_sorted:
            target = sorted({(root_pc + iv) % 12 for iv in intervals})
            if target == pcs:
                return _format(root_pc, name)

    # No exact shape match — show the pitch classes (e.g. "C E G B")
    return " ".join(_NOTE_NAMES[pc] for pc in pcs)


def _currently_sounding_midis(timelines: list[list[_Onset]], t_now: float) -> list[int]:
    """Collect every MIDI pitch sounding at t_now across all tracks.

    Notes contribute their single pitch; Chords contribute every pitch
    in their voicing.
    """
    out: list[int] = []
    for track_onsets in timelines:
        for o in track_onsets:
            if o.start <= t_now < o.end:
                if o.midis:
                    out.extend(o.midis)
                elif o.midi is not None:
                    out.append(o.midi)
    return out


def _sparkle_at_now(onsets: list[_Onset], t_now: float) -> tuple[str, float] | None:
    """Return (glyph, intensity 0..1) if any onset began within the
    sparkle window before t_now, else None.
    """
    best: tuple[str, float] | None = None
    for o in onsets:
        age = t_now - o.start
        if 0.0 <= age <= _SPARKLE_WINDOW:
            intensity = 1.0 - (age / _SPARKLE_WINDOW)
            if best is None or intensity > best[1]:
                idx = int((1 - intensity) * len(_SPARKLE_GLYPHS))
                glyph_idx = min(len(_SPARKLE_GLYPHS) - 1, idx)
                best = (_SPARKLE_GLYPHS[glyph_idx], intensity)
    return best


# ─── Sheet music helpers ──────────────────────────────────────────────
def _midi_range_from_timelines(
    timelines: list[list[_Onset]],
) -> tuple[int, int]:
    """Find min/max MIDI across all pitched onsets, padded for staff fit."""
    midis: list[int] = []
    for track_onsets in timelines:
        for o in track_onsets:
            if o.midis:
                midis.extend(o.midis)
            elif o.midi is not None:
                midis.append(o.midi)
    if not midis:
        return 60, 72  # default C4..C5 range
    lo, hi = min(midis), max(midis)
    if hi == lo:
        return lo - 6, lo + 6
    # pad slightly so notes do not sit at the very top/bottom
    return lo - 1, hi + 1


def _staff_row(midi: int, midi_lo: int, midi_hi: int, n_rows: int = 7) -> int:
    """Map a MIDI pitch to a row index (0=top, n_rows-1=bottom).

    Rows 0 and n_rows-1 are reserved for above/below the 5-line staff.
    """
    if midi_hi <= midi_lo:
        return n_rows // 2
    frac = (midi - midi_lo) / (midi_hi - midi_lo)
    # invert so high pitch = low row index
    row = int(round((1.0 - frac) * (n_rows - 1)))
    return max(0, min(n_rows - 1, row))


def _note_rhythm(duration_beats: float) -> tuple[str, int, int]:
    """Return (head_glyph, stem_height, num_flags) for a duration in BEATS.

    Beats are tempo-independent: a quarter note is always 1 beat regardless
    of whether the song runs at 20 BPM or 400 BPM. The visualizer supports
    that full tempo range by reading durations from the song's beat grid,
    not from wall-clock seconds.

    Thresholds round to the nearest standard rhythmic value:
      whole       (≥ 3.0 beats): open head, no stem      (semibreve)
      half        (1.5–3.0):     open head + stem        (minim)
      quarter     (0.75–1.5):    filled head + stem      (crotchet)
      eighth      (0.375–0.75):  + single flag           (quaver)
      sixteenth   (< 0.375):     + double flag           (semiquaver)
    """
    if duration_beats >= 3.0:
        return ("○", 0, 0)
    if duration_beats >= 1.5:
        return ("○", 2, 0)
    if duration_beats >= 0.75:
        return ("●", 2, 0)
    if duration_beats >= 0.375:
        return ("●", 2, 1)
    return ("●", 2, 2)


def _draw_note_with_stem(
    frame: Frame,
    x: int,
    head_y: int,
    duration_beats: float,
    color: tuple[int, int, int],
    mid_line_y: int,
    panel_top: int,
    panel_bottom: int,
) -> None:
    """Draw a music-engraving-style note: head, stem, and flags.

    Duration is in BEATS so the rendered symbol stays correct across the
    full supported tempo range (20–400 BPM). Stem direction follows the
    standard rule: notes on or below the middle staff line stem up; notes
    above the middle line stem down. Stem cells and flag cells are clipped
    to the panel bounds so they never bleed into adjacent panels.
    """
    head, stem_h, n_flags = _note_rhythm(duration_beats)
    frame.put(x, head_y, head, color)
    if stem_h == 0:
        return

    stem_up = head_y >= mid_line_y
    # Inner stem cells (not the tip)
    inner = stem_h - (1 if n_flags > 0 else 0)
    for i in range(1, inner + 1):
        stem_y = head_y - i if stem_up else head_y + i
        if panel_top <= stem_y <= panel_bottom:
            frame.put(x, stem_y, "│", color)

    # Stem tip — flagged for eighth/sixteenth, plain otherwise
    tip_y = head_y - stem_h if stem_up else head_y + stem_h
    if not (panel_top <= tip_y <= panel_bottom):
        return
    if n_flags == 0:
        frame.put(x, tip_y, "│", color)
    elif n_flags == 1:
        frame.put(x, tip_y, "┐" if stem_up else "┘", color)
    else:
        # Sixteenth-or-shorter: heavier double-flag char
        frame.put(x, tip_y, "╗" if stem_up else "╝", color)


def _format_time(t: float) -> str:
    """Format seconds as mm:ss.s (zero-padded minutes, one-decimal sec)."""
    if t < 0:
        t = 0.0
    minutes = int(t // 60)
    seconds = t - minutes * 60
    return f"{minutes}:{seconds:04.1f}"


# ─── Frame builder ────────────────────────────────────────────────────
@dataclass
class _State:
    """Snapshot of song state at a moment in time, ready to render."""

    song: "Song"
    timelines: list[list[_Onset]]
    palette: list[tuple[int, int, int]]
    spectrum: np.ndarray
    spectrum_hop: float
    total_dur: float
    width: int
    height: int
    midi_lo: int = 60
    midi_hi: int = 72


def _draw_staff_panel(
    frame: Frame,
    state: _State,
    t_now: float,
    y0: int,
    panel_h: int,
    anim_phase: float,
) -> None:
    """Render a scrolling sheet-music staff into `frame` at row y0.

    Layout: clef glyph at left, 5 staff lines, bar lines at measure
    boundaries, notes from every track scrolling right→left, ledger lines
    for notes above or below the staff. The "now" column is the left edge
    of the staff body.
    """
    if panel_h < _STAFF_HEIGHT:
        return
    w = state.width
    song = state.song
    spb = 60.0 / max(song.bpm, 1.0)
    bar_seconds = song.time_sig[0] * spb

    # Reserve 3 cols on the left for the clef glyph, 2 cols on the right margin
    clef_x = 2
    staff_x = 5
    staff_w = max(10, w - staff_x - 2)

    window_sec = max(2.0, 4 * bar_seconds)
    sec_per_char = window_sec / staff_w

    n_lines = 5
    above_y = y0
    line_ys = [y0 + 1 + i for i in range(n_lines)]
    below_y = y0 + 1 + n_lines

    line_color = (110, 110, 130)
    bar_color = (140, 140, 170)
    now_color = (255, 200, 100)
    clef_color = (220, 220, 245)

    # 1. Five staff lines
    for ly in line_ys:
        for x in range(staff_w):
            frame.put(staff_x + x, ly, "─", line_color)

    # 2. Treble-clef glyph (ASCII fallback so monospace fonts cooperate)
    frame.put(clef_x, line_ys[1], "&", clef_color)
    frame.put(clef_x, line_ys[2], "&", clef_color)
    frame.put(clef_x, line_ys[3], "&", clef_color)

    # 3. Bar lines at measure boundaries inside the visible window
    if bar_seconds > 1e-6:
        first_bar_idx = math.floor(t_now / bar_seconds)
        last_bar_idx = math.ceil((t_now + window_sec) / bar_seconds)
        for bar_idx in range(first_bar_idx, last_bar_idx + 1):
            bar_t = bar_idx * bar_seconds
            col = (bar_t - t_now) / sec_per_char
            if 0 <= col < staff_w:
                bx = staff_x + int(col)
                for ly in line_ys:
                    frame.put(bx, ly, "│", bar_color)

    # 4. Now-line marker spanning the whole panel height (animated pulse)
    pulse = 0.85 + 0.15 * math.sin(anim_phase * 2 * math.pi * 2)
    pulsed_now = _scale_color(now_color, pulse)
    for ly in [above_y, *line_ys, below_y]:
        frame.put(staff_x, ly, "│", pulsed_now)

    # 5. Notes from every track sorted by start time, oldest first so newer
    #    notes draw on top of older ones at the same cell.
    all_notes: list[tuple[_Onset, int]] = []
    for ti, track_onsets in enumerate(state.timelines):
        for o in track_onsets:
            if o.midi is not None:
                all_notes.append((o, ti))
    all_notes.sort(key=lambda p: p[0].start)

    panel_top = above_y
    panel_bottom = below_y
    middle_line_y = line_ys[2]  # row corresponding to B4 (middle line)
    for o, ti in all_notes:
        col = (o.start - t_now) / sec_per_char
        if col < -2 or col >= staff_w:
            continue
        x = staff_x + int(round(col))
        if x < staff_x or x >= staff_x + staff_w:
            continue
        row = _staff_row(o.midi, state.midi_lo, state.midi_hi, _STAFF_HEIGHT)
        if row == 0:
            ny = above_y
            # Ledger line at the top staff line for high notes
            frame.put(x, line_ys[0], "─", line_color)
        elif row == _STAFF_HEIGHT - 1:
            ny = below_y
            frame.put(x, line_ys[-1], "─", line_color)
        else:
            ny = line_ys[row - 1]

        color = state.palette[ti] if ti < len(state.palette) else (200, 200, 200)
        sounding = o.start <= t_now < o.end
        if sounding:
            note_color = _scale_color(color, 1.25)
        elif o.end < t_now:
            note_color = _scale_color(color, 0.45)
        else:
            note_color = _scale_color(color, 0.95)
        _draw_note_with_stem(
            frame,
            x,
            ny,
            o.duration_beats,
            note_color,
            middle_line_y,
            panel_top,
            panel_bottom,
        )


def _build_frame(state: _State, t_now: float, anim_phase: float) -> Frame:
    """Compose one full frame for time `t_now`. anim_phase loops 0..1."""
    w, h = state.width, state.height
    frame = Frame(w, h)
    song = state.song

    # Draw side borders on every interior row first; corner glyphs and
    # horizontal separators below will overwrite where appropriate.
    for y in range(1, h - 1):
        frame.put(0, y, "│", (90, 90, 110))
        frame.put(w - 1, y, "│", (90, 90, 110))

    spb = 60.0 / max(song.bpm, 1.0)
    beat_now = t_now / spb
    # Use the time signature active at this beat (engine supports mid-song
    # changes via time_sig_map). Falls back to song.time_sig if unavailable.
    if hasattr(song, "time_sig_at"):
        ts_num, ts_den = song.time_sig_at(beat_now)
    else:
        ts_num, ts_den = song.time_sig
    bar_size = ts_num
    bar_now = int(beat_now // bar_size) + 1
    beat_in_bar = (beat_now % bar_size) + 1
    n_bars = max(1, int(song.total_beats / bar_size))

    # ── Header row ────────────────────────────────────────────────
    title = song.title[: max(10, w - 50)]
    # Animated gradient title — each char gets a hue offset that drifts
    for i, ch in enumerate(title):
        hue = (i / max(len(title), 1) + anim_phase) % 1.0
        frame.put(2 + i, 0, ch, _hsl_to_rgb(hue, 0.7, 0.65))

    info = f"  {song.bpm:.0f} BPM  bar {bar_now}/{n_bars}  beat {beat_in_bar:.1f}"
    timecode = f"{_format_time(t_now)} / {_format_time(state.total_dur)}"
    frame.text(w - len(timecode) - 2, 0, timecode, (180, 180, 180))
    info_x = 2 + len(title)
    if info_x + len(info) < w - len(timecode) - 4:
        frame.text(info_x, 0, info, (140, 140, 160))

    # ── Box top border ────────────────────────────────────────────
    frame.put(0, 0, "╭", (90, 90, 110))
    frame.put(w - 1, 0, "╮", (90, 90, 110))
    frame.hline(1, 1, w - 2, "─", (90, 90, 110))
    frame.put(0, 1, "│", (90, 90, 110))
    frame.put(w - 1, 1, "│", (90, 90, 110))

    # ── Live chord readout ───────────────────────────────────────
    # Drawn after the row-1 hline so the label wins over the dashes.
    # Pulses on every beat, names whatever is sounding right now.
    chord_label = _identify_chord(_currently_sounding_midis(state.timelines, t_now))
    if chord_label:
        beat_phase = beat_now % 1.0
        pulse = 1.1 - 0.4 * beat_phase  # bright at beat onset, dims toward next
        chord_color = _scale_color((255, 220, 130), max(0.5, min(1.3, pulse)))
        chord_str = f"♪ {chord_label} "
        cx = max(2, (w - len(chord_str)) // 2)
        # Replace surrounding dashes with spaces so the label reads cleanly
        frame.put(cx - 1, 1, " ", (90, 90, 110))
        frame.text(cx, 1, chord_str, chord_color)
        frame.put(cx + len(chord_str), 1, " ", (90, 90, 110))

    # ── Progress bar (row 2) ──────────────────────────────────────
    progress = t_now / max(state.total_dur, 1e-6)
    progress = max(0.0, min(1.0, progress))
    bar_w = w - 10
    filled = int(progress * bar_w)
    frame.put(0, 2, "│", (90, 90, 110))
    for i in range(bar_w):
        if i < filled:
            # Gradient sweep from cyan to magenta along the filled portion
            t = i / max(bar_w - 1, 1)
            hue = 0.55 - 0.4 * t  # cyan→pink
            frame.put(
                2 + i,
                2,
                "▓",
                _hsl_to_rgb(hue, 0.8, 0.55),
            )
        else:
            frame.put(2 + i, 2, "░", (60, 60, 70))
    pct = f"{int(progress * 100):3d}%"
    frame.text(w - len(pct) - 2, 2, pct, (200, 200, 200))
    frame.put(w - 1, 2, "│", (90, 90, 110))

    # ── Lane separator ────────────────────────────────────────────
    frame.put(0, 3, "├", (90, 90, 110))
    frame.hline(1, 3, w - 2, "─", (90, 90, 110))
    frame.put(w - 1, 3, "┤", (90, 90, 110))

    # ── Per-track lanes ───────────────────────────────────────────
    name_w = 9
    note_w = 7
    vu_w = 7
    pad_w = 6  # margins + dividers
    lane_w = max(10, w - name_w - note_w - vu_w - pad_w)
    window_sec = max(2.0, 4 * bar_size * spb)  # ~4 bars look-ahead
    sec_per_char = window_sec / lane_w

    lane_y_start = 4
    for ti, track in enumerate(song.tracks):
        y = lane_y_start + ti
        if y >= h - 8:
            break
        color = state.palette[ti] if ti < len(state.palette) else (200, 200, 200)
        frame.put(0, y, "│", (90, 90, 110))

        # Track name (truncated)
        nm = (track.name or track.instrument)[: name_w - 1]
        frame.text(2, y, nm.ljust(name_w - 1), (180, 180, 200))

        # Active or last-played note label, plus a "▶" marker if sounding
        active: _Onset | None = None
        last: _Onset | None = None
        for o in state.timelines[ti]:
            if o.start <= t_now < o.end:
                active = o
            if o.start <= t_now:
                last = o
            else:
                break
        if active is not None:
            frame.put(name_w + 1, y, "▶", _scale_color(color, 1.2))
            label = active.label[: note_w - 2]
            frame.text(name_w + 3, y, label, _scale_color(color, 1.1))
        elif last is not None:
            label = last.label[: note_w - 2]
            frame.text(name_w + 3, y, label, _scale_color(color, 0.55))
        else:
            frame.put(name_w + 3, y, "─", (80, 80, 90))

        # Lane left divider
        lane_x = name_w + note_w + 2
        frame.put(lane_x - 1, y, "│", (90, 90, 110))

        # Draw the piano-roll. Now-line is the leftmost column, future
        # extends to the right. Past notes scroll off the left.
        for o in state.timelines[ti]:
            x_start = (o.start - t_now) / sec_per_char
            x_end = (o.end - t_now) / sec_per_char
            if x_end < 0 or x_start >= lane_w:
                continue
            xs = max(0, int(math.floor(x_start)))
            xe = min(lane_w, int(math.ceil(x_end)))
            sounding = o.start <= t_now < o.end
            for x in range(xs, xe):
                if sounding and x == 0:
                    # Now-line flash: brighter, full block
                    pulse = 1.0 + 0.4 * math.sin(anim_phase * 2 * math.pi * 3)
                    frame.put(
                        lane_x + x,
                        y,
                        _NOW_FILL,
                        _scale_color(color, min(1.5, 0.9 + 0.3 * pulse)),
                    )
                elif sounding:
                    frame.put(lane_x + x, y, _NOW_FILL, _scale_color(color, 1.0))
                else:
                    frame.put(lane_x + x, y, _FUTURE_FILL, _scale_color(color, 0.6))

        # Now-line marker at column 0 if no note is sounding there
        if not active:
            frame.put(lane_x, y, "│", (140, 140, 160))

        # Sparkle burst on recent note onsets — fades over ~220ms
        sparkle = _sparkle_at_now(state.timelines[ti], t_now)
        if sparkle is not None:
            glyph, intensity = sparkle
            # Sparkles flicker around the now-line column with track-color tint
            spark_color = _scale_color(color, 1.0 + 0.4 * intensity)
            # Place at the now-line and one cell to its right when intensity is high
            frame.put(lane_x, y, glyph, spark_color)
            if intensity > 0.6 and lane_x + 1 < lane_x + lane_w:
                frame.put(
                    lane_x + 1,
                    y,
                    _SPARKLE_GLYPHS[-1],
                    _scale_color(color, 0.8 + 0.3 * intensity),
                )

        # Lane right divider
        frame.put(lane_x + lane_w, y, "│", (90, 90, 110))

        # VU meter: decaying envelope based on most recent onset
        vu = 0.0
        if last is not None:
            tau = max(0.25, last.end - last.start)
            elapsed = t_now - last.start
            vu = last.velocity * math.exp(-elapsed / tau)
            if active is not None:
                vu = max(vu, last.velocity)
        bar = _vu_chars(vu, vu_w - 1)
        for i, ch in enumerate(bar):
            shade = 0.5 + 0.5 * (i / max(vu_w - 2, 1))
            frame.put(lane_x + lane_w + 2 + i, y, ch, _scale_color(color, shade))

        frame.put(w - 1, y, "│", (90, 90, 110))

    # ── Sheet music panel ─────────────────────────────────────────
    eq_h = 6
    eq_y = h - eq_h - 2
    staff_top = lane_y_start + len(song.tracks)
    staff_panel_h = _STAFF_HEIGHT
    staff_avail = eq_y - staff_top - 1  # rows between last track and EQ sep
    show_staff = staff_avail >= staff_panel_h + 1
    if show_staff:
        # Staff separator with label
        sep_y = staff_top
        frame.put(0, sep_y, "├", (90, 90, 110))
        frame.hline(1, sep_y, w - 2, "─", (90, 90, 110))
        label = " sheet music "
        frame.text(
            (w - len(label)) // 2,
            sep_y,
            label,
            (160, 160, 200),
        )
        frame.put(w - 1, sep_y, "┤", (90, 90, 110))
        # Staff body
        _draw_staff_panel(frame, state, t_now, sep_y + 1, staff_panel_h, anim_phase)

    # ── EQ separator ──────────────────────────────────────────────
    if eq_y > lane_y_start + len(song.tracks):
        frame.put(0, eq_y, "├", (90, 90, 110))
        frame.hline(1, eq_y, w - 2, "─", (90, 90, 110))
        # EQ label centered in the separator
        label = " spectrum "
        frame.text(
            (w - len(label)) // 2,
            eq_y,
            label,
            (160, 160, 200),
        )
        frame.put(w - 1, eq_y, "┤", (90, 90, 110))

        # ── EQ bands ──────────────────────────────────────────────
        n_bands = state.spectrum.shape[1]
        spec_idx = min(state.spectrum.shape[0] - 1, int(t_now / state.spectrum_hop))
        col = state.spectrum[max(0, spec_idx)]
        # Render n_bands bars across the width, each ~bar_w_each cells wide
        avail = w - 4
        bar_w_each = max(1, avail // n_bands)
        eq_inner_h = eq_h
        for b in range(n_bands):
            level = float(col[b])
            bar_height_cells = level * eq_inner_h
            x0 = 2 + b * bar_w_each
            for row in range(eq_inner_h):
                y = eq_y + 1 + (eq_inner_h - 1 - row)
                if y >= h - 1:
                    continue
                cell_level = max(0.0, min(1.0, bar_height_cells - row))
                if cell_level <= 0:
                    continue
                # Color gradient from green (low band) to red (high band)
                hue = 0.33 - (b / max(n_bands - 1, 1)) * 0.33
                shade = 0.55 + 0.45 * cell_level
                color = _hsl_to_rgb(hue, 0.85, shade * 0.55)
                ch = _vbar_char(cell_level)
                for dx in range(bar_w_each):
                    if x0 + dx < w - 1:
                        frame.put(x0 + dx, y, ch, color)

        # EQ side borders
        for row in range(eq_h):
            y = eq_y + 1 + row
            if y < h - 1:
                frame.put(0, y, "│", (90, 90, 110))
                frame.put(w - 1, y, "│", (90, 90, 110))

    # ── Bottom border ─────────────────────────────────────────────
    frame.put(0, h - 1, "╰", (90, 90, 110))
    frame.put(w - 1, h - 1, "╯", (90, 90, 110))
    footer = " ↑ now → future "
    frame.hline(1, h - 1, w - 2, "─", (90, 90, 110))
    frame.text((w - len(footer)) // 2, h - 1, footer, (140, 140, 170))

    return frame


# ─── Audio playback (non-blocking) ────────────────────────────────────
def _start_audio_sounddevice(samples: np.ndarray, sample_rate: int) -> tuple[bool, object]:
    """Try to start non-blocking playback via sounddevice."""
    try:
        import sounddevice as sd

        sd.play(samples.astype(np.float32), samplerate=sample_rate)
        return True, sd
    except (ImportError, OSError, Exception):
        return False, None


def _start_audio_subprocess(
    samples: np.ndarray, sample_rate: int
) -> tuple[subprocess.Popen | None, Path | None]:
    """Fallback: write a temp WAV and Popen a system player."""
    from .export import export_wav

    player = None
    for cmd in ("afplay", "aplay", "ffplay", "paplay"):
        if shutil.which(cmd):
            player = cmd
            break
    if player is None:
        return None, None
    tmp_path = Path(tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name)
    export_wav(samples, tmp_path, sample_rate)
    args = [player, str(tmp_path)]
    if player == "ffplay":
        args = [player, "-nodisp", "-autoexit", str(tmp_path)]
    proc = subprocess.Popen(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return proc, tmp_path


# ─── Public entry point ───────────────────────────────────────────────
def play_visual(
    song: "Song",
    bpm: float | None = None,
    fps: int = 30,
    audio: bool = True,
    width: int | None = None,
    height: int | None = None,
) -> None:
    """Render `song` and play it with a real-time CLI visualizer.

    Args:
        song:   Song to render.
        bpm:    Optional BPM override applied before rendering.
        fps:    Frames per second for the visualizer (default 30).
        audio: If False, run the visualization without producing sound
                (useful for screencaps or when no audio device exists).
        width:  Force terminal width (default: detect).
        height: Force terminal height (default: detect).
    """
    from .synth import Synth

    if bpm is not None:
        song.bpm = bpm

    print(f"  Rendering '{song.title}' — {song.duration_sec:.1f}s @ {song.bpm} BPM ...")
    t0 = time.monotonic()
    samples = Synth(sample_rate=song.sample_rate).render_song(song)
    print(f"  Rendered in {time.monotonic() - t0:.1f}s. Visualizing ...")

    timelines, total_dur = _build_timeline(song)
    palette = _track_palette(len(song.tracks))
    spectrum_hop = 0.05
    spectrum = _precompute_spectrum(samples, song.sample_rate, hop_sec=spectrum_hop)
    midi_lo, midi_hi = _midi_range_from_timelines(timelines)

    # Terminal sizing
    if width is None or height is None:
        try:
            term_size = os.get_terminal_size()
            term_w = width or term_size.columns
            term_h = height or term_size.lines
        except OSError:
            term_w = width or 100
            term_h = height or 30
    else:
        term_w = width
        term_h = height
    term_w = max(60, min(180, term_w))
    # header(3) + tracks(N) + staff_sep(1) + staff(7) + eq_sep(1) + eq(6) + footer(2)
    needed_h = 4 + len(song.tracks) + 1 + _STAFF_HEIGHT + 1 + 6 + 2
    term_h = max(needed_h, min(60, term_h))

    state = _State(
        song=song,
        timelines=timelines,
        palette=palette,
        spectrum=spectrum,
        spectrum_hop=spectrum_hop,
        total_dur=total_dur,
        width=term_w,
        height=term_h,
        midi_lo=midi_lo,
        midi_hi=midi_hi,
    )

    use_color = _supports_color()
    if not use_color:
        # Without ANSI, just print the rendered duration and return; the
        # visualizer is a TTY-only experience.
        print("  (no TTY color support detected — falling back to silent render)")
        if audio:
            from .playback import play as _play

            _play(song)
        return

    # Start audio
    sd_started = False
    sd_module: object | None = None
    proc: subprocess.Popen | None = None
    tmp_path: Path | None = None
    if audio:
        sd_started, sd_module = _start_audio_sounddevice(samples, song.sample_rate)
        if not sd_started:
            proc, tmp_path = _start_audio_subprocess(samples, song.sample_rate)

    # Restore-on-exit handlers (cursor, alt-screen, audio teardown)
    def _cleanup() -> None:
        sys.stdout.write(SHOW_CURSOR + ALT_SCREEN_OFF)
        sys.stdout.flush()
        if sd_started and sd_module is not None:
            try:
                sd_module.stop()  # type: ignore[attr-defined]
            except Exception:
                pass
        if proc is not None:
            try:
                proc.terminate()
                proc.wait(timeout=1.0)
            except Exception:
                pass
        if tmp_path is not None:
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                pass

    prev_handler = signal.getsignal(signal.SIGINT)

    def _on_sigint(_sig, _frame) -> None:  # noqa: ANN001
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, _on_sigint)
    sys.stdout.write(ALT_SCREEN_ON + HIDE_CURSOR + CLEAR_SCREEN + HOME)
    sys.stdout.flush()

    start_time = time.monotonic()
    frame_period = 1.0 / max(1, fps)
    try:
        while True:
            t_now = time.monotonic() - start_time
            if t_now >= total_dur + 0.5:
                break
            anim = (t_now * 0.25) % 1.0
            frame = _build_frame(state, t_now, anim)
            sys.stdout.write(HOME + frame.render())
            sys.stdout.flush()
            # Sleep to next frame boundary, accounting for render overhead
            target = start_time + (math.floor((t_now) / frame_period) + 1) * frame_period
            remaining = target - time.monotonic()
            if remaining > 0:
                time.sleep(remaining)
    except KeyboardInterrupt:
        pass
    finally:
        signal.signal(signal.SIGINT, prev_handler)
        _cleanup()
        # Block until audio actually ends so the song doesn't get cut short
        if sd_started and sd_module is not None:
            try:
                sd_module.wait()  # type: ignore[attr-defined]
            except Exception:
                pass
        elif proc is not None:
            try:
                proc.wait(timeout=max(0.0, total_dur - (time.monotonic() - start_time)))
            except Exception:
                pass
        print("  Done.")
