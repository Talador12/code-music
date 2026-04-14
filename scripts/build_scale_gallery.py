"""Build an HTML gallery of all 44 scales.

Renders every scale in the atlas as a C-rooted ascending run using a piano
preset. Generates docs/scales.html with inline audio players grouped by
category (diatonic, pentatonic, exotic, modal).
"""

from __future__ import annotations

import base64
import html
import io
import sys
import wave
from pathlib import Path

import numpy as np


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


def build():
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    from code_music import scale
    from code_music.engine import SCALES
    from code_music.sound_design import PRESETS

    sr = 22050
    piano = PRESETS["pm_guitar"]  # plucked sound is clearer for scales

    # Categorize scales
    categories = {
        "Diatonic": ["major", "minor", "harmonic_minor", "melodic_minor"],
        "Modal": [
            "dorian",
            "phrygian",
            "lydian",
            "mixolydian",
            "locrian",
            "aeolian",
            "ionian",
        ],
        "Pentatonic": [
            "pentatonic",
            "pentatonic_minor",
            "pentatonic_blues",
        ],
        "Blues & Jazz": ["blues", "bebop_dominant", "bebop_major"],
        "Exotic": [],  # everything else
    }
    categorized = set()
    for names in categories.values():
        categorized.update(names)
    categories["Exotic"] = sorted(name for name in SCALES if name not in categorized)

    total = 0
    sections_html = []

    for cat_name, scale_names in categories.items():
        if not scale_names:
            continue
        cards = []
        for name in scale_names:
            if name not in SCALES:
                continue
            try:
                notes = scale("C", name, octave=4, length=8)
                parts = []
                for note in notes:
                    from code_music.engine import _NOTE_SEMITONES

                    semi = _NOTE_SEMITONES.get(str(note.pitch), 0)
                    freq = 440.0 * (2.0 ** ((semi + note.octave * 12 - 69) / 12.0))
                    mono = piano.render(freq, 0.35, sr)
                    parts.append(mono)
                audio = np.concatenate(parts) if parts else np.zeros(sr)
            except Exception:
                audio = np.zeros(sr)

            wav_bytes = _mono_to_wav_bytes(audio, sr)
            b64 = base64.b64encode(wav_bytes).decode("ascii")
            data_uri = f"data:audio/wav;base64,{b64}"

            intervals = SCALES[name]
            interval_str = "-".join(str(i) for i in intervals)

            cards.append(
                f'<div class="scale-card">'
                f'<span class="scale-name">{html.escape(name)}</span>'
                f'<span class="intervals">{interval_str}</span>'
                f'<audio controls preload="none" src="{data_uri}"></audio>'
                f"</div>"
            )
            total += 1

        sections_html.append(
            f"<section>"
            f'<h2>{html.escape(cat_name)} <span class="count">({len(cards)})</span></h2>'
            f'<div class="grid">{"".join(cards)}</div>'
            f"</section>"
        )

    page = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Scale Atlas - All {total} Scales</title>
<style>
:root {{
  --bg:#0a0a10; --bg2:#12121a; --bg3:#1a1a25;
  --fg:#e0e0e0; --fg2:#888; --accent:#7755ff; --green:#44cc88;
  --mono:"SF Mono","Fira Code",Menlo,Consolas,monospace;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:var(--mono); background:var(--bg); color:var(--fg); }}
header {{ padding:30px 40px; border-bottom:1px solid var(--bg3); }}
header h1 {{ color:var(--accent); font-size:22px; margin-bottom:4px; }}
header p {{ color:var(--fg2); font-size:13px; }}
section {{ padding:20px 40px; }}
h2 {{ color:var(--accent); font-size:16px; margin-bottom:12px; }}
h2 .count {{ color:var(--fg2); font-size:12px; }}
.grid {{
  display:grid; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr));
  gap:10px; margin-bottom:20px;
}}
.scale-card {{
  background:var(--bg2); border:1px solid var(--bg3); border-radius:6px;
  padding:10px 14px;
}}
.scale-name {{ color:var(--green); font-size:13px; font-weight:bold; display:block; }}
.intervals {{ color:var(--fg2); font-size:11px; display:block; margin:2px 0 6px; }}
audio {{ width:100%; height:24px; }}
</style>
</head>
<body>
<header>
  <h1>Scale Atlas</h1>
  <p>{total} scales, all rooted on C, rendered with plucked guitar. Listen and compare.</p>
</header>
{"".join(sections_html)}
</body>
</html>"""

    out = project_root / "docs" / "scales.html"
    out.write_text(page)
    print(f"Generated {out} ({total} scales)")


if __name__ == "__main__":
    build()
