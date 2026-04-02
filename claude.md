# code-music — project state

## Status: v6.0.0 — 145 songs, 769 tests, custom sound design shipped

## What's built

### Engine
- Note, Chord, Beat, Track, Song, PolyphonicTrack, Section
- Chord.spread(), drop2(), close(), invert(n), voicings()
- Song.merge(other), Track.reverse(), Track.density
- suggest_progression(root, mood), analyze_progression(), voice_lead()
- bpm_ramp / accelerando / ritardando, time_sig_map
- scale(), arp(), chord_prog(), generate_melody(), remix()
- humanize, staccato, legato, pizzicato, prob, repeat, transpose
- crescendo, decrescendo, triplets, tuplets, all ornaments
- Lyrics class (text → voice track pipeline)
- 20+ chord shapes, 35+ scale modes

### Sound Design
- SoundDesigner class: oscillators, noise, filters, LFO, ADSR, pitch envelope
- 5 built-in designed presets (supersaw, sub_808, metallic_hit, vocal_pad, plucked_string)
- Register as instrument: song.register_instrument(name, designer)
- Serialization: to_dict/from_dict round-trip, to_wav export, preview playback
- Biquad filter (scipy-free): lowpass, highpass, bandpass

### Synth (65+ presets)
- Velocity-to-timbre, Karplus-Strong physical models
- Wobble bass, formant vowels, FM synthesis, per-note LFO filter
- Full orchestral + percussion + EDM + voice presets

### Effects (33 functions)
- reverb, delay, slapback, chorus, flanger, phaser, distortion
- conv_reverb (synthetic + real IR files), granular, autotune
- multitap_delay, eq, lowpass, highpass, bandpass
- compress, multiband_compress, limiter
- gate, lfo_filter, sidechain, stereo_width, tremolo, vibrato
- bitcrush, ring_mod, tape_sat, noise_sweep, pan, vocoder

### Export
- WAV, FLAC, MP3, OGG, MIDI, LilyPond, ABC, MusicXML

### Songs: 145 | Albums: 23 | Scale demos: 31 | Samples: 100+ | Styles: 7

### Scripts
- play_scales, play_vibe, arp_render, bpm_tap
- gen_album, midi_to_song, make_cover, make_waveform, make_sampler
- stereo_imager, fingerprint, stats, distrokid_prep, make_playlist
- spotify_auth + spotify_taste

### CI + Release
- GitHub Actions: lint + test + smoke render on push/PR
- Batch render artifact on main push
- GitHub Release with WAV zip on tag push

## Completed Roadmap

### Engine
- [x] Chord voicing spread control
- [x] Time signature automation
- [x] Note probability per-track
- [x] Chord.voicings()
- [x] Song.merge()
- [x] Track.reverse()

### Effects
- [x] Convolution reverb from real IR files
- [x] Slapback delay

### Scripts + Tools
- [x] make check
- [x] Song statistics
- [x] Stereo imager
- [x] BPM tap utility
- [x] Visual scale diagram in web player
- [x] Song fingerprinting
- [x] DistroKid batch upload helper
- [x] Spotify playlist generator

### Songs + Voice
- [x] Reach 60 songs
- [x] Lyrics + voice synthesis end-to-end song

### Distribution
- [x] GitHub Release with rendered WAV zip on tag push

## Next Roadmap

- [x] Song using BPM automation + time sig changes (showcase built features)
- [x] Deploy GitHub Pages web player (enable Pages on main, /docs source)
- [x] Expand albums to 5+ tracks each (0 at 3, 7 at 4, 13 at 5, 2 at 6)

## v1.2 Roadmap

- [x] Remaining 7 albums at 4 tracks → get all to 5+
- [x] Tag v1.1.0 release (triggers GitHub Release with 71-song WAV zip)
- [x] Chord.shell_voicing() with optional bass note override
- [x] Song.info() → dict with title, bpm, duration, track count, key, time_sig
- [x] make render-one SONG=name — render single song to all formats (WAV+FLAC+MP3)
- [x] New genres: Afrobeats, shoegaze, math rock
- [x] More PolyphonicTrack songs (3 total: conversations, nocturne_op2, town_square)

## v1.3 Roadmap

- [x] Track.quantize(grid) — snap note timings to nearest grid subdivision
- [x] Song.export_stems() — render each track as a separate WAV file
- [x] Reach 75 songs (75 total)

