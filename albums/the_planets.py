"""The Planets - A symphony for each planet in the solar system.

STUB ALBUM - songs not yet written.

Holst did 7 movements in 1916. We are doing all 8 planets (sorry Pluto)
plus the Sun and the Moon. Each track is a full multi-movement symphony
using the symphony.py composition system, with orchestration and mood
matching the character of each celestial body.

Export: full audio + orchestral sheet music (MusicXML + LilyPond).
"""

ALBUM = {
    "title": "The Planets: A Code-Music Symphony",
    "artist": "code-music",
    "genre": "Orchestral / Symphonic",
    "year": 2026,
    "description": (
        "Ten symphonic movements for the solar system. Mercury is fast and "
        "restless. Venus is warm and lyrical. Earth is complex and layered. "
        "Mars is violent and brass-heavy (Holst got this right). Jupiter is "
        "majestic and enormous. Saturn is slow and haunting. Uranus is weird "
        "and chaotic. Neptune is distant and dissolving into nothing. "
        "The Sun is the overture. The Moon is the epilogue."
    ),
    "tracks": [
        {
            "title": "I. Sol (The Sun)",
            "song": "planets_sun",
            "bpm": 108,
            "notes": "Overture. Brass fanfare. The source of all energy. "
            "Full orchestra, ff to pp, representing sunrise to sunset.",
        },
        {
            "title": "II. Mercury (The Messenger)",
            "song": "planets_mercury",
            "bpm": 176,
            "notes": "Scherzo. Fast, flickering, never settling. Woodwind runs. "
            "Piccolo and flute dancing. 7/8 time. Closest to the sun, fastest orbit.",
        },
        {
            "title": "III. Venus (The Beautiful)",
            "song": "planets_venus",
            "bpm": 72,
            "notes": "Adagio. Strings and harp. Warm, lyrical, romantic. "
            "Solo violin melody. The most beautiful thing in the sky.",
        },
        {
            "title": "IV. Terra (Earth)",
            "song": "planets_earth",
            "bpm": 120,
            "notes": "The one Holst skipped. Four seasons as movements within the movement. "
            "Spring = woodwinds. Summer = full orchestra. Autumn = brass and strings. "
            "Winter = sparse piano and celesta.",
        },
        {
            "title": "V. Luna (The Moon)",
            "song": "planets_moon",
            "bpm": 66,
            "notes": "Nocturne. Celesta, harp, muted strings. Debussy's Clair de Lune "
            "energy but original. Tidal pull expressed as a slow 6/8.",
        },
        {
            "title": "VI. Mars (The Bringer of War)",
            "song": "planets_mars",
            "bpm": 144,
            "notes": "5/4 time (Holst reference). Aggressive ostinato. Col legno strings. "
            "Brass blasts. Timpani. The angry one. Builds to overwhelming climax.",
        },
        {
            "title": "VII. Jupiter (The Bringer of Jollity)",
            "song": "planets_jupiter",
            "bpm": 132,
            "notes": "The big one. Majestic theme in Bb. Full orchestra at its most expansive. "
            "The famous Holst hymn moment, reinterpreted. Joy, grandeur, scale.",
        },
        {
            "title": "VIII. Saturn (The Bringer of Old Age)",
            "song": "planets_saturn",
            "bpm": 56,
            "notes": "Slow, inevitable, heavy. Low strings and contrabassoon. "
            "Tolling bells (tubular bells / celesta). Time passing. Mortality.",
        },
        {
            "title": "IX. Uranus (The Magician)",
            "song": "planets_uranus",
            "bpm": 152,
            "notes": "Chaotic, unpredictable. Sudden dynamic shifts. Brass outbursts. "
            "Xylophone and timpani. The trickster planet. Polymetric overlay.",
        },
        {
            "title": "X. Neptune (The Mystic)",
            "song": "planets_neptune",
            "bpm": 48,
            "notes": "Dissolving into the void. Choir fading. Shimmer reverb. "
            "The last note decays into silence. The orchestra disappears. "
            "Morendo to niente.",
        },
    ],
}
