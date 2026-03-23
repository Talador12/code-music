# code-music — project state

## Status: v0.2.0 — massive instrument library, 60+ samples, vectorized effects

## What's done

### Engine
- `Note / Chord / Beat / Track / Song` — full music primitives
- `Track.pan` (-1..1 equal-power), `Track.swing` (8th-note groove), `song._effects` hook

### Synth (60 instrument presets)
**Basic waveforms:** sine, square, sawtooth, triangle  
**Keyboards:** piano, organ, harpsichord, rhodes, wurlitzer, celesta  
**Strings:** strings, violin, cello, contrabass, pizzicato  
**Brass:** trumpet, trombone, french_horn, tuba, brass_section  
**Woodwinds:** flute, oboe, clarinet, bassoon, saxophone, piccolo  
**Plucked/Struck:** guitar_acoustic, guitar_electric, harp, marimba, vibraphone, xylophone  
**Orchestral perc:** timpani, gong, snare_orch, cymbals  
**Choir/Vocal:** choir_aah, choir_ooh, vox_pad  
**EDM:** bass, pad, pluck, supersaw, reese_bass, acid, hoover, stab, lead_edm, noise_sweep  
**Drums:** kick, snare, hat, clap, tom, ride, crash, 808

### Effects (`code_music/effects.py`) — all scipy/numpy vectorized, O(N log N)
- `reverb` — convolution reverb (FFT-based, fast for any signal length)
- `delay` — multi-tap stereo echo with ping-pong
- `chorus` — LFO-modulated warp via numpy interp
- `distortion` — soft-clip overdrive (scipy lfilter tone)
- `lowpass / highpass / bandpass` — scipy butter SOS filters
- `compress` — peak-following compressor (scipy lfilter envelope)
- `pan` — equal-power stereo pan

### Export: WAV (stdlib), FLAC (lossless), MP3 (320k), OGG (pydub + ffmpeg)

### Songs (in `songs/`)
- `hello_world.py` — C major scale
- `lo_fi_loop.py` — lo-fi hip-hop, Am, 90 BPM
- `prog_rock.py` — D Dorian prog rock
- `clarity_drive.py` — Zedd-style big-room electro, 128 BPM, 36 bars
- `lollipop_laser.py` — Mord Fustang cosmic disco-house, 128 BPM
- `deep_space_drift.py` — Brian Eno-style ambient, 60 BPM, 128s

### Samples (60+ files across 10 categories)
- `bass/` — deep_bass, walking_bass, sub_bass_pulse
- `highs/` — bright_lead, triangle_flute, pluck_arp
- `synths/` — lead_square, pad_lush, fm_organ
- `waves/` — pure_sine, sawtooth_demo, triangle_wave
- `chords/` — jazz_comping, power_chords, ambient_stack
- `instruments/` — piano_phrase, pluck_guitar
- `drums/` — basic_kit, breakbeat, four_on_floor
- `brass/` — trumpet_fanfare, trombone_slide, french_horn_call, brass_section_stab, tuba_low
- `woodwinds/` — flute_melody, saxophone_blues, clarinet_swing, oboe_pastoral, bassoon_bass
- `strings/` — string_quartet, cello_solo, pizzicato_groove, violin_tremolo
- `orchestral/` — full_orchestra_swell, symphonic_intro, harp_glissando, timpani_roll, gong_crash
- `jazz/` — bebop_head, jazz_piano_trio, swing_rhythm_section, trumpet_solo
- `edm/` — supersaw_lead, reese_bass, acid_303, hoover_lead, deadmau5_prog, daft_punk_stab, mord_fustang_laser

## Roadmap

### Next up
- [ ] `tank_bebop.py` song — full arrangement inspired by Seatbelts/Yoko Kanno
- [ ] LFO on synth parameters (filter sweep, vibrato, tremolo) — real-time modulation
- [ ] Arpeggiator helper: `arp(chord, pattern, rate)` sugar
- [ ] Sidechain compression (kick → pad ducking, classic EDM pump)
- [ ] Song sections API (verse/chorus/bridge markers for arrangement)
- [ ] MIDI export (`.mid`) for DAW round-tripping
- [ ] Velocity humanization (small random variations on notes)
- [ ] More songs: future bass, jazz nocturne, drum & bass
- [ ] Spotify distributor notes (DistroKid / TuneCore)
- [ ] GitHub Pages web player for previewing renders