## v1.4 Roadmap

- [x] Song.master() — master bus chain (EQ → compress → limit) in one call
- [x] Genre-aware song templates — make new-song STYLE=jazz copies genre template
- [x] Audio sample import — load a WAV as a Track instrument (sampling)
- [x] Reach 80 songs (80 total)
- [x] Tag v1.3.0 release

## v1.5 Roadmap

- [x] Sample-only song timing: include `sample_tracks` in `Song.total_beats`
- [x] Sample-only rendering: remove need for dummy instrument track
- [x] Voice-only song timing: estimate `VoiceTrack` duration for `Song.total_beats`
- [x] Voice-only rendering: use `Song.total_beats` (drop 8-beat synth fallback path)
- [x] Voice timing heuristic: account for punctuation pauses (commas / sentence endings)
- [x] Voice timing docs: document estimation model for creators/developers
- [x] Voice pacing API: per-clip pause overrides (`pause_short_sec`, `pause_terminal_sec`)
- [x] Voice convenience API: `VoiceClip.narration(...)` and `VoiceClip.rap(...)`
- [x] Voice sample: add side-by-side pacing demo (`samples/voices/voice_pacing_demo.py`)
- [x] Makefile cleanup: remove duplicate `play-album-anthology` target warning
- [x] Makefile bugfix: album play loop prints/plays real filenames (shell-safe basename)
- [x] Makefile regression tests: cover sample target discovery + album play shell vars
- [x] Makefile regression tests: assert no duplicate-target warnings + non-anthology album coverage
- [x] Makefile regression tests: assert per-album glob paths in generated play commands
- [x] Makefile regression tests: assert generated `play-<song>` target renders expected WAV path
- [x] Makefile regression tests: representative `play-<song>` targets stay generated across genres
- [x] Makefile regression tests: representative `preview-<sample>` targets stay generated across sample groups
- [x] Makefile regression tests: representative `play-scale-<mode>` targets stay generated across scale families
- [x] Makefile regression tests: representative `album-<name>` targets stay generated across album groups
- [x] Makefile scale cleanup: hide underscore/internal scale targets from generated `play-scale-*` rules
- [x] Makefile hidden-target guardrails: keep internal song/album helper files out of generated targets
- [x] Makefile UX: expose friendly `play-scale-circle_of_fifths` alias while keeping underscore target private
- [x] Docs: surface `play-scale-circle_of_fifths` in listener/theory/README command guides
- [x] README UX: split quick-play commands into song vs scale sections for faster scanning
- [x] Listener UX: add "Start here" command block grouping songs/scales/samples
- [x] Makefile regression tests: dynamically enforce hidden-target rules for all underscore files
- [x] Makefile sample cleanup: filter underscore sample files from generated preview targets
- [x] Test hygiene: remove empty-parametrize skip in Makefile tests (now fully green)
- [x] Make help regression tests: expose circle-of-fifths alias, keep internal targets hidden from help output
- [x] List command regression tests: keep friendly names in list output and hide internal template stems
- [x] List command regression tests: ensure `list-samples` never leaks underscore preview targets
- [x] Engine: `normalize_note_name()` + `ENHARMONICS` table for clean flat→sharp resolution
- [x] Engine: `Track.fade_in()` / `Track.fade_out()` — beat-level velocity ramps
- [x] Engine: `Song.arrange(sections)` — compose from named Section blocks
- [x] Reach 85 songs (5 new: arranged_journey, fade_to_dawn, flat_earth_funk, gb_waltz, eb_minor_elegy)
- [x] Tag v1.5.0 release

## v1.6 Roadmap

- [x] Real-time playback: `play(song)` function + `code-music --play` CLI flag
- [x] Add `sounddevice` as optional dependency with clear install instructions
- [x] Reach 90 songs (5 new: honky_tonk_moon, samba_de_janeiro, celtic_crossing, two_step_garage, minimal_pulse)
- [x] Tag v1.6.0 release

## v1.7 Roadmap

