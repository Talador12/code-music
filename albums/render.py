"""Album renderer CLI.

Usage:
    python -m albums.render <album_stem>          # one album, all formats
    python -m albums.render <album_stem> --wav    # WAV only
    python -m albums.render --all                 # every album
    python -m albums.render --list                # list albums
"""

from __future__ import annotations

import argparse
import importlib
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
ALBUMS_DIR = Path(__file__).parent
DIST_DIR = REPO_ROOT / "dist" / "albums"

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
DIM = "\033[2m"


def discover_albums() -> list[str]:
    """Return sorted list of album stems (filenames without .py, excluding _)."""
    EXCLUDE = {"render", "_album"}
    return sorted(
        p.stem
        for p in ALBUMS_DIR.glob("*.py")
        if not p.stem.startswith("_") and p.stem not in EXCLUDE
    )


def load_album(stem: str):
    """Import an album module and return its ALBUM dict."""
    spec = importlib.util.spec_from_file_location(f"albums.{stem}", ALBUMS_DIR / f"{stem}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "ALBUM"):
        raise AttributeError(f"albums/{stem}.py must define an ALBUM dict")
    return mod.ALBUM


def render_one(stem: str, formats: list[str]) -> None:
    album = load_album(stem)
    out_dir = DIST_DIR / stem
    print(f"\n{BOLD}{CYAN}{album['title']}{RESET}  {DIM}({album['genre']}){RESET}")
    print(f"  {DIM}{len(album['tracks'])} tracks · {', '.join(formats)}{RESET}\n")

    t0 = time.monotonic()
    from albums._album import render_album

    render_album(album, out_dir, formats)
    elapsed = time.monotonic() - t0

    print(f"\n  {GREEN}✓ {album['title']}{RESET}  →  {DIM}{out_dir}{RESET}  ({elapsed:.1f}s)\n")


def list_albums() -> None:
    stems = discover_albums()
    print(f"\n  {'ALBUM':<32} {'GENRE':<22} TRACKS")
    print(f"  {'─' * 32} {'─' * 22} {'─' * 6}")
    for stem in stems:
        try:
            a = load_album(stem)
            rendered = (DIST_DIR / stem / "liner_notes.txt").exists()
            mark = f"{GREEN}✓{RESET}" if rendered else f"{DIM}○{RESET}"
            print(f"  {mark}  {a['title']:<30} {DIM}{a['genre']:<22}{RESET} {len(a['tracks'])}")
        except Exception as e:
            print(f"  ?  {stem:<30} (error: {e})")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m albums.render")
    parser.add_argument("album", nargs="?", help="Album stem (filename without .py)")
    parser.add_argument("--all", action="store_true", help="Render all albums")
    parser.add_argument("--list", action="store_true", help="List albums without rendering")
    parser.add_argument("--wav", action="store_true")
    parser.add_argument("--flac", action="store_true")
    parser.add_argument("--mp3", action="store_true")
    args = parser.parse_args()

    formats = [f for f, flag in [("wav", args.wav), ("flac", args.flac), ("mp3", args.mp3)] if flag]
    if not formats:
        formats = ["wav", "flac", "mp3"]

    if args.list:
        list_albums()
        return

    stems = discover_albums() if args.all else ([args.album] if args.album else [])
    if not stems:
        parser.print_help()
        sys.exit(1)

    for stem in stems:
        render_one(stem, formats)

    if args.all:
        print(f"{GREEN}{BOLD}✓ All {len(stems)} albums rendered.{RESET}\n")


if __name__ == "__main__":
    main()
