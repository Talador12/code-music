"""Album cover art generator.

Generates a unique visual cover for each album using matplotlib.
Each genre gets a distinct aesthetic — waveforms, spectral plots,
geometric patterns, or abstract art. Saved as cover.png in the album dir.

Usage:
    python scripts/make_cover.py --album edm_progressive
    python scripts/make_cover.py --all
    make covers
"""

from __future__ import annotations

import argparse
import importlib
import math
import random
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO))

# Genre → visual style config
STYLES: dict[str, dict] = {
    # Progressive house: dark, circular, filter sweep gradient
    "edm_progressive": {"bg": "#0a0a14", "fg": "#6644ff", "style": "radial_sweep"},
    # Festival EDM: bright, sharp, stadium energy
    "edm_festival": {"bg": "#000000", "fg": "#ff2244", "style": "spikes"},
    # Cosmic electro: neon colors, laser grid
    "cosmic_electro": {"bg": "#050510", "fg": "#ff44ff", "style": "laser_grid"},
    # Techno: industrial, harsh, stark
    "techno": {"bg": "#111111", "fg": "#cccccc", "style": "grid_harsh"},
    # Dubstep: heavy wobble, distorted waveform
    "dubstep": {"bg": "#0d0010", "fg": "#9900ff", "style": "distorted_wave"},
    # Drum & Bass: fast streaks, motion blur feel
    "drum_and_bass": {"bg": "#000a08", "fg": "#00ffaa", "style": "streaks"},
    # Ambient: soft gradients, floating particles
    "ambient_cinematic": {"bg": "#08080f", "fg": "#4488ff", "style": "particles"},
    # Jazz: warm, organic, brushed texture
    "jazz_neosoul": {"bg": "#1a0e00", "fg": "#ffaa44", "style": "organic"},
    # Classical: formal, symmetric, gold
    "classical_orchestral": {"bg": "#0d0a00", "fg": "#d4aa44", "style": "ornate"},
    # Rock/Prog: distorted, angular, electric
    "rock_prog": {"bg": "#0a0a00", "fg": "#ff6600", "style": "electric"},
    # Metal: dark, fractal, brutal
    "metal": {"bg": "#080808", "fg": "#884422", "style": "fractal"},
    # Lo-fi: muted, grain, vintage
    "hiphop_lofi": {"bg": "#1a1510", "fg": "#aa9977", "style": "grain"},
    # R&B/Soul: velvet, deep purple, smooth
    "rnb_soul": {"bg": "#0a0010", "fg": "#cc66ff", "style": "velvet"},
    # Funk/Disco: bright, circular, disco ball
    "funk_disco": {"bg": "#1a0000", "fg": "#ff4422", "style": "disco"},
    # Folk: earthy, natural, wood grain
    "folk_acoustic": {"bg": "#100a00", "fg": "#cc8844", "style": "wood"},
    # Latin: warm, rhythmic, circular
    "latin": {"bg": "#150800", "fg": "#ff8833", "style": "rhythm"},
    # Pop: clean, bright, minimal
    "pop": {"bg": "#0a0a12", "fg": "#44aaff", "style": "minimal"},
    # Indie/Alt: lo-fi photography feel, muted
    "indie_alternative": {"bg": "#0d0d0d", "fg": "#88aa88", "style": "noise"},
    # World/Experimental: fractal, complex geometry
    "world_experimental": {"bg": "#080810", "fg": "#ffaa44", "style": "mandala"},
    # Country: rustic, simple, horizontal
    "country_americana": {"bg": "#100800", "fg": "#cc9944", "style": "horizon"},
    # Video game: pixel art feel, bright
    "videogame_anime": {"bg": "#000014", "fg": "#44ffcc", "style": "pixel"},
    # Anthology: all colors combined
    "anthology": {"bg": "#000000", "fg": "#ffffff", "style": "spectrum"},
    # Parody: deliberately garish
    "parody": {"bg": "#ff00ff", "fg": "#ffff00", "style": "garish"},
}

DEFAULT_STYLE = {"bg": "#0a0a0a", "fg": "#888888", "style": "minimal"}
SIZE = 800


