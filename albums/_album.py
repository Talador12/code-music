"""Album system for code-music.

An album is a collection of songs rendered as individual tracks + a playlist.
Each album file defines an ALBUM dict and a list of song modules to include.

Usage:
    python -m albums.render edm_progressive          # render one album
    python -m albums.render --all                    # render all albums
    make album-edm_progressive                       # via Makefile
    make albums                                      # all albums

Album dict schema:
    {
        "title":       str,           # Album title
        "artist":      str,           # Artist name (default: "code-music")
        "genre":       str,           # Primary genre
        "year":        int,           # Release year
        "description": str,           # One paragraph about the album's concept
        "influences":  [str, ...],    # Real artists that inspired the sound
        "tracks":      [              # Ordered track list
            {
                "title":  str,        # Track title (overrides song.title)
                "song":   str,        # songs/ filename stem (no .py)
                "bpm":    int | None, # Override BPM (None = use song default)
            },
            ...
        ],
    }

Output (all gitignored under dist/albums/<album_name>/):
    dist/albums/<name>/01 - <track>.wav       # individual tracks (lossless)
    dist/albums/<name>/01 - <track>.flac      # individual tracks (Spotify)
    dist/albums/<name>/01 - <track>.mp3       # individual tracks (sharing)
    dist/albums/<name>/playlist.m3u           # M3U playlist (all three formats)
    dist/albums/<name>/liner_notes.txt        # Genre, influences, track notes
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict


class TrackDef(TypedDict, total=False):
    title: str
    song: str  # stem of songs/<song>.py
    bpm: int | None


class AlbumDef(TypedDict):
    title: str
    artist: str
    genre: str
    year: int
    description: str
    influences: list[str]
    tracks: list[TrackDef]


def render_album(
    album: AlbumDef,
    out_dir: Path,
    formats: list[str] | None = None,
) -> list[Path]:
    """Render all tracks in an album to out_dir.

    Args:
        album:    Album definition dict.
        out_dir:  Output directory (created if missing).
        formats:  List of formats to render ('wav', 'flac', 'mp3').
                  Defaults to ['wav', 'flac', 'mp3'].

    Returns:
        List of rendered file paths.
    """
    import importlib.util

    from code_music.export import export_flac, export_mp3, export_wav
    from code_music.synth import Synth

    if formats is None:
        formats = ["wav", "flac", "mp3"]

    out_dir.mkdir(parents=True, exist_ok=True)
    repo_root = Path(__file__).parent.parent
    rendered: list[Path] = []

    for i, track in enumerate(album["tracks"], 1):
        song_stem = track["song"]
        track_title = track.get("title", song_stem.replace("_", " ").title())
        bpm_override = track.get("bpm")

        # Load the song module
        song_path = repo_root / "songs" / f"{song_stem}.py"
        if not song_path.exists():
            print(f"  ⚠ songs/{song_stem}.py not found — skipping")
            continue

        spec = importlib.util.spec_from_file_location("_song", song_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        song = mod.song

        # Apply overrides
        song.title = track_title
        if bpm_override:
            song.bpm = float(bpm_override)

        prefix = f"{i:02d} - {track_title}"
        n_tracks = len(album["tracks"])
        print(
            f"  [{i:02d}/{n_tracks}] '{track_title}' {song.bpm:.0f} BPM {song.duration_sec:.0f}s..."
        )

        synth = Synth(sample_rate=song.sample_rate)
        samples = synth.render_song(song)

        for fmt in formats:
            out_path = out_dir / f"{prefix}.{fmt}"
            if fmt == "wav":
                export_wav(samples, out_path, song.sample_rate)
            elif fmt == "flac":
                export_flac(samples, out_path, song.sample_rate)
            elif fmt == "mp3":
                export_mp3(samples, out_path, song.sample_rate)
            rendered.append(out_path)

    # Write liner notes
    _write_liner_notes(album, out_dir)

    # Write M3U playlist for each format
    for fmt in formats:
        _write_playlist(album, out_dir, fmt)

    return rendered


def _write_liner_notes(album: AlbumDef, out_dir: Path) -> None:
    lines = [
        "=" * 60,
        album["title"].upper(),
        f"by {album.get('artist', 'code-music')}",
        f"Genre: {album['genre']}  |  Year: {album['year']}",
        "=" * 60,
        "",
        album["description"],
        "",
        "INFLUENCES",
        "-" * 40,
        *[f"  {inf}" for inf in album["influences"]],
        "",
        "TRACK LISTING",
        "-" * 40,
        *[f"  {i:02d}. {t.get('title', t['song'])}" for i, t in enumerate(album["tracks"], 1)],
        "",
        "Generated with code-music",
        "https://github.com/Talador12/code-music",
        "=" * 60,
    ]
    (out_dir / "liner_notes.txt").write_text("\n".join(lines) + "\n")


def _write_playlist(album: AlbumDef, out_dir: Path, fmt: str) -> None:
    lines = ["#EXTM3U", f"#PLAYLIST:{album['title']}"]
    for i, track in enumerate(album["tracks"], 1):
        title = track.get("title", track["song"].replace("_", " ").title())
        prefix = f"{i:02d} - {title}"
        fname = f"{prefix}.{fmt}"
        lines += [f"#EXTINF:-1,{title}", fname]
    name = "playlist" if fmt == "wav" else f"playlist_{fmt}"
    (out_dir / f"{name}.m3u").write_text("\n".join(lines) + "\n")
