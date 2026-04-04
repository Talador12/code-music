"""theory.serial — tone rows, pitch class sets, post-tonal operations."""

from __future__ import annotations

from ._core import _NOTE_NAMES, _semi



# ---------------------------------------------------------------------------
# Multi-tonic / post-tonal systems (v64.0)
# ---------------------------------------------------------------------------


def tone_row(pitches: list[str] | None = None, seed: int | None = None) -> list[int]:
    """Create a 12-tone row (ordered set of all 12 pitch classes).

    Schoenberg's method: use all 12 notes before repeating any.
    The row is the DNA of the entire composition — every melody,
    harmony, and bass line derives from it.

    Args:
        pitches: Optional explicit ordering as note names. If None,
                 generates a random permutation.
        seed:    Random seed (only used when pitches is None).

    Returns:
        List of 12 integers (pitch classes 0–11).
    """
    if pitches is not None:
        return [_semi(p) for p in pitches]
    import random as _rng

    rng = _rng.Random(seed)
    row = list(range(12))
    rng.shuffle(row)
    return row



def row_transforms(row: list[int]) -> dict[str, list[int]]:
    """Generate the four standard transforms of a 12-tone row.

    Every serial composition uses these four forms — the prime (P),
    retrograde (R), inversion (I), and retrograde-inversion (RI).
    Webern built entire symphonies from just these four.

    Args:
        row: The prime row (list of 12 pitch classes).

    Returns:
        Dict with keys: 'prime', 'retrograde', 'inversion', 'retrograde_inversion'.
    """
    prime = list(row)
    retrograde = list(reversed(row))
    # Inversion: mirror intervals around the first note
    first = row[0]
    inversion = [(first - (pc - first)) % 12 for pc in row]
    retrograde_inversion = list(reversed(inversion))
    return {
        "prime": prime,
        "retrograde": retrograde,
        "inversion": inversion,
        "retrograde_inversion": retrograde_inversion,
    }



def interval_vector(pitch_set: list[int]) -> list[int]:
    """Compute the interval-class vector of a pitch-class set.

    The interval vector counts how many of each interval class (1–6)
    appear between all pairs. It's the fingerprint that Forte used
    to classify all 220 possible pitch-class sets. Two sets with the
    same vector are Z-related — they sound similar despite being
    different collections.

    Args:
        pitch_set: List of pitch classes (0–11).

    Returns:
        6-element list: [ic1_count, ic2_count, ..., ic6_count].
    """
    pcs = sorted(set(pc % 12 for pc in pitch_set))
    vector = [0] * 6
    for i in range(len(pcs)):
        for j in range(i + 1, len(pcs)):
            diff = (pcs[j] - pcs[i]) % 12
            ic = min(diff, 12 - diff)  # interval class (1–6)
            if 1 <= ic <= 6:
                vector[ic - 1] += 1
    return vector



# ---------------------------------------------------------------------------
# Pitch set operations (v104.0)
# ---------------------------------------------------------------------------


def pc_set(pitches: list[str]) -> set[int]:
    """Convert pitch names to a pitch-class set (integers 0-11).

    Args:
        pitches: List of note names.

    Returns:
        Set of pitch classes.
    """
    return {_semi(p) for p in pitches}



def pc_union(set_a: list[str], set_b: list[str]) -> list[str]:
    """Union of two pitch-class collections.

    Args:
        set_a: First pitch list.
        set_b: Second pitch list.

    Returns:
        Sorted list of unique pitch names from both sets.
    """
    pcs = pc_set(set_a) | pc_set(set_b)
    return sorted([_NOTE_NAMES[pc] for pc in pcs], key=lambda n: _semi(n))



def pc_intersection(set_a: list[str], set_b: list[str]) -> list[str]:
    """Intersection of two pitch-class collections.

    Args:
        set_a: First pitch list.
        set_b: Second pitch list.

    Returns:
        Sorted list of pitch names common to both sets.
    """
    pcs = pc_set(set_a) & pc_set(set_b)
    return sorted([_NOTE_NAMES[pc] for pc in pcs], key=lambda n: _semi(n))



def pc_complement(pitches: list[str]) -> list[str]:
    """Return all pitch classes NOT in the given set.

    Args:
        pitches: Input pitch names.

    Returns:
        Sorted list of pitch names absent from the input.
    """
    pcs = pc_set(pitches)
    return sorted([_NOTE_NAMES[i] for i in range(12) if i not in pcs], key=lambda n: _semi(n))



def transpose_set(pitches: list[str], semitones: int) -> list[str]:
    """Transpose a pitch-class set by a number of semitones.

    Args:
        pitches:   Input pitch names.
        semitones: Transposition amount.

    Returns:
        Transposed pitch names.
    """
    return [_NOTE_NAMES[(_semi(p) + semitones) % 12] for p in pitches]

