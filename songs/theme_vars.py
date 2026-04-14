"""Theme and Variations - classical variation form from generate_form."""

from code_music.theory import generate_form

song = generate_form(
    "theme_variations",
    key="Eb",
    bpm=96,
    chords_per_phrase=4,
    include_melody=True,
    seed=1685,  # Bach's birth year
)
