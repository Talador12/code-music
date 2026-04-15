"""Rhythm game chart exporters.

Export any Song to playable charts for StepMania (DDR) and Clone Hero
(Guitar Hero). We know where every note is. We know the BPM. We know
the difficulty. The rest is just formatting.

Formats:
    StepMania (.sm)  - DDR, ITG, StepMania 5. Arrow charts.
    Clone Hero (.chart) - Guitar Hero, Clone Hero. Fret charts.

The chart generator analyzes the Song's note onsets and maps them to
game inputs based on difficulty. Higher difficulty = more notes, faster
patterns, more complex arrow/fret combinations.

Example::

    from code_music import Song
    from code_music.rhythm_game import export_stepmania, export_clone_hero

    song = Song(title="My Track", bpm=128)
    # ... add tracks ...

    # DDR chart
    export_stepmania(song, "my_track.sm", difficulty="hard")

    # Guitar Hero / Clone Hero chart
    export_clone_hero(song, "my_track.chart", difficulty="expert")
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Sequence

from .engine import Beat, Chord, Note, Song, Track


# ---------------------------------------------------------------------------
# Onset extraction - find where the notes are
# ---------------------------------------------------------------------------


def _extract_onsets(song: Song) -> list[dict]:
    """Extract note onset times from a Song.

    Returns a list of dicts with beat position, velocity, pitch info,
    and which track it came from. This is the raw material for chart
    generation.
    """
    onsets: list[dict] = []
    for track in song.tracks:
        beat_pos = 0.0
        for beat in track.beats:
            event = beat.event
            if event is None:
                beat_pos += 1.0
                continue
            dur = getattr(event, "duration", 1.0)
            if isinstance(event, Note) and event.pitch is not None:
                onsets.append(
                    {
                        "beat": beat_pos,
                        "duration": dur,
                        "velocity": event.velocity,
                        "midi": event.midi,
                        "track": track.name,
                        "instrument": track.instrument,
                    }
                )
            elif isinstance(event, Chord):
                onsets.append(
                    {
                        "beat": beat_pos,
                        "duration": dur,
                        "velocity": getattr(event, "velocity", 0.8),
                        "midi": None,
                        "track": track.name,
                        "instrument": track.instrument,
                        "is_chord": True,
                    }
                )
            beat_pos += dur
    onsets.sort(key=lambda o: o["beat"])
    return onsets


# ---------------------------------------------------------------------------
# Difficulty scaling
# ---------------------------------------------------------------------------

# What fraction of onsets to include at each difficulty level
_DIFFICULTY_FRACTION = {
    "beginner": 0.15,
    "easy": 0.3,
    "medium": 0.5,
    "hard": 0.75,
    "expert": 1.0,
}

# StepMania difficulty names mapped to internal levels
_SM_DIFFICULTY_MAP = {
    "beginner": "Beginner",
    "easy": "Easy",
    "medium": "Medium",
    "hard": "Hard",
    "expert": "Challenge",
}

# Clone Hero difficulty names
_CH_DIFFICULTY_MAP = {
    "beginner": "Easy",
    "easy": "Easy",
    "medium": "Medium",
    "hard": "Hard",
    "expert": "Expert",
}


def _filter_onsets_by_difficulty(
    onsets: list[dict],
    difficulty: str,
    seed: int = 42,
) -> list[dict]:
    """Filter onsets based on difficulty level.

    Lower difficulty = fewer notes. We keep the loudest, most
    rhythmically important notes and drop the quieter, faster ones.
    """
    frac = _DIFFICULTY_FRACTION.get(difficulty, 1.0)
    if frac >= 1.0:
        return list(onsets)

    # Sort by importance: velocity * inverse_density
    # High velocity notes on strong beats survive the cut
    scored = []
    for i, o in enumerate(onsets):
        # Strong beats (on integer positions) score higher
        beat_strength = 1.0 if o["beat"] % 1.0 < 0.01 else 0.5
        score = o["velocity"] * beat_strength
        scored.append((score, i, o))

    scored.sort(key=lambda x: x[0], reverse=True)
    n_keep = max(1, int(len(scored) * frac))
    kept = sorted(scored[:n_keep], key=lambda x: x[1])
    return [k[2] for k in kept]


# ---------------------------------------------------------------------------
# StepMania (.sm) exporter
# ---------------------------------------------------------------------------


def export_stepmania(
    song: Song,
    path: str,
    difficulty: str = "hard",
    mode: str = "dance-single",
    track_name: str | None = None,
    quantize: int = 16,
) -> str:
    """Export a Song as a StepMania chart (.sm file).

    StepMania is the open-source DDR engine. The .sm format stores
    charts as measures of arrow data. Each row is a time position,
    each column is an arrow (Left, Down, Up, Right for dance-single).

    The generator maps note pitches to arrow directions and creates
    patterns that flow naturally for the difficulty level.

    Args:
        song:        Source Song.
        path:        Output file path.
        difficulty:  "beginner", "easy", "medium", "hard", "expert".
        mode:        Game mode ("dance-single" = 4 arrows,
                     "dance-double" = 8 arrows).
        track_name:  Which track to chart (None = all tracks merged).
        quantize:    Rows per measure (4=quarter, 8=8th, 16=16th, etc.)

    Returns:
        Path of the written file.
    """
    out = Path(path).with_suffix(".sm")
    out.parent.mkdir(parents=True, exist_ok=True)

    onsets = _extract_onsets(song)
    if track_name:
        onsets = [o for o in onsets if o["track"] == track_name]
    onsets = _filter_onsets_by_difficulty(onsets, difficulty)

    num, den = song.time_sig
    beats_per_measure = num * 4 / den
    total_beats = max((o["beat"] + o["duration"] for o in onsets), default=4.0)
    n_measures = max(1, math.ceil(total_beats / beats_per_measure))
    rows_per_measure = quantize

    n_arrows = 4 if "single" in mode else 8
    sm_diff = _SM_DIFFICULTY_MAP.get(difficulty, "Hard")

    # Map note onsets to arrow columns
    # Strategy: cycle through arrows based on pitch, with variety
    chart_rows: dict[int, list[int]] = {}  # global_row -> list of arrow columns

    for onset in onsets:
        beat = onset["beat"]
        row_in_song = round(beat / beats_per_measure * rows_per_measure)
        measure = int(beat / beats_per_measure)
        global_row = measure * rows_per_measure + (row_in_song % rows_per_measure)

        # Map pitch to arrow direction
        midi = onset.get("midi")
        if midi is not None:
            arrow = midi % n_arrows
        else:
            arrow = int(beat * 3) % n_arrows

        if global_row not in chart_rows:
            chart_rows[global_row] = []
        if arrow not in chart_rows[global_row]:
            chart_rows[global_row].append(arrow)

    # Build the .sm file
    lines = [
        f"#TITLE:{song.title};",
        f"#ARTIST:{getattr(song, 'composer', 'code-music')};",
        f"#MUSIC:{Path(path).stem}.ogg;",
        f"#OFFSET:0.000;",
        f"#BPMS:0.000={song.bpm:.3f};",
        f"#STOPS:;",
        "",
        "//--- {mode} - {sm_diff} ---",
        f"#NOTES:",
        f"     {mode}:",
        f"     :",
        f"     {sm_diff}:",
        f"     {_difficulty_to_meter(difficulty)}:",
        f"     :",
    ]

    # Write measures
    for m in range(n_measures):
        measure_lines = []
        for row in range(rows_per_measure):
            global_row = m * rows_per_measure + row
            arrows = chart_rows.get(global_row, [])
            row_str = ""
            for col in range(n_arrows):
                row_str += "1" if col in arrows else "0"
            measure_lines.append(row_str)

        lines.extend(measure_lines)
        if m < n_measures - 1:
            lines.append(",")
        else:
            lines.append(";")

    out.write_text("\n".join(lines) + "\n")
    return str(out)


# ---------------------------------------------------------------------------
# Clone Hero (.chart) exporter
# ---------------------------------------------------------------------------


def export_clone_hero(
    song: Song,
    path: str,
    difficulty: str = "expert",
    track_name: str | None = None,
    resolution: int = 192,
) -> str:
    """Export a Song as a Clone Hero chart (.chart file).

    Clone Hero is the open-source Guitar Hero engine. The .chart format
    uses tick positions and fret numbers (0=green through 4=orange for
    5-fret, or 0-5 for 6-fret).

    The generator maps pitches to fret positions. Higher pitches get
    higher frets. Chords map to multiple simultaneous frets.

    Args:
        song:        Source Song.
        path:        Output file path.
        difficulty:  "beginner", "easy", "medium", "hard", "expert".
        track_name:  Which track to chart (None = all tracks merged).
        resolution:  Ticks per quarter note (192 = standard).

    Returns:
        Path of the written file.
    """
    out = Path(path).with_suffix(".chart")
    out.parent.mkdir(parents=True, exist_ok=True)

    onsets = _extract_onsets(song)
    if track_name:
        onsets = [o for o in onsets if o["track"] == track_name]
    onsets = _filter_onsets_by_difficulty(onsets, difficulty)

    ch_diff = _CH_DIFFICULTY_MAP.get(difficulty, "Expert")

    lines = [
        "[Song]",
        "{",
        f'  Name = "{song.title}"',
        f'  Artist = "{getattr(song, "composer", "code-music")}"',
        f"  Resolution = {resolution}",
        f"  Offset = 0",
        "}",
        "[SyncTrack]",
        "{",
        f"  0 = TS {song.time_sig[0]} {int(math.log2(song.time_sig[1]))}",
        f"  0 = B {int(song.bpm * 1000)}",
        "}",
        "[Events]",
        "{",
        "}",
        f"[{ch_diff}Single]",
        "{",
    ]

    # Map onsets to fret numbers
    # Strategy: map MIDI pitch range to 5 frets
    midi_values = [o["midi"] for o in onsets if o.get("midi") is not None]
    if midi_values:
        min_midi = min(midi_values)
        max_midi = max(midi_values)
        midi_range = max(1, max_midi - min_midi)
    else:
        min_midi = 60
        midi_range = 24

    for onset in onsets:
        tick = int(onset["beat"] * resolution)
        dur_ticks = max(0, int(onset["duration"] * resolution) - 1)

        midi = onset.get("midi")
        if midi is not None:
            # Map pitch to fret 0-4
            fret = min(4, int((midi - min_midi) / midi_range * 5))
        else:
            # Chords get multiple frets based on beat position
            fret = int(onset["beat"] * 2) % 5

        is_chord = onset.get("is_chord", False)
        if is_chord:
            # Chord = two or three frets at once
            frets = [fret, (fret + 2) % 5]
            for f in frets:
                lines.append(f"  {tick} = N {f} {dur_ticks}")
        else:
            lines.append(f"  {tick} = N {fret} {dur_ticks}")

    lines += [
        "}",
    ]

    out.write_text("\n".join(lines) + "\n")
    return str(out)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _difficulty_to_meter(difficulty: str) -> int:
    """Map difficulty name to StepMania meter (1-13 scale)."""
    return {
        "beginner": 1,
        "easy": 3,
        "medium": 6,
        "hard": 9,
        "expert": 12,
    }.get(difficulty, 8)


def list_difficulties() -> list[str]:
    """Return available difficulty levels."""
    return ["beginner", "easy", "medium", "hard", "expert"]