def _hex_to_rgb(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))


def _draw_radial_sweep(ax, fg: tuple, rng: random.Random) -> None:
    """Progressive house: rings expanding from center, filter sweep gradient."""

    for i in range(60):
        r = (i / 60) ** 0.7
        alpha = (1 - r) * 0.8
        ax.add_patch(
            __import__("matplotlib.patches", fromlist=["Circle"]).Circle(
                (0.5, 0.5),
                r * 0.48,
                fill=False,
                color=fg,
                alpha=alpha,
                linewidth=0.8 + r * 2,
            )
        )
    # Sweeping arc
    theta = [rng.uniform(0, 2 * math.pi) for _ in range(200)]
    radii = [rng.gauss(0.35, 0.08) for _ in range(200)]
    xs = [0.5 + r * math.cos(t) for r, t in zip(radii, theta)]
    ys = [0.5 + r * math.sin(t) for r, t in zip(radii, theta)]
    ax.scatter(xs, ys, c=[fg], alpha=0.3, s=2)


def _draw_spikes(ax, fg: tuple, rng: random.Random) -> None:
    """Festival EDM: sharp vertical spikes from center."""

    n = 180
    for i in range(n):
        angle = i * 2 * math.pi / n
        length = 0.1 + abs(rng.gauss(0, 0.22))
        x0, y0 = 0.5, 0.5
        x1 = 0.5 + length * math.cos(angle)
        y1 = 0.5 + length * math.sin(angle)
        alpha = min(1.0, length * 2)
        ax.plot([x0, x1], [y0, y1], color=fg, alpha=alpha, linewidth=0.8)


def _draw_laser_grid(ax, fg: tuple, rng: random.Random) -> None:
    """Cosmic electro: perspective grid with glow."""
    for i in range(20):
        y = i / 20
        alpha = 0.15 + 0.4 * (1 - abs(y - 0.5) * 2)
        ax.axhline(y, color=fg, alpha=alpha, linewidth=0.6)
    for i in range(20):
        x = i / 20
        alpha = 0.15 + 0.4 * (1 - abs(x - 0.5) * 2)
        ax.axvline(x, color=fg, alpha=alpha, linewidth=0.6)
    # Center glow
    for r in [0.02, 0.05, 0.1, 0.18]:
        alpha = 0.6 / (r * 30 + 1)
        ax.add_patch(
            __import__("matplotlib.patches", fromlist=["Circle"]).Circle(
                (0.5, 0.5), r, fill=True, color=fg, alpha=alpha
            )
        )


def _draw_particles(ax, fg: tuple, rng: random.Random) -> None:
    """Ambient: floating particles with size variation, soft."""
    n = 300
    xs = [rng.gauss(0.5, 0.28) for _ in range(n)]
    ys = [rng.gauss(0.5, 0.28) for _ in range(n)]
    sizes = [rng.expovariate(8) * 60 for _ in range(n)]
    alphas = [rng.uniform(0.05, 0.4) for _ in range(n)]
    for x, y, s, a in zip(xs, ys, sizes, alphas):
        ax.scatter([x], [y], s=s, c=[fg], alpha=a)


def _draw_organic(ax, fg: tuple, rng: random.Random) -> None:
    """Jazz: organic curves, like brushstrokes."""
    import numpy as np

    for _ in range(25):
        t = np.linspace(0, 1, 100)
        cx = rng.uniform(0.1, 0.9)
        cy = rng.uniform(0.1, 0.9)
        rx = rng.uniform(0.05, 0.35)
        ry = rng.uniform(0.03, 0.2)
        angle = rng.uniform(0, math.pi)
        x = (
            cx
            + rx * np.cos(t * 2 * math.pi) * math.cos(angle)
            - ry * np.sin(t * 2 * math.pi) * math.sin(angle)
        )
        y = (
            cy
            + rx * np.cos(t * 2 * math.pi) * math.sin(angle)
            + ry * np.sin(t * 2 * math.pi) * math.cos(angle)
        )
        ax.plot(x, y, color=fg, alpha=rng.uniform(0.05, 0.35), linewidth=rng.uniform(0.5, 2.5))


