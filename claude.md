# code-music — project state

## Status: v143.0.0 — 323 songs, 2838 tests, 455+ theory functions, 44 scales

## Current state (for new conversations)

theory.py is ~10,500 lines with 385+ public functions. The module covers:
chromatic harmony, advanced rhythm (tuplets through irrational meters),
voice leading (SATB, constraints), modulation, Roman numerals, counterpoint
(species 1/2, validation, grading), generative melody (contour-shaped,
Markov, Mozart dice game), 44 scales (14 standard + 30 exotic), jazz
voicings (Evans rootless, Tyner quartal, stride, 30+ voicing DB), form
templates (5 forms + SongTemplate class), harmonic analysis (functional,
cadences, tension curves, complexity, ambiguity, full markdown reports),
genre-specific bass (jazz/funk/Latin), comping (5 styles), harmonization
(thirds/sixths/chorale), dynamics, tempo curves (rit/accel/rubato),
duration algebra, instrument techniques (hammer/pull/slide/palm mute),
ear training + quizzes, remix (key change, double/half time), 6 groove
templates, chord substitution + reharmonization (3 styles), orchestration
(19 instruments), microtuning (just intonation, quarter tones), texture
density control, lyrics-to-melody, enharmonic spelling, DSL parser,
voice independence scoring, 20-pattern melodic DB, practice tools (click
tracks, backing tracks, tempo trainer), corpus stats, Markov transitions,
serial composition (tone rows, transforms, interval vectors), ambient
generation (drone, evolving pad), pitch set operations, song fingerprinting
+ similarity, chord morphing, melody smoothing, and comprehensive stats
(pitch/velocity/duration/rest/leap/repetition/octave/summary).

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

### FM Synthesis
- SoundDesigner.fm(): carrier wave, mod_ratio, mod_index, volume — stack for multi-operator
- 4 FM presets (fm_electric_piano, fm_bell, fm_brass, fm_bass)

### Wavetable Synthesis
- Wavetable class: from_harmonics, from_wave, morph between shapes
- SoundDesigner.add_wavetable(): use custom waveforms as oscillators
- 3 wavetable presets (wt_organ, wt_bright_lead, wt_morph_pad)

### Euclidean Rhythms
- euclid(hits, steps): Bjorklund algorithm for mathematically-perfect beat distribution
- Rotation parameter for shifted patterns
- Tresillo, son clave, bossa nova — all generated from (N, M) pairs

### Granular Synthesis
- SoundDesigner.granular(): grain_size, density, scatter, seed — cloud textures
- 2 presets (grain_cloud, grain_shimmer)

### Physical Modeling
- Karplus-Strong plucked string, waveguide pipe/flute, modal struck body
- SoundDesigner.physical_model(): karplus_strong, waveguide_pipe, modal
- 3 presets (pm_guitar, pm_flute, pm_gong)

### Pattern Language
- Pattern class: mini-notation parser ("C4 E4 ~ G4"), transforms, polymeter
- Transforms: reverse, rotate, fast, slow, degrade, every, choose, cat
- Pattern.polymeter(): layer patterns of different lengths (LCM cycling)
- Pattern.to_notes(): convert to Note list for Track integration

### Spectral Processing
- SoundDesigner.spectral(fn): FFT-based post-processing on rendered audio
- Built-in: spectral_freeze, spectral_shift, spectral_smear
- Chain multiple .spectral() calls, custom lambda support

### Timbre Analysis
- SoundDesigner.analyze() -> Timbre: spectral fingerprint (centroid, bandwidth, flatness, rolloff, RMS)
- Timbre.distance(): perceptual distance between sounds
- Timbre.morph(): interpolate between timbres
- Timbre.to_dict(): JSON-serializable

### Analysis & Visualization
- to_tab(): ASCII guitar/bass tablature with fret numbers
- analyze_harmony(): Roman numeral analysis + harmonic function (tonic/subdominant/dominant)
- song_map(): ASCII density map showing per-track activity per bar

### Composition Intelligence
- composition.py: continue_melody() — Markov chain melody continuation (order 1-2)
- Named sections: Verse, Chorus, Bridge, Intro, Outro (Section subclasses)
- to_lead_sheet() — ASCII chord symbols + melody notation
- Supports major, minor, dorian, pentatonic, blues keys

### JSON Serialization
- serialization.py: song_to_json/song_from_json — full round-trip Song ↔ JSON
- Supports notes, chords, rests, custom SoundDesigner instruments, metadata
- Output to dict, string, or file. Input from dict, string, or file path.
- Enables collaboration (JSON exchange), web export, version control

### Music Theory Intelligence
- chord_scale(): compatible scales for chord improvisation (14 scales × all chord types)
- available_tensions(): 9th/11th/13th analysis for any chord
- generate_bass_line(): root, root_fifth, walking, syncopated styles
- generate_drums(): rock, jazz, electronic, latin, hiphop genre patterns
- song_diff/song_patch: structural diff + patch for collaboration

### Automation & Modulation
- Automation class: keyframed parameter curves (linear, exponential, smoothstep)
- value_at() interpolation, sample() for per-sample arrays
- ModMatrix: route LFO/random/envelope sources to any destination
- generate_mod_signal() for LFO, random (smoothed), envelope sources
- Song composition: song_overlay, song_append, song_extract utilities

### Mastering Pipeline
- mastering.py: LUFS metering (ITU-R BS.1770 simplified), normalize_lufs, true_peak_limit
- TPDF dithering for 16/24-bit export, stereo_analysis (correlation/width/balance)
- master_audio(): full chain (normalize → limit → dither) in one call

### Synth (80+ presets)
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

### Songs: 323 | Albums: 23 | Scale demos: 31 | Samples: 100+ | Styles: 7

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
- [x] `SoundDesigner.fm(carrier_wave, mod_ratio, mod_index, volume)` — frequency modulation
- [x] Multi-operator FM (stack .fm() calls, unlimited operators)
- [x] FM presets: fm_electric_piano, fm_bell, fm_brass, fm_bass

### Phase 2: Wavetable Synthesis
- [x] `SoundDesigner.add_wavetable(table, volume, detune_cents)` — user-defined single-cycle waveforms
- [x] `Wavetable.from_harmonics(amplitudes)` — additive → wavetable
- [x] `Wavetable.from_wave(name)` — built-in wave shapes
- [x] `Wavetable.morph(other, amount)` — interpolate between two wavetables
- [x] Wavetable presets: wt_organ, wt_bright_lead, wt_morph_pad
- [ ] Wavetable scanning with LFO (future)

### Phase 3: Granular Synthesis
- [x] `SoundDesigner.granular(grain_size, density, scatter, volume, seed)`
- [x] Source: base frequency sine grains with Hann windowing
- [x] Granular cloud textures for ambient/experimental music
- [x] 2 presets: grain_cloud, grain_shimmer
- [ ] Time-stretch and pitch-shift via grain manipulation (future)

### Phase 4: Physical Modeling
- [x] Karplus-Strong plucked string with decay and brightness params
- [x] Waveguide pipe/flute model with feedback and brightness
- [x] Modal synthesis (struck resonant body with configurable modes)
- [x] 3 presets: pm_guitar, pm_flute, pm_gong
- [ ] Bowed string model (future)

### Phase 5: Spectral Processing
- [x] `SoundDesigner.spectral(process_fn)` — FFT → manipulate → IFFT
- [x] `spectral_freeze(amount)` — sustain spectral content (STFT-based)
- [x] `spectral_shift(semitones)` — frequency bin shifting
- [x] `spectral_smear(amount)` — blur spectral magnitudes
- [x] Chain multiple .spectral() calls, custom lambda support
- [ ] Cross-synthesis: apply spectrum of one sound to another (future)
- [ ] Vocoder built on spectral processing (future)

### Phase 6: Timbre as Data
- [x] `SoundDesigner.analyze()` → Timbre object with spectral fingerprint
- [x] `timbre.distance(other)` — weighted Euclidean on normalized features
- [x] `timbre.morph(other, amount)` — interpolate between timbres
- [x] `timbre.to_dict()` — JSON-serializable
- [x] Features: centroid, bandwidth, flatness, rolloff, RMS

## v8.0 Roadmap — Pattern Language (TidalCycles expressiveness in Python)

TidalCycles has the most expressive pattern system ever built, but requires
Haskell + SuperCollider. We bring pattern transforms to Python.

- [x] `Pattern` class: `p("C3 E3 G3 C4")` mini-notation for note sequences
- [x] Pattern transforms: `p.reverse()`, `p.every(4, fn)`, `p.rotate(n)`, `p.fast(n)`, `p.slow(n)`
- [x] Euclidean rhythms: `euclid(hits, steps)` — Bjorklund algorithm (shipped v7.0)
- [x] Polyrhythm: `Pattern.polymeter(p1, p2)` — layer patterns of different lengths (LCM cycling)
- [x] Stochastic patterns: `p.choose(seed)`, `p.degrade(0.5, seed)`
- [x] Pattern → Track conversion: `p.to_notes(duration, default_octave, velocity)`
- [x] Mini-notation parser: `"[C3 E3] G3"` brackets, `~` rests, `*N` repeat, `?` random

## v39.0 Roadmap — Chromatic Harmony

Classical chromatic techniques — the colors between the colors.

- [x] `neapolitan_chord(key)` — bII major in first inversion, classic pre-dominant
- [x] `augmented_sixth(key, variety)` — Italian (3-note), French (4-note, whole-tone), German (4-note, dom7 enharmonic)
- [x] `picardy_third(key)` — major tonic in minor key context (Baroque surprise ending)
- [x] 3 songs: neapolitan_sunset, italian_sixth_waltz, picardy_dawn
- [x] 18 tests across all varieties and keys

## v40.0 Roadmap — Advanced Rhythm

Beyond triplets — irregular subdivisions, polyrhythms, and metric modulation.

- [x] `quintuplet(notes, total_duration)` — 5 in the space of 4
- [x] `septuplet(notes, total_duration)` — 7 in the space of 4/8
- [x] `generate_polyrhythm(root, rhythm_a, rhythm_b, bars)` — two interlocking patterns (3:4, 5:4, etc)
- [x] `metric_modulation(bpm, old_subdivision, new_subdivision)` — calculate new BPM after subdivision reinterpretation
- [x] 3 songs: polyrhythm_lab, metric_shift, five_against_four
- [x] 17 tests for all rhythm functions

## v41.0 Roadmap — Chord Progression Templates

The canonical progressions every musician should know, generated in any key.

- [x] `twelve_bar_blues(key)` — I-I-I-I-IV-IV-I-I-V-IV-I-V, all dom7
- [x] `rhythm_changes(key)` — Gershwin's 'I Got Rhythm' A section (I-vi-ii-V turnaround)
- [x] `coltrane_changes(key)` — Giant Steps substitution (3 tonal centers, major thirds apart)
- [x] `andalusian_cadence(key)` — i-bVII-bVI-V (flamenco/Phrygian descending bass)
- [x] 4 songs: twelve_bar_shuffle, giant_steps_study, rhythm_changes_blowout, andalusian_night
- [x] 20 tests for all progression templates

## v42.0 Roadmap — Voice Leading Engine

Proper four-part voice leading with SATB rules — the foundation of
classical composition that every theory textbook teaches but no Python
library implements.

- [x] `voice_lead_satb(progression, key)` — four-part harmonization with smooth voice leading
- [x] Voice range constraints: S(C4-G5), A(F3-D5), T(C3-A4), B(E2-E4)
- [x] Smooth voice leading: minimize total semitone movement between chords
- [x] Handle common tones (retain shared notes in the same voice)
- [x] `check_parallel_fifths(voicing_a, voicing_b)` — detect forbidden parallel P5/P8
- [x] No voice crossing (sorted output ensures soprano > alto > tenor > bass)
- [x] 1 song: satb_chorale
- [x] 10 tests for voice leading and parallel detection

## v43.0 Roadmap — Key Modulation & Pivot Chords

Smooth key changes — the art of moving between tonal centers without
the listener noticing (until the emotional payoff hits).

- [x] `find_pivot_chords(key_a, key_b)` — chords that exist diatonically in both keys
- [x] `modulation_path(key_a, key_b)` — shortest path via circle of fifths with V-I cadences
- [x] `direct_modulation(key_a, key_b)` — abrupt key change (truck driver modulation)
- [x] `pivot_modulation(key_a, key_b)` — smooth transition via first common chord
- [x] 2 songs: modulation_journey, pivot_chord_study
- [x] 19 tests for pivot detection, path finding, direct/pivot modulation

## v44.0 Roadmap — Roman Numeral Parsing

Read and write the universal language of harmony analysis.

- [x] `parse_roman(numeral, key)` — 'viio7/V' → (root, shape) in context
- [x] Support applied chords: V/V, V7/ii, vii/vi, etc
- [x] Support alterations: bVI, #IV, bII (Neapolitan)
- [x] Support quality suffixes: maj7, min7, dom7, o, o7, +, sus2, sus4, 9
- [x] `progression_from_roman(numerals, key)` — ['I', 'IV', 'V7', 'I'] → chord list
- [x] 2 songs: roman_numeral_pop, jazz_numerals
- [x] 25 tests for parsing, applied chords, accidentals, progressions

