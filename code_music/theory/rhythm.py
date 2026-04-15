"""theory.rhythm — rhythmic patterns, displacement, meters, groove, quantization."""

from __future__ import annotations

from ._core import (
    _GROOVE_TEMPLATES,
    _CLAVE_PATTERNS,
    _CASCARA_PATTERNS,
    _CONGA_PATTERNS,
    Note,
)


def harmonic_rhythm(song, beats_per_bar: int = 4) -> dict:
    """Measure how frequently chords change in a song.

    Args:
        song:          Song to analyze.
        beats_per_bar: Beats per bar.

    Returns:
        Dict with total_chords, total_bars, changes_per_bar, chord_durations.
    """
    from ..engine import Chord as _Chord

    chords: list[tuple[float, float]] = []  # (position, duration)
    for track in song.tracks:
        pos = 0.0
        for beat in track.beats:
            if beat.event and isinstance(beat.event, _Chord):
                chords.append((pos, beat.event.duration))
            if beat.event:
                pos += beat.event.duration

    total_beats = 0.0
    for track in song.tracks:
        track_dur = sum(b.event.duration if b.event else 0 for b in track.beats)
        total_beats = max(total_beats, track_dur)

    total_bars = max(1, int(total_beats / beats_per_bar))
    durations = [d for _, d in chords]

    return {
        "total_chords": len(chords),
        "total_bars": total_bars,
        "changes_per_bar": round(len(chords) / max(total_bars, 1), 2),
        "chord_durations": durations,
        "avg_chord_duration": round(sum(durations) / max(len(durations), 1), 2),
    }


def swing_notes(notes: list[Note], amount: float = 0.6) -> list[Note]:
    """Apply swing feel by alternating long/short note pairs.

    Pairs of notes get asymmetric durations: first note gets `amount`
    of the pair's total duration, second gets the rest.

    Args:
        notes:  List of Notes.
        amount: Swing ratio (0.5=straight, 0.67=triplet swing, 0.75=heavy).

    Returns:
        New list with swung durations.
    """
    result: list[Note] = []
    for i in range(0, len(notes) - 1, 2):
        pair_dur = notes[i].duration + notes[i + 1].duration
        long_dur = pair_dur * amount
        short_dur = pair_dur - long_dur
        n1, n2 = notes[i], notes[i + 1]
        if n1.pitch is None:
            result.append(Note.rest(long_dur))
        else:
            result.append(Note(str(n1.pitch), n1.octave, long_dur, velocity=n1.velocity))
        if n2.pitch is None:
            result.append(Note.rest(short_dur))
        else:
            result.append(Note(str(n2.pitch), n2.octave, short_dur, velocity=n2.velocity))
    if len(notes) % 2 == 1:
        result.append(notes[-1])
    return result


def accent_pattern(notes: list[Note], pattern: list[bool]) -> list[Note]:
    """Apply an accent pattern to notes — accented notes get louder.

    Args:
        notes:   List of Notes.
        pattern: Boolean list (cycled). True = accent (+30% velocity).

    Returns:
        New list with velocity accents.
    """
    if not pattern:
        return list(notes)
    result: list[Note] = []
    for i, n in enumerate(notes):
        accented = pattern[i % len(pattern)]
        if n.pitch is None:
            result.append(Note.rest(n.duration))
        else:
            vel = min(1.0, n.velocity * (1.3 if accented else 0.7))
            result.append(Note(str(n.pitch), n.octave, n.duration, velocity=vel))
    return result


def retrograde_rhythm(notes: list[Note]) -> list[Note]:
    """Reverse durations while keeping pitches in original order.

    A rhythmic retrograde — the pitch sequence stays the same but the
    rhythm plays backwards. Creates subtle variation without changing the melody.

    Args:
        notes: List of Notes.

    Returns:
        New list with reversed durations.
    """
    durations = [n.duration for n in reversed(notes)]
    result: list[Note] = []
    for i, n in enumerate(notes):
        if n.pitch is None:
            result.append(Note.rest(durations[i]))
        else:
            result.append(Note(str(n.pitch), n.octave, durations[i], velocity=n.velocity))
    return result


# ---------------------------------------------------------------------------
# Rhythm — tuplet variations, polyrhythm, metric modulation (v40.0)
# ---------------------------------------------------------------------------


def quintuplet(
    notes: list[Note],
    total_duration: float = 1.0,
) -> list[Note]:
    """Fit notes into a quintuplet grouping (5 in the space of 4).

    Args:
        notes:          Up to 5 notes to squeeze into the grouping.
        total_duration: The total beat duration for the quintuplet.

    Returns:
        List of Notes with durations adjusted for quintuplet timing.
    """
    count = min(len(notes), 5)
    dur = total_duration / 5
    return [Note(n.pitch, n.octave, dur, velocity=n.velocity) for n in notes[:count]]


def septuplet(
    notes: list[Note],
    total_duration: float = 2.0,
) -> list[Note]:
    """Fit notes into a septuplet grouping (7 in the space of 4 or 8).

    Args:
        notes:          Up to 7 notes to squeeze into the grouping.
        total_duration: The total beat duration for the septuplet.

    Returns:
        List of Notes with durations adjusted for septuplet timing.
    """
    count = min(len(notes), 7)
    dur = total_duration / 7
    return [Note(n.pitch, n.octave, dur, velocity=n.velocity) for n in notes[:count]]


def generate_polyrhythm(
    root: str = "C",
    octave: int = 4,
    rhythm_a: int = 3,
    rhythm_b: int = 4,
    bars: int = 1,
    beats_per_bar: int = 4,
    duration_per_beat: float = 1.0,
) -> tuple[list[Note], list[Note]]:
    """Generate two interlocking polyrhythmic patterns (e.g. 3-against-4).

    Polyrhythms layer two different subdivisions against each other.
    3:4 is the most common (found in West African music, jazz, EDM).
    5:4, 7:4, and other ratios create increasingly complex textures.

    Args:
        root:             Note pitch for both voices.
        octave:           Base octave (voice A); voice B is one octave up.
        rhythm_a:         Hits per bar for voice A.
        rhythm_b:         Hits per bar for voice B.
        bars:             Number of bars.
        beats_per_bar:    Beats per bar (for duration calculation).
        duration_per_beat: Duration of one beat.

    Returns:
        Tuple of (voice_a_notes, voice_b_notes).
    """
    total_dur = bars * beats_per_bar * duration_per_beat
    dur_a = total_dur / (rhythm_a * bars)
    dur_b = total_dur / (rhythm_b * bars)

    voice_a = [Note(root, octave, dur_a, velocity=100) for _ in range(rhythm_a * bars)]
    voice_b = [Note(root, octave + 1, dur_b, velocity=80) for _ in range(rhythm_b * bars)]

    return (voice_a, voice_b)


def metric_modulation(
    bpm: float,
    old_subdivision: int = 4,
    new_subdivision: int = 3,
) -> float:
    """Calculate the new BPM after a metric modulation.

    Metric modulation reinterprets a subdivision from the old tempo as
    the beat of the new tempo. For example, triplets at 120 BPM become
    straight beats at 180 BPM (120 * 3/2 = 180 ... wait, that's just
    math. But the music theory is what makes it *cool*).

    Args:
        bpm:             Current tempo.
        old_subdivision: Notes per beat in the old meter (e.g. 4 = 16ths).
        new_subdivision: Notes per beat in the new meter (e.g. 3 = triplets).

    Returns:
        New BPM after the modulation.
    """
    return bpm * old_subdivision / new_subdivision


# ---------------------------------------------------------------------------
# Rhythmic displacement & additive rhythm (v45.0)
# ---------------------------------------------------------------------------


def displace(notes: list[Note], offset_beats: float) -> list[Note]:
    """Shift a rhythmic pattern forward in time by inserting a rest.

    Displacement creates tension by pushing a pattern off the beat.
    Funk, Afrobeat, and prog rock live in that space between where
    you expect the hit and where it actually lands.

    Args:
        notes:        Original note list.
        offset_beats: How many beats to shift forward.

    Returns:
        New list with a leading rest, then the original notes.
    """
    if offset_beats <= 0 or not notes:
        return list(notes)
    return [Note.rest(offset_beats)] + list(notes)


def phase_shift(
    pattern_a: list[Note],
    pattern_b: list[Note],
    offset: float = 0.25,
) -> tuple[list[Note], list[Note]]:
    """Create a Steve Reich-style phase shift between two patterns.

    Both patterns play simultaneously, but pattern_b is displaced by
    a small offset. Over time, the two patterns drift in and out of
    alignment — the foundation of minimalism.

    Args:
        pattern_a: First pattern (unchanged).
        pattern_b: Second pattern (displaced).
        offset:    Displacement in beats for pattern_b.

    Returns:
        Tuple of (pattern_a, displaced_pattern_b).
    """
    shifted_b = displace(pattern_b, offset)
    return (list(pattern_a), shifted_b)


