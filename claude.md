# code-music — project state

## Status: v0.13.0 — 43 songs, PolyphonicTrack, remix(), generative album, CI

## What's built

### Engine
- All primitives: Note, Chord, Beat, Track, Song, scale, arp, etc.
- **PolyphonicTrack** — notes sound simultaneously (piano chords, guitar voicings)
- **remix(song, semitones, bpm_factor)** — transpose + retempo any song
- suggest_progression(root, mood) — 8 moods × 3 variations
- Chord.invert(n) — chord inversions
- generate_melody, humanize, staccato, legato, pizzicato, prob
- All ornaments: trill, mordent, turn, grace_note, doit, fall, flip, shake
- Tuplets: triplet(), tuplet(), triplets(), tuplets()
- 20+ chord shapes including min7b5, dim7, maj9, 7b9, 7#9

### Synth (65+ presets)
- Standard waveforms + all orchestral instruments
- Karplus-Strong: guitar_ks, banjo_ks, harp_ks, sitar_ks, koto_ks
- EDM: supersaw, reese_bass, wobble, acid, hoover, stab, 808
- All percussion: kick, snare, hat, clap, tom, ride, crash, taiko, tabla, djembe

### Effects (29 functions)
- reverb, delay, chorus, flanger, phaser, distortion
- lowpass, highpass, bandpass, compress, multiband_compress, limiter
- gate, lfo_filter, sidechain, stereo_width, tremolo, vibrato
- bitcrush, ring_mod, tape_sat, noise_sweep, pan, vocoder

### Songs (43 total, all genres covered)
Electronic: trance_odyssey, clarity_drive, lollipop_laser, deadmau5_house,
            future_bass, heavy_wobble, berlin_four, veldt, neon_grid, signal_loss,
            neuromancer, trap_god
Jazz/Soul:  tank_bebop, lo_fi_loop, late_shift, small_hours, upstream_two,
            gospel_hour, ipanema_hours, after_midnight
Rock:       prog_rock, the_room, fault_lines, teeth_two, slow_coast
Classical:  symphony_no1, cathedral, still_water
Cinematic:  cinematic_rise, deep_space_drift, open_circuit, drift_state
DnB:        liquid_dnb, upstream_two
Folk:       porch_song, mountain_road
Funk/Reggae:on_the_one, sun_and_sorrow
World:      wrong_side_of_the_scale, silk_road, duende
Pop:        second_chorus
Misc:       chiptune_quest, after_midnight

### Albums (22)
All have 3+ tracks. 6 have 4+. The Anthology has 11 (one per genre).

### Scripts
- scripts/gen_album.py — generative album from seed + genre
- scripts/play_scales.py — interactive scale player
- scripts/play_vibe.py — mood-based song player
- scripts/spotify_auth.py + spotify_taste.py — Spotify OAuth profiling

### CI (.github/workflows/ci.yml)
- Lint + test on push/PR (Python 3.11 + 3.12)
- Smoke renders key songs
- Tests PolyphonicTrack and remix()
- Batch render all songs on main push → uploaded as artifact

## Roadmap

### Next priorities
- [ ] Spotify taste calibration (run make spotify, paste output here)
- [ ] GitHub Pages web player — browse albums in browser
- [ ] MIDI → code-music reverse compiler
- [ ] Convolution reverb with real IR files
- [ ] More songs to calibrate to Spotify taste once OAuth runs
- [ ] Album artwork generation

### Engine ideas
- [ ] BPM automation (gradual tempo changes within a song)
- [ ] Velocity-to-timbre (louder hit = brighter on piano/drums)
- [ ] Chord voicing spread control (open vs close voicings)

### Effects ideas
- [ ] Auto-tune (snap voice pitch to scale)
- [ ] Multi-tap delay (more than 2 taps)
- [ ] Granular synthesis (scattered grain texture)

### Distribution
- [ ] DistroKid batch upload helper
- [ ] Spotify playlist generation from rendered songs
- [ ] Album cover art (matplotlib + Pillow text art)
