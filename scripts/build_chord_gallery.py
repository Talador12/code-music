"""Build an HTML gallery of all chord shapes.

Renders every chord shape rooted on C using a piano preset. Groups by
category (triads, 7ths, extensions, suspensions, power). Generates
docs/chords.html with inline audio.
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

    from code_music.engine import CHORD_SHAPES
    from code_music.sound_design import PRESETS

    sr = 22050
    piano = PRESETS.get("fm_electric_piano", PRESETS.get("pm_guitar"))

    categories = {
        "Triads": ["maj", "min", "dim", "aug"],
        "Suspensions": ["sus2", "sus4"],
        "Power": ["5"],
        "Seventh Chords": ["maj7", "min7", "dom7", "min7b5", "dim7", "7sus4"],
        "Sixth Chords": ["maj6", "min6"],
        "Extended": ["maj9", "min9", "dom9", "9", "7b9", "7#9"],
        "Other": [],
    }
    categorized = set()
    for names in categories.values():
        categorized.update(names)
    categories["Other"] = sorted(name for name in CHORD_SHAPES if name not in categorized)

    # Note name to semitone
    _SEMI = {
        "C": 0,
        "C#": 1,
        "Db": 1,
        "D": 2,
        "D#": 3,
        "Eb": 3,
        "E": 4,
        "F": 5,
        "F#": 6,
        "Gb": 6,
        "G": 7,
        "G#": 8,
        "Ab": 8,
        "A": 9,
        "A#": 10,
        "Bb": 10,
        "B": 11,
    }
    _NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    total = 0
    sections = []

    for cat_name, shape_names in categories.items():
        if not shape_names:
            continue
        cards = []
        for shape in shape_names:
            if shape not in CHORD_SHAPES:
                continue
            offsets = CHORD_SHAPES[shape]
            note_names = [_NAMES[off % 12] for off in offsets]

            # Render chord: all notes simultaneously (additive)
            dur = 1.5
            n_samples = int(sr * dur)
            mix = np.zeros(n_samples, dtype=np.float64)
            for offset in offsets:
                midi = 60 + offset  # C4 base
                freq = 440.0 * (2.0 ** ((midi - 69) / 12.0))
                try:
                    mono = piano.render(freq, dur, sr)
                    if len(mono) > n_samples:
                        mono = mono[:n_samples]
                    mix[: len(mono)] += mono * 0.3
                except Exception:
                    t = np.linspace(0, dur, n_samples)
                    mix += np.sin(2 * np.pi * freq * t) * 0.15

            wav_bytes = _mono_to_wav_bytes(mix, sr)
            b64 = base64.b64encode(wav_bytes).decode("ascii")

            cards.append(
                f'<div class="chord-card">'
                f'<span class="chord-name">C{html.escape(shape)}</span>'
                f'<span class="notes">{" ".join(note_names)}</span>'
                f'<span class="offsets">[{", ".join(str(o) for o in offsets)}]</span>'
                f'<audio controls preload="none" src="data:audio/wav;base64,{b64}"></audio>'
                f"</div>"
            )
            total += 1

        sections.append(
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
<title>Chord Shape Gallery - {total} Chords</title>
<style>
:root {{
  --bg:#0a0a10; --bg2:#12121a; --bg3:#1a1a25;
  --fg:#e0e0e0; --fg2:#888; --accent:#7755ff; --green:#44cc88; --orange:#ffaa44;
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
  display:grid; grid-template-columns:repeat(auto-fill, minmax(220px, 1fr));
  gap:10px; margin-bottom:20px;
}}
.chord-card {{
  background:var(--bg2); border:1px solid var(--bg3); border-radius:6px;
  padding:10px 14px;
}}
.chord-name {{ color:var(--green); font-size:14px; font-weight:bold; display:block; }}
.notes {{ color:var(--orange); font-size:11px; display:block; margin:2px 0; }}
.offsets {{ color:var(--fg2); font-size:10px; display:block; margin-bottom:6px; }}
audio {{ width:100%; height:24px; }}
</style>
</head>
<body>
<header>
  <h1>Chord Shape Gallery</h1>
  <p>{total} chord shapes, all rooted on C4, rendered with electric piano.</p>
</header>
{"".join(sections)}
</body>
</html>"""

    out = project_root / "docs" / "chords.html"
    out.write_text(page)
    print(f"Generated {out} ({total} chords)")


if __name__ == "__main__":
    build()
