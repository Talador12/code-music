"""Rondo in G - complete rondo form from generate_form."""

from code_music.theory import generate_form

song = generate_form("rondo", key="G", bpm=120, include_melody=True, seed=314)
