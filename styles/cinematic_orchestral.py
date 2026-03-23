"""Cinematic / hybrid orchestral style profile.

Theory analysis of modern cinematic music (2000s–present).
Artists: Hans Zimmer, John Williams, Ennio Morricone, Ramin Djawadi,
Two Steps From Hell, Thomas Bergersen, Brian Tyler.

What makes the sound:
  - Slow harmonic rhythm: chords sustain for bars, not beats.
  - Layered dynamics: everything builds from nothing (pp) to maximum (fff).
  - Taiko or large percussion for impact hits.
  - String ostinatos: short repeated patterns that build tension relentlessly.
  - Choir swells on the emotional peaks.
  - Modal writing: Dorian, Aeolian, Phrygian — avoids functional harmony.
  - Pedal tones: bass note sustained while harmony moves above it.
  - Hybrid: live strings/brass + electronic elements (bass hits, synth pads).
"""

PROFILE = {
    "name": "Cinematic / Hybrid Orchestral",
    "era": "2000s–present",
    "bpm_range": (60, 120),
    "bpm_typical": 92,
    "scales": [
        "minor",  # dark and epic
        "dorian",  # minor with raised 6th — heroic
        "phrygian",  # very dark, threatening
        "harmonic_minor",  # for emotional tension moments
        "whole_tone",  # for surreal/dream sequences
    ],
    "keys": ["Cm", "Dm", "Am", "Em", "Bm"],
    "chord_progressions": [
        # Zimmer: i → bVII → bVI → bVII (circular, no resolution)
        [("C", "min", 3, 4), ("Bb", "maj", 3, 4), ("Ab", "maj", 3, 4), ("Bb", "maj", 3, 4)],
        # Power progression: i → bVI → bIII → bVII
        [("A", "min", 3, 4), ("F", "maj", 3, 4), ("C", "maj", 3, 4), ("G", "maj", 3, 4)],
        # Two-chord suspense: i ↔ bVII (just oscillating)
        [("C", "min", 3, 8), ("Bb", "maj", 3, 8)],
        # Zimmer final resolution: i → IV → i → V (rare — saves for climax)
        [("C", "min", 3, 4), ("F", "min", 3, 4), ("C", "min", 3, 4), ("G", "dom7", 3, 4)],
    ],
    "instruments": {
        "strings": "strings",  # section strings — the core texture
        "cellos": "cello",  # ostinato pattern
        "brass": "french_horn",  # sustained pad layer
        "choir": "choir_aah",  # swell on the climax
        "percussion": "taiko",  # impact hits
        "sub": "sub_bass",  # sub frequency weight on hits
        "pad": "pad",  # hybrid synth pad underneath
    },
    "effects": {
        "strings": {
            "reverb": {"room_size": 0.8, "damping": 0.4, "wet": 0.3},
        },
        "choir": {
            "reverb": {"room_size": 0.9, "damping": 0.3, "wet": 0.45},
            "stereo_width": 1.8,
        },
        "brass": {
            "reverb": {"room_size": 0.85, "wet": 0.3},
        },
        "taiko": {
            "reverb": {"room_size": 0.8, "wet": 0.3},
        },
        "pad": {
            "reverb": {"room_size": 0.7, "wet": 0.3},
            "lfo_filter": {"rate_hz": 0.03, "min_cutoff": 200.0, "max_cutoff": 4000.0},
        },
    },
    "rhythm": {
        "feel": "straight — no swing",
        "swing": 0.0,
        "string_ostinato": "16th notes or 8th notes, repeated pattern, builds intensity",
        "percussion_hits": "sparse — impact on structural downbeats only",
        "taiko_pattern": "hits on 1, sometimes 3 — heavy and sparse",
        "no_drums_in_quiet": "quiet sections have no percussion at all",
    },
    "arrangement": {
        # Cinematic music follows dramatic arc, not verse/chorus
        "silence_intro": 4,  # silence or very quiet pad
        "string_enter": 8,  # ostinato begins quietly
        "brass_enters": 16,  # brass pad added
        "choir_enters": 24,  # choir swell
        "climax_bars": 32,  # full tutti — taiko, choir, brass, strings
        "pullback": 16,  # strip to strings only
        "second_climax": 32,  # bigger — sub bass added, choir louder
        "resolution_bars": 8,  # solo cello or piano, very quiet
    },
    "character": [
        "epic",
        "cinematic",
        "emotional",
        "powerful",
        "building",
        "atmospheric",
        "vast",
        "inevitable",
    ],
    "notes": """
    The Zimmer approach:
    - Modal writing avoids functional harmony (no I → V → I cadences).
      This prevents resolution, keeping tension across long stretches.
    - The i → bVII → bVI → bVII loop is the workhorse of modern trailers.
      It never resolves and loops perfectly.
    - Ostinato: a short string figure repeated insistently. The harmony
      changes underneath it, creating the sensation of rising tension without
      moving the melody.
    - Layering: start with one element (cello pizzicato, or a solo flute).
      Add one layer at a time. Let each layer establish itself before the next.
    - The climax earns its impact through what it contrasts with — the quiet
      before it must be genuinely quiet.
    - Taiko and low brass on structural hits (bar 1 of a new section).
      Between hits: silence or very low texture.
    - The choir is the emotional peak. Use it sparingly.

    Pedal tones:
    - Sustain a bass note (usually the tonic) while the harmony above moves.
    - Example: C pedal in bass, while chords go Cm → Ab → Bb → Cm.
    - Creates tension between bass and harmony — very effective for builds.
    """,
}
