# code-music

[![PyPI version](https://img.shields.io/pypi/v/code-music)](https://pypi.org/project/code-music/)
[![Python 3.11+](https://img.shields.io/pypi/pyversions/code-music)](https://pypi.org/project/code-music/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/github/actions/workflow/status/Talador12/code-music/ci.yml?label=tests)](https://github.com/Talador12/code-music/actions)

Code-generated music. Write Python, hear sound, export to Spotify.

**[Try it in your browser](https://talador12.github.io/code-music/playground.html)** -- no install needed.

---

**Who are you?**

| | |
|---|---|
| 🎧 **Just want to listen** | [Start here →](docs/for_listeners.md) |
| 🎹 **Want to make music (no theory needed)** | [Start here →](docs/for_creators.md) |
| 🎼 **Know your modes and want full control** | [Start here →](docs/for_theory_heads.md) |
| 💻 **Want to understand or extend the code** | [Start here →](docs/for_developers.md) |

---

## What is this?

A Python library and tool set for generating music programmatically — from
a single scale all the way to full multi-track songs with orchestral
instruments, EDM synthesis, jazz arpeggios, and effects chains.

```python
from code_music import Song, Track, Note, Chord, EffectsChain, scale, reverb, play

song = Song(title="My Track", bpm=120)

pad  = song.add_track(Track(instrument="pad",    volume=0.5))
lead = song.add_track(Track(instrument="piano",  volume=0.8))

pad.add(Chord("A", "min7", 3, duration=8.0))
lead.extend(scale("A", "pentatonic", octave=5))

song.effects = {"pad": EffectsChain().add(reverb, room_size=0.7, wet=0.4)}

play(song)  # hear it instantly
```

```bash
code-music my_track.py --flac    # → Spotify-ready FLAC
```

## Install

```bash
pip install code-music              # from PyPI
pip install code-music[play]        # + real-time playback (sounddevice)
```

Or develop from source:

```bash
git clone https://github.com/Talador12/code-music
cd code-music
make dev          # creates .venv, installs deps, checks ffmpeg
make test         # full pytest suite
```

Requires **Python 3.11+**. For MP3/FLAC/OGG export: `brew install ffmpeg`.

## What's in the box

**By the numbers:** 98 effects, 171 instrument presets, 67 genre profiles,
97 chord shapes, 53 scales, 22 export presets, 9 mastering styles, 3705 tests.

| Category | Highlights |
|---|---|
| **Synthesis** | 27-stage per-note pipeline. Band-limited oscillators fill to Nyquist. Exponential ADSR. Karplus-Strong with body resonance. FM with configurable mod ratio. Unison/detune engine. Sub-oscillator. Pink/brown noise. |
| **Realism** | 14 acoustic noise layers (breath, bow rosin, hammer thump, lip buzz, reed, key click, damper release, string release). Per-note vibrato with delayed onset. Pitch drift on sustained notes. Velocity-to-timbre per instrument family. Register-dependent tonal tilt. |
| **Effects** | 98 functions: parametric EQ, dynamic EQ, multiband compress, parallel compress, glue compressor, phaser, flanger, chorus (multi-voice stereo), reverb (early reflections + allpass), shimmer/spring/reverse reverb, convolver (load any IR), amp/cab sim, oversampled distortion, waveshaper (5 curves), saturator (4 analog models), tape emulation, lo-fi vinyl, ring mod, freq shift, pitch correct, formant shift, spectral freeze, volume shaper, stutter, beat slicer, and more. |
| **Articulations** | 33 playing techniques that change timbre, not just duration: pizzicato, sul ponticello, con sordino, harmon mute, brush/mallet/rod, cross-stick, marcato, tenuto, staccatissimo. |
| **Genre transform** | `genre_transform(song, "jazz")` converts any song to any of 67 genres. 7 transform layers: rhythm, harmony, instruments, groove, dynamics, articulation, effects. 28 named rhythm patterns (tresillo, dembow, second line, etc). |
| **Composition** | auto_harmonize, embellish (5 styles), rhythmic_variation (5 styles), chord_substitute (7 types), reharmonize, melodic_inversion, retrograde, melodic_sequence, call_and_response, pedal_tone. 25+ ornament functions. 5 non-chord tone inserters. |
| **Auto-mix** | `auto_mix(song)` sets levels, pans tracks, carves EQ. `master_audio(audio, sr, style="balanced")` runs a 7-stage mastering chain with 9 style presets (balanced, loud, warm, clean, aggressive, hiphop, orchestral, podcast, vinyl). |
| **Export** | 22 platform presets: `--quality spotify-upload`, `--quality apple-lossless`, `--quality archive-master`. 24-bit WAV default, 32-bit float, FLAC, MP3 320k, OGG. TPDF dithering. |
| **Symphony** | Multi-movement orchestral composition. Transposing instruments. MusicXML + LilyPond score export. Part extraction. Big band orchestrator. |
| **Integrations** | music21, pretty_midi, librosa, Csound, SuperCollider, SoX, FluidSynth, AI generation hooks. `--list-integrations` to check. |
| **Rhythm games** | `export_stepmania(song, "chart.sm")` and `export_clone_hero(song, "chart.chart")` with 5 difficulty levels. |

| Directory | What's there |
|---|---|
| `examples/` | 19 step-by-step tutorials: hello world → spatial audio → visualization |
| `songs/` | 400+ songs across 30+ genres |
| `samples/` | 100+ short instrument and technique demos |
| `albums/` | 8 concept albums stubbed (including 118-element Periodic Table) |
| `scales/` | 31 guided scale demos (all 12 keys), plus arpeggio mode |
| `styles/` | Theory profiles for 7 genres (deadmau5, Zedd, bebop, cinematic...) |
| `scripts/` | Interactive scale/arp player with progress bar |
| `code_music/` | The engine, synth, effects, export, notation, transform, symphony, auto_mix, mastering |

## Play something right now

```bash
# Songs
make play-trance_odyssey      # 90s uplifting trance
make play-tank_bebop          # Cowboy Bebop big-band jazz
make play-deep_space_drift    # Brian Eno ambient
make play-clarity_drive       # Zedd-style festival EDM
make play-symphony_no1        # original orchestral movement
make preview-voice_pacing_demo # narration vs rap pacing demo
```

```bash
# Scales and key relationships
make play-scales
make play-scales-arp          # same scales as arpeggios
make play-scales-group GROUP=world
make play-scale-circle_of_fifths # key relationship reference run

# Direct playback (no file written)
code-music songs/trance_odyssey.py --play

# Live coding: auto-render + play on every save
code-music songs/my_wip.py --watch --play

# Import and render a MIDI file
code-music dummy.py --import-midi my_track.mid -o remix.wav

# Generate a random song and play it (no script needed)
code-music --random
code-music --random jazz
```

```python
# Generate a complete song from a genre template
from code_music import generate_song, detect_key, play

song = generate_song("lo_fi", bars=16, seed=42)
play(song)

# Transform any song into a different genre
from code_music import genre_transform
jazz_version = genre_transform(song, "jazz")
bossa = genre_transform(song, "bossa_nova")
metal = genre_transform(song, "melodic_metalcore")

# Auto-mix and master
from code_music import auto_mix
from code_music.mastering import master_audio
auto_mix(song)
audio = song.render()
mastered = master_audio(audio, 44100, style="balanced")

# Export for any platform
from code_music import export_with_preset
export_with_preset(mastered, "my_track", "spotify-upload")
export_with_preset(mastered, "my_track", "apple-lossless")

# List all 67 genres and 22 quality presets
code-music --list-genres
code-music --list-quality

# Embellish a melody with style-appropriate ornaments
from code_music import scale, embellish, auto_harmonize
melody = scale("C", "minor", 5, length=16)
melody = embellish(melody, style="jazz", density=0.3)
harmony = auto_harmonize(melody, key="C", scale_name="minor", interval="thirds")

# Design instruments from raw oscillators
from code_music import SoundDesigner

supersaw = (
    SoundDesigner("supersaw")
    .add_osc("sawtooth", detune_cents=0, volume=0.3)
    .add_osc("sawtooth", detune_cents=10, volume=0.25)
    .add_osc("sawtooth", detune_cents=-10, volume=0.25)
    .envelope(attack=0.02, decay=0.1, sustain=0.7, release=0.4)
    .filter("lowpass", cutoff=4000, resonance=0.6)
)
song.register_instrument("supersaw", supersaw)
```

## Learn by example

The `examples/` directory walks through the entire API step by step:

| # | Example | What you'll learn |
|---|---|---|
| 01 | `hello_world.py` | Notes, tracks, Song basics |
| 02 | `chords_and_scales.py` | Chord shapes, scale(), modes |
| 03 | `effects_chain.py` | EffectsChain, reverb, delay, compress |
| 04 | `arrangement.py` | Section, repeat, Song.arrange |
| 05 | `track_transforms.py` | transpose, loop, split, merge, stretch, filter |
| 06 | `midi_roundtrip.py` | Export to MIDI, import back |
| 07 | `json_save_load.py` | Song JSON serialization round-trip |
| 08 | `live_coding.py` | --watch --play for instant feedback |
| 09 | `generative.py` | generate_full_song() multi-track generation |
| 10 | `analysis.py` | detect_key(), Song.analyze() |
| 11 | `sound_design.py` | SoundDesigner - instruments from scratch |
| 12 | `fm_and_wavetables.py` | FM synthesis, wavetables, euclidean rhythms |
| 13 | `granular_and_physical.py` | Granular clouds, Karplus-Strong, bowed string |
| 14 | `patterns.py` | Pattern mini-notation, transforms, polymeter |
| 15 | `automation.py` | Automation curves, EnvFollower, Clip loops |
| 16 | `spatial.py` | 3D panning, orbit, ambisonics, spatial_mix |
| 17 | `plugins.py` | Plugin registry, custom instruments/effects |
| 18 | `structure.py` | Form generation, Session view, fill_tracks |
| 19 | `visualization.py` | Piano roll, spectrogram, sheet music (6 types) |

```bash
code-music examples/01_hello_world.py --play    # start here
code-music --random jazz                        # or just generate one
```

## Export to Spotify

```bash
make spotify                           # renders all songs to dist/flac/
code-music my_track.py --quality spotify-upload  # single track, best quality
```

Upload at **https://artists.spotify.com** -> Music -> Upload Track.
Minimum: 30s, 44100 Hz stereo. FLAC preferred.

22 export presets: `spotify-upload`, `apple-lossless`, `apple-hires`,
`youtube`, `tidal-master`, `bandcamp`, `studio`, `daw-float`,
`archive-master`, `cd`, `mp3-320`, `podcast`, and more.
Run `code-music --list-quality` to see all.

## Sheet music and rhythm games

```bash
make notation-all   # LilyPond (.ly), ABC (.abc), MusicXML (.xml) for every song
```

- **LilyPond**: `lilypond dist/notation/lily/trance_odyssey.ly` -> PDF
- **ABC**: paste `dist/notation/abc/tank_bebop.abc` into https://abc.rectanglered.com
- **MusicXML**: open in MuseScore, Sibelius, Dorico, Finale

```python
# Export to rhythm games
from code_music import export_stepmania, export_clone_hero
export_stepmania(song, "my_track.sm", difficulty="hard")
export_clone_hero(song, "my_track.chart", difficulty="expert")
```

## Genre transform

Convert any song to any of 67 genres with one function call:

```bash
code-music my_track.py --genre-transform jazz --flac
code-music my_track.py --genre-transform bossa_nova --flac
code-music my_track.py --genre-transform melodic_metalcore --flac
code-music --list-genres   # see all 67
```

## Integrations

Use code-music alongside other tools:

```python
from code_music.integrations import from_music21, to_music21, analyze_audio
from code_music.integrations import render_with_csound, render_with_fluidsynth

# Import a music21 score
import music21
score = music21.corpus.parse("bach/bwv66.6")
song = from_music21(score)

# Render with a SoundFont for realistic instruments
audio = render_with_fluidsynth("/tmp/song.mid", "grand_piano.sf2")

# Check what's available
code-music --list-integrations
```

---

*See [docs/](docs/) for audience-specific guides.*
