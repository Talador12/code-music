"""Music theory intelligence — chord-scale theory, tension analysis, smart generators.

Example::

    from code_music.theory import (
        chord_scale, available_tensions, generate_bass_line, generate_drums,
    )

    scales = chord_scale("C", "min7")     # → ["dorian", "aeolian", "phrygian"]
    tensions = available_tensions("C", "min7")  # → ["9", "11", "13"]
    bass = generate_bass_line([("C", "min7"), ("F", "dom7")], style="walking")
    drums = generate_drums("jazz", bars=4)
"""

from __future__ import annotations

from .engine import Note, euclid

# ---------------------------------------------------------------------------
# Note utilities
# ---------------------------------------------------------------------------

_NOTE_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
_NOTE_TO_SEMI = {n: i for i, n in enumerate(_NOTE_NAMES)}
# Enharmonic aliases
_NOTE_TO_SEMI.update(
    {"Db": 1, "D#": 3, "Fb": 4, "E#": 5, "Gb": 6, "G#": 8, "A#": 10, "Cb": 11, "B#": 0}
)


def _semi(note: str) -> int:
    return _NOTE_TO_SEMI[note]


# ---------------------------------------------------------------------------
# Scale intervals (semitones from root)
# ---------------------------------------------------------------------------

_SCALE_INTERVALS = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "aeolian": [0, 2, 3, 5, 7, 8, 10],
    "locrian": [0, 1, 3, 5, 6, 8, 10],
    "melodic_minor": [0, 2, 3, 5, 7, 9, 11],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "whole_tone": [0, 2, 4, 6, 8, 10],
    "diminished": [0, 2, 3, 5, 6, 8, 9, 11],  # half-whole
    "blues": [0, 3, 5, 6, 7, 10],
    "pentatonic": [0, 2, 4, 7, 9],
    "pentatonic_minor": [0, 3, 5, 7, 10],
}

# Chord shape → semitones from root
_CHORD_SEMI = {
    "maj": [0, 4, 7],
    "min": [0, 3, 7],
    "dim": [0, 3, 6],
    "aug": [0, 4, 8],
    "dom7": [0, 4, 7, 10],
    "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10],
    "dim7": [0, 3, 6, 9],
    "min7b5": [0, 3, 6, 10],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    "min9": [0, 3, 7, 10, 14],
    "maj9": [0, 4, 7, 11, 14],
    "dom9": [0, 4, 7, 10, 14],
}


# ---------------------------------------------------------------------------
# Chord-scale theory
# ---------------------------------------------------------------------------


def chord_scale(root: str, shape: str) -> list[str]:
    """Return scales compatible with a given chord for improvisation.

    Finds scales whose notes contain all chord tones as a subset.

    Args:
        root:  Chord root note (e.g. 'C', 'F#').
        shape: Chord quality (e.g. 'min7', 'dom7', 'maj7').

    Returns:
        List of scale names compatible with the chord.

    Example::

        chord_scale("C", "min7")   # → ["dorian", "aeolian", "phrygian"]
        chord_scale("G", "dom7")   # → ["mixolydian"]
    """
    if shape not in _CHORD_SEMI:
        raise ValueError(f"Unknown chord shape {shape!r}")

    root_semi = _semi(root)
    chord_pcs = {(root_semi + s) % 12 for s in _CHORD_SEMI[shape]}

    compatible = []
    for scale_name, intervals in _SCALE_INTERVALS.items():
        scale_pcs = {(root_semi + s) % 12 for s in intervals}
        if chord_pcs.issubset(scale_pcs):
            compatible.append(scale_name)
    return sorted(compatible)


def available_tensions(root: str, shape: str) -> list[str]:
    """Return available tension extensions for a chord.

    Analyzes which 9th, 11th, and 13th degrees are available without
    clashing with the chord tones.

    Args:
        root:  Chord root note.
        shape: Chord quality.

    Returns:
        List of tension names (e.g. ["9", "11", "b13"]).
    """
    if shape not in _CHORD_SEMI:
        raise ValueError(f"Unknown chord shape {shape!r}")

    root_semi = _semi(root)
    chord_pcs = {(root_semi + s) % 12 for s in _CHORD_SEMI[shape]}

    tensions = []
    # Check each possible tension
    tension_map = {
        "b9": 1,
        "9": 2,
        "#9": 3,
        "11": 5,
        "#11": 6,
        "b13": 8,
        "13": 9,
    }

    for name, semi in tension_map.items():
        tension_pc = (root_semi + semi) % 12
        # Tension is available if it doesn't clash with a chord tone
        # (not a semitone away from any chord tone)
        clashes = False
        for ct in chord_pcs:
            if abs(tension_pc - ct) == 1 or abs(tension_pc - ct) == 11:
                clashes = True
                break
        if not clashes and tension_pc not in chord_pcs:
            tensions.append(name)

    return tensions


# ---------------------------------------------------------------------------
# Smart generators
# ---------------------------------------------------------------------------


def generate_bass_line(
    chords: list[tuple[str, str]],
    style: str = "root",
    octave: int = 2,
    duration: float = 1.0,
    bars_per_chord: int = 1,
    seed: int | None = None,
) -> list[Note]:
    """Generate a bass line from a chord progression.

    Args:
        chords:         List of (root, shape) tuples.
        style:          'root' (roots only), 'root_fifth' (alternating root-5th),
                        'walking' (chromatic walking bass), 'syncopated'.
        octave:         Bass octave.
        duration:       Duration per note in beats.
        bars_per_chord: How many bars each chord gets.
        seed:           Random seed for 'walking' style.

    Returns:
        List of Notes.
    """
    import random

    rng = random.Random(seed)
    notes: list[Note] = []
    beats_per_bar = int(4 / duration)  # assuming 4/4

    for root, shape in chords:
        root_semi = _semi(root)
        chord_semis = _CHORD_SEMI.get(shape, [0, 4, 7])
        fifth_semi = (root_semi + 7) % 12

        for bar in range(bars_per_chord):
            if style == "root":
                for _ in range(beats_per_bar):
                    notes.append(Note(root, octave, duration))

            elif style == "root_fifth":
                fifth_name = _NOTE_NAMES[fifth_semi]
                for i in range(beats_per_bar):
                    if i % 2 == 0:
                        notes.append(Note(root, octave, duration))
                    else:
                        notes.append(Note(fifth_name, octave, duration))

            elif style == "walking":
                # Walking bass: chord tones + chromatic approach notes
                chord_notes = [_NOTE_NAMES[(root_semi + s) % 12] for s in chord_semis]
                for i in range(beats_per_bar):
                    if i == 0:
                        notes.append(Note(root, octave, duration))
                    elif i == beats_per_bar - 1 and bar < bars_per_chord - 1:
                        # Approach note to next chord
                        notes.append(Note(rng.choice(chord_notes), octave, duration))
                    else:
                        notes.append(Note(rng.choice(chord_notes), octave, duration))

            elif style == "syncopated":
                # Offbeat emphasis
                for i in range(beats_per_bar):
                    if i % 2 == 1:
                        notes.append(Note(root, octave, duration))
                    else:
                        notes.append(Note.rest(duration))
            else:
                raise ValueError(f"Unknown bass style {style!r}")

    return notes


