"""Build an HTML gallery of SoundDesigner presets.

Usage: python scripts/build_gallery.py
Output: docs/gallery.html

Renders every SoundDesigner preset at 3 pitches (C3, C4, C5), encodes
them as base64 WAV data URIs, and generates a single-page HTML gallery
with inline audio players and waveform visualizations.
"""

from __future__ import annotations

import base64
import html
import io
import sys
import wave
from pathlib import Path

import numpy as np


def _render_preset(preset, freq: float, duration: float, sr: int) -> np.ndarray:
    """Render a SoundDesigner preset to mono float64."""
    try:
        return preset.render(freq, duration, sr)
    except Exception:
        return np.zeros(int(sr * duration))


def _mono_to_wav_bytes(mono: np.ndarray, sr: int) -> bytes:
    """Convert mono float64 to WAV bytes."""
    clipped = np.clip(mono, -1.0, 1.0)
    int16 = (clipped * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(int16.tobytes())
    return buf.getvalue()


def _waveform_svg(mono: np.ndarray, width: int = 300, height: int = 60) -> str:
    """Generate an inline SVG waveform visualization."""
    n = len(mono)
    if n == 0:
        return ""
    # Downsample to width points
    step = max(1, n // width)
    points = []
    for i in range(0, min(n, width * step), step):
        chunk = mono[i : i + step]
        hi = float(np.max(chunk))
        lo = float(np.min(chunk))
        x = len(points)
        y_hi = height / 2 - hi * (height / 2 - 2)
        y_lo = height / 2 - lo * (height / 2 - 2)
        points.append((x, y_hi, y_lo))

    path_parts = []
    for x, y_hi, y_lo in points:
        path_parts.append(
            f'<line x1="{x}" y1="{y_hi:.1f}" x2="{x}" y2="{y_lo:.1f}" '
            f'stroke="#7755ff" stroke-width="1" />'
        )

    return (
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="background:#12121a;border-radius:4px;">'
        f'<line x1="0" y1="{height // 2}" x2="{width}" y2="{height // 2}" '
        f'stroke="#333" stroke-width="1" />'
        f"{''.join(path_parts)}"
        f"</svg>"
    )


def build_gallery():
    """Generate docs/gallery.html from SoundDesigner presets."""
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    from code_music.sound_design import PRESETS

    sr = 22050
    duration = 1.5
    pitches = [("C3", 130.81), ("C4", 261.63), ("C5", 523.25)]

    preset_cards = []
    for name, preset in sorted(PRESETS.items()):
        pitch_players = []
        for pitch_name, freq in pitches:
            mono = _render_preset(preset, freq, duration, sr)
            wav_bytes = _mono_to_wav_bytes(mono, sr)
            b64 = base64.b64encode(wav_bytes).decode("ascii")
            data_uri = f"data:audio/wav;base64,{b64}"
            svg = _waveform_svg(mono)
            pitch_players.append(
                f'<div class="pitch">'
                f'<span class="pitch-name">{pitch_name}</span>'
                f'<audio controls preload="none" src="{data_uri}"></audio>'
                f"{svg}"
                f"</div>"
            )

        card = (
            f'<div class="preset-card" id="{name}">'
            f"<h3>{html.escape(name)}</h3>"
            f"{''.join(pitch_players)}"
            f"</div>"
        )
        preset_cards.append(card)

    total = len(PRESETS)

    page = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>code-music Preset Gallery</title>
<style>
:root {{
  --bg: #0a0a10; --bg2: #12121a; --bg3: #1a1a25;
  --fg: #e0e0e0; --fg2: #888; --accent: #7755ff;
  --green: #44cc88; --orange: #ffaa44;
  --mono: "SF Mono","Fira Code","JetBrains Mono",Menlo,Consolas,monospace;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:var(--mono); background:var(--bg); color:var(--fg); }}
header {{
  padding:30px 40px; border-bottom:1px solid var(--bg3);
}}
header h1 {{ color:var(--accent); font-size:22px; margin-bottom:4px; }}
header p {{ color:var(--fg2); font-size:13px; }}
.grid {{
  display:grid; grid-template-columns:repeat(auto-fill, minmax(340px, 1fr));
  gap:16px; padding:30px 40px;
}}
.preset-card {{
  background:var(--bg2); border:1px solid var(--bg3); border-radius:8px;
  padding:16px;
}}
.preset-card h3 {{
  color:var(--green); font-size:15px; margin-bottom:12px;
}}
.pitch {{
  margin-bottom:8px;
}}
.pitch-name {{
  color:var(--orange); font-size:11px; font-weight:bold; display:block; margin-bottom:4px;
}}
audio {{
  width:100%; height:28px; margin-bottom:4px;
}}
audio::-webkit-media-controls-panel {{
  background:var(--bg3);
}}
</style>
</head>
<body>
<header>
  <h1>Preset Gallery</h1>
  <p>{total} SoundDesigner presets. Each rendered at C3, C4, C5 (22050 Hz, 1.5s).</p>
</header>
<div class="grid">
  {"".join(preset_cards)}
</div>
</body>
</html>"""

    out_path = project_root / "docs" / "gallery.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page)
    print(f"Generated {out_path} ({total} presets)")


if __name__ == "__main__":
    build_gallery()
