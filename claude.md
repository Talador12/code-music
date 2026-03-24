# code-music — project state

## Status: v1.0.0 — 60 songs, 327 tests, full roadmap complete

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

### Songs: 60 | Albums: 22 | Scales: 32 | Samples: 100+ | Styles: 7

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
- [ ] Reach 80 songs
- [x] Tag v1.3.0 release
