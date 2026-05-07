"""ASCII tracker — grid-based notation, inspired by Switch Angel's Strudel setup.

Phase 2 of the Strudel integration plan (`docs/strudel_integration.md`).

The format is a multi-line text grid where rows are time steps and columns are
voices. Switch Angel uses something similar live in Strudel for trance
performances; this module brings the idea into code-music so a song can be
written as a single legible grid string and rendered through the existing
Synth pipeline.

Example::

    from code_music.ascii_tracker import AsciiTracker

    grid = '''
              KICK SNARE HAT  BASS
        00 |  C2   ...   C5   F1
        01 |  ...  ...   ...  ...
        02 |  ...  D2    C5   ...
        03 |  ...  ...   C5   ...
        04 |  C2   ...   C5   F1
        05 |  ...  ...   ...  D5
        06 |  ...  D2    C5   ...
        07 |  ...  ...   C5   Eb5
    '''

    tracker = AsciiTracker.from_string(grid)
    song = tracker.to_song(
        bpm=128,
        instruments={
            "KICK": "drums_kick",
            "SNARE": "drums_snare",
            "HAT": "drums_hat",
            "BASS": "bass",
        },
    )

Cell formats inside the grid:

- ``~`` or ``-`` or ``...`` -- rest / continue (no new note this step)
- ``C2``, ``F#3``, ``Bb4`` -- a single pitched note
- ``C2,E2,G2`` -- a chord (comma-separated literal pitches; no spaces)
- ``C2:80`` -- note with explicit MIDI velocity (0..127). ``C2:0.6`` is also
  accepted as a 0..1 fraction.

Lines starting with ``#`` are treated as comments and ignored.
A leading ``NN |`` step-index column is optional; both ``00 | C2 ...`` and
``C2 ...`` are valid rows.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .engine import Note, PolyphonicTrack, Song
from .pattern import Pattern, _parse_note_spec

DEFAULT_STEP_DURATION: float = 0.25
DEFAULT_VELOCITY: float = 0.8
REST_TOKENS: frozenset[str] = frozenset({"~", "-", "...", "..", ".", ""})

_NOTE_TOKEN_RE = re.compile(r"^([A-Ga-g][#b]?\d+)(?::(\d+(?:\.\d+)?))?$")


@dataclass(frozen=True)
class Cell:
    """One parsed cell. Rest cells have an empty ``notes`` tuple."""

    notes: tuple[Note, ...] = field(default_factory=tuple)

    @property
    def is_rest(self) -> bool:
        return not self.notes


@dataclass
class AsciiTracker:
    """Parsed tracker grid.

    Attributes:
        column_names: Voice column labels in left-to-right order.
        rows:         List of rows, each a list of ``Cell`` (one per column).
    """

    column_names: list[str]
    rows: list[list[Cell]]

    @classmethod
    def from_string(cls, grid: str) -> "AsciiTracker":
        """Parse a multi-line tracker grid into an :class:`AsciiTracker`."""
        column_names, raw_rows = _parse_grid(grid)
        rows: list[list[Cell]] = []
        for row in raw_rows:
            if len(row) != len(column_names):
                raise ValueError(
                    f"row {row!r} has {len(row)} cells but header declares "
                    f"{len(column_names)} columns"
                )
            rows.append([_parse_cell(cell) for cell in row])
        return cls(column_names=column_names, rows=rows)

    @property
    def num_steps(self) -> int:
        """Number of time steps in the grid."""
        return len(self.rows)

    @property
    def num_voices(self) -> int:
        """Number of voice columns in the grid."""
        return len(self.column_names)

    def cells_for(self, column: str) -> list[Cell]:
        """Return the column of cells for the named voice."""
        try:
            idx = self.column_names.index(column)
        except ValueError as exc:
            raise KeyError(f"unknown column {column!r}; have {self.column_names}") from exc
        return [row[idx] for row in self.rows]

    def to_patterns(self) -> dict[str, Pattern]:
        """Return one ``Pattern`` per voice, single-note only.

        Cells with chord content are reduced to the lowest note (which keeps the
        result a clean monophonic pattern). For full chord rendering, use
        :meth:`to_song` instead.
        """
        out: dict[str, Pattern] = {}
        for col, name in enumerate(self.column_names):
            events: list[str | None] = []
            for row in self.rows:
                cell = row[col]
                if cell.is_rest:
                    events.append(None)
                else:
                    n = min(cell.notes, key=lambda x: x.midi or 0)
                    events.append(_note_to_spec(n))
            out[name] = Pattern(events)
        return out

    def to_song(
        self,
        bpm: float = 128.0,
        step_duration: float = DEFAULT_STEP_DURATION,
        instruments: dict[str, str] | None = None,
        title: str = "AsciiTracker Song",
    ) -> Song:
        """Render the tracker as a :class:`Song` with one polyphonic track per voice.

        Args:
            bpm:           Song tempo.
            step_duration: Beats per row. Default 0.25 (a sixteenth note).
            instruments:   Map of column name -> instrument preset. Columns
                           without an entry default to ``pad``.
            title:         Song title.
        """
        instruments = instruments or {}
        song = Song(title=title, bpm=bpm)
        for col, name in enumerate(self.column_names):
            instrument = instruments.get(name, "pad")
            track = song.add_polytrack(PolyphonicTrack(name=name, instrument=instrument))
            for step, row in enumerate(self.rows):
                cell = row[col]
                if cell.is_rest:
                    continue
                at = step * step_duration
                for note in cell.notes:
                    track.add(_with_duration(note, step_duration), at=at)
        return song

    def to_string(self) -> str:
        """Render the tracker back to a normalised grid string.

        Round-trips with :meth:`from_string` for any tracker built from
        ``from_string``. Velocities are preserved using the ``Pitch:vel`` form
        when not equal to the default.
        """
        widths = [max(len(name), 4) for name in self.column_names]
        for row in self.rows:
            for col, cell in enumerate(row):
                widths[col] = max(widths[col], len(_format_cell(cell)))
        index_width = max(2, len(str(max(self.num_steps - 1, 0))))
        lines: list[str] = []
        header = " " * (index_width + 3) + "  ".join(
            name.ljust(widths[i]) for i, name in enumerate(self.column_names)
        )
        lines.append(header.rstrip())
        for step, row in enumerate(self.rows):
            cells = "  ".join(_format_cell(cell).ljust(widths[i]) for i, cell in enumerate(row))
            lines.append(f"{step:0{index_width}d} | {cells}".rstrip())
        return "\n".join(lines) + "\n"


def tracker(grid: str) -> AsciiTracker:
    """Convenience constructor: ``tracker(grid)`` is :meth:`AsciiTracker.from_string`."""
    return AsciiTracker.from_string(grid)


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _parse_grid(grid: str) -> tuple[list[str], list[list[str]]]:
    """Strip comments + blank lines; return ``(column_names, rows_of_cells)``.

    Each row's cells are the whitespace-separated tokens after any leading
    ``NN |`` step-index column.
    """
    raw_lines = [
        line
        for line in grid.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not raw_lines:
        raise ValueError("empty tracker grid")
    header_tokens = _strip_index_column(raw_lines[0]).split()
    if not header_tokens:
        raise ValueError("tracker header has no column names")
    rows = [_strip_index_column(line).split() for line in raw_lines[1:]]
    return header_tokens, rows


def _strip_index_column(line: str) -> str:
    """Drop a leading ``NN |`` step-index prefix if present."""
    stripped = line.strip()
    m = re.match(r"^\d+\s*\|\s*(.*)$", stripped)
    if m:
        return m.group(1)
    return stripped


def _parse_cell(cell: str) -> Cell:
    """Parse one cell token into a :class:`Cell`."""
    token = cell.strip()
    if token.lower() in REST_TOKENS or set(token) <= {"."}:
        return Cell()
    parts = token.split(",") if "," in token else [token]
    notes: list[Note] = []
    for part in parts:
        notes.append(_parse_note_token(part.strip()))
    return Cell(notes=tuple(notes))


def _parse_note_token(token: str) -> Note:
    """Parse a single note token, optionally suffixed with ``:velocity``."""
    m = _NOTE_TOKEN_RE.match(token)
    if not m:
        raise ValueError(f"cannot parse cell note {token!r}")
    pitch_text, vel_text = m.group(1), m.group(2)
    pitch, octave = _parse_note_spec(pitch_text)
    velocity = _parse_velocity(vel_text)
    return Note(pitch=pitch, octave=octave, velocity=velocity)


def _parse_velocity(text: str | None) -> float:
    """Convert ``"80"`` (MIDI 0-127) or ``"0.6"`` (fraction) to a 0-1 float."""
    if text is None:
        return DEFAULT_VELOCITY
    value = float(text)
    if value <= 1.0:
        return max(0.0, value)
    return min(1.0, value / 127.0)


def _with_duration(note: Note, duration: float) -> Note:
    """Return a copy of ``note`` with the given duration."""
    return Note(
        pitch=note.pitch,
        octave=note.octave,
        duration=duration,
        velocity=note.velocity,
        articulation=note.articulation,
    )


def _note_to_spec(note: Note) -> str:
    """Format a :class:`Note` back to a ``C2``-style spec."""
    if note.pitch is None:
        return "~"
    if isinstance(note.pitch, int):
        from .engine import NOTE_NAMES, midi_to_freq  # noqa: F401  (NOTE_NAMES needed)

        midi = note.pitch
        return f"{NOTE_NAMES[midi % 12]}{midi // 12 - 1}"
    return f"{note.pitch}{note.octave}"


def _format_cell(cell: Cell) -> str:
    """Render a :class:`Cell` back to its tracker-string form."""
    if cell.is_rest:
        return "..."
    parts: list[str] = []
    for note in cell.notes:
        spec = _note_to_spec(note)
        if abs(note.velocity - DEFAULT_VELOCITY) > 1e-6:
            parts.append(f"{spec}:{int(round(note.velocity * 127))}")
        else:
            parts.append(spec)
    return ",".join(parts)