def hemiola(
    note: str = "C",
    octave: int = 4,
    bars: int = 2,
    duration: float = 1.0,
) -> tuple[list[Note], list[Note]]:
    """Generate a hemiola — 3-against-2 grouping across barlines.

    Two bars of 3/4 reinterpreted as three groups of 2. Brahms built
    half his career on this trick. The rhythmic illusion where the
    meter seems to flip without the time signature actually changing.

    Args:
        note:     Pitch for both voices.
        octave:   Base octave.
        bars:     Number of bar pairs (each pair = 1 hemiola cycle).
        duration: Base beat duration.

    Returns:
        Tuple of (voice_in_3, voice_in_2) for layering.
    """
    # Voice in 3: groups of 3 beats (normal 3/4)
    voice_3 = [Note(note, octave, duration) for _ in range(3 * bars)]
    # Voice in 2: groups of 2 beats (hemiola reinterpretation)
    two_dur = duration * 3 / 2  # stretch to fill same total time in groups of 2
    voice_2 = [Note(note, octave + 1, two_dur) for _ in range(2 * bars)]
    return (voice_3, voice_2)


def additive_rhythm(
    groups: list[int],
    note: str = "C",
    octave: int = 4,
    base_duration: float = 0.25,
) -> list[Note]:
    """Generate an additive rhythm from beat groupings.

    Additive rhythms define meter as sums of unequal groups instead
    of equal subdivisions. [2,2,3] = 7/8 (Balkan), [3,3,2] = tresillo
    (Afro-Cuban), [2,3,2,2,3] = 12/8 aksak. Fundamental to music
    from the Balkans, Turkey, India, and West Africa.

    Args:
        groups:        List of beat counts per group (e.g. [2,3,2]).
        note:          Pitch for accented beats.
        octave:        Base octave.
        base_duration: Duration of one subdivision.

    Returns:
        List of Notes with accented downbeats and quieter fills.
    """
    result: list[Note] = []
    for group_size in groups:
        # First beat of each group is accented
        result.append(Note(note, octave, base_duration, velocity=100))
        for _ in range(group_size - 1):
            result.append(Note(note, octave, base_duration, velocity=60))
    return result


def aksak(
    pattern_name: str = "7/8",
    note: str = "C",
    octave: int = 4,
    bars: int = 1,
) -> list[Note]:
    """Generate a named Balkan aksak (additive) rhythm pattern.

    Aksak means "limping" in Turkish — these are the asymmetric meters
    that make Balkan music dance differently from Western pop. If it
    doesn't make you want to stomp, the groupings are wrong.

    Supported patterns:
        '5/8':  [2,3]           — common in Greek/Turkish
        '7/8':  [2,2,3]         — ruchenitsa (Bulgarian)
        '9/8':  [2,2,2,3]       — karsilama (Turkish)
        '11/8': [2,2,3,2,2]     — kopanitsa (Bulgarian)
        '15/8': [2,2,2,2,2,3]   — Balkan compound

    Args:
        pattern_name: Time signature name.
        note:         Pitch.
        octave:       Octave.
        bars:         Number of repetitions.

    Returns:
        List of Notes with the aksak rhythm.
    """
    patterns = {
        "5/8": [2, 3],
        "7/8": [2, 2, 3],
        "9/8": [2, 2, 2, 3],
        "11/8": [2, 2, 3, 2, 2],
        "15/8": [2, 2, 2, 2, 2, 3],
    }
    if pattern_name not in patterns:
        raise ValueError(f"Unknown aksak pattern {pattern_name!r}. Choose: {', '.join(patterns)}")
    groups = patterns[pattern_name]
    result: list[Note] = []
    for _ in range(bars):
        result.extend(additive_rhythm(groups, note, octave))
    return result


def generate_rhythm_pattern(
    hits: int = 8,
    slots: int = 16,
    duration_per_slot: float = 0.25,
    note: str = "C",
    octave: int = 4,
    seed: int | None = None,
) -> list[Note]:
    """Generate a random rhythm pattern with rests.

    Distributes hits across slots randomly but avoids clustering.
    More organic than Euclidean distribution — less mathematical,
    more human.

    Args:
        hits:             Number of sounding notes.
        slots:            Total number of time slots.
        duration_per_slot: Duration of each slot.
        note:             Pitch for hits.
        octave:           Octave for hits.
        seed:             Random seed.

    Returns:
        List of Notes and rests.
    """
    import random as _rng

    rng = _rng.Random(seed)
    positions = sorted(rng.sample(range(slots), min(hits, slots)))
    hit_set = set(positions)

    result: list[Note] = []
    for i in range(slots):
        if i in hit_set:
            result.append(Note(note, octave, duration_per_slot, velocity=90))
        else:
            result.append(Note.rest(duration_per_slot))
    return result


def groove_template(name: str) -> list[float]:
    """Return a named groove template (timing offsets per 16th note).

    Positive values push the note late (behind the beat), negative
    values pull it early. The difference between a robot and a
    drummer with soul.

    Supported grooves: straight, mpc_swing, j_dilla, motown, shuffle, bossa.

    Args:
        name: Groove template name.

    Returns:
        16-element list of timing offsets in beats.

    Raises:
        ValueError: If name is not recognized.
    """
    if name not in _GROOVE_TEMPLATES:
        raise ValueError(f"Unknown groove {name!r}. Choose: {', '.join(sorted(_GROOVE_TEMPLATES))}")
    return list(_GROOVE_TEMPLATES[name])


def apply_groove(
    notes: list[Note],
    template: list[float],
    strength: float = 1.0,
) -> list[Note]:
    """Apply a groove template to a note list by adjusting durations.

    Since code-music uses sequential durations (not onset times), groove
    is approximated by stretching/compressing individual note durations
    to simulate the timing feel. The total duration is preserved.

    Args:
        notes:    Input notes.
        template: Timing offsets (from groove_template or custom).
        strength: How much groove to apply (0.0 = none, 1.0 = full).

    Returns:
        New note list with groove-adjusted durations.
    """
    if not notes or not template:
        return list(notes)

    result: list[Note] = []
    for i, n in enumerate(notes):
        slot = i % len(template)
        offset = template[slot] * strength
        new_dur = max(0.01, n.duration + offset)
        if n.pitch is None:
            result.append(Note.rest(new_dur))
        else:
            result.append(Note(n.pitch, n.octave, new_dur, velocity=n.velocity))
    return result


def extract_groove(notes: list[Note], grid_duration: float = 0.25) -> list[float]:
    """Extract a groove template from a note list by comparing to a grid.

    Measures how much each note's duration deviates from the expected
    grid spacing. Use this to capture a human performance's feel and
    apply it to other patterns.

    Args:
        notes:         Input notes.
        grid_duration: Expected duration per grid slot.

    Returns:
        List of timing offsets, one per note.
    """
    return [round(n.duration - grid_duration, 4) for n in notes]


# ---------------------------------------------------------------------------
# Tuplet nesting & complex meters (v67.0)
# ---------------------------------------------------------------------------


def nested_tuplet(
    outer: int,
    inner: int,
    notes: list[Note],
    total_duration: float = 4.0,
) -> list[Note]:
    """Create a nested tuplet — a tuplet inside a tuplet.

    For example, nested_tuplet(3, 5, notes) creates quintuplets inside
    each beat of a triplet. Carter and Ferneyhough territory — the kind
    of rhythm that makes drummers quit and join law school.

    Args:
        outer:          Outer tuplet division (e.g. 3 = triplet).
        inner:          Inner tuplet division per outer beat.
        notes:          Source notes to fill (truncated to outer*inner).
        total_duration: Total duration for the entire nested structure.

    Returns:
        List of Notes with durations adjusted for nesting.
    """
    total_notes = outer * inner
    dur_per_note = total_duration / total_notes
    result: list[Note] = []
    for i in range(min(len(notes), total_notes)):
        n = notes[i]
        if n.pitch is None:
            result.append(Note.rest(dur_per_note))
        else:
            result.append(Note(n.pitch, n.octave, dur_per_note, velocity=n.velocity))
    return result


def irrational_meter(
    numerator: int,
    denominator: int,
    note: str = "C",
    octave: int = 4,
    bars: int = 1,
    base_duration: float = 0.25,
) -> list[Note]:
    """Generate a pattern in an irrational meter (e.g. 7/12, 5/6).

    Irrational meters have denominators that aren't powers of 2.
    7/12 means 7 beats where each beat is a 12th-note (a triplet
    subdivision of a quarter). The math is clean but the feel is alien.

    Args:
        numerator:     Beats per bar.
        denominator:   Beat unit (can be any integer, not just powers of 2).
        note:          Pitch for beats.
        octave:        Octave.
        bars:          Number of bars.
        base_duration: Duration reference for a standard quarter note.

    Returns:
        List of Notes representing the irrational pattern.
    """
    # Duration per beat: scale by denominator ratio to quarter note
    beat_dur = base_duration * (4.0 / denominator)
    result: list[Note] = []
    for _ in range(bars):
        for beat in range(numerator):
            vel = 100 if beat == 0 else 70  # accent beat 1
            result.append(Note(note, octave, beat_dur, velocity=vel))
    return result


def polymetric_overlay(
    meters: list[tuple[int, int]],
    note: str = "C",
    octave: int = 4,
    bars: int = 1,
    base_duration: float = 0.25,
) -> list[list[Note]]:
    """Layer multiple meters simultaneously.

    Each meter produces its own voice. When played together, the
    different cycle lengths create complex phase relationships.
    The foundation of West African polyrhythm and Steve Reich's music.

    Args:
        meters:        List of (numerator, denominator) tuples.
        note:          Pitch for all voices.
        octave:        Base octave (each voice offset by 1).
        bars:          Number of bars.
        base_duration: Duration reference.

    Returns:
        List of note lists, one per meter.
    """
    voices: list[list[Note]] = []
    for i, (num, den) in enumerate(meters):
        voice = irrational_meter(num, den, note, octave + i, bars, base_duration)
        voices.append(voice)
    return voices


