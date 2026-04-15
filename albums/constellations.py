"""Constellations - Night sky patterns as music.

STUB ALBUM - songs not yet written.

Real constellations. Not horoscopes. Each track takes the visual shape
of a constellation and maps it to music: star positions become pitches,
brightness becomes velocity, connecting lines become melodic contour.
Orion's Belt is a three-note motif. The Big Dipper traces a melody.
Cassiopeia's W is a contour. The night sky is a score.

The concept: take the RA/Dec coordinates of each constellation's major
stars, normalize to a pitch range, and use the star pattern as the
melodic seed. Then develop it into a full composition in a genre that
fits the mythology.
"""

ALBUM = {
    "title": "Constellations",
    "artist": "code-music",
    "genre": "Multi-genre / Concept Album",
    "year": 2026,
    "description": (
        "The night sky as a musical score. Star coordinates mapped to pitch. "
        "Star brightness mapped to velocity. Constellation shapes become "
        "melodic contours. Each track develops its star-pattern seed into "
        "a full composition. Astronomy meets synthesis."
    ),
    "tracks": [
        {
            "title": "Orion (The Hunter)",
            "song": "const_orion",
            "bpm": 144,
            "genre": "melodic_metalcore",
            "notes": "The most recognizable constellation. Belt = three-note motif (even spacing, "
            "descending). Betelgeuse (bright, red) = high velocity root. Rigel (bright, blue) "
            "= high velocity fifth. Shoulders and knees form the rhythm. "
            "Dual guitar harmony for the hunter's two arms. Heroic, powerful.",
        },
        {
            "title": "Ursa Major (The Great Bear)",
            "song": "const_ursa_major",
            "bpm": 108,
            "genre": "classical",
            "notes": "Seven bright stars = seven-note theme. The Big Dipper's ladle shape "
            "traces an ascending-then-descending contour. Orchestral. Majestic and slow. "
            "The bear lumbers through the northern sky. Strings and horns.",
        },
        {
            "title": "Ursa Minor (The Little Bear)",
            "song": "const_ursa_minor",
            "bpm": 90,
            "genre": "lofi",
            "notes": "The Little Dipper. Polaris (North Star) = the tonic anchor that never moves. "
            "Everything revolves around it. Smaller, quieter, more intimate version of "
            "the Ursa Major theme. Rhodes and dusty drums. The steady one.",
        },
        {
            "title": "Cassiopeia (The Queen)",
            "song": "const_cassiopeia",
            "bpm": 160,
            "genre": "big_band",
            "notes": "W shape = zigzag melody contour. Up-down-up-down-up. "
            "Dramatic, regal, vain. Big band brass soli tracing the W. "
            "The queen demands attention. Shout chorus.",
        },
        {
            "title": "Scorpius (The Scorpion)",
            "song": "const_scorpius",
            "bpm": 130,
            "genre": "flamenco",
            "notes": "Curved tail = descending chromatic run. Antares (red supergiant, heart of the "
            "scorpion) = sustained low note, maximum intensity. Flamenco guitar. "
            "Cajon. Dangerous and beautiful. The stinger is the final note.",
        },
        {
            "title": "Cygnus (The Swan)",
            "song": "const_cygnus",
            "bpm": 72,
            "genre": "ambient",
            "notes": "Cross shape = two intersecting melodic lines. Northern Cross. "
            "Deneb (bright) at the top = high sustained note. Wings spread = "
            "wide intervals. Ethereal, floating, glass pads and shimmer reverb. "
            "The swan gliding across the Milky Way.",
        },
        {
            "title": "Leo (The Lion)",
            "song": "const_leo",
            "bpm": 150,
            "genre": "funk",
            "notes": "Sickle shape (head) = curved ascending riff. Regulus (heart) = the one. "
            "Funk groove. Moog bass. The lion does not chase - the groove comes to you. "
            "Confident, strutting, king of the sky.",
        },
        {
            "title": "Lyra (The Harp)",
            "song": "const_lyra",
            "bpm": 100,
            "genre": "celtic",
            "notes": "The constellation IS a musical instrument. Vega (brightest star in the "
            "summer sky) = the open string ring. Arpeggiated harp patterns. "
            "6/8 time. Flute melody. Orpheus playing for Eurydice.",
        },
        {
            "title": "Canis Major (The Great Dog)",
            "song": "const_canis_major",
            "bpm": 168,
            "genre": "ska",
            "notes": "Sirius (brightest star in the ENTIRE sky) = maximum velocity hit on beat 1. "
            "The dog star. Energetic, loyal, bounding. Ska offbeats because the dog "
            "is excited to see you. Horn stabs for the bark. Walking bass because... walk.",
        },
        {
            "title": "Aquila (The Eagle)",
            "song": "const_aquila",
            "bpm": 155,
            "genre": "prog_rock",
            "notes": "Altair at the center. Eagle shape = wide wingspan intervals (octaves+). "
            "Soaring. 7/8 time signature because eagles do not follow 4/4. "
            "Long melodic lines that climb and dive. Odd meter prog.",
        },
        {
            "title": "Centaurus (The Centaur)",
            "song": "const_centaurus",
            "bpm": 180,
            "genre": "fusion",
            "notes": "Half human, half horse = two genres fused. Jazz harmony over metal rhythm. "
            "Alpha Centauri (closest star system) = the root. Proxima Centauri = "
            "a quiet grace note, barely audible. Extended chords over gallop drums.",
        },
        {
            "title": "The Southern Cross (Crux)",
            "song": "const_crux",
            "bpm": 95,
            "genre": "bossa_nova",
            "notes": "Smallest constellation, four bright stars in a cross. Southern hemisphere. "
            "Compact four-note motif. Bossa clave. The navigation star of sailors. "
            "Warm, guiding, the compass of the album. Nylon guitar and flute.",
        },
        {
            "title": "Andromeda (The Chained Princess)",
            "song": "const_andromeda",
            "bpm": 120,
            "genre": "post_rock",
            "notes": "Contains the Andromeda Galaxy - the furthest thing visible to the naked eye. "
            "Starts quiet, builds to overwhelming. The galaxy is approaching at 110 km/s. "
            "Crescendo that never stops. The collision is coming in 4.5 billion years. "
            "We have time. The dynamics say otherwise.",
        },
        {
            "title": "Draco (The Dragon)",
            "song": "const_draco",
            "bpm": 140,
            "genre": "metal",
            "notes": "Serpentine shape = chromatic winding melody. Thuban (former North Star) = "
            "detuned drone underneath everything. The dragon coils around the pole. "
            "Drop C. Palm muted chugs following the constellation's curve.",
        },
        {
            "title": "Pleiades (The Seven Sisters)",
            "song": "const_pleiades",
            "bpm": 132,
            "genre": "classical",
            "notes": "Open star cluster, not a constellation, but too beautiful to skip. "
            "Seven voices = seven-part harmony. Each sister a different instrument. "
            "The cluster shimmers. Strings and woodwinds in close harmony. "
            "The most photogenic object in the night sky, as music.",
        },
    ],
}
