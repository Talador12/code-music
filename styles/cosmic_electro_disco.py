"""Cosmic electro / retro disco-house style profile.

Theory analysis of the cosmic electro / neon disco-house genre.
Artists working in this space: Mord Fustang, Feed Me, SBTRKT, Cut Copy,
Daft Punk (Discovery era), Chromeo.

What makes the sound:
  - Major keys. This genre is euphorically happy where prog house is dark.
  - Disco-influenced chord voicings: maj7, add9, 6/9 — lush and colourful.
  - The laser arp: a hoover or supersaw synth playing 16th-note arpeggios
    of maj7 chords. Fast, relentless, colourful.
  - Funky bass: Motown-influenced, octave jumps, locked to kick.
  - Four-on-the-floor with a strong offbeat clap or open hat.
  - Chorus/flanger on the arp — that neon shimmer is the signature.
  - Bright, slightly retro production: think 2009–2012.
"""

PROFILE = {
    "name": "Cosmic Electro / Retro Disco House",
    "era": "2009–2013",
    "bpm_range": (124, 132),
    "bpm_typical": 128,
    "scales": [
        "major",  # euphorically bright — the main choice
        "lydian",  # even brighter — floating and cosmic
        "dorian",  # for darker sections / bass lines
        "pentatonic",  # for the melodic lead
    ],
    "keys": ["Eb", "Bb", "F", "Ab", "Db"],  # flat keys — piano-friendly, warm
    "chord_progressions": [
        # Mord Fustang cosmos loop: Ebmaj7 - Cm7 - Abmaj7 - Bb
        [("Eb", "maj7", 3, 4), ("C", "min7", 3, 4), ("Ab", "maj7", 3, 4), ("Bb", "dom7", 3, 4)],
        # Daft Punk Discovery feel: Fm - Db - Ab - Eb
        [("F", "min7", 3, 4), ("Db", "maj7", 3, 4), ("Ab", "maj7", 3, 4), ("Eb", "dom7", 3, 4)],
        # Bright add9 loop
        [("Bb", "add9", 3, 4), ("F", "maj7", 3, 4), ("Gm", "min7", 3, 4), ("Eb", "maj7", 3, 4)],
        # Two-chord shimmer (Mord Fustang loves these)
        [("Eb", "maj7", 3, 8), ("Ab", "maj7", 3, 8)],
    ],
    "instruments": {
        "bass": "bass",  # funky, slightly mid-range — not a sub bass
        "pad": "pad",  # slow-attack pad underneath everything
        "laser": "hoover",  # the signature — hoover or sawtooth in 16ths
        "lead": "pluck",  # melodic lead above the arp
        "drums": {
            "kick": "drums_kick",
            "clap": "drums_clap",  # on 2 & 4, tight
            "hat": "drums_hat",  # open hat on offbeats
            "ride": "drums_ride",  # optional ride for disco feel
        },
    },
    "effects": {
        "laser": {
            "chorus": {"rate_hz": 1.2, "depth_ms": 2.5, "wet": 0.45},  # the shimmer
            "delay": {"delay_ms": 187.5, "feedback": 0.25, "wet": 0.2, "ping_pong": True},
            "reverb": {"room_size": 0.4, "wet": 0.15},
        },
        "pad": {
            "reverb": {"room_size": 0.75, "damping": 0.5, "wet": 0.35},
            "stereo_width": 1.8,
        },
        "lead": {
            "reverb": {"room_size": 0.6, "wet": 0.2},
            "delay": {"delay_ms": 375.0, "feedback": 0.35, "wet": 0.3},
        },
        "bass": {
            "compress": {"threshold": 0.6, "ratio": 3.0, "makeup_gain": 1.15},
        },
    },
    "rhythm": {
        "kick_pattern": "4-on-the-floor",
        "bass_pattern": "funky — root + octave jumps, syncopated 8ths",
        "hat_pattern": "open hat on offbeats (very disco)",
        "clap_pattern": "2 and 4, tight",
        "arp_pattern": "16th-note arpeggio of chord tones, all bars",
        "swing": 0.0,
        "fill_density": "low — fills at 8-bar transitions",
    },
    "arrangement": {
        "intro_bars": 8,  # pad + arp only
        "verse_bars": 8,  # add bass + kit
        "bridge_bars": 8,  # melody enters
        "chorus_bars": 16,  # everything — the euphoric peak
        "breakdown_bars": 4,  # brief strip to arp + pad
        "second_chorus": 16,
        "outro_bars": 8,
    },
    "character": [
        "euphoric",
        "cosmic",
        "neon",
        "retro",
        "shimmering",
        "funky",
        "uplifting",
        "colourful",
    ],
    "notes": """
    The Mord Fustang approach:
    - Major keys are non-negotiable. The whole point is euphoria.
    - The laser arp is the hook. It plays the full chord in 16ths, all bars,
      no variation — the chord change IS the variation.
    - Chorus effect on the arp creates the neon shimmer. This is essential.
    - The bass is funky and present — not a sub. Think Motown played on a synth.
    - Open hi-hats on offbeats give it the disco feel.

    Theory moves:
    - Flat keys: Eb, Bb, Ab. They sit well on piano and sound warm.
    - maj7 and add9 chords throughout — never just triads.
    - The progression rarely fully resolves — it loops with the same slight
      tension on every last chord (dom7 or sus2).
    - Lydian mode sections: the #4 creates that floating, cosmic quality.

    Chord voicings:
    - Spread voicings (not close): root in bass, 3rd and 7th in mid, 9th on top.
    - This openness is part of the sound — chords don't feel dense.
    """,
}