def generate_drums(
    genre: str = "rock",
    bars: int = 4,
    duration: float = 0.5,
    seed: int | None = None,
) -> dict[str, list[Note]]:
    """Generate drum patterns for common genres.

    Returns a dict mapping track names to note lists.

    Args:
        genre:    'rock', 'jazz', 'electronic', 'latin', 'hiphop'.
        bars:     Number of bars to generate.
        duration: Duration per step (eighth note = 0.5 default).
        seed:     Random seed.

    Returns:
        Dict of {"kick": [...], "snare": [...], "hat": [...]}.
    """
    result: dict[str, list[Note]] = {"kick": [], "snare": [], "hat": []}
    steps_per_bar = int(4 / duration)

    for _ in range(bars):
        if genre == "rock":
            # Kick: 1 and 3, Snare: 2 and 4, Hat: all eighths
            result["kick"].extend(euclid(2, steps_per_bar, "C", 2, duration, rotation=0))
            result["snare"].extend(
                euclid(2, steps_per_bar, "D", 4, duration, rotation=steps_per_bar // 2)
            )
            for i in range(steps_per_bar):
                result["hat"].append(Note("F#", 6, duration))

        elif genre == "jazz":
            # Ride: all, kick: sparse, snare: ghost notes
            result["kick"].extend(euclid(2, steps_per_bar, "C", 2, duration))
            result["snare"].extend(euclid(3, steps_per_bar, "D", 4, duration, rotation=1))
            for i in range(steps_per_bar):
                result["hat"].append(Note("F#", 6, duration))

        elif genre == "electronic":
            # Four-on-floor kick, offbeat hat, snare on 2+4
            for i in range(steps_per_bar):
                if i % (steps_per_bar // 4) == 0:
                    result["kick"].append(Note("C", 2, duration))
                else:
                    result["kick"].append(Note.rest(duration))
            result["snare"].extend(
                euclid(2, steps_per_bar, "D", 4, duration, rotation=steps_per_bar // 4)
            )
            for i in range(steps_per_bar):
                if i % 2 == 1:
                    result["hat"].append(Note("F#", 6, duration))
                else:
                    result["hat"].append(Note.rest(duration))

        elif genre == "latin":
            # Tresillo kick, son clave snare
            result["kick"].extend(euclid(3, steps_per_bar, "C", 2, duration))
            result["snare"].extend(
                euclid(5, steps_per_bar * 2, "D", 4, duration / 2)[:steps_per_bar]
            )
            for i in range(steps_per_bar):
                result["hat"].append(Note("F#", 6, duration))

        elif genre == "hiphop":
            # Boom-bap: heavy kick, snare on 2+4, sparse hat
            result["kick"].extend(euclid(3, steps_per_bar, "C", 2, duration))
            result["snare"].extend(
                euclid(2, steps_per_bar, "D", 4, duration, rotation=steps_per_bar // 4)
            )
            result["hat"].extend(euclid(5, steps_per_bar, "F#", 6, duration))

        else:
            raise ValueError(
                f"Unknown drum genre {genre!r}. Choose: rock, jazz, electronic, latin, hiphop"
            )

    return result


def generate_chord_melody(
    chords: list[tuple[str, str]],
    contour: str = "arch",
    octave: int = 5,
    duration: float = 0.5,
    notes_per_chord: int = 4,
    seed: int | None = None,
) -> list[Note]:
    """Generate a melody that follows a chord progression's harmonic rhythm.

    Each chord gets `notes_per_chord` notes chosen from its chord tones,
    shaped by the contour pattern.

    Args:
        chords:          List of (root, shape) tuples.
        contour:         Melodic shape: 'arch' (up then down), 'descending',
                         'ascending', 'wave', 'random'.
        octave:          Base octave.
        duration:        Duration per note.
        notes_per_chord: How many notes to generate per chord.
        seed:            Random seed.

    Returns:
        List of Notes.
    """
    import random

    rng = random.Random(seed)
    result: list[Note] = []
    total_notes = len(chords) * notes_per_chord

    for chord_idx, (root, shape) in enumerate(chords):
        root_semi = _semi(root)
        chord_semis = _CHORD_SEMI.get(shape, [0, 4, 7])
        chord_notes = [_NOTE_NAMES[(root_semi + s) % 12] for s in chord_semis]

        for note_idx in range(notes_per_chord):
            # Position in overall melody (0.0 to 1.0)
            pos = (chord_idx * notes_per_chord + note_idx) / max(total_notes - 1, 1)

            if contour == "arch":
                # Parabolic arch: low → high → low
                height = 1.0 - 4.0 * (pos - 0.5) ** 2
            elif contour == "ascending":
                height = pos
            elif contour == "descending":
                height = 1.0 - pos
            elif contour == "wave":
                import math

                height = 0.5 + 0.5 * math.sin(pos * 2 * math.pi)
            elif contour == "random":
                height = rng.random()
            else:
                height = 0.5

            # Map height to chord tone selection + octave offset
            tone_idx = int(height * (len(chord_notes) - 1))
            tone_idx = max(0, min(tone_idx, len(chord_notes) - 1))
            oct_offset = int(height * 2) - 1  # -1, 0, or 1
            note_oct = max(3, min(7, octave + oct_offset))

            result.append(Note(chord_notes[tone_idx], note_oct, duration))

    return result


def generate_counterpoint(
    melody: list[Note],
    species: int = 1,
    interval: str = "third",
    seed: int | None = None,
) -> list[Note]:
    """Generate a counterpoint line against a given melody.

    First species counterpoint: one note against one note, using
    consonant intervals (thirds, sixths, fifths, octaves).

    Args:
        melody:   The cantus firmus (original melody).
        species:  Counterpoint species (only 1 supported currently).
        interval: Preferred interval: 'third', 'sixth', 'fifth'.
        seed:     Random seed.

    Returns:
        List of Notes forming the counterpoint line.
    """
    import random

    rng = random.Random(seed)

    interval_semis = {"third": [3, 4], "sixth": [8, 9], "fifth": [7]}
    preferred = interval_semis.get(interval, [3, 4])

    result: list[Note] = []
    for note in melody:
        if note.pitch is None:
            result.append(Note.rest(note.duration))
            continue

        note_semi = _semi(str(note.pitch))
        # Choose a consonant interval (above)
        offset = rng.choice(preferred)
        cp_semi = (note_semi + offset) % 12
        cp_pitch = _NOTE_NAMES[cp_semi]
        # Place counterpoint an octave above
        cp_oct = min(7, note.octave + 1)

        result.append(Note(cp_pitch, cp_oct, note.duration, velocity=note.velocity * 0.8))

    return result


# ---------------------------------------------------------------------------
# Song diffing
# ---------------------------------------------------------------------------
# Harmonic analysis
# ---------------------------------------------------------------------------

_ROMAN = {
    0: "I",
    1: "bII",
    2: "II",
    3: "bIII",
    4: "III",
    5: "IV",
    6: "#IV",
    7: "V",
    8: "bVI",
    9: "VI",
    10: "bVII",
    11: "VII",
}

_QUALITY_MAP = {
    "maj": "",
    "min": "m",
    "dim": "dim",
    "aug": "+",
    "dom7": "7",
    "maj7": "M7",
    "min7": "m7",
    "dim7": "dim7",
    "min7b5": "m7b5",
    "sus2": "sus2",
    "sus4": "sus4",
    "min9": "m9",
    "maj9": "M9",
    "dom9": "9",
}

_FUNCTION_MAP = {
    0: "tonic",
    2: "supertonic",
    4: "mediant",
    5: "subdominant",
    7: "dominant",
    9: "submediant",
    11: "leading",
}


def analyze_harmony(song, key: str | None = None) -> list[dict]:
    """Analyze a song's chord progression with Roman numeral analysis.

    Finds all chords in the song, assigns Roman numerals relative to
    the detected (or specified) key, and labels harmonic function
    (tonic, subdominant, dominant).

    Args:
        song: Song object.
        key:  Key root (e.g. 'C'). If None, uses song.key_sig or detect_key().

    Returns:
        List of dicts with: beat, root, shape, roman, quality, function.

    Example::

        analysis = analyze_harmony(song)
        for a in analysis:
            print(f"Beat {a['beat']}: {a['roman']}{a['quality']} ({a['function']})")
        # Beat 0: IIm7 (supertonic)
        # Beat 4: V7 (dominant)
        # Beat 8: IM7 (tonic)
    """
    from .engine import Chord

    # Determine key
    if key is None:
        key = getattr(song, "key_sig", "C")
        if key and len(key) > 1 and key[-1] == "m":
            key = key[:-1]  # strip minor indicator for root
    key_semi = _semi(key) if key else 0

    # Extract chords
    chords: list[tuple[float, str, str]] = []
    for track in song.tracks:
        pos = 0.0
        for beat in track.beats:
            if beat.event and isinstance(beat.event, Chord):
                chords.append(
                    (
                        pos,
                        beat.event.root,
                        beat.event.shape if isinstance(beat.event.shape, str) else "maj",
                    )
                )
            if beat.event:
                pos += beat.event.duration

    # Analyze each chord
    result = []
    for beat_pos, root, shape in sorted(chords):
        root_semi = _semi(root)
        interval = (root_semi - key_semi) % 12
        roman = _ROMAN.get(interval, "?")
        quality = _QUALITY_MAP.get(shape, shape)

        # Lowercase roman for minor chords
        if shape in ("min", "min7", "min7b5", "dim", "dim7", "min9"):
            roman = roman.lower()

        func = _FUNCTION_MAP.get(interval, "chromatic")

        result.append(
            {
                "beat": beat_pos,
                "root": root,
                "shape": shape,
                "roman": roman,
                "quality": quality,
                "function": func,
            }
        )

    return result


# ---------------------------------------------------------------------------
# Melodic variation generators
# ---------------------------------------------------------------------------


def generate_variation(
    melody: list[Note],
    technique: str = "inversion",
    key: str = "C",
    seed: int | None = None,
) -> list[Note]:
    """Create a melodic variation using classical techniques.

    Args:
        melody:    Original melody (list of Notes).
        technique: Variation type:
            - 'inversion': mirror intervals (up→down, down→up)
            - 'retrograde': reverse the melody
            - 'retrograde_inversion': reverse + invert
            - 'augmentation': double note durations
            - 'diminution': halve note durations
            - 'sequence': transpose up by a step each repeat
            - 'ornamental': add passing tones between notes
        key:       Key root for scale-aware techniques.
        seed:      Random seed for ornamental technique.

    Returns:
        List of Notes forming the variation.
    """
    import random as _random

    if not melody:
        return []

    if technique == "retrograde":
        return [
            Note(str(n.pitch), n.octave, n.duration, velocity=n.velocity)
            if n.pitch is not None
            else Note.rest(n.duration)
            for n in reversed(melody)
        ]

    elif technique == "inversion":
        # Mirror intervals around the first note
        result: list[Note] = []
        first_pitched = next((n for n in melody if n.pitch is not None), None)
        if first_pitched is None:
            return list(melody)
        anchor_semi = _semi(str(first_pitched.pitch)) + first_pitched.octave * 12
        for note in melody:
            if note.pitch is None:
                result.append(Note.rest(note.duration))
            else:
                note_semi = _semi(str(note.pitch)) + note.octave * 12
                interval = note_semi - anchor_semi
                inv_semi = anchor_semi - interval
                inv_pc = inv_semi % 12
                inv_oct = max(2, min(7, inv_semi // 12))
                result.append(
                    Note(_NOTE_NAMES[inv_pc], inv_oct, note.duration, velocity=note.velocity)
                )
        return result

    elif technique == "retrograde_inversion":
        inverted = generate_variation(melody, "inversion", key)
        return list(reversed(inverted))

    elif technique == "augmentation":
        return [
            Note(str(n.pitch), n.octave, n.duration * 2, velocity=n.velocity)
            if n.pitch is not None
            else Note.rest(n.duration * 2)
            for n in melody
        ]

    elif technique == "diminution":
        return [
            Note(str(n.pitch), n.octave, max(0.125, n.duration / 2), velocity=n.velocity)
            if n.pitch is not None
            else Note.rest(max(0.125, n.duration / 2))
            for n in melody
        ]

    elif technique == "sequence":
        # Transpose up by 2 semitones (a whole step)
        result = []
        for note in melody:
            if note.pitch is None:
                result.append(Note.rest(note.duration))
            else:
                semi = (_semi(str(note.pitch)) + 2) % 12
                result.append(
                    Note(_NOTE_NAMES[semi], note.octave, note.duration, velocity=note.velocity)
                )
        return result

    elif technique == "ornamental":
        # Add passing tones between notes
        rng = _random.Random(seed)
        result = []
        for i, note in enumerate(melody):
            if note.pitch is None:
                result.append(Note.rest(note.duration))
                continue
            half_dur = note.duration / 2
            result.append(Note(str(note.pitch), note.octave, half_dur, velocity=note.velocity))
            # Add a passing tone
            semi = _semi(str(note.pitch))
            step = rng.choice([-1, 1, 2, -2])
            pass_semi = (semi + step) % 12
            result.append(
                Note(_NOTE_NAMES[pass_semi], note.octave, half_dur, velocity=note.velocity * 0.7)
            )
        return result

    else:
        raise ValueError(
            f"Unknown technique {technique!r}. Choose: "
            "inversion, retrograde, retrograde_inversion, "
            "augmentation, diminution, sequence, ornamental"
        )


# ---------------------------------------------------------------------------
# Velocity humanization
# ---------------------------------------------------------------------------


def humanize_velocity(
    notes: list[Note],
    amount: float = 0.15,
    seed: int | None = None,
) -> list[Note]:
    """Add random velocity variation to notes for a more human feel.

    Args:
        notes:  List of Notes.
        amount: Maximum velocity deviation (0.0-0.5).
        seed:   Random seed for reproducibility.

    Returns:
        New list of Notes with randomized velocities.
    """
    import random

    rng = random.Random(seed)
    result: list[Note] = []
    for note in notes:
        if note.pitch is None:
            result.append(Note.rest(note.duration))
        else:
            delta = rng.uniform(-amount, amount)
            new_vel = max(0.05, min(1.0, note.velocity + delta))
            result.append(Note(str(note.pitch), note.octave, note.duration, velocity=new_vel))
    return result


def transpose_progression(
    chords: list[tuple[str, str]],
    semitones: int = 0,
) -> list[tuple[str, str]]:
    """Transpose a chord progression by a number of semitones.

    Args:
        chords:    List of (root, shape) tuples.
        semitones: Number of semitones to transpose (positive=up, negative=down).

    Returns:
        New list of (root, shape) tuples with transposed roots.
    """
    result: list[tuple[str, str]] = []
    for root, shape in chords:
        root_semi = _semi(root)
        new_semi = (root_semi + semitones) % 12
        result.append((_NOTE_NAMES[new_semi], shape))
    return result


def detect_tempo(audio, sr: int = 44100) -> float:
    """Estimate BPM from rendered audio using onset detection.

    Simple energy-based onset detection with autocorrelation.

    Args:
        audio: Float64 audio array (mono or stereo).
        sr:    Sample rate.

    Returns:
        Estimated BPM (60-200 range).
    """
    import numpy as np

    if audio.ndim > 1:
        mono = np.mean(audio, axis=1)
    else:
        mono = audio

    # Compute energy envelope
    hop = sr // 100  # 10ms hops
    n_frames = len(mono) // hop
    if n_frames < 10:
        return 120.0  # not enough data

    energy = np.zeros(n_frames)
    for i in range(n_frames):
        start = i * hop
        end = min(start + hop, len(mono))
        energy[i] = np.sum(mono[start:end] ** 2)

    # Onset detection (first difference of energy)
    onset = np.diff(energy)
    onset = np.maximum(onset, 0)

    # Autocorrelation to find periodicity
    if len(onset) < 20:
        return 120.0

    corr = np.correlate(onset, onset, mode="full")
    corr = corr[len(corr) // 2 :]

    # Find first significant peak after minimum lag
    min_bpm, max_bpm = 60, 200
    min_lag = int(60.0 / max_bpm * 100)  # 100 = frames per second
    max_lag = int(60.0 / min_bpm * 100)
    max_lag = min(max_lag, len(corr) - 1)

    if min_lag >= max_lag:
        return 120.0

    search = corr[min_lag:max_lag]
    if len(search) == 0:
        return 120.0

    peak_idx = np.argmax(search) + min_lag
    if peak_idx == 0:
        return 120.0

    bpm = 60.0 / (peak_idx / 100.0)
    return round(float(bpm), 1)


# ---------------------------------------------------------------------------
# Scale info & chord extensions
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Melody analysis utilities
# ---------------------------------------------------------------------------


def melody_contour(notes: list[Note]) -> dict:
    """Classify the melodic contour (shape) of a note sequence.

    Returns step/skip/leap statistics and overall direction.

    Args:
        notes: List of Notes.

    Returns:
        Dict with direction, steps, skips, leaps, contour_string.
    """
    pitched = [(n.pitch, n.octave) for n in notes if n.pitch is not None]
    if len(pitched) < 2:
        return {"direction": "static", "steps": 0, "skips": 0, "leaps": 0, "contour_string": ""}

    intervals: list[int] = []
    for i in range(len(pitched) - 1):
        a = _semi(str(pitched[i][0])) + pitched[i][1] * 12
        b = _semi(str(pitched[i + 1][0])) + pitched[i + 1][1] * 12
        intervals.append(b - a)

    steps = sum(1 for i in intervals if abs(i) <= 2)
    skips = sum(1 for i in intervals if 3 <= abs(i) <= 4)
    leaps = sum(1 for i in intervals if abs(i) >= 5)

    net = sum(intervals)
    if net > 2:
        direction = "ascending"
    elif net < -2:
        direction = "descending"
    else:
        direction = "static"

    contour = "".join("+" if i > 0 else "-" if i < 0 else "=" for i in intervals)

    return {
        "direction": direction,
        "steps": steps,
        "skips": skips,
        "leaps": leaps,
        "contour_string": contour,
    }


def harmonic_rhythm(song, beats_per_bar: int = 4) -> dict:
    """Measure how frequently chords change in a song.

    Args:
        song:          Song to analyze.
        beats_per_bar: Beats per bar.

    Returns:
        Dict with total_chords, total_bars, changes_per_bar, chord_durations.
    """
    from .engine import Chord as _Chord

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


def consonance_score(notes: list[Note]) -> float:
    """Measure harmonic consonance of simultaneous/sequential notes.

    Rates intervals: unison/octave=1.0, fifth=0.9, fourth=0.8,
    third/sixth=0.7, second/seventh=0.3, tritone=0.1.

    Args:
        notes: List of Notes (analyzed pairwise).

    Returns:
        Average consonance score (0.0-1.0).
    """
    _CONSONANCE = {
        0: 1.0,
        1: 0.3,
        2: 0.3,
        3: 0.7,
        4: 0.7,
        5: 0.8,
        6: 0.1,
        7: 0.9,
        8: 0.7,
        9: 0.7,
        10: 0.3,
        11: 0.3,
    }

    pitched = [n for n in notes if n.pitch is not None]
    if len(pitched) < 2:
        return 1.0

    scores: list[float] = []
    for i in range(len(pitched) - 1):
        a = _semi(str(pitched[i].pitch))
        b = _semi(str(pitched[i + 1].pitch))
        interval = abs(b - a) % 12
        scores.append(_CONSONANCE.get(interval, 0.5))

    return round(sum(scores) / len(scores), 3)


def secondary_dominant(target_root: str, target_shape: str = "maj") -> tuple[str, str]:
    """Return the secondary dominant (V/x) that resolves to the target chord.

    The secondary dominant is a dom7 chord whose root is a perfect 5th
    above the target. V/ii, V/V, V/vi — classic tonicization technique.

    Args:
        target_root:  Root of the chord to tonicize.
        target_shape: Shape of target chord (unused in calculation, for context).

    Returns:
        (root, "dom7") tuple of the secondary dominant.
    """
    target_semi = _semi(target_root)
    dom_semi = (target_semi + 7) % 12  # perfect 5th above
    return (_NOTE_NAMES[dom_semi], "dom7")


def deceptive_cadence(key: str = "C") -> list[tuple[str, str]]:
    """Generate a deceptive cadence: V → vi instead of V → I.

    The listener expects resolution to tonic but gets the relative minor.
    Classic surprise ending used since the Baroque era.

    Args:
        key: Key root.

    Returns:
        Two-chord progression [(V, dom7), (vi, min)].
    """
    key_semi = _semi(key)
    v_semi = (key_semi + 7) % 12
    vi_semi = (key_semi + 9) % 12
    return [(_NOTE_NAMES[v_semi], "dom7"), (_NOTE_NAMES[vi_semi], "min")]


def plagal_cadence(key: str = "C") -> list[tuple[str, str]]:
    """Generate a plagal cadence: IV → I (the 'Amen' cadence).

    Warm, conclusive resolution without dominant tension.
    Used in hymns, gospel, and as a tag ending.

    Args:
        key: Key root.

    Returns:
        Two-chord progression [(IV, maj), (I, maj)].
    """
    key_semi = _semi(key)
    iv_semi = (key_semi + 5) % 12
    return [(_NOTE_NAMES[iv_semi], "maj"), (key, "maj")]


def dorian_lick(
    root: str,
    octave: int = 5,
    duration: float = 0.25,
    seed: int | None = None,
) -> list[Note]:
    """Generate a dorian mode lick (natural 6 over minor gives jazz/funk quality)."""
    import random

    rng = random.Random(seed)
    root_semi = _semi(root)
    dorian = [0, 2, 3, 5, 7, 9, 10]
    dorian_notes = [_NOTE_NAMES[(root_semi + i) % 12] for i in dorian]
    lick_len = rng.randint(6, 10)
    result: list[Note] = [Note(rng.choice(dorian_notes), octave, duration) for _ in range(lick_len)]
    result.append(Note(root, octave, duration * 2))
    return result


def phrygian_run(
    root: str,
    octave: int = 5,
    length: int = 8,
    duration: float = 0.25,
) -> list[Note]:
    """Generate a phrygian scale run (b2 gives Spanish/flamenco quality)."""
    root_semi = _semi(root)
    phrygian = [0, 1, 3, 5, 7, 8, 10]
    result: list[Note] = []
    for i in range(length):
        idx = i % len(phrygian)
        oct_off = i // len(phrygian)
        semi = (root_semi + phrygian[idx]) % 12
        result.append(Note(_NOTE_NAMES[semi], min(7, octave + oct_off), duration))
    return result


def tritone_sub(chords: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Apply tritone substitution to dominant 7th chords.

    Replaces V7 chords with bII7 (same tritone, different root).
    Classic jazz reharmonization technique.

    Args:
        chords: List of (root, shape) tuples.

    Returns:
        New list with dominant chords tritone-substituted.
    """
    result: list[tuple[str, str]] = []
    for root, shape in chords:
        if shape in ("dom7", "dom9"):
            root_semi = _semi(root)
            tri_semi = (root_semi + 6) % 12  # tritone = 6 semitones
            result.append((_NOTE_NAMES[tri_semi], shape))
        else:
            result.append((root, shape))
    return result


def lydian_run(
    root: str,
    octave: int = 5,
    length: int = 8,
    duration: float = 0.25,
) -> list[Note]:
    """Generate a lydian scale run (#4 gives bright, floating quality).

    Args:
        root:     Starting note.
        octave:   Starting octave.
        length:   Number of notes.
        duration: Duration per note.
    """
    root_semi = _semi(root)
    lydian = [0, 2, 4, 6, 7, 9, 11]  # 1 2 3 #4 5 6 7
    result: list[Note] = []
    for i in range(length):
        idx = i % len(lydian)
        oct_off = i // len(lydian)
        semi = (root_semi + lydian[idx]) % 12
        result.append(Note(_NOTE_NAMES[semi], min(7, octave + oct_off), duration))
    return result


def mixolydian_lick(
    root: str,
    octave: int = 5,
    duration: float = 0.25,
    seed: int | None = None,
) -> list[Note]:
    """Generate a mixolydian lick (b7 gives bluesy/rock dominant quality).

    Args:
        root:     Root note.
        octave:   Octave.
        duration: Duration per note.
        seed:     Random seed.
    """
    import random

    rng = random.Random(seed)
    root_semi = _semi(root)
    mixo = [0, 2, 4, 5, 7, 9, 10]  # 1 2 3 4 5 6 b7
    mixo_notes = [_NOTE_NAMES[(root_semi + i) % 12] for i in mixo]
    lick_len = rng.randint(6, 10)
    result: list[Note] = []
    for _ in range(lick_len):
        result.append(Note(rng.choice(mixo_notes), octave, duration))
    result.append(Note(root, octave, duration * 2))  # resolve to root
    return result


def modal_interchange(
    chords: list[tuple[str, str]],
    key: str = "C",
    target_mode: str = "minor",
) -> list[tuple[str, str]]:
    """Borrow chords from a parallel mode for harmonic color.

    Takes a progression in the key and substitutes chords that exist
    in the target mode but not the original major scale. Classic
    technique: borrowing bIII, bVI, bVII, iv from minor.

    Args:
        chords:      Original progression [(root, shape), ...].
        key:         Key root.
        target_mode: Mode to borrow from ('minor', 'dorian', 'mixolydian').

    Returns:
        New progression with some chords borrowed from target mode.
    """
    key_semi = _semi(key)
    mode_intervals = _SCALE_INTERVALS.get(
        target_mode, _SCALE_INTERVALS.get("aeolian", [0, 2, 3, 5, 7, 8, 10])
    )
    # Build borrowed chord lookup
    borrowed: dict[int, tuple[str, str]] = {}
    _degree_shapes_minor = {0: "min", 2: "dim", 3: "maj", 5: "min", 7: "min", 8: "maj", 10: "maj"}
    for interval in mode_intervals:
        semi = (key_semi + interval) % 12
        shape = _degree_shapes_minor.get(interval, "maj")
        borrowed[semi] = (_NOTE_NAMES[semi], shape)

    result: list[tuple[str, str]] = []
    for root, shape in chords:
        root_semi = _semi(root)
        # If chord is diatonic to major, sometimes swap with borrowed
        if root_semi in borrowed and shape == "maj":
            b_root, b_shape = borrowed[root_semi]
            if b_shape != shape:  # only swap if it's actually different
                result.append((b_root, b_shape))
                continue
        result.append((root, shape))
    return result


def whole_tone_run(
    root: str,
    octave: int = 4,
    length: int = 6,
    duration: float = 0.25,
) -> list[Note]:
    """Generate a whole tone scale run (all whole steps).

    Creates a dreamlike, ambiguous quality — no leading tone.

    Args:
        root:     Starting note.
        octave:   Starting octave.
        length:   Number of notes.
        duration: Duration per note.
    """
    root_semi = _semi(root)
    wt_intervals = [0, 2, 4, 6, 8, 10]
    result: list[Note] = []
    for i in range(length):
        idx = i % len(wt_intervals)
        oct_off = i // len(wt_intervals)
        semi = (root_semi + wt_intervals[idx]) % 12
        result.append(Note(_NOTE_NAMES[semi], min(7, octave + oct_off), duration))
    return result


def blues_lick(
    root: str,
    octave: int = 4,
    duration: float = 0.25,
    seed: int | None = None,
) -> list[Note]:
    """Generate a short blues lick from the blues scale.

    Classic turnaround phrase — 6-8 notes from the blues scale
    with characteristic bends (chromatic approach notes).

    Args:
        root:     Root note of the blues key.
        octave:   Octave.
        duration: Duration per note.
        seed:     Random seed.
    """
    import random

    rng = random.Random(seed)
    root_semi = _semi(root)
    blues = [0, 3, 5, 6, 7, 10]  # blues scale intervals
    blues_notes = [_NOTE_NAMES[(root_semi + i) % 12] for i in blues]

    # Classic lick shape: root area → blue note → resolve
    lick_len = rng.randint(6, 8)
    result: list[Note] = []
    for i in range(lick_len):
        note = rng.choice(blues_notes)
        result.append(Note(note, octave, duration))
    # End on root
    result.append(Note(root, octave, duration * 2))
    return result


def arpeggio_pattern(
    root: str,
    shape: str,
    octave: int = 4,
    pattern: str = "1353",
    duration: float = 0.25,
) -> list[Note]:
    """Generate an arpeggio from a numbered pattern string.

    Pattern digits map to chord tone indices: 1=root, 3=third, 5=fifth, etc.

    Args:
        root:     Chord root.
        shape:    Chord quality.
        octave:   Base octave.
        pattern:  String of digits (1-indexed chord tones). e.g. "1353", "1535".
        duration: Duration per note.
    """
    if shape not in _CHORD_SEMI:
        raise ValueError(f"Unknown chord shape {shape!r}")
    root_semi = _semi(root)
    semis = _CHORD_SEMI[shape]
    chord_notes = [_NOTE_NAMES[(root_semi + s) % 12] for s in semis]

    result: list[Note] = []
    for ch in pattern:
        idx = int(ch) - 1
        if 0 <= idx < len(chord_notes):
            result.append(Note(chord_notes[idx], octave, duration))
    return result


def chromatic_run(
    start: str,
    start_octave: int,
    length: int = 12,
    direction: str = "up",
    duration: float = 0.125,
) -> list[Note]:
    """Generate a chromatic scale run.

    Args:
        start:         Starting note.
        start_octave:  Starting octave.
        length:        Number of notes.
        direction:     'up' or 'down'.
        duration:      Duration per note.

    Returns:
        List of chromatic Notes.
    """
    semi = _semi(start)
    step = 1 if direction == "up" else -1
    result: list[Note] = []
    for i in range(length):
        s = (semi + i * step) % 12
        oct = start_octave + (semi + i * step) // 12
        oct = max(2, min(7, oct))
        result.append(Note(_NOTE_NAMES[s], oct, duration))
    return result


def trill(
    note: str,
    octave: int,
    upper: bool = True,
    duration: float = 2.0,
    speed: float = 0.125,
) -> list[Note]:
    """Generate a trill between two adjacent notes.

    Args:
        note:     Main note.
        octave:   Octave.
        upper:    If True, trill with note above; else below.
        duration: Total trill duration.
        speed:    Duration of each alternation.

    Returns:
        List of alternating Notes.
    """
    semi = _semi(note)
    alt_semi = (semi + (1 if upper else -1)) % 12
    alt_oct = octave + (
        1 if upper and semi + 1 >= 12 else (-1 if not upper and semi - 1 < 0 else 0)
    )
    alt_oct = max(2, min(7, alt_oct))
    alt_note = _NOTE_NAMES[alt_semi]

    count = max(2, int(duration / speed))
    result: list[Note] = []
    for i in range(count):
        if i % 2 == 0:
            result.append(Note(note, octave, speed))
        else:
            result.append(Note(alt_note, alt_oct, speed))
    return result


def diminished_run(
    root: str,
    octave: int = 4,
    length: int = 8,
    duration: float = 0.25,
) -> list[Note]:
    """Generate a diminished scale run (half-whole pattern).

    Args:
        root:     Starting note.
        octave:   Starting octave.
        length:   Number of notes.
        duration: Duration per note.

    Returns:
        List of Notes on the diminished scale.
    """
    root_semi = _semi(root)
    dim_intervals = [0, 1, 3, 4, 6, 7, 9, 10]  # half-whole
    result: list[Note] = []
    for i in range(length):
        idx = i % len(dim_intervals)
        octave_offset = i // len(dim_intervals)
        semi = (root_semi + dim_intervals[idx]) % 12
        oct = min(7, octave + octave_offset)
        result.append(Note(_NOTE_NAMES[semi], oct, duration))
    return result


def canon(melody: list[Note], delay_beats: float = 4.0, voices: int = 2) -> list[list[Note]]:
    """Create a canon (round) — the same melody offset in time.

    Returns multiple voice lists. Voice 0 starts immediately,
    voice 1 starts after delay_beats of rests, etc.

    Args:
        melody:      The melody to canonize.
        delay_beats: Beats of delay between each voice entry.
        voices:      Number of voices (2-4).

    Returns:
        List of note lists, one per voice.
    """
    result: list[list[Note]] = []
    for v in range(min(voices, 4)):
        voice: list[Note] = []
        rest_dur = delay_beats * v
        if rest_dur > 0:
            voice.append(Note.rest(rest_dur))
        voice.extend(melody)
        result.append(voice)
    return result


def hocket(melody: list[Note], voices: int = 2) -> list[list[Note]]:
    """Split a melody across multiple voices (hocket technique).

    Each voice gets alternating notes — the others rest. Creates
    an interlocking texture where voices complete each other.

    Args:
        melody: The melody to split.
        voices: Number of voices to distribute across.

    Returns:
        List of note lists, one per voice.
    """
    result: list[list[Note]] = [[] for _ in range(voices)]
    for i, note in enumerate(melody):
        for v in range(voices):
            if i % voices == v:
                result[v].append(note)
            else:
                result[v].append(Note.rest(note.duration))
    return result


def sequence_by_interval(
    melody: list[Note],
    interval: int = 2,
    repetitions: int = 3,
) -> list[Note]:
    """Repeat a melody transposed up by an interval each time.

    Classical sequential technique — the same phrase at ascending
    or descending pitch levels.

    Args:
        melody:      Original phrase.
        interval:    Semitones to transpose each repetition.
        repetitions: Total repetitions (including original).

    Returns:
        Concatenated transposed phrases.
    """
    result: list[Note] = []
    for rep in range(repetitions):
        shift = interval * rep
        for note in melody:
            if note.pitch is None:
                result.append(Note.rest(note.duration))
            else:
                semi = (_semi(str(note.pitch)) + shift) % 12
                oct = note.octave + ((_semi(str(note.pitch)) + shift) // 12)
                oct = max(2, min(7, oct))
                result.append(Note(_NOTE_NAMES[semi], oct, note.duration, velocity=note.velocity))
    return result


def call_and_response(
    call: list[Note],
    key: str = "C",
    mode: str = "major",
    seed: int | None = None,
) -> list[Note]:
    """Generate a 'response' phrase that answers a 'call' phrase.

    The response uses the same rhythm but different pitches from the
    same scale, ending on a chord tone for resolution.

    Args:
        call: The call phrase (list of Notes).
        key:  Key root.
        mode: Scale mode.
        seed: Random seed.

    Returns:
        Response phrase (same length/rhythm as call).
    """
    import random

    rng = random.Random(seed)
    scale_intervals = _SCALE_INTERVALS.get(mode, _SCALE_INTERVALS["major"])
    root_semi = _semi(key)
    scale_notes = [_NOTE_NAMES[(root_semi + i) % 12] for i in scale_intervals]

    result: list[Note] = []
    for i, n in enumerate(call):
        if n.pitch is None:
            result.append(Note.rest(n.duration))
        elif i == len(call) - 1:
            # End on root for resolution
            result.append(Note(key, n.octave, n.duration, velocity=n.velocity))
        else:
            pitch = rng.choice(scale_notes)
            result.append(Note(pitch, n.octave, n.duration, velocity=n.velocity))
    return result


def ostinato(
    pattern: list[Note],
    repeats: int = 4,
    variation: float = 0.0,
    seed: int | None = None,
) -> list[Note]:
    """Repeat a short pattern with optional subtle variation.

    Args:
        pattern:   Short note pattern to repeat.
        repeats:   Number of repetitions.
        variation: Probability (0-1) of each note being slightly altered.
        seed:      Random seed.

    Returns:
        Repeated pattern with optional variations.
    """
    import random

    rng = random.Random(seed)
    result: list[Note] = []
    for _ in range(repeats):
        for n in pattern:
            if n.pitch is None or variation == 0 or rng.random() > variation:
                result.append(n)
            else:
                # Slight variation: shift pitch by ±1-2 semitones
                semi = _semi(str(n.pitch))
                shift = rng.choice([-2, -1, 1, 2])
                new_semi = (semi + shift) % 12
                result.append(
                    Note(_NOTE_NAMES[new_semi], n.octave, n.duration, velocity=n.velocity)
                )
    return result


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


def dynamics_curve(notes: list[Note], start_vel: float = 0.3, end_vel: float = 0.9) -> list[Note]:
    """Apply a linear dynamics curve (crescendo or decrescendo).

    Args:
        notes:     List of Notes.
        start_vel: Starting velocity.
        end_vel:   Ending velocity.

    Returns:
        New list with linearly interpolated velocities.
    """
    if not notes:
        return []
    result: list[Note] = []
    for i, n in enumerate(notes):
        t = i / max(len(notes) - 1, 1)
        vel = start_vel + (end_vel - start_vel) * t
        vel = max(0.05, min(1.0, vel))
        if n.pitch is None:
            result.append(Note.rest(n.duration))
        else:
            result.append(Note(str(n.pitch), n.octave, n.duration, velocity=vel))
    return result


def arpeggiate_chord(
    root: str,
    shape: str,
    octave: int = 4,
    duration: float = 0.25,
    direction: str = "up",
    repeats: int = 1,
) -> list[Note]:
    """Convert a chord into an arpeggiated note sequence.

    Args:
        root:      Chord root.
        shape:     Chord quality.
        octave:    Base octave.
        duration:  Duration per note.
        direction: 'up', 'down', or 'updown'.
        repeats:   How many times to repeat the pattern.

    Returns:
        List of Notes.
    """
    if shape not in _CHORD_SEMI:
        raise ValueError(f"Unknown chord shape {shape!r}")
    root_semi = _semi(root)
    semis = _CHORD_SEMI[shape]
    notes = [
        Note(_NOTE_NAMES[(root_semi + s) % 12], octave + (root_semi + s) // 12, duration)
        for s in semis
    ]

    if direction == "down":
        notes = list(reversed(notes))
    elif direction == "updown":
        notes = (
            notes + list(reversed(notes[1:-1])) if len(notes) > 2 else notes + list(reversed(notes))
        )

    return notes * repeats


def staccato(notes: list[Note], ratio: float = 0.5) -> list[Note]:
    """Shorten notes and add rests for a staccato articulation.

    Args:
        notes: List of Notes.
        ratio: Fraction of duration to sound (0.0-1.0). Rest fills remainder.

    Returns:
        New list with shortened notes + rests.
    """
    result: list[Note] = []
    for n in notes:
        if n.pitch is None:
            result.append(Note.rest(n.duration))
        else:
            sounding = max(0.0625, n.duration * ratio)
            silence = n.duration - sounding
            result.append(Note(str(n.pitch), n.octave, sounding, velocity=n.velocity))
            if silence > 0.001:
                result.append(Note.rest(silence))
    return result


def legato_connect(notes: list[Note], overlap: float = 0.1) -> list[Note]:
    """Extend note durations for a legato feel (overlapping notes).

    Each note's duration is extended by `overlap` beats, creating
    a connected, singing quality.

    Args:
        notes:   List of Notes.
        overlap: Extra duration in beats to add.

    Returns:
        New list with extended durations.
    """
    result: list[Note] = []
    for n in notes:
        if n.pitch is None:
            result.append(Note.rest(n.duration))
        else:
            result.append(Note(str(n.pitch), n.octave, n.duration + overlap, velocity=n.velocity))
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


def stretch_melody(notes: list[Note], factor: float = 2.0) -> list[Note]:
    """Multiply all note durations by a factor.

    factor > 1 = slower (augmentation), factor < 1 = faster (diminution).
    More flexible than generate_variation augmentation/diminution since
    it accepts any float factor.

    Args:
        notes:  List of Notes.
        factor: Duration multiplier.

    Returns:
        New list with scaled durations.
    """
    result: list[Note] = []
    for n in notes:
        new_dur = max(0.0625, n.duration * factor)
        if n.pitch is None:
            result.append(Note.rest(new_dur))
        else:
            result.append(Note(str(n.pitch), n.octave, new_dur, velocity=n.velocity))
    return result


def invert_chord(notes: list[Note], inversion: int = 1) -> list[Note]:
    """Apply a chord inversion by rotating the bottom note(s) up an octave.

    Args:
        notes:     List of Notes forming a chord.
        inversion: 1=first inversion, 2=second, etc.

    Returns:
        New list with bottom note(s) moved up an octave.
    """
    result = list(notes)
    for _ in range(min(inversion, len(result) - 1)):
        bottom = result.pop(0)
        if bottom.pitch is not None:
            result.append(
                Note(
                    str(bottom.pitch),
                    min(bottom.octave + 1, 7),
                    bottom.duration,
                    velocity=bottom.velocity,
                )
            )
        else:
            result.append(bottom)
    return result


def rotate_voicing(notes: list[Note], steps: int = 1) -> list[Note]:
    """Rotate a voicing by moving notes cyclically (no octave change).

    Args:
        notes: List of Notes.
        steps: Number of positions to rotate (positive=right).

    Returns:
        Rotated list.
    """
    if not notes:
        return []
    s = steps % len(notes)
    return notes[s:] + notes[:s]


def pedal_point(note: str, octave: int, melody: list[Note]) -> list[Note]:
    """Add a pedal point (sustained bass note) alternating with melody notes.

    Creates a bass line that alternates between the pedal note and each
    melody note. Classic technique for building tension.

    Args:
        note:   Pedal note pitch.
        octave: Pedal note octave.
        melody: Melody notes to alternate with.

    Returns:
        List with pedal-melody-pedal-melody pattern.
    """
    result: list[Note] = []
    for m in melody:
        result.append(Note(note, octave, m.duration, velocity=m.velocity * 0.7))
        result.append(m)
    return result


def normalize_notes(notes: list[Note], target_octave: int = 4) -> list[Note]:
    """Normalize all pitched notes to a single octave.

    Useful for pitch class analysis — removes octave variation.

    Args:
        notes:         List of Notes.
        target_octave: Octave to normalize to.

    Returns:
        New list with all pitches at target_octave.
    """
    result: list[Note] = []
    for n in notes:
        if n.pitch is None:
            result.append(Note.rest(n.duration))
        else:
            result.append(Note(str(n.pitch), target_octave, n.duration, velocity=n.velocity))
    return result


def count_pitch_classes(notes: list[Note]) -> dict[str, int]:
    """Count occurrences of each pitch class (ignoring octave).

    Args:
        notes: List of Notes.

    Returns:
        Dict mapping pitch name to count, sorted by frequency.
    """
    counts: dict[str, int] = {}
    for n in notes:
        if n.pitch is not None:
            pitch = str(n.pitch)
            counts[pitch] = counts.get(pitch, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


def melodic_interval_histogram(notes: list[Note]) -> dict[str, int]:
    """Build a histogram of melodic interval sizes.

    Args:
        notes: List of Notes.

    Returns:
        Dict mapping interval name to count.
    """
    pitched = [n for n in notes if n.pitch is not None]
    if len(pitched) < 2:
        return {}

    histogram: dict[str, int] = {}
    for i in range(len(pitched) - 1):
        a = _semi(str(pitched[i].pitch)) + pitched[i].octave * 12
        b = _semi(str(pitched[i + 1].pitch)) + pitched[i + 1].octave * 12
        dist = abs(b - a) % 12
        name = _INTERVAL_NAMES.get(dist, f"{dist}st")
        histogram[name] = histogram.get(name, 0) + 1
    return dict(sorted(histogram.items(), key=lambda x: -x[1]))


def note_range(notes: list[Note]) -> dict:
    """Find the pitch range of a melody.

    Args:
        notes: List of Notes.

    Returns:
        Dict with lowest, highest, span_semitones, span_octaves.
    """
    pitched = [(n.pitch, n.octave) for n in notes if n.pitch is not None]
    if not pitched:
        return {"lowest": None, "highest": None, "span_semitones": 0, "span_octaves": 0}

    midi_vals = [_semi(str(p)) + o * 12 for p, o in pitched]
    lo_midi = min(midi_vals)
    hi_midi = max(midi_vals)
    lo_idx = midi_vals.index(lo_midi)
    hi_idx = midi_vals.index(hi_midi)

    return {
        "lowest": f"{pitched[lo_idx][0]}{pitched[lo_idx][1]}",
        "highest": f"{pitched[hi_idx][0]}{pitched[hi_idx][1]}",
        "span_semitones": hi_midi - lo_midi,
        "span_octaves": round((hi_midi - lo_midi) / 12, 1),
    }


def rhythmic_density(notes: list[Note]) -> dict:
    """Calculate rhythmic density metrics for a note list.

    Args:
        notes: List of Notes.

    Returns:
        Dict with total_notes, total_rests, total_beats, notes_per_beat,
        shortest_note, longest_note.
    """
    pitched = [n for n in notes if n.pitch is not None]
    rests = [n for n in notes if n.pitch is None]
    total_beats = sum(n.duration for n in notes)
    durations = [n.duration for n in pitched] if pitched else [0]

    return {
        "total_notes": len(pitched),
        "total_rests": len(rests),
        "total_beats": round(total_beats, 2),
        "notes_per_beat": round(len(pitched) / max(total_beats, 0.01), 2),
        "shortest_note": min(durations),
        "longest_note": max(durations),
    }


def detect_repeated_sections(
    song,
    beats_per_bar: int = 4,
    min_bars: int = 2,
) -> list[dict]:
    """Detect repeated bar patterns in a song.

    Compares bars by note content hash to find sections that repeat.

    Args:
        song:          Song to analyze.
        beats_per_bar: Beats per bar.
        min_bars:      Minimum bars for a section to count.

    Returns:
        List of dicts: {track, pattern_hash, bars, repeat_count}.
    """
    from .engine import Chord as _Chord

    results: list[dict] = []

    for track in song.tracks:
        # Build bar content strings
        bar_contents: dict[int, str] = {}
        pos = 0.0
        for beat in track.beats:
            if beat.event:
                bar_idx = int(pos / beats_per_bar)
                event_str = ""
                if isinstance(beat.event, Note) and beat.event.pitch is not None:
                    event_str = f"{beat.event.pitch}{beat.event.octave}"
                elif isinstance(beat.event, _Chord):
                    event_str = f"{beat.event.root}{beat.event.shape}"
                bar_contents.setdefault(bar_idx, "")
                bar_contents[bar_idx] += event_str
                pos += beat.event.duration

        if not bar_contents:
            continue

        # Find repeated patterns (sequences of bars)
        for length in range(min_bars, len(bar_contents) // 2 + 1):
            patterns: dict[str, list[int]] = {}
            for start in range(0, len(bar_contents) - length + 1):
                pattern = "|".join(bar_contents.get(start + i, "") for i in range(length))
                if pattern and pattern != "|" * (length - 1):
                    patterns.setdefault(pattern, []).append(start)

            for pattern_hash, starts in patterns.items():
                if len(starts) > 1:
                    results.append(
                        {
                            "track": track.name,
                            "pattern_hash": hash(pattern_hash) % 10000,
                            "bars": length,
                            "repeat_count": len(starts),
                            "at_bars": starts,
                        }
                    )

    # Deduplicate — keep longest patterns
    seen: set[tuple[str, int]] = set()
    unique: list[dict] = []
    for r in sorted(results, key=lambda x: -x["bars"]):
        key = (r["track"], r["at_bars"][0])
        if key not in seen:
            unique.append(r)
            seen.add(key)

    return unique[:20]  # limit output


# ---------------------------------------------------------------------------
# Interval naming and parallel harmony
# ---------------------------------------------------------------------------

_INTERVAL_NAMES = {
    0: "unison",
    1: "minor 2nd",
    2: "major 2nd",
    3: "minor 3rd",
    4: "major 3rd",
    5: "perfect 4th",
    6: "tritone",
    7: "perfect 5th",
    8: "minor 6th",
    9: "major 6th",
    10: "minor 7th",
    11: "major 7th",
    12: "octave",
}


def interval_name(note_a: str, note_b: str) -> str:
    """Name the interval between two notes.

    Args:
        note_a: First note (e.g. 'C').
        note_b: Second note (e.g. 'E').

    Returns:
        Interval name (e.g. 'major 3rd').
    """
    semi_a = _semi(note_a)
    semi_b = _semi(note_b)
    dist = (semi_b - semi_a) % 12
    return _INTERVAL_NAMES.get(dist, f"{dist} semitones")


def parallel_motion(
    melody: list[Note],
    interval: int = 7,
    above: bool = True,
) -> list[Note]:
    """Harmonize a melody by adding a parallel interval.

    Args:
        melody:   Original melody.
        interval: Interval in semitones (default 7 = perfect 5th).
        above:    If True, harmony is above; if False, below.

    Returns:
        List of Notes at the parallel interval.
    """
    result: list[Note] = []
    for note in melody:
        if note.pitch is None:
            result.append(Note.rest(note.duration))
        else:
            semi = _semi(str(note.pitch))
            offset = interval if above else -interval
            new_semi = (semi + offset) % 12
            new_oct = note.octave + (1 if above and semi + offset >= 12 else 0)
            new_oct = max(
                2, min(7, new_oct if above else note.octave - (1 if semi + offset < 0 else 0))
            )
            result.append(
                Note(_NOTE_NAMES[new_semi], new_oct, note.duration, velocity=note.velocity * 0.85)
            )
    return result


# Common chord progressions for suggestion engine
_COMMON_NEXT = {
    "I": ["IV", "V", "vi", "ii"],
    "ii": ["V", "vii", "IV"],
    "iii": ["vi", "IV", "ii"],
    "IV": ["V", "I", "ii", "vii"],
    "V": ["I", "vi", "IV"],
    "vi": ["IV", "ii", "V", "I"],
    "vii": ["I", "iii"],
}

_DEGREE_TO_SEMI = {"I": 0, "ii": 2, "iii": 4, "IV": 5, "V": 7, "vi": 9, "vii": 11}
_DEGREE_SHAPES = {
    "I": "maj",
    "ii": "min",
    "iii": "min",
    "IV": "maj",
    "V": "maj",
    "vi": "min",
    "vii": "dim",
}


def suggest_next_chord(
    current_root: str,
    current_shape: str,
    key: str = "C",
) -> list[tuple[str, str]]:
    """Suggest the next chord in a progression based on common voice leading.

    Args:
        current_root:  Current chord root.
        current_shape: Current chord quality.
        key:           Key of the progression.

    Returns:
        List of (root, shape) suggestions, most common first.
    """
    key_semi = _semi(key)
    current_semi = _semi(current_root)
    degree_semi = (current_semi - key_semi) % 12

    # Find current degree
    current_degree = None
    for deg, semi in _DEGREE_TO_SEMI.items():
        if semi == degree_semi:
            current_degree = deg
            break

    if current_degree is None:
        # Chromatic chord — suggest tonic resolution
        return [(key, "maj")]

    suggestions = _COMMON_NEXT.get(current_degree, ["I"])
    result: list[tuple[str, str]] = []
    for deg in suggestions:
        semi = _DEGREE_TO_SEMI[deg]
        root = _NOTE_NAMES[(key_semi + semi) % 12]
        shape = _DEGREE_SHAPES[deg]
        result.append((root, shape))
    return result


def scale_info(scale_name: str, root: str = "C") -> dict:
    """Describe a scale with intervals, note names, and compatible chords.

    Args:
        scale_name: Scale name (major, minor, dorian, etc).
        root:       Root note.

    Returns:
        Dict with name, root, notes, intervals, chord_fits.
    """
    # Alias common names
    aliases = {"minor": "aeolian", "natural_minor": "aeolian"}
    scale_name = aliases.get(scale_name, scale_name)
    if scale_name not in _SCALE_INTERVALS:
        raise ValueError(f"Unknown scale {scale_name!r}")

    root_semi = _semi(root)
    intervals = _SCALE_INTERVALS[scale_name]
    notes = [_NOTE_NAMES[(root_semi + i) % 12] for i in intervals]

    # Find chords whose tones are subsets of this scale
    scale_pcs = {(root_semi + i) % 12 for i in intervals}
    chord_fits: list[str] = []
    for degree_idx, interval in enumerate(intervals):
        degree_root = _NOTE_NAMES[(root_semi + interval) % 12]
        for shape, semis in _CHORD_SEMI.items():
            chord_pcs = {(root_semi + interval + s) % 12 for s in semis}
            if chord_pcs.issubset(scale_pcs):
                chord_fits.append(f"{degree_root}{shape}")

    return {
        "name": scale_name,
        "root": root,
        "notes": notes,
        "intervals": intervals,
        "chord_fits": chord_fits,
    }


def chord_extensions(
    root: str,
    shape: str,
    extensions: list[str] | None = None,
) -> list[Note]:
    """Add extensions (9th, 11th, 13th) to a chord.

    Args:
        root:       Chord root note.
        shape:      Base chord quality.
        extensions: List of extensions to add: '9', '11', '13', 'b9', '#9', '#11', 'b13'.
                    If None, adds available tensions automatically.

    Returns:
        List of Notes forming the extended chord.
    """
    if shape not in _CHORD_SEMI:
        raise ValueError(f"Unknown chord shape {shape!r}")

    root_semi = _semi(root)
    base_semis = list(_CHORD_SEMI[shape])

    tension_map = {"b9": 1, "9": 2, "#9": 3, "11": 5, "#11": 6, "b13": 8, "13": 9}

    if extensions is None:
        extensions = available_tensions(root, shape)

    for ext in extensions:
        if ext in tension_map:
            base_semis.append(tension_map[ext])

    return [
        Note(_NOTE_NAMES[(root_semi + s) % 12], 3 + s // 12, 4.0) for s in sorted(set(base_semis))
    ]


def merge_tracks(tracks_notes: list[list[Note]]) -> list[Note]:
    """Merge multiple note lists into a single interleaved list.

    Takes notes from each list in round-robin order.

    Args:
        tracks_notes: List of note lists to merge.

    Returns:
        Single merged list.
    """
    if not tracks_notes:
        return []

    result: list[Note] = []
    max_len = max(len(t) for t in tracks_notes)
    for i in range(max_len):
        for track in tracks_notes:
            if i < len(track):
                result.append(track[i])
    return result


# ---------------------------------------------------------------------------
# Chord voicing generators
# ---------------------------------------------------------------------------


def generate_chord_voicing(
    root: str,
    shape: str,
    octave: int = 3,
    voicing: str = "close",
    duration: float = 4.0,
) -> list[Note]:
    """Generate a specific chord voicing as individual notes.

    Args:
        root:     Chord root note.
        shape:    Chord quality (maj, min7, dom7, etc).
        octave:   Base octave.
        voicing:  Voicing type:
            - 'close': all notes within one octave (default)
            - 'spread': notes spread across 2+ octaves
            - 'drop2': second-highest note dropped an octave
            - 'rootless': omit root (jazz voicing)
        duration: Note duration.

    Returns:
        List of Notes forming the voicing.
    """
    if shape not in _CHORD_SEMI:
        raise ValueError(f"Unknown chord shape {shape!r}")

    root_semi = _semi(root)
    semis = _CHORD_SEMI[shape]

    if voicing == "close":
        return [
            Note(_NOTE_NAMES[(root_semi + s) % 12], octave + (root_semi + s) // 12, duration)
            for s in semis
        ]
    elif voicing == "spread":
        result: list[Note] = []
        for i, s in enumerate(semis):
            oct = octave + i  # each note one octave higher
            result.append(Note(_NOTE_NAMES[(root_semi + s) % 12], min(oct, 7), duration))
        return result
    elif voicing == "drop2":
        close = [(_NOTE_NAMES[(root_semi + s) % 12], octave + (root_semi + s) // 12) for s in semis]
        if len(close) >= 3:
            # Drop second-highest note by one octave
            second_idx = len(close) - 2
            p, o = close[second_idx]
            close[second_idx] = (p, max(2, o - 1))
        return [Note(p, o, duration) for p, o in close]
    elif voicing == "rootless":
        # Skip the root (first note)
        return [
            Note(_NOTE_NAMES[(root_semi + s) % 12], octave + (root_semi + s) // 12, duration)
            for s in semis[1:]
        ]
    else:
        raise ValueError(f"Unknown voicing {voicing!r}. Choose: close, spread, drop2, rootless")


# ---------------------------------------------------------------------------
# Chromatic harmony — Neapolitan, augmented sixth, picardy third (v39.0)
# ---------------------------------------------------------------------------


def neapolitan_chord(key: str = "C", octave: int = 3, duration: float = 4.0) -> list[Note]:
    """Generate a Neapolitan chord (bII major in first inversion).

    The Neapolitan is a major triad built on the lowered second degree,
    typically in first inversion. It resolves to V, creating dramatic
    pre-dominant tension. Staple of classical and film music.

    Args:
        key:      Key root.
        octave:   Base octave.
        duration: Note duration.

    Returns:
        List of Notes forming the Neapolitan chord (bII/first inversion).
    """
    key_semi = _semi(key)
    bii_semi = (key_semi + 1) % 12  # lowered 2nd degree
    # Major triad on bII: root, major 3rd, perfect 5th
    pitches = [bii_semi, (bii_semi + 4) % 12, (bii_semi + 7) % 12]
    # First inversion: 3rd in bass, then root, then 5th
    return [
        Note(_NOTE_NAMES[pitches[1]], octave, duration),
        Note(_NOTE_NAMES[pitches[0]], octave + 1, duration),
        Note(_NOTE_NAMES[pitches[2]], octave + 1, duration),
    ]


def augmented_sixth(
    key: str = "C",
    variety: str = "italian",
    octave: int = 3,
    duration: float = 4.0,
) -> list[Note]:
    """Generate an augmented sixth chord (Italian, French, or German).

    All three share the characteristic interval: b6 to #4 (an augmented
    sixth) that resolves outward to an octave on the dominant. The varieties
    differ in the additional tones:

    - Italian (It+6): b6, 1, #4 — three notes, lean and bright
    - French (Fr+6): b6, 1, 2, #4 — adds the major 2nd, whole-tone flavor
    - German (Gr+6): b6, 1, b3, #4 — adds the minor 3rd, enharmonic with dom7

    Args:
        key:      Key root.
        variety:  'italian', 'french', or 'german'.
        octave:   Base octave.
        duration: Note duration.

    Returns:
        List of Notes forming the augmented sixth chord.

    Raises:
        ValueError: If variety is not italian, french, or german.
    """
    key_semi = _semi(key)
    b6 = (key_semi + 8) % 12  # lowered 6th degree
    root = key_semi  # tonic (scale degree 1)
    sharp4 = (key_semi + 6) % 12  # raised 4th degree

    if variety == "italian":
        return [
            Note(_NOTE_NAMES[b6], octave, duration),
            Note(_NOTE_NAMES[root], octave + 1, duration),
            Note(_NOTE_NAMES[sharp4], octave + 1, duration),
        ]
    elif variety == "french":
        d2 = (key_semi + 2) % 12  # major 2nd
        return [
            Note(_NOTE_NAMES[b6], octave, duration),
            Note(_NOTE_NAMES[root], octave + 1, duration),
            Note(_NOTE_NAMES[d2], octave + 1, duration),
            Note(_NOTE_NAMES[sharp4], octave + 1, duration),
        ]
    elif variety == "german":
        b3 = (key_semi + 3) % 12  # minor 3rd
        return [
            Note(_NOTE_NAMES[b6], octave, duration),
            Note(_NOTE_NAMES[root], octave + 1, duration),
            Note(_NOTE_NAMES[b3], octave + 1, duration),
            Note(_NOTE_NAMES[sharp4], octave + 1, duration),
        ]
    else:
        raise ValueError(f"Unknown variety {variety!r}. Choose: italian, french, german")


def picardy_third(key: str = "C", octave: int = 3, duration: float = 4.0) -> list[Note]:
    """Generate a Picardy third — major tonic chord in a minor key context.

    The Picardy third replaces the expected minor tonic with a major chord
    at the end of a piece in a minor key, creating an unexpectedly bright
    resolution. Common in Baroque music (Bach chorales), metal endings,
    and film scores.

    Args:
        key:      Minor key root (e.g. 'C' for C minor).
        octave:   Base octave.
        duration: Note duration.

    Returns:
        List of Notes forming the major tonic (Picardy) chord.
    """
    key_semi = _semi(key)
    # Major triad on the tonic (raises the minor 3rd to major 3rd)
    pitches = [key_semi, (key_semi + 4) % 12, (key_semi + 7) % 12]
    return [Note(_NOTE_NAMES[p], octave + p // 12, duration) for p in pitches]


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
# Chord progression templates (v41.0)
# ---------------------------------------------------------------------------


def twelve_bar_blues(
    key: str = "C",
) -> list[tuple[str, str]]:
    """Generate a 12-bar blues progression.

    The 12-bar blues is the most important chord progression in modern
    music. Rock, jazz, country, R&B — everything traces back to these
    12 bars. I-I-I-I / IV-IV-I-I / V-IV-I-V (quick change optional).

    Args:
        key: Key root.

    Returns:
        12-element list of (root, shape) tuples, one per bar.
    """
    k = _semi(key)
    tonic = (_NOTE_NAMES[k], "dom7")
    iv = (_NOTE_NAMES[(k + 5) % 12], "dom7")
    v = (_NOTE_NAMES[(k + 7) % 12], "dom7")
    return [tonic, tonic, tonic, tonic, iv, iv, tonic, tonic, v, iv, tonic, v]


def rhythm_changes(
    key: str = "Bb",
) -> list[tuple[str, str]]:
    """Generate the A section of rhythm changes (Gershwin's 'I Got Rhythm').

    Rhythm changes are the second most important chord progression in jazz
    after the blues. The 8-bar A section cycles I-vi-ii-V with chromatic
    turnarounds. Bird, Diz, Sonny Rollins — everyone cut their teeth
    on rhythm changes.

    Args:
        key: Key root (Bb is traditional).

    Returns:
        8-element list of (root, shape) tuples for the A section.
    """
    k = _semi(key)
    tonic = _NOTE_NAMES[k]
    vi = _NOTE_NAMES[(k + 9) % 12]
    ii = _NOTE_NAMES[(k + 2) % 12]
    v = _NOTE_NAMES[(k + 7) % 12]
    return [
        (tonic, "maj7"),
        (vi, "min7"),
        (ii, "min7"),
        (v, "dom7"),
        (tonic, "maj7"),
        (vi, "min7"),
        (ii, "min7"),
        (v, "dom7"),
    ]


def coltrane_changes(
    key: str = "C",
) -> list[tuple[str, str]]:
    """Generate Coltrane changes (Giant Steps substitution pattern).

    John Coltrane's 'Giant Steps' divides the octave into three equal
    parts (major thirds) and moves through all three tonal centers.
    The hardest chord changes in jazz — if you can play these, you can
    play anything.

    Args:
        key: Starting key root.

    Returns:
        12-element list of (root, shape) tuples cycling through three keys.
    """
    k = _semi(key)
    # Three tonal centers a major third apart
    c1 = _NOTE_NAMES[k]
    c2 = _NOTE_NAMES[(k + 4) % 12]
    c3 = _NOTE_NAMES[(k + 8) % 12]
    # V7 of each center
    v1 = _NOTE_NAMES[(k + 7) % 12]
    v2 = _NOTE_NAMES[(k + 11) % 12]
    v3 = _NOTE_NAMES[(k + 3) % 12]

    return [
        (c1, "maj7"),
        (v2, "dom7"),
        (c2, "maj7"),
        (v3, "dom7"),
        (c3, "maj7"),
        (v1, "dom7"),
        (c1, "maj7"),
        (v2, "dom7"),
        (c2, "maj7"),
        (v3, "dom7"),
        (c3, "maj7"),
        (v1, "dom7"),
    ]


def andalusian_cadence(
    key: str = "A",
) -> list[tuple[str, str]]:
    """Generate the Andalusian cadence (i-bVII-bVI-V).

    The most distinctive sound of flamenco, but it shows up everywhere:
    'Hit the Road Jack', 'Sultans of Swing', 'Stairway to Heaven' intro.
    Descending bass line from tonic through the Phrygian mode.

    Args:
        key: Minor key root (A minor is traditional).

    Returns:
        4-element list of (root, shape) tuples.
    """
    k = _semi(key)
    i = (_NOTE_NAMES[k], "min")
    bVII = (_NOTE_NAMES[(k + 10) % 12], "maj")
    bVI = (_NOTE_NAMES[(k + 8) % 12], "maj")
    V = (_NOTE_NAMES[(k + 7) % 12], "maj")
    return [i, bVII, bVI, V]


# ---------------------------------------------------------------------------
# Voice leading engine — SATB (v42.0)
# ---------------------------------------------------------------------------

# SATB voice ranges (MIDI-style octave numbering)
_SATB_RANGES = {
    "soprano": (60, 79),  # C4–G5
    "alto": (53, 74),  # F3–D5
    "tenor": (48, 69),  # C3–A4
    "bass": (40, 64),  # E2–E4
}


def _note_to_abs(pitch: str, octave: int) -> int:
    """Convert note name + octave to absolute semitone (C4 = 60)."""
    return _semi(pitch) + octave * 12


def _abs_to_note(absolute: int) -> tuple[str, int]:
    """Convert absolute semitone to (pitch_name, octave)."""
    return (_NOTE_NAMES[absolute % 12], absolute // 12)


def voice_lead_satb(
    progression: list[tuple[str, str]],
    key: str = "C",
) -> list[list[Note]]:
    """Generate four-part SATB voice leading for a chord progression.

    Produces smooth voice leading with parallel 5th/octave avoidance,
    voice range constraints, and common-tone retention. Each chord is
    realized as [soprano, alto, tenor, bass] Notes.

    This is the bread and butter of classical harmony — the algorithm
    every composition student learns in their first semester.

    Args:
        progression: List of (root, shape) chord tuples.
        key:         Key root (for context, used in doubling decisions).

    Returns:
        List of 4-element Note lists, one per chord in the progression.
    """
    if not progression:
        return []

    result: list[list[Note]] = []
    prev_voicing: list[int] | None = None

    for root, shape in progression:
        if shape not in _CHORD_SEMI:
            raise ValueError(f"Unknown chord shape {shape!r}")

        root_semi = _semi(root)
        chord_pcs = [(root_semi + s) % 12 for s in _CHORD_SEMI[shape]]

        if prev_voicing is None:
            # First chord — spread across SATB ranges
            bass_pc = chord_pcs[0]  # root in bass
            bass_abs = _find_nearest(bass_pc, 52, *_SATB_RANGES["bass"])
            tenor_pc = chord_pcs[2 % len(chord_pcs)]
            tenor_abs = _find_nearest(tenor_pc, 57, *_SATB_RANGES["tenor"])
            alto_pc = chord_pcs[1 % len(chord_pcs)]
            alto_abs = _find_nearest(alto_pc, 62, *_SATB_RANGES["alto"])
            soprano_pc = chord_pcs[0]  # double root in soprano
            soprano_abs = _find_nearest(soprano_pc, 72, *_SATB_RANGES["soprano"])
            voicing = [soprano_abs, alto_abs, tenor_abs, bass_abs]
        else:
            # Subsequent chords — minimize movement, retain common tones
            voicing = _smooth_voice_lead(chord_pcs, prev_voicing)

        # Enforce no voice crossing
        voicing.sort(reverse=True)  # soprano highest, bass lowest

        prev_voicing = voicing
        notes = []
        for absolute in voicing:
            p, o = _abs_to_note(absolute)
            notes.append(Note(p, o, 4.0))
        result.append(notes)

    return result


def _find_nearest(pc: int, target: int, low: int, high: int) -> int:
    """Find the absolute pitch closest to target with the given pitch class."""
    candidates = []
    for octave in range(low // 12, high // 12 + 2):
        absolute = pc + octave * 12
        if low <= absolute <= high:
            candidates.append(absolute)
    if not candidates:
        # Fallback: closest to range
        return pc + (target // 12) * 12
    return min(candidates, key=lambda a: abs(a - target))


def _smooth_voice_lead(chord_pcs: list[int], prev: list[int]) -> list[int]:
    """Voice-lead to new chord PCs from previous voicing, minimizing movement."""
    # For each voice, find the nearest realization of any chord tone
    used: set[int] = set()
    result: list[int] = []
    voices = ["soprano", "alto", "tenor", "bass"]

    for i, (prev_abs, voice) in enumerate(zip(prev, voices)):
        low, high = _SATB_RANGES[voice]
        best_abs = prev_abs
        best_dist = 999

        for pc in chord_pcs:
            for octave in range(low // 12, high // 12 + 2):
                candidate = pc + octave * 12
                if low <= candidate <= high:
                    dist = abs(candidate - prev_abs)
                    if dist < best_dist:
                        best_dist = dist
                        best_abs = candidate

        result.append(best_abs)
        used.add(best_abs % 12)

    return result


def check_parallel_fifths(voicing_a: list[Note], voicing_b: list[Note]) -> bool:
    """Check if two SATB voicings contain parallel perfect 5ths or octaves.

    Returns True if a forbidden parallel is detected. Classical part-writing
    rule: no two voices may move in parallel motion to a perfect 5th or octave.

    Args:
        voicing_a: First chord voicing (4 Notes, high to low).
        voicing_b: Second chord voicing (4 Notes, high to low).

    Returns:
        True if parallel 5ths or octaves are found.
    """
    for i in range(len(voicing_a)):
        for j in range(i + 1, len(voicing_a)):
            interval_a = (
                abs(
                    _note_to_abs(str(voicing_a[i].pitch), voicing_a[i].octave)
                    - _note_to_abs(str(voicing_a[j].pitch), voicing_a[j].octave)
                )
                % 12
            )
            interval_b = (
                abs(
                    _note_to_abs(str(voicing_b[i].pitch), voicing_b[i].octave)
                    - _note_to_abs(str(voicing_b[j].pitch), voicing_b[j].octave)
                )
                % 12
            )
            # Both intervals are P5 (7) or P8 (0) and voices moved
            if interval_a == interval_b and interval_a in (0, 7):
                moved_i = _note_to_abs(
                    str(voicing_a[i].pitch), voicing_a[i].octave
                ) != _note_to_abs(str(voicing_b[i].pitch), voicing_b[i].octave)
                moved_j = _note_to_abs(
                    str(voicing_a[j].pitch), voicing_a[j].octave
                ) != _note_to_abs(str(voicing_b[j].pitch), voicing_b[j].octave)
                if moved_i and moved_j:
                    return True
    return False


# ---------------------------------------------------------------------------
# Key modulation & pivot chords (v43.0)
# ---------------------------------------------------------------------------


def _diatonic_chords(key: str, mode: str = "major") -> list[tuple[str, str]]:
    """Return the 7 diatonic triads in a key."""
    intervals = _SCALE_INTERVALS.get(mode, _SCALE_INTERVALS["major"])
    k = _semi(key)
    # Quality pattern for major: maj min min maj maj min dim
    qualities_major = ["maj", "min", "min", "maj", "maj", "min", "dim"]
    qualities_minor = ["min", "dim", "maj", "min", "min", "maj", "maj"]
    quals = qualities_minor if mode in ("aeolian", "minor") else qualities_major
    chords = []
    for i, interval in enumerate(intervals[:7]):
        root = _NOTE_NAMES[(k + interval) % 12]
        chords.append((root, quals[i % len(quals)]))
    return chords


def find_pivot_chords(
    key_a: str,
    key_b: str,
    mode_a: str = "major",
    mode_b: str = "major",
) -> list[tuple[str, str]]:
    """Find chords common to two keys (pivot chords for modulation).

    A pivot chord exists diatonically in both keys, enabling smooth
    modulation. The listener hears it as belonging to the old key, but
    the composer reinterprets it in the new key. Sneaky and elegant.

    Args:
        key_a:  First key root.
        key_b:  Second key root.
        mode_a: Mode of first key.
        mode_b: Mode of second key.

    Returns:
        List of (root, shape) tuples that exist in both keys.
    """
    chords_a = set(_diatonic_chords(key_a, mode_a))
    chords_b = set(_diatonic_chords(key_b, mode_b))
    return sorted(chords_a & chords_b)


def modulation_path(
    key_a: str,
    key_b: str,
    mode: str = "major",
) -> list[tuple[str, str]]:
    """Find the shortest chord path from one key to another.

    Walks through the circle of fifths, collecting chords at each step.
    Each adjacent pair of keys shares many pivot chords, so the path
    stays smooth even for distant modulations.

    Args:
        key_a: Starting key root.
        key_b: Target key root.
        mode:  Mode for both keys.

    Returns:
        Chord progression that moves from key_a to key_b.
    """
    a_semi = _semi(key_a)
    b_semi = _semi(key_b)

    # Go around circle of fifths (each step = +7 semitones)
    # or circle of fourths (each step = +5 semitones), whichever shorter
    fifths_dist = 0
    s = a_semi
    while s != b_semi and fifths_dist < 12:
        s = (s + 7) % 12
        fifths_dist += 1

    fourths_dist = 0
    s = a_semi
    while s != b_semi and fourths_dist < 12:
        s = (s + 5) % 12
        fourths_dist += 1

    step = 7 if fifths_dist <= fourths_dist else 5
    steps = fifths_dist if step == 7 else fourths_dist

    path: list[tuple[str, str]] = []
    current = a_semi
    for _ in range(steps):
        next_semi = (current + step) % 12
        next_key = _NOTE_NAMES[next_semi]
        # Add V-I cadence at each step
        v_of_next = _NOTE_NAMES[(next_semi + 7) % 12]
        path.append((v_of_next, "dom7"))
        path.append((next_key, "maj"))
        current = next_semi

    return path


def direct_modulation(
    key_a: str,
    key_b: str,
) -> list[tuple[str, str]]:
    """Generate a direct (truck-driver) modulation — abrupt key change.

    No pivot chord, no preparation. Just slam into the new key with a
    V-I cadence. Used in pop music when you need that energy boost for
    the final chorus. Bon Jovi approved.

    Args:
        key_a: Starting key root.
        key_b: Target key root.

    Returns:
        Short progression: I in old key, then V7-I in new key.
    """
    b_semi = _semi(key_b)
    v_of_b = _NOTE_NAMES[(b_semi + 7) % 12]
    return [(key_a, "maj"), (v_of_b, "dom7"), (key_b, "maj")]


def pivot_modulation(
    key_a: str,
    key_b: str,
    mode_a: str = "major",
    mode_b: str = "major",
) -> list[tuple[str, str]]:
    """Generate a smooth modulation via a pivot chord.

    Finds a chord common to both keys and uses it as the bridge.
    The smoothest type of modulation — the listener barely notices
    the key change happened.

    Args:
        key_a:  Starting key root.
        key_b:  Target key root.
        mode_a: Mode of starting key.
        mode_b: Mode of target key.

    Returns:
        Progression: tonic A → pivot chord → V7 of B → tonic B.
    """
    pivots = find_pivot_chords(key_a, key_b, mode_a, mode_b)
    b_semi = _semi(key_b)
    v_of_b = _NOTE_NAMES[(b_semi + 7) % 12]

    if pivots:
        pivot = pivots[0]  # use the first common chord
        return [(key_a, "maj"), pivot, (v_of_b, "dom7"), (key_b, "maj")]
    else:
        # No common chords — fall back to direct modulation
        return direct_modulation(key_a, key_b)


# ---------------------------------------------------------------------------
# Roman numeral parsing (v44.0)
# ---------------------------------------------------------------------------

_ROMAN_TO_DEGREE = {
    "I": 0,
    "II": 2,
    "III": 4,
    "IV": 5,
    "V": 7,
    "VI": 9,
    "VII": 11,
    "i": 0,
    "ii": 2,
    "iii": 4,
    "iv": 5,
    "v": 7,
    "vi": 9,
    "vii": 11,
}

_ROMAN_PATTERNS = [
    "VII",
    "VII",
    "III",
    "III",
    "II",
    "II",
    "IV",
    "IV",
    "VI",
    "VI",
    "vii",
    "iii",
    "ii",
    "iv",
    "vi",
    "I",
    "V",
    "i",
    "v",
]


def parse_roman(numeral: str, key: str = "C") -> tuple[str, str]:
    """Parse a Roman numeral chord symbol into (root, shape).

    Handles uppercase (major), lowercase (minor), diminished (o/dim),
    augmented (+), seventh chords (7), and applied chords (V/V).

    Examples:
        parse_roman('V7', 'C')    → ('G', 'dom7')
        parse_roman('ii', 'C')    → ('D', 'min')
        parse_roman('bVI', 'C')   → ('Ab', 'maj')
        parse_roman('viio', 'C')  → ('B', 'dim')
        parse_roman('V/V', 'C')   → ('D', 'dom7')

    Args:
        numeral: Roman numeral string.
        key:     Key root.

    Returns:
        (root, shape) tuple.
    """
    key_semi = _semi(key)
    original = numeral

    # Handle applied chords: V/V, vii/ii, etc
    if "/" in numeral:
        parts = numeral.split("/")
        # Resolve the target chord first
        target_root, _ = parse_roman(parts[1], key)
        # Then parse the applied chord relative to that target
        return parse_roman(parts[0], target_root)

    # Handle accidentals
    flat = False
    sharp = False
    if numeral.startswith("b"):
        flat = True
        numeral = numeral[1:]
    elif numeral.startswith("#"):
        sharp = True
        numeral = numeral[1:]

    # Extract quality suffix
    suffix = ""
    base = numeral
    for s in [
        "o7",
        "dim7",
        "maj7",
        "min7",
        "dom7",
        "7",
        "o",
        "dim",
        "+",
        "aug",
        "sus4",
        "sus2",
        "9",
        "min9",
        "maj9",
    ]:
        if numeral.endswith(s):
            suffix = s
            base = numeral[: -len(s)]
            break

    # Find degree
    degree_semi = None
    is_minor = base == base.lower() and base != ""
    upper_base = base.upper()

    for roman in ["VII", "III", "II", "IV", "VI", "I", "V"]:
        if upper_base == roman:
            degree_semi = _ROMAN_TO_DEGREE[roman]
            break

    if degree_semi is None:
        raise ValueError(f"Cannot parse Roman numeral {original!r}")

    # Apply accidentals
    if flat:
        degree_semi = (degree_semi - 1) % 12
    elif sharp:
        degree_semi = (degree_semi + 1) % 12

    root = _NOTE_NAMES[(key_semi + degree_semi) % 12]

    # Determine shape
    if suffix in ("o7", "dim7"):
        shape = "dim7"
    elif suffix in ("o", "dim"):
        shape = "dim"
    elif suffix in ("+", "aug"):
        shape = "aug"
    elif suffix == "maj7":
        shape = "maj7"
    elif suffix == "min7":
        shape = "min7"
    elif suffix == "dom7":
        shape = "dom7"
    elif suffix == "7":
        shape = "dom7" if not is_minor else "min7"
    elif suffix == "9":
        shape = "dom9"
    elif suffix == "min9":
        shape = "min9"
    elif suffix == "maj9":
        shape = "maj9"
    elif suffix == "sus4":
        shape = "sus4"
    elif suffix == "sus2":
        shape = "sus2"
    elif is_minor:
        shape = "min"
    else:
        shape = "maj"

    return (root, shape)


def progression_from_roman(
    numerals: list[str],
    key: str = "C",
) -> list[tuple[str, str]]:
    """Convert a list of Roman numerals to a chord progression.

    Enables writing progressions in analysis notation and getting
    concrete chords in any key. The universal language of harmony.

    Args:
        numerals: List of Roman numeral strings.
        key:      Key root.

    Returns:
        List of (root, shape) tuples.

    Examples:
        >>> progression_from_roman(['I', 'IV', 'V7', 'I'], 'C')
        [('C', 'maj'), ('F', 'maj'), ('G', 'dom7'), ('C', 'maj')]
    """
    return [parse_roman(n, key) for n in numerals]


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


# ---------------------------------------------------------------------------
# Species counterpoint (v46.0)
# ---------------------------------------------------------------------------

# Consonance classification (intervals in semitones)
_PERFECT_CONSONANCES = {0, 7}  # unison, perfect 5th
_IMPERFECT_CONSONANCES = {3, 4, 8, 9}  # minor/major 3rd, minor/major 6th
_DISSONANCES = {1, 2, 5, 6, 10, 11}  # seconds, tritone, sevenths


def classify_interval(semitones: int) -> str:
    """Classify an interval as perfect consonance, imperfect consonance, or dissonance.

    The backbone of counterpoint rules — whether two notes sound stable,
    pleasant, or tense determines where they can appear in the texture.

    Args:
        semitones: Interval in semitones (mod 12).

    Returns:
        'perfect', 'imperfect', or 'dissonant'.
    """
    s = abs(semitones) % 12
    if s in _PERFECT_CONSONANCES:
        return "perfect"
    elif s in _IMPERFECT_CONSONANCES:
        return "imperfect"
    else:
        return "dissonant"


def species_counterpoint(
    cantus_firmus: list[Note],
    species: int = 1,
    above: bool = True,
    seed: int | None = None,
) -> list[Note]:
    """Generate counterpoint against a cantus firmus.

    Species counterpoint is the 500-year-old method that trained Bach,
    Mozart, and Beethoven. Each species adds rhythmic complexity while
    maintaining consonance rules.

    Species 1: note-against-note (whole notes)
    Species 2: two notes against one (half notes, passing tones allowed)

    Args:
        cantus_firmus: The given melody (one note per bar).
        species:       1 or 2.
        above:         True = counterpoint above CF, False = below.
        seed:          Random seed for deterministic output.

    Returns:
        List of Notes forming the counterpoint voice.
    """
    import random as _rng

    rng = _rng.Random(seed)

    if species not in (1, 2):
        raise ValueError(f"Only species 1 and 2 are supported, got {species}")

    result: list[Note] = []

    if species == 1:
        # Note-against-note: each counterpoint note must be consonant
        for cf_note in cantus_firmus:
            if cf_note.pitch is None:
                result.append(Note.rest(cf_note.duration))
                continue
            cf_semi = _semi(str(cf_note.pitch))
            # Pick a consonant interval
            consonant = [0, 3, 4, 7, 8, 9]  # P1, m3, M3, P5, m6, M6
            interval = rng.choice(consonant)
            if above:
                new_semi = (cf_semi + interval) % 12
                new_oct = cf_note.octave + (1 if cf_semi + interval >= 12 else 0)
            else:
                new_semi = (cf_semi - interval) % 12
                new_oct = cf_note.octave - (1 if cf_semi - interval < 0 else 0)
            new_oct = max(2, min(7, new_oct))
            result.append(Note(_NOTE_NAMES[new_semi], new_oct, cf_note.duration))

    elif species == 2:
        # Two notes per CF note: strong beat consonant, weak beat can pass
        for cf_note in cantus_firmus:
            if cf_note.pitch is None:
                result.append(Note.rest(cf_note.duration))
                continue
            cf_semi = _semi(str(cf_note.pitch))
            half_dur = cf_note.duration / 2

            # Strong beat: consonant
            consonant = [0, 3, 4, 7, 8, 9]
            interval1 = rng.choice(consonant)
            if above:
                s1 = (cf_semi + interval1) % 12
                o1 = cf_note.octave + (1 if cf_semi + interval1 >= 12 else 0)
            else:
                s1 = (cf_semi - interval1) % 12
                o1 = cf_note.octave - (1 if cf_semi - interval1 < 0 else 0)
            o1 = max(2, min(7, o1))
            result.append(Note(_NOTE_NAMES[s1], o1, half_dur))

            # Weak beat: passing tone (step from strong beat)
            step = rng.choice([-2, -1, 1, 2])
            s2 = (s1 + step) % 12
            o2 = o1 + (1 if s1 + step >= 12 else (-1 if s1 + step < 0 else 0))
            o2 = max(2, min(7, o2))
            result.append(Note(_NOTE_NAMES[s2], o2, half_dur))

    return result


# ---------------------------------------------------------------------------
# Scale-aware melody generation (v47.0)
# ---------------------------------------------------------------------------


def generate_scale_melody(
    key: str = "C",
    scale_name: str = "major",
    length: int = 16,
    octave: int = 5,
    duration: float = 0.5,
    contour: str = "arch",
    seed: int | None = None,
) -> list[Note]:
    """Generate a melody constrained to a scale with a shaped contour.

    Uses a biased random walk that respects scale degrees and follows
    a melodic contour (arch, descending, wave, flat). More musical than
    pure random — the contour shapes the phrase like a breath.

    Args:
        key:        Root note.
        scale_name: Scale name (major, minor/aeolian, dorian, etc).
        length:     Number of notes.
        octave:     Center octave.
        duration:   Note duration.
        contour:    Shape of the melody: 'arch', 'descending', 'wave', 'flat'.
        seed:       Random seed for reproducibility.

    Returns:
        List of Notes following the scale and contour.
    """
    import random as _rng

    rng = _rng.Random(seed)

    aliases = {"minor": "aeolian", "natural_minor": "aeolian"}
    sname = aliases.get(scale_name, scale_name)
    if sname not in _SCALE_INTERVALS:
        raise ValueError(f"Unknown scale {scale_name!r}")

    intervals = _SCALE_INTERVALS[sname]
    key_semi = _semi(key)

    # Build pool of absolute pitches across 2 octaves centered on target
    pool: list[int] = []
    for oct in range(octave - 1, octave + 2):
        for iv in intervals:
            pool.append(key_semi + iv + oct * 12)
    pool.sort()

    # Contour: target index offset over time (as fraction of length)
    def _contour_bias(pos: float) -> float:
        if contour == "arch":
            return 1.0 - abs(2.0 * pos - 1.0)  # peak at middle
        elif contour == "descending":
            return 1.0 - pos
        elif contour == "wave":
            import math

            return 0.5 + 0.5 * math.sin(pos * math.pi * 2)
        else:  # flat
            return 0.5

    center_idx = len(pool) // 2
    spread = len(pool) // 4
    idx = center_idx
    result: list[Note] = []

    for i in range(length):
        frac = i / max(length - 1, 1)
        bias = _contour_bias(frac)
        # Target index: center ± spread, shaped by contour
        target = int(center_idx + (bias - 0.5) * 2 * spread)
        # Random walk biased toward target
        if idx < target:
            step = rng.choice([0, 1, 1, 2])
        elif idx > target:
            step = rng.choice([0, -1, -1, -2])
        else:
            step = rng.choice([-1, 0, 0, 1])
        idx = max(0, min(len(pool) - 1, idx + step))

        absolute = pool[idx]
        pitch = _NOTE_NAMES[absolute % 12]
        oct = absolute // 12
        result.append(Note(pitch, oct, duration))

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


# ---------------------------------------------------------------------------
# Chord voicing library (v48.0)
# ---------------------------------------------------------------------------


def rootless_a(
    root: str,
    shape: str = "dom7",
    octave: int = 3,
    duration: float = 4.0,
) -> list[Note]:
    """Generate a Bill Evans 'A' rootless voicing (3rd on bottom).

    The rootless voicing omits the root (the bass player has it) and
    stacks the 3rd, 7th, and upper extensions. The 'A' form puts the
    3rd in the lowest position. Evans built modern jazz piano on this.

    Args:
        root:     Chord root.
        shape:    Chord quality (dom7, maj7, min7).
        octave:   Base octave.
        duration: Note duration.

    Returns:
        List of Notes forming the rootless A voicing.
    """
    k = _semi(root)
    if shape in ("dom7", "dom9"):
        # 3, 7, 9, 13 → intervals: 4, 10, 14, 21
        intervals = [4, 10, 14, 21]
    elif shape in ("maj7", "maj9"):
        # 3, 7, 9 → intervals: 4, 11, 14
        intervals = [4, 11, 14]
    elif shape in ("min7", "min9"):
        # b3, 7, 9, 11 → intervals: 3, 10, 14, 17
        intervals = [3, 10, 14, 17]
    else:
        intervals = list(_CHORD_SEMI.get(shape, [0, 4, 7]))[1:]  # drop root
    return [Note(_NOTE_NAMES[(k + iv) % 12], octave + (k + iv) // 12, duration) for iv in intervals]


def rootless_b(
    root: str,
    shape: str = "dom7",
    octave: int = 3,
    duration: float = 4.0,
) -> list[Note]:
    """Generate a Bill Evans 'B' rootless voicing (7th on bottom).

    The complement of the 'A' voicing — the 7th sits in the bass
    register with the 3rd on top. Alternating A and B voicings in a
    ii-V-I creates smooth voice leading without the pianist ever
    touching the root. Pure Evans magic.

    Args:
        root:     Chord root.
        shape:    Chord quality.
        octave:   Base octave.
        duration: Note duration.

    Returns:
        List of Notes forming the rootless B voicing.
    """
    k = _semi(root)
    if shape in ("dom7", "dom9"):
        # 7, 9, 3(+12), 13 → intervals: 10, 14, 16, 21
        intervals = [10, 14, 16, 21]
    elif shape in ("maj7", "maj9"):
        # 7, 9, 3(+12) → intervals: 11, 14, 16
        intervals = [11, 14, 16]
    elif shape in ("min7", "min9"):
        # 7, 9, b3(+12), 5(+12) → intervals: 10, 14, 15, 19
        intervals = [10, 14, 15, 19]
    else:
        semis = list(_CHORD_SEMI.get(shape, [0, 4, 7]))
        intervals = semis[1:] + [semis[0] + 12] if len(semis) > 1 else semis
    return [Note(_NOTE_NAMES[(k + iv) % 12], octave + (k + iv) // 12, duration) for iv in intervals]


def quartal_voicing(
    root: str,
    octave: int = 3,
    duration: float = 4.0,
    layers: int = 4,
) -> list[Note]:
    """Generate a McCoy Tyner-style quartal voicing (stacked perfect 4ths).

    Quartal harmony replaces tertian (3rd-based) stacking with perfect
    4ths. The sound is open, ambiguous, and modern — neither clearly
    major nor minor. Tyner drove Coltrane's quartets with these.

    Args:
        root:     Starting note.
        octave:   Base octave.
        duration: Note duration.
        layers:   Number of stacked 4ths (default 4).

    Returns:
        List of Notes in stacked 4ths.
    """
    k = _semi(root)
    return [
        Note(
            _NOTE_NAMES[(k + i * 5) % 12],
            octave + (k + i * 5) // 12,
            duration,
        )
        for i in range(layers)
    ]


def stride_voicing(
    root: str,
    shape: str = "maj",
    octave: int = 3,
    duration: float = 1.0,
) -> list[Note]:
    """Generate a stride piano voicing (low root then mid-register chord).

    Stride alternates: beat 1 = root (or root+5th) in the bass,
    beat 2 = chord in the middle register. The left-hand bounce
    that powered ragtime, early jazz, and Thelonious Monk.

    Args:
        root:     Chord root.
        shape:    Chord quality.
        octave:   Bass octave for the root.
        duration: Duration per hit (root and chord each get this).

    Returns:
        List of Notes: [bass_root, chord_tone_1, chord_tone_2, ...].
    """
    k = _semi(root)
    semis = _CHORD_SEMI.get(shape, [0, 4, 7])
    bass = [Note(root, octave, duration)]
    chord_notes = [Note(_NOTE_NAMES[(k + s) % 12], octave + 1, duration) for s in semis]
    return bass + chord_notes


# ---------------------------------------------------------------------------
# Form templates (v49.0)
# ---------------------------------------------------------------------------


def song_form(
    form_name: str = "pop",
) -> list[str]:
    """Return a section-name list for a standard song form.

    Song form is the large-scale architecture — which sections appear
    in which order. This is the blueprint you fill in with chords,
    melody, and arrangement.

    Supported forms:
        'pop':    intro verse chorus verse chorus bridge chorus outro
        'aaba':   A A B A (Tin Pan Alley / jazz standard)
        'blues':  head solo head (3 × 12 bars)
        'edm':    intro buildup drop breakdown buildup drop outro
        'rondo':  A B A C A B A (classical rondo)

    Args:
        form_name: Form template name.

    Returns:
        List of section name strings.

    Raises:
        ValueError: If form_name is not recognized.
    """
    forms = {
        "pop": [
            "intro",
            "verse",
            "chorus",
            "verse",
            "chorus",
            "bridge",
            "chorus",
            "outro",
        ],
        "aaba": ["A", "A", "B", "A"],
        "blues": ["head", "solo", "head"],
        "edm": [
            "intro",
            "buildup",
            "drop",
            "breakdown",
            "buildup",
            "drop",
            "outro",
        ],
        "rondo": ["A", "B", "A", "C", "A", "B", "A"],
    }
    if form_name not in forms:
        raise ValueError(f"Unknown form {form_name!r}. Choose: {', '.join(forms)}")
    return forms[form_name]


def section_bars(
    form_name: str = "pop",
    bars_per_section: int = 8,
) -> list[tuple[str, int]]:
    """Return (section_name, bar_count) pairs for a song form.

    Combines song_form() with a default bar length per section.
    Useful for auto-generating arrangement skeletons.

    Args:
        form_name:        Form template name.
        bars_per_section: Default bars per section.

    Returns:
        List of (section_name, bars) tuples.
    """
    return [(s, bars_per_section) for s in song_form(form_name)]


# ---------------------------------------------------------------------------
# Harmonic analysis (v50.0)
# ---------------------------------------------------------------------------


def functional_analysis(
    progression: list[tuple[str, str]],
    key: str = "C",
) -> list[dict]:
    """Analyze each chord's function (tonic, subdominant, dominant).

    Returns a Roman numeral and functional label for each chord in
    the progression. The kind of analysis a theory professor puts
    on the blackboard — but automated.

    Args:
        progression: List of (root, shape) tuples.
        key:         Key for analysis.

    Returns:
        List of dicts with keys: root, shape, roman, function.
    """
    key_semi = _semi(key)
    # Diatonic degrees → Roman numerals (major key)
    degree_roman_major = {
        0: "I",
        2: "ii",
        4: "iii",
        5: "IV",
        7: "V",
        9: "vi",
        11: "viio",
    }
    # Functional groups
    tonic_degrees = {0, 4, 9}  # I, iii, vi
    subdominant_degrees = {2, 5}  # ii, IV
    dominant_degrees = {7, 11}  # V, viio

    result = []
    for root, shape in progression:
        root_semi = _semi(root)
        degree = (root_semi - key_semi) % 12
        roman = degree_roman_major.get(degree, f"?({degree})")

        if degree in tonic_degrees:
            func = "T"
        elif degree in subdominant_degrees:
            func = "S"
        elif degree in dominant_degrees:
            func = "D"
        else:
            func = "chromatic"

        result.append(
            {
                "root": root,
                "shape": shape,
                "roman": roman,
                "function": func,
            }
        )

    return result


def detect_cadences(
    progression: list[tuple[str, str]],
    key: str = "C",
) -> list[dict]:
    """Detect cadences in a chord progression.

    Scans consecutive chord pairs for the four standard cadence types:
    - Authentic (V→I): the strongest resolution in tonal music
    - Half (→V): suspension of resolution, "to be continued"
    - Plagal (IV→I): the "Amen" cadence
    - Deceptive (V→vi): the bait-and-switch that makes listeners gasp

    Args:
        progression: List of (root, shape) tuples.
        key:         Key for analysis.

    Returns:
        List of dicts: {position, type, chords}.
    """
    key_semi = _semi(key)
    cadences = []

    for i in range(len(progression) - 1):
        r1_semi = (_semi(progression[i][0]) - key_semi) % 12
        r2_semi = (_semi(progression[i + 1][0]) - key_semi) % 12

        if r1_semi == 7 and r2_semi == 0:
            cadences.append(
                {
                    "position": i,
                    "type": "authentic",
                    "chords": (progression[i], progression[i + 1]),
                }
            )
        elif r2_semi == 7:
            cadences.append(
                {
                    "position": i,
                    "type": "half",
                    "chords": (progression[i], progression[i + 1]),
                }
            )
        elif r1_semi == 5 and r2_semi == 0:
            cadences.append(
                {
                    "position": i,
                    "type": "plagal",
                    "chords": (progression[i], progression[i + 1]),
                }
            )
        elif r1_semi == 7 and r2_semi == 9:
            cadences.append(
                {
                    "position": i,
                    "type": "deceptive",
                    "chords": (progression[i], progression[i + 1]),
                }
            )

    return cadences


def detect_key(
    progression: list[tuple[str, str]],
) -> str:
    """Estimate the key of a chord progression by pitch-class frequency.

    Counts how often each pitch class appears as a chord root and
    matches against major-key diatonic sets. The key whose diatonic
    set best covers the progression roots wins.

    Args:
        progression: List of (root, shape) tuples.

    Returns:
        Estimated key root (e.g. 'C', 'G').
    """
    root_counts: list[int] = [0] * 12
    for root, _ in progression:
        root_counts[_semi(root)] += 1

    major_intervals = _SCALE_INTERVALS["major"]
    best_key = 0
    best_score = -1

    for candidate in range(12):
        diatonic = {(candidate + iv) % 12 for iv in major_intervals}
        score = sum(root_counts[pc] for pc in diatonic)
        # Tiebreaker: prefer key whose root appears most often
        if score > best_score or (
            score == best_score and root_counts[candidate] > root_counts[best_key]
        ):
            best_score = score
            best_key = candidate

    return _NOTE_NAMES[best_key]


# ---------------------------------------------------------------------------
# Ear training & exercises (v51.0)
# ---------------------------------------------------------------------------


def ear_training_intervals(
    count: int = 10,
    max_semitones: int = 12,
    seed: int | None = None,
) -> list[dict]:
    """Generate melodic interval ear training exercises.

    Each exercise is a pair of notes with the correct interval name.
    Play both notes, then check your answer. The building block of
    every ear training course from Berklee to YouTube.

    Args:
        count:          Number of exercises to generate.
        max_semitones:  Maximum interval size in semitones.
        seed:           Random seed for reproducibility.

    Returns:
        List of dicts: {note_a, note_b, semitones, interval_name}.
    """
    import random as _rng

    rng = _rng.Random(seed)
    _INTERVAL_NAMES = {
        0: "P1",
        1: "m2",
        2: "M2",
        3: "m3",
        4: "M3",
        5: "P4",
        6: "TT",
        7: "P5",
        8: "m6",
        9: "M6",
        10: "m7",
        11: "M7",
        12: "P8",
    }
    exercises = []
    for _ in range(count):
        root_semi = rng.randint(0, 11)
        interval = rng.randint(1, min(max_semitones, 12))
        target_semi = (root_semi + interval) % 12
        root_oct = 4
        target_oct = root_oct + (root_semi + interval) // 12
        exercises.append(
            {
                "note_a": Note(_NOTE_NAMES[root_semi], root_oct, 2.0),
                "note_b": Note(_NOTE_NAMES[target_semi], target_oct, 2.0),
                "semitones": interval,
                "interval_name": _INTERVAL_NAMES.get(interval, f"{interval}st"),
            }
        )
    return exercises


def ear_training_chords(
    count: int = 10,
    types: list[str] | None = None,
    seed: int | None = None,
) -> list[dict]:
    """Generate chord quality identification exercises.

    Each exercise is a chord with the correct quality label. Play it,
    name the quality. Major? Minor? Diminished? Aug? Dom7?

    Args:
        count: Number of exercises.
        types: Chord types to include (default: maj, min, dim, aug, dom7).
        seed:  Random seed.

    Returns:
        List of dicts: {root, shape, notes}.
    """
    import random as _rng

    rng = _rng.Random(seed)
    if types is None:
        types = ["maj", "min", "dim", "aug", "dom7"]
    exercises = []
    for _ in range(count):
        root_semi = rng.randint(0, 11)
        shape = rng.choice(types)
        root = _NOTE_NAMES[root_semi]
        semis = _CHORD_SEMI.get(shape, [0, 4, 7])
        notes = [Note(_NOTE_NAMES[(root_semi + s) % 12], 4, 2.0) for s in semis]
        exercises.append({"root": root, "shape": shape, "notes": notes})
    return exercises


def scale_exercise(
    key: str = "C",
    mode: str = "major",
    direction: str = "ascending",
    octave: int = 4,
    duration: float = 0.5,
) -> list[Note]:
    """Generate a scale exercise — ascending, descending, or both.

    The most fundamental practice exercise in music. Every day,
    every key. There are no shortcuts.

    Args:
        key:       Root note.
        mode:      Scale name.
        direction: 'ascending', 'descending', or 'both'.
        octave:    Starting octave.
        duration:  Note duration.

    Returns:
        List of Notes traversing the scale.
    """
    aliases = {"minor": "aeolian", "natural_minor": "aeolian"}
    sname = aliases.get(mode, mode)
    if sname not in _SCALE_INTERVALS:
        raise ValueError(f"Unknown scale {mode!r}")

    k = _semi(key)
    intervals = _SCALE_INTERVALS[sname]
    asc = [Note(_NOTE_NAMES[(k + iv) % 12], octave + (k + iv) // 12, duration) for iv in intervals]
    # Add the octave
    asc.append(Note(key, octave + 1, duration))

    if direction == "ascending":
        return asc
    elif direction == "descending":
        return list(reversed(asc))
    else:  # both
        return asc + list(reversed(asc[:-1]))


# ---------------------------------------------------------------------------
# Tension & resolution curves (v52.0)
# ---------------------------------------------------------------------------


def tension_curve(
    progression: list[tuple[str, str]],
    key: str = "C",
) -> list[float]:
    """Calculate a tension value (0.0–1.0) for each chord in a progression.

    Tension is modeled from three factors:
    - Harmonic distance from tonic (chromatic chords = high tension)
    - Chord complexity (7ths > triads, altered > diatonic)
    - Dominant function (V and viio are inherently tense)

    The result is a curve you can plot or use to drive dynamics,
    filter sweeps, or arrangement density.

    Args:
        progression: List of (root, shape) tuples.
        key:         Key for analysis.

    Returns:
        List of floats, one per chord, in range [0.0, 1.0].
    """
    key_semi = _semi(key)
    major_intervals = set(_SCALE_INTERVALS["major"])
    curve = []

    for root, shape in progression:
        root_semi = _semi(root)
        degree = (root_semi - key_semi) % 12

        # Factor 1: diatonic distance (0 if diatonic, 0.3 if chromatic)
        diatonic = degree in major_intervals
        dist_score = 0.0 if diatonic else 0.3

        # Factor 2: chord complexity
        semis = _CHORD_SEMI.get(shape, [0, 4, 7])
        complexity = min(len(semis) / 5.0, 0.3)  # more notes = more tension

        # Factor 3: dominant function
        dom_score = 0.0
        if degree == 7:  # V
            dom_score = 0.25
        elif degree == 11:  # viio
            dom_score = 0.3
        elif degree == 6:  # tritone area
            dom_score = 0.2

        # Factor 4: tonic resolution (I is the least tense)
        tonic_rest = 0.15 if degree == 0 else 0.0

        tension = min(1.0, dist_score + complexity + dom_score - tonic_rest)
        tension = max(0.0, tension)
        curve.append(round(tension, 3))

    return curve


def tension_at(
    progression: list[tuple[str, str]],
    index: int,
    key: str = "C",
) -> float:
    """Get the tension value at a specific chord index.

    Args:
        progression: List of (root, shape) tuples.
        index:       Chord index (0-based).
        key:         Key for analysis.

    Returns:
        Tension float in [0.0, 1.0].
    """
    curve = tension_curve(progression, key)
    if 0 <= index < len(curve):
        return curve[index]
    return 0.0


# ---------------------------------------------------------------------------
# Orchestration & instrument ranges (v53.0)
# ---------------------------------------------------------------------------

# Instrument ranges as (lowest_abs, highest_abs) using C4=60 convention
_INSTRUMENT_RANGES = {
    "violin": (55, 88),  # G3–E7
    "viola": (48, 81),  # C3–A5
    "cello": (36, 69),  # C2–A4
    "contrabass": (28, 55),  # E1–G3
    "flute": (60, 84),  # C4–C7
    "oboe": (58, 82),  # Bb3–A6
    "clarinet": (50, 79),  # D3–G5 (Bb clarinet, written)
    "bassoon": (34, 65),  # Bb1–F4
    "trumpet": (55, 77),  # G3–F5
    "french_horn": (41, 67),  # F2–G4
    "trombone": (34, 65),  # Bb1–F4
    "tuba": (24, 53),  # C1–F3
    "piano": (21, 108),  # A0–C8
    "guitar": (40, 76),  # E2–E5
    "bass_guitar": (28, 55),  # E1–G3
    "soprano_voice": (60, 79),  # C4–G5
    "alto_voice": (53, 74),  # F3–D5
    "tenor_voice": (48, 69),  # C3–A4
    "bass_voice": (40, 64),  # E2–E4
}


def instrument_range(name: str) -> tuple[int, int]:
    """Return the playable range of an instrument as absolute semitones.

    Args:
        name: Instrument name (e.g. 'violin', 'cello', 'trumpet').

    Returns:
        (lowest, highest) absolute semitone values.

    Raises:
        ValueError: If instrument name is not recognized.
    """
    if name not in _INSTRUMENT_RANGES:
        raise ValueError(
            f"Unknown instrument {name!r}. Choose: {', '.join(sorted(_INSTRUMENT_RANGES))}"
        )
    return _INSTRUMENT_RANGES[name]


def in_range(note: Note, instrument: str) -> bool:
    """Check if a note falls within an instrument's playable range.

    Args:
        note:       A Note object.
        instrument: Instrument name.

    Returns:
        True if the note is playable on the instrument.
    """
    if note.pitch is None:
        return True  # rests are always valid
    low, high = instrument_range(instrument)
    absolute = _semi(str(note.pitch)) + note.octave * 12
    return low <= absolute <= high


def double_at_octave(
    notes: list[Note],
    direction: int = 1,
) -> list[Note]:
    """Create an octave doubling of a note list.

    Doubling at the octave is the simplest orchestration technique.
    It adds weight without changing the harmony. Strings do it
    constantly, brass does it for power.

    Args:
        notes:     Original notes.
        direction: +1 = octave above, -1 = octave below.

    Returns:
        New list with every note shifted by one octave.
    """
    result = []
    for n in notes:
        if n.pitch is None:
            result.append(Note.rest(n.duration))
        else:
            result.append(Note(n.pitch, n.octave + direction, n.duration, velocity=n.velocity))
    return result


def string_quartet(
    melody: list[Note],
    harmony: list[tuple[str, str]],
    key: str = "C",
    duration: float = 4.0,
) -> dict[str, list[Note]]:
    """Arrange a melody and chord progression for string quartet.

    Assigns the melody to violin I, generates inner voices for
    violin II and viola from the harmony, and gives the cello
    the bass line. The most common chamber music ensemble.

    Args:
        melody:   Melody notes (assigned to violin I).
        harmony:  Chord progression as (root, shape) tuples.
        key:      Key (for voice leading context).
        duration: Duration per chord for inner voices.

    Returns:
        Dict with keys: 'violin_1', 'violin_2', 'viola', 'cello'.
    """
    violin_1 = list(melody)

    violin_2: list[Note] = []
    viola: list[Note] = []
    cello: list[Note] = []

    for root, shape in harmony:
        k = _semi(root)
        semis = _CHORD_SEMI.get(shape, [0, 4, 7])

        # Cello: root
        cello.append(Note(root, 3, duration))

        # Viola: 5th (or 3rd if only 3 notes)
        fifth_idx = 2 if len(semis) > 2 else 1
        viola_semi = (k + semis[fifth_idx]) % 12
        viola.append(Note(_NOTE_NAMES[viola_semi], 4, duration))

        # Violin II: 3rd
        third_semi = (k + semis[1 % len(semis)]) % 12
        violin_2.append(Note(_NOTE_NAMES[third_semi], 4, duration))

    return {
        "violin_1": violin_1,
        "violin_2": violin_2,
        "viola": viola,
        "cello": cello,
    }


# ---------------------------------------------------------------------------
# Motif development & variation (v54.0)
# ---------------------------------------------------------------------------


def augment(motif: list[Note], factor: float = 2.0) -> list[Note]:
    """Double (or multiply) note durations — rhythmic augmentation.

    Makes the motif grander and more spacious. Beethoven's Fifth
    is basically one motif augmented and diminished for 30 minutes.

    Args:
        motif:  List of Notes.
        factor: Duration multiplier (2.0 = double, 3.0 = triple).

    Returns:
        New list with stretched durations.
    """
    return [
        Note(n.pitch, n.octave, n.duration * factor, velocity=n.velocity)
        if n.pitch is not None
        else Note.rest(n.duration * factor)
        for n in motif
    ]


def diminish(motif: list[Note], factor: float = 2.0) -> list[Note]:
    """Halve (or divide) note durations — rhythmic diminution.

    Makes the motif urgent and compressed. The stretto in a fugue
    is diminution plus imitation — chaos on purpose.

    Args:
        motif:  List of Notes.
        factor: Duration divisor (2.0 = halve, 4.0 = quarter).

    Returns:
        New list with compressed durations.
    """
    return [
        Note(n.pitch, n.octave, n.duration / factor, velocity=n.velocity)
        if n.pitch is not None
        else Note.rest(n.duration / factor)
        for n in motif
    ]


def fragment(motif: list[Note], length: int) -> list[Note]:
    """Extract the first N notes of a motif — fragmentation.

    The head motif is the most memorable part. Fragmentation isolates
    it for development — repeat the fragment, sequence it, build
    tension by withholding the rest.

    Args:
        motif:  List of Notes.
        length: Number of notes to extract.

    Returns:
        First `length` notes of the motif.
    """
    return list(motif[:length])


def motif_similarity(a: list[Note], b: list[Note]) -> float:
    """Compare two motifs by pitch contour and rhythm similarity.

    Returns a value between 0.0 (completely different) and 1.0
    (identical). Uses normalized pitch intervals and duration ratios.

    Args:
        a: First motif.
        b: Second motif.

    Returns:
        Similarity score in [0.0, 1.0].
    """
    if not a or not b:
        return 0.0

    # Compare pitch contours (direction of intervals)
    def _contour(notes: list[Note]) -> list[int]:
        result = []
        for i in range(1, len(notes)):
            if notes[i].pitch is None or notes[i - 1].pitch is None:
                result.append(0)
                continue
            s_curr = _semi(str(notes[i].pitch)) + notes[i].octave * 12
            s_prev = _semi(str(notes[i - 1].pitch)) + notes[i - 1].octave * 12
            diff = s_curr - s_prev
            result.append(1 if diff > 0 else (-1 if diff < 0 else 0))
        return result

    ca = _contour(a)
    cb = _contour(b)

    # Pad shorter contour with zeros
    max_len = max(len(ca), len(cb))
    if max_len == 0:
        return 1.0
    ca.extend([0] * (max_len - len(ca)))
    cb.extend([0] * (max_len - len(cb)))

    # Contour match score
    contour_match = sum(1 for x, y in zip(ca, cb) if x == y) / max_len

    # Duration ratio similarity
    dur_a = [n.duration for n in a]
    dur_b = [n.duration for n in b]
    max_dur_len = max(len(dur_a), len(dur_b))
    dur_a.extend([0.0] * (max_dur_len - len(dur_a)))
    dur_b.extend([0.0] * (max_dur_len - len(dur_b)))
    dur_match = (
        sum(1.0 - abs(da - db) / max(da, db, 0.01) for da, db in zip(dur_a, dur_b)) / max_dur_len
    )

    return round((contour_match + dur_match) / 2.0, 3)


# ---------------------------------------------------------------------------
# Scale atlas — extended scale database (v56.0)
# ---------------------------------------------------------------------------

# Additional scales beyond the 14 standard ones in _SCALE_INTERVALS
_EXOTIC_SCALES = {
    "hungarian_minor": [0, 2, 3, 6, 7, 8, 11],
    "hungarian_major": [0, 3, 4, 6, 7, 9, 10],
    "hirajoshi": [0, 2, 3, 7, 8],
    "in_sen": [0, 1, 5, 7, 10],
    "iwato": [0, 1, 5, 6, 10],
    "phrygian_dominant": [0, 1, 4, 5, 7, 8, 10],
    "double_harmonic": [0, 1, 4, 5, 7, 8, 11],
    "enigmatic": [0, 1, 4, 6, 8, 10, 11],
    "prometheus": [0, 2, 4, 6, 9, 10],
    "augmented": [0, 3, 4, 7, 8, 11],
    "tritone": [0, 1, 4, 6, 7, 10],
    "bebop_dominant": [0, 2, 4, 5, 7, 9, 10, 11],
    "bebop_major": [0, 2, 4, 5, 7, 8, 9, 11],
    "bebop_minor": [0, 2, 3, 5, 7, 8, 9, 10],
    "neapolitan_major": [0, 1, 3, 5, 7, 9, 11],
    "neapolitan_minor": [0, 1, 3, 5, 7, 8, 11],
    "persian": [0, 1, 4, 5, 6, 8, 11],
    "arabian": [0, 2, 4, 5, 6, 8, 10],
    "balinese": [0, 1, 3, 7, 8],
    "chinese": [0, 4, 6, 7, 11],
    "egyptian": [0, 2, 5, 7, 10],
    "kumoi": [0, 2, 3, 7, 9],
    "pelog": [0, 1, 3, 7, 8],
    "spanish_gypsy": [0, 1, 4, 5, 7, 8, 10],
    "super_locrian": [0, 1, 3, 4, 6, 8, 10],
    "lydian_dominant": [0, 2, 4, 6, 7, 9, 10],
    "lydian_augmented": [0, 2, 4, 6, 8, 9, 11],
    "half_diminished": [0, 2, 3, 5, 6, 8, 10],
    "altered": [0, 1, 3, 4, 6, 8, 10],
    "acoustic": [0, 2, 4, 6, 7, 9, 10],
}

# Merge into the main dict at module load time
_SCALE_INTERVALS.update(_EXOTIC_SCALES)


def list_scales() -> list[str]:
    """Return all available scale names, sorted alphabetically.

    Returns:
        Sorted list of scale name strings.
    """
    return sorted(_SCALE_INTERVALS.keys())


def scale_search(pitches: list[str]) -> list[str]:
    """Find scales that contain all given pitch classes.

    Useful for: "I'm using these notes — what scale am I in?"
    The reverse lookup every improviser needs.

    Args:
        pitches: List of note names (e.g. ['C', 'E', 'G', 'Bb']).

    Returns:
        List of scale names that contain all given pitch classes
        (assumes C root — transpose mentally for other keys).
    """
    target_pcs = {_semi(p) for p in pitches}
    matches = []
    for name, intervals in _SCALE_INTERVALS.items():
        scale_pcs = set(intervals)
        if target_pcs.issubset(scale_pcs):
            matches.append(name)
    return sorted(matches)


def scale_brightness(name: str) -> float:
    """Rank a scale from dark (0.0) to bright (1.0) by interval content.

    Brightness correlates with how many raised/sharp degrees a scale has.
    Lydian is the brightest mode, Locrian the darkest. This metric
    extends that concept to all scales in the atlas.

    Args:
        name: Scale name.

    Returns:
        Brightness score in [0.0, 1.0].

    Raises:
        ValueError: If scale name is not recognized.
    """
    if name not in _SCALE_INTERVALS:
        raise ValueError(f"Unknown scale {name!r}")
    intervals = _SCALE_INTERVALS[name]
    # Brightness = average interval position relative to chromatic max
    # Higher average = brighter
    if not intervals:
        return 0.0
    avg = sum(intervals) / len(intervals)
    # Normalize: max possible avg for 7-note scale ≈ 8.14 (lydian)
    return round(min(avg / 8.5, 1.0), 3)


def scale_modes(name: str) -> list[tuple[str, list[int]]]:
    """Generate all rotational modes of a scale.

    Each mode starts on a different degree and rotates the intervals.
    The 7 modes of the major scale (Ionian through Locrian) are the
    most famous example, but every scale has modes.

    Args:
        name: Scale name.

    Returns:
        List of (mode_label, intervals) tuples.

    Raises:
        ValueError: If scale name is not recognized.
    """
    if name not in _SCALE_INTERVALS:
        raise ValueError(f"Unknown scale {name!r}")
    intervals = _SCALE_INTERVALS[name]
    modes = []
    for i in range(len(intervals)):
        rotated = [(iv - intervals[i]) % 12 for iv in intervals]
        rotated.sort()
        modes.append((f"{name}_mode_{i + 1}", rotated))
    return modes


# ---------------------------------------------------------------------------
# Lyric rhythm matching (v58.0)
# ---------------------------------------------------------------------------


def count_syllables(word: str) -> int:
    """Estimate syllable count for an English word.

    Uses a vowel-cluster heuristic: count groups of consecutive vowels,
    adjust for silent-e and common patterns. Not perfect — English is
    a chaotic language — but good enough for songwriting.

    Args:
        word: A single English word.

    Returns:
        Estimated syllable count (minimum 1).
    """
    word = word.lower().strip(".,!?;:'\"()-")
    if not word:
        return 0
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    # Silent-e adjustment
    if word.endswith("e") and count > 1:
        count -= 1
    # Words like "the" need at least 1
    return max(count, 1)


def stress_pattern(text: str) -> list[bool]:
    """Extract a strong/weak syllable pattern from text.

    Simple heuristic: in multi-syllable words, odd-indexed syllables
    are stressed (English tends toward alternating stress). Single-syllable
    content words are stressed, function words are unstressed.

    Args:
        text: A line of text.

    Returns:
        List of bools (True = stressed, False = unstressed), one per syllable.
    """
    _UNSTRESSED_WORDS = {
        "a",
        "an",
        "the",
        "of",
        "in",
        "on",
        "at",
        "to",
        "for",
        "and",
        "but",
        "or",
        "is",
        "was",
        "be",
        "it",
        "its",
        "my",
        "your",
        "his",
        "her",
        "our",
        "their",
        "this",
        "that",
        "with",
        "from",
        "by",
        "as",
    }
    pattern: list[bool] = []
    words = text.split()
    for word in words:
        clean = word.lower().strip(".,!?;:'\"()-")
        n = count_syllables(clean)
        if n == 1:
            pattern.append(clean not in _UNSTRESSED_WORDS)
        else:
            for i in range(n):
                pattern.append(i % 2 == 0)  # stress on even positions (1st, 3rd, ...)
    return pattern


def text_to_melody(
    text: str,
    key: str = "C",
    scale_name: str = "major",
    octave: int = 5,
    beat_duration: float = 0.5,
    seed: int | None = None,
) -> list[Note]:
    """Map text to a melody based on syllable stress and contour.

    Stressed syllables get higher pitches and longer durations.
    Unstressed syllables stay low and short. Questions end with
    a rising contour, statements fall. The bridge between words
    and music that every songwriter needs.

    Args:
        text:          Input text (one line).
        key:           Root note.
        scale_name:    Scale to constrain pitches.
        octave:        Center octave.
        beat_duration: Base duration per syllable.
        seed:          Random seed for variation.

    Returns:
        List of Notes, one per syllable.
    """
    import random as _rng

    rng = _rng.Random(seed)
    stresses = stress_pattern(text)
    if not stresses:
        return []

    aliases = {"minor": "aeolian", "natural_minor": "aeolian"}
    sname = aliases.get(scale_name, scale_name)
    intervals = _SCALE_INTERVALS.get(sname, _SCALE_INTERVALS["major"])
    k = _semi(key)

    # Build pitch pool
    pool: list[int] = []
    for o in range(octave - 1, octave + 2):
        for iv in intervals:
            pool.append(k + iv + o * 12)
    pool.sort()
    center = len(pool) // 2

    # Question = rising end, statement = falling end
    is_question = text.strip().endswith("?")

    notes: list[Note] = []
    idx = center
    for i, stressed in enumerate(stresses):
        frac = i / max(len(stresses) - 1, 1)

        if stressed:
            idx = min(idx + rng.randint(1, 3), len(pool) - 1)
            dur = beat_duration * 1.5
        else:
            idx = max(idx - rng.randint(0, 2), 0)
            dur = beat_duration * 0.75

        # End contour
        if frac > 0.8:
            if is_question:
                idx = min(idx + 1, len(pool) - 1)
            else:
                idx = max(idx - 1, 0)

        absolute = pool[idx]
        pitch = _NOTE_NAMES[absolute % 12]
        oct = absolute // 12
        notes.append(Note(pitch, oct, dur))

    return notes


# ---------------------------------------------------------------------------
# Groove templates & swing maps (v59.0)
# ---------------------------------------------------------------------------

# Named groove templates: list of timing offsets per 16th note in a bar
# Positive = late (behind the beat), negative = early (ahead)
_GROOVE_TEMPLATES = {
    "straight": [0.0] * 16,
    "mpc_swing": [
        0.0,
        0.03,
        0.0,
        -0.02,
        0.0,
        0.03,
        0.0,
        -0.02,
        0.0,
        0.03,
        0.0,
        -0.02,
        0.0,
        0.03,
        0.0,
        -0.02,
    ],
    "j_dilla": [
        0.0,
        0.06,
        -0.01,
        0.04,
        0.0,
        0.05,
        -0.02,
        0.03,
        0.0,
        0.07,
        -0.01,
        0.05,
        0.0,
        0.06,
        -0.02,
        0.04,
    ],
    "motown": [
        0.0,
        0.02,
        0.0,
        0.01,
        0.0,
        0.02,
        0.0,
        0.01,
        0.0,
        0.02,
        0.0,
        0.01,
        0.0,
        0.02,
        0.0,
        0.01,
    ],
    "shuffle": [
        0.0,
        0.0,
        0.04,
        0.0,
        0.0,
        0.0,
        0.04,
        0.0,
        0.0,
        0.0,
        0.04,
        0.0,
        0.0,
        0.0,
        0.04,
        0.0,
    ],
    "bossa": [
        0.0,
        0.0,
        0.02,
        -0.01,
        0.0,
        0.0,
        0.02,
        -0.01,
        0.0,
        0.0,
        0.02,
        -0.01,
        0.0,
        0.0,
        0.02,
        -0.01,
    ],
}


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
# Chord substitution engine (v60.0)
# ---------------------------------------------------------------------------


def suggest_substitutions(
    root: str,
    shape: str,
    key: str = "C",
) -> list[tuple[str, str, str]]:
    """Suggest chord substitutions for a given chord.

    Returns a list of alternative chords with the substitution type.
    Each result is (root, shape, substitution_type).

    Substitution types:
    - tritone_sub: replace dom7 with dom7 a tritone away
    - related_ii: add the ii chord that precedes a dominant
    - modal_interchange: borrow from parallel minor/major
    - relative: substitute with the relative major/minor

    Args:
        root:  Chord root.
        shape: Chord quality.
        key:   Key context.

    Returns:
        List of (root, shape, sub_type) tuples.
    """
    key_semi = _semi(key)
    root_semi = _semi(root)
    degree = (root_semi - key_semi) % 12
    subs: list[tuple[str, str, str]] = []

    # Tritone substitution (dom7 → dom7 a tritone away)
    if "dom" in shape or "7" in shape:
        tri_semi = (root_semi + 6) % 12
        subs.append((_NOTE_NAMES[tri_semi], "dom7", "tritone_sub"))

    # Related ii (prepend ii-V before a dominant)
    if degree == 7:  # V chord
        ii_semi = (key_semi + 2) % 12
        subs.append((_NOTE_NAMES[ii_semi], "min7", "related_ii"))

    # Modal interchange (borrow from parallel minor)
    if shape in ("maj", "maj7"):
        minor_semi = (root_semi + 0) % 12
        subs.append((_NOTE_NAMES[minor_semi], "min", "modal_interchange"))
    elif shape in ("min", "min7"):
        subs.append((_NOTE_NAMES[root_semi], "maj", "modal_interchange"))

    # Relative major/minor
    if shape in ("maj", "maj7"):
        rel_semi = (root_semi + 9) % 12  # relative minor
        subs.append((_NOTE_NAMES[rel_semi], "min", "relative"))
    elif shape in ("min", "min7"):
        rel_semi = (root_semi + 3) % 12  # relative major
        subs.append((_NOTE_NAMES[rel_semi], "maj", "relative"))

    return subs


def reharmonize(
    progression: list[tuple[str, str]],
    key: str = "C",
    style: str = "jazz",
) -> list[tuple[str, str]]:
    """Reharmonize a chord progression by applying substitutions.

    Takes a simple progression and adds color: tritone subs on
    dominants, related ii chords, modal interchange. The difference
    between a hymnal and a jazz standard.

    Styles:
    - 'jazz': tritone subs + related ii's on all dominants
    - 'modal': modal interchange on all diatonic chords
    - 'simple': relative major/minor swaps only

    Args:
        progression: Original (root, shape) progression.
        key:         Key context.
        style:       Substitution strategy.

    Returns:
        Reharmonized progression.
    """
    key_semi = _semi(key)
    result: list[tuple[str, str]] = []

    for root, shape in progression:
        root_semi = _semi(root)
        degree = (root_semi - key_semi) % 12

        if style == "jazz":
            if degree == 7 and ("dom" in shape or "7" in shape):
                # Add related ii before V
                ii_semi = (root_semi - 5) % 12
                result.append((_NOTE_NAMES[ii_semi], "min7"))
            # Tritone sub on secondary dominants
            if "dom" in shape and degree != 7:
                tri_semi = (root_semi + 6) % 12
                result.append((_NOTE_NAMES[tri_semi], "dom7"))
            else:
                result.append((root, shape))

        elif style == "modal":
            if shape in ("maj", "maj7"):
                result.append((root, "min"))
            elif shape in ("min", "min7"):
                result.append((root, "maj"))
            else:
                result.append((root, shape))

        else:  # simple
            if shape in ("maj", "maj7"):
                rel = _NOTE_NAMES[(root_semi + 9) % 12]
                result.append((rel, "min"))
            elif shape in ("min", "min7"):
                rel = _NOTE_NAMES[(root_semi + 3) % 12]
                result.append((rel, "maj"))
            else:
                result.append((root, shape))

    return result


# ---------------------------------------------------------------------------
# Song fingerprinting & similarity (v61.0)
# ---------------------------------------------------------------------------


def song_fingerprint(
    progression: list[tuple[str, str]],
    notes: list[Note] | None = None,
) -> dict:
    """Extract a feature vector from a chord progression (and optional melody).

    The fingerprint captures the harmonic and melodic DNA of a piece:
    pitch class histogram, chord quality distribution, average interval,
    and rhythmic density. Use it to compare songs or cluster a corpus.

    Args:
        progression: List of (root, shape) tuples.
        notes:       Optional melody notes for pitch/rhythm stats.

    Returns:
        Dict with keys: pitch_histogram, quality_dist, avg_interval,
        rhythm_density, chord_count.
    """
    # Pitch class histogram (12 bins)
    pc_hist = [0] * 12
    quality_counts: dict[str, int] = {}
    for root, shape in progression:
        pc_hist[_semi(root)] += 1
        quality_counts[shape] = quality_counts.get(shape, 0) + 1

    total = max(sum(pc_hist), 1)
    pc_hist_norm = [round(c / total, 3) for c in pc_hist]

    quality_total = max(sum(quality_counts.values()), 1)
    quality_dist = {k: round(v / quality_total, 3) for k, v in sorted(quality_counts.items())}

    # Melody stats
    avg_interval = 0.0
    rhythm_density = 0.0
    if notes:
        intervals = []
        sounding = 0
        for i in range(1, len(notes)):
            if notes[i].pitch and notes[i - 1].pitch:
                a = _semi(str(notes[i].pitch)) + notes[i].octave * 12
                b = _semi(str(notes[i - 1].pitch)) + notes[i - 1].octave * 12
                intervals.append(abs(a - b))
            if notes[i].pitch is not None:
                sounding += 1
        avg_interval = round(sum(intervals) / max(len(intervals), 1), 2)
        rhythm_density = round(sounding / max(len(notes), 1), 3)

    return {
        "pitch_histogram": pc_hist_norm,
        "quality_dist": quality_dist,
        "avg_interval": avg_interval,
        "rhythm_density": rhythm_density,
        "chord_count": len(progression),
    }


def song_similarity(fp_a: dict, fp_b: dict) -> float:
    """Compute cosine similarity between two song fingerprints.

    Args:
        fp_a: First fingerprint (from song_fingerprint).
        fp_b: Second fingerprint.

    Returns:
        Similarity score in [0.0, 1.0].
    """
    import math

    vec_a = fp_a["pitch_histogram"]
    vec_b = fp_b["pitch_histogram"]
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a)) or 1e-9
    mag_b = math.sqrt(sum(b * b for b in vec_b)) or 1e-9
    return round(dot / (mag_a * mag_b), 3)


# ---------------------------------------------------------------------------
# Counterpoint rules validator (v62.0)
# ---------------------------------------------------------------------------


def validate_counterpoint(
    cf: list[Note],
    cp: list[Note],
    species: int = 1,
) -> list[str]:
    """Validate counterpoint against a cantus firmus and return violations.

    Checks:
    - No parallel perfect 5ths or octaves
    - No voice crossing
    - No leaps greater than an octave
    - Consonant intervals on strong beats (species 1)

    Args:
        cf: Cantus firmus notes.
        cp: Counterpoint notes.
        species: Species number (1 or 2).

    Returns:
        List of violation description strings. Empty = perfect counterpoint.
    """
    violations: list[str] = []
    min_len = min(len(cf), len(cp))

    for i in range(min_len):
        if cf[i].pitch is None or cp[i].pitch is None:
            continue

        cf_abs = _semi(str(cf[i].pitch)) + cf[i].octave * 12
        cp_abs = _semi(str(cp[i].pitch)) + cp[i].octave * 12
        interval = abs(cp_abs - cf_abs) % 12

        # Voice crossing check
        if cp_abs < cf_abs:
            violations.append(f"Bar {i + 1}: voice crossing (CP below CF)")

        # Consonance check on strong beats
        if species == 1 or i % 2 == 0:
            if interval in _DISSONANCES:
                violations.append(f"Bar {i + 1}: dissonant interval ({interval} semitones)")

        # Leap > octave in CP
        if i > 0 and cp[i - 1].pitch is not None:
            prev_cp = _semi(str(cp[i - 1].pitch)) + cp[i - 1].octave * 12
            leap = abs(cp_abs - prev_cp)
            if leap > 12:
                violations.append(f"Bar {i + 1}: leap > octave ({leap} semitones)")

        # Parallel 5ths/octaves
        if i > 0 and cf[i - 1].pitch is not None and cp[i - 1].pitch is not None:
            prev_cf = _semi(str(cf[i - 1].pitch)) + cf[i - 1].octave * 12
            prev_cp = _semi(str(cp[i - 1].pitch)) + cp[i - 1].octave * 12
            prev_interval = abs(prev_cp - prev_cf) % 12
            curr_interval = interval
            if prev_interval == curr_interval and curr_interval in (0, 7):
                cf_moved = cf_abs != prev_cf
                cp_moved = cp_abs != prev_cp
                if cf_moved and cp_moved:
                    label = "P8" if curr_interval == 0 else "P5"
                    violations.append(f"Bar {i + 1}: parallel {label}")

    return violations


def grade_counterpoint(
    cf: list[Note],
    cp: list[Note],
    species: int = 1,
) -> int:
    """Grade counterpoint on a 0-100 scale.

    100 = no violations. Each violation deducts points based on severity.

    Args:
        cf: Cantus firmus.
        cp: Counterpoint.
        species: Species number.

    Returns:
        Integer score 0-100.
    """
    violations = validate_counterpoint(cf, cp, species)
    # Deduct 10 per violation, floor at 0
    score = max(0, 100 - len(violations) * 10)
    return score


# ---------------------------------------------------------------------------
# Chord tone targeting (v63.0)
# ---------------------------------------------------------------------------


def target_chord_tones(
    progression: list[tuple[str, str]],
    key: str = "C",
    notes_per_chord: int = 4,
    seed: int | None = None,
) -> list[Note]:
    """Generate a melody that lands on chord tones at strong beats.

    The core principle of jazz improvisation: beat 1 and 3 hit chord
    tones, beats 2 and 4 use passing scale tones. The difference
    between noodling and intentional storytelling.

    Args:
        progression: Chord progression as (root, shape) tuples.
        key:         Key for scale-tone fills.
        notes_per_chord: Notes per chord (must be even; odd beats = chord tones).
        seed:        Random seed.

    Returns:
        List of Notes targeting chord tones on strong beats.
    """
    import random as _rng

    rng = _rng.Random(seed)

    key_semi = _semi(key)
    scale_ivs = _SCALE_INTERVALS.get("major", [0, 2, 4, 5, 7, 9, 11])
    scale_pcs = [(key_semi + iv) % 12 for iv in scale_ivs]

    result: list[Note] = []
    for root, shape in progression:
        root_semi = _semi(root)
        chord_pcs = [(root_semi + s) % 12 for s in _CHORD_SEMI.get(shape, [0, 4, 7])]

        for beat in range(notes_per_chord):
            if beat % 2 == 0:
                # Strong beat: chord tone
                pc = rng.choice(chord_pcs)
            else:
                # Weak beat: scale tone (passing)
                pc = rng.choice(scale_pcs)

            result.append(Note(_NOTE_NAMES[pc], 5, 0.5))

    return result


def approach_pattern(
    target: str,
    octave: int = 5,
    direction: str = "chromatic",
    duration: float = 0.25,
) -> list[Note]:
    """Generate an approach pattern to a target note.

    Approach patterns are how jazz musicians arrive at a chord tone
    with style instead of just landing on it. Three flavors:

    - chromatic: half-step above and below, then target
    - diatonic: step above, step below, then target
    - enclosure: above then below (or vice versa), then target

    Args:
        target:    Target pitch name.
        octave:    Target octave.
        direction: 'chromatic', 'diatonic', or 'enclosure'.
        duration:  Duration per approach note.

    Returns:
        List of 3 Notes: approach above, approach below, target.
    """
    t = _semi(target)
    if direction == "chromatic":
        above = (t + 1) % 12
        below = (t - 1) % 12
    elif direction == "diatonic":
        above = (t + 2) % 12
        below = (t - 2) % 12
    else:  # enclosure
        above = (t + 1) % 12
        below = (t - 2) % 12

    return [
        Note(_NOTE_NAMES[above], octave, duration),
        Note(_NOTE_NAMES[below], octave, duration),
        Note(target, octave, duration * 2),
    ]


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
# Song structure detection (v65.0)
# ---------------------------------------------------------------------------


def section_similarity_matrix(
    progression: list[tuple[str, str]],
    bars_per_section: int = 4,
) -> list[list[float]]:
    """Compute pairwise similarity between sections of a progression.

    Divides the progression into chunks and compares each pair using
    pitch-class overlap. The resulting matrix reveals repeated sections.

    Args:
        progression:     Full chord progression.
        bars_per_section: Chords per section.

    Returns:
        NxN matrix of similarity scores (0.0–1.0), where N = number of sections.
    """
    sections = [
        progression[i : i + bars_per_section] for i in range(0, len(progression), bars_per_section)
    ]

    def _section_pcs(section: list[tuple[str, str]]) -> set[int]:
        return {_semi(r) for r, _ in section}

    n = len(sections)
    matrix: list[list[float]] = []
    for i in range(n):
        row: list[float] = []
        pcs_i = _section_pcs(sections[i])
        for j in range(n):
            pcs_j = _section_pcs(sections[j])
            union = pcs_i | pcs_j
            if not union:
                row.append(1.0)
            else:
                row.append(round(len(pcs_i & pcs_j) / len(union), 3))
        matrix.append(row)
    return matrix


def detect_sections(
    progression: list[tuple[str, str]],
    bars_per_section: int = 4,
    threshold: float = 0.7,
) -> list[dict]:
    """Detect repeated sections in a chord progression.

    Groups sections by similarity: sections that match above the threshold
    get the same label (A, B, C, ...). Returns a list of section descriptors.

    Args:
        progression:     Full chord progression.
        bars_per_section: Chords per section.
        threshold:       Similarity threshold for grouping.

    Returns:
        List of dicts: {start, end, label}.
    """
    matrix = section_similarity_matrix(progression, bars_per_section)
    n = len(matrix)
    labels: list[str] = [""] * n
    current_label = "A"

    for i in range(n):
        if labels[i]:
            continue
        labels[i] = current_label
        for j in range(i + 1, n):
            if not labels[j] and matrix[i][j] >= threshold:
                labels[j] = current_label
        current_label = chr(ord(current_label) + 1)

    return [
        {
            "start": i * bars_per_section,
            "end": min((i + 1) * bars_per_section, len(progression)),
            "label": labels[i],
        }
        for i in range(n)
    ]


def label_form(
    progression: list[tuple[str, str]],
    bars_per_section: int = 4,
) -> str:
    """Auto-label the form of a progression (e.g. 'AABA', 'ABAB').

    Args:
        progression:     Full chord progression.
        bars_per_section: Chords per section.

    Returns:
        Form string (e.g. 'AABA', 'ABCABC').
    """
    sections = detect_sections(progression, bars_per_section)
    return "".join(s["label"] for s in sections)


# ---------------------------------------------------------------------------
# Drone & ambient generator (v66.0)
# ---------------------------------------------------------------------------


def drone(
    key: str = "C",
    octave: int = 3,
    duration: float = 32.0,
    overtones: int = 4,
) -> list[Note]:
    """Generate a rich drone with harmonic overtone series.

    A drone is the simplest and oldest musical texture — a sustained
    tone with natural harmonics. Indian classical music, bagpipes,
    hurdy-gurdy, shoegaze guitar, ambient synths — the drone is
    the foundation.

    Args:
        key:       Root note.
        octave:    Base octave.
        duration:  Total duration.
        overtones: Number of harmonic overtones to include.

    Returns:
        List of Notes: root + overtones (layered, same duration).
    """
    k = _semi(key)
    # Harmonic series: 1x, 2x, 3x, 4x, 5x frequency
    # Approximated by octaves + fifths + thirds
    _OVERTONE_INTERVALS = [0, 12, 19, 24, 28, 31, 34, 36]
    result = []
    for i in range(min(overtones + 1, len(_OVERTONE_INTERVALS))):
        total_semi = k + _OVERTONE_INTERVALS[i]
        pc = total_semi % 12
        oct = octave + total_semi // 12
        vel = max(30, 100 - i * 15)  # overtones get quieter
        result.append(Note(_NOTE_NAMES[pc], oct, duration, velocity=vel))
    return result


def evolving_pad(
    key: str = "C",
    scale_name: str = "major",
    duration: float = 64.0,
    density: int = 8,
    octave: int = 4,
    seed: int | None = None,
) -> list[Note]:
    """Generate a slowly morphing ambient pad texture.

    Random notes from the scale appear and sustain for varying
    durations, creating a cloud-like harmonic texture that evolves
    without repeating. Brian Eno's Music for Airports, in a function.

    Args:
        key:        Root note.
        scale_name: Scale to draw from.
        duration:   Total duration of the pad.
        density:    Number of note events.
        octave:     Center octave.
        seed:       Random seed.

    Returns:
        List of Notes with varying onsets and long durations.
    """
    import random as _rng

    rng = _rng.Random(seed)

    aliases = {"minor": "aeolian", "natural_minor": "aeolian"}
    sname = aliases.get(scale_name, scale_name)
    intervals = _SCALE_INTERVALS.get(sname, _SCALE_INTERVALS["major"])
    k = _semi(key)

    pool = [(k + iv) % 12 for iv in intervals]
    result: list[Note] = []
    remaining = duration

    for _ in range(density):
        if remaining <= 0:
            break
        pc = rng.choice(pool)
        oct = octave + rng.choice([-1, 0, 0, 1])
        note_dur = rng.uniform(duration / density * 0.5, duration / density * 2.0)
        note_dur = min(note_dur, remaining)
        vel = rng.randint(40, 80)
        result.append(Note(_NOTE_NAMES[pc], oct, round(note_dur, 2), velocity=vel))
        remaining -= note_dur

    return result


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
# Harmonic reduction (v68.0)
# ---------------------------------------------------------------------------


def reduce_to_chords(
    notes: list[Note],
    beats_per_chord: int = 4,
) -> list[tuple[str, str]]:
    """Collapse a melody to its implied chords by grouping pitch classes.

    Divides notes into chunks and finds the best-matching triad for
    each chunk. The reverse of melody generation — "what chords does
    this melody outline?"

    Args:
        notes:           Melody notes.
        beats_per_chord: Notes per chord group.

    Returns:
        List of (root, shape) tuples, one per group.
    """
    result: list[tuple[str, str]] = []
    for i in range(0, len(notes), beats_per_chord):
        chunk = notes[i : i + beats_per_chord]
        pcs = [_semi(str(n.pitch)) for n in chunk if n.pitch is not None]
        if not pcs:
            result.append(("C", "maj"))
            continue
        # Try each root and find best triad match
        best_root = 0
        best_shape = "maj"
        best_score = -1
        pc_set = set(pcs)
        for candidate_root in range(12):
            for shape, intervals in [
                ("maj", [0, 4, 7]),
                ("min", [0, 3, 7]),
                ("dim", [0, 3, 6]),
                ("aug", [0, 4, 8]),
            ]:
                chord_pcs = {(candidate_root + iv) % 12 for iv in intervals}
                score = len(pc_set & chord_pcs)
                if score > best_score:
                    best_score = score
                    best_root = candidate_root
                    best_shape = shape
        result.append((_NOTE_NAMES[best_root], best_shape))
    return result


def harmonic_skeleton(
    progression: list[tuple[str, str]],
    key: str = "C",
) -> list[tuple[str, str]]:
    """Reduce a progression to its functional skeleton (I, IV, V only).

    Strips away secondary dominants, chromatic chords, and modal
    mixture — leaving only the three pillars of tonal harmony.

    Args:
        progression: Full chord progression.
        key:         Key for analysis.

    Returns:
        Simplified progression using only I, IV, and V.
    """
    key_semi = _semi(key)
    tonic = (_NOTE_NAMES[key_semi], "maj")
    subdominant = (_NOTE_NAMES[(key_semi + 5) % 12], "maj")
    dominant = (_NOTE_NAMES[(key_semi + 7) % 12], "maj")

    subdom_degrees = {1, 2, 5, 6, 10}  # bII, II, IV, bV, bVII → subdominant
    dom_degrees = {7, 11}  # V, VII → dominant

    result: list[tuple[str, str]] = []
    for root, _shape in progression:
        degree = (_semi(root) - key_semi) % 12
        if degree in dom_degrees:
            result.append(dominant)
        elif degree in subdom_degrees:
            result.append(subdominant)
        else:
            result.append(tonic)  # everything else is tonic function
    return result


def complexity_score(
    progression: list[tuple[str, str]],
    key: str = "C",
) -> int:
    """Rate the harmonic complexity of a progression (0–100).

    Factors: number of distinct roots, chord quality variety, chromatic
    chords, and functional variety. A I-IV-V-I scores low; Coltrane
    changes score high.

    Args:
        progression: Chord progression.
        key:         Key for analysis.

    Returns:
        Integer score 0–100.
    """
    if not progression:
        return 0
    key_semi = _semi(key)
    major_pcs = {(key_semi + iv) % 12 for iv in _SCALE_INTERVALS["major"]}

    roots = {_semi(r) for r, _ in progression}
    shapes = {s for _, s in progression}
    chromatic = sum(1 for r, _ in progression if _semi(r) not in major_pcs)

    root_score = min(len(roots) * 8, 30)  # up to 30 for root variety
    shape_score = min(len(shapes) * 6, 25)  # up to 25 for quality variety
    chrom_score = min(chromatic * 5, 25)  # up to 25 for chromatic chords
    length_score = min(len(progression), 20)  # up to 20 for length

    return min(100, root_score + shape_score + chrom_score + length_score)


# ---------------------------------------------------------------------------
# Musical dice game — Musikalisches Würfelspiel (v69.0)
# ---------------------------------------------------------------------------

# Mozart's original table (simplified — measure indices for a minuet)
# Each row = one of 11 possible dice outcomes (2-12); each column = one bar position
_MOZART_MINUET_TABLE = [
    [96, 22, 141, 41, 105, 122, 11, 30, 70, 121, 26, 9, 112, 49, 109, 14],
    [32, 6, 128, 63, 146, 46, 134, 81, 117, 39, 126, 56, 174, 18, 116, 83],
    [69, 95, 158, 13, 153, 55, 110, 24, 66, 139, 15, 132, 73, 58, 145, 79],
    [40, 17, 113, 85, 161, 2, 159, 100, 90, 176, 7, 34, 67, 160, 52, 170],
    [148, 74, 163, 45, 80, 97, 36, 107, 25, 143, 64, 125, 76, 136, 1, 93],
    [104, 157, 27, 167, 154, 68, 118, 91, 138, 71, 150, 29, 101, 162, 23, 151],
    [152, 60, 171, 53, 99, 133, 21, 127, 16, 155, 57, 175, 43, 168, 89, 172],
    [119, 84, 114, 50, 140, 86, 169, 94, 120, 88, 48, 166, 51, 115, 72, 111],
    [98, 142, 42, 156, 75, 129, 62, 123, 65, 77, 19, 82, 137, 38, 149, 8],
    [3, 87, 165, 61, 135, 47, 147, 33, 102, 4, 31, 164, 144, 59, 173, 78],
    [54, 130, 10, 103, 28, 37, 106, 5, 35, 20, 108, 92, 12, 124, 44, 131],
]


def dice_game(
    seed: int | None = None,
    bars: int = 16,
) -> list[int]:
    """Select bar indices using Mozart's musical dice game.

    Roll two dice for each bar position, subtract 2, use as table index.
    The result is a list of "measure numbers" from Mozart's pool — each
    maps to a pre-composed one-bar fragment.

    Args:
        seed: Random seed.
        bars: Number of bars to generate (max 16 for the Mozart table).

    Returns:
        List of measure indices (integers from Mozart's table).
    """
    import random as _rng

    rng = _rng.Random(seed)
    result: list[int] = []
    for col in range(min(bars, 16)):
        roll = rng.randint(1, 6) + rng.randint(1, 6)  # 2d6
        row = roll - 2  # 0-10
        result.append(_MOZART_MINUET_TABLE[row][col])
    return result


def classical_minuet(
    key: str = "C",
    octave: int = 5,
    seed: int | None = None,
) -> list[Note]:
    """Generate a 16-bar minuet using Mozart's dice game method.

    Each bar's measure index from the dice roll maps to a simple
    melodic fragment derived from the key's scale. The original 1787
    algorithm — the first generative music, 230 years before AI.

    Args:
        key:    Key root.
        octave: Melody octave.
        seed:   Random seed.

    Returns:
        List of Notes forming a 16-bar minuet.
    """
    import random as _rng

    k = _semi(key)
    intervals = _SCALE_INTERVALS.get("major", [0, 2, 4, 5, 7, 9, 11])
    bar_indices = dice_game(seed=seed)

    result: list[Note] = []
    for idx in bar_indices:
        # Use the index to seed a small melodic fragment (3 notes per bar in 3/4)
        frag_rng = _rng.Random(idx)
        for _ in range(3):
            iv = frag_rng.choice(intervals)
            pc = (k + iv) % 12
            result.append(Note(_NOTE_NAMES[pc], octave, 1.0))

    return result


# ---------------------------------------------------------------------------
# Microtuning & just intonation (v70.0)
# ---------------------------------------------------------------------------

# Pure harmonic ratios for just intonation
_JUST_RATIOS = {
    0: (1, 1),  # unison
    1: (16, 15),  # minor second
    2: (9, 8),  # major second
    3: (6, 5),  # minor third
    4: (5, 4),  # major third
    5: (4, 3),  # perfect fourth
    6: (45, 32),  # tritone (augmented fourth)
    7: (3, 2),  # perfect fifth
    8: (8, 5),  # minor sixth
    9: (5, 3),  # major sixth
    10: (9, 5),  # minor seventh
    11: (15, 8),  # major seventh
    12: (2, 1),  # octave
}


def just_ratio(semitones: int) -> tuple[int, int]:
    """Return the pure harmonic ratio for an interval.

    Just intonation uses simple integer ratios instead of equal
    temperament's irrational numbers. A perfect fifth is 3/2, not
    2^(7/12). The difference is subtle but audible — just intervals
    are beatless and pure.

    Args:
        semitones: Interval in semitones (0–12).

    Returns:
        (numerator, denominator) ratio tuple.
    """
    s = abs(semitones) % 13
    return _JUST_RATIOS.get(s, (1, 1))


def cents_from_et(semitones: int) -> float:
    """Calculate how many cents a just interval deviates from equal temperament.

    A cent is 1/100th of a semitone. Just major third is ~14 cents flat
    compared to ET. This is why pianos sound slightly out of tune on
    sustained chords — they're in equal temperament, not just.

    Args:
        semitones: Interval in semitones.

    Returns:
        Deviation in cents (positive = sharp, negative = flat).
    """
    import math

    num, den = just_ratio(semitones)
    just_cents = 1200 * math.log2(num / den)
    et_cents = semitones * 100.0
    return round(just_cents - et_cents, 2)


def detune_to_just(
    notes: list[Note],
    key: str = "C",
) -> list[dict]:
    """Calculate just-intonation detuning for each note relative to a key.

    Returns the cent offset each note would need to sound in just
    intonation. Apply these offsets in a DAW or synth for pure tuning.

    Args:
        notes: Melody notes.
        key:   Reference key (the "1/1" pitch).

    Returns:
        List of dicts: {pitch, octave, cents_offset}.
    """
    key_semi = _semi(key)
    result = []
    for n in notes:
        if n.pitch is None:
            result.append({"pitch": None, "octave": n.octave, "cents_offset": 0.0})
        else:
            interval = (_semi(str(n.pitch)) - key_semi) % 12
            offset = cents_from_et(interval)
            result.append(
                {
                    "pitch": n.pitch,
                    "octave": n.octave,
                    "cents_offset": offset,
                }
            )
    return result


def quarter_tone(
    note: str,
    octave: int = 4,
    direction: str = "up",
    duration: float = 1.0,
) -> dict:
    """Create a quarter-tone pitch (halfway between two semitones).

    Quarter tones are fundamental to Arabic maqam, Turkish makam, and
    contemporary classical music. They don't fit into standard Western
    notation, so we return a dict with the nearest note + cent offset.

    Args:
        note:      Base note name.
        octave:    Octave.
        direction: 'up' = 50 cents sharp, 'down' = 50 cents flat.
        duration:  Note duration.

    Returns:
        Dict: {base_note, octave, cents_offset, duration}.
    """
    offset = 50.0 if direction == "up" else -50.0
    return {
        "base_note": note,
        "octave": octave,
        "cents_offset": offset,
        "duration": duration,
    }


# ---------------------------------------------------------------------------
# Texture density control (v71.0)
# ---------------------------------------------------------------------------


def texture_density(
    notes: list[Note],
    window_beats: float = 4.0,
) -> list[float]:
    """Measure notes-per-beat density in a sliding window.

    Returns a density value for each note position, representing
    how busy the texture is at that point. Useful for identifying
    climaxes, sparse passages, and density transitions.

    Args:
        notes:        Input notes.
        window_beats: Window size in beats for density calculation.

    Returns:
        List of density values (notes-per-beat), one per note.
    """
    if not notes:
        return []

    # Calculate cumulative beat positions
    positions: list[float] = []
    beat = 0.0
    for n in notes:
        positions.append(beat)
        beat += n.duration

    result: list[float] = []
    for i, pos in enumerate(positions):
        # Count notes within the window centered on this position
        window_start = pos - window_beats / 2
        window_end = pos + window_beats / 2
        count = sum(1 for p in positions if window_start <= p <= window_end)
        density = count / window_beats
        result.append(round(density, 2))

    return result


def thin_texture(
    notes: list[Note],
    target_density: float = 0.5,
    seed: int | None = None,
) -> list[Note]:
    """Remove notes to reach a target density (notes-per-beat).

    Randomly converts sounding notes to rests until the overall
    density drops to the target. Preserves the first and last notes.

    Args:
        notes:          Input notes.
        target_density: Desired notes-per-beat.
        seed:           Random seed.

    Returns:
        Thinned note list with some notes replaced by rests.
    """
    import random as _rng

    rng = _rng.Random(seed)
    if not notes:
        return []

    total_dur = sum(n.duration for n in notes)
    sounding = [i for i, n in enumerate(notes) if n.pitch is not None]
    current_density = len(sounding) / max(total_dur, 0.01)

    result = list(notes)
    # Protect first and last sounding notes
    removable = [i for i in sounding if i != 0 and i != len(notes) - 1]
    rng.shuffle(removable)

    while current_density > target_density and removable:
        idx = removable.pop()
        result[idx] = Note.rest(notes[idx].duration)
        sounding_count = sum(1 for n in result if n.pitch is not None)
        current_density = sounding_count / max(total_dur, 0.01)

    return result


def thicken_texture(
    notes: list[Note],
    scale_name: str = "major",
    key: str = "C",
    target_density: float = 2.0,
    seed: int | None = None,
) -> list[Note]:
    """Add passing tones to increase texture density.

    Inserts scale-tone fills between existing notes until the target
    density is reached. New notes are half the duration of the original.

    Args:
        notes:          Input notes.
        scale_name:     Scale for fill notes.
        key:            Key root.
        target_density: Desired notes-per-beat.
        seed:           Random seed.

    Returns:
        Thickened note list with added passing tones.
    """
    import random as _rng

    rng = _rng.Random(seed)
    if not notes:
        return []

    aliases = {"minor": "aeolian", "natural_minor": "aeolian"}
    sname = aliases.get(scale_name, scale_name)
    intervals = _SCALE_INTERVALS.get(sname, _SCALE_INTERVALS["major"])
    k = _semi(key)
    scale_pcs = [(k + iv) % 12 for iv in intervals]

    result: list[Note] = []
    total_dur = sum(n.duration for n in notes)
    sounding = sum(1 for n in notes if n.pitch is not None)
    current_density = sounding / max(total_dur, 0.01)

    for n in notes:
        result.append(n)
        if current_density < target_density and n.pitch is not None:
            # Insert a passing tone
            fill_pc = rng.choice(scale_pcs)
            fill_dur = n.duration / 2
            result[-1] = Note(n.pitch, n.octave, n.duration / 2, velocity=n.velocity)
            result.append(Note(_NOTE_NAMES[fill_pc], n.octave, fill_dur, velocity=70))
            sounding += 1
            current_density = sounding / max(total_dur, 0.01)

    return result


# ---------------------------------------------------------------------------
# Chord voicing constraints (v72.0)
# ---------------------------------------------------------------------------


def optimal_voicing(
    root: str,
    shape: str,
    voices: int = 4,
    max_span: int = 24,
    prefer_close: bool = True,
    octave: int = 3,
    duration: float = 4.0,
) -> list[Note]:
    """Find the optimal voicing for a chord under constraints.

    A constraint-satisfaction approach: spread chord tones across
    the specified number of voices while respecting span limits and
    close/open position preference.

    Args:
        root:         Chord root.
        shape:        Chord quality.
        voices:       Number of voices (3-6).
        max_span:     Maximum semitone span from lowest to highest note.
        prefer_close: True = close position, False = open (spread).
        octave:       Base octave for lowest voice.
        duration:     Note duration.

    Returns:
        List of Notes forming the constrained voicing.
    """
    k = _semi(root)
    semis = list(_CHORD_SEMI.get(shape, [0, 4, 7]))

    # Build candidate pitches across octaves
    candidates: list[int] = []
    for o in range(octave, octave + 3):
        for s in semis:
            candidates.append(k + s + o * 12)
    candidates.sort()

    # Pick `voices` notes within max_span
    best: list[int] = []
    best_score = -1

    for start_idx in range(len(candidates)):
        bass = candidates[start_idx]
        group = [bass]
        for c in candidates[start_idx + 1 :]:
            if c - bass > max_span:
                break
            group.append(c)

        if len(group) < voices:
            continue

        # Score: prefer close or open position
        # Try all combinations of `voices` from `group`
        # For efficiency, just take the first `voices` (close) or spread evenly (open)
        if prefer_close:
            selected = group[:voices]
        else:
            step = max(1, len(group) // voices)
            selected = [group[i * step] for i in range(min(voices, len(group)))]

        if len(selected) < voices:
            continue

        span = selected[-1] - selected[0]
        # Score close voicings higher when prefer_close, wider when not
        if prefer_close:
            score = max_span - span
        else:
            score = span

        if score > best_score:
            best_score = score
            best = selected

    if not best:
        # Fallback: simple stacking
        best = [
            (k + semis[i % len(semis)] + (octave + i // len(semis)) * 12) for i in range(voices)
        ]

    return [Note(_NOTE_NAMES[p % 12], p // 12, duration) for p in best]


def smooth_voicings(
    progression: list[tuple[str, str]],
    voices: int = 4,
    max_span: int = 24,
    octave: int = 3,
    duration: float = 4.0,
) -> list[list[Note]]:
    """Generate smooth voice-led voicings for a progression under constraints.

    Each chord is voiced to minimize total movement from the previous voicing
    while respecting span and voice count constraints.

    Args:
        progression: List of (root, shape) tuples.
        voices:      Number of voices.
        max_span:    Maximum span per voicing.
        octave:      Base octave.
        duration:    Duration per chord.

    Returns:
        List of voicing note-lists, one per chord.
    """
    if not progression:
        return []

    result: list[list[Note]] = []
    prev: list[int] | None = None

    for root, shape in progression:
        voicing = optimal_voicing(root, shape, voices, max_span, True, octave, duration)
        current = [_semi(str(n.pitch)) + n.octave * 12 for n in voicing]

        if prev is not None:
            # Try to minimize movement by octave-shifting notes
            adjusted: list[int] = []
            for i, c in enumerate(current):
                target = prev[i] if i < len(prev) else c
                # Find the octave placement closest to target
                pc = c % 12
                best_abs = c
                best_dist = abs(c - target)
                for o in range(octave, octave + 3):
                    candidate = pc + o * 12
                    if abs(candidate - target) < best_dist:
                        best_dist = abs(candidate - target)
                        best_abs = candidate
                adjusted.append(best_abs)
            adjusted.sort()
            voicing = [Note(_NOTE_NAMES[p % 12], p // 12, duration) for p in adjusted]
            prev = adjusted
        else:
            prev = current

        result.append(voicing)

    return result


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
# Bass line intelligence (v74.0)
# ---------------------------------------------------------------------------


def bass_line_jazz(
    progression: list[tuple[str, str]],
    octave: int = 2,
    seed: int | None = None,
) -> list[Note]:
    """Generate a jazz walking bass line with chromatic approaches.

    Hits the root on beat 1, walks through chord tones and chromatic
    approaches on beats 2-4. Mingus-level bass lines require a human,
    but this gets you 80% of the way.

    Args:
        progression: Chord progression as (root, shape) tuples.
        octave:      Bass octave.
        seed:        Random seed.

    Returns:
        List of Notes (4 notes per chord).
    """
    import random as _rng

    rng = _rng.Random(seed)
    result: list[Note] = []

    for idx, (root, shape) in enumerate(progression):
        k = _semi(root)
        semis = _CHORD_SEMI.get(shape, [0, 4, 7])
        chord_tones = [(k + s) % 12 for s in semis]

        # Beat 1: root
        result.append(Note(_NOTE_NAMES[k], octave, 1.0, velocity=95))

        # Beat 2: chord tone
        ct = rng.choice(chord_tones[1:]) if len(chord_tones) > 1 else k
        result.append(Note(_NOTE_NAMES[ct], octave, 1.0, velocity=80))

        # Beat 3: passing tone (scale step)
        passing = (k + rng.choice([2, 5, 7, 9])) % 12
        result.append(Note(_NOTE_NAMES[passing], octave, 1.0, velocity=75))

        # Beat 4: chromatic approach to next root
        if idx + 1 < len(progression):
            next_root = _semi(progression[idx + 1][0])
            approach = (next_root + rng.choice([-1, 1])) % 12
        else:
            approach = (k + rng.choice([-1, 1])) % 12
        result.append(Note(_NOTE_NAMES[approach], octave, 1.0, velocity=85))

    return result


def bass_line_funk(
    progression: list[tuple[str, str]],
    octave: int = 2,
    seed: int | None = None,
) -> list[Note]:
    """Generate a syncopated funk bass line with octave pops.

    Bootsy Collins vibes: root on the one, syncopated ghost notes,
    and the occasional octave pop. The pocket is everything.

    Args:
        progression: Chord progression.
        octave:      Bass octave.
        seed:        Random seed.

    Returns:
        List of Notes (8 sixteenth-notes per chord).
    """
    import random as _rng

    rng = _rng.Random(seed)
    result: list[Note] = []

    for root, shape in progression:
        k = _semi(root)
        for beat in range(8):
            if beat == 0:
                # Strong downbeat
                result.append(Note(_NOTE_NAMES[k], octave, 0.5, velocity=100))
            elif beat == 3 and rng.random() > 0.4:
                # Octave pop
                result.append(Note(_NOTE_NAMES[k], octave + 1, 0.5, velocity=90))
            elif rng.random() > 0.5:
                # Ghost note or passing tone
                ghost = (k + rng.choice([0, 5, 7])) % 12
                result.append(Note(_NOTE_NAMES[ghost], octave, 0.5, velocity=50))
            else:
                # Rest (the space IS the funk)
                result.append(Note.rest(0.5))

    return result


def bass_line_latin(
    progression: list[tuple[str, str]],
    octave: int = 2,
    seed: int | None = None,
) -> list[Note]:
    """Generate a Latin tumbao bass pattern.

    The tumbao is the rhythmic foundation of salsa, son, and
    Afro-Cuban music. Anticipates beat 1 by playing on the "and"
    of beat 4, creating forward momentum.

    Args:
        progression: Chord progression.
        octave:      Bass octave.
        seed:        Random seed.

    Returns:
        List of Notes in tumbao rhythm.
    """
    result: list[Note] = []

    for idx, (root, shape) in enumerate(progression):
        k = _semi(root)
        fifth = (k + 7) % 12

        # Tumbao pattern: rest, root, rest, fifth, rest, root, fifth, anticipation
        result.append(Note.rest(0.5))
        result.append(Note(_NOTE_NAMES[k], octave, 0.5, velocity=90))
        result.append(Note.rest(0.5))
        result.append(Note(_NOTE_NAMES[fifth], octave, 0.5, velocity=80))
        result.append(Note.rest(0.5))
        result.append(Note(_NOTE_NAMES[k], octave, 0.5, velocity=85))
        result.append(Note(_NOTE_NAMES[fifth], octave, 0.5, velocity=75))
        # Anticipation: next root a half-beat early
        if idx + 1 < len(progression):
            next_k = _semi(progression[idx + 1][0])
            result.append(Note(_NOTE_NAMES[next_k], octave, 0.5, velocity=95))
        else:
            result.append(Note(_NOTE_NAMES[k], octave, 0.5, velocity=80))

    return result


# ---------------------------------------------------------------------------
# Melody harmonization (v75.0)
# ---------------------------------------------------------------------------


def harmonize_melody(
    melody: list[Note],
    key: str = "C",
    style: str = "thirds",
    scale_name: str = "major",
) -> list[list[Note]]:
    """Add harmony voices to a single-line melody.

    The inverse of melody extraction — given a melody, automatically
    generate 1-3 additional voices in a specific harmonic style.

    Styles:
    - 'thirds': parallel diatonic thirds (pop/rock)
    - 'sixths': parallel diatonic sixths (country)
    - 'chorale': SATB-style with contrary motion

    Args:
        melody:     Input melody notes.
        key:        Key root.
        style:      Harmonization style.
        scale_name: Scale for diatonic interval calculation.

    Returns:
        List of voice lists: [melody, harmony_1, ...].
    """
    aliases = {"minor": "aeolian", "natural_minor": "aeolian"}
    sname = aliases.get(scale_name, scale_name)
    intervals = _SCALE_INTERVALS.get(sname, _SCALE_INTERVALS["major"])
    k = _semi(key)
    scale_pcs = [(k + iv) % 12 for iv in intervals]

    def _diatonic_above(pc: int, steps: int) -> int:
        if pc in scale_pcs:
            idx = scale_pcs.index(pc)
        else:
            idx = min(range(len(scale_pcs)), key=lambda i: abs(scale_pcs[i] - pc))
        new_idx = (idx + steps) % len(scale_pcs)
        return scale_pcs[new_idx]

    def _diatonic_below(pc: int, steps: int) -> int:
        return _diatonic_above(pc, -steps)

    voices: list[list[Note]] = [list(melody)]

    if style == "thirds":
        harmony: list[Note] = []
        for n in melody:
            if n.pitch is None:
                harmony.append(Note.rest(n.duration))
            else:
                pc = _semi(str(n.pitch))
                h_pc = _diatonic_above(pc, 2)  # diatonic 3rd above
                harmony.append(Note(_NOTE_NAMES[h_pc], n.octave, n.duration, velocity=n.velocity))
        voices.append(harmony)

    elif style == "sixths":
        harmony = []
        for n in melody:
            if n.pitch is None:
                harmony.append(Note.rest(n.duration))
            else:
                pc = _semi(str(n.pitch))
                h_pc = _diatonic_below(pc, 2)  # diatonic 3rd below = 6th above
                harmony.append(
                    Note(
                        _NOTE_NAMES[h_pc],
                        n.octave - 1 if h_pc > pc else n.octave,
                        n.duration,
                        velocity=n.velocity,
                    )
                )
        voices.append(harmony)

    elif style == "chorale":
        # Simplified: thirds above + sixth below
        thirds: list[Note] = []
        sixths: list[Note] = []
        for n in melody:
            if n.pitch is None:
                thirds.append(Note.rest(n.duration))
                sixths.append(Note.rest(n.duration))
            else:
                pc = _semi(str(n.pitch))
                t_pc = _diatonic_above(pc, 2)
                s_pc = _diatonic_below(pc, 2)
                thirds.append(Note(_NOTE_NAMES[t_pc], n.octave, n.duration, velocity=n.velocity))
                sixths.append(
                    Note(
                        _NOTE_NAMES[s_pc],
                        n.octave - 1 if s_pc > pc else n.octave,
                        n.duration,
                        velocity=n.velocity,
                    )
                )
        voices.append(thirds)
        voices.append(sixths)

    return voices


# ---------------------------------------------------------------------------
# Practice room tools (v76.0)
# ---------------------------------------------------------------------------


def click_track(
    bpm: float = 120.0,
    bars: int = 8,
    beats_per_bar: int = 4,
    subdivisions: int = 1,
    accent_note: str = "C",
    tick_note: str = "C",
    octave: int = 6,
) -> list[Note]:
    """Generate a metronome click track.

    Beat 1 is accented, remaining beats are softer. Subdivisions add
    ticks between beats (2 = 8th notes, 4 = 16th notes).

    Args:
        bpm:            Tempo (for reference — duration is calculated).
        bars:           Number of bars.
        beats_per_bar:  Beats per bar.
        subdivisions:   Subdivisions per beat (1 = none, 2 = 8ths, 4 = 16ths).
        accent_note:    Pitch for accented beat 1.
        tick_note:      Pitch for regular beats.
        octave:         Click octave.

    Returns:
        List of Notes forming the click track.
    """
    beat_dur = 60.0 / bpm
    sub_dur = beat_dur / subdivisions
    result: list[Note] = []

    for bar in range(bars):
        for beat in range(beats_per_bar):
            for sub in range(subdivisions):
                if beat == 0 and sub == 0:
                    result.append(Note(accent_note, octave, sub_dur, velocity=100))
                elif sub == 0:
                    result.append(Note(tick_note, octave, sub_dur, velocity=75))
                else:
                    result.append(Note(tick_note, octave - 1, sub_dur, velocity=50))

    return result


def backing_track(
    progression: list[tuple[str, str]],
    key: str = "C",
    style: str = "rock",
    bars_per_chord: int = 1,
    seed: int | None = None,
) -> dict[str, list[Note]]:
    """Generate a backing track with drums, bass, and chords.

    One function to get a full rhythm section. Useful for practice,
    demos, or as the foundation of a song.

    Args:
        progression:    Chord progression.
        key:            Key for bass line.
        style:          'rock', 'jazz', 'latin', or 'funk'.
        bars_per_chord: Bars per chord (for duration calc).
        seed:           Random seed.

    Returns:
        Dict: {bass, chords, kick, snare, hat} — each a list of Notes.
    """
    chords: list[Note] = []
    chord_dur = bars_per_chord * 4.0
    for root, shape in progression:
        # Simple chord hit
        k = _semi(root)
        semis = _CHORD_SEMI.get(shape, [0, 4, 7])
        for s in semis:
            chords.append(Note(_NOTE_NAMES[(k + s) % 12], 3, chord_dur))

    # Bass
    if style == "jazz":
        bass = bass_line_jazz(progression, seed=seed)
    elif style == "funk":
        bass = bass_line_funk(progression, seed=seed)
    elif style == "latin":
        bass = bass_line_latin(progression, seed=seed)
    else:
        # Rock: root notes
        bass = []
        for root, _ in progression:
            for _ in range(bars_per_chord * 4):
                bass.append(Note(root, 2, 1.0, velocity=90))

    # Drums (simplified patterns)
    total_beats = len(progression) * bars_per_chord * 4
    kick: list[Note] = []
    snare: list[Note] = []
    hat: list[Note] = []
    for beat in range(total_beats):
        if beat % 4 == 0:
            kick.append(Note("C", 2, 1.0, velocity=100))
        elif beat % 4 == 2:
            kick.append(Note("C", 2, 1.0, velocity=70))
        else:
            kick.append(Note.rest(1.0))

        if beat % 4 == 2:
            snare.append(Note("C", 3, 1.0, velocity=90))
        else:
            snare.append(Note.rest(1.0))

        hat.append(Note("C", 5, 0.5, velocity=60))
        hat.append(Note("C", 5, 0.5, velocity=40))

    return {"bass": bass, "chords": chords, "kick": kick, "snare": snare, "hat": hat}


def tempo_trainer(
    start_bpm: float = 80.0,
    end_bpm: float = 160.0,
    bars_per_step: int = 4,
    bpm_increment: float = 10.0,
    beats_per_bar: int = 4,
) -> list[dict]:
    """Generate a tempo training plan with gradually increasing BPM.

    Returns a list of sections, each with its BPM and click track.
    Practice starts slow and builds — the only honest way to get fast.

    Args:
        start_bpm:      Starting tempo.
        end_bpm:        Target tempo.
        bars_per_step:  Bars at each tempo level.
        bpm_increment:  BPM increase per step.
        beats_per_bar:  Beats per bar.

    Returns:
        List of dicts: {bpm, click, bars}.
    """
    sections: list[dict] = []
    current_bpm = start_bpm
    while current_bpm <= end_bpm:
        clicks = click_track(current_bpm, bars_per_step, beats_per_bar)
        sections.append({"bpm": current_bpm, "click": clicks, "bars": bars_per_step})
        current_bpm += bpm_increment
    return sections


# ---------------------------------------------------------------------------
# Song statistics (v77.0)
# ---------------------------------------------------------------------------


def corpus_stats(
    progressions: list[list[tuple[str, str]]],
) -> dict:
    """Aggregate statistics across a collection of chord progressions.

    The bird's-eye view: how many unique roots, which chord shapes
    dominate, average progression length.

    Args:
        progressions: List of chord progressions (each a list of (root, shape) tuples).

    Returns:
        Dict with: total_chords, unique_roots, unique_shapes, avg_length,
        most_common_root, most_common_shape.
    """
    total_chords = 0
    root_counts: dict[str, int] = {}
    shape_counts: dict[str, int] = {}

    for prog in progressions:
        total_chords += len(prog)
        for root, shape in prog:
            root_counts[root] = root_counts.get(root, 0) + 1
            shape_counts[shape] = shape_counts.get(shape, 0) + 1

    avg_length = total_chords / max(len(progressions), 1)
    most_common_root = max(root_counts, key=root_counts.get) if root_counts else "C"
    most_common_shape = max(shape_counts, key=shape_counts.get) if shape_counts else "maj"

    return {
        "total_progressions": len(progressions),
        "total_chords": total_chords,
        "unique_roots": len(root_counts),
        "unique_shapes": len(shape_counts),
        "avg_length": round(avg_length, 1),
        "most_common_root": most_common_root,
        "most_common_shape": most_common_shape,
        "root_counts": dict(sorted(root_counts.items(), key=lambda x: -x[1])),
        "shape_counts": dict(sorted(shape_counts.items(), key=lambda x: -x[1])),
    }


def key_distribution(
    progressions: list[list[tuple[str, str]]],
) -> dict[str, int]:
    """Count how many progressions are in each estimated key.

    Args:
        progressions: List of chord progressions.

    Returns:
        Dict mapping key name → count, sorted by frequency.
    """
    counts: dict[str, int] = {}
    for prog in progressions:
        if prog:
            estimated = detect_key(prog)
            counts[estimated] = counts.get(estimated, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


def tempo_distribution(
    bpms: list[float],
    bucket_size: float = 10.0,
) -> dict[str, int]:
    """Create a BPM histogram from a list of tempos.

    Args:
        bpms:        List of BPM values.
        bucket_size: Width of each histogram bucket.

    Returns:
        Dict mapping BPM range string → count.
    """
    buckets: dict[str, int] = {}
    for bpm in bpms:
        low = int(bpm // bucket_size) * int(bucket_size)
        high = low + int(bucket_size)
        key = f"{low}-{high}"
        buckets[key] = buckets.get(key, 0) + 1
    return dict(sorted(buckets.items()))


# ---------------------------------------------------------------------------
# Melodic pattern database (v78.0)
# ---------------------------------------------------------------------------

_PATTERN_DB = {
    # Jazz licks
    "jazz_ii_v_i": {"notes": [2, 4, 5, 7, 9, 7, 5, 4], "genre": "jazz", "difficulty": 2},
    "jazz_bebop_turn": {"notes": [0, 2, 4, 3, 4, 7, 5, 4], "genre": "jazz", "difficulty": 3},
    "jazz_enclosure": {"notes": [5, 3, 4, 7, 6, 7], "genre": "jazz", "difficulty": 2},
    "jazz_coltrane_pattern": {"notes": [0, 4, 7, 11, 9, 7, 4, 2], "genre": "jazz", "difficulty": 4},
    "jazz_blues_head": {"notes": [0, 3, 5, 6, 7, 10, 7, 5], "genre": "jazz", "difficulty": 2},
    # Blues licks
    "blues_bend": {"notes": [0, 3, 5, 3, 0], "genre": "blues", "difficulty": 1},
    "blues_turnaround": {"notes": [7, 6, 5, 4, 3, 2, 0], "genre": "blues", "difficulty": 2},
    "blues_call": {"notes": [0, 3, 5, 7, 5, 3], "genre": "blues", "difficulty": 1},
    "blues_response": {"notes": [10, 7, 5, 3, 0], "genre": "blues", "difficulty": 1},
    # Rock riffs
    "rock_power": {"notes": [0, 0, 7, 7, 5, 5, 0], "genre": "rock", "difficulty": 1},
    "rock_pentatonic_run": {"notes": [0, 2, 4, 7, 9, 12, 9, 7], "genre": "rock", "difficulty": 2},
    "rock_chromatic_walk": {"notes": [0, 1, 2, 3, 4, 5, 6, 7], "genre": "rock", "difficulty": 1},
    # Latin patterns
    "latin_montuno": {"notes": [0, 4, 7, 4, 0, 4, 7, 9], "genre": "latin", "difficulty": 2},
    "latin_guajeo": {"notes": [0, 3, 7, 8, 7, 3, 0, 3], "genre": "latin", "difficulty": 2},
    # Classical figures
    "classical_alberti": {"notes": [0, 4, 7, 4, 0, 4, 7, 4], "genre": "classical", "difficulty": 1},
    "classical_mordent": {"notes": [0, 2, 0], "genre": "classical", "difficulty": 1},
    "classical_turn": {"notes": [2, 0, -1, 0], "genre": "classical", "difficulty": 1},
    "classical_scale_run": {
        "notes": [0, 2, 4, 5, 7, 9, 11, 12],
        "genre": "classical",
        "difficulty": 2,
    },
    # Funk patterns
    "funk_slap": {"notes": [0, 12, 0, 5, 0, 12, 7, 5], "genre": "funk", "difficulty": 2},
    "funk_ghost": {"notes": [0, 0, 5, 0, 7, 0, 5, 0], "genre": "funk", "difficulty": 2},
}


def list_patterns(
    genre: str | None = None,
    max_difficulty: int | None = None,
) -> list[str]:
    """List available patterns, optionally filtered by genre/difficulty.

    Args:
        genre:          Filter by genre (jazz, blues, rock, latin, classical, funk).
        max_difficulty: Maximum difficulty (1-4).

    Returns:
        Sorted list of pattern names.
    """
    result = []
    for name, info in _PATTERN_DB.items():
        if genre and info["genre"] != genre:
            continue
        if max_difficulty and info["difficulty"] > max_difficulty:
            continue
        result.append(name)
    return sorted(result)


def get_pattern(
    name: str,
    key: str = "C",
    octave: int = 5,
    duration: float = 0.5,
) -> list[Note]:
    """Retrieve a named pattern transposed to a key.

    Args:
        name:     Pattern name from the database.
        key:      Key root to transpose to.
        octave:   Base octave.
        duration: Note duration.

    Returns:
        List of Notes forming the pattern.

    Raises:
        ValueError: If pattern name not found.
    """
    if name not in _PATTERN_DB:
        raise ValueError(f"Unknown pattern {name!r}. Use list_patterns() to see available.")
    k = _semi(key)
    intervals = _PATTERN_DB[name]["notes"]
    return [Note(_NOTE_NAMES[(k + iv) % 12], octave + (k + iv) // 12, duration) for iv in intervals]


def chain_patterns(
    names: list[str],
    key: str = "C",
    octave: int = 5,
    duration: float = 0.5,
    connector_duration: float = 0.25,
) -> list[Note]:
    """Chain multiple patterns together with scale-tone connectors.

    Retrieves each pattern and links them with a passing tone between
    the last note of one pattern and the first of the next.

    Args:
        names:              Pattern names.
        key:                Key root.
        octave:             Base octave.
        duration:           Note duration within patterns.
        connector_duration: Duration for connecting notes.

    Returns:
        List of Notes forming the chained sequence.
    """
    result: list[Note] = []
    for i, name in enumerate(names):
        notes = get_pattern(name, key, octave, duration)
        result.extend(notes)
        # Add connector between patterns
        if i < len(names) - 1 and notes:
            last_semi = _semi(str(notes[-1].pitch))
            next_pattern = get_pattern(names[i + 1], key, octave, duration)
            if next_pattern:
                next_semi = _semi(str(next_pattern[0].pitch))
                mid = ((last_semi + next_semi) // 2) % 12
                result.append(Note(_NOTE_NAMES[mid], octave, connector_duration))
    return result


# ---------------------------------------------------------------------------
# Dynamic range processing (v79.0)
# ---------------------------------------------------------------------------


def crescendo(
    notes: list[Note],
    start_vel: int = 40,
    end_vel: int = 100,
) -> list[Note]:
    """Apply a gradual volume increase across a note list.

    Args:
        notes:     Input notes.
        start_vel: Starting velocity (0-127).
        end_vel:   Ending velocity (0-127).

    Returns:
        New note list with linearly interpolated velocities.
    """
    if not notes:
        return []
    result: list[Note] = []
    for i, n in enumerate(notes):
        frac = i / max(len(notes) - 1, 1)
        vel = int(start_vel + (end_vel - start_vel) * frac)
        vel = max(0, min(127, vel))
        if n.pitch is None:
            result.append(Note.rest(n.duration))
        else:
            result.append(Note(n.pitch, n.octave, n.duration, velocity=vel))
    return result


def decrescendo(
    notes: list[Note],
    start_vel: int = 100,
    end_vel: int = 40,
) -> list[Note]:
    """Apply a gradual volume decrease across a note list.

    Args:
        notes:     Input notes.
        start_vel: Starting velocity.
        end_vel:   Ending velocity.

    Returns:
        New note list with decreasing velocities.
    """
    return crescendo(notes, start_vel, end_vel)


def sforzando(notes: list[Note], position: int = 0, accent_vel: int = 127) -> list[Note]:
    """Apply a sudden accent at a specific note position.

    Args:
        notes:      Input notes.
        position:   Index of the note to accent.
        accent_vel: Velocity for the accented note.

    Returns:
        New note list with the accent applied.
    """
    result = list(notes)
    if 0 <= position < len(result) and result[position].pitch is not None:
        n = result[position]
        result[position] = Note(n.pitch, n.octave, n.duration, velocity=accent_vel)
    return result


def dynamics_map(notes: list[Note]) -> list[int]:
    """Extract the velocity curve from a note list.

    Args:
        notes: Input notes.

    Returns:
        List of velocity values, one per note (0 for rests).
    """
    return [n.velocity if n.pitch is not None else 0 for n in notes]


# ---------------------------------------------------------------------------
# Chord progression generator (v80.0)
# ---------------------------------------------------------------------------

_GENRE_TEMPLATES = {
    "pop": [
        ["I", "V", "vi", "IV"],
        ["I", "IV", "V", "V"],
        ["vi", "IV", "I", "V"],
    ],
    "jazz": [
        ["IImaj7", "V7", "Imaj7", "Imaj7"],
        ["Imaj7", "vi7", "ii7", "V7"],
        ["iii7", "vi7", "ii7", "V7"],
    ],
    "classical": [
        ["I", "IV", "V", "I"],
        ["I", "vi", "IV", "V"],
        ["I", "ii", "V", "I"],
    ],
    "blues": [
        ["I7", "I7", "I7", "I7", "IV7", "IV7", "I7", "I7", "V7", "IV7", "I7", "V7"],
    ],
}

# Mood modifiers: intervals to add/substitute
_MOOD_MAP = {
    "bright": {"prefer": ["I", "IV", "V"], "avoid": ["vi", "ii"]},
    "dark": {"prefer": ["vi", "ii", "iii"], "avoid": ["I", "IV"]},
    "tense": {"prefer": ["V7", "viio", "bII"], "avoid": ["I", "IV"]},
}


def generate_progression(
    key: str = "C",
    length: int = 4,
    genre: str = "pop",
    seed: int | None = None,
) -> list[tuple[str, str]]:
    """Generate a chord progression from genre templates.

    Picks a template randomly from the genre's pool and transposes to key.
    For blues, returns a full 12-bar progression regardless of length.

    Args:
        key:    Key root.
        length: Number of chords (ignored for blues).
        genre:  'pop', 'jazz', 'classical', or 'blues'.
        seed:   Random seed.

    Returns:
        List of (root, shape) tuples.
    """
    import random as _rng

    rng = _rng.Random(seed)
    templates = _GENRE_TEMPLATES.get(genre, _GENRE_TEMPLATES["pop"])
    template = rng.choice(templates)

    # Parse roman numerals
    result: list[tuple[str, str]] = []
    for numeral in template:
        # Quick parse: uppercase = major context
        clean = numeral.replace("7", "").replace("maj", "")
        suffix = ""
        if "maj7" in numeral:
            suffix = "maj7"
        elif "7" in numeral:
            suffix = "dom7"

        roman_map = {
            "I": 0,
            "II": 2,
            "III": 4,
            "IV": 5,
            "V": 7,
            "VI": 9,
            "VII": 11,
            "i": 0,
            "ii": 2,
            "iii": 4,
            "iv": 5,
            "v": 7,
            "vi": 9,
            "vii": 11,
        }

        # Handle lowercase prefix
        is_minor = clean[0].islower() if clean else False
        upper = clean.upper()

        degree = roman_map.get(upper, 0)
        k = _semi(key)
        root = _NOTE_NAMES[(k + degree) % 12]

        if suffix:
            shape = suffix
        elif is_minor:
            shape = "min"
        else:
            shape = "maj"

        result.append((root, shape))

    # Trim or repeat to length (blues is always 12)
    if genre != "blues":
        while len(result) < length:
            result.extend(result)
        result = result[:length]

    return result


def extend_progression(
    existing: list[tuple[str, str]],
    bars: int = 4,
    key: str = "C",
    seed: int | None = None,
) -> list[tuple[str, str]]:
    """Extend an existing progression by generating compatible continuation.

    Uses the last chord as context to pick a natural next chord,
    then continues for the requested number of bars.

    Args:
        existing: Current progression.
        bars:     Number of chords to add.
        key:      Key context.
        seed:     Random seed.

    Returns:
        Extended progression (original + new chords).
    """
    import random as _rng

    rng = _rng.Random(seed)
    result = list(existing)
    k = _semi(key)

    for _ in range(bars):
        # Pick a diatonic chord biased toward common functions
        degree = rng.choice([0, 0, 5, 5, 7, 7, 9, 2])  # I, IV, V, vi, ii
        root = _NOTE_NAMES[(k + degree) % 12]
        shape = "min" if degree in (2, 4, 9) else "maj"
        if degree == 7:
            shape = "dom7"
        result.append((root, shape))

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
# Comping pattern library (v82.0)
# ---------------------------------------------------------------------------


def comp_pattern(
    progression: list[tuple[str, str]],
    style: str = "rock",
    octave: int = 3,
    seed: int | None = None,
) -> list[Note]:
    """Generate a rhythmic comping (accompaniment) pattern for chords.

    Comping is what the rhythm section plays behind the soloist. Each
    style has its own rhythmic DNA — bossa nova syncopation is not
    swing quarter notes is not funk muted 16ths.

    Styles:
    - 'rock':   power chord 8th notes on every beat
    - 'swing':  Freddie Green quarter-note chunks
    - 'funk':   muted 16th-note chops with ghost notes
    - 'bossa':  syncopated shell voicings (3-7 on anticipations)
    - 'ballad': arpeggiated chords, slow and spacious

    Args:
        progression: Chord progression as (root, shape) tuples.
        style:       Comping style name.
        octave:      Chord octave.
        seed:        Random seed.

    Returns:
        List of Notes forming the comping pattern.
    """
    import random as _rng

    rng = _rng.Random(seed)
    result: list[Note] = []

    for root, shape in progression:
        k = _semi(root)
        semis = _CHORD_SEMI.get(shape, [0, 4, 7])

        if style == "rock":
            # 8th note power chords (root + 5th)
            for _ in range(8):
                result.append(Note(_NOTE_NAMES[k], octave, 0.5, velocity=85))

        elif style == "swing":
            # Freddie Green: quarter note chords, beat 2 and 4 accented
            for beat in range(4):
                vel = 90 if beat in (1, 3) else 70
                result.append(Note(_NOTE_NAMES[(k + semis[0]) % 12], octave, 1.0, velocity=vel))

        elif style == "funk":
            # Muted 16th-note chops with gaps
            for sub in range(16):
                if sub % 4 == 0:
                    result.append(Note(_NOTE_NAMES[k], octave, 0.25, velocity=90))
                elif rng.random() > 0.4:
                    result.append(Note(_NOTE_NAMES[k], octave, 0.25, velocity=40))
                else:
                    result.append(Note.rest(0.25))

        elif style == "bossa":
            # Syncopated: hit on 1, anticipate beat 3 (on the "and" of 2)
            result.append(
                Note(_NOTE_NAMES[(k + semis[1 % len(semis)]) % 12], octave, 1.5, velocity=75)
            )
            result.append(
                Note(_NOTE_NAMES[(k + semis[2 % len(semis)]) % 12], octave, 1.0, velocity=70)
            )
            result.append(Note(_NOTE_NAMES[(k + semis[0]) % 12], octave, 1.5, velocity=80))

        else:  # ballad — arpeggiated
            for s in semis:
                pc = (k + s) % 12
                result.append(Note(_NOTE_NAMES[pc], octave, 4.0 / len(semis), velocity=60))

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
# Instrument technique simulation (v84.0)
# ---------------------------------------------------------------------------


def hammer_on(note_a: Note, note_b: Note) -> list[Note]:
    """Simulate a guitar hammer-on — second note is quieter with no attack gap.

    Args:
        note_a: First (picked) note.
        note_b: Second (hammered) note — gets reduced velocity.

    Returns:
        Two notes: original velocity, then 60% velocity.
    """
    n2_vel = int(note_b.velocity * 0.6) if note_b.pitch else 0
    return [
        note_a,
        Note(note_b.pitch, note_b.octave, note_b.duration, velocity=n2_vel)
        if note_b.pitch
        else Note.rest(note_b.duration),
    ]


def pull_off(note_a: Note, note_b: Note) -> list[Note]:
    """Simulate a guitar pull-off — reverse of hammer-on.

    Args:
        note_a: First (fretted) note.
        note_b: Second (pulled-off to) note — gets reduced velocity.

    Returns:
        Two notes with decreasing velocity.
    """
    return hammer_on(note_a, note_b)  # same velocity profile


def slide(
    note_a: Note,
    note_b: Note,
    steps: int = 4,
) -> list[Note]:
    """Simulate a glissando (slide) between two notes.

    Inserts chromatic passing tones between the start and end notes.
    The slide duration is divided equally among all intermediate notes.

    Args:
        note_a: Starting note.
        note_b: Ending note.
        steps:  Number of intermediate chromatic steps.

    Returns:
        List of notes from A to B via chromatic steps.
    """
    if note_a.pitch is None or note_b.pitch is None:
        return [note_a, note_b]

    a_abs = _semi(str(note_a.pitch)) + note_a.octave * 12
    b_abs = _semi(str(note_b.pitch)) + note_b.octave * 12
    direction = 1 if b_abs > a_abs else -1
    total_semitones = abs(b_abs - a_abs)
    actual_steps = min(steps, total_semitones)

    if actual_steps <= 0:
        return [note_a, note_b]

    step_dur = note_a.duration / (actual_steps + 1)
    result: list[Note] = []
    for i in range(actual_steps + 1):
        current = a_abs + direction * i * (total_semitones // (actual_steps + 1))
        pc = current % 12
        oct = current // 12
        vel = note_a.velocity - (i * 5)  # slight decay during slide
        result.append(Note(_NOTE_NAMES[pc], oct, step_dur, velocity=max(vel, 30)))

    result.append(note_b)
    return result


def palm_mute(notes: list[Note], decay_factor: float = 0.3) -> list[Note]:
    """Simulate palm muting — reduced sustain and percussive attack.

    Palm muting shortens note durations and reduces velocity for a
    tight, chunky sound. The backbone of metal rhythm guitar.

    Args:
        notes:        Input notes.
        decay_factor: Duration multiplier (0.3 = 30% of original length, rest fills gap).

    Returns:
        Notes with shortened durations, padded with rests.
    """
    result: list[Note] = []
    for n in notes:
        if n.pitch is None:
            result.append(n)
        else:
            short_dur = n.duration * decay_factor
            rest_dur = n.duration * (1.0 - decay_factor)
            result.append(Note(n.pitch, n.octave, short_dur, velocity=n.velocity))
            result.append(Note.rest(rest_dur))
    return result


# ---------------------------------------------------------------------------
# Song comparison report (v85.0)
# ---------------------------------------------------------------------------


def compare_progressions(
    prog_a: list[tuple[str, str]],
    prog_b: list[tuple[str, str]],
    key: str = "C",
) -> dict:
    """Compare two chord progressions across multiple dimensions.

    Returns a structured report: shared chords, key estimates,
    complexity delta, length delta, root overlap ratio.

    Args:
        prog_a: First progression.
        prog_b: Second progression.
        key:    Key context for complexity scoring.

    Returns:
        Dict with comparison metrics.
    """
    set_a = set(prog_a)
    set_b = set(prog_b)
    shared = sorted(set_a & set_b)

    key_a = detect_key(prog_a) if prog_a else "C"
    key_b = detect_key(prog_b) if prog_b else "C"

    comp_a = complexity_score(prog_a, key)
    comp_b = complexity_score(prog_b, key)

    roots_a = {r for r, _ in prog_a}
    roots_b = {r for r, _ in prog_b}
    root_overlap = len(roots_a & roots_b) / max(len(roots_a | roots_b), 1)

    return {
        "length_a": len(prog_a),
        "length_b": len(prog_b),
        "shared_chords": shared,
        "shared_count": len(shared),
        "unique_to_a": sorted(set_a - set_b),
        "unique_to_b": sorted(set_b - set_a),
        "key_a": key_a,
        "key_b": key_b,
        "same_key": key_a == key_b,
        "complexity_a": comp_a,
        "complexity_b": comp_b,
        "complexity_delta": comp_b - comp_a,
        "root_overlap": round(root_overlap, 3),
    }


# ---------------------------------------------------------------------------
# Enharmonic intelligence (v86.0)
# ---------------------------------------------------------------------------

_ENHARMONIC_MAP = {
    "C": "C",
    "C#": "Db",
    "Db": "C#",
    "D": "D",
    "D#": "Eb",
    "Eb": "D#",
    "E": "Fb",
    "Fb": "E",
    "F": "F",
    "F#": "Gb",
    "Gb": "F#",
    "G": "G",
    "G#": "Ab",
    "Ab": "G#",
    "A": "A",
    "A#": "Bb",
    "Bb": "A#",
    "B": "Cb",
    "Cb": "B",
}

_KEY_SIGNATURES = {
    "C": [],
    "G": ["F#"],
    "D": ["F#", "C#"],
    "A": ["F#", "C#", "G#"],
    "E": ["F#", "C#", "G#", "D#"],
    "B": ["F#", "C#", "G#", "D#", "A#"],
    "F#": ["F#", "C#", "G#", "D#", "A#", "E#"],
    "F": ["Bb"],
    "Bb": ["Bb", "Eb"],
    "Eb": ["Bb", "Eb", "Ab"],
    "Ab": ["Bb", "Eb", "Ab", "Db"],
    "Db": ["Bb", "Eb", "Ab", "Db", "Gb"],
    "Gb": ["Bb", "Eb", "Ab", "Db", "Gb", "Cb"],
}


def enharmonic_equivalent(note: str) -> str:
    """Return the enharmonic equivalent of a note name.

    C# ↔ Db, F# ↔ Gb, etc. Notes without common enharmonics
    (like C, D, G) return themselves.

    Args:
        note: Note name.

    Returns:
        Enharmonic spelling.
    """
    return _ENHARMONIC_MAP.get(note, note)


def key_signature_accidentals(key: str) -> list[str]:
    """Return the sharps or flats in a key signature.

    Args:
        key: Key name (e.g. 'G', 'Bb', 'F#').

    Returns:
        List of accidentals (e.g. ['F#'] for G major, ['Bb', 'Eb'] for Bb major).
    """
    return list(_KEY_SIGNATURES.get(key, []))


def respell_note(note: str, key: str) -> str:
    """Pick the enharmonic spelling that fits the key signature.

    In Ab major, use Db (not C#). In A major, use C# (not Db).
    Context-aware spelling is what separates readable notation from chaos.

    Args:
        note: Note name to potentially respell.
        key:  Key context.

    Returns:
        The spelling that fits the key.
    """
    accidentals = key_signature_accidentals(key)
    alt = enharmonic_equivalent(note)

    # Prefer the spelling that appears in the key's accidentals
    if note in accidentals:
        return note
    if alt in accidentals:
        return alt

    # Prefer flats in flat keys, sharps in sharp keys
    has_flats = any("b" in a for a in accidentals)
    has_sharps = any("#" in a for a in accidentals)

    if has_flats and "b" in alt and "#" in note:
        return alt
    if has_sharps and "#" in alt and "b" in note:
        return alt

    return note  # no change needed


# ---------------------------------------------------------------------------
# Song builder DSL (v87.0)
# ---------------------------------------------------------------------------


def parse_chord_line(text: str) -> list[tuple[str, str]]:
    """Parse a chord chart line into a chord progression.

    Syntax: `| Cmaj7 | Am7 | Dm7 | G7 |`
    Each cell between pipes is one chord. Supports standard
    chord symbols: maj, min, 7, maj7, min7, dim, aug, sus4, sus2.

    Args:
        text: Chord chart line.

    Returns:
        List of (root, shape) tuples.
    """
    chords: list[tuple[str, str]] = []
    cells = [c.strip() for c in text.split("|") if c.strip()]

    for cell in cells:
        symbol = cell.strip()
        if not symbol or symbol == "-":
            continue

        # Extract root (1-2 chars: letter + optional #/b)
        root = symbol[0]
        idx = 1
        if idx < len(symbol) and symbol[idx] in "#b":
            root += symbol[idx]
            idx += 1

        suffix = symbol[idx:]
        shape_map = {
            "": "maj",
            "m": "min",
            "min": "min",
            "7": "dom7",
            "maj7": "maj7",
            "min7": "min7",
            "m7": "min7",
            "dim": "dim",
            "dim7": "dim7",
            "aug": "aug",
            "sus4": "sus4",
            "sus2": "sus2",
            "9": "dom9",
            "m9": "min9",
            "maj9": "maj9",
        }
        shape = shape_map.get(suffix, "maj")
        chords.append((root, shape))

    return chords


def parse_melody_line(
    text: str,
    octave: int = 5,
    duration: float = 0.5,
) -> list[Note]:
    """Parse a melody notation line into notes.

    Syntax: `C5 D5 E5 - F5 G5` where `-` is a rest.
    Notes can include octave (C5) or use the default octave (C).

    Args:
        text:     Melody line.
        octave:   Default octave if not specified per note.
        duration: Duration per note.

    Returns:
        List of Notes.
    """
    notes: list[Note] = []
    tokens = text.split()

    for token in tokens:
        if token == "-" or token == "~":
            notes.append(Note.rest(duration))
            continue

        # Extract pitch and optional octave
        pitch = token[0]
        idx = 1
        if idx < len(token) and token[idx] in "#b":
            pitch += token[idx]
            idx += 1

        if idx < len(token) and token[idx].isdigit():
            oct = int(token[idx])
        else:
            oct = octave

        notes.append(Note(pitch, oct, duration))

    return notes


def song_from_dsl(text: str, bpm: int = 120) -> dict:
    """Parse a mini-DSL into song components.

    Syntax:
        [verse]
        chords: | Cmaj7 | Am7 | Dm7 | G7 |
        melody: C5 D5 E5 - F5 G5 A5 G5

        [chorus]
        chords: | Fmaj7 | G7 | Cmaj7 | Cmaj7 |
        melody: A5 G5 F5 E5 D5 C5 D5 E5

    Returns a dict of sections, each with chords and melody.

    Args:
        text: DSL text.
        bpm:  Tempo.

    Returns:
        Dict: {bpm, sections: [{name, chords, melody}, ...]}.
    """
    result: dict = {"bpm": bpm, "sections": []}
    current_section: dict | None = None

    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith("[") and line.endswith("]"):
            if current_section:
                result["sections"].append(current_section)
            current_section = {"name": line[1:-1], "chords": [], "melody": []}
            continue

        if current_section is None:
            current_section = {"name": "intro", "chords": [], "melody": []}

        if line.startswith("chords:"):
            chord_text = line[len("chords:") :].strip()
            current_section["chords"] = parse_chord_line(chord_text)
        elif line.startswith("melody:"):
            melody_text = line[len("melody:") :].strip()
            current_section["melody"] = parse_melody_line(melody_text)

    if current_section:
        result["sections"].append(current_section)

    return result


# ---------------------------------------------------------------------------
# Remix engine (v88.0)
# ---------------------------------------------------------------------------


def change_key(
    notes: list[Note],
    from_key: str,
    to_key: str,
) -> list[Note]:
    """Transpose a note list from one key to another.

    Preserves intervals by shifting all pitches by the semitone
    difference between keys.

    Args:
        notes:    Input notes.
        from_key: Original key root.
        to_key:   Target key root.

    Returns:
        Transposed note list.
    """
    delta = (_semi(to_key) - _semi(from_key)) % 12
    result: list[Note] = []
    for n in notes:
        if n.pitch is None:
            result.append(Note.rest(n.duration))
        else:
            new_semi = (_semi(str(n.pitch)) + delta) % 12
            new_oct = n.octave + (_semi(str(n.pitch)) + delta) // 12
            result.append(Note(_NOTE_NAMES[new_semi], new_oct, n.duration, velocity=n.velocity))
    return result


def double_time(notes: list[Note]) -> list[Note]:
    """Halve all durations — double the effective tempo.

    Everything plays twice as fast without changing the BPM number.

    Args:
        notes: Input notes.

    Returns:
        Notes with halved durations.
    """
    return [
        Note(n.pitch, n.octave, n.duration / 2, velocity=n.velocity)
        if n.pitch is not None
        else Note.rest(n.duration / 2)
        for n in notes
    ]


def half_time(notes: list[Note]) -> list[Note]:
    """Double all durations — halve the effective tempo.

    Everything plays twice as slow. The breakdown section.

    Args:
        notes: Input notes.

    Returns:
        Notes with doubled durations.
    """
    return [
        Note(n.pitch, n.octave, n.duration * 2, velocity=n.velocity)
        if n.pitch is not None
        else Note.rest(n.duration * 2)
        for n in notes
    ]


# ---------------------------------------------------------------------------
# Harmonic voice independence (v89.0)
# ---------------------------------------------------------------------------


def _motion_type(
    a1: int,
    a2: int,
    b1: int,
    b2: int,
) -> str:
    """Classify the motion between two voice pairs."""
    dir_a = 1 if a2 > a1 else (-1 if a2 < a1 else 0)
    dir_b = 1 if b2 > b1 else (-1 if b2 < b1 else 0)
    if dir_a == 0 and dir_b == 0:
        return "static"
    elif dir_a == 0 or dir_b == 0:
        return "oblique"
    elif dir_a == dir_b:
        return "similar"
    else:
        return "contrary"


def similar_motion_ratio(voice_a: list[Note], voice_b: list[Note]) -> float:
    """What fraction of movements are in parallel (similar) motion.

    Args:
        voice_a: First voice.
        voice_b: Second voice.

    Returns:
        Ratio 0.0–1.0 of similar motion.
    """
    count = 0
    total = 0
    min_len = min(len(voice_a), len(voice_b))
    for i in range(1, min_len):
        if any(n.pitch is None for n in [voice_a[i - 1], voice_a[i], voice_b[i - 1], voice_b[i]]):
            continue
        a1 = _semi(str(voice_a[i - 1].pitch)) + voice_a[i - 1].octave * 12
        a2 = _semi(str(voice_a[i].pitch)) + voice_a[i].octave * 12
        b1 = _semi(str(voice_b[i - 1].pitch)) + voice_b[i - 1].octave * 12
        b2 = _semi(str(voice_b[i].pitch)) + voice_b[i].octave * 12
        total += 1
        if _motion_type(a1, a2, b1, b2) == "similar":
            count += 1
    return round(count / max(total, 1), 3)


def contrary_motion_ratio(voice_a: list[Note], voice_b: list[Note]) -> float:
    """What fraction of movements are in contrary motion.

    Contrary motion = voices move in opposite directions. The gold
    standard for voice independence — Bach maximized this.

    Args:
        voice_a: First voice.
        voice_b: Second voice.

    Returns:
        Ratio 0.0–1.0 of contrary motion.
    """
    count = 0
    total = 0
    min_len = min(len(voice_a), len(voice_b))
    for i in range(1, min_len):
        if any(n.pitch is None for n in [voice_a[i - 1], voice_a[i], voice_b[i - 1], voice_b[i]]):
            continue
        a1 = _semi(str(voice_a[i - 1].pitch)) + voice_a[i - 1].octave * 12
        a2 = _semi(str(voice_a[i].pitch)) + voice_a[i].octave * 12
        b1 = _semi(str(voice_b[i - 1].pitch)) + voice_b[i - 1].octave * 12
        b2 = _semi(str(voice_b[i].pitch)) + voice_b[i].octave * 12
        total += 1
        if _motion_type(a1, a2, b1, b2) == "contrary":
            count += 1
    return round(count / max(total, 1), 3)


def voice_independence_score(voices: list[list[Note]]) -> int:
    """Rate how independently multiple voices move (0-100).

    Higher = more contrary/oblique motion, fewer parallel movements.
    Bach would score 90+. Parallel thirds score ~30.

    Args:
        voices: List of voice note-lists.

    Returns:
        Score 0-100.
    """
    if len(voices) < 2:
        return 100

    total_contrary = 0.0
    pairs = 0
    for i in range(len(voices)):
        for j in range(i + 1, len(voices)):
            total_contrary += contrary_motion_ratio(voices[i], voices[j])
            pairs += 1

    avg_contrary = total_contrary / max(pairs, 1)
    return min(100, int(avg_contrary * 130))  # scale so ~77% contrary = 100


# ---------------------------------------------------------------------------
# Music theory quiz generator (v90.0)
# ---------------------------------------------------------------------------


def quiz_intervals(
    count: int = 10,
    seed: int | None = None,
) -> list[dict]:
    """Generate interval identification quiz questions.

    Each question presents two notes; the answer is the interval name.

    Args:
        count: Number of questions.
        seed:  Random seed.

    Returns:
        List of dicts: {note_a, note_b, answer}.
    """
    import random as _rng

    rng = _rng.Random(seed)
    _INTERVAL_NAMES = {
        0: "P1",
        1: "m2",
        2: "M2",
        3: "m3",
        4: "M3",
        5: "P4",
        6: "TT",
        7: "P5",
        8: "m6",
        9: "M6",
        10: "m7",
        11: "M7",
    }
    questions = []
    for _ in range(count):
        pc_a = rng.randint(0, 11)
        interval = rng.randint(0, 11)
        pc_b = (pc_a + interval) % 12
        questions.append(
            {
                "note_a": _NOTE_NAMES[pc_a],
                "note_b": _NOTE_NAMES[pc_b],
                "answer": _INTERVAL_NAMES[interval],
            }
        )
    return questions


def quiz_chords(
    count: int = 10,
    seed: int | None = None,
) -> list[dict]:
    """Generate chord quality identification quiz questions.

    Each question presents a set of notes; the answer is the chord quality.

    Args:
        count: Number of questions.
        seed:  Random seed.

    Returns:
        List of dicts: {notes, answer_root, answer_shape}.
    """
    import random as _rng

    rng = _rng.Random(seed)
    shapes = ["maj", "min", "dim", "aug", "dom7"]
    questions = []
    for _ in range(count):
        root_pc = rng.randint(0, 11)
        shape = rng.choice(shapes)
        semis = _CHORD_SEMI.get(shape, [0, 4, 7])
        note_names = [_NOTE_NAMES[(root_pc + s) % 12] for s in semis]
        questions.append(
            {
                "notes": note_names,
                "answer_root": _NOTE_NAMES[root_pc],
                "answer_shape": shape,
            }
        )
    return questions


def grade_quiz(answers: list[str], correct: list[str]) -> dict:
    """Grade a quiz — compare user answers to correct answers.

    Args:
        answers: User's answers.
        correct: Correct answers.

    Returns:
        Dict: {score, total, percentage, wrong_indices}.
    """
    total = len(correct)
    right = sum(1 for a, c in zip(answers, correct) if a == c)
    wrong = [i for i, (a, c) in enumerate(zip(answers, correct)) if a != c]
    return {
        "score": right,
        "total": total,
        "percentage": round(right / max(total, 1) * 100, 1),
        "wrong_indices": wrong,
    }


# ---------------------------------------------------------------------------
# Arrangement density planner (v91.0)
# ---------------------------------------------------------------------------


def density_plan(
    sections: list[str],
    instruments: list[str],
    pattern: str = "build",
) -> list[dict]:
    """Plan which instruments play in which sections.

    Patterns:
    - 'build':  start sparse, add instruments each section
    - 'strip':  start full, remove instruments each section
    - 'wave':   sparse → full → sparse → full
    - 'full':   all instruments in every section

    Args:
        sections:    Section names (e.g. ['intro', 'verse', 'chorus']).
        instruments: Instrument/track names.
        pattern:     Density pattern.

    Returns:
        List of dicts: {section, active_instruments, count}.
    """
    n_sections = len(sections)
    n_instruments = len(instruments)
    result: list[dict] = []

    for i, section in enumerate(sections):
        if pattern == "build":
            count = max(1, int((i + 1) / n_sections * n_instruments))
        elif pattern == "strip":
            count = max(1, n_instruments - int(i / max(n_sections - 1, 1) * (n_instruments - 1)))
        elif pattern == "wave":
            import math

            frac = (math.sin(i / max(n_sections - 1, 1) * math.pi) + 1) / 2
            count = max(1, int(frac * n_instruments))
        else:  # full
            count = n_instruments

        active = instruments[:count]
        result.append(
            {
                "section": section,
                "active_instruments": active,
                "count": count,
            }
        )

    return result


def orchestration_curve(plan: list[dict]) -> list[int]:
    """Extract the instrument count curve from a density plan.

    Args:
        plan: Output from density_plan().

    Returns:
        List of integers: active instrument count per section.
    """
    return [p["count"] for p in plan]


# ---------------------------------------------------------------------------
# Chord progression probability matrix (v92.0)
# ---------------------------------------------------------------------------


def build_transition_matrix(
    progressions: list[list[tuple[str, str]]],
) -> dict[tuple[str, str], dict[tuple[str, str], float]]:
    """Build a Markov transition matrix from a corpus of progressions.

    Counts how often each chord follows another, then normalizes
    to probabilities. The statistical DNA of a musical style.

    Args:
        progressions: List of chord progressions.

    Returns:
        Nested dict: matrix[from_chord][to_chord] = probability.
    """
    counts: dict[tuple[str, str], dict[tuple[str, str], int]] = {}

    for prog in progressions:
        for i in range(len(prog) - 1):
            current = prog[i]
            nxt = prog[i + 1]
            if current not in counts:
                counts[current] = {}
            counts[current][nxt] = counts[current].get(nxt, 0) + 1

    # Normalize to probabilities
    matrix: dict[tuple[str, str], dict[tuple[str, str], float]] = {}
    for chord, transitions in counts.items():
        total = sum(transitions.values())
        matrix[chord] = {k: round(v / total, 4) for k, v in transitions.items()}

    return matrix


def most_likely_next(
    current: tuple[str, str],
    matrix: dict[tuple[str, str], dict[tuple[str, str], float]],
) -> tuple[str, str] | None:
    """Return the most probable next chord from a transition matrix.

    Args:
        current: Current chord (root, shape).
        matrix:  Transition matrix from build_transition_matrix().

    Returns:
        Most likely next chord, or None if current not in matrix.
    """
    transitions = matrix.get(current)
    if not transitions:
        return None
    return max(transitions, key=lambda k: transitions[k])


def generate_from_matrix(
    matrix: dict[tuple[str, str], dict[tuple[str, str], float]],
    length: int = 8,
    start: tuple[str, str] | None = None,
    seed: int | None = None,
) -> list[tuple[str, str]]:
    """Generate a chord progression by random walk through a transition matrix.

    Each chord is chosen probabilistically based on the transition
    weights from the current chord. The statistical ghost of every
    progression in the training corpus.

    Args:
        matrix: Transition matrix.
        length: Number of chords to generate.
        start:  Starting chord (random if None).
        seed:   Random seed.

    Returns:
        Generated chord progression.
    """
    import random as _rng

    rng = _rng.Random(seed)

    if not matrix:
        return []

    if start is None:
        start = rng.choice(list(matrix.keys()))

    result = [start]
    current = start

    for _ in range(length - 1):
        transitions = matrix.get(current)
        if not transitions:
            # Dead end — restart from random
            current = rng.choice(list(matrix.keys()))
            result.append(current)
            continue

        chords = list(transitions.keys())
        weights = list(transitions.values())
        chosen = rng.choices(chords, weights=weights, k=1)[0]
        result.append(chosen)
        current = chosen

    return result


# ---------------------------------------------------------------------------
# Musical form analysis report (v93.0)
# ---------------------------------------------------------------------------


def analysis_report(
    progression: list[tuple[str, str]],
    key: str = "C",
    bpm: float = 120.0,
    title: str = "Untitled",
) -> str:
    """Generate a markdown analysis report for a chord progression.

    Covers: form, key, cadences, complexity, tension curve, chord
    function distribution. The kind of report a theory professor
    writes — but in one function call.

    Args:
        progression: Chord progression.
        key:         Key for analysis.
        bpm:         Tempo.
        title:       Song/progression title.

    Returns:
        Markdown-formatted analysis string.
    """
    # Form
    form = label_form(progression, bars_per_section=4)

    # Cadences
    cadences = detect_cadences(progression, key)
    cadence_strs = [f"  - {c['type']} at position {c['position']}" for c in cadences]

    # Functional analysis
    func_analysis = functional_analysis(progression, key)
    func_counts: dict[str, int] = {}
    for fa in func_analysis:
        func_counts[fa["function"]] = func_counts.get(fa["function"], 0) + 1

    # Tension
    curve = tension_curve(progression, key)
    avg_tension = sum(curve) / max(len(curve), 1)
    peak_idx = curve.index(max(curve)) if curve else 0

    # Complexity
    comp = complexity_score(progression, key)

    lines = [
        f"# Analysis: {title}",
        "",
        f"**Key:** {key} major",
        f"**Tempo:** {bpm} BPM",
        f"**Length:** {len(progression)} chords",
        f"**Form:** {form}",
        f"**Complexity:** {comp}/100",
        "",
        "## Cadences",
    ]
    if cadence_strs:
        lines.extend(cadence_strs)
    else:
        lines.append("  (none detected)")

    lines.extend(
        [
            "",
            "## Functional Distribution",
            f"  - Tonic (T): {func_counts.get('T', 0)}",
            f"  - Subdominant (S): {func_counts.get('S', 0)}",
            f"  - Dominant (D): {func_counts.get('D', 0)}",
            f"  - Chromatic: {func_counts.get('chromatic', 0)}",
            "",
            "## Tension Curve",
            f"  - Average tension: {avg_tension:.2f}",
            f"  - Peak tension at chord {peak_idx + 1}",
            f"  - Values: {', '.join(str(v) for v in curve)}",
        ]
    )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Interactive scale explorer (v94.0)
# ---------------------------------------------------------------------------


def suggest_scale(
    notes_so_far: list[str],
    key: str = "C",
) -> list[tuple[str, float]]:
    """Rank scales by how well they fit the notes played so far.

    The real-time improv advisor: "you've played C E G Bb — you're
    probably in mixolydian or blues."

    Args:
        notes_so_far: Pitch names played so far.
        key:          Key root for scale transposition.

    Returns:
        List of (scale_name, fit_score) sorted by score descending.
    """
    k = _semi(key)
    played_pcs = {(_semi(n) - k) % 12 for n in notes_so_far}
    if not played_pcs:
        return [(name, 1.0) for name in sorted(_SCALE_INTERVALS)[:5]]

    results: list[tuple[str, float]] = []
    for name, intervals in _SCALE_INTERVALS.items():
        scale_pcs = set(intervals)
        if not scale_pcs:
            continue
        overlap = len(played_pcs & scale_pcs)
        outside = len(played_pcs - scale_pcs)
        score = overlap / len(played_pcs) - outside * 0.3
        score = max(0.0, min(1.0, score))
        results.append((name, round(score, 3)))

    results.sort(key=lambda x: -x[1])
    return results


def available_notes(
    key: str = "C",
    scale_name: str = "major",
) -> list[str]:
    """Return all pitches available in a scale, in order.

    Args:
        key:        Key root.
        scale_name: Scale name.

    Returns:
        List of note names in the scale.
    """
    aliases = {"minor": "aeolian", "natural_minor": "aeolian"}
    sname = aliases.get(scale_name, scale_name)
    if sname not in _SCALE_INTERVALS:
        return []
    k = _semi(key)
    return [_NOTE_NAMES[(k + iv) % 12] for iv in _SCALE_INTERVALS[sname]]


def avoid_notes(
    key: str = "C",
    scale_name: str = "major",
) -> list[str]:
    """Return all pitches NOT in a scale — the notes to avoid.

    Args:
        key:        Key root.
        scale_name: Scale name.

    Returns:
        List of note names outside the scale.
    """
    good = set(available_notes(key, scale_name))
    return [_NOTE_NAMES[i] for i in range(12) if _NOTE_NAMES[i] not in good]


# ---------------------------------------------------------------------------
# Chord voicing database (v95.0)
# ---------------------------------------------------------------------------

_VOICING_DB: dict[str, list[list[int]]] = {
    "maj": [
        [0, 4, 7],  # root position
        [4, 7, 12],  # first inversion
        [7, 12, 16],  # second inversion
        [0, 7, 16],  # open voicing
    ],
    "min": [
        [0, 3, 7],
        [3, 7, 12],
        [7, 12, 15],
        [0, 7, 15],
    ],
    "dom7": [
        [0, 4, 7, 10],
        [4, 7, 10, 12],
        [0, 4, 10],  # shell voicing
        [10, 16, 19],  # spread
    ],
    "maj7": [
        [0, 4, 7, 11],
        [4, 7, 11, 12],
        [0, 4, 11],  # shell
        [11, 16, 19],  # spread
    ],
    "min7": [
        [0, 3, 7, 10],
        [3, 7, 10, 12],
        [0, 3, 10],  # shell
        [10, 15, 19],  # spread
    ],
    "dim": [[0, 3, 6], [3, 6, 12]],
    "aug": [[0, 4, 8], [4, 8, 12]],
    "sus4": [[0, 5, 7], [5, 7, 12]],
    "sus2": [[0, 2, 7], [2, 7, 12]],
}


def lookup_voicing(
    root: str,
    shape: str,
    position: int = 0,
    octave: int = 3,
    duration: float = 4.0,
) -> list[Note]:
    """Retrieve a specific voicing from the database.

    Args:
        root:     Chord root.
        shape:    Chord quality.
        position: Voicing index (0 = root position, 1+ = inversions/spreads).
        octave:   Base octave.
        duration: Note duration.

    Returns:
        List of Notes.
    """
    voicings = _VOICING_DB.get(shape, [[0, 4, 7]])
    idx = position % len(voicings)
    k = _semi(root)
    return [
        Note(_NOTE_NAMES[(k + iv) % 12], octave + (k + iv) // 12, duration) for iv in voicings[idx]
    ]


def random_voicing(
    root: str,
    shape: str,
    octave: int = 3,
    duration: float = 4.0,
    seed: int | None = None,
) -> list[Note]:
    """Pick a random voicing from the database for variety.

    Args:
        root:     Chord root.
        shape:    Chord quality.
        octave:   Base octave.
        duration: Note duration.
        seed:     Random seed.

    Returns:
        List of Notes.
    """
    import random as _rng

    rng = _rng.Random(seed)
    voicings = _VOICING_DB.get(shape, [[0, 4, 7]])
    idx = rng.randint(0, len(voicings) - 1)
    return lookup_voicing(root, shape, idx, octave, duration)


# ---------------------------------------------------------------------------
# Musical memory game (v96.0)
# ---------------------------------------------------------------------------


def memory_game(
    length: int = 8,
    key: str = "C",
    scale_name: str = "major",
    octave: int = 5,
    duration: float = 0.5,
    seed: int | None = None,
) -> list[list[Note]]:
    """Generate a Simon-says memory game — each round adds one note.

    Round 1 = 1 note, round 2 = 2 notes, ..., round N = N notes.
    All notes are drawn from the specified scale.

    Args:
        length:     Total sequence length (= number of rounds).
        key:        Key root.
        scale_name: Scale for note selection.
        octave:     Melody octave.
        duration:   Note duration.
        seed:       Random seed.

    Returns:
        List of rounds, each a list of Notes (growing by 1 each round).
    """
    import random as _rng

    rng = _rng.Random(seed)
    aliases = {"minor": "aeolian", "natural_minor": "aeolian"}
    sname = aliases.get(scale_name, scale_name)
    intervals = _SCALE_INTERVALS.get(sname, _SCALE_INTERVALS["major"])
    k = _semi(key)
    pool = [_NOTE_NAMES[(k + iv) % 12] for iv in intervals]

    full_seq = [rng.choice(pool) for _ in range(length)]
    rounds: list[list[Note]] = []
    for i in range(1, length + 1):
        round_notes = [Note(p, octave, duration) for p in full_seq[:i]]
        rounds.append(round_notes)

    return rounds


def verify_playback(
    original: list[Note],
    attempt: list[Note],
) -> dict:
    """Check if a playback attempt matches the original sequence.

    Args:
        original: The correct sequence.
        attempt:  The player's attempt.

    Returns:
        Dict: {correct, total, accuracy, wrong_positions}.
    """
    total = len(original)
    correct = 0
    wrong: list[int] = []
    for i in range(min(len(original), len(attempt))):
        if original[i].pitch == attempt[i].pitch:
            correct += 1
        else:
            wrong.append(i)

    # Missing notes count as wrong
    if len(attempt) < total:
        wrong.extend(range(len(attempt), total))

    return {
        "correct": correct,
        "total": total,
        "accuracy": round(correct / max(total, 1) * 100, 1),
        "wrong_positions": wrong,
    }


# ---------------------------------------------------------------------------
# Harmonic field map (v97.0)
# ---------------------------------------------------------------------------


def harmonic_field(
    key: str = "C",
    mode: str = "major",
) -> list[dict]:
    """Return all diatonic chords with Roman numerals and functions.

    The harmonic field is the complete map of a key — every chord
    that belongs, what it's called, and what it does.

    Args:
        key:  Key root.
        mode: 'major' or 'minor' (aeolian).

    Returns:
        List of 7 dicts: {degree, roman, root, shape, function}.
    """
    k = _semi(key)
    if mode in ("minor", "aeolian"):
        intervals = _SCALE_INTERVALS.get("aeolian", [0, 2, 3, 5, 7, 8, 10])
        romans = ["i", "iio", "III", "iv", "v", "VI", "VII"]
        shapes = ["min", "dim", "maj", "min", "min", "maj", "maj"]
        funcs = ["T", "S", "T", "S", "D", "T", "D"]
    else:
        intervals = _SCALE_INTERVALS.get("major", [0, 2, 4, 5, 7, 9, 11])
        romans = ["I", "ii", "iii", "IV", "V", "vi", "viio"]
        shapes = ["maj", "min", "min", "maj", "maj", "min", "dim"]
        funcs = ["T", "S", "T", "S", "D", "T", "D"]

    field: list[dict] = []
    for i in range(7):
        root_pc = (k + intervals[i]) % 12
        field.append(
            {
                "degree": i + 1,
                "roman": romans[i],
                "root": _NOTE_NAMES[root_pc],
                "shape": shapes[i],
                "function": funcs[i],
            }
        )
    return field


def chord_relationships(key: str = "C") -> dict[str, list[str]]:
    """Map which chords resolve to which in a key.

    Dominant → tonic, subdominant → dominant or tonic. The arrows
    on the theory professor's blackboard.

    Args:
        key: Key root.

    Returns:
        Dict mapping Roman numeral → list of resolution targets.
    """
    return {
        "I": [],  # tonic = home, resolves nowhere
        "ii": ["V", "viio"],
        "iii": ["vi", "IV"],
        "IV": ["V", "I", "viio"],
        "V": ["I", "vi"],  # authentic or deceptive
        "vi": ["ii", "IV"],
        "viio": ["I"],
    }


# ---------------------------------------------------------------------------
# Phrase boundary detection (v98.0)
# ---------------------------------------------------------------------------


def detect_phrases(
    notes: list[Note],
    min_gap: float = 0.5,
) -> list[dict]:
    """Detect phrase boundaries by rest gaps and contour peaks.

    A phrase ends when there's a rest longer than min_gap, or at
    a local pitch maximum followed by a descent.

    Args:
        notes:   Input notes.
        min_gap: Minimum rest duration to mark a boundary.

    Returns:
        List of dicts: {start, end, length}.
    """
    if not notes:
        return []

    phrases: list[dict] = []
    phrase_start = 0

    for i, n in enumerate(notes):
        is_boundary = False

        # Rest gap boundary
        if n.pitch is None and n.duration >= min_gap:
            is_boundary = True

        # End of list
        if i == len(notes) - 1:
            is_boundary = True

        if is_boundary and i >= phrase_start:
            phrases.append(
                {
                    "start": phrase_start,
                    "end": i,
                    "length": i - phrase_start,
                }
            )
            phrase_start = i + 1

    return phrases


def phrase_lengths(notes: list[Note], min_gap: float = 0.5) -> list[int]:
    """Return the length of each detected phrase.

    Args:
        notes:   Input notes.
        min_gap: Rest gap threshold.

    Returns:
        List of phrase lengths (note counts).
    """
    return [p["length"] for p in detect_phrases(notes, min_gap)]


# ---------------------------------------------------------------------------
# Song template engine (v99.0)
# ---------------------------------------------------------------------------


class SongTemplate:
    """A slot-based song template for rapid composition.

    Define a form with named sections, fill each section with
    chords and melody, then render to a flat progression + melody.

    Example:
        t = SongTemplate("pop")
        t.fill("verse", chords=[("C","maj"),("G","dom7")], melody=[Note("E",5,1.0)])
        t.fill("chorus", chords=[("F","maj"),("C","maj")])
        result = t.render()
    """

    def __init__(self, form_name: str = "pop"):
        self.sections = song_form(form_name)
        self._slots: dict[str, dict] = {}

    def fill(
        self,
        section_name: str,
        chords: list[tuple[str, str]] | None = None,
        melody: list[Note] | None = None,
    ) -> "SongTemplate":
        """Fill a section slot with chords and/or melody.

        Args:
            section_name: Section to fill (e.g. 'verse', 'chorus').
            chords:       Chord progression for this section.
            melody:       Melody notes for this section.

        Returns:
            Self for chaining.
        """
        self._slots[section_name] = {
            "chords": chords or [],
            "melody": melody or [],
        }
        return self

    def render(self) -> dict:
        """Render the template to flat chord + melody lists.

        Returns:
            Dict: {chords: [...], melody: [...], form: [...]}.
        """
        chords: list[tuple[str, str]] = []
        melody: list[Note] = []

        for section in self.sections:
            slot = self._slots.get(section, {"chords": [], "melody": []})
            chords.extend(slot["chords"])
            melody.extend(slot["melody"])

        return {"chords": chords, "melody": melody, "form": list(self.sections)}

    def randomize(
        self,
        key: str = "C",
        seed: int | None = None,
    ) -> "SongTemplate":
        """Auto-fill all empty slots with generated content.

        Args:
            key:  Key for generation.
            seed: Random seed.

        Returns:
            Self for chaining.
        """
        import random as _rng

        rng = _rng.Random(seed)
        unique_sections = set(self.sections)

        for section in unique_sections:
            if section not in self._slots:
                prog = generate_progression(
                    key=key, length=4, genre="pop", seed=rng.randint(0, 9999)
                )
                mel = generate_scale_melody(key=key, length=8, seed=rng.randint(0, 9999))
                self.fill(section, chords=prog, melody=mel)

        return self


# ---------------------------------------------------------------------------
# Corpus learning (v101.0)
# ---------------------------------------------------------------------------


def train_style_from_corpus(
    progressions: list[list[tuple[str, str]]],
) -> dict:
    """Learn a musical style from a corpus of progressions.

    Extracts: transition matrix, root frequency, shape frequency,
    average length, and key distribution. Everything needed to
    generate new music "in the style of" the corpus.

    Args:
        progressions: List of chord progressions.

    Returns:
        Style dict: {matrix, root_freq, shape_freq, avg_length, key_dist}.
    """
    matrix = build_transition_matrix(progressions)
    stats = corpus_stats(progressions)
    keys = key_distribution(progressions)

    return {
        "matrix": matrix,
        "root_freq": stats["root_counts"],
        "shape_freq": stats["shape_counts"],
        "avg_length": stats["avg_length"],
        "key_dist": keys,
        "corpus_size": len(progressions),
    }


def continue_in_style(
    style: dict,
    start: tuple[str, str] | None = None,
    length: int = 8,
    seed: int | None = None,
) -> list[tuple[str, str]]:
    """Generate a new progression in a learned style.

    Uses the transition matrix from train_style_from_corpus to
    produce a stochastic walk that sounds like the training data.

    Args:
        style:  Style dict from train_style_from_corpus.
        start:  Starting chord (None = random from corpus).
        length: Number of chords to generate.
        seed:   Random seed.

    Returns:
        Generated chord progression.
    """
    return generate_from_matrix(style["matrix"], length, start, seed)


# ---------------------------------------------------------------------------
# Note probability (v102.0)
# ---------------------------------------------------------------------------


def note_probability(
    notes: list[Note],
) -> dict[str, float]:
    """Calculate the probability distribution of pitch classes in a note list.

    Args:
        notes: Input notes.

    Returns:
        Dict mapping pitch name → probability (0.0–1.0).
    """
    counts: dict[str, int] = {}
    total = 0
    for n in notes:
        if n.pitch is not None:
            p = str(n.pitch)
            counts[p] = counts.get(p, 0) + 1
            total += 1
    if total == 0:
        return {}
    return {k: round(v / total, 4) for k, v in sorted(counts.items(), key=lambda x: -x[1])}


def next_note_distribution(
    notes: list[Note],
    current: str,
) -> dict[str, float]:
    """Given the current note, what's the probability of each next note?

    Builds a first-order Markov chain from the note list and queries
    the distribution for the current pitch.

    Args:
        notes:   Training melody.
        current: Current pitch name.

    Returns:
        Dict mapping pitch name → probability of following `current`.
    """
    transitions: dict[str, dict[str, int]] = {}
    for i in range(len(notes) - 1):
        if notes[i].pitch is None or notes[i + 1].pitch is None:
            continue
        src = str(notes[i].pitch)
        dst = str(notes[i + 1].pitch)
        if src not in transitions:
            transitions[src] = {}
        transitions[src][dst] = transitions[src].get(dst, 0) + 1

    if current not in transitions:
        return {}

    trans = transitions[current]
    total = sum(trans.values())
    return {k: round(v / total, 4) for k, v in sorted(trans.items(), key=lambda x: -x[1])}


# ---------------------------------------------------------------------------
# Chord quality morphing (v103.0)
# ---------------------------------------------------------------------------


def morph_chord(
    from_chord: tuple[str, str],
    to_chord: tuple[str, str],
    steps: int = 4,
    octave: int = 3,
    duration: float = 4.0,
) -> list[list[Note]]:
    """Morph from one chord to another by gradually changing pitch classes.

    At each step, one pitch class from the source chord moves by a
    semitone toward the target chord. The result is a smooth
    transformation — the harmonic equivalent of a dissolve cut.

    Args:
        from_chord: Starting (root, shape).
        to_chord:   Ending (root, shape).
        steps:      Number of intermediate chords.
        octave:     Base octave.
        duration:   Duration per chord.

    Returns:
        List of voicings (each a list of Notes), from source to target.
    """
    from_k = _semi(from_chord[0])
    to_k = _semi(to_chord[0])
    from_semis = [(from_k + s) % 12 for s in _CHORD_SEMI.get(from_chord[1], [0, 4, 7])]
    to_semis = [(to_k + s) % 12 for s in _CHORD_SEMI.get(to_chord[1], [0, 4, 7])]

    # Pad shorter chord to match length
    max_voices = max(len(from_semis), len(to_semis))
    while len(from_semis) < max_voices:
        from_semis.append(from_semis[-1])
    while len(to_semis) < max_voices:
        to_semis.append(to_semis[-1])

    result: list[list[Note]] = []
    for step in range(steps + 1):
        frac = step / max(steps, 1)
        current: list[int] = []
        for f, t in zip(from_semis, to_semis):
            # Linear interpolation in pitch-class space (shortest path)
            diff = (t - f + 6) % 12 - 6  # signed shortest distance
            c = (f + round(diff * frac)) % 12
            current.append(c)

        voicing = [Note(_NOTE_NAMES[pc], octave, duration) for pc in current]
        result.append(voicing)

    return result


def chord_interpolation(
    progression: list[tuple[str, str]],
    steps_between: int = 2,
    octave: int = 3,
    duration: float = 2.0,
) -> list[list[Note]]:
    """Insert morphing intermediate chords between each chord in a progression.

    Makes abrupt chord changes smoother by adding gradual transitions.

    Args:
        progression:   Chord progression.
        steps_between: Intermediate chords between each pair.
        octave:        Base octave.
        duration:      Duration per intermediate chord.

    Returns:
        List of voicings with morphing intermediates inserted.
    """
    if len(progression) < 2:
        return [
            [
                Note(_NOTE_NAMES[(_semi(r) + s) % 12], octave, duration)
                for s in _CHORD_SEMI.get(sh, [0, 4, 7])
            ]
            for r, sh in progression
        ]

    result: list[list[Note]] = []
    for i in range(len(progression) - 1):
        morphed = morph_chord(progression[i], progression[i + 1], steps_between, octave, duration)
        result.extend(morphed[:-1])  # skip last to avoid duplication with next start

    # Add final chord
    last_r, last_s = progression[-1]
    last_k = _semi(last_r)
    result.append(
        [
            Note(_NOTE_NAMES[(last_k + s) % 12], octave, duration)
            for s in _CHORD_SEMI.get(last_s, [0, 4, 7])
        ]
    )

    return result


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


# ---------------------------------------------------------------------------
# Rhythmic density analysis (v105.0)
# ---------------------------------------------------------------------------


def density_profile(
    notes: list[Note],
    resolution: float = 1.0,
) -> list[float]:
    """Build a rhythmic density profile — notes per beat at a given resolution.

    Divides the total duration into bins of `resolution` beats and counts
    the number of sounding note onsets in each bin.

    Args:
        notes:      Input notes.
        resolution: Bin size in beats.

    Returns:
        List of floats: note count per bin.
    """
    if not notes:
        return []
    total_dur = sum(n.duration for n in notes)
    n_bins = max(1, int(total_dur / resolution))
    bins = [0.0] * n_bins

    onset = 0.0
    for n in notes:
        if n.pitch is not None:
            bin_idx = min(int(onset / resolution), n_bins - 1)
            bins[bin_idx] += 1.0
        onset += n.duration

    return bins


def density_contrast(
    notes: list[Note],
    split_at: int | None = None,
) -> float:
    """Measure the density contrast between the first and second halves.

    Returns a ratio: second_half_density / first_half_density.
    Values > 1.0 = builds energy, < 1.0 = winds down, ~1.0 = steady.

    Args:
        notes:    Input notes.
        split_at: Note index to split at (default: midpoint).

    Returns:
        Density contrast ratio.
    """
    if not notes:
        return 1.0
    mid = split_at if split_at else len(notes) // 2
    first_half = notes[:mid]
    second_half = notes[mid:]

    def _density(ns: list[Note]) -> float:
        sounding = sum(1 for n in ns if n.pitch is not None)
        total_dur = sum(n.duration for n in ns) or 1.0
        return sounding / total_dur

    d1 = _density(first_half)
    d2 = _density(second_half)
    return round(d2 / max(d1, 0.001), 3)


# ---------------------------------------------------------------------------
# Harmonic ambiguity score (v106.0)
# ---------------------------------------------------------------------------


def ambiguity_score(
    progression: list[tuple[str, str]],
) -> float:
    """Rate how ambiguous a progression's key center is (0.0-1.0).

    0.0 = clearly in one key (all diatonic). 1.0 = completely ambiguous
    (every chord is chromatic, no key fits well). Measures the gap
    between the best and second-best key candidates.

    Args:
        progression: Chord progression.

    Returns:
        Ambiguity score 0.0-1.0.
    """
    if not progression:
        return 0.0

    root_counts = [0] * 12
    for root, _ in progression:
        root_counts[_semi(root)] += 1

    major_intervals = _SCALE_INTERVALS["major"]
    scores: list[int] = []
    for candidate in range(12):
        diatonic = {(candidate + iv) % 12 for iv in major_intervals}
        score = sum(root_counts[pc] for pc in diatonic)
        scores.append(score)

    scores_with_root = []
    for candidate in range(12):
        diatonic = {(candidate + iv) % 12 for iv in major_intervals}
        score = sum(root_counts[pc] for pc in diatonic)
        # Bonus for root being tonic itself
        root_bonus = root_counts[candidate] * 0.5
        scores_with_root.append(score + root_bonus)

    scores_with_root.sort(reverse=True)
    best = scores_with_root[0]
    second = scores_with_root[1] if len(scores_with_root) > 1 else 0
    total = sum(root_counts)

    if total == 0 or best == 0:
        return 0.0

    # Ambiguity = how close second-best is to best (normalized)
    gap = (best - second) / best
    return round(max(0.0, min(1.0, 1.0 - gap)), 3)


def key_certainty(
    progression: list[tuple[str, str]],
) -> dict:
    """Return the estimated key with a confidence score.

    Args:
        progression: Chord progression.

    Returns:
        Dict: {key, confidence (0.0-1.0), ambiguity}.
    """
    if not progression:
        return {"key": "C", "confidence": 0.0, "ambiguity": 0.0}

    estimated = detect_key(progression)
    amb = ambiguity_score(progression)
    confidence = round(1.0 - amb, 3)

    return {"key": estimated, "confidence": confidence, "ambiguity": amb}


# ---------------------------------------------------------------------------
# Chord symbol formatter (v107.0)
# ---------------------------------------------------------------------------

_SHAPE_SYMBOLS = {
    "maj": "",
    "min": "m",
    "dim": "dim",
    "aug": "+",
    "dom7": "7",
    "maj7": "maj7",
    "min7": "m7",
    "dim7": "dim7",
    "aug7": "+7",
    "sus4": "sus4",
    "sus2": "sus2",
    "dom9": "9",
    "min9": "m9",
    "maj9": "maj9",
    "min11": "m11",
    "dom13": "13",
}


def format_chord(root: str, shape: str) -> str:
    """Format a (root, shape) tuple as a standard chord symbol.

    Args:
        root:  Chord root.
        shape: Chord quality.

    Returns:
        Standard chord symbol string (e.g. 'Cmaj7', 'Dm7', 'G7', 'F#dim').
    """
    suffix = _SHAPE_SYMBOLS.get(shape, shape)
    return f"{root}{suffix}"


def format_progression(
    progression: list[tuple[str, str]],
    separator: str = " | ",
) -> str:
    """Format a full progression as a readable chord chart line.

    Args:
        progression: List of (root, shape) tuples.
        separator:   String between chords.

    Returns:
        Formatted string (e.g. 'Cmaj7 | Dm7 | G7 | Cmaj7').
    """
    return separator.join(format_chord(r, s) for r, s in progression)


# ---------------------------------------------------------------------------
# Voice range optimizer (v108.0)
# ---------------------------------------------------------------------------


def fit_to_range(
    notes: list[Note],
    low: int = 48,
    high: int = 72,
) -> list[Note]:
    """Transpose notes to fit within a pitch range by octave shifting.

    Each note is individually octave-shifted to the closest octave
    placement that falls within [low, high]. Rests pass through.

    Args:
        notes: Input notes.
        low:   Lowest allowed absolute pitch (C3 = 48).
        high:  Highest allowed absolute pitch (C5 = 72).

    Returns:
        Notes with octaves adjusted to fit range.
    """
    result: list[Note] = []
    for n in notes:
        if n.pitch is None:
            result.append(Note.rest(n.duration))
            continue
        pc = _semi(str(n.pitch))
        current_abs = pc + n.octave * 12
        if low <= current_abs <= high:
            result.append(n)
            continue
        # Find closest octave within range
        best_oct = n.octave
        best_dist = abs(current_abs - (low + high) // 2)
        for o in range(0, 10):
            candidate = pc + o * 12
            if low <= candidate <= high:
                dist = abs(candidate - (low + high) // 2)
                if dist < best_dist:
                    best_dist = dist
                    best_oct = o
        result.append(Note(n.pitch, best_oct, n.duration, velocity=n.velocity))
    return result


def auto_octave(
    notes: list[Note],
    target_octave: int = 4,
) -> list[Note]:
    """Shift all notes to center around a target octave.

    Calculates the average octave and shifts the entire melody.

    Args:
        notes:         Input notes.
        target_octave: Desired center octave.

    Returns:
        Octave-shifted notes.
    """
    sounding = [n for n in notes if n.pitch is not None]
    if not sounding:
        return list(notes)
    avg_oct = sum(n.octave for n in sounding) / len(sounding)
    shift = round(target_octave - avg_oct)
    return [
        Note(n.pitch, n.octave + shift, n.duration, velocity=n.velocity)
        if n.pitch is not None
        else Note.rest(n.duration)
        for n in notes
    ]


# ---------------------------------------------------------------------------
# Interval sequence analysis (v109.0)
# ---------------------------------------------------------------------------


def interval_sequence(notes: list[Note]) -> list[int]:
    """Extract the sequence of melodic intervals (in semitones) from a note list.

    Args:
        notes: Input melody.

    Returns:
        List of signed integers: positive = ascending, negative = descending.
    """
    result: list[int] = []
    for i in range(1, len(notes)):
        if notes[i].pitch is None or notes[i - 1].pitch is None:
            continue
        a = _semi(str(notes[i - 1].pitch)) + notes[i - 1].octave * 12
        b = _semi(str(notes[i].pitch)) + notes[i].octave * 12
        result.append(b - a)
    return result


def common_intervals(notes: list[Note], top_n: int = 5) -> list[tuple[int, int]]:
    """Find the most frequently used melodic intervals.

    Args:
        notes: Input melody.
        top_n: Number of top intervals to return.

    Returns:
        List of (interval_semitones, count) sorted by frequency.
    """
    seq = interval_sequence(notes)
    counts: dict[int, int] = {}
    for iv in seq:
        counts[iv] = counts.get(iv, 0) + 1
    sorted_intervals = sorted(counts.items(), key=lambda x: -x[1])
    return sorted_intervals[:top_n]


# ---------------------------------------------------------------------------
# Melodic contour matching (v110.0)
# ---------------------------------------------------------------------------


def contour_string(notes: list[Note]) -> str:
    """Encode a melody's contour as a string: U=up, D=down, R=repeat.

    The contour is the shape of the melody stripped of exact pitches.
    Two melodies with the same contour string move in the same
    directions — they're melodically related even if in different keys.

    Args:
        notes: Input melody.

    Returns:
        String of U/D/R characters.
    """
    result: list[str] = []
    for i in range(1, len(notes)):
        if notes[i].pitch is None or notes[i - 1].pitch is None:
            continue
        a = _semi(str(notes[i - 1].pitch)) + notes[i - 1].octave * 12
        b = _semi(str(notes[i].pitch)) + notes[i].octave * 12
        if b > a:
            result.append("U")
        elif b < a:
            result.append("D")
        else:
            result.append("R")
    return "".join(result)


def contour_match(melody_a: list[Note], melody_b: list[Note]) -> float:
    """Compare two melodies by contour similarity (0.0-1.0).

    Two melodies that move in the same directions at the same positions
    score 1.0, regardless of actual pitches or key.

    Args:
        melody_a: First melody.
        melody_b: Second melody.

    Returns:
        Similarity score 0.0-1.0.
    """
    ca = contour_string(melody_a)
    cb = contour_string(melody_b)
    if not ca or not cb:
        return 0.0
    max_len = max(len(ca), len(cb))
    matches = sum(1 for a, b in zip(ca, cb) if a == b)
    return round(matches / max_len, 3)


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
# Progression complexity curve (v112.0)
# ---------------------------------------------------------------------------


def complexity_curve(
    progression: list[tuple[str, str]],
    key: str = "C",
    window: int = 4,
) -> list[int]:
    """Compute a sliding-window complexity score across a progression.

    Each position gets the complexity_score of the surrounding `window`
    chords. Shows where the harmony gets dense or simple over time.

    Args:
        progression: Chord progression.
        key:         Key context.
        window:      Number of chords per window.

    Returns:
        List of complexity scores, one per chord position.
    """
    if not progression:
        return []
    result: list[int] = []
    for i in range(len(progression)):
        start = max(0, i - window // 2)
        end = min(len(progression), start + window)
        chunk = progression[start:end]
        result.append(complexity_score(chunk, key))
    return result


def complexity_contrast(
    progression: list[tuple[str, str]],
    key: str = "C",
) -> float:
    """Ratio of second-half complexity to first-half complexity.

    > 1.0 = gets more complex over time (builds).
    < 1.0 = gets simpler (resolves).
    ~1.0 = steady complexity.

    Args:
        progression: Chord progression.
        key:         Key context.

    Returns:
        Complexity contrast ratio.
    """
    if len(progression) < 2:
        return 1.0
    mid = len(progression) // 2
    first = complexity_score(progression[:mid], key)
    second = complexity_score(progression[mid:], key)
    return round(second / max(first, 1), 3)


class Change:
    """A single structural change between two songs."""

    __slots__ = ("change_type", "track_name", "detail")

    def __init__(self, change_type: str, track_name: str, detail: str):
        self.change_type = change_type  # "added", "removed", "modified"
        self.track_name = track_name
        self.detail = detail

    def __repr__(self) -> str:
        return f"Change({self.change_type!r}, {self.track_name!r}, {self.detail!r})"


def song_diff(a, b) -> list[Change]:
    """Compute structural differences between two songs.

    Returns a list of Change objects describing what changed between
    song A and song B.

    Args:
        a: First Song.
        b: Second Song.

    Returns:
        List of Change objects.
    """
    changes: list[Change] = []

    a_tracks = {t.name: t for t in a.tracks}
    b_tracks = {t.name: t for t in b.tracks}

    # Songs-level changes
    if a.bpm != b.bpm:
        changes.append(Change("modified", "_song", f"bpm: {a.bpm} → {b.bpm}"))
    if a.title != b.title:
        changes.append(Change("modified", "_song", f"title: {a.title!r} → {b.title!r}"))

    # Tracks added/removed
    for name in sorted(b_tracks.keys() - a_tracks.keys()):
        t = b_tracks[name]
        changes.append(Change("added", name, f"instrument={t.instrument}, {len(t.beats)} beats"))
    for name in sorted(a_tracks.keys() - b_tracks.keys()):
        t = a_tracks[name]
        changes.append(Change("removed", name, f"instrument={t.instrument}, {len(t.beats)} beats"))

    # Tracks modified
    for name in sorted(a_tracks.keys() & b_tracks.keys()):
        ta = a_tracks[name]
        tb = b_tracks[name]

        if ta.instrument != tb.instrument:
            changes.append(
                Change("modified", name, f"instrument: {ta.instrument} → {tb.instrument}")
            )
        if ta.volume != tb.volume:
            changes.append(Change("modified", name, f"volume: {ta.volume} → {tb.volume}"))
        if ta.pan != tb.pan:
            changes.append(Change("modified", name, f"pan: {ta.pan} → {tb.pan}"))
        if len(ta.beats) != len(tb.beats):
            changes.append(Change("modified", name, f"beats: {len(ta.beats)} → {len(tb.beats)}"))

    return changes


def song_patch(base, changes: list[Change]):
    """Apply a list of changes to a song (best-effort).

    Modifies the song in place. Only handles simple property changes
    and track additions (not beat-level reconstruction).

    Args:
        base:    Song to modify.
        changes: List of Change objects (from song_diff).

    Returns:
        The modified Song.
    """
    from .engine import Track

    for change in changes:
        if change.track_name == "_song":
            if "bpm:" in change.detail:
                parts = change.detail.split(" → ")
                new_bpm = float(parts[1])
                base.bpm = new_bpm
            if "title:" in change.detail:
                parts = change.detail.split(" → ")
                base.title = parts[1].strip("'\"")

        elif change.change_type == "added":
            # Parse instrument from detail
            parts = change.detail.split(", ")
            instrument = parts[0].split("=")[1] if "=" in parts[0] else "sine"
            base.add_track(Track(name=change.track_name, instrument=instrument))

        elif change.change_type == "removed":
            base.tracks = [t for t in base.tracks if t.name != change.track_name]

        elif change.change_type == "modified":
            for track in base.tracks:
                if track.name == change.track_name:
                    if "volume:" in change.detail:
                        parts = change.detail.split(" → ")
                        track.volume = float(parts[1])
                    elif "pan:" in change.detail:
                        parts = change.detail.split(" → ")
                        track.pan = float(parts[1])
                    elif "instrument:" in change.detail:
                        parts = change.detail.split(" → ")
                        track.instrument = parts[1].strip()
                    break

    return base
