# code-music — project state

## Status: BOOTSTRAPPED — engine + examples working, CI live

## What's done
- `code_music/engine.py` — Note, Chord, Beat, Track, Song, scale()
- `code_music/synth.py` — Synth with 11 presets (ADSR + additive synthesis)
- `code_music/export.py` — export_wav (stdlib wave) + export_mp3 (pydub)
- `code_music/cli.py` — `code-music <script.py>` CLI with --mp3 / --bpm flags
- `examples/hello_world.py` — C major scale
- `examples/lo_fi_loop.py` — 4-bar lo-fi hip-hop loop (Am, 90 BPM, drums)
- `examples/prog_rock.py` — D Dorian prog rock, intro/verse/chorus/outro
- Tests: test_engine.py + test_synth.py
- CI: GitHub Actions on Python 3.11 + 3.12

## Next steps
- [ ] Run locally, verify WAV output sounds correct
- [ ] Add reverb / delay effects to synth.py
- [ ] Add swing/groove quantization to Beat scheduling
- [ ] Add MIDI export option (for DAW import)
- [ ] More example songs (ambient, techno, jazz)
- [ ] Spotify upload guide in AGENTS.md
