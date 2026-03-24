#!/usr/bin/env python3
"""Stereo imager — visualize L/R balance of a WAV file as a PNG.

Generates a Lissajous-style stereo field plot showing how the audio
energy is distributed between left and right channels. Centered audio
appears as a vertical line; wide stereo appears as a circle or cloud.

Usage:
    python scripts/stereo_imager.py dist/wav/trance_odyssey.wav
    python scripts/stereo_imager.py --all
    make stereo-image-trance_odyssey
"""

from __future__ import annotations

import argparse
import sys
import wave
from pathlib import Path

import numpy as np

REPO = Path(__file__).parent.parent


def stereo_image(
    wav_path: Path,
    out_path: Path | None = None,
    size: int = 600,
    color: str = "#7755ff",
    bg: str = "#0a0a10",
) -> Path:
    """Render a stereo field visualization to PNG."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  matplotlib required: pip install matplotlib")
        sys.exit(1)

    if out_path is None:
        out_path = wav_path.with_suffix(".stereo.png")

    # Read WAV
    with wave.open(str(wav_path), "rb") as wf:
        n_frames = wf.getnframes()
        n_ch = wf.getnchannels()
        sw = wf.getsampwidth()
        raw = wf.readframes(n_frames)

    dtype = np.int16 if sw == 2 else np.int32
    samples = np.frombuffer(raw, dtype=dtype).astype(np.float64)
    samples /= 32768.0 if sw == 2 else 2147483648.0

    if n_ch == 1:
        left = right = samples
    else:
        samples = samples.reshape(-1, 2)
        left = samples[:, 0]
        right = samples[:, 1]

    # Mid/Side decomposition
    mid = (left + right) * 0.5
    side = (left - right) * 0.5

    # Downsample for plotting (max 50k points)
    max_pts = 50000
    if len(mid) > max_pts:
        step = len(mid) // max_pts
        mid = mid[::step][:max_pts]
        side = side[::step][:max_pts]

    # Colors
    bg_rgb = tuple(int(bg.lstrip("#")[i : i + 2], 16) / 255 for i in (0, 2, 4))
    col_rgb = tuple(int(color.lstrip("#")[i : i + 2], 16) / 255 for i in (0, 2, 4))

    fig, ax = plt.subplots(1, 1, figsize=(size / 100, size / 100), dpi=100)
    fig.patch.set_facecolor(bg_rgb)
    ax.set_facecolor(bg_rgb)

    # Plot: X = side (width), Y = mid (center)
    ax.scatter(side, mid, s=0.3, c=[col_rgb], alpha=0.15, edgecolors="none")

    # Crosshairs
    ax.axhline(0, color=col_rgb, alpha=0.15, linewidth=0.5)
    ax.axvline(0, color=col_rgb, alpha=0.15, linewidth=0.5)

    # Labels
    lim = max(np.max(np.abs(mid)), np.max(np.abs(side)), 0.01) * 1.15
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")

    ax.text(
        -lim * 0.95,
        0,
        "L",
        color=col_rgb,
        fontsize=10,
        fontfamily="monospace",
        alpha=0.6,
        va="center",
    )
    ax.text(
        lim * 0.90,
        0,
        "R",
        color=col_rgb,
        fontsize=10,
        fontfamily="monospace",
        alpha=0.6,
        va="center",
    )
    ax.text(
        0,
        lim * 0.90,
        "M",
        color=col_rgb,
        fontsize=10,
        fontfamily="monospace",
        alpha=0.6,
        ha="center",
    )

    # Title
    stem = wav_path.stem
    width_pct = (np.mean(np.abs(side)) / max(np.mean(np.abs(mid)), 1e-9)) * 100
    balance = np.mean(right) - np.mean(left)
    bal_str = (
        "center" if abs(balance) < 0.01 else f"{'R' if balance > 0 else 'L'} {abs(balance):.3f}"
    )
    ax.set_title(
        f"{stem}  ·  width: {width_pct:.0f}%  ·  balance: {bal_str}",
        color=col_rgb,
        fontsize=8,
        fontfamily="monospace",
        pad=8,
    )

    ax.tick_params(colors=col_rgb, labelsize=6)
    for spine in ax.spines.values():
        spine.set_color(col_rgb)
        spine.set_alpha(0.2)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out_path), bbox_inches="tight", pad_inches=0.3, dpi=100, facecolor=bg_rgb)
    plt.close(fig)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Stereo field visualizer")
    parser.add_argument("wav", nargs="?", type=Path, help="Input WAV file")
    parser.add_argument("--all", action="store_true", help="All rendered songs")
    parser.add_argument("--out-dir", type=Path, default=REPO / "dist" / "stereo")
    args = parser.parse_args()

    if args.all:
        wavs = sorted((REPO / "dist" / "wav").glob("*.wav"))
        if not wavs:
            print("No WAV files found. Run: make songs-wav")
            sys.exit(1)
        for wav in wavs:
            out = args.out_dir / f"{wav.stem}.stereo.png"
            print(f"  {wav.stem} → {out.name} ... ", end="", flush=True)
            stereo_image(wav, out)
            print("done")
    elif args.wav:
        if not args.wav.exists():
            print(f"File not found: {args.wav}")
            sys.exit(1)
        out = args.out_dir / f"{args.wav.stem}.stereo.png"
        stereo_image(args.wav, out)
        print(f"  → {out}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