# ---------------------------------------------------------------------------
# Rhythm quantization & grid snap (v73.0)
# ---------------------------------------------------------------------------


def quantize_rhythm(
    notes: list[Note],
    grid: float = 0.25,
) -> list[Note]:
    """Snap note durations to the nearest grid value.

    The "fix my sloppy playing" function. Rounds every duration to
    the nearest multiple of the grid value. 0.25 = sixteenth notes,
    0.5 = eighths, 1.0 = quarters.

    Args:
        notes: Input notes.
        grid:  Grid resolution in beats.

    Returns:
        Quantized note list.
    """
    result: list[Note] = []
    for n in notes:
        snapped = max(grid, round(n.duration / grid) * grid)
        if n.pitch is None:
            result.append(Note.rest(snapped))
        else:
            result.append(Note(n.pitch, n.octave, snapped, velocity=n.velocity))
    return result


def swing_quantize(
    notes: list[Note],
    grid: float = 0.5,
    swing_amount: float = 0.66,
) -> list[Note]:
    """Quantize with swing feel preserved.

    Even-indexed notes land on the grid. Odd-indexed notes are pushed
    late by the swing ratio. A swing_amount of 0.66 = triplet swing
    (2:1 ratio), 0.5 = straight.

    Args:
        notes:        Input notes.
        grid:         Base grid resolution.
        swing_amount: Ratio for the swung beat (0.5 = straight, 0.66 = triplet).

    Returns:
        Swing-quantized note list.
    """
    result: list[Note] = []
    for i, n in enumerate(notes):
        if i % 2 == 0:
            dur = grid * swing_amount * 2
        else:
            dur = grid * (1.0 - swing_amount) * 2
        dur = max(0.01, dur)
        if n.pitch is None:
            result.append(Note.rest(dur))
        else:
            result.append(Note(n.pitch, n.octave, dur, velocity=n.velocity))
    return result


def humanize_timing(
    notes: list[Note],
    amount: float = 0.02,
    seed: int | None = None,
) -> list[Note]:
    """Add random timing deviations to make quantized music feel human.

    The opposite of quantize — adds imperfection on purpose. Real
    drummers are never perfectly on the grid. This function adds
    that life back.

    Args:
        notes:  Input notes.
        amount: Max deviation in beats (default 0.02 = subtle).
        seed:   Random seed.

    Returns:
        Humanized note list.
    """
    import random as _rng

    rng = _rng.Random(seed)
    result: list[Note] = []
    for n in notes:
        deviation = rng.uniform(-amount, amount)
        new_dur = max(0.01, n.duration + deviation)
        if n.pitch is None:
            result.append(Note.rest(new_dur))
        else:
            result.append(Note(n.pitch, n.octave, new_dur, velocity=n.velocity))
    return result


# ---------------------------------------------------------------------------
# Tempo curve rendering (v81.0)
# ---------------------------------------------------------------------------


def ritardando(
    notes: list[Note],
    start_bpm: float = 120.0,
    end_bpm: float = 60.0,
) -> list[Note]:
    """Gradually slow down by stretching note durations.

    The musical "slow down" — rubato's dignified cousin. Each note
    gets progressively longer as the tempo drops from start to end.

    Args:
        notes:     Input notes.
        start_bpm: Starting tempo.
        end_bpm:   Ending tempo.

    Returns:
        Notes with stretched durations simulating tempo decrease.
    """
    if not notes:
        return []
    result: list[Note] = []
    for i, n in enumerate(notes):
        frac = i / max(len(notes) - 1, 1)
        current_bpm = start_bpm + (end_bpm - start_bpm) * frac
        ratio = start_bpm / max(current_bpm, 1)
        new_dur = n.duration * ratio
        if n.pitch is None:
            result.append(Note.rest(new_dur))
        else:
            result.append(Note(n.pitch, n.octave, new_dur, velocity=n.velocity))
    return result


def accelerando(
    notes: list[Note],
    start_bpm: float = 60.0,
    end_bpm: float = 120.0,
) -> list[Note]:
    """Gradually speed up by compressing note durations.

    Args:
        notes:     Input notes.
        start_bpm: Starting tempo.
        end_bpm:   Ending tempo.

    Returns:
        Notes with compressed durations simulating tempo increase.
    """
    return ritardando(notes, start_bpm, end_bpm)


def rubato(
    notes: list[Note],
    amount: float = 0.15,
    seed: int | None = None,
) -> list[Note]:
    """Apply rubato — expressive push-pull timing around a tempo center.

    Unlike humanize_timing (random noise), rubato has musical intent:
    it alternates between stretching and compressing, like a singer
    breathing through a phrase.

    Args:
        notes:  Input notes.
        amount: Max stretch/compress ratio (0.15 = ±15%).
        seed:   Random seed.

    Returns:
        Notes with rubato-adjusted durations.
    """
    import math
    import random as _rng

    rng = _rng.Random(seed)
    if not notes:
        return []

    result: list[Note] = []
    for i, n in enumerate(notes):
        # Sinusoidal base with random perturbation
        phase = math.sin(i * 0.7) * amount
        jitter = rng.uniform(-amount * 0.3, amount * 0.3)
        ratio = 1.0 + phase + jitter
        new_dur = max(0.01, n.duration * ratio)
        if n.pitch is None:
            result.append(Note.rest(new_dur))
        else:
            result.append(Note(n.pitch, n.octave, new_dur, velocity=n.velocity))
    return result


# ---------------------------------------------------------------------------
# Note duration algebra (v83.0)
# ---------------------------------------------------------------------------


def dotted(note: Note) -> Note:
    """Add a dot to a note — increases duration by 50%.

    A dotted quarter = 1.5 beats, dotted half = 3 beats. The most
    common rhythmic extension in Western music.

    Args:
        note: Input note.

    Returns:
        New note with 1.5x duration.
    """
    new_dur = note.duration * 1.5
    if note.pitch is None:
        return Note.rest(new_dur)
    return Note(note.pitch, note.octave, new_dur, velocity=note.velocity)


def double_dotted(note: Note) -> Note:
    """Add a double dot — increases duration by 75%.

    Double-dotted quarter = 1.75 beats. Rare but elegant.

    Args:
        note: Input note.

    Returns:
        New note with 1.75x duration.
    """
    new_dur = note.duration * 1.75
    if note.pitch is None:
        return Note.rest(new_dur)
    return Note(note.pitch, note.octave, new_dur, velocity=note.velocity)


def tied(note_a: Note, note_b: Note) -> Note:
    """Tie two notes — merge into one note with combined duration.

    Both notes must have the same pitch (or both be rests). The tie
    is the notation trick for durations that don't fit standard values.

    Args:
        note_a: First note.
        note_b: Second note.

    Returns:
        Single note with summed duration.

    Raises:
        ValueError: If pitches don't match.
    """
    if note_a.pitch != note_b.pitch:
        raise ValueError(f"Cannot tie different pitches: {note_a.pitch} and {note_b.pitch}")
    new_dur = note_a.duration + note_b.duration
    if note_a.pitch is None:
        return Note.rest(new_dur)
    return Note(note_a.pitch, note_a.octave, new_dur, velocity=note_a.velocity)


def split_note(note: Note, divisions: int = 2) -> list[Note]:
    """Split one note into N equal parts.

    A whole note split into 4 = four quarter notes. The reverse of a tie.

    Args:
        note:      Input note.
        divisions: Number of parts.

    Returns:
        List of notes, each with duration / divisions.
    """
    sub_dur = note.duration / divisions
    if note.pitch is None:
        return [Note.rest(sub_dur) for _ in range(divisions)]
    return [
        Note(note.pitch, note.octave, sub_dur, velocity=note.velocity) for _ in range(divisions)
    ]


# ---------------------------------------------------------------------------
# Rhythm pattern matching (v111.0)
# ---------------------------------------------------------------------------


def rhythm_string(notes: list[Note], grid: float = 0.25) -> str:
    """Encode a rhythm as a string: X=note, .=rest, each char = one grid slot.

    The rhythmic skeleton of a melody — strip away pitch and dynamics,
    keep only "when does something happen?"

    Args:
        notes: Input notes.
        grid:  Grid resolution in beats per slot.

    Returns:
        String of X and . characters.
    """
    result: list[str] = []
    for n in notes:
        slots = max(1, round(n.duration / grid))
        if n.pitch is not None:
            result.append("X")
            result.extend("." * (slots - 1))
        else:
            result.extend("." * slots)
    return "".join(result)


def rhythm_match(melody_a: list[Note], melody_b: list[Note], grid: float = 0.25) -> float:
    """Compare two melodies by rhythmic similarity (0.0-1.0).

    Compares the X/. patterns. Two melodies that hit notes at the
    same positions score 1.0, regardless of pitch.

    Args:
        melody_a: First melody.
        melody_b: Second melody.
        grid:     Grid resolution.

    Returns:
        Similarity score 0.0-1.0.
    """
    ra = rhythm_string(melody_a, grid)
    rb = rhythm_string(melody_b, grid)
    if not ra or not rb:
        return 0.0
    max_len = max(len(ra), len(rb))
    matches = sum(1 for a, b in zip(ra, rb) if a == b)
    return round(matches / max_len, 3)


