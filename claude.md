# code-music — project state

## Status: v0.17.0 — 55 songs, voice_lead(), 269 tests, all albums 3+

## What's built (full inventory)

### Engine
- Note, Chord, Beat, Track, Song, PolyphonicTrack, Section
- suggest_progression(root, mood) — 8 moods × 3 variations
- analyze_progression(chords, key_root) — Roman numeral analysis
- **voice_lead(chords)** — smooth voice leading via inversion minimisation
- bpm_ramp / accelerando / ritardando — tempo automation
- Chord.invert(n), Chord.notes
- scale(), arp(), chord_prog(), generate_melody()
- humanize, staccato, legato, pizzicato, prob, repeat, transpose
- crescendo, decrescendo, triplets, tuplets, all ornaments
- remix(song, semitones, bpm_factor) — transpose + retempo

### Synth (65+ presets)
- Velocity-to-timbre: acoustic instruments get brighter when struck harder
- Karplus-Strong: guitar_ks, banjo_ks, harp_ks, sitar_ks, koto_ks
- Wobble bass (per-note LFO filter), formant vowels, FM synthesis
- Full orchestral + percussion + EDM + voice presets

### Effects (31 functions)
- reverb, delay, chorus, flanger, phaser, distortion
- **conv_reverb(room)** — convolution reverb (hall/chamber/plate/room/cave/spring)
- **granular(grain_size_ms, scatter)** — grain scatter texture
- **autotune(scale_notes, strength)** — pitch correction to scale
- **multitap_delay(taps)** — multiple echoes, individual delay/level/pan
- lowpass, highpass, bandpass, compress, multiband_compress, limiter
- gate, lfo_filter, sidechain, stereo_width, tremolo, vibrato
- bitcrush, ring_mod, tape_sat, noise_sweep, pan, vocoder

### Songs (55 total)
All major genres covered. Key highlights:
- EDM: veldt, neon_grid, lost_frequencies (deep house), slipstream, electric_dreams
- Jazz: tank_bebop, after_midnight, fusion_flight, conversations (PolyphonicTrack)
- Classical: symphony_no1, cathedral, still_water
- Cinematic: neon_cathedral (conv_reverb), cinematic_rise
- Rock/Metal: prog_rock, fault_lines, the_arc (5/4)
- Folk: porch_song, mountain_road, campfire
- Hip-hop: lo_fi_loop, east_coast_night, trap_god, vapor_wave
- World: silk_road, wrong_side_of_the_scale, duende

### Albums (22) — all 3+ tracks
All genres covered, most at 4-5 tracks.

### Scripts
- gen_album.py — generative album from seed + genre
- midi_to_song.py — MIDI reverse compiler
- make_cover.py — album cover art generator
- play_scales.py, play_vibe.py — interactive players
- spotify_auth.py + spotify_taste.py — Spotify OAuth

### Web Player
docs/web/index.html — dark terminal aesthetic, plays from dist/wav/

### CI
GitHub Actions: lint + test + smoke renders + batch render artifact

## Roadmap

### Next priorities
- [ ] Spotify taste calibration — paste `make spotify` output here
- [ ] More songs based on taste once calibrated
- [ ] Update web player song list (currently shows old 42 songs)
- [ ] Album artwork auto-bundled with album render

### Engine
- [ ] Chord voicing spread control (open vs close voicing)
- [ ] Time signature automation (change mid-song)
- [ ] Note probability per-track

### Effects
- [ ] Multi-band EQ
- [ ] Convolution reverb from real IR files (load .wav)

### Distribution
- [ ] DistroKid batch upload helper
- [ ] Spotify playlist from rendered songs

### Ideas
- [ ] Visual waveform export (matplotlib png of audio)
- [ ] Song fingerprinting (compare two renders for regression)
- [ ] Lyrics + voice synthesis integration
- [ ] Album sampler: one 2-minute preview mixing all tracks
