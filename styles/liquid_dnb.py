"""Liquid Drum & Bass style profile.

Theory analysis of the liquid DnB genre.
Artists working in this space: LTJ Bukem, Goldie, Calibre, Hospital Records
artists (London Elektricity, Nu:Tone, Logistics), Netsky, Hybrid Minds.

What makes the sound:
  - Fast tempo (174 BPM) but the music feels unhurried — the drums move fast
    but the chords change slowly, the bass is sustained.
  - Jazz-influenced chord voicings: min9, maj7, dim. Real harmonic colour.
  - Reese bass or sub bass that sustains chord tones — not just roots.
  - Rhodes or Wurlitzer comping (swung 8ths, jazz feel).
  - Lush reverbed pads and atmospheric flute or string melody.
  - The drums are breakbeat-influenced, not 4-on-the-floor.
  - Swing on the hi-hats (0.45–0.55) — the DnB groove comes from swing.
"""

PROFILE = {
    "name": "Liquid Drum & Bass",
    "era": "1995–present (peak: 2000–2010)",
    "bpm_range": (170, 178),
    "bpm_typical": 174,
    "scales": [
        "dorian",  # the primary choice — minor with warmth
        "minor",  # natural minor for darker sections
        "pentatonic_minor",  # bass lines and simple melodies
        "melodic_minor",  # for jazz-inflected melody lines
    ],
    "keys": ["Dm", "Cm", "Am", "Gm", "Fm"],
    "chord_progressions": [
        # Jazz-inflected minor: Dm9 - Bbmaj7 - Fmaj7 - Am7
        [("D", "min9", 3, 4), ("Bb", "maj7", 3, 4), ("F", "maj7", 3, 4), ("A", "min7", 3, 4)],
        # Two-chord sustain (LTJ Bukem approach — very little movement)
        [("D", "min7", 3, 8), ("G", "dom7", 3, 8)],
        # Jazz ii-V-i turnaround
        [("E", "min7b5", 3, 4), ("A", "dom7", 3, 4), ("D", "min9", 3, 8)],
        # Warm major section for contrast
        [("F", "maj7", 3, 4), ("C", "maj7", 3, 4), ("Bb", "maj7", 3, 4), ("Gm", "min7", 3, 4)],
    ],
    "instruments": {
        "bass": "reese_bass",  # sustains chord tones, not just root
        "pad": "pad",  # atmospheric, wide, reverbed
        "rhodes": "rhodes",  # comping with swing, jazz voicings
        "melody": "flute",  # or strings — atmospheric, reverbed
        "drums": {
            "kick": "drums_kick",  # not 4-on-the-floor: 1, 2.5 in DnB
            "snare": "drums_snare",  # backbeat, tight
            "hat": "drums_hat",  # swung 8ths + occasional 16th bursts
            "ride": "drums_ride",  # optional jazz ride texture
        },
    },
    "effects": {
        "pad": {
            "reverb": {"room_size": 0.75, "wet": 0.35},
            "stereo_width": 1.6,
            "chorus": {"rate_hz": 0.6, "wet": 0.15},
        },
        "melody": {
            "reverb": {"room_size": 0.5, "wet": 0.2},
            "delay": {"delay_ms": 345.0, "feedback": 0.35, "wet": 0.25},
        },
        "rhodes": {
            "chorus": {"rate_hz": 0.6, "wet": 0.18},
            "reverb": {"room_size": 0.4, "wet": 0.12},
        },
        "bass": {
            "compress": {"threshold": 0.5, "ratio": 4.0, "makeup_gain": 1.15},
        },
    },
    "rhythm": {
        "kick_pattern": "DnB syncopated: beat 1, beat 2.5 (the 'and' of 2)",
        "snare_pattern": "backbeat: 2 and 4",
        "hat_pattern": "swung 8ths, occasional 16th fills",
        "swing": 0.48,  # the DnB groove — slight but essential
        "fill_density": "moderate — snare rolls every 2 bars",
        "bass_rhythm": "sustained long notes, not busy",
    },
    "arrangement": {
        "intro_bars": 8,  # pads only
        "bass_enters": 16,  # Reese bass comes in
        "drums_enter": 8,  # drums drop
        "full_bars": 32,  # full texture
        "breakdown": 16,  # strip to pads + melody
        "rebuild": 8,
        "second_drop": 32,
        "outro": 16,
    },
    "character": [
        "warm",
        "jazzy",
        "atmospheric",
        "lush",
        "melancholic",
        "sophisticated",
        "flowing",
        "introspective",
    ],
    "notes": """
    The liquid DnB approach:
    - Fast tempo, slow harmonic rhythm. The drums move at 174 BPM but the
      chords might only change once every 4 bars. The tension comes from the
      contrast between drum speed and harmonic stillness.
    - The Reese bass is not just a root note — it sustains the 3rd or 5th of
      the chord for colour. Bass notes are long, not busy.
    - Swing is essential. Without swing on the hats, it sounds mechanical.
      0.45–0.55 range.
    - The DnB kick pattern: beat 1, then the 'and' of beat 2 (beat 2.5).
      Not 4-on-the-floor. This is what makes it feel like a breakbeat.
    - Rhodes or Wurlitzer with jazz voicings: shell voicings (3rd and 7th only,
      no root — the bass covers that).
    - Everything is reverbed. The atmosphere is as important as the notes.

    Theory moves:
    - Dorian mode throughout: minor feel but with the bright major 6th.
    - ii-V-i jazz turnarounds appear in bass lines and melody lines.
    - min9 chords instead of plain min7 — the 9th adds warmth.
    - Modal interchange: borrow from parallel major for colour (Fmaj7 in Dm).
    """,
}
