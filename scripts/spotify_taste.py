#!/usr/bin/env python3
"""Read your Spotify listening data and write a music taste profile.

Run after spotify_auth.py has stored a token:

    python scripts/spotify_taste.py

Reads:
  - Your top artists (short, medium, long term)
  - Your top tracks
  - Recently played
  - Saved tracks sample
  - Public playlists (names + track counts)

Writes:
  - styles/my_taste.py   — Python profile for code-music to use
  - styles/my_taste.json — Raw data for inspection

Usage in songs:
    from styles.my_taste import PROFILE
    # PROFILE["top_artists"], PROFILE["top_genres"], PROFILE["bpm_range"], etc.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path

TOKEN_FILE = Path(__file__).parent.parent / ".spotify_token"
STYLES_DIR = Path(__file__).parent.parent / "styles"
OUTPUT_PY = STYLES_DIR / "my_taste.py"
OUTPUT_JSON = STYLES_DIR / "my_taste.json"

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
DIM = "\033[2m"


def _api(endpoint: str, token: str) -> dict:
    """Make a Spotify API call."""
    url = f"https://api.spotify.com/v1/{endpoint}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print(f"\n{YELLOW}Token expired — run: python scripts/spotify_auth.py{RESET}")
            sys.exit(1)
        raise


def _collect(token: str) -> dict:
    """Fetch all relevant data from Spotify API."""
    data: dict = {}

    print(f"  {DIM}Fetching user profile...{RESET}")
    data["profile"] = _api("me", token)

    print(f"  {DIM}Fetching top artists (short term)...{RESET}")
    data["top_artists_short"] = _api("me/top/artists?limit=50&time_range=short_term", token)

    print(f"  {DIM}Fetching top artists (medium term)...{RESET}")
    data["top_artists_medium"] = _api("me/top/artists?limit=50&time_range=medium_term", token)

    print(f"  {DIM}Fetching top artists (long term)...{RESET}")
    data["top_artists_long"] = _api("me/top/artists?limit=50&time_range=long_term", token)

    print(f"  {DIM}Fetching top tracks (medium term)...{RESET}")
    data["top_tracks_medium"] = _api("me/top/tracks?limit=50&time_range=medium_term", token)

    print(f"  {DIM}Fetching recently played...{RESET}")
    data["recent"] = _api("me/player/recently-played?limit=50", token)

    print(f"  {DIM}Fetching saved tracks sample...{RESET}")
    data["saved_tracks"] = _api("me/tracks?limit=50", token)

    print(f"  {DIM}Fetching playlists...{RESET}")
    data["playlists"] = _api("me/playlists?limit=50", token)

    print(f"  {DIM}Fetching followed artists...{RESET}")
    data["followed"] = _api("me/following?type=artist&limit=50", token)

    return data


def _analyze(data: dict) -> dict:
    """Extract meaningful patterns from raw API data."""
    profile = data["profile"]

    # ── Top artists across all time ranges ─────────────────────────────────
    artist_counts: Counter = Counter()
    all_artists: dict[str, dict] = {}

    for key in ("top_artists_short", "top_artists_medium", "top_artists_long"):
        items = data[key].get("items", [])
        weight = {"short": 3, "medium": 2, "long": 1}[key.split("_")[-1]]
        for i, artist in enumerate(items):
            name = artist["name"]
            score = (50 - i) * weight  # rank-weighted score
            artist_counts[name] += score
            all_artists[name] = artist

    top_artists = [
        {
            "name": name,
            "genres": all_artists[name].get("genres", []),
            "popularity": all_artists[name].get("popularity", 0),
            "score": score,
        }
        for name, score in artist_counts.most_common(30)
    ]

    # ── Genre extraction ────────────────────────────────────────────────────
    genre_counts: Counter = Counter()
    for artist in all_artists.values():
        for genre in artist.get("genres", []):
            genre_counts[genre] += 1

    top_genres = [g for g, _ in genre_counts.most_common(20)]

    # ── Top tracks ──────────────────────────────────────────────────────────
    top_tracks = [
        {
            "name": t["name"],
            "artist": t["artists"][0]["name"] if t["artists"] else "",
            "popularity": t["popularity"],
        }
        for t in data["top_tracks_medium"].get("items", [])[:20]
    ]

    # ── Audio features approximation (BPM, energy, valence) ────────────────
    # Extract from track tempos where available in audio features
    # We'll use popularity and genre heuristics since audio-features endpoint
    # needs extra API calls per track
    edm_genres = {
        "electronic",
        "edm",
        "house",
        "techno",
        "trance",
        "drum and bass",
        "dubstep",
        "electro",
        "progressive house",
        "big room",
    }
    jazz_genres = {"jazz", "bebop", "fusion", "smooth jazz", "nu jazz"}
    rock_genres = {
        "rock",
        "alternative rock",
        "indie rock",
        "prog rock",
        "metal",
        "hard rock",
        "punk",
        "post-rock",
    }
    classical_genres = {
        "classical",
        "orchestral",
        "chamber music",
        "baroque",
        "contemporary classical",
    }
    hiphop_genres = {"hip hop", "rap", "trap", "r&b", "soul", "funk", "neo soul"}

    genre_set = set(genre_counts.keys())

    def genre_overlap(target_genres):
        return len(genre_set & target_genres) / max(len(target_genres), 1)

    # ── Playlist names ──────────────────────────────────────────────────────
    playlists = [
        {
            "name": p["name"],
            "tracks": p["tracks"]["total"],
            "public": p["public"],
        }
        for p in data["playlists"].get("items", [])
        if p is not None
    ]

    # ── Recent tracks ───────────────────────────────────────────────────────
    recent_artists = [
        item["track"]["artists"][0]["name"]
        for item in data["recent"].get("items", [])
        if item.get("track") and item["track"].get("artists")
    ]

    # ── Followed artists ────────────────────────────────────────────────────
    followed = [a["name"] for a in data["followed"].get("artists", {}).get("items", [])]

    return {
        "display_name": profile.get("display_name", ""),
        "user_id": profile.get("id", ""),
        "top_artists": top_artists,
        "top_genres": top_genres,
        "top_tracks": top_tracks,
        "playlists": playlists,
        "recent_artists": recent_artists[:20],
        "followed_artists": followed[:30],
        "genre_scores": {
            "edm": genre_overlap(edm_genres),
            "jazz": genre_overlap(jazz_genres),
            "rock": genre_overlap(rock_genres),
            "classical": genre_overlap(classical_genres),
            "hiphop": genre_overlap(hiphop_genres),
        },
    }


def _write_profile(analysis: dict) -> None:
    """Write the taste profile as a Python module."""
    name = analysis["display_name"]
    user_id = analysis["user_id"]
    genres = analysis["top_genres"][:10]
    playlists = analysis["playlists"]
    followed = analysis["followed_artists"][:15]

    # Playlist name hints

    lines = [
        f'"""styles/my_taste.py — Music taste profile for {name} ({user_id}).',
        "",
        "Generated by scripts/spotify_taste.py from Spotify listening data.",
        "Re-run to update: python scripts/spotify_taste.py",
        '"""',
        "",
        "PROFILE = {",
        f'    "user":    "{user_id}",',
        f'    "name":    "{name}",',
        "",
        "    # Top artists by listening weight (short-term weighted 3x)",
        '    "top_artists": [',
    ]
    for a in analysis["top_artists"][:20]:
        genres_str = ", ".join(a["genres"][:3])
        lines.append(f'        "{a["name"]}",  # {genres_str}')
    lines += [
        "    ],",
        "",
        "    # Genres Spotify assigned to your top artists",
        '    "top_genres": [',
    ]
    for g in genres:
        lines.append(f'        "{g}",')
    lines += [
        "    ],",
        "",
        "    # Your top tracks",
        '    "top_tracks": [',
    ]
    for t in analysis["top_tracks"][:10]:
        lines.append(f'        # "{t["name"]}" by {t["artist"]}')
    lines += [
        "    ],",
        "",
        "    # Playlist names (what you've curated)",
        '    "playlists": [',
    ]
    for p in playlists[:15]:
        lines.append(f'        "{p["name"]}",  # {p["tracks"]} tracks')
    lines += [
        "    ],",
        "",
        "    # Artists you've followed",
        '    "followed_artists": [',
    ]
    for a in followed:
        lines.append(f'        "{a}",')
    lines += [
        "    ],",
        "",
        "    # Genre affinity scores (0.0–1.0, higher = more of this in your library)",
        f'    "genre_scores": {json.dumps(analysis["genre_scores"], indent=8)},',
        "",
        "    # code-music album recommendations based on your taste",
        "    # (update these manually after reviewing your profile)",
        '    "recommended_albums": [',
    ]

    # Smart album recommendations
    gs = analysis["genre_scores"]
    recs = []
    if gs["edm"] > 0.1:
        recs += ["edm_progressive", "edm_festival", "cosmic_electro", "techno", "dubstep"]
    if gs["jazz"] > 0.05:
        recs += ["jazz_neosoul", "drum_and_bass"]
    if gs["rock"] > 0.1:
        recs += ["rock_prog", "indie_alternative", "metal"]
    if gs["classical"] > 0.05:
        recs += ["classical_orchestral", "ambient_cinematic"]
    if gs["hiphop"] > 0.05:
        recs += ["hiphop_lofi", "rnb_soul", "funk_disco"]
    if not recs:
        recs = ["anthology"]  # fallback

    for r in recs:
        lines.append(f'        "{r}",')
    lines += [
        "    ],",
        "}",
    ]

    OUTPUT_PY.write_text("\n".join(lines) + "\n")