- [x] EffectsChain class: ordered steps with per-step wet/dry, bypass, kwargs binding
- [x] Song.effects dict: proper attribute replacing _effects hack, backward-compatible
- [x] Synth renderer: prefers song.effects, falls back to song._effects
- [x] Migrate 3 songs to EffectsChain (fade_to_dawn, trance_odyssey, cinematic_rise)
- [x] Update docs with EffectsChain usage (creators + theory)
- [x] Reach 95 songs (5 new: buenos_aires_tango, swing_shift, drill_sermon, psy_gate, balkan_brass)
- [x] Tag v1.7.0 release

## v1.8 Roadmap

- [x] Reach 100 songs (5 new: accordion_polka, cumbia_luna, jungle_pressure, drift_phonk, hardstyle_anthem)
- [x] MIDI import: `import_midi()` parses .mid → Song (SMF type 0/1, zero deps)
- [x] `midi_to_note_name()` utility in engine.py
- [x] CLI `--import-midi` flag renders .mid directly to WAV
- [x] Update docs with MIDI import usage (creators, theory, developers, README)
- [x] Tag v1.8.0 release

## v1.9 Roadmap

- [x] Live coding: `--watch --play` auto-renders and plays on every file save
- [x] Tag v1.9.0 release

## v2.0 Roadmap

- [x] `Section.repeat(n)` — avoid manual section duplication in arrangements
- [x] `Track.concat(other)` — join tracks end-to-end for sectional composition
- [x] Deprecation warning on `song._effects` (redirects to `song.effects`)
- [x] Batch migrate 138 files from `_effects` → `effects`
- [x] Clean internal engine.py/synth.py references to `_effects`
- [x] 5 new songs (105 total): repeat_offender, concat_highway, afro_house, raga_dawn, mashup_machine
- [x] 14 new tests for Section.repeat, Track.concat, _effects deprecation
- [x] Tag v2.0.0 release

## v2.1 Roadmap

- [x] `Track.transpose(semitones)` — new Track with all Notes/Chords shifted
- [x] `Track.loop(n)` — repeat existing beats N times
- [x] `Song.render()` — convenience wrapper for Synth().render_song()
- [x] `EffectsChain.to_dict()`/`from_dict()` — serialization + round-trip restore
- [x] 27 new tests across all 4 features
- [x] Tag v2.1.0 release

## v2.2 Roadmap

- [x] Wire up `bpm_ramp`: add `Song.bpm_map` field + Synth per-beat tempo rendering
- [x] `Track.split(at_beat)` — split track into two at a given beat position
- [x] `Track.filter(predicate)` — new track with matching beats, rests for rejected
- [x] AGENTS.md migration: `_effects` → `effects` + EffectsChain example
- [x] Fix `bpm_ramp`/`accelerando`/`ritardando` docstrings (remove nonexistent function refs)
- [x] 5 new songs (110 total): tempo_drift, split_personality, filter_funk, canon_machine, accelerando_chase
- [x] 20 new tests for bpm_map, split, filter
- [x] Tag v2.2.0 release

## v2.3 Roadmap

- [x] `Track.slice(start_beat, end_beat)` — extract a subsection
- [x] `Song.to_dict()` / `Song.from_dict()` — full JSON-compatible serialization
- [x] CLI `--info` flag — show title/BPM/duration/tracks without rendering
- [x] Song smoke tests: 110 parametrized tests verify every song imports + defines `song`
- [x] 15 feature tests (slice, serialization round-trip, CLI info)
- [x] Tag v2.3.0 release

## v2.4 Roadmap

- [x] Fix CI: use `sys.executable` in CLI test (no `.venv/bin/python` in CI)
- [x] `Track.merge(other)` — overlay two tracks at same beat positions
- [x] `Track.stretch(factor)` — time-stretch by scaling all beat durations
- [x] `Song.export_json()` / `Song.load_json()` — file-level JSON serialization
- [x] 5 new songs (115 total): merged_grooves, time_warp, persian_nights, stutter_step, json_roundtrip
- [x] 15 new tests for merge, stretch, export/load JSON
- [x] Tag v2.4.0 release

## v2.5 Roadmap — Packaging & Distribution

- [x] `__version__` via `importlib.metadata` in `__init__.py`
- [x] CLI `--version` flag (`code-music --version`)
- [x] PyPI metadata: license, authors, readme, keywords, classifiers, urls in pyproject.toml
- [x] Version bumped to 2.5.0 (was 0.2.0)
- [x] `pip install code-music` instructions in README
- [x] PyPI publish job in CI (Trusted Publisher via `pypa/gh-action-pypi-publish`)
- [x] 3 new tests (__version__ importable, semver format, CLI --version)
- [x] Tag v2.5.0 release

