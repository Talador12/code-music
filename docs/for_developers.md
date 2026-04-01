# For Developers

Architecture, extension points, and contribution guide.

## Quick orientation

```
code_music/
  engine.py      Primitives: Note, Chord, Beat, Track, Song + all helpers
  synth.py       Renders Song → numpy float64 stereo array
  effects.py     All audio effects (scipy/numpy, O(N log N))
  export.py      WAV (stdlib), MP3/FLAC/OGG (pydub + ffmpeg)
  midi.py        MIDI import/export — pure stdlib, no mido
  notation.py    LilyPond, ABC, MusicXML exporters
  voice.py       Voice synthesis: say / Bark / ElevenLabs / OpenAI backends
  cli.py         `code-music` entry point, --watch live-reload

songs/           Full compositions — each defines a `song` variable
samples/         Short instrument/technique demos
scales/          Guided scale demos + grouping metadata
styles/          Genre theory profiles (pure Python dicts)
scripts/         Interactive tools (scale player, arp renderer)
tests/           pytest suite
```

## Data flow

```
Song (engine.py)
  └─ Track[] → Synth.render_track() → mono float64 numpy array
  └─ VoiceTrack[] → voice.render_voice_track() → stereo float64
       └─ timeline sizing uses VoiceTrack.estimate_total_beats(bpm)
  └─ song.effects dict → EffectsChain or callable per-track, applied post-render
  └─ all tracks mixed → master bus → tanh soft clip → stereo float64
       └─ export_wav / export_mp3 / export_flac / export_midi / notation
```

## The Note / Beat model

```python
Note(pitch="C", octave=4, duration=1.0, velocity=0.8)
# pitch: str name, MIDI int, or None (rest)
# duration: beats (1.0 = quarter note at any BPM)
# velocity: 0.0–1.0 amplitude

Beat(event=note_or_chord_or_none)   # single rhythmic slot
Track.beats: list[Beat]             # the track timeline
```

The synth walks `Track.beats` sequentially, converting each Beat to
samples and writing to a pre-allocated buffer. Cursor advances by
`beat.duration * beat_sec * sample_rate` samples per beat.

## Adding a new instrument preset

Add an entry to `Synth.PRESETS` in `code_music/synth.py`:

```python
"my_preset": {
    "wave":     "sawtooth",   # sine | square | sawtooth | triangle |
                               # supersaw | reese | hoover | moog | fm |
                               # formant | porta | noise | wobble
    "harmonics": 8,            # additive harmonic count
    "A": 0.01,                 # ADSR attack seconds
    "D": 0.1,                  # decay
    "S": 0.8,                  # sustain level (0–1)
    "R": 0.3,                  # release
    # optional:
    "lfo_rate":       2.0,     # enables per-note LFO LP filter (wobble)
    "lfo_min_cutoff": 80.0,
    "lfo_max_cutoff": 4000.0,
    "formant":        "a",     # "a"|"e"|"i"|"o"|"u" — enables formant filter
},
```

Existing wave types live in `Synth._wave()`. Add a new `elif wave == "..."` branch
returning a numpy array of shape `(n_samples,)`.

## Adding a new effect

Add a function to `code_music/effects.py`:

```python
def my_effect(
    samples: FloatArray,    # stereo float64, shape (N, 2)
    sample_rate: int = 44100,
    my_param: float = 1.0,
) -> FloatArray:
    """Brief description."""
    # ... scipy/numpy operations ...
    return result.astype(np.float64)
```

Then export from `code_music/__init__.py`. All effects must:
- Accept `(samples, sample_rate, **kwargs)` as their first two args
- Return the same shape as input
- Never use Python-level sample loops (use scipy/numpy for performance)
- Keep output in `[-1.0, 1.0]` range

## Adding a new scale

Add an entry to `SCALES` in `code_music/engine.py`:

```python
SCALES["my_scale"] = [0, 2, 3, 6, 7, 9, 11]   # semitone intervals from root
```

Then generate the scale file:

```bash
# Add to the SCALES list in scripts/play_scales.py and run:
.venv/bin/python -c "
from code_music.engine import SCALES
# verify it's there
print(SCALES['my_scale'])
"
```

## Adding a new song

Create `songs/my_song.py`. Must define a module-level `song` variable:

```python
from code_music import Song, Track, Note

song = Song(title="My Song", bpm=128)
tr = song.add_track(Track(name="lead", instrument="supersaw"))
tr.add(Note("A", 4, 4.0))
```

```bash
make play-my_song              # renders + plays
make songs-all                 # included in batch renders automatically
```

## The `song.effects` hook

Post-render per-track effect chain using `EffectsChain`:

```python
from code_music import EffectsChain, reverb, delay

song.effects = {
    "pad": EffectsChain().add(reverb, room_size=0.7, wet=0.3),
    "lead": EffectsChain().add(delay, delay_ms=250, wet=0.2).add(reverb, room_size=0.4, wet=0.15),
}
```

Applied in `Synth.render_song()` after each track is rendered to stereo,
before mixing into the master bus. Exceptions are caught silently — a buggy
effect never crashes the render. Plain callables `(samples, sr) → samples`
also work for backward compatibility.

## Adding a new notation exporter

Add a function to `code_music/notation.py` following the pattern:

```python
def export_myformat(song: Song, path: str | Path) -> Path:
    """Export to .xyz format."""
    out = Path(path).with_suffix(".xyz")
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for track in song.tracks:
        for beat in track.beats:
            # ... convert beat.event (Note|Chord|None) to format ...
    out.write_text("\n".join(lines))
    return out
```

Export it from `__init__.py` and add a Makefile target.

## Running tests

```bash
make test                      # full suite
.venv/bin/pytest tests/test_engine.py -v       # one module
.venv/bin/pytest -k "test_trill" -v            # one test by name
```

Tests use `sample_rate=22050` for speed. Production renders use 44100.

## Lint

```bash
make lint
# or auto-fix:
.venv/bin/ruff check code_music tests songs samples scales scripts --fix
```

## Performance notes

- `Synth._wave()` is fully vectorised with numpy broadcasting — no Python loops
- `effects.py` uses `scipy.signal.sosfilt` / `fftconvolve` — O(N log N)
- The reverb uses FFT convolution with a synthetic IR — fast at any signal length
- Long notes (>4 bars) should be broken into 1-bar repeats in song scripts
  to avoid allocating huge single buffers
- `render_song()` pre-allocates the full stereo mix buffer once

## Adding a voice backend

Add a function `_generate_mybackend(clip: VoiceClip, target_sr: int) → FloatArray`
to `code_music/voice.py`, then add it to the `generate()` dispatch and
`detect_backends()` check.

## CI

GitHub Actions on push to `main`:
- Python 3.11 + 3.12
- `ruff check`
- `pytest tests/ -v`
- Smoke renders: hello_world, clarity_drive, lollipop_laser, deep_space_drift

See `.github/workflows/ci.yml`.

## pyproject.toml

```toml
[project.scripts]
code-music = "code_music.cli:main"
```

Install in editable mode with `pip install -e ".[dev]"`.
Dev extras: pytest, ruff.

---

*Back to [README](../README.md)*
