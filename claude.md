# code-music — project state

## Status: v0.7.0 — album system, 11 genre albums, The Anthology

## What's done

### Album system (`albums/`)
- `_album.py` — AlbumDef schema, render_album(), liner_notes, M3U playlists
- `render.py` — CLI: `python -m albums.render <stem>` / `--all` / `--list`
- Makefile: `make album-<name>`, `make albums`, `make list-albums`
- Output: `dist/albums/<name>/01 - Title.{wav,flac,mp3}` + `liner_notes.txt` + `playlist*.m3u`

### 11 genre albums
| Album file | Title | Genre |
|---|---|---|
| `edm_progressive` | Machine Dreams | Progressive House (deadmau5) |
| `edm_festival` | Clarity Drive | Big Room / Festival EDM (Zedd) |
| `cosmic_electro` | Neon Lollipop | Cosmic Electro / Disco House (Mord Fustang) |
| `jazz_neosoul` | After Hours | Jazz / Neo-Soul (Cowboy Bebop, Herbie Hancock) |
| `drum_and_bass` | Liquid State | Liquid Drum & Bass (Hospital Records) |
| `ambient_cinematic` | Deep Space Drift | Ambient / Cinematic (Eno, Zimmer) |
| `classical_orchestral` | Symphony No. 1 in C Minor | Classical / Orchestral |
| `rock_prog` | Dorian Excursion | Progressive Rock (Floyd, Tool, Rush) |
| `hiphop_lofi` | 3am Study Session | Lo-Fi Hip-Hop (Nujabes, J Dilla) |
| `videogame_anime` | Loading Screen | Video Game / Anime OST (Kanno, Mitsuda) |
| `anthology` | The Anthology | Compilation — 11 genres, 1 per genre |

### make help reorganized
Four audience sections: [VIBE] [CREATE] [EXPLORE] [DEV]
Albums listed with descriptions in [CREATE] section.

## All songs (13)
hello_world, lo_fi_loop, prog_rock, clarity_drive, lollipop_laser,
deep_space_drift, trance_odyssey, tank_bebop, symphony_no1, cinematic_rise,
deadmau5_house, liquid_dnb, future_bass

## Roadmap

### Albums — next
- [ ] Dubstep album (heavy wobble bass, half-time — Skrillex, Excision era)
- [ ] Future Bass / Melodic Dubstep album (Illenium, Marshmello, Flume)
- [ ] Classical Piano album (Chopin nocturnes, Debussy impressionism)
- [ ] World Music album (flamenco, arabic maqam, Japanese traditional)
- [ ] Metal / Symphonic Metal album (Rammstein energy, Nightwish orchestration)
- [ ] R&B / Neo-Soul album (D'Angelo, Frank Ocean influence)
- [ ] Each album needs more tracks — expand to 5-8 tracks minimum

### Songs needed
- [ ] Dubstep song (wobble bass, half-time drops)
- [ ] Flamenco-influenced song (phrygian dominant, guitar + percussion)
- [ ] Neo-soul song (Rhodes, walking bass, jazz-funk hybrid)
- [ ] Chiptune / 8-bit song (square waves, NES-era feel)
- [ ] Drum & Bass — harder (Pendulum-style, distorted bass)

### Engine
- [ ] Chord progression suggester: root + mood → progression
- [ ] Velocity-to-timbre (louder = brighter)
- [ ] Polyphonic Track (simultaneous notes, not sequential)
- [ ] Bitcrusher / lo-fi effect
- [ ] Ring modulator
- [ ] Tape saturation
- [ ] Karplus-Strong string synthesis

### Distribution
- [ ] Spotify upload guide per album (DistroKid / TuneCore)
- [ ] GitHub Pages album browser (web player)
- [ ] Batch CI render to dist/ on push
- [ ] Album artwork generation (matplotlib? or AI image)

### Ideas from sessions
- [ ] Generative album: seed + genre → full album procedurally
- [ ] Live coding mode: --watch auto-plays on save
- [ ] Collaborative: multiple song files merged into one song
- [ ] BPM tap utility
- [ ] Autotune post-processing for voice tracks