## v2.6 Roadmap

- [x] Fix CI: invalid classifier `Sound/Audio :: Synthesis` → `Sound/Audio :: Sound Synthesis`
- [x] Add MIT LICENSE file
- [x] Local `python -m build` verified (sdist + wheel)
- [x] 5 new songs (120 total): gospel_praise, dnb_neurofunk, disco_revival, reggaeton_noche, synthwave_drive
- [x] Tag v2.6.0 release

## v2.7 Roadmap — Interactive Examples

- [x] `examples/` directory with 8 step-by-step tutorials covering entire API
- [x] 01: hello world — simplest possible song
- [x] 02: chords and scales — harmonic building blocks
- [x] 03: effects chain — EffectsChain walkthrough
- [x] 04: arrangement — Section + repeat + Song.arrange
- [x] 05: track transforms — transpose, loop, split, merge, stretch, filter
- [x] 06: MIDI roundtrip — export + import + remix
- [x] 07: JSON save/load — Song serialization workflow
- [x] 08: live coding — --watch --play instant feedback
- [x] README: examples table + "Learn by example" section
- [x] Smoke tests for all 8 examples
- [x] Tag v2.7.0 release

## v2.8 Roadmap

- [x] Fix PyPI publish CI: add `environment: pypi` for OIDC Trusted Publisher
- [x] `make examples` + `make play-examples` Makefile targets
- [x] 5 new songs (125 total): west_coast_g_funk, flamenco_fire, shoegaze_haze, trip_hop_noir, hawaiian_slack_key
- [x] Tag v2.8.0 release

## v2.9 Roadmap — UX Polish

- [x] Fix `--import-midi` requiring dummy script arg (script now optional via `nargs='?'`)
- [x] `code-music --new my_song.py` scaffolds a starter song with template
- [x] `code-music --list-instruments` shows all 65+ synth presets
- [x] `Track.__repr__` — concise: name, instrument, beat count, total_beats, volume
- [x] `Song.__repr__` — concise: title, bpm, track count, duration, track names
- [x] CLI help text rewrite: description + epilog with 8 usage examples
- [x] Clear error message when no script provided
- [x] 10 new tests (repr, --import-midi no-script, --list-instruments, --new, help text, no-script error)
- [x] Tag v2.9.0 release

## v3.0 Roadmap — Performance & Polish

- [x] Profile render pipeline (identified _wave 44%, effects 24%, butter-per-note)
- [x] Cache harmonics lookup in Synth._wave() (was O(presets) per call → O(1))
- [x] CLI `--benchmark` flag: render + report timing without export
- [x] `Song.__len__` (returns track count), `Song.__bool__` (has tracks)
- [x] `Track.__len__` (returns beat count), `Track.__bool__` (has beats)
- [x] Ruff: E501 exemption for song/sample/example/album files (music data, not logic)
- [x] 5 new songs (130 total): dub_reggae, motown_groove, electro_swing, dark_ambient, math_rock
- [x] Tag v3.0.0 release

## v3.1 Roadmap — Discoverability & Final Polish

- [x] GitHub repo: 10 topics (python, music, audio, synthesis, midi, generative-music, dsp, wav, music-generation, creative-coding)
- [x] GitHub repo description updated with pip install command
- [x] GitHub homepage set to README anchor
- [x] `py.typed` marker for PEP 561 type checker support
- [x] 5 new songs (135 total): ambient_techno, bluegrass_picking, garage_rock, prog_metal (5/4), ragtime_rag
- [x] Tag v3.1.0 release

## v3.2 Roadmap — Documentation Quality

- [x] Fix README hero code: `_effects` lambda → `EffectsChain` + `play(song)`
- [x] Fix developer docs: `song._effects` hook → `song.effects` + EffectsChain example
- [x] Fix developer data-flow diagram: `_effects` → `effects`
- [x] Audit all docs/README/AGENTS.md/examples for stale `_effects` refs — zero remaining
- [x] Tag v3.2.0 release

## v3.3 Roadmap — Contributor Infrastructure

