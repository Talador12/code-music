"""Progressive house style profile.

Theory analysis of the progressive house genre (early 2010s peak).
Artists working in this space: deadmau5, Eric Prydz, Feed Me, Wolfgang Gartner.

What makes the sound:
  - Patience. Loops evolve very slowly — a chord might sustain for 8+ bars
    before anything changes. The tension builds through filter automation,
    not new elements.
  - The LP filter sweep IS the drop. Nothing gets added; the filter opens.
  - Simple 4-chord loop repeated many, many times.
  - Kick is always 4-on-the-floor — never varies, never misses.
  - The bass is a simple root note, locked to the kick, not busy.
  - One lead idea, introduced late, developed slowly.
  - Lots of space. Silence between elements is intentional.
"""

PROFILE = {
    "name": "Progressive House",
    "era": "2008–2014",
    "bpm_range": (124, 132),
    "bpm_typical": 128,
    "scales": [
        "minor",  # the dominant choice — dark and slow-burning
        "dorian",  # minor with raised 6th — slightly less dark, more open
        "natural_minor",  # same as minor — Aeolian mode
    ],
    # These keys come up constantly in the genre
    "keys": ["F", "Fm", "Am", "Dm", "Gm", "Cm"],
    # Common chord progressions (root, shape, bars each)
    "chord_progressions": [
        # The classic deadmau5 loop: i → VI → III → VII
        [("F", "min7", 4), ("Db", "maj7", 4), ("Ab", "maj7", 4), ("Eb", "dom7", 4)],
        # Minor loop with sus chords for ambiguity
        [("A", "min7", 4), ("F", "maj7", 4), ("C", "maj", 4), ("G", "dom7", 4)],
        # Two-chord drone (very deadmau5 — just hangs on two chords)
        [("F", "min7", 8), ("Db", "maj7", 8)],
        # Four-chord with add9 for extra colour
        [("D", "min9", 4), ("Bb", "maj7", 4), ("F", "maj7", 4), ("C", "dom7", 4)],
    ],
    "instruments": {
        "bass": "bass",  # simple root note, sine or sawtooth, low and clean
        "pad": "supersaw",  # the defining sound — detuned saw wall
        "lead": "lead_edm",  # enters late, simple melodic idea
        "arp": "pluck",  # optional 16th-note arp over pad
        "drums": {
            "kick": "drums_kick",  # 4-on-the-floor, every beat, no variation
            "hat": "drums_hat",  # offbeat 8ths (or 16ths in builds)
            "snare": "drums_snare",  # 2 & 4 only, simple
            "clap": "drums_clap",  # sometimes replaces snare
        },
    },
    "effects": {
        "pad": {
            "reverb": {"room_size": 0.55, "wet": 0.2},
            "lfo_filter": {
                # The signature: filter slowly opens across the track
                "rate_hz": 0.005,  # extremely slow — one sweep per ~3 minutes
                "min_cutoff": 200.0,  # starts dark
                "max_cutoff": 8000.0,  # opens up at the drop
            },
            "stereo_width": 1.7,  # wide but not overwhelming
        },
        "lead": {
            "delay": {"delay_ms": 234.0, "feedback": 0.35, "ping_pong": True},
            "reverb": {"room_size": 0.5, "wet": 0.18},
        },
        "bass": {
            "compress": {"threshold": 0.5, "ratio": 4.0, "makeup_gain": 1.1},
        },
    },
    "rhythm": {
        "kick_pattern": "4-on-the-floor (every beat, all bars)",
        "bass_pattern": "root quarter note on 1, rest of bar",
        "hat_pattern": "offbeat 8th notes (2-and, 4-and)",
        "snare_pattern": "2 and 4 only",
        "swing": 0.0,  # straight — no swing in house
        "fill_density": "very low — fills only at major transitions",
    },
    "arrangement": {
        # Progressive house tracks are long — 8+ minute DJ versions
        "intro_bars": 16,  # kick alone, or pad alone
        "pad_enters": 8,  # pad comes in with filter closed
        "bass_enters": 16,  # bass enters with kick
        "build_bars": 32,  # long, patient buildup
        "drop_bars": 32,  # drop = filter opens, not new elements
        "breakdown_bars": 16,  # strip back to pad + maybe arp
        "second_drop_bars": 32,
        "outro_bars": 16,
    },
    "character": [
        "patient",
        "hypnotic",
        "minimal",
        "dark",
        "driving",
        "emotional",  # the lead melody is always emotional when it arrives
        "late-night",
        "cinematic",
    ],
    "notes": """
    The deadmau5 approach to arrangement:
    - The track earns its drop through patience. The listener waits 2+ minutes
      before the filter fully opens. When it does, it feels enormous.
    - The supersaw pad is the centre of gravity. Everything orbits it.
    - Filter automation (lfo_filter at very slow rate) is the primary
      progression tool — not chord changes.
    - The lead melody is simple: 4–8 notes, usually stepwise, often pentatonic.
      It enters only after the track has already established itself.
    - Mixing: the kick is always the loudest element. The pad sits just behind.
      The bass fills the sub below the kick. The lead floats above everything.
    - The breakdown strips everything back to pad + maybe arp. Silence before
      the second drop makes it hit harder.

    Key theory moves:
    - Minor 7th chords throughout — never fully resolving, always slightly tense.
    - The i → bVI → bIII → bVII progression (minor) is ubiquitous.
    - Avoid the 5th chord resolving to the 1st — that closure kills the loop feel.
    - Lydian and Dorian occasionally appear for brighter sections.
    """,
}