# ---------------------------------------------------------------------------
# Harmonic rhythm quantizer (v127.0)
# ---------------------------------------------------------------------------


def chords_per_bar(
    progression: list[tuple[str, str]],
    total_bars: int,
) -> float:
    """Calculate the average number of chord changes per bar.

    Args:
        progression: Chord progression.
        total_bars:  Number of bars the progression spans.

    Returns:
        Average chords per bar.
    """
    if total_bars <= 0:
        return 0.0
    return round(len(progression) / total_bars, 2)


# ---------------------------------------------------------------------------
# Musical performance effects (v170)
# ---------------------------------------------------------------------------


def fermata(note: Note, stretch: float = 2.0) -> Note:
    """Hold a note longer than written - the classic pause marking.

    A fermata (bird's eye) typically doubles the note's duration, though
    the exact length is at the performer's discretion. In code, we use
    a stretch factor.

    Args:
        note:    Note to hold.
        stretch: Duration multiplier (2.0 = double, 1.5 = moderate hold).

    Returns:
        New Note with stretched duration.
    """
    new_dur = note.duration * stretch
    if note.pitch is None:
        return Note.rest(new_dur)
    return Note(note.pitch, note.octave, new_dur, velocity=note.velocity)


def caesura(duration: float = 1.0) -> Note:
    """Insert a caesura (grand pause / breath mark) as a rest.

    A complete silence where all parts stop. In orchestral music,
    the conductor holds the baton still. Everything breathes.

    Args:
        duration: Length of the silence in beats.

    Returns:
        A rest Note of the specified duration.
    """
    return Note.rest(duration)


def grand_pause(duration: float = 2.0) -> Note:
    """A dramatic silence - longer than a caesura, used for effect.

    Beethoven's favorite trick. The silence after a loud passage
    that makes the audience hold their breath.

    Args:
        duration: Length of the silence in beats.

    Returns:
        A rest Note.
    """
    return Note.rest(duration)


def a_tempo(
    notes: list[Note],
    target_bpm: float,
    current_bpm: float,
) -> list[Note]:
    """Return to the original tempo after a ritardando or accelerando.

    Adjusts all note durations to account for the tempo ratio between
    the current (slowed/sped) tempo and the target tempo.

    Args:
        notes:       Notes currently at the modified tempo.
        target_bpm:  The tempo to return to.
        current_bpm: The current (modified) tempo.

    Returns:
        Notes with durations adjusted for the target tempo.
    """
    if current_bpm <= 0 or target_bpm <= 0:
        return list(notes)
    ratio = current_bpm / target_bpm
    result: list[Note] = []
    for n in notes:
        new_dur = n.duration * ratio
        if n.pitch is None:
            result.append(Note.rest(new_dur))
        else:
            result.append(Note(n.pitch, n.octave, new_dur, velocity=n.velocity))
    return result


def tempo_curve(
    notes: list[Note],
    bpm_values: list[float],
    base_bpm: float = 120.0,
) -> list[Note]:
    """Apply an arbitrary tempo curve across a note sequence.

    Each note gets a BPM value from the list (interpolated if the list
    is shorter than the notes). Duration is scaled by base_bpm/local_bpm.
    This is the general-purpose version of ritardando/accelerando - you
    can draw any tempo shape.

    Args:
        notes:      Input notes.
        bpm_values: List of BPM values defining the curve.
        base_bpm:   Reference BPM (durations are relative to this).

    Returns:
        Notes with tempo-curved durations.
    """
    if not notes or not bpm_values:
        return list(notes)
    result: list[Note] = []
    for i, n in enumerate(notes):
        # Interpolate BPM from the curve
        frac = i / max(len(notes) - 1, 1)
        idx = frac * (len(bpm_values) - 1)
        lo_idx = int(idx)
        hi_idx = min(lo_idx + 1, len(bpm_values) - 1)
        t = idx - lo_idx
        local_bpm = bpm_values[lo_idx] * (1 - t) + bpm_values[hi_idx] * t
        ratio = base_bpm / max(local_bpm, 1)
        new_dur = n.duration * ratio
        if n.pitch is None:
            result.append(Note.rest(new_dur))
        else:
            result.append(Note(n.pitch, n.octave, new_dur, velocity=n.velocity))
    return result


def morendo(
    notes: list[Note],
    start_vel: float = 0.7,
    end_vel: float = 0.05,
    start_bpm: float = 120.0,
    end_bpm: float = 60.0,
) -> list[Note]:
    """Dying away - simultaneous ritardando and diminuendo.

    The musical instruction to let the sound fade to nothing while
    slowing down. The last breath of a Mahler symphony.

    Args:
        notes:     Input notes.
        start_vel: Starting velocity.
        end_vel:   Ending velocity (near zero).
        start_bpm: Starting tempo.
        end_bpm:   Ending tempo (slower).

    Returns:
        Notes with both slowing and fading applied.
    """
    if not notes:
        return []
    result: list[Note] = []
    for i, n in enumerate(notes):
        frac = i / max(len(notes) - 1, 1)
        current_bpm = start_bpm + (end_bpm - start_bpm) * frac
        vel = start_vel + (end_vel - start_vel) * frac
        ratio = start_bpm / max(current_bpm, 1)
        new_dur = n.duration * ratio
        if n.pitch is None:
            result.append(Note.rest(new_dur))
        else:
            result.append(Note(n.pitch, n.octave, new_dur, velocity=vel))
    return result


def calando(
    notes: list[Note],
    amount: float = 0.5,
) -> list[Note]:
    """Calando - gradually softer and slower. Less dramatic than morendo.

    Args:
        notes:  Input notes.
        amount: How much to calm down (0.0-1.0).

    Returns:
        Notes with gentle slowing and softening.
    """
    if not notes:
        return []
    result: list[Note] = []
    for i, n in enumerate(notes):
        frac = i / max(len(notes) - 1, 1)
        vel_scale = 1.0 - (frac * amount * 0.5)
        dur_scale = 1.0 + (frac * amount * 0.3)
        if n.pitch is None:
            result.append(Note.rest(n.duration * dur_scale))
        else:
            result.append(
                Note(n.pitch, n.octave, n.duration * dur_scale, velocity=n.velocity * vel_scale)
            )
    return result


# ---------------------------------------------------------------------------
# Latin percussion patterns (v170)
# ---------------------------------------------------------------------------


def clave_pattern(
    style: str = "son_32",
    note: str = "C",
    octave: int = 5,
    duration_per_step: float = 0.25,
    bars: int = 1,
    velocity: float = 0.85,
) -> list[Note]:
    """Generate a clave pattern - the rhythmic backbone of Latin music.

    The clave is not just a rhythm. It is the organizing principle.
    Every other part in the ensemble locks to it. Get the clave wrong
    and the whole thing falls apart.

    Styles:
        son_32:     Son clave 3-2 (most common in salsa)
        son_23:     Son clave 2-3 (reversed, used in some arrangements)
        rumba_32:   Rumba clave 3-2 (shifted third hit, more syncopated)
        rumba_23:   Rumba clave 2-3
        bossa:      Bossa nova clave (Brazilian, subtler)
        afro_cuban: 6/8 Afro-Cuban bell pattern

    Args:
        style:              Clave type.
        note:               Pitch for hits.
        octave:             Octave.
        duration_per_step:  Duration of each 16th note slot.
        bars:               Number of repetitions.
        velocity:           Hit velocity.

    Returns:
        List of Notes and rests.
    """
    if style not in _CLAVE_PATTERNS:
        raise ValueError(
            f"Unknown clave style {style!r}. Choose: {', '.join(sorted(_CLAVE_PATTERNS))}"
        )
    pattern = _CLAVE_PATTERNS[style]
    result: list[Note] = []
    for _ in range(bars):
        for hit in pattern:
            if hit:
                result.append(Note(note, octave, duration_per_step, velocity=velocity))
            else:
                result.append(Note.rest(duration_per_step))
    return result


def cascara_pattern(
    style: str = "cascara_32",
    note: str = "C",
    octave: int = 5,
    duration_per_step: float = 0.25,
    bars: int = 1,
    velocity: float = 0.7,
) -> list[Note]:
    """Generate a cascara (timbales shell) pattern.

    The cascara rides on top of the clave. On the shell of the timbales
    during verses, switching to the bell during choruses. The interlocking
    of clave + cascara is what makes salsa percolate.

    Args:
        style:  "cascara_32" or "cascara_23".
        note:   Pitch for hits.
        octave: Octave.
        duration_per_step: Duration per 16th note.
        bars:   Repetitions.
        velocity: Hit velocity.

    Returns:
        List of Notes and rests.
    """
    if style not in _CASCARA_PATTERNS:
        raise ValueError(f"Unknown cascara {style!r}. Choose: {', '.join(_CASCARA_PATTERNS)}")
    pattern = _CASCARA_PATTERNS[style]
    result: list[Note] = []
    for _ in range(bars):
        for hit in pattern:
            if hit:
                result.append(Note(note, octave, duration_per_step, velocity=velocity))
            else:
                result.append(Note.rest(duration_per_step))
    return result


