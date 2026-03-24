#!/usr/bin/env python3
"""Generate playlists from rendered songs.

Creates M3U, JSON, and plain-text playlists from the rendered WAV/FLAC/MP3
files. Optionally creates a Spotify playlist via the API if a token exists.

Usage:
    python scripts/make_playlist.py                         # all songs, M3U+JSON
    python scripts/make_playlist.py --vibe chill            # filter by vibe
    python scripts/make_playlist.py --format m3u            # M3U only
    python scripts/make_playlist.py --spotify               # also push to Spotify
    make playlist                                           # all songs
    make playlist-chill                                     # chill vibe only
"""

from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

REPO = Path(__file__).parent.parent

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
CYAN = "\033[96m"
DIM = "\033[2m"

# Song catalog — same as play_vibe.py but with full metadata
SONGS = [
    # (file_stem, title, genre, bpm, vibe)
    ("deep_space_drift", "Carrier", "Ambient", 60, "chill"),
    ("drift_state", "Drift State", "Generative Amb.", 50, "chill"),
    ("lo_fi_loop", "Bedside Table", "Lo-Fi", 90, "chill"),
    ("small_hours", "Ember", "Lo-Fi", 85, "chill"),
    ("late_shift", "Low Light", "Neo-Soul", 88, "chill"),
    ("deadmau5_house", "Machine Dreams", "Prog House", 128, "chill"),
    ("still_water", "Still Water", "Neo-Classical", 66, "chill"),
    ("open_circuit", "Open Circuit", "Cinematic Amb.", 65, "chill"),
    ("conversations", "Conversations", "Jazz/Neo-Class.", 80, "chill"),
    ("campfire", "Campfire", "Folk", 76, "chill"),
    ("porch_song", "Porch Song", "Folk", 84, "chill"),
    ("vapor_wave", "Vapor Wave", "Vaporwave", 80, "chill"),
    ("quarter_life", "Quarter Life", "Bedroom Pop", 95, "chill"),
    ("trance_odyssey", "Drop", "Trance", 138, "energizing"),
    ("clarity_drive", "Offshore", "Festival EDM", 128, "energizing"),
    ("future_bass", "Between", "Future Bass", 150, "energizing"),
    ("neon_prayer", "Neon Prayer", "Future Bass", 145, "energizing"),
    ("berlin_four", "Concrete", "Techno", 138, "energizing"),
    ("electric_dreams", "Electric Dreams", "Synthwave", 110, "energizing"),
    ("slipstream", "Slipstream", "Synthwave", 118, "energizing"),
    ("chiptune_quest", "Save Point", "Chiptune", 160, "energizing"),
    ("prog_rock", "Teeth", "Prog Rock", 130, "energizing"),
    ("on_the_one", "On the One", "Funk", 108, "energizing"),
    ("chromatic_bloom", "Chromatic Bloom", "Synth Pop", 120, "energizing"),
    ("fusion_flight", "Fusion Flight", "Jazz Fusion", 148, "energizing"),
    ("mountain_road", "Mountain Road", "Bluegrass", 96, "energizing"),
    ("lollipop_laser", "Lollipop Laser", "Cosmic Disco", 128, "alluring"),
    ("neon_grid", "Neon Grid", "Cosmic Disco", 124, "alluring"),
    ("liquid_dnb", "Upstream", "Liquid DnB", 174, "alluring"),
    ("upstream_two", "Upstream II", "Liquid DnB", 174, "alluring"),
    ("tank_bebop", "The Count", "Bebop Jazz", 168, "alluring"),
    ("after_midnight", "After Midnight", "Jazz Ballad", 58, "alluring"),
    ("the_room", "Room Tone", "Indie Rock", 104, "alluring"),
    ("slow_coast", "Slow Coast", "Indie/Lo-Fi", 92, "alluring"),
    ("heavy_wobble", "Half Step", "Dubstep", 140, "alluring"),
    ("duende", "Duende", "Flamenco", 140, "alluring"),
    ("silk_road", "Silk Road", "Persian/World", 88, "alluring"),
    ("lost_frequencies", "Lost Frequencies", "Deep House", 122, "alluring"),
    ("hollow_ground", "Hollow Ground", "Dark Ambient", 72, "alluring"),
    ("symphony_no1", "Symphony No. 1", "Classical", 108, "powerful"),
    ("cathedral", "Cathedral", "Romantic", 84, "powerful"),
    ("cinematic_rise", "Weight", "Cinematic", 100, "powerful"),
    ("neon_cathedral", "Neon Cathedral", "Hybrid Orch.", 88, "powerful"),
    ("fault_lines", "Fault Lines", "Prog Metal", 152, "powerful"),
    ("the_arc", "The Arc", "Prog Rock 5/4", 124, "powerful"),
    ("signal_loss", "Signal Loss", "Hard DnB", 174, "powerful"),
    ("neuromancer", "Neuromancer", "Neurofunk", 174, "powerful"),
    ("gospel_hour", "Gospel Hour", "Gospel", 76, "powerful"),
    ("midnight_gospel", "Midnight Gospel", "Gospel/Soul", 82, "powerful"),
    ("trap_god", "Trap God", "Trap", 140, "powerful"),
    ("east_coast_night", "East Coast Night", "Boom Bap", 92, "powerful"),
    ("teeth_two", "Teeth II", "Prog Rock", 118, "powerful"),
]