- [x] CONTRIBUTING.md with dev setup, song writing guide, PR checklist
- [x] GitHub issue templates: bug report, feature request, new song
- [x] GitHub PR template with checklist
- [x] `make check` target (lint + test in one command)
- [x] Fix duplicate `check` target in Makefile
- [x] 5 new songs (140 total): acid_house, new_wave, industrial_grind, dream_pop, afrobeat_groove
- [x] Tag v3.3.0 release

## v4.0 Roadmap — Web Playground

- [x] `docs/playground.html`: Pyodide-based in-browser code editor + audio renderer
- [x] Loads numpy + scipy + code-music in browser via Pyodide/micropip
- [x] 4 pre-loaded examples (hello world, chords, effects, arrangement)
- [x] WAV rendering in-browser via Web Audio API + blob URLs
- [x] Ctrl/Cmd+Enter keyboard shortcut to run
- [x] Tab key inserts spaces in editor
- [x] Linked from landing page (docs/index.html) and README
- [x] Updated landing page version + description
- [x] Tag v4.0.0 release

## v4.1 Roadmap — Playground Reliability

- [x] Dynamic wheel URL: playground fetches wheel from GitHub releases API (no hardcoded version)
- [x] CI: build wheel + attach to GitHub Release alongside WAV zip
- [x] Better error messages when Pyodide or package load fails
- [x] Ready state shows Ctrl+Enter hint
- [x] Uploaded v4.0.0 wheel to release manually for immediate playground use
- [x] Tag v4.1.0 release

## v5.0 Roadmap — Generative Music + Analysis

- [x] `generate_song(genre, bars, seed)`: assembles complete multi-track songs from genre templates (8 genres: lo_fi, jazz, ambient, edm, rock, classical, funk, hip_hop)
- [x] `detect_key(song)`: Krumhansl-Kessler pitch-class profile correlation — analyzes Song to return (root, mode, confidence)
- [x] CLI `--random [genre]`: generate and play a random song on the fly
- [x] 15 new tests (generate all genres, determinism, render, key detection C/Am/G/chords/empty/generated, CLI genre error)
- [x] Tag v5.0.0 release

## v5.1 Roadmap — Surface v5 Features Everywhere

- [x] Playground: added "Generative (AI Composer)" + "Key Detection" to examples dropdown
- [x] `examples/09_generative.py` — generate_song() tutorial with genre/seed/bars docs
- [x] `examples/10_analysis.py` — detect_key() tutorial with manual + generated songs
- [x] README: added generate_song + detect_key + --random to quick-start code blocks
- [x] README: updated examples table (now 10 entries)
- [x] Landing page: updated version + description to mention "AI composer"
- [x] 2 new example smoke tests
- [x] Tag v5.1.0 release

## v6.0 Roadmap — Custom Sound Design (from scratch, zero deps)

Design your own instruments from raw oscillators, noise, filters, and envelopes.
No WAV files, no external libraries — pure numpy synthesis. Then use them at
any pitch in any song, just like built-in presets.

### Phase 1: SoundDesigner class — build sounds from primitives
- [x] `SoundDesigner` class in `code_music/sound_design.py`
- [x] Oscillator layer: `osc(wave, freq, duration)` — sine, saw, square, triangle, noise
- [x] Multi-oscillator stacking: `add_osc(wave, detune_cents, volume)` — layer oscillators with detuning
- [x] ADSR envelope: `envelope(attack, decay, sustain, release)` — per-layer or master
- [x] Filter: `filter(type, cutoff, resonance)` — lowpass, highpass, bandpass built-in (scipy-free, biquad)
- [x] LFO modulation: `lfo(target, rate, depth)` — modulate pitch, filter cutoff, or volume
- [x] Noise generator: `noise(type)` — white, pink, brown noise layers
- [x] `render(freq, duration, sr)` → mono float64 array — renders the designed sound at any pitch

### Phase 2: Register as instrument — use in any song
- [x] `Synth.register(name, sound_designer)` — registers a SoundDesigner as a playable instrument
- [x] Registered instruments work with `Track(instrument="my_kick")` — same API as built-in presets
- [x] Pitch follows Note frequency automatically (oscillator ratios preserved, not absolute freqs)
- [x] `Song.register_instrument(name, designer)` — song-level registration for portability