## v45.0 Roadmap — Rhythmic Displacement & Metric Illusions

Shift patterns against the beat to create rhythmic tension.

- [x] `displace(notes, offset_beats)` — shift a pattern forward by inserting a leading rest
- [x] `phase_shift(pattern_a, pattern_b, offset)` — Steve Reich-style phasing
- [x] `hemiola(note, octave, bars)` — 3-against-2 grouping across barlines
- [x] `additive_rhythm(groups, note, octave)` — e.g. [2,3,2,2,3] with accented downbeats
- [x] `aksak(pattern_name)` — named Balkan rhythms: 5/8, 7/8, 9/8, 11/8, 15/8
- [x] 3 songs: balkan_stomp, reich_phase, hemiola_waltz
- [x] 18 tests for displacement, phasing, hemiola, additive, aksak

## v46.0 Roadmap — Counterpoint Species

Species counterpoint — the 500-year-old composition method that trained
Bach, Mozart, and Beethoven.

- [x] `classify_interval(semitones)` — perfect / imperfect / dissonant classification
- [x] `species_counterpoint(cantus_firmus, species=1)` — note-against-note (species 1)
- [x] Species 2: two notes against one (strong beat consonant, weak beat passing)
- [x] Deterministic output via seed parameter
- [x] Above/below CF with octave clamping
- [x] 1 song: species_study
- [x] 19 tests for interval classification, species 1/2, rests, determinism

## v47.0 Roadmap — Generative Melody

Scale-aware melody generation with contour shaping and rhythm patterns.

- [x] `generate_scale_melody(key, scale, length, contour, seed)` — biased random walk constrained to scale degrees
- [x] Four contour shapes: arch (peak at middle), descending, wave (sinusoidal), flat
- [x] `generate_rhythm_pattern(hits, slots, seed)` — random rhythm with rests, avoids clustering
- [x] 2 songs: contour_arch, wave_melody
- [x] 18 tests for melody generation, rhythm patterns, contours, determinism

## v48.0 Roadmap — Chord Voicing Library

Genre-specific voicings that real pianists actually use.

- [x] `rootless_a(root, shape)` — Bill Evans A voicing (3rd on bottom, omit root)
- [x] `rootless_b(root, shape)` — Bill Evans B voicing (7th on bottom, omit root)
- [x] `quartal_voicing(root, layers)` — McCoy Tyner stacked perfect 4ths
- [x] `stride_voicing(root, shape)` — stride piano (low root + mid-register chord)
- [x] 2 songs: evans_voicings, quartal_towers
- [x] 15 tests for all voicing types

## v49.0 Roadmap — Form Templates & Song Blueprints

Pre-built song structures as section-name lists.

- [x] `song_form(name)` — returns section list: pop, aaba, blues, edm, rondo
- [x] `section_bars(name, bars_per_section)` — (section, bars) tuples for auto-arrangement
- [x] 1 song: pop_form_demo
- [x] 9 tests for all form templates

## v50.0 Roadmap — Harmonic Analysis

Automated harmonic analysis — the kind of report a theory professor puts
on the blackboard, but in Python.

- [x] `functional_analysis(progression, key)` — Roman numeral + T/S/D function per chord
- [x] `detect_cadences(progression, key)` — authentic, half, plagal, deceptive
- [x] `detect_key(progression)` — key estimation from root frequency with tiebreaker
- [x] 1 song: cadence_detective
- [x] 21 tests for functional analysis, cadence detection, key estimation

## v51.0 Roadmap — Ear Training Tools

Music education: generate exercises for intervals, chords, and scales.

- [x] `ear_training_intervals(count, max_semitones, seed)` — melodic interval quizzes with correct answers
- [x] `ear_training_chords(count, types, seed)` — chord quality identification exercises
- [x] `scale_exercise(key, mode, direction)` — ascending, descending, or both
- [x] 2 songs: interval_drills, scale_practice
- [x] 18 tests for exercise generation, structure, determinism

## v52.0 Roadmap — Tension & Resolution Curves

Quantify emotional intensity over time.

- [x] `tension_curve(progression, key)` — 0.0–1.0 per chord (harmonic distance + complexity + dominant function)
- [x] `tension_at(progression, index, key)` — point query for tension at a chord index
- [x] Tonic chords lowest tension, dominants high, chromatic chords highest
- [x] 1 song: tension_arc
- [x] 9 tests for curve shape, range, tonic/dominant ordering

## v53.0 Roadmap — Orchestration & Instrument Doubling

Range-aware instrument assignment and ensemble templates.

- [x] `instrument_range(name)` — playable range for 19 instruments (violin→bass_voice)
- [x] `in_range(note, instrument)` — check if a note is playable
- [x] `double_at_octave(notes, direction)` — octave doubling up or down
- [x] `string_quartet(melody, harmony, key)` — auto-arrange for violin I/II, viola, cello
- [x] 2 songs: string_quartet_no1, octave_doubling
- [x] 14 tests for range validation, doubling, quartet arrangement

## v54.0 Roadmap — Motif Development & Variation

Classical motif development techniques — the Beethoven toolkit.

- [x] `augment(motif, factor)` — multiply note durations (rhythmic augmentation)
- [x] `diminish(motif, factor)` — divide note durations (rhythmic diminution)
- [x] `fragment(motif, length)` — extract the head motif
- [x] `motif_similarity(a, b)` — contour + rhythm comparison, 0.0–1.0 score
- [x] 1 song: motif_development
- [x] 15 tests for augmentation, diminution, fragmentation, similarity

## v55.0 Roadmap — MIDI Import/Export

Already existed (export_midi, import_midi in code_music.midi). Skipped.

## v56.0 Roadmap — Scale Atlas

44 scales from around the world — catalogued, searchable, and playable.

- [x] 30 exotic scales added: hungarian_minor, hungarian_major, hirajoshi, in_sen,
      iwato, phrygian_dominant, double_harmonic, enigmatic, prometheus, augmented,
      tritone, bebop_dominant/major/minor, neapolitan_major/minor, persian,
      arabian, balinese, chinese, egyptian, kumoi, pelog, spanish_gypsy,
      super_locrian, lydian_dominant, lydian_augmented, half_diminished, altered, acoustic
- [x] `list_scales()` — all 44 scale names, sorted alphabetically
- [x] `scale_search(pitches)` — reverse lookup: which scales contain these notes?
- [x] `scale_brightness(name)` — 0.0 (dark, Locrian) to 1.0 (bright, Lydian)
- [x] `scale_modes(name)` — generate all rotational modes of any scale
- [x] Fixed scale_explorer.py: added fallback mappings for new scale names in chord_scale results
- [x] 3 songs: hirajoshi_garden, hungarian_fire, double_harmonic_dusk
- [x] 19 tests for listing, search, brightness, modes

## v57.0 Roadmap — Real-Time Performance Engine

Skipped — requires sounddevice runtime dependency.

## v58.0 Roadmap — Lyric Rhythm Matching

Map syllable stress to musical rhythm and pitch.

- [x] `count_syllables(word)` — vowel-cluster heuristic with silent-e adjustment
- [x] `stress_pattern(text)` — strong/weak per syllable (content vs function words, alternating stress)
- [x] `text_to_melody(text, key, scale, seed)` — stressed syllables get higher pitch + longer duration,
      questions rise at end, statements fall
- [x] 1 song: lyrics_to_melody
- [x] 14 tests for syllable counting, stress, melody generation, determinism

## v59.0 Roadmap — Groove Templates & Swing Maps

Pre-built timing feels that make music breathe.

- [x] `groove_template(name)` — 6 named grooves: straight, mpc_swing, j_dilla, motown, shuffle, bossa
- [x] `apply_groove(notes, template, strength)` — adjust durations to simulate timing feel
- [x] `extract_groove(notes, grid_duration)` — capture timing deviations from a grid
- [x] 1 song: dilla_groove
- [x] 14 tests for all grooves, application, extraction, strength control

## v60.0 Roadmap — Chord Substitution Engine

Automated reharmonization — change the color without breaking the function.

- [x] `suggest_substitutions(root, shape, key)` — tritone sub, related ii, modal interchange, relative
- [x] `reharmonize(progression, key, style)` — jazz (tritone + related ii), modal (major↔minor swap), simple (relative swap)
- [x] 1 song: reharmonized_pop
- [x] 13 tests for substitution types, reharmonization styles, length preservation

## v61.0 Roadmap — Song Fingerprinting & Similarity

Compare songs by their harmonic and melodic DNA.

- [x] `song_fingerprint(progression, notes)` — pitch histogram (12 bins), quality distribution,
      average interval, rhythm density, chord count
- [x] `song_similarity(fp_a, fp_b)` — cosine similarity on pitch histograms (0.0–1.0)
- [x] 10 tests for fingerprint structure, similarity identity, relative ranking

## v62.0 Roadmap — Counterpoint Rules Validator

Strict grading engine for counterpoint exercises.

- [x] `validate_counterpoint(cf, cp, species)` — returns list of violation strings:
      parallel P5/P8, voice crossing, dissonant intervals, leaps > octave
- [x] `grade_counterpoint(cf, cp, species)` — 0–100 score (100 = no violations, -10 per violation)
- [x] 8 tests for rule detection, perfect score, floor at zero

## v63.0 Roadmap — Chord Tone Targeting

Jazz improvisation: land on chord tones at strong beats, fill with scale tones.

- [x] `target_chord_tones(progression, key, notes_per_chord, seed)` — even beats = chord tones,
      odd beats = scale passing tones
- [x] `approach_pattern(target, direction, duration)` — chromatic (half-step), diatonic (whole-step),
      or enclosure (above+below) approach to a target note
- [x] 2 songs: chord_tone_solo, song_300 (300th song milestone!)
- [x] 11 tests for targeting, approach patterns, determinism

## v64.0 Roadmap — Multi-Tonic Systems

Schoenberg's 12-tone method and Forte's set theory — in Python.

- [x] `tone_row(pitches, seed)` — create a 12-tone row (all 12 PCs, no repeats)
- [x] `row_transforms(row)` — prime, retrograde, inversion, retrograde-inversion
- [x] `interval_vector(pitch_set)` — Forte-style 6-element IC vector
- [x] 1 song: serial_composition
- [x] 15 tests for row generation, transforms, interval vectors

## v65.0 Roadmap — Song Structure Detection

Automatically identify repeated sections and label form.

- [x] `section_similarity_matrix(progression, bars_per_section)` — Jaccard similarity on pitch-class sets
- [x] `detect_sections(progression, bars_per_section, threshold)` — group similar sections with same label
- [x] `label_form(progression, bars_per_section)` — return form string ("AABA", "ABAB", etc)
- [x] 1 song: form_detective
- [x] 10 tests for matrix shape, AABA detection, ABAB detection

## v66.0 Roadmap — Drone & Ambient Generator

Brian Eno in a function — sustained tones and slowly morphing textures.

- [x] `drone(key, octave, duration, overtones)` — root + harmonic overtone series with decaying velocity
- [x] `evolving_pad(key, scale, duration, density, octave, seed)` — random scale-tone cloud with varying durations
- [x] 1 song: ambient_drift
- [x] 10 tests for drone structure, overtone decay, pad duration bounds

## v67.0 Roadmap — Tuplet Nesting & Complex Meters

Carter, Ferneyhough, and progressive metal territory.

- [x] `nested_tuplet(outer, inner, notes, total_duration)` — e.g. quintuplets inside triplets (3*5=15 notes)
- [x] `irrational_meter(numerator, denominator, bars)` — 7/12, 5/6, etc. with accented beat 1
- [x] `polymetric_overlay(meters, note, octave, bars)` — layer multiple meters, each voice offset by octave
- [x] 1 song: nested_rhythms
- [x] 15 tests for nesting, duration math, irrational scaling, polymetric voices

## v68.0 Roadmap — Harmonic Reduction

The opposite of reharmonization — strip to the functional core.

- [x] `reduce_to_chords(notes, beats_per_chord)` — collapse melody to best-matching triads
- [x] `harmonic_skeleton(progression, key)` — reduce to I/IV/V by functional group
- [x] `complexity_score(progression, key)` — 0–100 rating (root variety + quality variety + chromatic + length)
- [x] 1 song: harmonic_x_ray
- [x] 9 tests for chord reduction, skeleton mapping, complexity scoring

## v69.0 Roadmap — Musical Dice Game (Musikalisches Wurfelspiel)

Mozart's 1787 algorithm — the first generative music, 230 years before AI.

- [x] `dice_game(seed, bars)` — 2d6 per bar, index into Mozart's 11x16 measure table
- [x] `classical_minuet(key, octave, seed)` — 16-bar minuet in 3/4, 3 notes per bar from scale
- [x] Mozart's original table embedded as `_MOZART_MINUET_TABLE`
- [x] 1 song: mozart_dice
- [x] 11 tests for bar count, determinism, key transposition, table range

## v70.0 Roadmap — Microtuning & Just Intonation

Pure intervals, cent deviations, and quarter-tones.

