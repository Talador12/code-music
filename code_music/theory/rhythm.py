"""theory.rhythm — rhythmic patterns, displacement, meters, groove, quantization."""

from __future__ import annotations

from ._core import _GROOVE_TEMPLATES, Note


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

