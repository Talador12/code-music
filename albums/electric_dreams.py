"""Album: Electric Dreams - 8-track electronic/dance album."""

TITLE = "Electric Dreams"
ARTIST = "code-music"
YEAR = 2025
GENRE = "Electronic / Dance"
TARGET_LUFS = -14.0

TRACKLIST = [
    "trance_odyssey",
    "minimal_techno",
    "synthwave_neon",
    "acid_303",
    "drum_and_bass",
    "sidechain_pump",
    "session_looper",
    "hip_hop_beat",
]

if __name__ == "__main__":
    import sys

    if "--render" in sys.argv:
        import subprocess

        songs = " ".join(TRACKLIST)
        subprocess.run(
            ["make", "album", f"ALBUM={TITLE.lower().replace(' ', '_')}", f"SONGS={songs}"],
            cwd=str(__import__("pathlib").Path(__file__).parent.parent),
        )
    else:
        print(" ".join(TRACKLIST))