- [x] `just_ratio(semitones)` — pure harmonic ratio (3/2 for P5, 5/4 for M3, etc)
- [x] `cents_from_et(semitones)` — how many cents a just interval deviates from equal temperament
- [x] `detune_to_just(notes, key)` — cent offsets per note for just intonation tuning
- [x] `quarter_tone(note, direction)` — half-semitone pitch (50 cents up/down) for maqam/makam
- [x] Complete `_JUST_RATIOS` table for all 13 intervals (unison through octave)
- [x] 1 song: just_intonation
- [x] 12 tests for ratios, cent deviation, detuning, quarter tones

## v71.0 Roadmap — Texture Density Control

Measure, thin, and thicken musical texture on demand.

- [x] `texture_density(notes, window_beats)` — sliding-window notes-per-beat measurement
- [x] `thin_texture(notes, target_density, seed)` — randomly convert sounding notes to rests (preserves first/last)
- [x] `thicken_texture(notes, scale, key, target_density, seed)` — insert scale-tone passing notes
- [x] 9 tests for density measurement, thinning, thickening

## v72.0 Roadmap — Chord Voicing Constraints

Constraint-satisfaction voicing solver with smooth voice leading.

- [x] `optimal_voicing(root, shape, voices, max_span, prefer_close, octave)` — find best voicing under span/position constraints
- [x] `smooth_voicings(progression, voices, max_span, octave)` — voice-led sequence minimizing movement between chords
- [x] 1 song: constrained_voicings
- [x] 8 tests for voice count, empty input, single chord, progression length

## v73.0 Roadmap — Rhythm Quantization & Grid Snap

Fix sloppy timing, add swing, or make robots sound human.

- [x] `quantize_rhythm(notes, grid)` — snap durations to nearest grid multiple (0.25 = 16ths, 0.5 = 8ths)
- [x] `swing_quantize(notes, grid, swing_amount)` — even beats on grid, odd beats late by swing ratio (0.66 = triplet)
- [x] `humanize_timing(notes, amount, seed)` — add random deviations to make quantized music breathe
- [x] 11 tests for snapping, swing alternation, humanize determinism

## v74.0 Roadmap — Bass Line Intelligence

Genre-specific bass generators that understand harmonic rhythm.

- [x] `bass_line_jazz(progression, octave, seed)` — root on 1, chord tones on 2-3, chromatic approach to next root on 4
- [x] `bass_line_funk(progression, octave, seed)` — root on the one, syncopated ghost notes, octave pops, rests (the space IS the funk)
- [x] `bass_line_latin(progression, octave, seed)` — tumbao pattern with anticipation: rest-root-rest-fifth-rest-root-fifth-next_root
- [x] 2 songs: jazz_walking, funk_pocket
- [x] 11 tests for note counts, root placement, rests, anticipation

## v75.0 Roadmap — Melody Harmonization

Auto-generate harmony voices from a single melody line.

- [x] `harmonize_melody(melody, key, style, scale_name)` — three styles:
  - `thirds`: parallel diatonic thirds above (pop/rock)
  - `sixths`: parallel diatonic thirds below = sixths above (country)
  - `chorale`: thirds above + sixths below (3 voices total)
- [x] 1 song: harmonized_thirds
- [x] 8 tests for voice counts, pitch preservation, rest passthrough, key/scale variants

## v76.0 Roadmap — Practice Room Tools

Metronome, backing tracks, and tempo training — the practice room in code.

- [x] `click_track(bpm, bars, beats_per_bar, subdivisions)` — accented beat 1, configurable subdivisions (2=8ths, 4=16ths)
- [x] `backing_track(progression, key, style, seed)` — full rhythm section: bass + chords + kick + snare + hat. Styles: rock, jazz, funk, latin
- [x] `tempo_trainer(start_bpm, end_bpm, bars_per_step, increment)` — progressive tempo plan with click tracks per section
- [x] 2 songs: practice_session, rock_backing
- [x] 14 tests for click count, accents, subdivisions, backing parts, tempo sections

## v77.0 Roadmap — Song Statistics Dashboard

Bird's-eye view of a corpus of progressions.

- [x] `corpus_stats(progressions)` — total chords, unique roots/shapes, avg length, most common root/shape, full count dicts
- [x] `key_distribution(progressions)` — estimated key per progression, frequency-sorted counts
- [x] `tempo_distribution(bpms, bucket_size)` — BPM histogram with configurable bucket width
- [x] 9 tests for stats accuracy, empty corpus, distribution bucketing

## v78.0 Roadmap — Melodic Pattern Database

20 built-in licks/riffs indexed by genre and difficulty.

- [x] `_PATTERN_DB` — 20 named patterns across 6 genres: jazz (5), blues (4), rock (3), latin (2), classical (4), funk (2). Each with interval list, genre tag, difficulty 1-4
- [x] `list_patterns(genre, max_difficulty)` — filtered, sorted pattern name list
- [x] `get_pattern(name, key, octave, duration)` — retrieve and transpose to any key
- [x] `chain_patterns(names, key, octave, duration)` — link patterns with midpoint passing-tone connectors
- [x] 1 song: pattern_chain
- [x] 12 tests for listing, filtering, transposition, chaining, unknown pattern error

## v79.0 Roadmap — Dynamic Range Processing

Musical dynamics as first-class velocity transforms.

- [x] `sforzando(notes, position, accent_vel)` — sudden accent at a specific note position
- [x] `dynamics_map(notes)` — extract velocity curve (0 for rests)
- [x] theory.py `crescendo`/`decrescendo` — linear velocity interpolation (engine versions also exist)
- [x] 1 song: dynamic_arc
- [x] 7 tests for accent, out-of-bounds, rest skip, velocity extraction

## v80.0 Roadmap — Chord Progression Generator

One-function song starter with genre templates.

- [x] `generate_progression(key, length, genre, seed)` — 4 genres: pop (3 templates), jazz (3), classical (3), blues (12-bar)
- [x] `extend_progression(existing, bars, key, seed)` — add diatonic chords biased toward common functions (I, IV, V, vi, ii)
- [x] `_GENRE_TEMPLATES` with 10 template progressions across 4 genres
- [x] 1 song: generated_jazz
- [x] 10 tests for genre output, blues 12-bar, determinism, key transposition, extension

## v81.0 Roadmap — Tempo Curve Rendering

BPM as a continuous function — expressive timing through duration manipulation.

- [x] `ritardando(notes, start_bpm, end_bpm)` — gradual slowdown by stretching durations proportional to BPM ratio
- [x] `accelerando(notes, start_bpm, end_bpm)` — gradual speedup (same function, reversed args)
- [x] `rubato(notes, amount, seed)` — sinusoidal push-pull with random perturbation (±amount%, Chopin-style)
- [x] 1 song: rubato_nocturne
- [x] 12 tests for duration increase/decrease, first-note preservation, determinism, rest passthrough

## v82.0 Roadmap — Comping Pattern Library

Five comping styles for rhythm section accompaniment.

- [x] `comp_pattern(progression, style, octave, seed)` — 5 styles:
  - `rock`: power chord 8th notes on every beat
  - `swing`: Freddie Green quarter-note chunks (2 & 4 accented)
  - `funk`: muted 16th-note chops with random gaps
  - `bossa`: syncopated shell voicings (anticipate beat 3)
  - `ballad`: arpeggiated chords, one note per chord tone
- [x] 1 song: bossa_comp
- [x] 7 tests for all styles, multi-chord progressions, determinism

## v83.0 Roadmap — Note Duration Algebra

Durations as composable math — dot, tie, split.

- [x] `dotted(note)` — 1.5x duration (dotted quarter = 1.5 beats)
- [x] `double_dotted(note)` — 1.75x duration (rare but elegant)
- [x] `tied(note_a, note_b)` — merge two same-pitch notes into one (ValueError on mismatch)
- [x] `split_note(note, divisions)` — divide into N equal parts
- [x] 1 song: palm_mute_riff (uses dotted + split_note)
- [x] 13 tests for dotting, tying, splitting, rest handling, pitch mismatch

## v84.0 Roadmap — Instrument Technique Simulation

Simulate what real players do beyond "play the notes."

- [x] `hammer_on(note_a, note_b)` — second note at 60% velocity (no pick attack)
- [x] `pull_off(note_a, note_b)` — same profile as hammer-on (reverse direction)
- [x] `slide(note_a, note_b, steps)` — chromatic glissando with decaying velocity
- [x] `palm_mute(notes, decay_factor)` — shorten to 30% duration, fill with rests (metal chunk)
- [x] 1 song: guitar_techniques
- [x] 13 tests for velocity reduction, intermediates, duration preservation, rest handling

## v85.0 Roadmap — Song Comparison Report

Structured diff between two chord progressions.

- [x] `compare_progressions(prog_a, prog_b, key)` — shared chords, unique to each,
      key estimates, same_key flag, complexity scores + delta, root overlap ratio
- [x] 6 tests for identical, different, partial overlap, complexity, root overlap, empty

## v86.0 Roadmap — Chord Spelling & Enharmonic Intelligence

Context-aware note spelling — Db vs C# depends on the key.

- [x] `enharmonic_equivalent(note)` — C# ↔ Db, F# ↔ Gb, etc. (19-entry map)
- [x] `key_signature_accidentals(key)` — return sharps/flats for all 12 major keys
- [x] `respell_note(note, key)` — pick the spelling that fits: C# in A major, Db in Ab major
- [x] `_KEY_SIGNATURES` dict: all 12 major keys with correct accidental lists
- [x] 11 tests for equivalents, key signatures, context-aware respelling

## v87.0 Roadmap — Song Builder DSL

Write songs in a mini-notation language — less Python boilerplate, more music.

- [x] `parse_chord_line(text)` — `| Cmaj7 | Am7 | Dm7 | G7 |` → chord tuples
- [x] `parse_melody_line(text)` — `C5 D5 E5 - F5` → Notes (- = rest, optional octave)
- [x] `song_from_dsl(text, bpm)` — full DSL parser: `[section]` markers, `chords:` and `melody:` lines
- [x] Supports: sharps/flats in roots, all standard chord suffixes, default octave
- [x] 1 song: dsl_pop_song
- [x] 16 tests for chord parsing, melody parsing, sections, sharp/flat, empty input

## v88.0 Roadmap — Remix Engine

Transform note lists: transpose, double/half time.

- [x] `change_key(notes, from_key, to_key)` — transpose by semitone delta, preserves intervals
- [x] `double_time(notes)` — halve all durations (plays 2x faster)
- [x] `half_time(notes)` — double all durations (plays 2x slower, the breakdown)
- [x] 9 tests for transposition, identity, rest passthrough, duration math

## v89.0 Roadmap — Harmonic Voice Independence

Measure how independently multiple voices move — the Bach score.

- [x] `similar_motion_ratio(voice_a, voice_b)` — fraction of movements in parallel (0.0–1.0)
- [x] `contrary_motion_ratio(voice_a, voice_b)` — fraction in opposite directions (Bach maximized this)
- [x] `voice_independence_score(voices)` — 0–100 rating across all voice pairs (130% × avg contrary, capped at 100)
- [x] 8 tests for parallel detection, contrary detection, single voice, score range

## v90.0 Roadmap — Music Theory Quiz Generator

Generate and grade theory quizzes.

- [x] `quiz_intervals(count, seed)` — note pairs with interval name answers (P1–M7)
- [x] `quiz_chords(count, seed)` — chord spellings with root+quality answers (5 types)
- [x] `grade_quiz(answers, correct)` — score, total, percentage, wrong_indices
- [x] 9 tests for count, structure, determinism, grading (perfect/partial/empty)

## v91.0 Roadmap — Arrangement Density Planner

Plan which instruments play in which sections.

- [x] `density_plan(sections, instruments, pattern)` — 4 patterns: build (sparse→full), strip (full→sparse), wave (sinusoidal), full (everyone always)
- [x] `orchestration_curve(plan)` — extract instrument count per section as int list
- [x] 6 tests for all patterns, min-1-instrument guarantee, curve extraction

## v92.0 Roadmap — Chord Progression Probability Matrix

Markov model of chord transitions — learned from a corpus, generates by random walk.

- [x] `build_transition_matrix(progressions)` — count transitions, normalize to probabilities
- [x] `most_likely_next(current, matrix)` — single most probable next chord
- [x] `generate_from_matrix(matrix, length, start, seed)` — stochastic walk with weighted random choice
- [x] 9 tests for matrix structure, probability sums, determinism, dead-end recovery

## v93.0 Roadmap — Musical Form Analysis Report

One-function markdown analysis — the theory professor's blackboard, automated.

- [x] `analysis_report(progression, key, bpm, title)` — full markdown report:
      form label, key, tempo, length, complexity score, cadence list, functional
      distribution (T/S/D/chromatic counts), tension curve (avg + peak + values)
- [x] 8 tests for string output, title/key/form/complexity/tension/cadence presence

## v94.0 Roadmap — Interactive Scale Explorer

Real-time scale suggestion from notes played so far.

