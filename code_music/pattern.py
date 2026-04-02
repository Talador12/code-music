"""Pattern language — TidalCycles-inspired pattern transforms in Python.

Build note sequences from mini-notation strings, transform them with
reverse/every/degrade, layer polyrhythms, and convert to Tracks.

Example::

    from code_music.pattern import Pattern

    p = Pattern("C4 E4 G4 C5")
    p.reverse().every(4, lambda x: x.reverse())
    tr.extend(p.to_notes(duration=0.5))
"""

from __future__ import annotations

import random
import re
from typing import Callable

from .engine import Note


class Pattern:
    """A sequence of note events with functional transforms.

    Create from a mini-notation string or a list of note specs.
    Supports chaining transforms that return new Pattern instances (immutable).

    Mini-notation syntax::

        "C4 E4 G4"           → three notes
        "C4 ~ E4"            → note, rest, note
        "[C4 E4] G4"         → C4+E4 share one slot, G4 gets one slot
        "C4*3"               → C4 repeated 3 times
        "C4?"                → C4 with 50% probability
    """

    def __init__(self, source: str | list[str | None] = "") -> None:
        if isinstance(source, str):
            self._events = _parse_mini(source)
        else:
            self._events = list(source)

    @property
    def events(self) -> list[str | None]:
        """Raw event list. None = rest, str = note spec like 'C4'."""
        return list(self._events)

    def __len__(self) -> int:
        return len(self._events)

    def __repr__(self) -> str:
        display = " ".join("~" if e is None else e for e in self._events[:16])
        if len(self._events) > 16:
            display += " ..."
        return f"Pattern({display!r}, len={len(self._events)})"

    # -- Transforms --------------------------------------------------------

    def reverse(self) -> "Pattern":
        """Reverse the pattern."""
        return Pattern(list(reversed(self._events)))

    def rotate(self, n: int = 1) -> "Pattern":
        """Rotate the pattern by n steps."""
        if not self._events:
            return Pattern([])
        n = n % len(self._events)
        return Pattern(self._events[n:] + self._events[:n])

    def every(self, n: int, fn: Callable[["Pattern"], "Pattern"]) -> "Pattern":
        """Apply fn to every nth repetition when cycling.

        Returns a pattern that is n repetitions long, with fn applied to
        the nth one.
        """
        reps: list[str | None] = []
        for i in range(n):
            if i == n - 1:
                reps.extend(fn(self)._events)
            else:
                reps.extend(self._events)
        return Pattern(reps)

    def degrade(self, probability: float = 0.5, seed: int | None = None) -> "Pattern":
        """Randomly replace events with rests.

        Args:
            probability: Chance each event survives (0-1).
            seed:        Random seed for reproducibility.
        """
        rng = random.Random(seed)
        return Pattern([e if rng.random() < probability else None for e in self._events])

    def fast(self, factor: int) -> "Pattern":
        """Repeat the pattern `factor` times (speed up)."""
        return Pattern(self._events * factor)

    def slow(self, factor: int) -> "Pattern":
        """Stretch each event by inserting rests (slow down)."""
        result: list[str | None] = []
        for e in self._events:
            result.append(e)
            result.extend([None] * (factor - 1))
        return Pattern(result)

    def choose(self, seed: int | None = None) -> "Pattern":
        """Shuffle the pattern randomly."""
        rng = random.Random(seed)
        events = list(self._events)
        rng.shuffle(events)
        return Pattern(events)

    # -- Combination -------------------------------------------------------

    def cat(self, other: "Pattern") -> "Pattern":
        """Concatenate two patterns."""
        return Pattern(self._events + other._events)

    @staticmethod
    def polymeter(*patterns: "Pattern") -> "Pattern":
        """Layer patterns of different lengths — each cycles at its own rate.

        The result length is the LCM of all pattern lengths, with each
        pattern repeating to fill the full cycle.
        """
        if not patterns:
            return Pattern([])
        from math import gcd

        lengths = [len(p) for p in patterns]
        total = lengths[0]
        for length in lengths[1:]:
            total = total * length // gcd(total, length)

        result: list[str | None] = [None] * total
        for pat in patterns:
            if not pat._events:
                continue
            for i in range(total):
                event = pat._events[i % len(pat._events)]
                if event is not None:
                    result[i] = event
        return Pattern(result)

    # -- Conversion --------------------------------------------------------

    def to_notes(
        self,
        duration: float = 0.5,
        default_octave: int = 4,
        velocity: float = 0.8,
    ) -> list[Note]:
        """Convert pattern events to a list of Notes.

        Args:
            duration:       Duration of each step in beats.
            default_octave: Octave if not specified in the event string.
            velocity:       Note velocity.
        """
        notes: list[Note] = []
        for event in self._events:
            if event is None:
                notes.append(Note.rest(duration))
            else:
                pitch, octave = _parse_note_spec(event, default_octave)
                notes.append(Note(pitch, octave, duration, velocity=velocity))
        return notes


# ---------------------------------------------------------------------------
# Mini-notation parser
# ---------------------------------------------------------------------------

_NOTE_RE = re.compile(r"^([A-Ga-g][#b]?)(\d+)?$")


def _parse_note_spec(spec: str, default_octave: int = 4) -> tuple[str, int]:
    """Parse 'C#4' → ('C#', 4) or 'E' → ('E', default_octave)."""
    m = _NOTE_RE.match(spec.strip())
    if not m:
        raise ValueError(f"Cannot parse note spec: {spec!r}")
    raw = m.group(1)
    pitch = raw[0].upper() + raw[1:] if len(raw) > 1 else raw.upper()
    octave = int(m.group(2)) if m.group(2) else default_octave
    return pitch, octave


def _parse_mini(source: str) -> list[str | None]:
    """Parse mini-notation string into event list.

    Supports:
        C4 E4 G4     → ["C4", "E4", "G4"]
        C4 ~ E4      → ["C4", None, "E4"]
        [C4 E4] G4   → ["C4", "E4", "G4"] (subdivisions flattened)
        C4*3          → ["C4", "C4", "C4"]
        C4?           → ["C4"] or [None] (50% chance, resolved at parse time)
    """
    if not source.strip():
        return []

    tokens = _tokenize(source)
    events: list[str | None] = []
    for tok in tokens:
        if tok == "~":
            events.append(None)
        elif tok.endswith("?"):
            base = tok[:-1]
            events.append(base if random.random() < 0.5 else None)
        elif "*" in tok:
            parts = tok.split("*", 1)
            base = parts[0]
            count = int(parts[1]) if parts[1].isdigit() else 1
            events.extend([base] * count)
        else:
            events.append(tok)
    return events


def _tokenize(source: str) -> list[str]:
    """Tokenize mini-notation, handling brackets."""
    tokens: list[str] = []
    i = 0
    s = source.strip()
    while i < len(s):
        if s[i] == "[":
            # Find matching ]
            depth = 1
            j = i + 1
            while j < len(s) and depth > 0:
                if s[j] == "[":
                    depth += 1
                elif s[j] == "]":
                    depth -= 1
                j += 1
            inner = s[i + 1 : j - 1]
            # Recursively tokenize inner content (subdivision → flattened)
            tokens.extend(_tokenize(inner))
            i = j
        elif s[i] in (" ", "\t", "\n"):
            i += 1
        else:
            j = i
            while j < len(s) and s[j] not in (" ", "\t", "\n", "[", "]"):
                j += 1
            tokens.append(s[i:j])
            i = j
    return tokens