### Phase 3: Preset library — built-in designed sounds
- [x] Design 5+ sounds using SoundDesigner that aren't possible with current presets:
  - Supersaw (7-voice detuned sawtooth stack)
  - 808 sub (pitch-drop sine + long release + LP filter)
  - Metallic hit (inharmonic partials + noise burst + bandpass)
  - Vocal pad (detuned sawtooths + bandpass + LFO filter)
  - Plucked string (white noise + triangle + LP filter)
- [x] Ship as `code_music.sound_design.PRESETS` — importable, tweakable

### Phase 4: Export / reuse
- [x] `SoundDesigner.to_dict()` / `from_dict()` — serialize designs to JSON
- [x] `SoundDesigner.to_wav(path, freq, duration)` — render and save as WAV for use in SampleTrack
- [x] `SoundDesigner.preview(freq, duration)` — render + play immediately

### Phase 5: Tests + examples + docs
- [x] Tests: render at multiple pitches, register + play in Song, serialization round-trip (27 tests)
- [x] `examples/11_sound_design.py` — tutorial: build a supersaw from scratch, use in a song
- [x] Playground: add "Sound Design" example to dropdown
- [x] Update for_creators.md and for_theory_heads.md with sound design section
- [x] Update README: examples table (11 entries), SoundDesigner quick-start code block
- [x] Update landing page version + description

### Phase 6: Songs showcasing custom sounds
- [x] 5 songs using only SoundDesigner instruments (synth_lab, oscillator_garden, waveform_rider, noise_floor, custom_kit)
- [x] Tag v6.0.0 release

## v7.0 Roadmap — Advanced Synthesis (SuperCollider-depth, Python ergonomics)

No other Python library does this. pyo comes closest but hits CPython's ceiling
and has no composition integration. We stay pure numpy but add synthesis
techniques that only SuperCollider/CSound/Faust currently offer.

### Phase 1: FM Synthesis
- [ ] `SoundDesigner.fm(carrier, modulator, mod_index)` — frequency modulation
- [ ] Multi-operator FM (2-op, 4-op, 6-op like DX7)
- [ ] FM presets: electric piano, bell, brass, bass

### Phase 2: Wavetable Synthesis
- [ ] `SoundDesigner.wavetable(table)` — user-defined single-cycle waveforms
- [ ] `Wavetable.from_harmonics(amplitudes)` — additive → wavetable
- [ ] `Wavetable.morph(other, amount)` — interpolate between two wavetables
- [ ] Wavetable scanning with LFO

### Phase 3: Granular Synthesis
- [ ] `SoundDesigner.granular(source, grain_size, density, scatter)`
- [ ] Source can be another SoundDesigner, a WAV, or generated noise
- [ ] Time-stretch and pitch-shift via grain manipulation
- [ ] Granular cloud textures for ambient/experimental music

### Phase 4: Physical Modeling
- [ ] Karplus-Strong string (already exists in presets, extract to SoundDesigner)
- [ ] Waveguide flute/pipe model
- [ ] Modal synthesis (struck/plucked resonant body)
- [ ] Bowed string model

### Phase 5: Spectral Processing
- [ ] `SoundDesigner.spectral(process_fn)` — FFT → manipulate → IFFT
- [ ] Spectral freeze, smear, shift, stretch
- [ ] Cross-synthesis: apply spectrum of one sound to another
- [ ] Vocoder built on spectral processing

### Phase 6: Timbre as Data
- [ ] `SoundDesigner.analyze()` → spectral fingerprint dict
- [ ] `timbre_a.distance(timbre_b)` — perceptual distance metric
- [ ] `timbre_a.morph(timbre_b, amount=0.5)` — interpolate between timbres
- [ ] Timbres are JSON-serializable, diffable, versionable

## v8.0 Roadmap — Pattern Language (TidalCycles expressiveness in Python)

TidalCycles has the most expressive pattern system ever built, but requires
Haskell + SuperCollider. We bring pattern transforms to Python.

- [ ] `Pattern` class: `p("C3 E3 G3 C4")` mini-notation for note sequences
- [ ] Pattern transforms: `p.reverse()`, `p.every(4, reverse)`, `p.jux(rev)`
- [ ] Euclidean rhythms: `p.euclid(5, 8)` — distribute N hits over M slots
- [ ] Polyrhythm: `p.polymeter(p1, p2)` — layer patterns of different lengths
- [ ] Stochastic patterns: `p.choose(["C3", "E3", "G3"])`, `p.degrade(0.3)`
- [ ] Pattern → Track conversion: `pattern.to_track(instrument="supersaw")`
- [ ] Mini-notation parser: `"[C3 E3] G3 [A3 B3 C4]"` — brackets for subdivisions

