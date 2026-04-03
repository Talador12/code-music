# code-music — project state

## Status: v28.0.0 — 249 songs, 1261 tests, inversions + voicing rotation + pedal point

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

### Songs: 249 | Albums: 23 | Scale demos: 31 | Samples: 100+ | Styles: 7

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
