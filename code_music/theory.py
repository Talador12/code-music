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
