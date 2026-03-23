# code-music — project state

## Status: v0.3.0 — voice synthesis, LFO modulation, sidechain, 90 tests

## What's done

### Voice system (`code_music/voice.py`)
- `VoiceClip` — text + voice + backend spec (rate, pitch, volume, pan)
- `VoiceTrack` — sequence of (VoiceClip, beat_offset) pairs
- `Song.add_voice_track()` — mix voice clips alongside instrument tracks
- `generate(clip)` — render one clip to stereo numpy array
- `render_voice_track()` — render full track aligned to song timeline

**Backends (auto-detected, in priority order):**
- `say` — macOS built-in, 184 voices, zero install. Musical voices: Cellos,
  Organ, Zarvox, Trinoids, Bells, Bubbles, Whisper, Wobble, Boing
- `bark` — Suno Bark AI (transformers + torch), realistic speech + ♪ singing ♪
- `elevenlabs` — ElevenLabs API (ELEVENLABS_API_KEY env var)
- `openai` — OpenAI TTS API (OPENAI_API_KEY env var), voices: alloy/echo/fable/onyx/nova/shimmer

### New effects
- `tremolo(rate_hz, depth)` — amplitude LFO
- `vibrato(rate_hz, depth_cents)` — pitch LFO via time-warp
- `lfo_filter(rate_hz, min_cutoff, max_cutoff)` — swept filter (EDM filter-open)
- `sidechain(target, trigger, ...)` — classic EDM pumping / kick-duck

### Voice samples (`samples/voices/`)
- `robot_choir.py` — Zarvox + Trinoids + Cellos "ah/ooh" choir over Cm pad
- `daft_punk_vocoder.py` — Cellos + Organ funk vocoder over disco beat
- `singing_demo.py` — all 11 musical say voices back-to-back demo
- `spoken_word_beat.py` — Whisper poetry over lo-fi hip-hop beat
- `operatic_drama.py` — Cellos operatic "aaaah" over string orchestra swell
- `edm_vocal_chop.py` — Bubbles + Junior syllable chops over 128bpm EDM

### Tests: 90 passing
- `test_voice.py` — backend detection, clip generation, pan/volume, VoiceTrack render
- `test_lfo_sidechain.py` — tremolo, vibrato, lfo_filter, sidechain

## Roadmap

### Voice / AI
- [ ] Bark integration test (needs GPU or patience)
- [ ] ElevenLabs singing mode (v3 API)
- [ ] `VoiceClip.phonemes` — explicit phoneme timing for robotic stutter effects
- [ ] Pitch-correct voice to scale (autotune-style post-processing)

### EDM
- [ ] LFO on synth parameters at note level (per-note filter sweep)
- [ ] Arpeggiator helper: `arp(chord, pattern, rate)` sugar
- [ ] Song sections API (verse/chorus/bridge markers)
- [ ] Tank!/Bebop-style full song with brass + sax + voice

### Orchestral
- [ ] Dynamic velocity curves (crescendo/decrescendo helpers)
- [ ] Instrument articulations (staccato, legato, pizz toggle)

### Export / Distribution
- [ ] MIDI export (`.mid`) for DAW import
- [ ] Spotify distributor notes (DistroKid / TuneCore guide)
- [ ] GitHub Pages web player

### Ideas from roadmap sessions
- [ ] Generative composition: scale + mood → auto-generated melody
- [ ] Song remix: take an existing song script and transpose/retempo it
- [ ] Live coding mode: `--watch` flag that re-renders on file save
