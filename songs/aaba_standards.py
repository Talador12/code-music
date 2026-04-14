"""AABA Standards - classic 32-bar AABA form via generate_form."""

from code_music.theory import generate_form

song = generate_form("aaba", key="F", bpm=132, include_melody=True, seed=1964)