def _draw_ornate(ax, fg: tuple, rng: random.Random) -> None:
    """Classical: symmetric ornamental pattern."""
    import numpy as np

    for k in range(1, 9):
        t = np.linspace(0, 2 * math.pi, 400)
        r = 0.1 + 0.35 * (k / 8) * (1 + 0.3 * np.sin(k * 4 * t))
        x = 0.5 + r * np.cos(t)
        y = 0.5 + r * np.sin(t)
        ax.plot(x, y, color=fg, alpha=0.3 + 0.07 * k, linewidth=0.6)


def _draw_grain(ax, fg: tuple, rng: random.Random) -> None:
    """Lo-fi: noise grain texture."""
    import numpy as np

    n = 4000
    xs = np.random.uniform(0, 1, n)
    ys = np.random.uniform(0, 1, n)
    alphas = np.random.uniform(0.02, 0.12, n)
    sizes = np.random.uniform(0.5, 4, n)
    for x, y, a, s in zip(xs[:500], ys[:500], alphas[:500], sizes[:500]):
        ax.scatter([x], [y], s=s, c=[fg], alpha=a)
    # Horizontal scan lines
    for i in range(0, 100, 3):
        ax.axhline(i / 100, color=fg, alpha=0.04, linewidth=0.5)


def _draw_streaks(ax, fg: tuple, rng: random.Random) -> None:
    """DnB: horizontal motion streaks."""
    for _ in range(80):
        y = rng.random()
        x0 = rng.uniform(-0.1, 0.3)
        length = rng.expovariate(3)
        alpha = rng.uniform(0.1, 0.7)
        lw = rng.uniform(0.3, 2.0)
        ax.plot(
            [x0, x0 + length], [y, y + rng.gauss(0, 0.005)], color=fg, alpha=alpha, linewidth=lw
        )


def _draw_mandala(ax, fg: tuple, rng: random.Random) -> None:
    """World: mandala-like geometric pattern."""
    import numpy as np

    for k in range(1, 12):
        n_pts = k * 6
        t = np.linspace(0, 2 * math.pi, n_pts + 1)
        r = 0.04 * k
        x = 0.5 + r * np.cos(t)
        y = 0.5 + r * np.sin(t)
        ax.fill(x, y, color=fg, alpha=0.08)
        ax.plot(x, y, color=fg, alpha=0.25, linewidth=0.6)


def _draw_spectrum(ax, fg: tuple, rng: random.Random) -> None:
    """Anthology: full color spectrum."""

    n = 500
    for i in range(n):
        hue = i / n
        import colorsys

        r, g, b = colorsys.hsv_to_rgb(hue, 0.9, 0.9)
        angle = hue * 2 * math.pi
        dist = 0.05 + rng.expovariate(4) * 0.4
        x = 0.5 + dist * math.cos(angle)
        y = 0.5 + dist * math.sin(angle)
        ax.scatter([x], [y], c=[(r, g, b)], s=rng.uniform(5, 25), alpha=0.5)


def _draw_minimal(ax, fg: tuple, rng: random.Random) -> None:
    """Pop/default: clean minimal lines."""
    for i in range(3):
        offset = (i - 1) * 0.12
        ax.plot(
            [0.15, 0.85],
            [0.5 + offset, 0.5 + offset],
            color=fg,
            alpha=0.6 - abs(offset) * 2,
            linewidth=1.5 - abs(offset) * 3,
        )


def _draw_pixel(ax, fg: tuple, rng: random.Random) -> None:
    """Video game: pixelated pattern."""

    grid = 20
    for i in range(grid):
        for j in range(grid):
            if rng.random() < 0.35:
                x = i / grid
                y = j / grid
                alpha = rng.uniform(0.3, 0.9)
                ax.add_patch(
                    __import__("matplotlib.patches", fromlist=["Rectangle"]).Rectangle(
                        (x, y),
                        1 / grid * 0.9,
                        1 / grid * 0.9,
                        color=fg,
                        alpha=alpha,
                    )
                )