## v9.0 Roadmap — Gallery & Showcase

The entire library showcased through curated, categorized demos.

### Instrument Gallery
- [ ] `gallery/instruments/` — one file per SoundDesigner preset, renders to WAV
- [ ] Each file: design → render at C3/C4/C5 → play all three pitches
- [ ] `make gallery-instruments` — renders all, creates HTML index with audio players
- [ ] Web gallery page on GitHub Pages with waveform visualizations

### Synthesis Technique Gallery
- [ ] `gallery/techniques/` — FM, wavetable, granular, physical modeling, spectral
- [ ] Each technique: minimal example + full song using only that technique
- [ ] Side-by-side comparisons (same melody, different synthesis)

### Song Showcase
- [ ] `gallery/songs/` — curated "best of" with descriptions and audio
- [ ] Organized by genre, mood, and synthesis technique used
- [ ] `make gallery` — builds entire gallery site to `dist/gallery/`

### Scale & Theory Gallery
- [ ] `gallery/scales/` — every scale rendered with the same instrument for comparison
- [ ] `gallery/chords/` — every chord shape rendered and visualized
- [ ] `gallery/progressions/` — common progressions in all keys

## v10.0 Roadmap — Production Pipeline

Bridge the gap from "cool demo" to "this goes on Spotify."

- [ ] `Song.master()` improvements: LUFS loudness targeting (-14 LUFS for streaming)
- [ ] Dithering (TPDF) for 16-bit export
- [ ] True peak limiting (ISP)
- [ ] Stereo imaging analysis + correction
- [ ] `code-music master song.wav --target-lufs=-14 --format=flac` CLI
- [ ] Batch mastering: `make master` processes all songs to release-ready specs
- [ ] Metadata embedding (ID3 tags for MP3, Vorbis comments for FLAC/OGG)

## v11.0 Roadmap — Automation & Modulation Matrix

Every parameter should be automatable. Move from static values to envelopes
over time — the difference between a sketch and a finished production.

### Phase 1: Parameter Automation
- [ ] `Automation(param, keyframes)` — time-value curves for any numeric param
- [ ] `Track.automate("volume", [(0, 0.0), (4, 0.8), (12, 0.3)])` — per-track
- [ ] `Song.automate("bpm", [(0, 120), (16, 140)])` — replaces bpm_ramp with general system
- [ ] Linear, exponential, and smoothstep interpolation modes
- [ ] `EffectsChain.automate(step_idx, "wet", [(0, 0), (8, 0.5)])` — per-effect param

### Phase 2: Modulation Matrix
- [ ] `ModMatrix` — route any source to any destination with scaling
- [ ] Sources: LFO, envelope follower, random, note velocity, beat position
- [ ] Destinations: volume, pan, filter cutoff, effect params, pitch
- [ ] `song.mod_matrix.connect(source="lfo1", dest="pad.filter_cutoff", amount=0.5)`
- [ ] Visualizable as a routing table in `__repr__`

### Phase 3: Sidechain Automation
- [ ] Envelope follower source: `EnvFollower(track_name)` — derives amplitude from another track
- [ ] Classic sidechain pump: `mod_matrix.connect(source=EnvFollower("kick"), dest="pad.volume", amount=-0.8)`
- [ ] Ducking without the `sidechain()` effect — works at mix level

### Phase 4: Tests + docs + songs
- [ ] Tests for automation curves, mod matrix routing, envelope follower
- [ ] `examples/12_automation.py` — automate filter sweeps and volume fades
- [ ] 5 songs showcasing automation (150 total)
- [ ] Tag v11.0.0 release

## v12.0 Roadmap — Collaboration & Stems

Make code-music multiplayer. Two people should be able to work on the same song
from different files and merge the result.

### Phase 1: Song Merge Improvements
- [ ] `Song.overlay(other, at_beat)` — drop another song's tracks at a specific beat offset
- [ ] `Song.append(other)` — concatenate songs end-to-end (auto-adjusts beat offsets)
- [ ] `Song.extract_tracks(names)` — pull specific tracks into a new Song
- [ ] Conflict resolution: track name collisions get `_2` suffix

