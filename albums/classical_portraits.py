"""Album: Classical Portraits - 8-track classical/orchestral album."""

TITLE = "Classical Portraits"
ARTIST = "code-music"
YEAR = 2025
GENRE = "Classical / Orchestral"
TARGET_LUFS = -14.0

TRACKLIST = [
    "bowed_quartet",
    "string_quartet_v2",
    "baroque_prelude",
    "form_showcase",
    "rondo_in_g",
    "theme_vars",
    "pachelbel_canon",
    "cinematic_trailer",
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
