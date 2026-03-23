"""Parody — every genre's worst impulses, played completely straight.

The joke is that it's sincere. Each track is a faithful reproduction
of the most exhausted tropes of its genre. The bro-country anthem
with the truck/beer/girl checklist. The EDM track where the drop
is just the breakdown again but louder. The jazz musician who plays
the same ii-V-I for 47 choruses without making eye contact.
The prog rock song that's 23 minutes and still doesn't resolve.

This album is also just fine to listen to. That's the meta-joke.
"""

ALBUM = {
    "title": "Certified Mid",
    "artist": "code-music",
    "genre": "Parody / Everything",
    "year": 2026,
    "description": (
        "Certified Mid is the genre-parody album. Every track faithfully "
        "reproduces the most recognizable clichés of its source material. "
        "The country track mentions trucks. The EDM track has a 'drop' that "
        "is just silence followed by the same thing but with a kick drum. "
        "The jazz track is 47 choruses of Autumn Leaves. "
        "The ambient track is 8 minutes of a single C major chord. "
        "And somehow, it's all still fine to listen to. "
        "That's the thing about clichés — they became clichés because they work."
    ),
    "influences": [
        "'Weird Al' Yankovic — every album",
        "The Mountain Goats — self-aware songwriting",
        "LCD Soundsystem — Losing My Edge (peak self-aware)",
        "Spinal Tap — Smell the Glove",
        "Every producer who has ever said 'drop the key a half step'",
    ],
    "tracks": [
        # "Trucks" — bro-country by-the-numbers (pentatonic major, 4/4, 95 BPM)
        {"title": "Trucks", "song": "lo_fi_loop", "bpm": 95},
        # "The Drop" — EDM where the drop is a lie
        {"title": "The Drop", "song": "trance_odyssey", "bpm": 128},
        # "Autumn Leaves Again" — jazz standard for the 1000th time
        {"title": "Autumn Leaves Again", "song": "tank_bebop", "bpm": 160},
        # "23 Minutes" — prog rock epic that forgets to end
        {"title": "23 Minutes", "song": "prog_rock", "bpm": 130},
        # "C Major" — ambient that's literally just a C major chord
        {"title": "C Major", "song": "deep_space_drift", "bpm": 60},
    ],
}
