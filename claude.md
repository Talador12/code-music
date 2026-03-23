# code-music — project state

## Status: v0.4.0 — arp helper, MIDI export, 4 new songs, 119 tests, --watch mode

## What's done

### Engine helpers (`code_music/engine.py`)
- `arp(chord, pattern, rate, octaves)` — 8 named patterns: up, down, up_down, down_up, random, outside_in, skip, pinky
- `crescendo(notes, start_vel, end_vel)` — linear velocity ramp up (works on Notes and Chords)
- `decrescendo(notes, start_vel, end_vel)` — linear velocity ramp down
- `transpose(notes, semitones)` — shift pitch up/down
- `humanize(notes, vel_spread, timing_spread)` — organic random micro-variation
- `repeat(events, n)` — convenience repeat helper
- `Section` dataclass — named song blocks for arrangement docs
- Extended chord shapes: 9, min9, add9, maj9, 6, min6, 6/9, 11, 13, power, flat5, aug7

### MIDI export (`code_music/midi.py`)
- `export_midi(song, path)` — pure-stdlib SMF type 1 (.mid) file
- General MIDI program mapping for all 60 instruments
- Drum track auto-routes to channel 10
- `code-music song.py --midi` from CLI

### CLI additions (`code_music/cli.py`)
- `--midi` flag: export as MIDI
- `--watch` flag: poll for file changes, re-render on save (live coding mode)

### Effects additions (`code_music/effects.py`)
- `gate(rate_hz, shape, duty)` — rhythmic amplitude chop: square/ramp_up/ramp_down/trapezoid
- `limiter(ceiling, release_ms)` — brick-wall peak limiter (mastering)
- `stereo_width(width)` — M/S stereo widening (0=mono, 2=extra wide)
- `noise_sweep(n_samples, start_cutoff, end_cutoff)` — EDM build-up effect
- `phaser(rate_hz, depth, stages)` — multi-stage all-pass LFO phaser
- `flanger(rate_hz, depth_ms, feedback)` — LFO delay flanger (jet-engine sweep)

### Songs (in `songs/`)
- `trance_odyssey.py` — uplifting trance, 138 BPM, A minor, 36 bars, gated strings + supersaw
- `tank_bebop.py` — Cowboy Bebop inspired big-band jazz, 168 BPM, Bb, full orchestra
- `symphony_no1.py` — original symphony movement, C minor, sonata form, 108 BPM
- `future_bass.py` — future bass / melodic dubstep, 150 BPM, F# major, 808 bass

### Samples additions (`samples/techniques/`)
- `arp_patterns.py` — all 8 arp patterns showcased on Am7
- `gate_effects.py` — gate shapes: square / ramp_up / trapezoid
- `trance_gate_strings.py` — trance gated strings texture
- `crescendo_showcase.py` — strings swell in/out with humanize
- `noise_build.py` — noise sweep reference

### Tests: 119 passing
- `test_engine_helpers.py` — arp, crescendo, decrescendo, transpose, humanize, repeat (31 tests)
- `test_midi.py` — MIDI export, file structure, drum routing, multi-track (8 tests)

## Roadmap

### Engine
- [ ] LFO modulation on synth params at note level (filter cutoff sweep per note)
- [ ] Portamento / glide between notes (pitch slide)
- [ ] Velocity curves per track (humanize at track level, not note level)
- [ ] Note probability / generative randomness (p=0.7 to play a note)

### EDM
- [ ] Future house / moombahton song
- [ ] DnB / liquid DnB song (174 BPM, Reese bass, amen break-style drums)
- [ ] Deadmau5-style progressive house full song (8+ minute structure)
- [ ] Dubstep wobble bass (LFO on filter cutoff synced to BPM)

### Orchestral / Jazz
- [ ] Cinematic trailer music song (Hans Zimmer inspired)
- [ ] Full jazz standards arrangement (Autumn Leaves / Giant Steps style)
- [ ] String pizzicato toggle helper (easy pizz/arco switching)
- [ ] Dynamics automation over bars (not just per-note)

### Voice / AI
- [ ] Bark integration test + install guide
- [ ] ElevenLabs v3 singing mode exploration
- [ ] Phoneme stutter/glitch effect for robotic vocal chops
- [ ] Autotune post-processing (snap voice pitch to scale)

### Export / Distribution
- [ ] Spotify distributor guide (DistroKid / TuneCore upload steps)
- [ ] GitHub Pages web player for previewing songs
- [ ] Batch render all songs to dist/ in CI

### Ideas
- [ ] Generative mood-based composition (mood + scale → auto-melody)
- [ ] Song remix helper (transpose + retempo existing song)
- [ ] BPM tap utility (figure out BPM from listening)
- [ ] Chord progression suggester (given root + mood → progression)
