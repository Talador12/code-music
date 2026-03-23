#!/usr/bin/env python3
"""Play all scales with name + in-place progress bar.

Usage:
    .venv/bin/python scripts/play_scales.py                        # straight scales
    .venv/bin/python scripts/play_scales.py --arp                  # arpeggio mode
    .venv/bin/python scripts/play_scales.py --arp --pattern skip   # specific pattern
    .venv/bin/python scripts/play_scales.py --arp --octaves 3      # 3-octave arpeggios
    .venv/bin/python scripts/play_scales.py --group world          # one group only
    .venv/bin/python scripts/play_scales.py --list                 # list without playing
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import threading
import time
import wave
from pathlib import Path

from scripts.arp_render import ARP_PATTERN_NAMES

# ── Scale order: well-known → exotic ──────────────────────────────────────
# (filename_stem, scale_key, display_name, group, character)
SCALES: list[tuple[str, str, str, str, str]] = [
    # ── Everyone knows these ───────────────────────────────────────────────
    ("major", "major", "Major", "diatonic", "bright, happy, resolved"),
    ("natural_minor", "minor", "Natural Minor", "diatonic", "dark, sad, familiar"),
    (
        "pentatonic_major",
        "pentatonic",
        "Major Pentatonic",
        "pentatonic",
        "folk, country, universal",
    ),
    (
        "pentatonic_minor",
        "pentatonic_minor",
        "Minor Pentatonic",
        "pentatonic",
        "rock, blues, guitar",
    ),
    ("blues_minor", "blues", "Blues", "blues", "soul, tension, bends"),
    # ── Common in jazz and rock ────────────────────────────────────────────
    ("dorian", "dorian", "Dorian", "diatonic", "minor but warmer — So What"),
    ("mixolydian", "mixolydian", "Mixolydian", "diatonic", "bluesy major — classic rock"),
    ("harmonic_minor", "harmonic_minor", "Harmonic Minor", "minor", "classical cadences, drama"),
    ("blues_major", "blues_major", "Blues Major", "blues", "country, gospel, lighter"),
    ("melodic_minor", "melodic_minor", "Melodic Minor", "minor", "jazz lines, smooth ascent"),
    # ── Film, game, cinematic ─────────────────────────────────────────────
    ("lydian", "lydian", "Lydian", "diatonic", "floating, John Williams magic"),
    ("phrygian", "phrygian", "Phrygian", "diatonic", "Spanish, metal, dark"),
    (
        "phrygian_dominant",
        "phrygian_dominant",
        "Phrygian Dominant",
        "minor",
        "flamenco, Middle East, fire",
    ),
    ("hungarian_minor", "hungarian_minor", "Hungarian Minor", "world", "gypsy, dramatic, Liszt"),
    # ── Jazz theory ────────────────────────────────────────────────────────
    ("bebop_dominant", "bebop_dominant", "Bebop Dominant", "bebop", "Parker, chord tones on beats"),
    ("bebop_major", "bebop_major", "Bebop Major", "bebop", "swing era, big band"),
    ("bebop_minor", "bebop_minor", "Bebop Minor", "bebop", "minor ii-V-i lines"),
    (
        "lydian_dominant",
        "lydian_dominant",
        "Lydian Dominant",
        "modal_jazz",
        "bright + bluesy fusion",
    ),
    (
        "super_locrian",
        "super_locrian",
        "Altered (Super Locrian)",
        "modal_jazz",
        "V7alt — maximum tension",
    ),
    (
        "lydian_augmented",
        "lydian_augmented",
        "Lydian Augmented",
        "modal_jazz",
        "floating, Coltrane",
    ),
    # ── Symmetric ─────────────────────────────────────────────────────────
    ("whole_tone", "whole_tone", "Whole Tone", "symmetric", "dreamy, Debussy, no gravity"),
    ("diminished", "diminished", "Diminished (Half-Whole)", "symmetric", "jazz tension, over dom7"),
    ("diminished_hw", "diminished_hw", "Diminished (Whole-Half)", "symmetric", "over dim7 chords"),
    ("augmented", "augmented", "Augmented", "symmetric", "eerie, Coltrane, Oliver Nelson"),
    ("locrian", "locrian", "Locrian", "diatonic", "unstable — tonic is diminished"),
    # ── World ─────────────────────────────────────────────────────────────
    ("arabic", "arabic", "Arabic / Double Harmonic", "world", "two aug 2nds, very dense"),
    ("japanese", "japanese", "Japanese (Hirajoshi)", "world", "koto, meditative, sparse"),
    ("in_sen", "in_sen", "In-Sen", "world", "haunting Japanese pentatonic"),
    ("persian", "persian", "Persian", "world", "tense, ancient, exotic"),
    ("enigmatic", "enigmatic", "Enigmatic (Verdi)", "world", "bizarre — barely harmonizable"),
    # ── Reference ─────────────────────────────────────────────────────────
    ("chromatic", "chromatic", "Chromatic", "reference", "all 12 semitones"),
    ("_circle_of_fifths", "major", "Circle of Fifths", "reference", "major scale in all 12 keys"),
]

GROUPS = sorted({s[3] for s in SCALES})

# ANSI
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
DIM = "\033[2m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
UP1 = "\033[1A"
ERASE = "\033[2K"

BAR_WIDTH = 36


def _wav_duration(path: Path) -> float:
    try:
        with wave.open(str(path), "rb") as wf:
            return wf.getnframes() / wf.getframerate()
    except Exception:
        return 0.0


def _bar(elapsed: float, total: float) -> str:
    frac = min(elapsed / total, 1.0) if total > 0 else 0.0
    filled = int(frac * BAR_WIDTH)
    empty = BAR_WIDTH - filled
    pct = int(frac * 100)
    return f"{'█' * filled}{'░' * empty}  {pct:3d}%  {elapsed:4.1f}s / {total:.0f}s"


def _play_wav(wav_path: Path, label: str) -> None:
    """Play wav_path while showing an in-place progress bar on the line below label."""
    duration = _wav_duration(wav_path)
    start = time.monotonic()
    done = threading.Event()

    # Write initial progress line
    sys.stdout.write(f"  {DIM}···{RESET}\n")
    sys.stdout.flush()

    def _tick() -> None:
        while not done.is_set():
            elapsed = time.monotonic() - start
            bar = _bar(elapsed, duration)
            sys.stdout.write(f"{UP1}{ERASE}  {GREEN}{bar}{RESET}\n")
            sys.stdout.flush()
            time.sleep(0.1)
        bar = _bar(duration, duration)
        sys.stdout.write(f"{UP1}{ERASE}  {GREEN}{bar}{RESET}\n")
        sys.stdout.flush()

    proc = subprocess.Popen(
        ["afplay", str(wav_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    t = threading.Thread(target=_tick, daemon=True)
    t.start()
    proc.wait()
    done.set()
    t.join(timeout=0.4)


def play_one(
    stem: str,
    scale_key: str,
    name: str,
    group: str,
    tag: str,
    index: int,
    total: int,
    arp: bool,
    arp_pattern: str,
    arp_octaves: int,
    arp_bpm: float,
    arp_instrument: str,
    wav_dir: Path,
) -> None:

    counter = f"{DIM}[{index}/{total}]{RESET}"
    grp = f"{MAGENTA}{group}{RESET}"
    mode_tag = ""
    if arp:
        pat_name = ARP_PATTERN_NAMES.get(arp_pattern, arp_pattern)
        mode_tag = f"  {BLUE}arp:{pat_name}  {arp_octaves}oct{RESET}"

    sys.stdout.write(f"\n{counter} {BOLD}{CYAN}{name}{RESET}  {grp}{mode_tag}\n")
    sys.stdout.write(f"  {DIM}{tag}{RESET}\n")
    sys.stdout.flush()

    if arp:
        # Render on the fly to a temp file
        try:
            from scripts.arp_render import render_arp

            wav_path = render_arp(
                scale_key=scale_key,
                pattern=arp_pattern,
                octaves=arp_octaves,
                bpm=arp_bpm,
                instrument=arp_instrument,
            )
            _play_wav(wav_path, name)
            os.unlink(wav_path)  # clean up temp file
        except Exception as e:
            sys.stdout.write(f"{UP1}{ERASE}  {YELLOW}render error: {e}{RESET}\n")
            sys.stdout.flush()
    else:
        wav = wav_dir / f"{stem}.wav"
        if not wav.exists():
            sys.stdout.write(f"  {YELLOW}⚠ not rendered — run: make scales{RESET}\n")
            sys.stdout.flush()
            return
        _play_wav(wav, name)


def run(
    scales: list[tuple[str, str, str, str, str]],
    wav_dir: Path,
    arp: bool,
    arp_pattern: str,
    arp_octaves: int,
    arp_bpm: float,
    arp_instrument: str,
) -> None:
    total = len(scales)
    for i, (stem, scale_key, name, group, tag) in enumerate(scales, 1):
        play_one(
            stem,
            scale_key,
            name,
            group,
            tag,
            i,
            total,
            arp,
            arp_pattern,
            arp_octaves,
            arp_bpm,
            arp_instrument,
            wav_dir,
        )
    sys.stdout.write(f"\n{GREEN}{BOLD}✓ done — {total} scales{RESET}\n\n")
    sys.stdout.flush()


def show_list(scales: list[tuple[str, str, str, str, str]], wav_dir: Path) -> None:
    print(f"\n  {'#':<4} {'SCALE':<32} {'GROUP':<12} CHARACTER")
    print(f"  {'─' * 4} {'─' * 32} {'─' * 12} {'─' * 28}")
    for i, (stem, _, name, group, tag) in enumerate(scales, 1):
        mark = f"{GREEN}✓{RESET}" if (wav_dir / f"{stem}.wav").exists() else f"{DIM}○{RESET}"
        print(f"  {mark} {i:<3} {name:<32} {DIM}{group:<12}{RESET} {DIM}{tag}{RESET}")
    rendered = sum(1 for s in scales if (wav_dir / f"{s[0]}.wav").exists())
    print(f"\n  {len(scales)} scales  ({rendered} rendered)\n")
    print(f"  Arp patterns: {', '.join(ARP_PATTERN_NAMES.keys())}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Play scales — straight or as arpeggios",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
arp patterns:  {", ".join(ARP_PATTERN_NAMES.keys())}

examples:
  play straight scales (pre-rendered):
    python scripts/play_scales.py

  play as arpeggios (rendered on the fly):
    python scripts/play_scales.py --arp
    python scripts/play_scales.py --arp --pattern cascade --octaves 3
    python scripts/play_scales.py --arp --pattern skip --instrument pluck
    python scripts/play_scales.py --group world --arp --pattern outside_in

  filter by group:
    python scripts/play_scales.py --group blues
    python scripts/play_scales.py --group world --arp
        """,
    )
    parser.add_argument("--group", choices=GROUPS + ["all"], default="all")
    parser.add_argument("--list", action="store_true", help="list without playing")
    parser.add_argument(
        "--dir", type=Path, default=Path(__file__).parent.parent / "dist" / "scales"
    )
    # Arpeggio options
    parser.add_argument("--arp", action="store_true", help="arpeggio mode (renders on the fly)")
    parser.add_argument(
        "--pattern",
        default="up_down",
        choices=list(ARP_PATTERN_NAMES.keys()),
        help="arp pattern (default: up_down)",
    )
    parser.add_argument("--octaves", type=int, default=2, help="octaves per key (default: 2)")
    parser.add_argument("--bpm", type=float, default=120.0, help="arp BPM (default: 120)")
    parser.add_argument("--instrument", default="piano", help="synth preset (default: piano)")
    args = parser.parse_args()

    scales = SCALES if args.group == "all" else [s for s in SCALES if s[3] == args.group]

    if args.list:
        show_list(scales, args.dir)
        return

    # Pre-render check only needed for non-arp mode
    if not args.arp and not args.dir.exists():
        sys.stdout.write(f"{YELLOW}Rendering scales first...{RESET}\n")
        subprocess.run(["make", "scales"], cwd=Path(__file__).parent.parent, check=True)

    mode_line = ""
    if args.arp:
        pat_desc = ARP_PATTERN_NAMES.get(args.pattern, args.pattern)
        mode_line = (
            f"  {BLUE}arp mode · pattern: {args.pattern} ({pat_desc})"
            f" · {args.octaves} octaves · {int(args.bpm)} BPM"
            f" · {args.instrument}{RESET}\n"
        )

    sys.stdout.write(
        f"\n{BOLD}code-music scales{RESET}  "
        f"{DIM}— {len(scales)} scales · all 12 keys{RESET}\n"
        f"{mode_line}"
        f"{DIM}Ctrl+C to stop{RESET}\n"
    )
    sys.stdout.flush()

    try:
        run(scales, args.dir, args.arp, args.pattern, args.octaves, args.bpm, args.instrument)
    except KeyboardInterrupt:
        sys.stdout.write(f"\n{DIM}stopped.{RESET}\n\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