- [x] `suggest_scale(notes_so_far, key)` — rank all 44 scales by overlap/outside penalty, 0.0–1.0
- [x] `available_notes(key, scale_name)` — all pitches in the scale, in order
- [x] `avoid_notes(key, scale_name)` — all 12-tone pitches NOT in the scale (complement)
- [x] 9 tests for ranking, major triad finds major, sorted output, complement completeness

## v95.0 Roadmap — Chord Voicing Database

30+ pre-built voicings across 9 chord shapes — instant lookup.

- [x] `_VOICING_DB` — 30+ voicings: maj(4), min(4), dom7(4), maj7(4), min7(4), dim(2), aug(2), sus4(2), sus2(2)
- [x] `lookup_voicing(root, shape, position, octave, duration)` — retrieve by index (wraps around)
- [x] `random_voicing(root, shape, octave, duration, seed)` — pick randomly for variety
- [x] 8 tests for positions, dom7, duration, wrap, determinism, variety

## v96.0 Roadmap — Musical Memory Game

Simon-says with scale tones — growing sequences, playback verification.

- [x] `memory_game(length, key, scale_name, octave, duration, seed)` — returns N rounds, each growing by 1 note
- [x] `verify_playback(original, attempt)` — correct count, total, accuracy%, wrong positions (handles short attempts)
- [x] 8 tests for round count, growing length, determinism, scale membership, perfect/wrong/partial/short playback

## v97.0 Roadmap — Harmonic Field Map

All diatonic chords + functions + resolution paths for any key.

- [x] `harmonic_field(key, mode)` — 7 chords with degree, Roman numeral, root, shape, function (T/S/D)
- [x] `chord_relationships(key)` — resolution map: V→[I,vi], ii→[V,viio], etc
- [x] Supports major and minor modes
- [x] 9 tests for field size, tonic/dominant, minor mode, resolution targets

## v98.0 Roadmap — Phrase Boundary Detection

Find where musical phrases breathe.

- [x] `detect_phrases(notes, min_gap)` — split by rest gaps ≥ min_gap, returns {start, end, length}
- [x] `phrase_lengths(notes, min_gap)` — just the length integers
- [x] 6 tests for single/multiple phrases, empty, positions, lengths

## v99.0 Roadmap — Song Template Engine

Slot-based composition: define structure, fill sections, render.

- [x] `SongTemplate(form_name)` — initialize from song_form ("pop", "aaba", "blues", etc)
- [x] `template.fill(section, chords, melody)` — fill a named section slot (chainable)
- [x] `template.render()` — flatten to {chords, melody, form} lists
- [x] `template.randomize(key, seed)` — auto-fill empty slots with generate_progression + generate_scale_melody
- [x] 7 tests for forms, fill/render, melody, empty, randomize, chaining, determinism

## v100.0 Roadmap — Centennial Release

THE CENTENNIAL. v39 → v100 in one development arc.

- [x] Milestone song: `centennial.py` using 25+ theory functions in 7 sections:
      jazz reharmonization, generated melody with harmony, Andalusian + Neapolitan + Picardy,
      motif development (augment/diminish/dotted/split/approach), chord tone targeting over blues,
      grooved additive rhythm, drone ending. Analysis report generated inline.
- [x] Integration mega-test: `test_centennial.py` — 37 assertions across 37 numbered subsystems:
      generation, analysis, tension, cadences, reharmonization, complexity, bass lines,
      comping, melody, harmony, dynamics, motif development, targeting, groove, rhythm,
      drone, chromatic harmony, Roman numerals, DSL parsing, tone rows, interval vectors,
      scale atlas, scale suggestion, pattern database, voicing lookup, memory game,
      harmonic field, phrase detection, section detection, song templates, transition matrix,
      corpus stats, quizzes, ear training, key transposition, interval classification, reports
- [x] All 323 songs import without error (smoke test passes)
- [x] 2103 tests total, all passing, lint clean

## v101.0 Roadmap — Corpus Learning

Train a musical style from the 323-song corpus — then generate in that style.

- [x] `train_style_from_corpus(progressions)` — extract: transition matrix, root/shape frequency,
      avg length, key distribution, corpus size. Everything needed for style-specific generation.
- [x] `continue_in_style(style, start, length, seed)` — generate via the learned transition matrix
- [x] 4 tests for style dict structure, generation, determinism

## v102.0 Roadmap — Note Probability

Pitch-class statistics and melodic Markov chains at the note level.

- [x] `note_probability(notes)` — probability distribution of pitch classes (frequency-sorted)
- [x] `next_note_distribution(notes, current)` — first-order Markov: what follows this pitch?
- [x] 7 tests for distribution, empty, rests, sum-to-1, unknown note

## v103.0 Roadmap — Chord Quality Morphing

Smooth transitions between chords by gradually moving pitch classes.

- [x] `morph_chord(from_chord, to_chord, steps, octave, duration)` — linear interpolation
      in pitch-class space (shortest path per voice), returns intermediate voicings
- [x] `chord_interpolation(progression, steps_between, octave, duration)` — insert morphing
      intermediates between every chord pair in a progression
- [x] 7 tests for step count, source/target preservation, single chord, interpolation

## v104.0 Roadmap — Pitch Set Operations

Set theory on pitch classes — union, intersection, complement, transposition.

- [x] `pc_set(pitches)` — convert note names to integer pitch-class set
- [x] `pc_union(set_a, set_b)` — union of two pitch collections
- [x] `pc_intersection(set_a, set_b)` — common pitches
- [x] `pc_complement(pitches)` — all 12 chromatic pitches NOT in the set
- [x] `transpose_set(pitches, semitones)` — shift all pitch classes
- [x] 11 tests for union, intersection, complement, transpose, duplicates, wrapping

## v105.0 Roadmap — Rhythmic Density Analysis

Measure note density over time and compare halves.

- [x] `density_profile(notes, resolution)` — binned note count per beat
- [x] `density_contrast(notes, split_at)` — second-half/first-half density ratio (>1 = builds, <1 = winds down)
- [x] 8 tests for profile shape, rests, contrast direction, empty input

## v106.0 Roadmap — Harmonic Ambiguity Score

How clearly is a progression in one key? Measure the gap.

- [x] `ambiguity_score(progression)` — 0.0 (clear key) to 1.0 (no key fits well). Uses root-frequency
      scoring with tonic bonus, then gap between best and second-best key candidate
- [x] `key_certainty(progression)` — {key, confidence (1-ambiguity), ambiguity}
- [x] 8 tests for diatonic/chromatic comparison, range, empty, confidence+ambiguity sum

## v107.0 Roadmap — Chord Symbol Formatter

Standard chord symbol rendering — Cmaj7, Dm7b5, G7, etc.

- [x] `format_chord(root, shape)` — render (root, shape) as standard chord symbol
- [x] `format_progression(progression, separator)` — render full progression as chart line
- [x] `_SHAPE_SYMBOLS` — 15 shape-to-symbol mappings (maj→"", min→"m", dom7→"7", etc)
- [x] 12 tests for all shapes, sharp roots, progression formatting

## v108.0 Roadmap — Voice Range Optimizer

Auto-transpose to fit singer/instrument ranges.

- [x] `fit_to_range(notes, low, high)` — octave-shift each note to fit [low, high] range
- [x] `auto_octave(notes, target_octave)` — shift entire melody to center on target octave
- [x] 9 tests for in-range, too-high, too-low, rest passthrough, pitch preservation

## v109.0 Roadmap — Interval Sequence Analysis

Extract and analyze melodic interval patterns.

- [x] `interval_sequence(notes)` — signed semitone intervals between consecutive notes
- [x] `common_intervals(notes, top_n)` — most frequent intervals, sorted by count
- [x] 8 tests for ascending, descending, rests, octave jumps, frequency ranking

## v110.0 Roadmap — Melodic Contour Matching

Compare melodies by shape, not pitch — transposition-invariant similarity.

- [x] `contour_string(notes)` — encode melody as U/D/R string (up/down/repeat)
- [x] `contour_match(melody_a, melody_b)` — contour similarity score (0.0-1.0)
- [x] 9 tests for ascending, descending, mixed, transposed, opposite, empty

## v111.0 Roadmap — Rhythm Pattern Matching

Compare melodies by when notes happen, not what they are.

- [x] `rhythm_string(notes, grid)` — encode rhythm as X/. string (note/rest per grid slot)
- [x] `rhythm_match(melody_a, melody_b, grid)` — rhythmic similarity score (0.0-1.0)
- [x] 8 tests for all-notes, rests, longer durations, pitch-independent, empty

## v112.0 Roadmap — Progression Complexity Curve

Track harmonic complexity over time with sliding windows.

- [x] `complexity_curve(progression, key, window)` — sliding-window complexity score per chord position
- [x] `complexity_contrast(progression, key)` — second-half/first-half complexity ratio
- [x] 7 tests for length, range, chromatic vs diatonic, single chord, steady

## v113.0 Roadmap — Chord Inversion Analyzer

Detect which inversion a voicing is in.

- [x] `detect_inversion(notes, root, shape)` — returns 0 (root), 1 (1st), 2 (2nd), 3 (3rd) by matching bass note to chord tones
- [x] `inversion_label(inversion)` — human-readable: "root position", "1st inversion", etc
- [x] 9 tests for all positions, dom7 3rd inversion, empty

## v114.0 Roadmap — Note Name Utilities

MIDI ↔ note name ↔ frequency conversions.

- [x] `note_to_midi(pitch, octave)` — C4 = 60, A4 = 69
- [x] `midi_to_note(midi)` — 60 → ("C", 4), round-trip verified
- [x] `note_to_freq(pitch, octave, a4)` — equal temperament, configurable A4 (default 440 Hz)
- [x] 10 tests for middle C, A4, C0, round-trip, frequency accuracy, custom tuning

## v115.0 Roadmap — Progression Similarity

Compare and search progressions by harmonic fingerprint.

- [x] `progression_similarity(prog_a, prog_b)` — combined pitch-class + shape Jaccard similarity (0.0-1.0)
- [x] `find_similar_progressions(target, corpus, top_n)` — rank a corpus by similarity to a target, returns (index, score) pairs
- [x] 7 tests for identical, different, empty, range, exact match finding, top_n, sorted output

## v116.0 Roadmap — Scale Degree Naming

Name scale degrees relative to any key.

- [x] `scale_degree(pitch, key)` — interval in semitones from key root (0-11)
- [x] `scale_degree_name(pitch, key)` — human-readable: "5", "b3 (minor 3rd)", "#4/b5 (tritone)"
- [x] 7 tests

## v117.0 Roadmap — Chord Tone Filter

Identify and filter chord tones in a melody.

- [x] `chord_tones(root, shape)` — list pitch names in the chord
- [x] `is_chord_tone(pitch, root, shape)` — boolean: is this pitch in the chord?
- [x] `filter_chord_tones(notes, root, shape)` — keep chord tones, replace non-chord-tones with rests
- [x] 8 tests

## v118.0 Roadmap — Melodic Range Stats

Analyze the pitch range and center of a melody.

- [x] `melodic_range(notes)` — {lowest, highest, range_semitones, range_octaves, avg_pitch}
- [x] `pitch_center(notes)` — (pitch_name, octave) of the average pitch
- [x] 8 tests

## v125.0 Roadmap — Chord Symbol Parser

Parse real-world chord symbols like Cmaj7, Dm7b5, G7#9.

- [x] `parse_chord_symbol(symbol)` — "Cmaj7" → ("C","maj7"), handles sharps/flats/all suffixes
- [x] `parse_chord_symbols(text)` — space-separated batch: "Cmaj7 Dm7 G7" → list of tuples
- [x] 15 tests

## v126.0 Roadmap — Melody Smoothing

Fill large leaps with passing tones for smoother melodies.

- [x] `smooth_melody(notes, max_leap)` — inserts one chromatic midpoint for leaps > max_leap
- [x] `fill_leaps(notes, threshold)` — replaces large leaps with full chromatic runs
- [x] 8 tests

## v127.0 Roadmap — Harmonic Rhythm Quantizer

Control chord density — expand or contract progressions.

- [x] `chords_per_bar(progression, total_bars)` — average chord changes per bar
- [x] `quantize_harmonic_rhythm(progression, target)` — contract (sample) or expand (repeat) to target density
- [x] 8 tests

## v128-v130 Roadmap (just shipped)

- [x] `octave_distribution`, `register_spread` — notes per octave, distinct octave count
- [x] `reverse_progression`, `rotate_progression` — retrograde + rotation of chord progressions
- [x] `melody_summary` — one-call comprehensive diagnostic (11 metrics: counts, duration, range, pitch center, rest/leap/repetition ratios)

## Completed roadmap items (archived)

Items below were planned in earlier sessions and have since shipped.

### Tier 1: Infrastructure - DONE
- [x] **Song Builder DSL v2** - `parse_song_dsl()` with BPM, time sig, instruments, bars (v137)
- [x] **Genre Classifier** - `classify_genre()` with 10 genre profiles, weighted scoring (v131)
- [ ] **MusicXML Export** - `to_musicxml(song)` for MuseScore/Finale/Sibelius