def montuno_pattern(
    root: str = "C",
    shape: str = "min7",
    octave: int = 4,
    duration_per_step: float = 0.25,
    bars: int = 1,
) -> list[Note]:
    """Generate a piano montuno pattern for Latin music.

    The montuno is the repeating piano figure in salsa, son, and timba.
    Locks to the clave. The pianist's left brain plays montuno while
    the right brain solos. Multitasking at its finest.

    Args:
        root:   Chord root.
        shape:  Chord quality.
        octave: Base octave.
        duration_per_step: Duration per note.
        bars:   Repetitions.

    Returns:
        List of Notes.
    """
    from ..engine import CHORD_SHAPES, note_name_to_midi

    offsets = CHORD_SHAPES.get(shape, CHORD_SHAPES["min7"])
    root_midi = note_name_to_midi(root, octave)

    # Classic montuno: root-3-5-3-root-3-5-octave with syncopation
    if len(offsets) >= 4:
        midi_seq = [
            root_midi + offsets[0],
            root_midi + offsets[1],
            root_midi + offsets[2],
            root_midi + offsets[1],
            root_midi + offsets[0],
            root_midi + offsets[1],
            root_midi + offsets[2],
            root_midi + offsets[3],
        ]
    else:
        midi_seq = [
            root_midi + offsets[0],
            root_midi + offsets[min(1, len(offsets) - 1)],
            root_midi + offsets[min(2, len(offsets) - 1)],
            root_midi + offsets[min(1, len(offsets) - 1)],
        ] * 2

    result: list[Note] = []
    for _ in range(bars):
        for midi in midi_seq:
            result.append(Note(pitch=midi, duration=duration_per_step, velocity=0.75))
    return result


def funk_drum_pattern(
    bars: int = 1,
    duration: float = 0.25,
    ghost_velocity: float = 0.3,
    seed: int | None = None,
) -> dict[str, list[Note]]:
    """Generate a funk drum pattern with ghost notes.

    Funk drumming is about the spaces between the hits. The ghost notes
    on the snare create the pocket. Without them it is just rock with
    a different bass line. Clyde Stubblefield knew this.

    Args:
        bars:            Number of bars.
        duration:        Duration per 16th note step.
        ghost_velocity:  Velocity for ghost notes (keep it low).
        seed:            Random seed.

    Returns:
        Dict with "kick", "snare", "hat" keys.
    """
    import random as _rng

    rng = _rng.Random(seed)

    steps = 16 * bars
    kick: list[Note] = []
    snare: list[Note] = []
    hat: list[Note] = []

    for bar in range(bars):
        for step in range(16):
            abs_step = bar * 16 + step
            # Kick: beat 1, "and" of 2, beat 3 with variation
            is_kick = step in (0, 6, 8) or (step == 10 and rng.random() > 0.5)
            if is_kick:
                kick.append(Note("C", 2, duration, velocity=0.9))
            else:
                kick.append(Note.rest(duration))

            # Snare: beat 2 and 4 accented, ghost notes everywhere else
            if step in (4, 12):
                snare.append(Note("D", 3, duration, velocity=0.85))
            elif step % 2 == 0 and rng.random() > 0.4:
                snare.append(Note("D", 3, duration, velocity=ghost_velocity))
            elif step % 2 == 1 and rng.random() > 0.6:
                snare.append(Note("D", 3, duration, velocity=ghost_velocity * 0.7))
            else:
                snare.append(Note.rest(duration))

            # Hat: tight 16ths with open hat on upbeats
            if step % 4 == 2 and rng.random() > 0.3:
                hat.append(Note("F#", 5, duration, velocity=0.6))  # open hat
            else:
                hat.append(Note("F#", 5, duration, velocity=0.45 if step % 2 == 0 else 0.3))

    return {"kick": kick, "snare": snare, "hat": hat}


def shuffle_drum_pattern(
    bars: int = 1,
    triplet_duration: float = 0.333,
    style: str = "blues",
) -> dict[str, list[Note]]:
    """Generate a shuffle/swing drum pattern in triplet feel.

    The shuffle is the heartbeat of blues, boogie-woogie, and swing.
    Three notes per beat, skip the middle one. That gap is where the
    groove lives. Texas Flood, Stormy Monday, Pride and Joy.

    Args:
        bars:              Number of bars.
        triplet_duration:  Duration per triplet subdivision.
        style:             "blues" (heavy), "swing" (lighter), "boogie" (driving).

    Returns:
        Dict with "kick", "snare", "hat" keys.
    """
    steps_per_bar = 12  # 4 beats x 3 triplet subdivisions
    total = steps_per_bar * bars
    kick: list[Note] = []
    snare: list[Note] = []
    hat: list[Note] = []

    for bar in range(bars):
        for step in range(steps_per_bar):
            # Kick on 1 and 3 (triplet positions 0 and 6)
            if step in (0, 6):
                kick.append(Note("C", 2, triplet_duration, velocity=0.85))
            elif style == "boogie" and step in (3, 9):
                kick.append(Note("C", 2, triplet_duration, velocity=0.6))
            else:
                kick.append(Note.rest(triplet_duration))

            # Snare on 2 and 4 (triplet positions 3 and 9)
            if step in (3, 9):
                vel = 0.8 if style == "blues" else 0.65
                snare.append(Note("D", 3, triplet_duration, velocity=vel))
            else:
                snare.append(Note.rest(triplet_duration))

            # Hat/ride: skip middle triplet (the shuffle feel)
            if step % 3 == 1:
                hat.append(Note.rest(triplet_duration))  # THE skip
            elif step % 3 == 0:
                hat.append(Note("F#", 5, triplet_duration, velocity=0.55))
            else:
                hat.append(Note("F#", 5, triplet_duration, velocity=0.35))

    return {"kick": kick, "snare": snare, "hat": hat}


def big_band_drum_pattern(
    bars: int = 1,
    duration: float = 0.5,
    feel: str = "swing",
) -> dict[str, list[Note]]:
    """Generate a big band drum pattern.

    Big band drumming is about the ride cymbal. Everything else
    is commentary. Hi-hat on 2 and 4 with the foot. Kick is feathered
    (barely audible four-on-the-floor). The snare comps and kicks
    accents with the horns.

    Args:
        bars:      Number of bars.
        duration:  Duration per 8th note step.
        feel:      "swing" (standard), "latin" (big band mambo),
                   "shuffle" (Kansas City).

    Returns:
        Dict with "ride", "hat_foot", "kick", "snare" keys.
    """
    steps = 8 * bars  # 8th notes
    ride: list[Note] = []
    hat_foot: list[Note] = []
    kick: list[Note] = []
    snare: list[Note] = []

    for bar in range(bars):
        for step in range(8):
            # Ride: constant spang-a-lang pattern
            if feel == "swing":
                if step % 2 == 0:
                    ride.append(Note("C", 6, duration, velocity=0.6))
                else:
                    ride.append(Note("C", 6, duration, velocity=0.35))
            elif feel == "latin":
                ride.append(Note("C", 6, duration, velocity=0.55))
            else:
                ride.append(Note("C", 6, duration, velocity=0.5 if step % 2 == 0 else 0.3))

            # Hi-hat foot: beats 2 and 4
            if step in (2, 6):
                hat_foot.append(Note("F#", 4, duration, velocity=0.4))
            else:
                hat_foot.append(Note.rest(duration))

            # Kick: feathered four-on-the-floor (very soft)
            if step % 2 == 0:
                kick.append(Note("C", 2, duration, velocity=0.2))
            else:
                kick.append(Note.rest(duration))

            # Snare: sparse comping (accent beats 2 and 4 occasionally)
            if step in (2, 6) and bar % 2 == 0:
                snare.append(Note("D", 3, duration, velocity=0.5))
            else:
                snare.append(Note.rest(duration))

    return {"ride": ride, "hat_foot": hat_foot, "kick": kick, "snare": snare}


def bossa_nova_pattern(
    bars: int = 1,
    duration: float = 0.25,
) -> dict[str, list[Note]]:
    """Generate a bossa nova drum pattern.

    Bossa nova drumming is restrained. Brushes or cross-stick on the
    snare, bass drum on 1 and the "and" of 2, hi-hat keeping soft time.
    Antonio Carlos Jobim territory. The quieter it is, the cooler
    it sounds.

    Args:
        bars:      Number of bars.
        duration:  Duration per 16th note.

    Returns:
        Dict with "kick", "snare", "hat" keys.
    """
    kick: list[Note] = []
    snare: list[Note] = []
    hat: list[Note] = []

    # 16 steps per bar
    # Kick: beat 1, and-of-2 (step 6)
    kick_pattern = [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    # Snare (cross-stick): beats 2 and 4 (steps 4, 12)
    snare_pattern = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
    # Hat: constant 8ths
    hat_pattern = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]

    for _ in range(bars):
        for step in range(16):
            if kick_pattern[step]:
                kick.append(Note("C", 2, duration, velocity=0.6))
            else:
                kick.append(Note.rest(duration))
            if snare_pattern[step]:
                snare.append(Note("D", 3, duration, velocity=0.4))
            else:
                snare.append(Note.rest(duration))
            if hat_pattern[step]:
                hat.append(Note("F#", 5, duration, velocity=0.3))
            else:
                hat.append(Note.rest(duration))

    return {"kick": kick, "snare": snare, "hat": hat}


