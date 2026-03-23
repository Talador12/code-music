#!/usr/bin/env python3
"""Vibe player — pick a mood, hear a song. No music theory required.

Usage:
    .venv/bin/python -m scripts.play_vibe
    .venv/bin/python -m scripts.play_vibe --vibe chill
    .venv/bin/python -m scripts.play_vibe --list
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import threading
import time
import wave
from pathlib import Path

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
UP1 = "\033[1A"
ERASE = "\033[2K"

# ── Song catalogue — no theory language ───────────────────────────────────────
# (file_stem, vibe, one_line_description)
SONGS: list[tuple[str, str, str]] = [
    # chill
    ("deep_space_drift", "chill", "slow, ambient, no drums — outer space"),
    ("lo_fi_loop", "chill", "lo-fi hip-hop beat — late night studying"),
    ("deadmau5_house", "chill", "slow-building electronic — patient and hypnotic"),
    # energizing
    ("trance_odyssey", "energizing", "uplifting trance — builds and drops hard"),
    ("clarity_drive", "energizing", "festival EDM — anthem melody, big drop"),
    ("future_bass", "energizing", "future bass — emotional and driving"),
    ("prog_rock", "energizing", "prog rock guitar — D Dorian, 130 BPM"),
    # alluring
    ("lollipop_laser", "alluring", "cosmic disco — neon, euphoric, retro"),
    ("liquid_dnb", "alluring", "liquid drum & bass — warm, jazzy, fast"),
    ("tank_bebop", "alluring", "big-band jazz — Cowboy Bebop energy"),
    # powerful
    ("symphony_no1", "powerful", "full orchestra — sonata form, strings and brass"),
    ("cinematic_rise", "powerful", "film trailer — taiko drums, choir swell"),
]

VIBES = sorted({s[1] for s in SONGS})


def _wav_duration(path: Path) -> float:
    try:
        with wave.open(str(path), "rb") as wf:
            return wf.getnframes() / wf.getframerate()
    except Exception:
        return 0.0


def _play(wav: Path, name: str, desc: str) -> None:
    duration = _wav_duration(wav)
    start = time.monotonic()
    done = threading.Event()

    sys.stdout.write(f"  {DIM}···{RESET}\n")
    sys.stdout.flush()

    def _tick() -> None:
        while not done.is_set():
            elapsed = time.monotonic() - start
            frac = min(elapsed / duration, 1.0) if duration > 0 else 0.0
            filled = int(frac * 40)
            bar = "█" * filled + "░" * (40 - filled)
            pct = int(frac * 100)
            sys.stdout.write(
                f"{UP1}{ERASE}  {GREEN}{bar}{RESET}  {pct:3d}%  "
                f"{DIM}{elapsed:.0f}s / {duration:.0f}s{RESET}\n"
            )
            sys.stdout.flush()
            time.sleep(0.1)
        bar = "█" * 40
        sys.stdout.write(
            f"{UP1}{ERASE}  {GREEN}{bar}{RESET}  100%  "
            f"{DIM}{duration:.0f}s / {duration:.0f}s{RESET}\n"
        )
        sys.stdout.flush()

    proc = subprocess.Popen(
        ["afplay", str(wav)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    t = threading.Thread(target=_tick, daemon=True)
    t.start()
    proc.wait()
    done.set()
    t.join(timeout=0.4)


def _render(stem: str, wav_dir: Path) -> Path | None:
    wav = wav_dir / f"{stem}.wav"
    if wav.exists():
        return wav
    sys.stdout.write(f"  {YELLOW}rendering {stem}...{RESET}\n")
    sys.stdout.flush()
    result = subprocess.run(
        [sys.executable, "-m", "code_music.cli", f"songs/{stem}.py", "-o", str(wav)],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
    )
    return wav if result.returncode == 0 else None


def play_song(stem: str, vibe: str, desc: str, index: int, total: int, wav_dir: Path) -> None:
    sys.stdout.write(
        f"\n{DIM}[{index}/{total}]{RESET}  "
        f"{BOLD}{CYAN}{stem.replace('_', ' ').title()}{RESET}  "
        f"{DIM}{vibe}{RESET}\n"
        f"  {desc}\n"
    )
    sys.stdout.flush()
    wav = _render(stem, wav_dir)
    if wav is None:
        sys.stdout.write(f"  {YELLOW}⚠ could not render{RESET}\n")
        return
    _play(wav, stem, desc)


def show_list(songs: list[tuple[str, str, str]], wav_dir: Path) -> None:
    print(f"\n  {'SONG':<28} {'VIBE':<12} DESCRIPTION")
    print(f"  {'─' * 28} {'─' * 12} {'─' * 30}")
    for stem, vibe, desc in songs:
        rendered = "✓" if (wav_dir / f"{stem}.wav").exists() else "○"
        title = stem.replace("_", " ").title()
        print(f"  {rendered}  {title:<26} {DIM}{vibe:<12}{RESET} {DIM}{desc}{RESET}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Play songs by vibe — no music theory required")
    parser.add_argument(
        "--vibe",
        choices=VIBES + ["all"],
        default="all",
        help="Filter by vibe: chill, energizing, alluring, powerful",
    )
    parser.add_argument("--list", action="store_true", help="list without playing")
    parser.add_argument("--dir", type=Path, default=Path(__file__).parent.parent / "dist" / "wav")
    args = parser.parse_args()

    songs = SONGS if args.vibe == "all" else [s for s in SONGS if s[1] == args.vibe]

    if args.list:
        show_list(songs, args.dir)
        return

    args.dir.mkdir(parents=True, exist_ok=True)

    vibe_line = f"vibe: {args.vibe}" if args.vibe != "all" else "all vibes"
    sys.stdout.write(
        f"\n{BOLD}code-music{RESET}  {DIM}— {len(songs)} songs · {vibe_line}{RESET}\n"
        f"{DIM}Ctrl+C to stop{RESET}\n"
    )
    sys.stdout.flush()

    try:
        for i, (stem, vibe, desc) in enumerate(songs, 1):
            play_song(stem, vibe, desc, i, len(songs), args.dir)
        sys.stdout.write(f"\n{GREEN}{BOLD}✓ done{RESET}\n\n")
    except KeyboardInterrupt:
        sys.stdout.write(f"\n{DIM}stopped.{RESET}\n\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