### Tier 2: Composition Intelligence - DONE
- [x] **Full Song Generator** - `generate_full_song()` with 7 genres, multi-track (v131)
- [x] **Countermelody Generator** - `generate_countermelody()` with 3 styles (v132)
- [x] **Arrangement Engine** - `auto_arrange()` with 4 style presets (v131)

### Tier 3: Analysis & Education - PARTIAL
- [x] **Comprehensive Song Analyzer** - `full_analysis()` multi-page report (v136)
- [ ] **Interactive Theory Course** - structured lesson sequence

### Tier 4: External Integration
- [ ] **Web Playground (Pyodide)** - theory module in the browser
- [ ] **MIDI Round-Trip v2** - import MIDI to Song

### Tier 5: Quality & Maintenance - PARTIAL
- [x] **theory.py Refactor** - split into 7 submodules under theory/ (v131)
- [ ] **Test Organization** - group 157+ test files by domain
- [ ] **Pre-existing LSP Errors** - Pyright type stubs for numpy

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

- [x] `measure_lufs()` — ITU-R BS.1770-4 simplified K-weighted loudness metering
- [x] `normalize_lufs(audio, sr, target=-14.0)` — LUFS loudness targeting for streaming
- [x] `dither(audio, bit_depth=16)` — TPDF dithering for 16/24-bit export
- [x] `true_peak_limit(audio, sr, ceiling_db=-1.0)` — 4× oversampled ISP limiter
- [x] `stereo_analysis(audio)` — correlation, width, balance, mid/side RMS
- [x] `master_audio()` — full chain: normalize → limit → dither
- [ ] `code-music master song.wav --target-lufs=-14 --format=flac` CLI (future)
- [ ] Batch mastering: `make master` processes all songs (future)
- [ ] Metadata embedding (ID3 tags for MP3, Vorbis comments for FLAC/OGG) (future)

## v11.0 Roadmap — Automation & Modulation Matrix

Every parameter should be automatable. Move from static values to envelopes
over time — the difference between a sketch and a finished production.

### Phase 1: Parameter Automation
- [x] `Automation(keyframes, mode)` — time-value curves with linear/exponential/smoothstep
- [x] `value_at(beat)` — interpolated value at any beat position
- [x] `sample(bpm, sr, duration_beats)` — per-sample array for rendering
- [x] Linear, exponential, and smoothstep interpolation modes
- [ ] `Track.automate("volume", auto)` — per-track integration (future)
- [ ] `EffectsChain.automate(step_idx, "wet", auto)` — per-effect param (future)

### Phase 2: Modulation Matrix
- [x] `ModMatrix` — route sources to destinations with amount + rate
- [x] Sources: lfo1, lfo2, random (smoothed), envelope (attack-release)
- [x] `generate_mod_signal(source, n, sr, rate)` — per-sample modulation signal
- [x] Chaining: `mm.connect(...).connect(...)`
- [x] `routes` property and `__repr__` for inspection
- [ ] Direct integration with Synth render pipeline (future)

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
- [x] `song_overlay(base, other, at_beat)` — drop tracks at beat offset, `_2` suffix on collision
- [x] `song_append(first, second)` — concatenate end-to-end, same-name tracks merge
- [x] `song_extract(song, track_names)` — pull specific tracks + effects into new Song
- [x] Conflict resolution: track name collisions get `_2` suffix

### Phase 2: Stem Import/Export
- [ ] `Song.import_stems(directory)` — load a folder of WAVs as SampleTracks
- [ ] `Song.export_stems()` improvements: include effects, master chain per-stem option
- [ ] Stem naming convention: `{song_title}_{track_name}.wav`
- [ ] Round-trip: export stems → reimport → identical render

### Phase 3: Song Diffing
- [x] `song_diff(a, b)` — structural diff (added/removed/modified tracks, bpm, title, volume, pan)
- [x] Machine-readable: returns list of `Change` objects (change_type, track_name, detail)
- [x] `song_patch(base, changes)` — apply diff to modify a song (add/remove tracks, modify props)
- [ ] Human-readable formatting: "Track 'lead' added 4 notes at beat 8" (future)

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
- [x] `chord_scale(root, shape)` — compatible scales for any chord (14 scale types)
- [x] `available_tensions(root, shape)` — 9th, 11th, 13th that don't clash
- [ ] `voice_lead(prog, voice_count=4)` improvements: SATB rules, parallel 5th avoidance (future)
- [ ] `analyze_harmony(song)` — full roman numeral + function analysis (future)

### Phase 2: Intelligent Generation
- [ ] `generate_song()` improvements: key changes, modulation, bridge sections
- [x] `generate_bass_line(chords, style)` — root, root_fifth, walking, syncopated (4 styles)
- [x] `generate_drums(genre, bars)` — rock, jazz, electronic, latin, hiphop (5 genres)
- [ ] `generate_melody(chords, contour)` — melody that follows harmonic rhythm (future)
- [ ] Counterpoint generator: `generate_counterpoint(melody, species=1)` (future)

### Phase 3: Analysis Dashboard
- [ ] `Song.analyze()` — returns full report: key, tempo, chord progression, density, dynamics
- [ ] Harmonic rhythm visualization (chord changes over time)
- [ ] Melodic contour analysis: step/skip/leap statistics
- [ ] Tension/release curve: consonance score over time

### Phase 4: Theory Examples + Tests
- [ ] `examples/13_theory.py` — chord-scale theory, voice leading, analysis
- [ ] 5 songs generated with advanced theory features (165 total)
- [ ] Tag v14.0.0 release

## v15.0 Roadmap — Spatial Audio & Immersive Sound

Move beyond stereo. Binaural, ambisonics, and 3D positioning for
headphone and multi-speaker experiences.

### Phase 1: Binaural Rendering
- [ ] `SpatialPanner(azimuth, elevation, distance)` — HRTF-based binaural panning
- [ ] Built-in KEMAR HRTF dataset (compact, numpy-only)
- [ ] `Track.spatial(azimuth=45, elevation=0, distance=2.0)` — per-track positioning
- [ ] Head tracking simulation: `Track.orbit(rate, radius)` — sound orbits the listener

### Phase 2: Ambisonics
- [ ] First-order ambisonics (B-format: W, X, Y, Z channels)
- [ ] Encode stereo or mono tracks to B-format
- [ ] Decode B-format to binaural, stereo, quad, or 5.1
- [ ] Ambisonic reverb: early reflections from encoded room geometry

### Phase 3: Distance & Room Modeling
- [ ] Distance attenuation (inverse-square, configurable rolloff)
- [ ] Simple room model: dimensions → early reflections + late tail
- [ ] Doppler effect for moving sources
- [ ] Air absorption filter (high-frequency rolloff with distance)

### Phase 4: Tests + docs + songs
- [ ] Tests for binaural, ambisonics, distance modeling
- [ ] `examples/14_spatial.py` — 3D audio positioning tutorial
- [ ] 5 spatial audio songs (170 total)
- [ ] Tag v15.0.0 release

## v16.0 Roadmap — Plugin Ecosystem & Extension API

Let the community extend code-music without forking. Clean plugin interface
for instruments, effects, generators, and exporters.

### Phase 1: Plugin Interface
- [ ] `@register_instrument` decorator — third-party instruments auto-discovered
- [ ] `@register_effect` decorator — third-party effects
- [ ] `@register_generator` decorator — third-party song generators
- [ ] Entry-point based discovery (`[project.entry-points."code_music.plugins"]`)

### Phase 2: Instrument Packs
- [ ] `code-music install-pack <name>` CLI — pip install + register
- [ ] Pack format: Python package with `instruments/`, `effects/`, `generators/`
- [ ] Built-in pack: `code-music-vintage` (FM pianos, analog strings, tape effects)

### Phase 3: Community Infrastructure
- [ ] `code-music share <song.py>` — upload song + custom instruments as a gist
- [ ] `code-music import <url>` — download and run shared songs
- [ ] Online preset browser: browse community SoundDesigner presets
- [ ] `make gallery-community` — auto-build gallery from shared presets

### Phase 4: Tests + docs
- [ ] Plugin API tests, pack install tests, share/import tests
- [ ] `examples/15_plugins.py` — write and register a custom plugin
- [ ] 5 songs using community-style plugins (175 total)
- [ ] Tag v16.0.0 release

## v17.0 Roadmap — Visual Score & Waveform Rendering

Generate visual representations of songs — piano rolls, waveform plots,
spectrograms, and notation directly from Song objects.

### Phase 1: Piano Roll
- [ ] `Song.piano_roll()` → PIL Image or matplotlib figure
- [ ] Color-coded tracks, time axis in beats, pitch axis in semitones
- [ ] `code-music songs/my_track.py --piano-roll -o roll.png` CLI
- [ ] SVG output for web embedding

### Phase 2: Waveform Visualization
- [ ] `Song.waveform()` → per-track waveform plots
- [ ] Envelope overlay showing ADSR shape
- [ ] Master waveform with peak/RMS markers
- [ ] `code-music songs/my_track.py --waveform -o wave.png`

### Phase 3: Spectrogram
- [ ] `Song.spectrogram()` → STFT-based frequency × time plot
- [ ] Log-frequency axis (musical), linear-frequency option
- [ ] Per-track spectrograms for mix analysis
- [ ] Mel spectrogram option for perceptual representation

### Phase 4: Integrated Web Viewer
- [ ] Extend playground with live waveform/piano-roll visualization
- [ ] `make visualize-all` — batch render visual scores for all songs
- [ ] 5 songs with accompanying visual scores (180 total)
- [ ] Tag v17.0.0 release

## v18.0 Roadmap — AI-Assisted Composition

Use LLMs and ML models to assist composition — not replace it.
The human stays in control; AI suggests, fills gaps, and extends ideas.

### Phase 1: Melody Continuation
- [ ] `continue_melody(notes, bars=4)` — extend a melodic fragment using Markov chains
- [ ] Style-aware: learns transition probabilities from existing songs in the library
- [ ] `continue_melody(notes, style="jazz")` — style-specific models from songs/ corpus
- [ ] Respects current key and scale (uses detect_key() internally)

### Phase 2: Accompaniment Generation
- [ ] `auto_accompany(melody, style)` — generate bass + chords from a melody
- [ ] Voice-leading aware: applies voice_lead() to generated progressions
- [ ] Drum pattern matching: selects appropriate euclidean patterns for genre
- [ ] `Song.fill_tracks(["bass", "drums"])` — auto-fill empty tracks

### Phase 3: Arrangement Suggestions
- [ ] `suggest_arrangement(song)` — returns a Section list based on song structure analysis
- [ ] Detects repetition, suggests intro/verse/chorus/bridge boundaries
- [ ] `Song.auto_arrange()` — applies suggested arrangement in place
- [ ] Build/drop detection for electronic music arrangements

### Phase 4: Tests + docs + songs
- [ ] Tests for melody continuation, accompaniment, arrangement
- [ ] `examples/16_ai_assist.py` — AI-assisted composition tutorial
- [ ] 5 songs composed with AI assistance (185 total)
- [ ] Tag v18.0.0 release

## v19.0 Roadmap — Microtonal & Alternative Tuning

Break free from 12-tone equal temperament. Support any tuning system —
just intonation, quarter-tones, Bohlen-Pierce, historical temperaments,
and user-defined scales.

### Phase 1: Tuning System Core
- [ ] `Tuning` class: define pitch-to-frequency mapping
- [ ] Built-in tunings: 12-TET (default), just intonation, Pythagorean, meantone
- [ ] `Tuning.from_cents(cent_list)` — build from cent values
- [ ] `Tuning.from_ratios(ratio_list)` — build from frequency ratios
- [ ] `Song(tuning=Tuning.just_intonation())` — song-level tuning override

### Phase 2: Microtonal Scales
- [ ] Quarter-tone scales (24-TET)
- [ ] Bohlen-Pierce (13 steps in a tritave)
- [ ] Gamelan slendro/pelog (5/7 unequal steps)
- [ ] `scale("C", "bohlen_pierce", tuning=Tuning.bp13())` — tuning-aware scale()
- [ ] Note names extend: `C4+50c` (50 cents sharp), `D4-25c` (25 cents flat)

### Phase 3: Historical Temperaments
- [ ] Well temperament (Werckmeister III, Kirnberger III)
- [ ] Equal temperament variants (19-TET, 31-TET, 53-TET)
- [ ] A/B comparison: render same melody in two tunings

### Phase 4: Tests + docs + songs
- [ ] `examples/17_microtonal.py` — tuning systems tutorial
- [ ] 5 microtonal songs (190 total)
- [ ] Tag v19.0.0 release

## v20.0 Roadmap — Song Structure Intelligence

Understand and manipulate song structure at a higher level than individual
notes — verses, choruses, builds, drops, transitions.

### Phase 1: Structure Primitives
- [ ] `Verse`, `Chorus`, `Bridge`, `Intro`, `Outro` — named Section subclasses
- [ ] `Song.structure` property: ordered list of structural sections
- [ ] Auto-detect structure from existing songs via repetition analysis
- [ ] `Song.map()` → ASCII art structure visualization

