"""Blues Shuffle - 12-bar blues with walking bass and swing."""

from code_music.theory import generate_full_song

song = generate_full_song(
    "blues",
    key="E",
    bpm=96,
    sections=["head", "head", "solo", "head"],
    seed=1958,  # year the blues was born (more or less)
)