VIBES = sorted({s[4] for s in SONGS})


def _find_audio(stem: str) -> Path | None:
    for fmt in ("flac", "wav", "mp3"):
        p = REPO / "dist" / fmt / f"{stem}.{fmt}"
        if p.exists():
            return p
    return None


def write_m3u(songs: list, out: Path, title: str = "code-music") -> None:
    lines = ["#EXTM3U", f"#PLAYLIST:{title}"]
    for stem, name, genre, bpm, vibe in songs:
        audio = _find_audio(stem)
        fname = audio.name if audio else f"{stem}.wav"
        lines += [f"#EXTINF:-1,{name} [{genre}]", str(audio or fname)]
    out.write_text("\n".join(lines) + "\n")


def write_json(songs: list, out: Path, title: str = "code-music") -> None:
    data = {
        "title": title,
        "generated_by": "code-music",
        "tracks": [
            {
                "title": name,
                "file": stem,
                "genre": genre,
                "bpm": bpm,
                "vibe": vibe,
                "audio": str(_find_audio(stem) or ""),
            }
            for stem, name, genre, bpm, vibe in songs
        ],
    }
    out.write_text(json.dumps(data, indent=2) + "\n")


def write_txt(songs: list, out: Path, title: str = "code-music") -> None:
    lines = [f"# {title}", f"# {len(songs)} tracks", ""]
    for i, (stem, name, genre, bpm, vibe) in enumerate(songs, 1):
        lines.append(f"{i:02d}. {name:<30} {genre:<20} {bpm:>3} BPM  [{vibe}]")
    out.write_text("\n".join(lines) + "\n")


def push_spotify(songs: list, title: str) -> bool:
    """Create a Spotify playlist if a token is available."""
    token_file = REPO / ".spotify_token"
    if not token_file.exists():
        print(f"  {DIM}No Spotify token — run: make spotify{RESET}")
        return False

    import time

    token_data = json.loads(token_file.read_text())
    token = token_data.get("access_token", "")
    if not token or time.time() >= token_data.get("expires_at", 0):
        print(f"  {DIM}Spotify token expired — run: make spotify{RESET}")
        return False

    # Get user ID
    req = urllib.request.Request(
        "https://api.spotify.com/v1/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            user = json.loads(resp.read())
        user_id = user["id"]
    except Exception as e:
        print(f"  {DIM}Spotify API error: {e}{RESET}")
        return False

    # Create playlist
    payload = json.dumps(
        {
            "name": title,
            "description": f"Generated by code-music — {len(songs)} tracks",
            "public": False,
        }
    ).encode()
    req = urllib.request.Request(
        f"https://api.spotify.com/v1/users/{user_id}/playlists",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            pl = json.loads(resp.read())
        print(f"  {GREEN}Spotify playlist created: {pl['external_urls']['spotify']}{RESET}")
        return True
    except Exception as e:
        print(f"  {DIM}Spotify playlist creation failed: {e}{RESET}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate playlists from rendered songs")
    parser.add_argument("--vibe", choices=VIBES + ["all"], default="all", help="Filter by vibe")
    parser.add_argument(
        "--format", choices=["m3u", "json", "txt", "all"], default="all", help="Output format"
    )
    parser.add_argument(
        "--spotify", action="store_true", help="Also create a Spotify playlist (needs token)"
    )
    parser.add_argument("--title", default=None, help="Playlist title")
    parser.add_argument("--out-dir", type=Path, default=REPO / "dist" / "playlists")
    args = parser.parse_args()

    songs = SONGS if args.vibe == "all" else [s for s in SONGS if s[4] == args.vibe]
    title = args.title or (f"code-music — {args.vibe}" if args.vibe != "all" else "code-music")
    slug = args.vibe if args.vibe != "all" else "all"

    args.out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{BOLD}{CYAN}{title}{RESET}  {DIM}({len(songs)} tracks){RESET}\n")

    if args.format in ("m3u", "all"):
        out = args.out_dir / f"{slug}.m3u"
        write_m3u(songs, out, title)
        print(f"  {GREEN}✓{RESET} {out.name}")

    if args.format in ("json", "all"):
        out = args.out_dir / f"{slug}.json"
        write_json(songs, out, title)
        print(f"  {GREEN}✓{RESET} {out.name}")

    if args.format in ("txt", "all"):
        out = args.out_dir / f"{slug}.txt"
        write_txt(songs, out, title)
        print(f"  {GREEN}✓{RESET} {out.name}")

    if args.spotify:
        push_spotify(songs, title)

    print(f"\n  → {args.out_dir}\n")


if __name__ == "__main__":
    main()