### Phase 2: Transition System
- [ ] `Transition(from_section, to_section, type)` — fill, riser, drop, crossfade
- [ ] Built-in transitions: drum fill, filter sweep, reverse cymbal, silence gap
- [ ] `Song.auto_transition()` — add transitions between all sections
- [ ] `SoundDesigner`-based transition sounds (risers, impacts, sweeps)

### Phase 3: Arrangement Templates
- [ ] `ArrangementTemplate` — predefined structures (AABA, ABAB, verse-chorus-bridge)
- [ ] `Song.apply_template(template)` — restructure song to match template
- [ ] Genre-specific templates: pop, EDM (build-drop), jazz (head-solo-head)
- [ ] `code-music arrange song.py --template edm_drop` CLI

### Phase 4: Tests + docs + songs
- [ ] `examples/18_structure.py` — song structure and arrangement tutorial
- [ ] 5 structurally complex songs (195 total)
- [ ] Tag v20.0.0 release

## v21.0 Roadmap — MIDI I/O & DAW Integration

Full bidirectional MIDI support — import from any DAW, export to any DAW,
real-time MIDI input for live performance.

### Phase 1: MIDI Import Enhancements
- [ ] `import_midi()` improvements: tempo changes, time signatures, CC automation
- [ ] Multi-track import with instrument mapping (GM → code-music presets)
- [ ] Velocity → volume mapping with configurable curves
- [ ] MIDI file analysis: key detection, chord extraction, structure detection

### Phase 2: MIDI Export Enhancements
- [ ] `export_midi()` improvements: CC automation, program changes, tempo maps
- [ ] Per-track MIDI channel assignment
- [ ] Pattern → MIDI conversion: `pattern.to_midi(path)`
- [ ] SoundDesigner params → CC automation (filter cutoff → CC74, etc)

### Phase 3: Real-Time MIDI Input
- [ ] `midi_input(port)` — listen on a MIDI port, convert to Notes in real-time
- [ ] `Song.record_midi(port, duration)` — record MIDI into a Track
- [ ] Quantization: snap recorded notes to grid (1/4, 1/8, 1/16)
- [ ] Live monitoring: play SoundDesigner instruments from MIDI keyboard

### Phase 4: Tests + docs + songs
- [ ] `examples/19_midi.py` — MIDI import/export/record tutorial
- [ ] 5 songs created from MIDI imports (200 total)
- [ ] Tag v21.0.0 release

## v22.0 Roadmap — Performance Optimization & Streaming

Make code-music fast enough for real-time and large-scale batch rendering.

### Phase 1: Rendering Performance
- [ ] NumPy vectorization audit — eliminate remaining Python loops in hot paths
- [ ] Pre-compute SoundDesigner wavetables at registration (not per-note)
- [ ] Parallel track rendering with multiprocessing.Pool
- [ ] Benchmark suite: `make bench` reports render time per song

### Phase 2: Streaming Render
- [ ] `Song.render_stream(chunk_size)` — yield audio chunks (generator)
- [ ] Enables real-time playback of arbitrarily long songs
- [ ] Streaming export: write to WAV while rendering (constant memory)
- [ ] Progress callback for long renders

### Phase 3: Caching
- [ ] `SoundDesigner.render()` LRU cache keyed on (freq, duration, sr)
- [ ] Track-level render cache (invalidated on note/effect changes)
- [ ] `Song.render(cache=True)` — skip unchanged tracks on re-render
- [ ] Cache statistics: `Song.cache_info()` → hit rate, memory usage

### Phase 4: Tests + docs
- [ ] Benchmark tests with regression detection
- [ ] `examples/20_performance.py` — optimization patterns tutorial
- [ ] 5 performance-intensive songs (205 total)
- [ ] Tag v22.0.0 release

## v23.0 Roadmap — Audio Import & Sampling

Load external audio files, slice them, and use them as instruments alongside
synthesized sounds.

### Phase 1: Audio File Loading
- [ ] `load_audio(path)` — load WAV/FLAC/MP3 → float64 array (mono or stereo)
- [ ] Automatic sample rate conversion to match Song.sample_rate
- [ ] `AudioClip` class: start/end markers, loop points, pitch detection
- [ ] `SampleTrack` improvements: trigger AudioClips at note events

### Phase 2: Slicing & Chopping
- [ ] `AudioClip.slice(n)` — split audio into N equal slices
- [ ] `AudioClip.detect_transients()` — find onset points for auto-slicing
- [ ] `AudioClip.slice_at(beats)` — slice at specific beat positions
- [ ] REX-style playback: trigger slices from Pattern or Note sequence

### Phase 3: Pitch Shifting & Time Stretching
- [ ] `AudioClip.pitch_shift(semitones)` — shift pitch without changing duration
- [ ] `AudioClip.time_stretch(ratio)` — change duration without changing pitch
- [ ] Phase vocoder implementation (numpy-only)
- [ ] Granular time stretching (leverages existing granular engine)

### Phase 4: Tests + docs + songs
- [ ] `examples/21_sampling.py` — load, slice, pitch-shift tutorial
- [ ] 5 sample-based songs (210 total)
- [ ] Tag v23.0.0 release

## v24.0 Roadmap — Web Audio Export & Embeddable Player

Make songs playable in the browser without any server or backend. Pure
client-side audio from Python-generated data.

### Phase 1: JSON Song Format
- [ ] `Song.to_json()` — serialize entire song (notes, instruments, effects) to JSON
- [ ] `Song.from_json(data)` — reconstruct from JSON
- [ ] SoundDesigner serialization included (already has to_dict/from_dict)
- [ ] Compact format: ~10KB for a typical 16-bar song

### Phase 2: Web Audio Renderer
- [ ] JavaScript Web Audio API renderer that reads the JSON format
- [ ] Oscillator mapping: code-music instrument names → Web Audio oscillators
- [ ] Effect mapping: reverb → ConvolverNode, delay → DelayNode, filter → BiquadFilterNode
- [ ] SoundDesigner → Web Audio: FM synthesis via OscillatorNode frequency modulation

### Phase 3: Embeddable Player Widget
- [ ] `<code-music-player>` web component (shadow DOM, zero dependencies)
- [ ] Waveform visualization, play/pause, track mute/solo
- [ ] `Song.to_html(path)` — generate standalone HTML file with embedded player
- [ ] GitHub Pages integration: `make web-player` builds playable gallery

### Phase 4: Tests + docs
- [ ] `examples/22_web_export.py` — export to JSON + HTML tutorial
- [ ] Browser-based integration tests (Playwright)
- [ ] 5 songs with web player exports (215 total)
- [ ] Tag v24.0.0 release

## v25.0 Roadmap — Song Versioning & History

Full undo/redo and version history for songs, enabling non-destructive
editing workflows.

### Phase 1: Snapshot System
- [ ] `Song.snapshot()` → immutable copy of current state
- [ ] `Song.history` — ordered list of snapshots with timestamps
- [ ] `Song.undo()` / `Song.redo()` — navigate history
- [ ] Auto-snapshot on every structural change (add_track, extend, etc)

### Phase 2: Named Versions
- [ ] `Song.tag(name)` — name a snapshot (like git tags)
- [ ] `Song.checkout(tag_name)` — restore a named version
- [ ] `Song.compare(tag_a, tag_b)` — diff between two versions
- [ ] Version log: `Song.log()` → list of (timestamp, tag, change_summary)

### Phase 3: Branch & Merge
- [ ] `Song.branch(name)` — fork the song for experimentation
- [ ] `Song.merge(branch_name)` — merge a branch back (uses song_diff internally)
- [ ] Conflict detection: overlapping track modifications flagged
- [ ] `Song.branches` — list all named branches

### Phase 4: Tests + docs
- [ ] `examples/23_versioning.py` — snapshot, undo, branch tutorial
- [ ] 5 songs demonstrating version workflows (220 total)
- [ ] Tag v25.0.0 release

## v26.0 Roadmap — Music Notation Rendering

Generate sheet music directly from Song objects — readable by musicians,
printable as PDF.

### Phase 1: ASCII Tab
- [ ] `Song.to_tab()` — guitar/bass tablature in ASCII
- [ ] `Song.to_lead_sheet()` — chord symbols + melody (ASCII)
- [ ] Time signature awareness (4/4, 3/4, 6/8)
- [ ] Key signature detection (uses detect_key())

### Phase 2: SVG Score
- [ ] `Song.to_svg()` — vector score with proper notation
- [ ] Notes, rests, beams, ties, slurs rendered as SVG paths
- [ ] Multi-staff: treble + bass clef for piano, single staff for melody
- [ ] Dynamic markings from volume automation

### Phase 3: PDF Export
- [ ] `Song.to_pdf(path)` — render SVG to PDF (reportlab or Cairo)
- [ ] Page layout: A4/Letter, title, composer, tempo marking
- [ ] `code-music score songs/my_track.py -o score.pdf` CLI

### Phase 4: Tests + docs
- [ ] `examples/24_notation.py` — generate tab + SVG + PDF
- [ ] 5 songs with notation exports (225 total)
- [ ] Tag v26.0.0 release

## v131.0 — Theory Refactor + Genre Classifier + Song Generator + Arrangement Engine

### theory.py → theory/ package (structural refactor)
- [x] Split 10,706-line `theory.py` into 7 submodules: `_core`, `harmony`, `rhythm`, `melody`, `analysis`, `generation`, `serial`
- [x] `theory/__init__.py` re-exports all 287 public names for backward compat
- [x] All 2338 existing tests pass with zero consumer changes
- [x] Direct submodule imports now work: `from code_music.theory.harmony import chord_scale`

### classify_genre — rule-based genre classifier
- [x] `classify_genre(progression, bpm, swing)` → predicted genre with confidence
- [x] 10 genre profiles: blues, jazz, pop, rock, classical, r&b, latin, ambient, electronic, metal
- [x] 6 features: quality distribution, root motion, progression length, tension profile, BPM, swing
- [x] Returns: genre, confidence (0-1), all genre scores, extracted feature dict
- [x] 16 tests (pop, blues, jazz, ambient, classical, edge cases, BPM/swing influence)

### generate_full_song — one-call complete song generation
- [x] `generate_full_song(genre, key, bpm, sections, seed)` → multi-track Song
- [x] 7 genres: jazz, pop, rock, blues, classical, electronic, ambient
- [x] Generates: chord track, bass line, drum pattern, scale melody per section
- [x] Genre-appropriate: walking bass for jazz, no drums for ambient, 12-bar for blues
- [x] Section-aware dynamics: chorus louder, intro/outro softer
- [x] 11 tests (all genres, custom sections, seed reproducibility, content validation)

### auto_arrange — arrangement engine
- [x] `auto_arrange(progression, key, bpm, style, bars_per_chord, seed)` → arranged Song
- [x] 4 style presets: jazz_combo, rock_band, orchestral, electronic
- [x] Assigns instruments, bass lines, drum patterns, comping, lead melody
- [x] Density-aware orchestration: brass accents follow density curve
- [x] 9 tests (all styles, bars_per_chord, empty/single chord, reproducibility)

**Stats:** 390+ public functions. 2374 tests. 323 songs. 44 scales.

## v132.0 — Countermelody + Style Transfer + Motif Development

### generate_countermelody — intelligent countermelody generation
- [x] `generate_countermelody(melody, progression, key, scale, style, seed)` → Note list
- [x] 3 styles: independent (contrary motion), descant (above, sparser), bass_counter (below, root-heavy)
- [x] Chord tones on strong beats, scale tones on weak beats, register separation
- [x] 13 tests (all styles, multi-chord, rests, minor key, velocity, seed, edge cases)

### restyle — genre style transfer
- [x] `restyle(song, target_genre, key, bpm, seed)` → restyled Song
- [x] 10 genre reharmonization profiles (triads→7ths for jazz, everything→dom7 for blues, etc.)
- [x] Extracts chords from source, reharmonizes, runs auto_arrange with genre instruments/swing
- [x] Key override with transposition, BPM override or genre-default
- [x] 13 tests (all genres, key/bpm override, jazz↔pop round-trip, reharmonization validation)

### develop_motif — motif-based composition
- [x] `develop_motif(motif, techniques, key, repetitions, seed)` → extended passage
- [x] 10 techniques: repeat, sequence, inversion, retrograde, retrograde_inversion, augmentation, diminution, fragmentation, extension, ornamentation
- [x] Default development arc: repeat → sequence → inversion → fragmentation → augmentation → repeat
- [x] 16 tests (all techniques, default arc, seed, empty, single note, chaining)

**Stats:** 393+ public functions. 2416 tests. 323 songs. 44 scales.

## v133.0 — Chord Voicing AI + Cadential Phrase Generator + Tension Narrative

### voice_progression — style-specific chord voicing
- [x] `voice_progression(progression, style, octave, duration)` → list of voicing note-lists
- [x] 5 styles: classical, jazz_rootless, quartal, drop2, shell
- [x] Classical: common-tone retention, smooth bass, step-wise upper voices
- [x] Jazz rootless: alternating A/B Evans voicings for smooth leading
- [x] Shell: 2-note Monk voicings (root + guide tone)
- [x] 13 tests (all styles, smooth movement check, empty/single, invalid style)

