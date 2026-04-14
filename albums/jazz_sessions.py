"""Album: Jazz Sessions - 8-track jazz album."""

TITLE = "Jazz Sessions"
ARTIST = "code-music"
YEAR = 2025
GENRE = "Jazz"
TARGET_LUFS = -14.0

TRACKLIST = [
    "tank_bebop",
    "jazz_waltz",
    "auto_jazz_trio",
    "bossa_sunset",
    "vintage_keys",
    "aaba_standards",
    "bebop_run",
    "analyzed_jazz_v2",
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
