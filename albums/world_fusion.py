"""Album: World Fusion - 8-track global music album."""

TITLE = "World Fusion"
ARTIST = "code-music"
YEAR = 2025
GENRE = "World / Fusion"
TARGET_LUFS = -14.0

TRACKLIST = [
    "west_african_kora",
    "indian_raga",
    "flamenco_fuego",
    "arabic_nights",
    "carnival_samba",
    "celtic_reel",
    "tango_passion",
    "desert_blues",
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