### generate_phrase — cadential phrase generator
- [x] `generate_phrase(key, cadence, length, include_melody, seed)` → dict
- [x] 4 cadence types: perfect (V-I), half (→V), deceptive (V-vi), plagal (IV-I)
- [x] Roman numeral templates expanded/contracted to requested length
- [x] Returns: progression, cadence_type, tension_curve, optional melody
- [x] 13 tests (all cadences, melody, key/length variants, seed reproducibility)

### tension_story — natural language tension narrative
- [x] `tension_story(progression, key, bars_per_chord)` → narrative string
- [x] Reads tension_curve + functional_analysis + detect_cadences
- [x] Describes: opening, tension build, climax, cadences, ending, overall character
- [x] Functional label mapping (T→tonic, D→dominant, S→subdominant)
- [x] 13 tests (opening/ending/overall present, empty, high/low tension, cadence mention)

**Stats:** 396+ public functions. 2455 tests. 323 songs. 44 scales.

## v134.0 — Variation Suite + Composition Critique + Modulation Detector

### generate_theme_and_variations — classical variation form
- [x] `generate_theme_and_variations(theme, key, scale, n_variations, bpm, seed)` → Song
- [x] 7 variation techniques: inversion, augmentation, diminution, retrograde, ornamentation, sequence, fragmentation
- [x] Generates or accepts theme, builds I-IV-V-I backing per section
- [x] 8 tests (default, custom theme, cap, zero vars, chord track, seed, key, scale)

### critique — automated theory review
- [x] `critique(progression, melody, key)` → dict with score/grade/issues/strengths/suggestions
- [x] 10 checks: variety, quality variety, cadence, unresolved dominant, tension arc, key consistency, functional balance, melody range, leaps, rests
- [x] Score 0-100, letter grade A/B/C/D/F
- [x] 12 tests (good/bad/empty, melody checks, range, dominant, blues, bounds)

### detect_modulations — key change detection
- [x] `detect_modulations(progression, window)` → list of key region dicts
- [x] Sliding-window detect_key, consecutive region merging, pivot chord ID
- [x] 9 tests (no mod, simple mod, coverage, contiguity, pivot, short, empty, window)

**Stats:** 399+ public functions. 2484 tests. 323 songs. 44 scales.

## v135.0 — Period Builder + Guided Composition + Melodic Similarity

### generate_period — classical period structure
- [x] `generate_period(key, antecedent_cadence, consequent_cadence, phrase_length, seed)` → dict
- [x] Chains generate_phrase: antecedent (half cadence) + consequent (perfect cadence)
- [x] Returns: combined progression, tension curve, optional melody
- [x] 10 tests (default, combined, custom cadences, key, dominant ending)

### compose — natural language to Song
- [x] `compose(prompt, seed)` → Song
- [x] Parses genre (30+ keywords), key (12 notes), BPM (numeric + adjectives), sections
- [x] Genre synonyms: swing/bebop→jazz, edm/techno→electronic, punk→rock, etc.
- [x] Tempo adjectives: fast→160, slow/ballad→72, medium→110
- [x] 10 tests (jazz/rock/ambient, BPM, sections, synonyms, empty prompt)

### melody_similarity + find_similar_melodies — melodic search
- [x] `melody_similarity(a, b, weights)` → 0.0-1.0 score
- [x] 3 features: contour matching, interval matching, rhythm matching
- [x] `find_similar_melodies(query, corpus, top_k, min_score)` → ranked results
- [x] 16 tests (identity, transposition, contour, weights, corpus search, filtering)

**Stats:** 405+ public functions. 2520 tests. 323 songs. 44 scales.

## v136.0 — Comprehensive Song Analyzer

### full_analysis — multi-page markdown analysis report
- [x] `full_analysis(song)` → comprehensive markdown report
- [x] Sections: Overview, Harmonic Analysis (key, cadences, function distribution,
      tension curve, complexity, ambiguity, modulations), Structure (sections, form),
      Track Analysis (per-track note/chord counts, velocities, pitch ranges, durations),
      Fingerprint (pitch histogram)
- [x] 14 tests (empty song, single track, chords, structure, markdown format,
      velocity reporting, pitch range, duration, multi-track, fingerprint, rests,
      edge cases)

**Stats:** 406+ public functions. 2534 tests. 323 songs. 44 scales.


## v137.0 — Song Builder DSL v2

