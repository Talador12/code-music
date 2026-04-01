# code-music

Code-generated music. Write Python, hear sound, export to Spotify.

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
from code_music import Song, Track, Note, Chord, scale, reverb

song = Song(title="My Track", bpm=120)

pad  = song.add_track(Track(instrument="pad",    volume=0.5))
lead = song.add_track(Track(instrument="piano",  volume=0.8))

pad.add(Chord("A", "min7", 3, duration=8.0))
lead.extend(scale("A", "pentatonic", octave=5))

song._effects = {"pad": lambda s, sr: reverb(s, sr, wet=0.4)}
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

| Directory | What's there |
|---|---|
| `examples/` | 8 step-by-step tutorials: hello world → live coding |
| `songs/` | 120 full songs across 40+ genres |
| `samples/` | 100+ short instrument and technique demos |
| `scales/` | 31 guided scale demos (all 12 keys), plus arpeggio mode |
| `styles/` | Theory profiles for 7 genres (deadmau5, Zedd, bebop, cinematic…) |
| `scripts/` | Interactive scale/arp player with progress bar |
| `code_music/` | The engine, synth, effects, export, notation, voice |

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
| 06 | `midi_roundtrip.py` | Export to MIDI, import back, remix |
| 07 | `json_save_load.py` | Song.export_json / Song.load_json |
| 08 | `live_coding.py` | --watch --play for instant feedback |

```bash
code-music examples/01_hello_world.py --play    # start here
```

## Export to Spotify

```bash
make spotify     # renders all songs to dist/flac/ + prints upload link
```

Upload at **https://artists.spotify.com** → Music → Upload Track.
Minimum: 30s, 44100 Hz stereo. FLAC preferred.

## Sheet music

```bash
make notation-all   # LilyPond (.ly), ABC (.abc), MusicXML (.xml) for every song
```

- **LilyPond**: `lilypond dist/notation/lily/trance_odyssey.ly` → PDF
- **ABC**: paste `dist/notation/abc/tank_bebop.abc` into https://abc.rectanglered.com
- **MusicXML**: open in MuseScore, Sibelius, Dorico, Finale

---

*See [docs/](docs/) for audience-specific guides.*
