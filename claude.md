# code-music — project state

## Status: v0.19.0 — 58 songs, chord voicing spread/drop2/close, 278 tests

## What's built (full inventory)

### Engine
- Note, Chord, Beat, Track, Song, PolyphonicTrack, Section
- **Chord.spread(octave_spread)** — open voicing (alternate notes up an octave)
- **Chord.drop2()** — jazz drop-2 voicing (2nd-from-top note down an octave)
- **Chord.close()** — compact back to one octave
- Chord.invert(n) — chord inversions
- suggest_progression(root, mood) — 8 moods × 3 variations
- analyze_progression(chords, key_root) — Roman numeral analysis
- voice_lead(chords) — smooth voice leading via inversion minimisation
- bpm_ramp / accelerando / ritardando — tempo automation
- scale(), arp(), chord_prog(), generate_melody()
- humanize, staccato, legato, pizzicato, prob, repeat, transpose
- crescendo, decrescendo, triplets, tuplets, all ornaments
- remix(song, semitones, bpm_factor) — transpose + retempo
- 20+ chord shapes including min7b5, dim7, maj9, 7b9, 7#9

### Synth (65+ presets)
- Velocity-to-timbre: acoustic instruments get brighter when struck harder
- Karplus-Strong: guitar_ks, banjo_ks, harp_ks, sitar_ks, koto_ks
- Wobble bass (per-note LFO filter), formant vowels, FM synthesis
- Full orchestral + percussion + EDM + voice presets

### Effects (32 functions)
- reverb, delay, chorus, flanger, phaser, distortion
- conv_reverb(room) — convolution reverb (hall/chamber/plate/room/cave/spring)
- granular, autotune, multitap_delay, eq (parametric multi-band EQ)
- lowpass, highpass, bandpass, compress, multiband_compress, limiter
- gate, lfo_filter, sidechain, stereo_width, tremolo, vibrato
- bitcrush, ring_mod, tape_sat, noise_sweep, pan, vocoder

### Songs (58), Albums (22), Scales (32), Samples (100+), Styles (7)

### Scripts
- gen_album.py, midi_to_song.py, make_cover.py, make_waveform.py, make_sampler.py
- play_scales.py, play_vibe.py, arp_render.py
- spotify_auth.py + spotify_taste.py

## Roadmap

### Engine
- [x] Chord voicing spread control (open vs close voicing)
- [x] Time signature automation (change mid-song)
- [x] Note probability per-track (density slider at track level)

### Effects
- [x] Convolution reverb from real IR files (load .wav)

### Distribution
- [x] DistroKid batch upload helper
- [x] Spotify playlist from rendered songs

### Ideas (completed)
- [x] Song fingerprinting (compare two renders for regression)
- [x] Lyrics + voice synthesis integration
- [x] Visual scale diagram in web player
- [x] BPM tap utility

## Next Roadmap

### Engine
- [x] Chord.voicings() — return all common voicings of a chord (root, drop2, spread, shell)
- [x] Song.merge(other_song) — combine two songs into one (layer tracks)
- [x] Track.reverse() — play a track's notes in reverse order

### Effects
- [x] Stereo imager — visualize L/R balance as a PNG
- [x] Slapback delay — single short echo (rockabilly, early rock)

### Songs
- [x] Reach 60 songs (60 total)
- [x] Write a song that uses Lyrics + voice synthesis end-to-end

### Scripts
- [x] make check — run lint + test in one command
- [x] Song statistics script — total duration, BPM distribution, genre counts

### Distribution
- [x] GitHub Release with rendered WAV zip artifact on tag push
