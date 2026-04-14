"""Modulating Pop - pop song with bridge key change via generate_full_song."""

from code_music.theory import generate_full_song

# Bridge modulates to F (subdominant of C) for emotional lift
song = generate_full_song(
    "pop",
    key="C",
    bpm=118,
    sections=["intro", "verse", "chorus", "verse", "chorus", "bridge", "chorus", "outro"],
    modulate_bridge=True,
    seed=2024,
)
