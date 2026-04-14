"""Album: Ambient Horizons - 8-track ambient/electronic album.

Render with: make album ALBUM=ambient_horizons SONGS="$(python albums/ambient_horizons.py)"
Or: python albums/ambient_horizons.py --render
"""

TITLE = "Ambient Horizons"
ARTIST = "code-music"
YEAR = 2025
GENRE = "Ambient / Electronic"
TARGET_LUFS = -14.0

TRACKLIST = [
    "ambient_drone",
    "ambient_space",
    "ethereal_drift",
    "dark_cathedral",
    "space_ambient_v2",
    "japanese_garden",
    "nordic_folk",
    "deep_space_drift",
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
