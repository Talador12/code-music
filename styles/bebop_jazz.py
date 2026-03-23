"""Bebop jazz style profile.

Theory analysis of the bebop jazz genre (1940s–present).
Artists: Charlie Parker, Dizzy Gillespie, Thelonious Monk, Miles Davis,
John Coltrane, Sonny Rollins, Clifford Brown. Film/anime: Yoko Kanno /
The Seatbelts (Cowboy Bebop soundtrack — Tank!, Rain, etc.)

What makes the sound:
  - Fast tempos (160–280 BPM) with swung 8th notes.
  - Complex chord progressions: ii-V-I in multiple keys per bar.
  - Chromatic passing tones — notes outside the scale used as approach notes.
  - The bebop scale (dominant: Mixolydian + maj7 passing tone).
  - Unison melody between front-line instruments (trumpet + sax).
  - Walking bass: quarter notes, chord-tone oriented, chromatic approaches.
  - Drums: ride cymbal keeps time (not hi-hat), snare on 2 & 4 is optional.
  - Lots of space — silence is part of the vocabulary.
"""

PROFILE = {
    "name": "Bebop Jazz",
    "era": "1940s–present",
    "bpm_range": (160, 280),
    "bpm_typical": 220,  # "up tempo" bebop standard
    "scales": [
        "bebop_dominant",  # the core bebop vocabulary
        "bebop_major",
        "bebop_minor",
        "blues",  # blues inflections throughout
        "dorian",  # for ii chords
        "mixolydian",  # for V chords
        "super_locrian",  # altered scale on V7alt
    ],
    "keys": ["Bb", "F", "Eb", "Ab", "G", "C"],  # horn-friendly keys
    "chord_progressions": [
        # ii-V-I in Bb (the most common bebop move)
        [("C", "min7", 3, 1), ("F", "dom7", 3, 1), ("Bb", "maj7", 3, 2)],
        # Rhythm changes (I Got Rhythm): Bb - G7 - Cm7 - F7
        [("Bb", "maj7", 3, 1), ("G", "dom7", 3, 1), ("C", "min7", 3, 1), ("F", "dom7", 3, 1)],
        # Coltrane changes (Giant Steps): B - D7 - G - Bb7 - Eb
        [
            ("B", "maj7", 3, 1),
            ("D", "dom7", 3, 1),
            ("G", "maj7", 3, 1),
            ("Bb", "dom7", 3, 1),
            ("Eb", "maj7", 3, 2),
        ],
        # Minor ii-V-i: Dm7b5 - G7alt - Cm
        [("D", "min7", 3, 1), ("G", "dom7", 3, 1), ("C", "min7", 3, 2)],
        # Blues in Bb (12 bars):
        [
            ("Bb", "dom7", 3, 4),
            ("Eb", "dom7", 3, 2),
            ("Bb", "dom7", 3, 2),
            ("F", "dom7", 3, 1),
            ("Eb", "dom7", 3, 1),
            ("Bb", "dom7", 3, 2),
        ],
    ],
    "instruments": {
        "melody": "saxophone",  # lead melodic voice — or trumpet
        "comp": "rhodes",  # piano comp — sparse, shell voicings
        "bass": "contrabass",  # walking bass, quarter notes
        "drums": {
            "ride": "drums_ride",  # ride cymbal = the timekeeping voice
            "snare": "drums_snare",  # comping on snare, not just 2&4
            "kick": "drums_kick",  # sparse, accent only
            "hat": "drums_hat",  # hi-hat on 2 & 4 (foot)
        },
    },
    "effects": {
        "melody": {
            "reverb": {"room_size": 0.35, "wet": 0.12},  # small room — intimate
        },
        "comp": {
            "reverb": {"room_size": 0.3, "wet": 0.1},
            "chorus": {"rate_hz": 0.5, "wet": 0.08},
        },
        "bass": {
            "reverb": {"room_size": 0.3, "wet": 0.1},
        },
    },
    "rhythm": {
        "feel": "swung 8th notes — the triplet feel of jazz",
        "swing": 0.52,  # medium swing — triplet feel
        "ride_pattern": "swing pattern: quarter, 8th rest, 8th, repeat",
        "snare_pattern": "comping — reactive, not fixed",
        "kick_pattern": "accent only — no steady pattern",
        "bass_pattern": "walking: quarter notes, chord tones + chromatic approaches",
    },
    "arrangement": {
        # Jazz is typically: head → solos → head out
        "head_bars": 32,  # melody statement (AABA or 12-bar)
        "solo_choruses": 4,  # each soloist plays multiple choruses
        "head_out_bars": 32,  # melody restated
        "trading_bars": 4,  # optional: 4-bar trades between soloists
    },
    "character": [
        "sophisticated",
        "virtuosic",
        "swinging",
        "intellectual",
        "conversational",  # jazz is dialogue between instruments
        "spontaneous",
        "urban",
        "late-night",
    ],
    "notes": """
    The bebop vocabulary:
    - The bebop scale adds a chromatic passing tone so that chord tones fall
      on beats when playing 8th notes. This is why bebop melodies lock in.
    - ii-V-I is the fundamental unit: Cm7 - F7 - Bbmaj7. Everything else
      is elaboration, substitution, or extension of this.
    - Tritone substitution: replace F7 with B7. The tritone of F7 (C-Gb)
      = the tritone of B7 (F-B). Gives smooth half-step bass movement.
    - Coltrane substitutions: replace ii-V-I with a sequence of major chords
      a major third apart (Giant Steps / Countdown).
    - The altered scale (super_locrian) is used on V7alt chords: b9, #9, #11, b13.
    - Shell voicings for comp: 3rd and 7th only, no root (bass covers it).
      Add the 9th or 13th for colour.

    Tank! / Seatbelts style specifically:
    - Unison trumpet + sax on the head — very tight, very fast.
    - Aggressive rhythm section: the drums really push.
    - Brass stabs off the rhythm section.
    - Big band feel condensed into a smaller ensemble.
    - Blues inflections even in major keys.
    """,
}