### parse_song_dsl — parse full song specification
- [x] `parse_song_dsl(text)` → dict with bpm, time_sig, key_sig, title, tracks, effects
- [x] Global settings: bpm, time, key, title
- [x] Track definitions: `track <name> <instrument>:` with bar notation
- [x] Mini-notation support: notes (C4, G#5), rests (-, ~), chords ([C4 E4 G4])
- [x] Comments support (#)

## v138.0 — Harmonic Language Model

### train_harmonic_model — corpus-trained Markov chains
- [x] `train_harmonic_model(progressions, order)` → model dict
- [x] Learns chord transition probabilities from real songs
- [x] Supports order 1 (bigram) and order 2 (trigram)
- [x] Tracks starts, transitions, chord frequencies, corpus size

### generate_progression_learned — learned progression generation
- [x] `generate_progression_learned(model, length, key, start_chord, seed)` → progression
- [x] Uses trained Markov model for idiomatic progressions
- [x] Transposes to any key
- [x] Weighted random selection based on learned probabilities

### suggest_progression_learnt — high-level learned suggestion
- [x] `suggest_progression_learnt(genre, length, key, seed)` → progression
- [x] Pre-trained models for jazz, pop, blues, rock, classical
- [x] Genre-appropriate idioms learned from 323-song corpus patterns
- [x] Example: jazz → maj7/dominant chains, blues → dom7 chains, pop → I-V-vi-IV variations

**Stats:** 411+ public functions. 2534 tests. 323 songs. 44 scales.

## v139.0 — Fugue Generator

### generate_fugue — Baroque counterpoint automated
- [x] `generate_fugue(subject, voices, key, tonal, include_stretto, episodes, seed)` → Song
- [x] **Exposition**: Subject entries in all voices alternating with tonal/real answers
- [x] **Tonal answer**: Transposition to dominant with interval adjustments
- [x] **Real answer**: Exact transposition to dominant
- [x] **Countersubject**: Harmony line in 3rds/6ths complementing the subject
- [x] **Episodes**: Connecting passages with sequential figures and modulation
- [x] **Stretto**: Overlapping subject entries for climactic finish
- [x] **Cadence**: All voices converge to tonic
- [x] Supports 2-4 voices (soprano, alto, tenor, bass)
- [x] 11 tests (basic, custom subject, voice counts, tonal/real, stretto toggle, episodes, keys, notes present, reproducibility, edge cases)

**Stats:** 412+ public functions. 2545 tests. 323 songs. 44 scales.

## Next session roadmap

### Tier 1: Ship immediately (v141.x) - DONE
- [x] **MusicXML Export** - `export_musicxml(song, path)` in notation.py (shipped earlier)
- [x] **Harmonic Language Model** - `suggest_progression_learnt(genre, length, key)` with per-genre Markov models (shipped earlier)

### Tier 2: Composition intelligence (v141.x-v142.x) - DONE
- [x] **Song-Level Critique** - `critique_song(song, key)` with inter-track analysis, arrangement balance (v140)
- [x] **Form Generators** - `generate_canon`, `generate_sonata_form`, `generate_rondo` (v140), `generate_theme_and_variations` (v134), `generate_fugue` (v139)
- [x] **Unified Form Dispatcher** - `generate_form(style, key, bpm)` - 7 formal structures: sonata, rondo, aaba, verse_chorus, binary, ternary, theme_variations (v136)

### Tier 3: Analysis & intelligence (v143.x-v145.x) - DONE (v136)
- [x] **Style Fingerprint** - `style_fingerprint(song)` - 8-dimension feature vector (harmonic, melodic, rhythmic, timbral, dynamic, structural, register, density) + flat vector for distance computation (v136)
- [x] **Chord Progression DNA** - `progression_dna()` + `progression_distance()` + `find_similar_progressions_dna()` - 22-element feature vector (12 root motion bins + 5 tension stats + 2 counts + 3 quality fracs), Euclidean distance, corpus search (v137)
- [x] **Arrangement Analyzer** - `analyze_arrangement(song)` - track roles (melody/bass/pad/rhythm), register usage, instrument density, voice crossing, range violations, frequency balance, scoring (v136)

### Tier 4: Platform & ecosystem (v146.x-v148.x)
- [x] **Web Playground (Pyodide)** - docs/playground.html with 9 examples, WAV rendering, Ctrl+Enter (shipped earlier)
- [x] **MIDI Round-Trip v2** - import_midi() already exists in midi.py + CLI --import-midi
- [x] **Live Coding REPL** - `code-music --repl` with slash commands (/play, /info, /tracks, /bpm, /export, /undo, /reset) (v138)
- [x] **Song Rendering CLI v2** - `code-music --compose "jazz in Bb"` + `--analyze` (v137)

### Tier 5: Quality & performance (ongoing)
- [ ] **Test Organization** - group 160+ test files by domain (dirs exist, files not moved yet - low priority cosmetic)
- [x] **Benchmark Suite** - 13 perf tests: generation, analysis, rendering, corpus search (v137)
- [x] **py.typed marker** - PEP 561 marker added, `__main__.py` for `python -m code_music` (v137)
- [ ] **Type Annotation Completion** - fix Pyright errors across codebase
- [x] **API Reference Generator** - `make docs` generates docs/api.html (430 functions, 19 modules, searchable) (v138)

### Future exploration
- MusicXML import/export round-trip improvements
- Real-time audio streaming (low-latency playback without file export)
- Collaborative editing (multi-user song composition via CRDTs)
- Plugin system for custom instruments and effects
- VST/AU bridge for external instrument integration

## v140.0 — Song-Level Critique + Form Generators

### critique_song - comprehensive full-song analysis
- [x] `critique_song(song, key)` - detailed critique dict
- [x] **Harmony critique**: Uses existing critique() on extracted progression
- [x] **Per-track analysis**: Note count, range, density for each track
- [x] **Register overlap detection**: Identifies tracks crowding same frequency range
- [x] **Density balance**: Detects severe activity imbalance between tracks
- [x] **Voice independence metric**: Measures track differentiation
- [x] **Arrangement scoring**: Balance score based on track interactions
- [x] **Register spread bonus**: Rewards wide frequency utilization
- [x] **Combined feedback**: Merges harmony + arrangement issues/strengths/suggestions
- [x] **Weighted scoring**: 60% harmony, 40% arrangement
- [x] 14 tests

### generate_canon - Canon/Round form generator
- [x] `generate_canon(melody, voices, key, scale_name, delay_beats, interval, bpm, seed)` - Song
- [x] 2-6 voices with register spread and pan positioning
- [x] Canon at unison (interval=0) or any transposition (e.g. interval=7 for canon at the fifth)
- [x] Auto-generated or user-provided melody
- [x] 13 tests (basic, custom melody, voice counts, clamping, intervals, keys, delay, reproducibility, content)

### generate_sonata_form - Sonata-Allegro form generator
- [x] `generate_sonata_form(key, mode, bpm, include_development, include_coda, seed)` - Song
- [x] **Exposition**: Theme A (tonic), transition, Theme B (dominant/relative major), closing
- [x] **Development**: Fragmentation through 3 remote keys, retransition with dominant prep
- [x] **Recapitulation**: Both themes return in tonic key
- [x] **Coda**: Fragment of Theme A with authority
- [x] Major and minor mode support with automatic second key area
- [x] 10 tests (basic, minor, dev toggle, coda toggle, keys, bpm, reproducibility, content)

### generate_rondo - Rondo form generator
- [x] `generate_rondo(key, scale_name, episodes, bpm, seed)` - Song
- [x] A-B-A-C-A pattern with 1-4 contrasting episodes
- [x] Each episode in a different key (dominant, subdominant, relative minor, supertonic)
- [x] Varied melodic contours and chord progressions per episode
- [x] 11 tests (basic, episode counts, length scaling, clamping, keys, reproducibility, content)

### Integration tests
- [x] 5 cross-form tests (all return Song, titles contain key, all produce notes, top-level imports, theory imports)

**Stats:** 416+ public functions. 2590 tests. 323 songs. 44 scales.

## v136.0 — Form Generator + Style Fingerprint + Arrangement Analyzer

**generate_form(style, key, bpm, chords_per_phrase, include_melody, seed):**
Unified form generator that builds complete formal structures as multi-section
Songs. 7 form templates: sonata (16 phrases with exposition/development/recap),
rondo (11 phrases with A-B-A-C-A), aaba (8 phrases), verse_chorus (16 phrases
with intro/verse/chorus/bridge/outro), binary (6 phrases), ternary (6 phrases),
theme_variations (10 phrases). Development/bridge sections modulate to related
keys. Produces chord, bass, and optional melody tracks.

**style_fingerprint(song):**
Multi-dimensional feature vector across 8 categories: harmonic (root diversity,
quality diversity, tension mean/range, cadence count, key stability), melodic
(pitch range, avg interval, step/leap/rest ratios, contour direction), rhythmic
(avg duration, variety, density, swing, syncopation), timbral (instrument count,
unique instruments, percussion/bass/melody detection), dynamic (velocity mean/
range/std, crescendo/decrescendo detection), structural (track count, total
beats/bars, section estimate), register (lowest/highest/avg MIDI, span), density
(notes/chords/rests per beat). Flat vector output for distance computation.

**analyze_arrangement(song):**
Arrangement analysis with track role detection (melody/bass/pad/rhythm by
instrument name and register heuristics), per-track analysis (note count, rest
count, density, MIDI range, register), voice crossing detection between track
pairs, instrument range violations against the 19-instrument range database,
frequency balance (low/mid/high distribution), and 0-100 arrangement quality
score. Generates actionable suggestions for missing bass, empty registers, and
competing melody tracks.

- [x] `generate_form()` — 7 formal structures, modulating development sections
- [x] `style_fingerprint()` — 8-category feature vector with flat distance vector
- [x] `analyze_arrangement()` — track roles, crossings, violations, balance, scoring
- [x] 42 tests (18 generate_form, 11 style_fingerprint, 13 analyze_arrangement)
- [x] All 3 functions exported from theory/__init__.py and code_music/__init__.py

**Stats:** 420+ public functions. 2657 tests. 323 songs. 44 scales.

## v137.0 — Chord Progression DNA + CLI Compose/Analyze

**progression_dna(progression):**
Encodes a chord progression as a 22-element feature vector: 12-bin root
motion histogram (normalized), 5 tension curve stats (mean, std, min, max,
range), unique root/quality counts, and major/minor/dominant quality fractions.
Fixed-size vectors enable instant corpus-wide similarity without per-chord
comparison.

**progression_distance(dna_a, dna_b):**
Euclidean distance between DNA vectors. Zero = identical harmonic DNA.

**find_similar_progressions_dna(query, corpus, top_k):**
Corpus search by DNA distance. Computes query DNA once, ranks all entries
by Euclidean distance. Returns top-k sorted ascending.

**CLI --compose:**
`code-music --compose jazz ballad in Bb at 90 bpm` generates a Song from
natural language via the existing `compose()` function, then plays or exports.
Supports all format flags (--flac, --mp3, --wav, --midi) and --play.

**CLI --analyze:**
`code-music my_song.py --analyze` prints a full markdown analysis report
(form, key, modulations, cadences, tension, complexity, density, style) via
`full_analysis()`. No audio render - pure analysis.

- [x] `progression_dna()` — 22-element feature vector from progression
- [x] `progression_distance()` — Euclidean distance between DNA vectors
- [x] `find_similar_progressions_dna()` — corpus search by DNA distance
- [x] CLI `--compose` — natural language song generation from command line
- [x] CLI `--analyze` — full analysis report without rendering
- [x] 29 tests (14 DNA, 5 distance, 5 corpus search, 5 CLI/imports)
- [x] All functions exported from theory/__init__.py and code_music/__init__.py

**Stats:** 425+ public functions. 2686 tests. 323 songs. 44 scales.

## v138.0 — Live Coding REPL + API Reference Generator

**code-music --repl:**
Interactive Python REPL with all 430+ code_music functions pre-imported.
Creates a default Song object. Slash commands for immediate feedback:
/play (render + play), /info (metadata), /tracks (list), /bpm (get/set),
/export (WAV/FLAC/MP3/MIDI), /undo (remove last track), /reset (fresh song),
/add (execute code + auto-play). Built on Python's code.InteractiveConsole
with command interception. Handles Song falsiness (empty songs are falsy
in code_music, so all checks use `is not None`).

**API Reference Generator (make docs):**
`scripts/build_api_docs.py` introspects the code_music module, extracts
all public functions/classes with signatures and docstrings, categorizes
by source module (19 categories), and generates a single-page HTML reference
at `docs/api.html`. Dark-themed, searchable via JS filter, includes class
methods, module attribution, and formatted docstring sections (Args,
Returns, Examples). 430 functions documented.

**Makefile `docs` target:**
`make docs` runs the generator and prints the GitHub Pages URL.

- [x] `code_music/repl.py` — MusicConsole, slash command handler, start_repl()
- [x] CLI `--repl` flag wired into cli.py
- [x] `scripts/build_api_docs.py` — introspection + HTML generation
- [x] `docs/api.html` — 430 functions, 19 modules, dark theme, search
- [x] Makefile `docs` target
- [x] 21 tests (15 REPL commands, 1 CLI flag, 5 docs validation)
- [x] pyproject.toml version bump to 138.0.0

**Stats:** 430+ public functions. 2720 tests. 323 songs. 44 scales.

## v139.0 — Auto-Accompaniment + Song Comparison

**auto_accompany(melody, key, genre, bpm, title, seed):**
Give it a melody, get a full band. Detects key from melody if not provided,
generates genre-appropriate chord progressions via generate_progression,
builds bass lines (walking for jazz/blues, root-fifth for pop/rock,
syncopated for electronic), adds drum patterns (skipped for ambient/classical).
7 genre profiles: pop, jazz, rock, blues, classical, electronic, ambient.
The inverse of compose() - start from a musical idea, get the rest filled in.

**compare_songs(song_a, song_b):**
Multi-dimensional song comparison using style_fingerprint vectors. Computes
per-dimension similarity (harmonic, melodic, rhythmic, timbral, structural)
using normalized Euclidean distance. Weighted overall score (harmonic 30%,
melodic 25%, rhythmic 20%, structural 15%, timbral 10%). Lists notable
differences: tempo, key, track count, exclusive instruments, harmonic/melodic
divergence. Useful for A/B testing, style matching, plagiarism detection.

- [x] `auto_accompany()` — melody-to-full-arrangement, 7 genres, key auto-detect
- [x] `compare_songs()` — 5-dimension similarity with weighted overall score
- [x] 29 tests (17 auto_accompany, 12 compare_songs)
- [x] All functions exported from theory/__init__.py and code_music/__init__.py

**Stats:** 435+ public functions. 2749 tests. 323 songs. 44 scales.

## v140.1 — Mastering CLI + Stem Import/Export + Metadata Embedding

**CLI --master:**
`code-music --master song.wav --target-lufs=-14 --flac` masters an existing
WAV file: reads audio, measures input LUFS, runs full mastering chain
(normalize LUFS, true peak limit, dither), exports to WAV/FLAC/MP3/OGG.
Completes the production pipeline: write -> render -> master -> distribute.

**CLI --stems:**
`code-music my_song.py --stems` exports each track as a separate audio file.
Supports --flac and --mp3 format flags. Output directory defaults to
`<script_name>_stems/`. Lists all exported stems with filenames.

**Song.import_stems(directory, bpm, title, sample_rate):**
Import a directory of WAV/FLAC/MP3 files as SampleTracks. Each file becomes
a SampleTrack triggered at beat 0. File name (without extension) becomes the
track name. Round-trip: export_stems -> import_stems. The inverse of
export_stems().

**Metadata embedding:**
export_mp3(), export_flac(), and export_ogg() now accept an optional
`metadata` dict for ID3/Vorbis tags (artist, title, album, year). Tags are
passed through to pydub/ffmpeg for embedding in the output file.

- [x] CLI `--master` — master WAV files with LUFS normalization
- [x] CLI `--stems` — export individual track stems
- [x] CLI `--target-lufs` — configurable LUFS target for mastering
- [x] `Song.import_stems()` — import WAV directory as SampleTracks
- [x] `metadata` parameter on export_mp3/export_flac/export_ogg
- [x] 15 tests (4 master CLI, 1 stems CLI, 6 import, 3 metadata, 1 round-trip)

**Stats:** 440+ public functions. 2764 tests. 323 songs. 44 scales.

## v141.0 — Theory Course + Time-stretch/Pitch-shift + Batch Mastering

**theory_course(lesson_id, topic) + grade_lesson(lesson_id, answers):**
12-lesson interactive music theory course covering notes, major/minor scales,
intervals, triads, seventh chords, progressions, cadences, voice leading,
modes, rhythm/meter, and song form. Each lesson has topic, description,
concepts list, and 3 graded exercises. Filter by topic (basics, scales,
intervals, chords, harmony, rhythm, form). grade_lesson() returns score,
percentage, letter grade (A-F), and per-question feedback with correct
answers. Case-insensitive grading. Self-test passes 100% on all 12 lessons.

**time_stretch(samples, sample_rate, rate, grain_size_ms):**
Grain-based overlap-add (OLA) time-stretcher. Rate > 1.0 = faster (shorter),
rate < 1.0 = slower (longer). Pitch stays the same. Hann-windowed grains
with overlap normalization. Works on mono and stereo. No external deps.

**pitch_shift(samples, sample_rate, semitones, grain_size_ms):**
Pitch-shift without changing duration. Combines time_stretch (inverse ratio)
with linear interpolation resampling. +12 = octave up, -12 = octave down.
Output length matches input. Works on mono and stereo.

**make master:**
Batch masters all rendered WAVs in dist/wav/ to dist/mastered/. Runs
code-music --master on each file. Tries FLAC first, falls back to WAV
if ffmpeg is not installed.

- [x] `theory_course()` — 12 lessons, topic filtering, exercise grading
- [x] `grade_lesson()` — score, percentage, letter grade, per-question feedback
- [x] `time_stretch()` — grain OLA time-stretcher (mono + stereo)
- [x] `pitch_shift()` — resample-based pitch-shift preserving duration
- [x] `make master` — batch mastering Makefile target
- [x] 34 tests (11 course, 10 grading, 7 time-stretch, 5 pitch-shift, 1 Makefile)

**Stats:** 445+ public functions. 2798 tests. 323 songs. 44 scales.

## v142.0 — Cross-synthesis + Wavetable Scanning + Bowed String Model

**cross_synthesis(source, target, sample_rate, fft_size, blend, wet):**
STFT-based cross-synthesis: takes magnitude spectrum from target and phase
spectrum from source. The result has the pitch/timing of source but the
timbral character of target. Overlap-add with Hann windowing for artifact-free
reconstruction. blend parameter controls interpolation between source and
target magnitudes. Higher fidelity than the vocoder (band-pass filter approach)
because it operates directly in the frequency domain.

**SoundDesigner.wavetable_scan(tables, scan_rate, volume, detune_cents):**
LFO-scanned wavetable bank. A triangle LFO sweeps through a list of
Wavetable objects, interpolating between adjacent tables at each sample.
Produces the evolving, animated timbres characteristic of modern synths
(Serum, Vital, Massive). scan_rate controls sweep speed in Hz. Works with
any number of tables (minimum 2). Chainable with envelope, filter, LFO.

**bowed_string physical model:**
Waveguide with continuous friction excitation simulating a bowed string
(violin, cello, viola). Unlike Karplus-Strong (single pluck then decay),
the bow maintains sustained excitation through a stick-slip friction model
(hyperbolic tangent approximation). bow_pressure controls excitation force
(0=gentle sul tasto, 1=forceful marcato). Includes rosin noise texture.
New preset: `pm_violin`. 18 total SoundDesigner presets.

- [x] `cross_synthesis()` — STFT magnitude/phase transfer effect
- [x] `SoundDesigner.wavetable_scan()` — LFO-scanned wavetable bank
- [x] `bowed_string` physical model — sustained friction-driven waveguide
- [x] `pm_violin` preset — bowed string with ADSR + lowpass
- [x] 20 tests (7 cross-synthesis, 6 wavetable scanning, 7 bowed string)

**Stats:** 450+ public functions. 2818 tests. 323 songs. 44 scales.

## v143.0 — Envelope Follower + Gallery Builder + Lint Cleanup

**EnvFollower(attack_ms, release_ms):**
Amplitude envelope extractor with one-pole ballistics. Three methods:
follow() extracts envelope from audio (mono/stereo, normalized 0-1),
duck() applies sidechain ducking (loud sidechain = quiet target),
gate() applies envelope-based gating (below threshold = attenuated).
Classic pump effect in one function call. Integrated into ModMatrix via
connect_env_follower() for routing sidechain to any destination.

**make gallery (scripts/build_gallery.py):**
Renders all 18 SoundDesigner presets at C3/C4/C5, encodes as base64 WAV
data URIs, generates docs/gallery.html with inline audio players and SVG
waveform visualizations. Dark-themed, single-page, zero server needed.

**Lint cleanup:**
Fixed 140+ lint errors across the codebase: import sorting (I001),
unused imports (F401), unused variables (F841), ambiguous names (E741),
line length (E501), and f-string issues (F541). Added per-file ignores
in pyproject.toml for F821 (Song forward refs) and E402 (song scripts).
make check now passes clean.

- [x] `EnvFollower` — follow, duck, gate methods
- [x] `ModMatrix.connect_env_follower()` — sidechain routing
- [x] `make gallery` — preset gallery with audio players
- [x] Lint cleanup: 140+ errors fixed, make check passes clean
- [x] 20 tests (7 follow, 5 duck, 3 gate, 5 ModMatrix integration)

**Stats:** 455+ public functions. 2838 tests. 323 songs. 44 scales.
