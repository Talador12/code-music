# code-music — project state

## Status: v1.5.0-rc — 85 songs, 428 tests, ready to tag

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

### Songs: 85 | Albums: 23 | Scale demos: 31 | Samples: 100+ | Styles: 7

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
- [ ] Tag v1.5.0 release
