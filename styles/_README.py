"""styles/ — Musical style profiles.

Each file captures the *theory* behind a musical style: scales, chord
progressions, rhythmic patterns, BPM ranges, synth character, effect chains,
and arrangement structure. Nothing here is copyrighted — these are descriptions
of music theory choices, the same way a textbook describes jazz harmony.

How to use a profile in a song::

    from styles.progressive_house import PROFILE
    from code_music import Song, Track, Chord, Note

    song = Song(title="My Track", bpm=PROFILE["bpm_typical"])
    # Use PROFILE["chord_progressions"][0], PROFILE["scales"], etc.

Profile structure (every file follows this shape):

    PROFILE = {
        "name":             str,          # style name
        "era":              str,          # decade / period
        "bpm_range":        (int, int),   # typical BPM low/high
        "bpm_typical":      int,          # the sweet spot
        "scales":           [str, ...],   # scale modes that define the sound
        "keys":             [str, ...],   # keys this style gravitates toward
        "chord_progressions": [           # list of common progressions
            [(root, shape, bars), ...],   # one progression per entry
        ],
        "instruments": {                  # synth presets that nail the sound
            "bass":    str,
            "pad":     str,
            "lead":    str,
            "drums":   {kick, snare, hat, ...},
        },
        "effects": {                      # effect settings that define the character
            "pad":   {...},
            "lead":  {...},
        },
        "rhythm": {                       # rhythmic feel
            "kick_pattern":   str,        # description
            "swing":          float,      # 0.0 = straight, 0.5 = swung
            "hat_pattern":    str,
        },
        "arrangement": {                  # song structure tendencies
            "intro_bars":     int,
            "buildup_bars":   int,
            "drop_bars":      int,
            "breakdown_bars": int,
        },
        "character": [str, ...],          # adjectives describing the sound
        "notes":     str,                 # free-form theory notes
    }
"""
