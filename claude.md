# code-music — project state

## Status: v0.8.0 — 5 new songs, bitcrush/ring_mod/tape_sat, 22 albums fleshed out

## Songs (18 total)
| File | Title | Genre | BPM |
|---|---|---|---|
| hello_world | Hello World | tutorial | 100 |
| lo_fi_loop | Bedside Table | lo-fi hip-hop | 90 |
| prog_rock | Teeth | prog rock | 130 |
| clarity_drive | Offshore | festival EDM | 128 |
| lollipop_laser | Lollipop Laser | cosmic disco | 128 |
| deep_space_drift | Carrier | ambient | 60 |
| trance_odyssey | Drop | uplifting trance | 138 |
| tank_bebop | The Count | bebop jazz | 168 |
| symphony_no1 | Symphony No. 1 | classical | 108 |
| cinematic_rise | Weight | cinematic | 100 |
| deadmau5_house | Machine Dreams | progressive house | 128 |
| liquid_dnb | Upstream | liquid DnB | 174 |
| future_bass | Between | future bass | 150 |
| **heavy_wobble** | **Half Step** | **dubstep** | **140** |
| **late_shift** | **Low Light** | **neo-soul R&B** | **88** |
| **berlin_four** | **Concrete** | **techno** | **138** |
| **chiptune_quest** | **Save Point** | **chiptune/8-bit** | **160** |
| **the_room** | **Room Tone** | **indie/alt rock** | **104** |

## New effects
- `bitcrush(bit_depth, downsample)` — lo-fi / chiptune / NES texture
- `ring_mod(freq_hz)` — metallic / robotic / AM radio
- `tape_sat(drive, warmth)` — warm analog tape saturation

## Albums (22)
All referenced in `albums/` with full track lists, descriptions, influences.
Most now have 2-3 songs each. Target is 4-6 per album.

## Roadmap

### Songs still needed
- [ ] Flamenco / phrygian dominant (guitar + cajon percussion)
- [ ] Gospel / soul choir song (choir_aah full arrangement)
- [ ] Drum & bass — harder (Pendulum/Chase & Status energy, 174)
- [ ] Funk full song (proper James Brown-style groove)
- [ ] Latin jazz / bossa nova
- [ ] Metal full song (heavy distortion, odd time)
- [ ] Folk / fingerpicked full song
- [ ] Ambient generative (procedural, runs indefinitely)

### Engine
- [ ] Karplus-Strong string synthesis (plucked string realism)
- [ ] Chord progression suggester: root + mood → chord list
- [ ] Velocity-to-timbre (harder hit = brighter piano/drums)
- [ ] Polyphonic Track (simultaneous notes)
- [ ] Swing per-note variation (humanize rhythm timing)

### Effects
- [ ] Multi-band compressor (mastering chain)
- [ ] Convolution reverb with real IR files
- [ ] Vocoder effect (robot/harmonizer voice)

### Albums
- [ ] Expand every album to 4-6 tracks minimum
- [ ] Album artwork generation
- [ ] GitHub Pages album browser / web player

### Spotify
- [ ] DistroKid / TuneCore upload guide in docs/
- [ ] Batch CI render to dist/ on push

### Ideas
- [ ] Generative album: seed + genre → whole album procedurally
- [ ] Live watch mode: --watch auto-plays on save
- [ ] BPM tap utility
- [ ] Music taste profile from Spotify API (needs OAuth token)
