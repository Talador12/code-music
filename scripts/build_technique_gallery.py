"""Build a synthesis technique comparison gallery.

Renders the same melody through 7 synthesis techniques, encodes as
base64 WAV data URIs, and generates docs/techniques.html with inline
audio players and waveform SVGs for side-by-side comparison.
"""

from __future__ import annotations

import base64
import html
import io
import sys
import wave
from pathlib import Path

import numpy as np


def _render_sd(sd, notes, sr):
    """Render a SoundDesigner through a list of (freq, dur) notes."""
    parts = []
    for freq, dur in notes:
        mono = sd.render(freq, dur, sr)
        parts.append(mono)
    if not parts:
        return np.zeros(sr)
    return np.concatenate(parts)


def _mono_to_wav_bytes(mono, sr):
    clipped = np.clip(mono, -1.0, 1.0)
    peak = np.max(np.abs(clipped))
    if peak > 0:
        clipped = clipped / peak * 0.9
    int16 = (clipped * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(int16.tobytes())
    return buf.getvalue()


def _waveform_svg(mono, width=400, height=60):
    n = len(mono)
    if n == 0:
        return ""
    step = max(1, n // width)
    lines = []
    for i in range(0, min(n, width * step), step):
        chunk = mono[i : i + step]
        x = len(lines)
        hi = float(np.max(chunk))
        lo = float(np.min(chunk))
        y_hi = height / 2 - hi * (height / 2 - 2)
        y_lo = height / 2 - lo * (height / 2 - 2)
        lines.append(
            f'<line x1="{x}" y1="{y_hi:.1f}" x2="{x}" y2="{y_lo:.1f}" '
            f'stroke="#7755ff" stroke-width="1" />'
        )
    return (
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="background:#12121a;border-radius:4px;">'
        f'<line x1="0" y1="{height // 2}" x2="{width}" y2="{height // 2}" '
        f'stroke="#333" stroke-width="1" />'
        f"{''.join(lines)}"
        f"</svg>"
    )


def build():
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    from code_music.sound_design import (
        SoundDesigner,
        Wavetable,
    )

    sr = 22050

    # Common melody: C major scale ascending then descending
    melody = [
        (261.63, 0.3),
        (293.66, 0.3),
        (329.63, 0.3),
        (349.23, 0.3),
        (392.00, 0.3),
        (440.00, 0.3),
        (493.88, 0.3),
        (523.25, 0.6),
        (493.88, 0.3),
        (440.00, 0.3),
        (392.00, 0.3),
        (349.23, 0.3),
        (329.63, 0.3),
        (293.66, 0.3),
        (261.63, 0.6),
    ]

    # 7 synthesis techniques
    techniques = [
        (
            "Subtractive",
            "Classic analog: oscillator -> filter -> envelope. The bread and butter.",
            SoundDesigner("subtractive")
            .add_osc("sawtooth", volume=0.5)
            .add_osc("sawtooth", detune_cents=7, volume=0.4)
            .envelope(attack=0.02, decay=0.15, sustain=0.6, release=0.3)
            .filter("lowpass", cutoff=3000, resonance=0.6),
        ),
        (
            "FM Synthesis",
            "Frequency modulation: one oscillator modulates another. Bell-like timbres.",
            SoundDesigner("fm")
            .fm("sine", mod_ratio=2.0, mod_index=3.5, volume=0.7)
            .envelope(attack=0.01, decay=0.2, sustain=0.4, release=0.3)
            .filter("lowpass", cutoff=5000, resonance=0.3),
        ),
        (
            "Wavetable",
            "Single-cycle waveforms with morphing. Rich, evolving timbres.",
            SoundDesigner("wavetable")
            .add_wavetable(Wavetable.from_harmonics([1.0, 0.5, 0.25, 0.125]), volume=0.6)
            .add_wavetable(Wavetable.from_wave("sawtooth"), volume=0.3, detune_cents=5)
            .envelope(attack=0.03, decay=0.1, sustain=0.7, release=0.4)
            .filter("lowpass", cutoff=4000, resonance=0.5),
        ),
        (
            "Wavetable Scanning",
            "LFO sweeps through a bank of tables. Animated, breathing sound.",
            SoundDesigner("wt_scan")
            .wavetable_scan(
                [
                    Wavetable.from_wave("sine"),
                    Wavetable.from_wave("sawtooth"),
                    Wavetable.from_wave("square"),
                    Wavetable.from_wave("triangle"),
                ],
                scan_rate=0.4,
                volume=0.6,
            )
            .envelope(attack=0.05, decay=0.1, sustain=0.7, release=0.3)
            .filter("lowpass", cutoff=3500, resonance=0.5),
        ),
        (
            "Granular",
            "Tiny grains scattered in time. Cloud-like, ethereal textures.",
            SoundDesigner("granular")
            .granular(grain_size=0.04, density=15, scatter=0.5, seed=42)
            .envelope(attack=0.1, decay=0.1, sustain=0.8, release=0.5)
            .filter("lowpass", cutoff=4000, resonance=0.4),
        ),
        (
            "Physical Modeling (Plucked)",
            "Karplus-Strong: short noise burst -> delay line -> filter. Realistic strings.",
            SoundDesigner("karplus")
            .physical_model("karplus_strong", decay=0.996, brightness=0.5, volume=0.8)
            .envelope(attack=0.001, decay=0.3, sustain=0.2, release=0.4),
        ),
        (
            "Physical Modeling (Bowed)",
            "Continuous friction excitation. Sustained violin-like tone.",
            SoundDesigner("bowed")
            .physical_model("bowed_string", bow_pressure=0.5, brightness=0.6, volume=0.8)
            .envelope(attack=0.08, decay=0.15, sustain=0.8, release=0.4)
            .filter("lowpass", cutoff=5000, resonance=0.3),
        ),
    ]

    cards = []
    for name, desc, sd in techniques:
        try:
            mono = _render_sd(sd, melody, sr)
        except Exception as e:
            print(f"  Warning: {name} failed: {e}")
            mono = np.zeros(sr)

        wav_bytes = _mono_to_wav_bytes(mono, sr)
        b64 = base64.b64encode(wav_bytes).decode("ascii")
        data_uri = f"data:audio/wav;base64,{b64}"
        svg = _waveform_svg(mono)

        cards.append(
            f'<div class="tech-card">'
            f"<h3>{html.escape(name)}</h3>"
            f'<p class="desc">{html.escape(desc)}</p>'
            f"{svg}"
            f'<audio controls preload="none" src="{data_uri}"></audio>'
            f"</div>"
        )

    page = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Synthesis Technique Comparison</title>
<style>
:root {{
  --bg:#0a0a10; --bg2:#12121a; --bg3:#1a1a25;
  --fg:#e0e0e0; --fg2:#888; --accent:#7755ff;
  --green:#44cc88; --mono:"SF Mono","Fira Code",Menlo,Consolas,monospace;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:var(--mono); background:var(--bg); color:var(--fg); }}
header {{ padding:30px 40px; border-bottom:1px solid var(--bg3); }}
header h1 {{ color:var(--accent); font-size:22px; margin-bottom:4px; }}
header p {{ color:var(--fg2); font-size:13px; }}
.grid {{
  display:grid; grid-template-columns:repeat(auto-fill, minmax(420px, 1fr));
  gap:16px; padding:30px 40px;
}}
.tech-card {{
  background:var(--bg2); border:1px solid var(--bg3); border-radius:8px;
  padding:18px;
}}
.tech-card h3 {{ color:var(--green); font-size:15px; margin-bottom:6px; }}
.desc {{ color:var(--fg2); font-size:12px; margin-bottom:10px; }}
audio {{ width:100%; height:28px; margin-top:8px; }}
</style>
</head>
<body>
<header>
  <h1>Synthesis Technique Comparison</h1>
  <p>Same melody (C major scale), 7 different synthesis methods. Listen to the difference.</p>
</header>
<div class="grid">
  {"".join(cards)}
</div>
</body>
</html>"""

    out = project_root / "docs" / "techniques.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    print(f"Generated {out} ({len(techniques)} techniques)")


if __name__ == "__main__":
    build()