def _display(analysis: dict) -> None:
    """Print a human-readable summary."""
    print(f"\n{BOLD}{CYAN}{analysis['display_name']}'s Music Profile{RESET}")
    print(f"{DIM}Spotify user: {analysis['user_id']}{RESET}\n")

    print(f"{BOLD}Top Artists:{RESET}")
    for i, a in enumerate(analysis["top_artists"][:10], 1):
        genres = ", ".join(a["genres"][:2]) if a["genres"] else "unknown genre"
        print(f"  {i:2}. {a['name']:<30} {DIM}{genres}{RESET}")

    print(f"\n{BOLD}Top Genres:{RESET}")
    for i, g in enumerate(analysis["top_genres"][:12], 1):
        print(f"  {i:2}. {g}")

    print(f"\n{BOLD}Playlists:{RESET}")
    for p in analysis["playlists"][:10]:
        pub = "" if p["public"] else f" {DIM}(private){RESET}"
        print(f"  {p['name']:<35} {DIM}{p['tracks']} tracks{RESET}{pub}")

    print(f"\n{BOLD}Genre Affinity:{RESET}")
    for genre, score in sorted(analysis["genre_scores"].items(), key=lambda x: -x[1]):
        bar_len = int(score * 30)
        bar = "█" * bar_len + "░" * (30 - bar_len)
        pct = int(score * 100)
        print(f"  {genre:<12} {GREEN}{bar}{RESET} {pct}%")

    print(f"\n{GREEN}Profile written to:{RESET}")
    print(f"  {OUTPUT_PY}")
    print(f"  {OUTPUT_JSON}\n")


def main():
    if not TOKEN_FILE.exists():
        print(f"\n{YELLOW}No token found. Run first:{RESET}")
        print("  python scripts/spotify_auth.py\n")
        sys.exit(1)

    token_data = json.loads(TOKEN_FILE.read_text())
    token = token_data.get("access_token")

    # Check if expired
    if time.time() >= token_data.get("expires_at", 0) - 60:
        print(f"\n{YELLOW}Token expired. Re-run:{RESET}")
        print(
            f"  python scripts/spotify_auth.py "
            f"--client-id {token_data.get('client_id', 'YOUR_ID')}\n"
        )
        sys.exit(1)

    print(f"\n{BOLD}Reading your Spotify data...{RESET}")
    raw = _collect(token)
    analysis = _analyze(raw)

    # Save raw JSON
    STYLES_DIR.mkdir(exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(raw, indent=2))

    # Write Python profile
    _write_profile(analysis)

    # Display summary
    _display(analysis)


if __name__ == "__main__":
    main()
