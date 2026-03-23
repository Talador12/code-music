"""Big room electro / festival EDM style profile.

Theory analysis of the big room / electro house genre (2012–2016 peak).
Artists working in this space: Zedd, Hardwell, Martin Garrix, Tiësto (late era),
Avicii (melodic branch), Knife Party, Wolfgang Gartner.

What makes the sound:
  - Anthemic chord progressions that feel universal — i VI III VII in minor,
    or the same in relative major. Simple enough to sing, big enough to fill
    a stadium.
  - The drop is loud and immediate. No patience — build → bang.
  - Supersaw lead melody is the centrepiece. It earns the emotional peak.
  - Four-on-the-floor kick + punchy snare on 2 & 4.
  - Build-ups use noise sweeps, reverse cymbals, rising pitch.
  - Everything is maximised: stereo width, reverb, sidechain pump.
"""

PROFILE = {
    "name": "Big Room Electro / Festival EDM",
    "era": "2012–2016",
    "bpm_range": (126, 132),
    "bpm_typical": 128,
    "scales": [
        "minor",  # dark, epic feel — most common
        "natural_minor",  # same as minor
        "pentatonic_minor",  # for the drop melody — all notes work
    ],
    "keys": ["Am", "Dm", "Fm", "Cm", "Gm"],
    "chord_progressions": [
        # The universal big room loop: Am - F - C - G
        [("A", "min", 3, 4), ("F", "maj", 3, 4), ("C", "maj", 3, 4), ("G", "dom7", 3, 4)],
        # With 7ths for sophistication
        [("A", "min7", 3, 4), ("F", "maj7", 3, 4), ("C", "maj", 3, 4), ("G", "dom7", 3, 4)],
        # Dm version (Zedd gravitates toward this)
        [("D", "min", 3, 4), ("Bb", "maj", 3, 4), ("F", "maj", 3, 4), ("C", "dom7", 3, 4)],
        # Two-chord pre-chorus tension
        [("A", "min7", 3, 8), ("E", "dom7", 3, 8)],
    ],
    "instruments": {
        "bass": "bass",  # punching 8th-note root lock with kick
        "pad": "supersaw",  # wide stereo supersaw chord pad
        "lead": "supersaw",  # same preset, narrower, higher — the money riff
        "arp": "pluck",  # 16th-note arp in second drop
        "drums": {
            "kick": "drums_kick",
            "snare": "drums_snare",
            "hat": "drums_hat",
            "clap": "drums_clap",
            "crash": "drums_crash",  # crash on bar 1 of the drop
        },
    },
    "effects": {
        "pad": {
            "reverb": {"room_size": 0.5, "wet": 0.2},
            "stereo_width": 1.8,  # wide — fills the stereo field
        },
        "lead": {
            "delay": {"delay_ms": 375.0, "feedback": 0.3, "ping_pong": True},
            "reverb": {"room_size": 0.45, "wet": 0.15},
        },
        "bass": {
            # Sidechain from kick — the pumping feel is the genre
            "sidechain": {"threshold": 0.3, "ratio": 8.0, "release_ms": 80.0, "depth": 0.9},
        },
        "strings": {
            "gate": {"rate_hz": 4.0, "shape": "trapezoid"},  # gated string stabs
            "reverb": {"room_size": 0.4, "wet": 0.2},
        },
    },
    "rhythm": {
        "kick_pattern": "4-on-the-floor, every beat",
        "bass_pattern": "8th-note pump locked to kick in drop, quarter in verse",
        "hat_pattern": "offbeat 8ths in verse, 16ths in build",
        "snare_pattern": "2 and 4",
        "swing": 0.0,
        "fill_density": "low in verse, burst fills in build",
    },
    "arrangement": {
        # Shorter than progressive house — more immediate
        "intro_bars": 4,
        "verse_bars": 8,  # bass + hat only, no drop elements
        "pre_chorus_bars": 4,  # strip back for tension
        "build_bars": 8,  # noise sweep + rising snare + hats
        "drop_bars": 16,  # full texture, anthem melody
        "breakdown_bars": 8,  # strip to pad + ghost melody
        "build2_bars": 8,  # rebuild
        "drop2_bars": 16,  # second drop — bigger, more elements
        "outro_bars": 8,
    },
    "character": [
        "anthemic",
        "euphoric",
        "driving",
        "emotional",
        "festival",
        "uplifting",
        "big",
        "punchy",
    ],
    "notes": """
    The Zedd approach:
    - The drop melody is the whole track. Everything else exists to set it up.
    - The melody should be singable — if you can't hum it, it won't work.
    - Contrast is everything: the breakdown must be quiet so the drop sounds huge.
    - The sidechain pump on the pad/bass is not optional — it's the heartbeat.

    Theory moves:
    - i – bVI – bIII – bVII (minor version): Am – F – C – G
    - The melody peaks on the 5th or root of the scale — emotional resolution.
    - Pre-chorus: cut to just kick + pad, or just pad. Silence creates anticipation.
    - Build: 8 bars of rising tension. Noise sweep starts at bar 5. Snare rolls
      at bar 7. Everything cuts at bar 8 before the drop.
    - The drop melody repeats twice, second time an octave higher or with extra arp.

    Mixing:
    - Kick is loudest. Sidechain the pad against it so the bass breathes.
    - Stereo width on the pad: as wide as possible without phase issues.
    - The lead sits just above the pad in the high-mids, with ping-pong delay
      at tempo (375ms at 128bpm = dotted 8th delay).
    """,
}
