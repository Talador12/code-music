"""Electronic Build - EDM build + drop using generate_full_song."""

from code_music.theory import generate_full_song

song = generate_full_song(
    "electronic",
    key="A",
    bpm=138,
    sections=["intro", "verse", "verse", "drop", "breakdown", "drop", "outro"],
    modulate_bridge=True,
    seed=808,
)