def _draw_distorted_wave(ax, fg: tuple, rng: random.Random) -> None:
    """Dubstep: distorted waveform."""
    import numpy as np

    t = np.linspace(0, 1, 2000)
    y = 0.5 + 0.35 * np.sin(2 * math.pi * 3 * t)
    y += 0.1 * np.sin(2 * math.pi * 17 * t)
    y += 0.05 * np.random.normal(0, 1, len(t))
    # Hard clip — the dubstep aesthetic
    y = np.clip(y, 0.15, 0.85)
    ax.plot(t, y, color=fg, alpha=0.8, linewidth=1.2)
    ax.fill_between(t, 0.5, y, color=fg, alpha=0.15)


DRAWERS = {
    "radial_sweep": _draw_radial_sweep,
    "spikes": _draw_spikes,
    "laser_grid": _draw_laser_grid,
    "particles": _draw_particles,
    "organic": _draw_organic,
    "ornate": _draw_ornate,
    "grain": _draw_grain,
    "streaks": _draw_streaks,
    "mandala": _draw_mandala,
    "spectrum": _draw_spectrum,
    "minimal": _draw_minimal,
    "pixel": _draw_pixel,
    "distorted_wave": _draw_distorted_wave,
    "grid_harsh": _draw_laser_grid,  # reuse grid for techno
    "electric": _draw_spikes,
    "fractal": _draw_ornate,
    "velvet": _draw_particles,
    "disco": _draw_radial_sweep,
    "wood": _draw_grain,
    "rhythm": _draw_radial_sweep,
    "noise": _draw_grain,
    "horizon": _draw_streaks,
    "garish": _draw_spectrum,
}


def make_cover(album_stem: str, out_path: Path, seed: int = 0) -> Path:
    """Generate a cover image for an album."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  matplotlib required: pip install matplotlib")
        return out_path

    # Load album info
    album_dir = REPO / "albums" / f"{album_stem}.py"
    title = album_stem.replace("_", " ").title()
    genre_label = ""
    if album_dir.exists():
        spec = importlib.util.spec_from_file_location("_a", album_dir)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        alb = getattr(mod, "ALBUM", {})
        title = alb.get("title", title)
        genre_label = alb.get("genre", "")

    style = STYLES.get(album_stem, DEFAULT_STYLE)
    bg = _hex_to_rgb(style["bg"])
    fg = _hex_to_rgb(style["fg"])
    draw_fn = DRAWERS.get(style["style"], _draw_minimal)
    rng = random.Random(seed or hash(album_stem) % 99999)

    fig, ax = plt.subplots(1, 1, figsize=(4, 4), dpi=200)
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.axis("off")

    # Draw genre-specific art
    draw_fn(ax, fg, rng)

    # Title text
    ax.text(
        0.5,
        0.12,
        title.upper(),
        ha="center",
        va="center",
        color=fg,
        fontsize=10,
        fontweight="bold",
        transform=ax.transAxes,
        fontfamily="monospace",
        alpha=0.9,
    )
    if genre_label:
        ax.text(
            0.5,
            0.06,
            genre_label.upper(),
            ha="center",
            va="center",
            color=fg,
            fontsize=5,
            transform=ax.transAxes,
            fontfamily="monospace",
            alpha=0.55,
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out_path), bbox_inches="tight", pad_inches=0, dpi=200)
    plt.close(fig)
    return out_path


def main() -> None:
    from albums.render import discover_albums

    parser = argparse.ArgumentParser(description="Generate album cover art")
    parser.add_argument("--album", help="Single album stem")
    parser.add_argument("--all", action="store_true", help="All albums")
    parser.add_argument("--out-dir", type=Path, default=REPO / "dist" / "covers")
    args = parser.parse_args()

    stems = discover_albums() if args.all else ([args.album] if args.album else [])
    if not stems:
        parser.print_help()
        return

    for stem in stems:
        out = args.out_dir / f"{stem}.png"
        print(f"  {stem} → {out.name} ... ", end="", flush=True)
        make_cover(stem, out)
        print("done")


if __name__ == "__main__":
    main()
