# code-music — project state

## Status: v0.5.0 — wobble bass, formant vowels, generative melody, 3 new songs, 156 tests

## What's done

### New synth presets (code_music/synth.py)
- `wobble` — LFO-swept lowpass filter over sawtooth, the dubstep bass sound
- `portamento` — sawtooth with glide (pitch slide) character
- `fm_bell` — 2-operator FM synthesis, metallic bell tones
- `formant_a / formant_o / formant_e` — vowel-shaped bandpass filter chain over saw
- `taiko` — deep pitched drum with noise attack (cinematic hits)
- `tabla`, `djembe` — ethnic percussion with noise transient
- `moog_bass` — ladder-filter style bass with fast rolloff
- `sub_bass` — pure sine sub (808-adjacent but cleaner)

### Per-note effects wired into synth
- Wobble: LFO filter sweeps per note (rate, min/max cutoff configurable in preset)
- Formant: three bandpass resonators per note (F1/F2/F3 for each vowel)
- Taiko/djembe/tabla: noise burst on attack transient

### New engine helpers
- `staccato(notes, factor)` — shorten notes, add silence gap
- `legato(notes, overlap)` — extend notes for smooth slur feel
- `pizzicato(notes)` — very short staccato (plucked strings)
- `prob(note, p)` — play note with probability p, else rest
- `chord_prog(roots, shapes, ...)` — build chord progression from parallel lists
- `generate_melody(scale, mode, bars, density, seed)` — procedural melody generator

### Songs
- `liquid_dnb.py` — Liquid DnB, 174 BPM, D Dorian, warm + jazzy
- `cinematic_rise.py` — Hans Zimmer hybrid orchestral, 100 BPM, Cm, taiko + brass
- `deadmau5_house.py` — deadmau5 progressive house, 128 BPM, Fm, slow filter evolution

### Samples
- `samples/edm/wobble_bass.py` — dubstep wobble bass demo
- `samples/edm/fm_bell_arp.py` — FM bell arpeggios
- `samples/voices/formant_vowels.py` — A/O/E vowel synthesis comparison
- `samples/orchestral/taiko_impact.py` — taiko + djembe + tabla
- `samples/techniques/generative_melody.py` — procedural melody in 3 modes
- `samples/techniques/articulations.py` — legato vs normal vs staccato comparison

### Tests: 156 passing
- `test_articulations.py` — staccato, legato, pizzicato, prob, chord_prog, generate_melody (36 tests)
- `test_new_presets.py` — wobble, formant, taiko, moog, fm_bell, sub, all 11 new presets (14 tests)

## Roadmap

### Next priorities
- [ ] Dubstep full song (heavy wobble bass, half-time drops)
- [ ] Moombahton / reggaeton influenced song (100 BPM, tropical EDM)
- [ ] Autumn Leaves jazz arrangement (jazz standard, walking bass + comp + solo)
- [ ] Generative / procedural full song (whole track from seed + mood)

### Engine
- [ ] Chord progression suggester: given root + mood → chord progression
- [ ] Velocity-to-timbre (louder hit = brighter on piano/drums)
- [ ] Arp with probability (random note dropout for live-feel arps)
- [ ] Polyphonic Track (notes sound simultaneously, not sequentially)
- [ ] Time signature support beyond 4/4 (3/4, 6/8, 7/8)

### Synth/Sound
- [ ] Granular synthesis wave (scattered grain texture)
- [ ] Additive organ preset with drawbar controls
- [ ] Better piano: string resonance, damper pedal simulation
- [ ] Karplus-Strong string synthesis (more realistic plucked strings)

### Effects
- [ ] Bitcrusher / lo-fi downsampler (chiptune / lo-fi texture)
- [ ] Ring modulator (metallic / robot voice)
- [ ] Tape saturation (warm analog simulation)
- [ ] Multi-band compressor (mastering chain)
- [ ] Convolution reverb with real IR files

### Voice / AI
- [ ] Bark integration guide + async render helper
- [ ] Autotune: snap voice track to nearest scale note

### Export / Distribution
- [ ] Batch CI render (render all songs to dist/ on push)
- [ ] Spotify distributor guide (DistroKid / TuneCore steps)
- [ ] GitHub Pages web player

### Ideas  
- [ ] Live performance mode: real-time parameter control via keyboard
- [ ] Song export as Python snippet (compress a song to minimal code)
- [ ] BPM tap detection utility
- [ ] Album concept: release the 10 songs as a coherent album