def lofi_drum_pattern(
    bars: int = 1,
    duration: float = 0.25,
    seed: int | None = None,
) -> dict[str, list[Note]]:
    """Generate a lofi hip-hop drum pattern.

    J Dilla-inspired: slightly drunk timing, minimal kick and snare,
    rimshots, vinyl texture implied. Pair with lofi groove template
    for the full effect.

    Args:
        bars:      Number of bars.
        duration:  Duration per 16th note.
        seed:      Random seed.

    Returns:
        Dict with "kick", "snare", "hat" keys.
    """
    import random as _rng

    rng = _rng.Random(seed)

    kick: list[Note] = []
    snare: list[Note] = []
    hat: list[Note] = []

    for _ in range(bars):
        for step in range(16):
            # Kick: boom-bap with slight variation
            if (
                step == 0
                or (step == 6 and rng.random() > 0.3)
                or (step == 10 and rng.random() > 0.5)
            ):
                kick.append(Note("C", 2, duration, velocity=rng.uniform(0.65, 0.8)))
            else:
                kick.append(Note.rest(duration))

            # Snare: beats 2 and 4, occasional ghost
            if step in (4, 12):
                snare.append(Note("D", 3, duration, velocity=rng.uniform(0.6, 0.75)))
            elif step == 8 and rng.random() > 0.6:
                snare.append(Note("D", 3, duration, velocity=0.25))
            else:
                snare.append(Note.rest(duration))

            # Hat: variable velocity 8ths/16ths
            if step % 2 == 0:
                hat.append(Note("F#", 5, duration, velocity=rng.uniform(0.3, 0.5)))
            elif rng.random() > 0.4:
                hat.append(Note("F#", 5, duration, velocity=rng.uniform(0.15, 0.3)))
            else:
                hat.append(Note.rest(duration))

    return {"kick": kick, "snare": snare, "hat": hat}


# ---------------------------------------------------------------------------
# Ska patterns (v170 - because ska deserves its own section)
# ---------------------------------------------------------------------------


def ska_drum_pattern(
    bars: int = 1,
    duration: float = 0.25,
    style: str = "traditional",
) -> dict[str, list[Note]]:
    """Generate a ska drum pattern.

    Ska drumming is all about the afterbeat. The hi-hat or ride hammers
    on the offbeats (the "and"s). Kick on 1 and 3. Snare as cross-stick
    on 2 and 4. That is the recipe. Simple, relentless, infectious.

    Styles:
        traditional: First wave Jamaican (Lloyd Knibb, Drumbago)
        two_tone:    2 Tone / Specials (tighter, punkier, rimshot snare)
        ska_punk:    Third wave / ska-punk (double-time hat, hard kick)

    Args:
        bars:      Number of bars.
        duration:  Duration per 16th note.
        style:     "traditional", "two_tone", "ska_punk".

    Returns:
        Dict with "kick", "snare", "hat" keys.
    """
    kick: list[Note] = []
    snare: list[Note] = []
    hat: list[Note] = []

    for _ in range(bars):
        for step in range(16):
            # Kick: beats 1 and 3 (steps 0, 8)
            if style == "ska_punk":
                # Ska-punk: four-on-the-floor or driving 8ths
                is_kick = step % 4 == 0
            else:
                is_kick = step in (0, 8)

            if is_kick:
                kick.append(Note("C", 2, duration, velocity=0.75))
            else:
                kick.append(Note.rest(duration))

            # Snare: beats 2 and 4 (steps 4, 12)
            if step in (4, 12):
                art = "rimshot" if style == "two_tone" else "cross_stick"
                vel = 0.7 if style == "two_tone" else 0.55
                snare.append(Note("D", 3, duration, velocity=vel, articulation=art))
            else:
                snare.append(Note.rest(duration))

            # Hat: THE offbeat - this is what makes it ska
            if style == "ska_punk":
                # Ska-punk: straight 8ths, louder offbeats
                if step % 2 == 0:
                    hat.append(Note("F#", 5, duration, velocity=0.3))
                else:
                    hat.append(Note("F#", 5, duration, velocity=0.6))
            else:
                # Traditional: offbeat 8ths only (rests on downbeats)
                if step % 4 == 2:
                    hat.append(Note("F#", 5, duration, velocity=0.55))
                else:
                    hat.append(Note.rest(duration))

    return {"kick": kick, "snare": snare, "hat": hat}


def skank_pattern(
    root: str = "C",
    shape: str = "maj",
    octave: int = 4,
    bars: int = 1,
    duration_per_step: float = 0.25,
    style: str = "traditional",
) -> list[Note]:
    """Generate the ska guitar skank - the choppy offbeat chord stab.

    THE sound of ska. Every upbeat gets a sharp, muted chord. The
    guitar strings are barely ringing before the palm comes back
    down. Chuck-chuck-chuck-chuck on every "and." Rude boys nod
    in approval.

    Styles:
        traditional: Clean offbeat chops (Skatalites, Prince Buster)
        two_tone:    Slightly longer ring, more bite (The Specials)
        ska_punk:    Alternating power chord + muted ghost (Reel Big Fish)

    Args:
        root:              Chord root.
        shape:             Chord quality.
        octave:            Chord octave.
        bars:              Number of bars.
        duration_per_step: Duration per 16th note.
        style:             "traditional", "two_tone", "ska_punk".

    Returns:
        List of Notes (chords and rests) forming the skank pattern.
    """
    from ..engine import Chord as _Chord

    result: list[Note] = []

    for _ in range(bars):
        for step in range(16):
            if style == "ska_punk":
                if step % 4 == 2:
                    # Main upstroke: full chord, staccato
                    result.append(
                        Note(root, octave, duration_per_step, velocity=0.7, articulation="staccato")
                    )
                elif step % 4 == 0:
                    # Ghost mute on the downbeat
                    result.append(
                        Note(root, octave, duration_per_step, velocity=0.15, articulation="muted")
                    )
                else:
                    result.append(Note.rest(duration_per_step))
            elif style == "two_tone":
                if step % 4 == 2:
                    result.append(
                        Note(
                            root,
                            octave,
                            duration_per_step * 1.5,
                            velocity=0.65,
                            articulation="staccato",
                        )
                    )
                else:
                    result.append(Note.rest(duration_per_step))
            else:
                # Traditional: pure offbeat, clean and tight
                if step % 4 == 2:
                    result.append(
                        Note(root, octave, duration_per_step, velocity=0.6, articulation="staccato")
                    )
                else:
                    result.append(Note.rest(duration_per_step))

    return result


def ska_bass_line(
    progression: list[tuple[str, str]],
    octave: int = 2,
    style: str = "walking",
    seed: int | None = None,
) -> list[Note]:
    """Generate a ska bass line.

    Ska bass walks. Not jazz-walking with chromatic approach tones -
    ska-walking with root-fifth-octave-fifth patterns that lock to
    the offbeat. The bass and the skank guitar interlock like gears.

    Styles:
        walking:     Classic ska walking bass (root-5th-octave-5th)
        rocksteady:  Slower, deeper, more melodic (Leroy Sibbles style)
        ska_punk:    Driving 8th notes, root-heavy with punk energy

    Args:
        progression: Chord progression.
        octave:      Bass octave.
        style:       "walking", "rocksteady", "ska_punk".
        seed:        Random seed.

    Returns:
        List of Notes.
    """
    import random as _rng
    from ._core import _semi, _NOTE_NAMES

    rng = _rng.Random(seed)
    result: list[Note] = []

    for root_name, shape in progression:
        k = _semi(root_name)
        fifth = (k + 7) % 12
        octave_up = (k + 12) % 12  # same note, will use octave+1

        if style == "ska_punk":
            # Driving 8th notes: root root fifth fifth root root fifth root
            pattern = [k, k, fifth, fifth, k, k, fifth, k]
            for p in pattern:
                result.append(Note(_NOTE_NAMES[p], octave, 0.5, velocity=0.75))

        elif style == "rocksteady":
            # Melodic, slower: root on 1, fifth on 3, passing tone, root
            third = (k + 4) % 12 if "min" not in shape else (k + 3) % 12
            result.append(Note(_NOTE_NAMES[k], octave, 1.0, velocity=0.7))
            result.append(Note(_NOTE_NAMES[fifth], octave, 1.0, velocity=0.6))
            result.append(Note(_NOTE_NAMES[third], octave, 1.0, velocity=0.55))
            result.append(Note(_NOTE_NAMES[k], octave, 1.0, velocity=0.65))

        else:
            # Classic walking: root-5-octave-5 with variation
            pattern_choices = [
                [k, fifth, k, fifth],
                [k, fifth, fifth, k],
                [k, k, fifth, fifth],
            ]
            pattern = rng.choice(pattern_choices)
            for i, p in enumerate(pattern):
                oct = octave + 1 if i == 2 and rng.random() > 0.5 else octave
                result.append(Note(_NOTE_NAMES[p], oct, 1.0, velocity=0.7))

    return result


