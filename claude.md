# code-music — project state

## Status: v0.10.0 — 33 songs, 22 albums, 230 tests, Spotify OAuth

## What's built

### Engine
- `Note / Chord / Beat / Track / Song` — full music primitives
- `Track.pan`, `Track.swing`, `song._effects` post-render hook
- `song.time_sig`, `song.key_sig`, `song.composer`
- Duration constants: `WHOLE HALF QUARTER EIGHTH SIXTEENTH THIRTY_SECOND`
- Tuplets: `triplet() tuplet() triplets() tuplets()`
- Ornaments: `trill mordent upper_mordent turn grace_note doit fall flip shake`
- Articulations: `staccato legato pizzicato`
- Composition: `arp chord_prog crescendo decrescendo transpose humanize repeat scale`
- `suggest_progression(root, mood)` — 8 moods × 3 variations
- `generate_melody(scale, mode, bars, density, seed)`
- `prob(note, p)` — probabilistic notes

### Synth (65 presets)
- Standard waveforms + additive synthesis
- Supersaw (7 detuned saws), Reese bass, Hoover, Wobble (LFO filter per note)
- FM synthesis, Formant vowels (a/o/e), Moog ladder filter
- **Karplus-Strong physical models**: guitar_ks, banjo_ks, harp_ks, sitar_ks, koto_ks
- Full orchestral: strings, brass, woodwinds, percussion, choir
- EDM: acid, hoover, stab, supersaw, sub_bass, 808
- Drums: kick, snare, hat, clap, tom, ride, crash, 808, taiko, tabla, djembe

### Effects (all scipy/numpy vectorized)
- `reverb delay chorus flanger phaser distortion`
- `lowpass highpass bandpass compress limiter`
- `gate lfo_filter sidechain stereo_width tremolo vibrato`
- `bitcrush ring_mod tape_sat noise_sweep pan`

### Export
- WAV (stdlib), FLAC (lossless), MP3 (320k), OGG (pydub + ffmpeg)
- MIDI (pure stdlib, SMF type 1)
- LilyPond, ABC notation, MusicXML sheet music

### Songs (33 total)
Electronic: clarity_drive, lollipop_laser, trance_odyssey, deadmau5_house,
            future_bass, heavy_wobble, berlin_four, veldt, neon_grid
Jazz/Soul:  tank_bebop, lo_fi_loop, late_shift, small_hours, upstream_two,
            gospel_hour, ipanema_hours
Rock:       prog_rock, the_room, fault_lines, teeth_two
Classical:  symphony_no1, cathedral
Cinematic:  cinematic_rise, deep_space_drift
DnB:        liquid_dnb
Pop:        second_chorus
Folk:       porch_song
Funk:       on_the_one
Flamenco:   duende
World:      wrong_side_of_the_scale
Chiptune:   chiptune_quest
Neo-soul:   late_shift

### Albums (22)
All in `albums/` — most at 3+ tracks now

### Spotify integration
- `make spotify` — OAuth auth + reads your listening data
- Writes `styles/my_taste.py` with top artists, genres, playlists
- `make export-spotify` — renders all songs to dist/flac/ for upload

## Roadmap

### Songs
- [ ] Harder DnB (Pendulum / Chase & Status — distorted bass, faster)
- [ ] Ambient generative (procedural, slow-evolving, never repeats)
- [ ] Reggae / dancehall
- [ ] Neo-classical / minimal piano (Nils Frahm, Ólafur Arnalds)
- [ ] Drum & bass — neurofunk (dark, technical)
- [ ] Trap / hip-hop production (808 bass, hi-hat rolls)

### Engine
- [ ] Polyphonic Track (notes playing simultaneously, not sequentially)
- [ ] Velocity-to-timbre (louder = brighter on piano/drums)
- [ ] Note probability per-track (density control at track level)
- [ ] Chord inversion helper: `Chord.invert(n)`
- [ ] BPM automation (gradual tempo changes within a song)

### Effects
- [ ] Multi-band compressor (mastering chain — low/mid/high separate)
- [ ] Vocoder effect (robot/harmonizer voice)
- [ ] Convolution reverb with real IR files (load .wav impulse response)
- [ ] Auto-tune post-processing (snap voice pitch to scale)

### Albums
- [ ] Flesh out 7 remaining 2-track albums to 3+
- [ ] Album artwork generation (matplotlib text art, or AI image)
- [ ] GitHub Pages web player — browse and play albums in browser

### Distribution
- [ ] DistroKid / TuneCore upload guide in docs/
- [ ] Batch CI render to dist/ on push (GitHub Actions artifact)

### Ideas
- [ ] Generative album: seed + genre + mood → full procedural album
- [ ] Song remix helper: transpose + retempo existing song
- [ ] Live watch mode: --watch flag re-renders AND auto-plays on save
- [ ] BPM tap utility (figure out tempo from tapping)
- [ ] Music taste auto-calibration once Spotify OAuth token provided
- [ ] MIDI → code-music reverse compiler (read .mid → generate song script)
- [ ] Collaborate mode: merge two song scripts into one arrangement
