"""Build an HTML gallery of common chord progressions.

Renders 20 famous progressions in C, each as a chord sequence with piano.
Generates docs/progressions.html with inline audio and Roman numeral labels.
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


_PROGRESSIONS = [
    (
        "I-IV-V-I",
        "The cadential backbone of Western music",
        [("C", "maj"), ("F", "maj"), ("G", "maj"), ("C", "maj")],
    ),
    (
        "I-V-vi-IV",
        "Pop/rock anthem (Let It Be, No Woman No Cry)",
        [("C", "maj"), ("G", "maj"), ("A", "min"), ("F", "maj")],
    ),
    ("ii-V-I", "Jazz standard resolution", [("D", "min7"), ("G", "dom7"), ("C", "maj7")]),
    (
        "I-vi-IV-V",
        "50s doo-wop (Stand By Me)",
        [("C", "maj"), ("A", "min"), ("F", "maj"), ("G", "maj")],
    ),
    (
        "12-bar blues",
        "The foundation of blues and rock",
        [
            ("C", "dom7"),
            ("C", "dom7"),
            ("C", "dom7"),
            ("C", "dom7"),
            ("F", "dom7"),
            ("F", "dom7"),
            ("C", "dom7"),
            ("C", "dom7"),
            ("G", "dom7"),
            ("F", "dom7"),
            ("C", "dom7"),
            ("G", "dom7"),
        ],
    ),
    (
        "vi-IV-I-V",
        "Emotional pop (Someone Like You)",
        [("A", "min"), ("F", "maj"), ("C", "maj"), ("G", "maj")],
    ),
    ("I-IV-vi-V", "Axis of awesome", [("C", "maj"), ("F", "maj"), ("A", "min"), ("G", "maj")]),
    (
        "I-bVII-IV-I",
        "Mixolydian rock (Sweet Home Alabama)",
        [("C", "maj"), ("Bb", "maj"), ("F", "maj"), ("C", "maj")],
    ),
    (
        "i-bVI-bIII-bVII",
        "Andalusian cadence (flamenco/metal)",
        [("A", "min"), ("F", "maj"), ("C", "maj"), ("G", "maj")],
    ),
    ("i-iv-v-i", "Minor cadential", [("A", "min"), ("D", "min"), ("E", "min"), ("A", "min")]),
    (
        "I-III-IV-iv",
        "Creep progression (major to minor IV)",
        [("C", "maj"), ("E", "maj"), ("F", "maj"), ("F", "min")],
    ),
    (
        "ii-V-I-vi",
        "Rhythm changes turnaround",
        [("D", "min7"), ("G", "dom7"), ("C", "maj7"), ("A", "min7")],
    ),
    (
        "I-V-vi-iii-IV-I-IV-V",
        "Pachelbel's Canon",
        [
            ("C", "maj"),
            ("G", "maj"),
            ("A", "min"),
            ("E", "min"),
            ("F", "maj"),
            ("C", "maj"),
            ("F", "maj"),
            ("G", "maj"),
        ],
    ),
    (
        "i-bVII-bVI-V",
        "Descending minor (Hit the Road Jack)",
        [("A", "min"), ("G", "maj"), ("F", "maj"), ("E", "maj")],
    ),
    (
        "IV-V-iii-vi",
        "Royal road (J-pop standard)",
        [("F", "maj"), ("G", "maj"), ("E", "min"), ("A", "min")],
    ),
    ("I-IV-I-V", "Simple folk/country", [("C", "maj"), ("F", "maj"), ("C", "maj"), ("G", "maj")]),
    ("i-iv-VII-III", "Natural minor pop", [("A", "min"), ("D", "min"), ("G", "maj"), ("C", "maj")]),
    ("I-V-IV-V", "Rock shuffle", [("C", "maj"), ("G", "maj"), ("F", "maj"), ("G", "maj")]),
    (
        "ii-V-I-IV",
        "Jazz with subdominant detour",
        [("D", "min7"), ("G", "dom7"), ("C", "maj7"), ("F", "maj7")],
    ),
    ("I-bII-I", "Neapolitan resolution", [("C", "maj"), ("Db", "maj"), ("C", "maj")]),
]


def build():
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    from code_music.engine import CHORD_SHAPES
    from code_music.sound_design import PRESETS

    sr = 22050
    piano = PRESETS.get("fm_electric_piano", PRESETS.get("pm_guitar"))

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

    cards = []
    for name, desc, chords in _PROGRESSIONS:
        dur_per_chord = 1.2
        parts = []
        for root, shape in chords:
            offsets = CHORD_SHAPES.get(shape, [0, 4, 7])
            root_semi = _SEMI.get(root, 0)
            n_samples = int(sr * dur_per_chord)
            mix = np.zeros(n_samples, dtype=np.float64)
            for offset in offsets:
                midi = 48 + root_semi + offset  # C3 base
                freq = 440.0 * (2.0 ** ((midi - 69) / 12.0))
                try:
                    mono = piano.render(freq, dur_per_chord, sr)
                    if len(mono) > n_samples:
                        mono = mono[:n_samples]
                    mix[: len(mono)] += mono * 0.25
                except Exception:
                    t = np.linspace(0, dur_per_chord, n_samples)
                    mix += np.sin(2 * np.pi * freq * t) * 0.1
            parts.append(mix)

        audio = np.concatenate(parts)
        wav_bytes = _mono_to_wav_bytes(audio, sr)
        b64 = base64.b64encode(wav_bytes).decode("ascii")

        chord_labels = " - ".join(f"{r} {s}" for r, s in chords)

        cards.append(
            f'<div class="prog-card">'
            f"<h3>{html.escape(name)}</h3>"
            f'<p class="desc">{html.escape(desc)}</p>'
            f'<p class="chords">{html.escape(chord_labels)}</p>'
            f'<audio controls preload="none" src="data:audio/wav;base64,{b64}"></audio>'
            f"</div>"
        )

    page = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chord Progression Gallery - {len(_PROGRESSIONS)} Progressions</title>
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
.grid {{
  display:grid; grid-template-columns:repeat(auto-fill, minmax(380px, 1fr));
  gap:14px; padding:30px 40px;
}}
.prog-card {{
  background:var(--bg2); border:1px solid var(--bg3); border-radius:8px;
  padding:14px 18px;
}}
.prog-card h3 {{ color:var(--green); font-size:14px; margin-bottom:4px; }}
.desc {{ color:var(--fg2); font-size:12px; margin-bottom:6px; }}
.chords {{ color:var(--orange); font-size:11px; margin-bottom:8px; }}
audio {{ width:100%; height:28px; }}
</style>
</head>
<body>
<header>
  <h1>Chord Progression Gallery</h1>
  <p>{len(_PROGRESSIONS)} famous progressions. All rendered in C with electric piano.</p>
</header>
<div class="grid">
  {"".join(cards)}
</div>
</body>
</html>"""

    out = project_root / "docs" / "progressions.html"
    out.write_text(page)
    print(f"Generated {out} ({len(_PROGRESSIONS)} progressions)")


if __name__ == "__main__":
    build()
