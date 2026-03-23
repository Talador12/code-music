"""Ambient style profile.

Theory analysis of ambient and atmospheric music.
Artists: Brian Eno, Harold Budd, Stars of the Lid, Ólafur Arnalds,
Nils Frahm, Jon Hopkins, Moby (early), William Basinski, Tim Hecker.

What makes the sound:
  - Extended time. Notes sustain for many bars. Nothing rushes.
  - Texture over melody — the sound itself is the music.
  - Very little rhythmic structure. When rhythm exists, it's soft and subtle.
  - Modal harmony: notes and chords that don't pull toward resolution.
  - Reverb is not an effect here — it IS the sound. Everything is in a large space.
  - Deliberate use of silence and near-silence.
  - Notes that blur into each other through reverb tails.
  - Often just 1–3 elements total. Restraint is the technique.
"""

PROFILE = {
    "name": "Ambient / Atmospheric",
    "era": "1978–present",
    "bpm_range": (40, 80),
    "bpm_typical": 60,
    "scales": [
        "pentatonic",  # no tension — all notes harmonious
        "lydian",  # the 'floating' mode — #4 creates weightlessness
        "dorian",  # minor but open
        "whole_tone",  # completely unresolved — pure texture
        "major",  # can be ambient in context, with slow harmonic rhythm
    ],
    "keys": ["D", "G", "A", "E", "Dm", "Am"],  # open strings, resonant
    "chord_progressions": [
        # Two-chord drone: barely moves
        [("D", "min7", 3, 16), ("A", "sus2", 3, 16)],
        # Lydian float: Dmaj7 - A - Bm - G
        [("D", "maj7", 3, 8), ("A", "sus2", 3, 8), ("B", "min7", 3, 8), ("G", "maj7", 3, 8)],
        # Single sustained chord (Eno approach — one chord for the whole piece)
        [("D", "sus2", 3, 32)],
        # Sparse movement: four chords over 32 bars each
        [("A", "maj7", 3, 8), ("F#", "min7", 3, 8), ("D", "maj7", 3, 8), ("E", "sus4", 3, 8)],
    ],
    "instruments": {
        "piano": "piano",  # sparse, isolated notes
        "pad": "pad",  # slow-attack sustain — the core texture
        "harp": "harp",  # optional, sparse plucks
        "string": "strings",  # very quiet, pure sustain
        # No drums in pure ambient — maybe very quiet snare brush or
        # electronic clicks at low volume
    },
    "effects": {
        "piano": {
            "reverb": {"room_size": 0.85, "damping": 0.4, "wet": 0.45},
            "delay": {"delay_ms": 500.0, "feedback": 0.45, "wet": 0.3},
        },
        "pad": {
            "reverb": {"room_size": 0.9, "damping": 0.5, "wet": 0.5},
            "stereo_width": 1.9,  # very wide
            "chorus": {"rate_hz": 0.3, "wet": 0.15},
        },
        "harp": {
            "reverb": {"room_size": 0.8, "wet": 0.4},
            "delay": {"delay_ms": 750.0, "feedback": 0.4, "wet": 0.35},
        },
    },
    "rhythm": {
        "feel": "no fixed rhythm — events happen when they happen",
        "swing": 0.0,
        "pulse": "optional very quiet quarter or half-note pulse at most",
        "fill_density": "none",
        "note_timing": "irregular — notes placed intuitively, not on a grid",
    },
    "arrangement": {
        # Ambient has no structure — it's a continuous texture
        "single_section_bars": 64,  # ambient pieces are typically one long section
        "elements_count": 3,  # maximum 2-3 simultaneous elements
        "dynamics_range": "pp to mp only — never loud",
        "fade_in_bars": 16,  # gradual appearance
        "fade_out_bars": 16,  # gradual disappearance
    },
    "character": [
        "meditative",
        "spacious",
        "weightless",
        "introspective",
        "timeless",
        "quiet",
        "atmospheric",
        "dissolving",
    ],
    "notes": """
    The Eno approach:
    - 'Ambient music must be able to accommodate many levels of listening
      attention without enforcing one in particular.' — Brian Eno
    - The music should work as background AND as foreground listening.
    - Sparse: one note, played once, allowed to ring completely, is often
      more effective than five notes played quickly.
    - Reverb trails ARE the music. The decay of a piano note through 4 seconds
      of reverb is a musical event.
    - Use the delay to create self-generating patterns: feed a pad or piano
      into a long delay (750ms+) with high feedback. The pattern evolves on its own.

    Theory:
    - Avoid dominant 7th chords — they pull toward resolution and break the float.
    - Suspended chords (sus2, sus4) are perfect — no major/minor quality, ambiguous.
    - Lydian mode (#4) removes the tension of the natural 4th. Everything floats.
    - Pentatonic means every note works with every other note — pure consonance.
    - If using Dorian or minor, avoid the leading tone (major 7th) — it demands resolution.

    Mixing:
    - The reverb pre-delay matters: 0ms = notes blur immediately, 20ms = notes
      stay distinct briefly before washing out. Both are valid choices.
    - Stereo width on the pad: as wide as possible.
    - Very low in the frequency spectrum: sub frequencies are warm and grounding.
      High frequencies should be soft, not harsh.
    """,
}
