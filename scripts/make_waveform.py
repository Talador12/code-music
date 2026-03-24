"""Waveform export: render a WAV → PNG visualization.

Generates a clean waveform image suitable for sharing or the web player.
The visual style matches the project's dark terminal aesthetic.

Usage:
    python scripts/make_waveform.py dist/wav/trance_odyssey.wav
    python scripts/make_waveform.py --all              # all rendered songs
    make waveforms
"""

from __future__ import annotations

import argparse
import sys
import wave
from pathlib import Path

REPO = Path(__file__).parent.parent


def waveform_png(
    wav_path: Path,
    out_path: Path | None = None,
    width: int = 1200,
    height: int = 300,
    color: str = "#7755ff",
    bg: str = "#0a0a10",
) -> Path:
    """Render a WAV file to a waveform PNG."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("  matplotlib + numpy required: pip install matplotlib numpy")
        sys.exit(1)

    if out_path is None:
        out_path = wav_path.with_suffix(".png")

    # Read WAV
    with wave.open(str(wav_path), "rb") as wf:
        n_frames = wf.getnframes()
        n_ch = wf.getnchannels()
        raw = wf.readframes(n_frames)
        sampw = wf.getsampwidth()
        sr = wf.getframerate()

    dtype = np.int16 if sampw == 2 else np.int32
    samples = np.frombuffer(raw, dtype=dtype).astype(np.float64)
    if sampw == 2:
        samples /= 32768.0
    else:
        samples /= 2147483648.0

    if n_ch == 2:
        samples = samples.reshape(-1, 2)
        mono = samples.mean(axis=1)
    else:
        mono = samples

    duration = len(mono) / sr

    # Downsample to width * 4 points for rendering
    target = width * 4
    if len(mono) > target:
        step = len(mono) // target
        mono = mono[::step][:target]

    # Compute envelope: min/max per pixel column
    pixels = width
    chunk = max(1, len(mono) // pixels)
    env_max = np.array([mono[i * chunk : (i + 1) * chunk].max() for i in range(pixels)])
    env_min = np.array([mono[i * chunk : (i + 1) * chunk].min() for i in range(pixels)])

    bg_rgb = tuple(int(bg.lstrip("#")[i : i + 2], 16) / 255 for i in (0, 2, 4))
    col_rgb = tuple(int(color.lstrip("#")[i : i + 2], 16) / 255 for i in (0, 2, 4))

    fig, ax = plt.subplots(1, 1, figsize=(width / 100, height / 100), dpi=100)
    fig.patch.set_facecolor(bg_rgb)
    ax.set_facecolor(bg_rgb)

    xs = np.linspace(0, 1, pixels)
    ax.fill_between(xs, env_min, env_max, color=col_rgb, alpha=0.85, linewidth=0)
    ax.fill_between(xs, env_min * 0.3, env_max * 0.3, color=col_rgb, alpha=0.3, linewidth=0)

    # Duration label
    minutes = int(duration // 60)
    secs = int(duration % 60)
    label = f"{wav_path.stem.replace('_', ' ')}  ·  {minutes}:{secs:02d}"
    ax.text(
        0.01,
        0.92,
        label,
        transform=ax.transAxes,
        color=col_rgb,
        fontsize=9,
        fontfamily="monospace",
        alpha=0.85,
        va="top",
    )

    ax.set_xlim(0, 1)
    ax.set_ylim(-1.05, 1.05)
    ax.axis("off")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out_path), bbox_inches="tight", pad_inches=0, dpi=100, facecolor=bg_rgb)
    plt.close(fig)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render WAV → waveform PNG")
    parser.add_argument("wav", nargs="?", type=Path, help="Input WAV file")
    parser.add_argument("--all", action="store_true", help="All rendered songs")
    parser.add_argument("--out-dir", type=Path, default=REPO / "dist" / "waveforms")
    parser.add_argument("--color", default="#7755ff")
    parser.add_argument("--bg", default="#0a0a10")
    args = parser.parse_args()

    if args.all:
        wavs = sorted((REPO / "dist" / "wav").glob("*.wav"))
        if not wavs:
            print("No WAV files found. Run: make songs-wav")
            sys.exit(1)
        for wav in wavs:
            out = args.out_dir / wav.with_suffix(".png").name
            print(f"  {wav.stem} → {out.name} ... ", end="", flush=True)
            waveform_png(wav, out, color=args.color, bg=args.bg)
            print("done")
    elif args.wav:
        out = args.out_dir / args.wav.with_suffix(".png").name
        print(f"  {args.wav.stem} → {out}")
        waveform_png(args.wav, out, color=args.color, bg=args.bg)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
