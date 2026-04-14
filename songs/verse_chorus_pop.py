"""Verse Chorus Pop - standard pop form via generate_form."""

from code_music.theory import generate_form

song = generate_form(
    "verse_chorus",
    key="G",
    bpm=118,
    chords_per_phrase=4,
    include_melody=True,
    seed=2025,
)
