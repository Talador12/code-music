"""Rap flow and cadence patterns.

Generates syllable timing patterns inspired by different rap styles.
These are RHYTHMIC templates - they define when syllables land on the
beat, not what words are said. Use with VocalTrack to place text events
at musically appropriate positions.

Styles:
    boom_bap:    Classic 90s, laid-back pocket, emphasis on 2 and 4
    triplet:     Migos-style triplet flow, 3 syllables per beat
    double_time: Eminem-style rapid-fire, 2x syllable density
    laid_back:   Biggie-style behind-the-beat, relaxed timing
    syncopated:  Kendrick-style off-beat emphasis, unpredictable
    southern:    Wayne-style drawl, uneven syllable spacing

Example::

    from code_music.flow import generate_flow, apply_flow_to_lyrics

    # Get a 4-bar triplet flow pattern
    pattern = generate_flow("triplet", bars=4, bpm=140)

    # Apply lyrics to the pattern
    lyrics = ["verse one line one", "verse one line two", ...]
    events = apply_flow_to_lyrics(lyrics, pattern)
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class FlowBeat:
    """A single syllable position in a flow pattern.

    Attributes:
        beat:     Beat position (float, 0-indexed).
        duration: How long this syllable is held (in beats).
        emphasis: Accent strength (0.0-1.0). 1.0 = stressed syllable.
        rest:     If True, this is a rest (no syllable).
    """

    beat: float
    duration: float
    emphasis: float = 0.5
    rest: bool = False


def generate_flow(
    style: str = "boom_bap",
    bars: int = 4,
    bpm: int = 90,
    beats_per_bar: int = 4,
    seed: int | None = None,
) -> list[FlowBeat]:
    """Generate a rhythmic flow pattern for rap vocals.

    Returns a list of FlowBeats defining where syllables land relative
    to the beat grid. Does not generate words - just timing.

    Args:
        style:         Flow style name.
        bars:          Number of bars.
        bpm:           Tempo (affects feel but not positions).
        beats_per_bar: Beats per bar (default 4).
        seed:          Random seed for reproducibility.

    Returns:
        List of FlowBeat objects.

    Example::

        >>> pattern = generate_flow("triplet", bars=2, seed=42)
        >>> len(pattern) > 0
        True
    """
    rng = random.Random(seed)
    total_beats = bars * beats_per_bar
    pattern: list[FlowBeat] = []

    if style == "boom_bap":
        # Classic 90s: mostly on-beat, emphasis on 2 and 4, occasional 8th notes
        pos = 0.0
        while pos < total_beats:
            bar_beat = pos % beats_per_bar
            if rng.random() < 0.15:
                # Rest
                pattern.append(FlowBeat(beat=pos, duration=0.5, rest=True))
                pos += 0.5
            elif rng.random() < 0.3:
                # 8th note pair
                emph = 0.8 if bar_beat in (1, 3) else 0.5
                pattern.append(FlowBeat(beat=pos, duration=0.5, emphasis=emph))
                pos += 0.5
            else:
                emph = 0.9 if bar_beat in (1, 3) else 0.5
                pattern.append(FlowBeat(beat=pos, duration=1.0, emphasis=emph))
                pos += 1.0

    elif style == "triplet":
        # Migos-style: 3 syllables per beat
        pos = 0.0
        while pos < total_beats:
            if rng.random() < 0.1:
                pattern.append(FlowBeat(beat=pos, duration=1.0, rest=True))
                pos += 1.0
            else:
                for i in range(3):
                    emph = 0.8 if i == 0 else 0.4
                    pattern.append(
                        FlowBeat(
                            beat=pos + i / 3.0,
                            duration=1.0 / 3.0,
                            emphasis=emph,
                        )
                    )
                pos += 1.0

    elif style == "double_time":
        # Eminem-style: 16th notes with occasional breathers
        pos = 0.0
        while pos < total_beats:
            if rng.random() < 0.08:
                pattern.append(FlowBeat(beat=pos, duration=0.5, rest=True))
                pos += 0.5
            else:
                # Run of 16ths
                run_len = rng.choice([2, 3, 4, 4, 4])
                for i in range(run_len):
                    if pos + i * 0.25 >= total_beats:
                        break
                    emph = 0.7 if i % 2 == 0 else 0.4
                    pattern.append(
                        FlowBeat(
                            beat=pos + i * 0.25,
                            duration=0.25,
                            emphasis=emph,
                        )
                    )
                pos += run_len * 0.25

    elif style == "laid_back":
        # Biggie-style: behind the beat, relaxed, longer syllables
        pos = 0.0
        while pos < total_beats:
            # Swing: push notes slightly behind
            swing_offset = rng.uniform(0.05, 0.15)
            if rng.random() < 0.2:
                pattern.append(FlowBeat(beat=pos, duration=1.0, rest=True))
                pos += 1.0
            elif rng.random() < 0.4:
                # Long held syllable
                pattern.append(
                    FlowBeat(
                        beat=pos + swing_offset,
                        duration=1.5,
                        emphasis=0.7,
                    )
                )
                pos += 1.5
            else:
                pattern.append(
                    FlowBeat(
                        beat=pos + swing_offset,
                        duration=1.0,
                        emphasis=0.6,
                    )
                )
                pos += 1.0

    elif style == "syncopated":
        # Kendrick-style: off-beat emphasis, rhythmic surprises
        pos = 0.0
        while pos < total_beats:
            r = rng.random()
            if r < 0.1:
                pattern.append(FlowBeat(beat=pos, duration=0.5, rest=True))
                pos += 0.5
            elif r < 0.3:
                # Off-beat 8th
                pattern.append(
                    FlowBeat(
                        beat=pos + 0.5,
                        duration=0.5,
                        emphasis=0.9,
                    )
                )
                pos += 1.0
            elif r < 0.5:
                # Dotted rhythm
                pattern.append(FlowBeat(beat=pos, duration=0.75, emphasis=0.7))
                pattern.append(FlowBeat(beat=pos + 0.75, duration=0.25, emphasis=0.5))
                pos += 1.0
            else:
                pattern.append(FlowBeat(beat=pos, duration=0.5, emphasis=0.6))
                pos += 0.5

    elif style == "southern":
        # Wayne-style: drawl, uneven spacing, emphasis on last syllable of phrase
        pos = 0.0
        phrase_count = 0
        while pos < total_beats:
            # Phrases of 3-6 syllables
            phrase_len = rng.randint(3, 6)
            for i in range(phrase_len):
                if pos >= total_beats:
                    break
                dur = rng.choice([0.5, 0.75, 1.0])
                emph = 0.9 if i == phrase_len - 1 else 0.5
                pattern.append(FlowBeat(beat=pos, duration=dur, emphasis=emph))
                pos += dur
            # Rest between phrases
            if pos < total_beats:
                rest_dur = rng.choice([0.5, 1.0])
                pattern.append(FlowBeat(beat=pos, duration=rest_dur, rest=True))
                pos += rest_dur
            phrase_count += 1
    else:
        # Default: straight 8ths
        pos = 0.0
        while pos < total_beats:
            pattern.append(FlowBeat(beat=pos, duration=0.5, emphasis=0.5))
            pos += 0.5

    return pattern


def apply_flow_to_lyrics(
    lines: list[str],
    pattern: list[FlowBeat],
) -> list[dict]:
    """Map lyric lines onto a flow pattern.

    Each line is assigned to a non-rest beat position. Returns a list of
    dicts suitable for VocalTrack.say() calls.

    Args:
        lines:   List of lyric lines (one phrase per line).
        pattern: Flow pattern from generate_flow().

    Returns:
        List of dicts with text, at_beat, duration_beats, emphasis.

    Example::

        >>> pattern = generate_flow("boom_bap", bars=4, seed=42)
        >>> events = apply_flow_to_lyrics(["yo", "check it"], pattern)
        >>> events[0]["text"]
        'yo'
    """
    active_beats = [fb for fb in pattern if not fb.rest]
    results = []

    for i, line in enumerate(lines):
        if i >= len(active_beats):
            break
        fb = active_beats[i]
        results.append(
            {
                "text": line,
                "at_beat": fb.beat,
                "duration_beats": fb.duration,
                "emphasis": fb.emphasis,
            }
        )

    return results


def flow_summary(style: str, bars: int = 4, seed: int = 42) -> dict:
    """Get a summary of a flow pattern.

    Returns:
        Dict with style, total_beats, syllable_count, rest_count,
        avg_duration, density (syllables per beat).
    """
    pattern = generate_flow(style, bars=bars, seed=seed)
    syllables = [fb for fb in pattern if not fb.rest]
    rests = [fb for fb in pattern if fb.rest]
    total_beats = bars * 4

    return {
        "style": style,
        "total_beats": total_beats,
        "syllable_count": len(syllables),
        "rest_count": len(rests),
        "avg_duration": (sum(fb.duration for fb in syllables) / max(len(syllables), 1)),
        "density": len(syllables) / max(total_beats, 1),
    }