### Phase 2: Stem Import/Export
- [ ] `Song.import_stems(directory)` — load a folder of WAVs as SampleTracks
- [ ] `Song.export_stems()` improvements: include effects, master chain per-stem option
- [ ] Stem naming convention: `{song_title}_{track_name}.wav`
- [ ] Round-trip: export stems → reimport → identical render

### Phase 3: Song Diffing
- [ ] `song_diff(a, b)` — structural diff showing added/removed/changed tracks, notes, effects
- [ ] Human-readable output: "Track 'lead' added 4 notes at beat 8"
- [ ] Machine-readable: returns a list of `Change` objects for programmatic use
- [ ] `song_patch(base, changes)` — apply a diff to reconstruct a song

### Phase 4: Collaborative Workflow
- [ ] `code-music merge song_a.py song_b.py -o merged.py` CLI
- [ ] Git-friendly: JSON serialization enables standard diff/merge tools
- [ ] `make collab` target: renders all songs, exports stems to shared folder
- [ ] 5 songs built collaboratively from merged parts (155 total)
- [ ] Tag v12.0.0 release

## v13.0 Roadmap — Live Performance Mode

Real-time loop-based performance in the terminal. Think Ableton Live's
session view, but in Python.

### Phase 1: Clip System
- [ ] `Clip(track, start_beat, end_beat)` — loopable section of a track
- [ ] `Clip.loop(n)` — repeat N times, `Clip.loop_forever()` — until stopped
- [ ] `ClipSlot` — holds a clip + play/stop state
- [ ] Clips quantize to bar boundaries (configurable grid)

### Phase 2: Session View
- [ ] `Session(bpm)` — holds a grid of ClipSlots (tracks × scenes)
- [ ] `Session.play_scene(idx)` — trigger all clips in a scene row
- [ ] `Session.stop_track(name)` — stop a specific track
- [ ] Mix-level controls: volume, pan, mute, solo per track

### Phase 3: Real-Time Rendering
- [ ] Session renders in real-time using sounddevice stream callback
- [ ] Clip transitions: crossfade, hard cut, or beat-synced
- [ ] Effect bypass toggling in real-time
- [ ] BPM changes apply at next bar boundary

### Phase 4: TUI Dashboard
- [ ] `code-music session song.py` — launches terminal session view
- [ ] Grid display: tracks as columns, scenes as rows, colors for playing/queued/stopped
- [ ] Keyboard shortcuts: 1-9 for scenes, q/w/e/r for track mute, space for stop-all
- [ ] MIDI input support (optional): trigger clips from a MIDI controller
- [ ] 5 songs with session arrangements (160 total)
- [ ] Tag v13.0.0 release

## v14.0 Roadmap — Music Theory Intelligence

Make the engine understand music theory deeply enough to suggest, correct,
and generate with real harmonic awareness.

### Phase 1: Chord-Scale Theory
- [ ] `chord_scale(chord)` — returns compatible scales for improvisation
- [ ] `available_tensions(chord)` — 9th, 11th, 13th options that don't clash
- [ ] `voice_lead(prog, voice_count=4)` improvements: SATB rules, parallel 5th avoidance
- [ ] `analyze_harmony(song)` — full roman numeral + function analysis (tonic/subdominant/dominant)

### Phase 2: Intelligent Generation
- [ ] `generate_song()` improvements: key changes, modulation, bridge sections
- [ ] `generate_bass_line(chords, style)` — walking bass, root-fifth, syncopated
- [ ] `generate_drums(genre, fills_every=8)` — pattern-based with fills and variations
- [ ] `generate_melody(chords, contour)` — melody that follows harmonic rhythm
- [ ] Counterpoint generator: `generate_counterpoint(melody, species=1)`

### Phase 3: Analysis Dashboard
- [ ] `Song.analyze()` — returns full report: key, tempo, chord progression, density, dynamics
- [ ] Harmonic rhythm visualization (chord changes over time)
- [ ] Melodic contour analysis: step/skip/leap statistics
- [ ] Tension/release curve: consonance score over time

### Phase 4: Theory Examples + Tests
- [ ] `examples/13_theory.py` — chord-scale theory, voice leading, analysis
- [ ] 5 songs generated with advanced theory features (165 total)
- [ ] Tag v14.0.0 release
