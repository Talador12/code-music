# code-music

Code-generated music: write Python blocks, export Spotify-ready audio.

## Setup

```
make dev          # create .venv, install deps, check ffmpeg
make test         # run the test suite
make render-all   # render all example songs to output/
```

Requires Python 3.11+. MP3 export requires `ffmpeg` (`brew install ffmpeg`).

## Architecture

```
code_music/
  engine.py   - Note, Chord, Beat, Track, Song + scale helpers
  synth.py    - Synth: renders Song -> numpy float64 stereo array
  export.py   - export_wav / export_mp3 (pydub + ffmpeg for MP3)
  cli.py      - `code-music <script.py>` entry point

examples/
  hello_world.py   - C major scale, simplest possible song
  lo_fi_loop.py    - 4-bar lo-fi hip-hop loop (Am, multi-track, drums)
  prog_rock.py     - D Dorian prog rock piece with intro/verse/chorus/outro

tests/
  test_engine.py   - unit tests for music primitives
  test_synth.py    - unit tests for synth renderer
```

## Writing a Song

A song script must define a top-level `song` variable:

```python
from code_music import Note, Chord, Track, Song, scale

song = Song(title="My Track", bpm=120)
tr = song.add_track(Track(name="melody", instrument="piano"))
tr.extend(scale("C", "major", octave=4))
```

Run it:

```
code-music my_track.py             # → my_track.wav
code-music my_track.py --mp3       # → my_track.mp3 (needs ffmpeg)
code-music my_track.py --bpm 140   # override BPM
```

## Instruments (Synth Presets)

| Name          | Character                    |
|---------------|------------------------------|
| `sine`        | Pure, smooth                 |
| `square`      | Hollow, buzzy                |
| `sawtooth`    | Bright, cutting              |
| `triangle`    | Soft, mellow                 |
| `piano`       | Fast attack, long decay      |
| `organ`       | Sustained, no decay          |
| `bass`        | Low-end sawtooth             |
| `pad`         | Slow attack, ambient         |
| `pluck`       | Sharp attack, quick decay    |
| `drums_kick`  | Pitch-dropping kick drum     |
| `drums_snare` | Noise-mixed snare            |
| `drums_hat`   | High-frequency hat           |

## Spotify Pipeline

1. Render to 320kbps MP3: `code-music my_track.py --mp3`
2. Spotify for Artists → Music → Upload Track
3. Minimum requirements: 1:30 duration, 44100 Hz, stereo

## Conventions

- Songs live in `examples/` or user-created directories.
- One `song` variable per file; the CLI picks it up via dynamic import.
- `output/` is gitignored — rendered files are not committed.
- Tests use `sample_rate=22050` for speed; production songs use `44100`.