def ska_horn_riff(
    root: str = "C",
    shape: str = "maj",
    octave: int = 5,
    bars: int = 1,
    style: str = "stab",
    seed: int | None = None,
) -> list[Note]:
    """Generate ska horn section riffs and stabs.

    The horn section in ska punctuates. Short bursts on the offbeats,
    melodic fills between vocal lines, and the occasional unison riff
    that makes everyone in the venue jump. Usually trumpet + trombone
    + sax in tight harmony.

    Styles:
        stab:     Short offbeat hits (dah-dah-DAH rest pattern)
        riff:     Melodic 4-bar figure with call-and-response
        fanfare:  Bold ascending figure for intros/outros

    Args:
        root:    Chord root.
        shape:   Chord quality.
        octave:  Horn octave.
        bars:    Number of bars.
        style:   "stab", "riff", "fanfare".
        seed:    Random seed.

    Returns:
        List of Notes.
    """
    import random as _rng
    from ..engine import CHORD_SHAPES, note_name_to_midi

    rng = _rng.Random(seed)
    offsets = CHORD_SHAPES.get(shape, CHORD_SHAPES.get("maj", [0, 4, 7]))
    root_midi = note_name_to_midi(root, octave)
    result: list[Note] = []

    if style == "fanfare":
        # Ascending chord tones: bold, bright, introductory
        for _ in range(bars):
            for off in offsets[:4]:
                result.append(Note(pitch=root_midi + off, duration=0.5, velocity=0.8))
            result.append(Note(pitch=root_midi + 12, duration=2.0, velocity=0.85))

    elif style == "riff":
        # Melodic figure: scale-based with rhythmic variety
        for _ in range(bars):
            for off in offsets[:3]:
                result.append(Note(pitch=root_midi + off, duration=0.5, velocity=0.7))
            result.append(Note.rest(0.5))
            result.append(Note(pitch=root_midi + offsets[0], duration=1.0, velocity=0.75))
            result.append(Note.rest(1.0))

    else:
        # Stab: short offbeat hits
        for _ in range(bars):
            for step in range(8):
                if step % 2 == 1:  # offbeats
                    midi = root_midi + rng.choice(offsets[:3])
                    result.append(
                        Note(pitch=midi, duration=0.25, velocity=0.7, articulation="staccato")
                    )
                    result.append(Note.rest(0.25))
                else:
                    result.append(Note.rest(0.5))

    return result


# ---------------------------------------------------------------------------
# Metal engine (v170)
# The End of Heartache. Ascendancy. The Poison. Waking the Fallen.
# Two guitars panned hard left and right. Harmonized leads in thirds.
# Palm-muted chugs. Gallop riffs. Clean arpeggios. Double bass runs.
# ---------------------------------------------------------------------------


def harmonize_lead(
    melody: list[Note],
    interval: int = -3,
    key: str = "C",
    scale_name: str = "minor",
) -> list[Note]:
    """Harmonize a lead guitar melody at a diatonic interval.

    The Killswitch Engage / Iron Maiden technique: two guitarists
    playing the same melody a third or sixth apart. Panned hard L/R,
    it creates that wide, soaring sound that defines melodic metal.

    The interval is diatonic (follows the scale) not chromatic. So a
    third in minor could be 3 or 4 semitones depending on the scale
    degree. This is how real guitarists do it.

    Args:
        melody:     Lead guitar melody (the "left" guitar).
        interval:   Diatonic interval in scale degrees. -3 = third below
                    (most common), -6 = sixth below, +3 = third above,
                    -8 = octave below.
        key:        Key for diatonic harmonization.
        scale_name: Scale name ("minor", "major", "harmonic_minor", etc.)

    Returns:
        Harmony part (the "right" guitar). Same rhythm, different pitches.

    Example::

        lead = scale("E", "minor", 5, length=8)
        harmony = harmonize_lead(lead, interval=-3, key="E", scale_name="minor")
        # Pair with panning:
        # Track("guitar_L", pan=-0.8).extend(lead)
        # Track("guitar_R", pan=0.8).extend(harmony)
    """
    from ..engine import SCALES, note_name_to_midi, midi_to_note_name

    scale_intervals = SCALES.get(scale_name, SCALES.get("minor", [0, 2, 3, 5, 7, 8, 10]))
    key_midi = note_name_to_midi(key, 0)

    # Build a lookup: for any MIDI note, find the diatonic note N scale degrees away
    def _diatonic_shift(midi: int, degrees: int) -> int:
        # Find which scale degree this note is closest to
        pc = (midi - key_midi) % 12
        # Find closest scale degree
        best_deg = 0
        best_dist = 99
        for i, s in enumerate(scale_intervals):
            dist = abs(pc - s)
            if dist < best_dist:
                best_dist = dist
                best_deg = i
        # Shift by the requested number of scale degrees
        target_deg = best_deg + degrees
        octave_shift = 0
        while target_deg < 0:
            target_deg += len(scale_intervals)
            octave_shift -= 12
        while target_deg >= len(scale_intervals):
            target_deg -= len(scale_intervals)
            octave_shift += 12
        # Reconstruct MIDI note
        base_octave = ((midi - key_midi) // 12) * 12
        return key_midi + base_octave + scale_intervals[target_deg] + octave_shift

    result: list[Note] = []
    for n in melody:
        if n.pitch is None:
            result.append(n)
        else:
            midi = n.midi
            if midi is not None:
                new_midi = _diatonic_shift(midi, interval)
                result.append(
                    Note(
                        pitch=new_midi,
                        duration=n.duration,
                        velocity=n.velocity,
                        articulation=n.articulation,
                    )
                )
            else:
                result.append(n)
    return result


def dual_guitar(
    melody: list[Note],
    interval: int = -3,
    key: str = "C",
    scale_name: str = "minor",
    pan_width: float = 0.8,
) -> tuple[list[Note], list[Note], float, float]:
    """Create a dual guitar harmony pair ready for panning.

    Convenience wrapper around harmonize_lead. Returns both parts
    and their pan positions. Plug directly into two Tracks.

    Args:
        melody:      Lead melody.
        interval:    Diatonic interval for harmony (-3 = thirds).
        key:         Key.
        scale_name:  Scale.
        pan_width:   How hard to pan (0.8 = mostly L/R, 1.0 = full).

    Returns:
        (guitar_left, guitar_right, pan_left, pan_right)

    Example::

        left, right, pan_l, pan_r = dual_guitar(riff, key="E", scale_name="minor")
        song.add_track(Track("gtr_L", instrument="sawtooth", pan=pan_l)).extend(left)
        song.add_track(Track("gtr_R", instrument="sawtooth", pan=pan_r)).extend(right)
    """
    harmony = harmonize_lead(melody, interval, key, scale_name)
    return melody, harmony, -pan_width, pan_width


def drop_tuning(
    notes: list[Note],
    tuning: str = "drop_d",
) -> list[Note]:
    """Transpose notes to a drop tuning.

    Metal lives in drop tunings. Drop D lets you play power chords
    with one finger. Drop C is where metalcore lives. Drop B is for
    the heavy kids. This shifts all notes down by the appropriate
    number of semitones.

    Tunings:
        standard:  No change (E standard)
        drop_d:    -2 semitones (Drop D)
        drop_c:    -4 semitones (Drop C - the Killswitch tuning)
        drop_b:    -5 semitones (Drop B)
        drop_a:    -7 semitones (Drop A - 7-string territory)

    Args:
        notes:   Input notes.
        tuning:  Tuning name.

    Returns:
        Notes shifted to the target tuning.
    """
    from ..engine import transpose

    offsets = {
        "standard": 0,
        "drop_d": -2,
        "drop_c": -4,
        "drop_c_sharp": -3,
        "drop_b": -5,
        "drop_a": -7,
    }
    shift = offsets.get(tuning, 0)
    if shift == 0:
        return list(notes)
    return transpose(notes, shift)


def metal_drum_pattern(
    bars: int = 1,
    duration: float = 0.25,
    style: str = "double_bass",
    seed: int | None = None,
) -> dict[str, list[Note]]:
    """Generate a metal drum pattern.

    Metal drumming is about controlled violence. Double bass drums at
    speed. Snare on 2 and 4 like a gunshot. Ride or china instead of
    hi-hat during heavy sections. Chris Adler, Matt Halpern, Travis Smith.

    Styles:
        double_bass:  Constant double kick 16ths, snare on 2/4 (KSE, Trivium)
        blast_beat:   Alternating kick-snare 16ths, ride hammering (extreme)
        half_time:    Half-time groove for breakdowns (snare on 3 only)
        gallop:       Triplet kick pattern (Iron Maiden, Trivium Ascendancy)
        breakdown:    Slow, heavy, kick-snare-kick pattern with china crashes

    Args:
        bars:      Number of bars.
        duration:  Duration per 16th note.
        style:     Drum pattern style.
        seed:      Random seed.

    Returns:
        Dict with "kick", "snare", "hat" keys.
    """
    import random as _rng

    rng = _rng.Random(seed)

    kick: list[Note] = []
    snare: list[Note] = []
    hat: list[Note] = []

    for _ in range(bars):
        for step in range(16):
            if style == "double_bass":
                # Double bass: 16th notes on kick, snare on 2 and 4
                kick.append(Note("C", 2, duration, velocity=rng.uniform(0.75, 0.9)))
                if step in (4, 12):
                    snare.append(Note("D", 3, duration, velocity=0.9))
                else:
                    snare.append(Note.rest(duration))
                # Ride bell: 8th notes
                if step % 2 == 0:
                    hat.append(Note("F#", 5, duration, velocity=0.55))
                else:
                    hat.append(Note.rest(duration))

            elif style == "blast_beat":
                # Blast: alternating kick-snare at 16th note speed
                if step % 2 == 0:
                    kick.append(Note("C", 2, duration, velocity=0.85))
                    snare.append(Note.rest(duration))
                else:
                    kick.append(Note.rest(duration))
                    snare.append(Note("D", 3, duration, velocity=0.85))
                # Ride: constant 16ths
                hat.append(Note("F#", 5, duration, velocity=0.5))

            elif style == "half_time":
                # Half-time breakdown: kick on 1, snare on 3, china on 8ths
                if step == 0:
                    kick.append(Note("C", 2, duration, velocity=0.95))
                elif step == 8:
                    kick.append(Note("C", 2, duration, velocity=0.85))
                    snare.append(Note("D", 3, duration, velocity=0.95))
                    hat.append(Note("F#", 5, duration, velocity=0.65))
                    continue
                else:
                    kick.append(Note.rest(duration))
                if step != 8:
                    if step == 8:
                        snare.append(Note("D", 3, duration, velocity=0.95))
                    else:
                        snare.append(Note.rest(duration))
                # China crash: 8th notes for that metalcore breakdown sound
                if step % 4 == 0:
                    hat.append(Note("F#", 5, duration, velocity=0.65))
                else:
                    hat.append(Note.rest(duration))

            elif style == "gallop":
                # Gallop: triplet-feel kick (da-da-DUM da-da-DUM)
                # Approximated in 16ths: kick on 0,1,3, 4,5,7, 8,9,11, 12,13,15
                gallop_hits = {0, 1, 3, 4, 5, 7, 8, 9, 11, 12, 13, 15}
                if step in gallop_hits:
                    vel = 0.9 if step % 4 == 3 else 0.7
                    kick.append(Note("C", 2, duration, velocity=vel))
                else:
                    kick.append(Note.rest(duration))
                if step in (4, 12):
                    snare.append(Note("D", 3, duration, velocity=0.9))
                else:
                    snare.append(Note.rest(duration))
                if step % 2 == 0:
                    hat.append(Note("F#", 5, duration, velocity=0.5))
                else:
                    hat.append(Note.rest(duration))

            elif style == "breakdown":
                # Breakdown: slow and heavy, china on every hit
                if step in (0, 6, 8, 14):
                    kick.append(Note("C", 2, duration, velocity=0.95))
                else:
                    kick.append(Note.rest(duration))
                if step in (4, 12):
                    snare.append(Note("D", 3, duration, velocity=0.95))
                else:
                    snare.append(Note.rest(duration))
                if step in (0, 4, 8, 12):
                    hat.append(Note("F#", 5, duration, velocity=0.7))
                else:
                    hat.append(Note.rest(duration))

    return {"kick": kick, "snare": snare, "hat": hat}


def palm_mute_chug(
    root: str = "E",
    octave: int = 2,
    bars: int = 1,
    pattern: str = "straight",
    duration: float = 0.25,
) -> list[Note]:
    """Generate a palm-muted chugging rhythm guitar pattern.

    The foundation of metal rhythm. One note, palm-muted, played
    relentlessly in a rhythmic pattern. The tight "chugga-chugga" that
    the rhythm guitarist plays while the lead soars above.

    Patterns:
        straight:   Constant 16th notes (Killswitch verse riff)
        syncopated: Accented off-beats with ghost mutes (Lamb of God)
        gallop:     Da-da-DUM triplet feel (Iron Maiden, Trivium)
        djent:      Polyrhythmic stabs with rests (Meshuggah, Periphery)
        breakdown:  Slow open-note chugs for the pit (As I Lay Dying)

    Args:
        root:      Note to chug on (usually lowest string).
        octave:    Octave.
        bars:      Number of bars.
        pattern:   Chug pattern style.
        duration:  Duration per 16th note.

    Returns:
        List of Notes with palm_mute articulation.
    """
    result: list[Note] = []

    for _ in range(bars):
        if pattern == "straight":
            for _ in range(16):
                result.append(Note(root, octave, duration, velocity=0.8, articulation="muted"))

        elif pattern == "syncopated":
            # 0=accent, 1=ghost, 2=rest
            seq = [0, 1, 0, 1, 2, 0, 1, 0, 0, 1, 2, 0, 1, 0, 0, 1]
            for s in seq:
                if s == 0:
                    result.append(Note(root, octave, duration, velocity=0.85, articulation="muted"))
                elif s == 1:
                    result.append(Note(root, octave, duration, velocity=0.35, articulation="muted"))
                else:
                    result.append(Note.rest(duration))

        elif pattern == "gallop":
            # Da-da-DUM (short-short-long feel in 16th groupings)
            for beat in range(4):
                result.append(Note(root, octave, duration, velocity=0.65, articulation="muted"))
                result.append(Note(root, octave, duration, velocity=0.65, articulation="muted"))
                result.append(Note(root, octave, duration, velocity=0.9, articulation="muted"))
                result.append(Note.rest(duration))

        elif pattern == "djent":
            # Polyrhythmic stabs: hits then silence
            seq = [1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0]
            for s in seq:
                if s:
                    result.append(Note(root, octave, duration, velocity=0.95, articulation="muted"))
                else:
                    result.append(Note.rest(duration))

        elif pattern == "breakdown":
            # Slow open chugs: hit, ring, hit, ring (usually in half time)
            for beat in range(4):
                result.append(Note(root, octave, duration * 2, velocity=0.95))
                result.append(Note.rest(duration * 2))

    return result


def clean_arpeggio(
    root: str = "E",
    shape: str = "min",
    octave: int = 4,
    bars: int = 1,
    duration: float = 0.5,
    style: str = "ascending",
) -> list[Note]:
    """Generate a clean guitar arpeggio section.

    The quiet before the storm. Every 2004 metalcore track has a clean
    section - arpeggiated chords with delay and reverb, vocals go clean,
    the crowd catches its breath. Then the double bass comes back in
    and the pit opens up again. Bullet for My Valentine "Tears Do not Fall"
    intro energy.

    Styles:
        ascending:   Simple up arpeggio (root-3-5-octave)
        descending:  Top down
        fingerpick:  Travis picking pattern (1-3-2-3-1-3-2-3)
        sweep:       Fast sweep across chord tones

    Args:
        root:      Chord root.
        shape:     Chord quality.
        octave:    Base octave.
        bars:      Number of bars.
        duration:  Duration per note.
        style:     Arpeggio pattern.

    Returns:
        List of Notes (clean, no articulation = normal guitar sound).
    """
    from ..engine import CHORD_SHAPES, note_name_to_midi

    offsets = CHORD_SHAPES.get(shape, CHORD_SHAPES.get("min", [0, 3, 7]))
    root_midi = note_name_to_midi(root, octave)
    tones = [root_midi + o for o in offsets[:4]]  # max 4 chord tones
    # Add octave if we do not have 4
    while len(tones) < 4:
        tones.append(tones[0] + 12)

    result: list[Note] = []
    for _ in range(bars):
        if style == "ascending":
            for t in tones:
                result.append(Note(pitch=t, duration=duration, velocity=0.5))

        elif style == "descending":
            for t in reversed(tones):
                result.append(Note(pitch=t, duration=duration, velocity=0.5))

        elif style == "fingerpick":
            # Travis pick: bass-high-mid-high-bass-high-mid-high
            pick = [tones[0], tones[3], tones[1], tones[3], tones[0], tones[2], tones[1], tones[2]]
            for p in pick:
                result.append(Note(pitch=p, duration=duration * 0.5, velocity=0.45))

        elif style == "sweep":
            # Fast sweep up then down
            sweep_dur = duration * 0.25
            for t in tones:
                result.append(Note(pitch=t, duration=sweep_dur, velocity=0.6))
            for t in reversed(tones[:-1]):
                result.append(Note(pitch=t, duration=sweep_dur, velocity=0.55))
            # Hold the last note
            remaining = duration * 4 - sweep_dur * (len(tones) * 2 - 1)
            if remaining > 0:
                result.append(Note(pitch=tones[-1], duration=remaining, velocity=0.5))

    return result


def quantize_harmonic_rhythm(
    progression: list[tuple[str, str]],
    target_chords_per_bar: int = 1,
) -> list[tuple[str, str]]:
    """Quantize a progression to a target harmonic rhythm.

    If target is 1 chord per bar and the input has 2, keep every other chord.
    If target is 2 and input has 1, duplicate each chord.

    Args:
        progression:          Input progression.
        target_chords_per_bar: Desired density (1 = whole notes, 2 = half notes, 4 = quarters).

    Returns:
        Quantized progression.
    """
    if not progression or target_chords_per_bar <= 0:
        return list(progression)

    current_density = len(progression)

    if target_chords_per_bar >= current_density:
        # Expand: repeat each chord to fill
        ratio = target_chords_per_bar // max(current_density, 1)
        result: list[tuple[str, str]] = []
        for chord in progression:
            result.extend([chord] * max(ratio, 1))
        return result[: target_chords_per_bar * (len(progression) // current_density or 1)]
    else:
        # Contract: sample evenly
        step = max(1, current_density // target_chords_per_bar)
        return [progression[i] for i in range(0, len(progression), step)][:target_chords_per_bar]
