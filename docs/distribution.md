# Getting Your Music on Streaming Platforms

code-music generates Spotify-ready FLAC files. Here's how to get them
onto every major platform.

## Quick path: DistroKid (recommended)

**DistroKid** distributes to 150+ platforms (Spotify, Apple Music, Tidal,
Amazon Music, YouTube Music, TikTok, etc.) for ~$23/year unlimited uploads.

```bash
make export-spotify        # renders all songs to dist/flac/
```

Then:
1. Go to https://distrokid.com → Sign Up → Upload Music
2. For each song: upload the `.flac` file from `dist/flac/`
3. Fill in: song title, genre, release date (must be future date)
4. Choose "Single" unless you're releasing an album
5. DistroKid handles ISRC codes, store delivery, and royalty collection

**Timing:** Spotify approval takes 3–5 days. Apple Music takes 1–2 weeks.

---

## Alternative: TuneCore

**TuneCore** charges per release (~$10/single, ~$30/album/year) but
keeps 100% of royalties (vs DistroKid's 100% too, but different model).

Better if you release infrequently and want maximum per-release control.

1. https://www.tunecore.com → Start Distributing
2. Upload FLAC from `dist/flac/`
3. Set release date, territories, pricing
4. TuneCore generates UPC + ISRC automatically

---

## Direct: Spotify for Artists

Spotify now allows direct uploads for independent artists in some markets.

```bash
make export-spotify   # see upload instructions after rendering
```

1. https://artists.spotify.com → Music → Upload Track
2. Minimum requirements: 30 seconds, 44100 Hz, stereo
3. FLAC preferred; MP3 320kbps also accepted
4. Only available in select countries — check eligibility first

---

## Album releases

code-music generates full album packages in `dist/albums/<name>/`:
- Numbered track files: `01 - Title.flac`, `02 - Title.flac`, etc.
- `liner_notes.txt` — title, genre, description, track listing
- `playlist.m3u` — for local players

```bash
make album-edm_progressive    # renders Machine Dreams album
make albums                   # renders all genre albums
```

For DistroKid album upload:
1. Choose "Album" instead of "Single"
2. Upload tracks in numbered order
3. Use the album title from the liner notes
4. Genre comes from the album's `genre` field

---

## Audio format requirements (by platform)

| Platform | Format | Min Quality |
|---|---|---|
| Spotify | FLAC, MP3, WAV | 44100 Hz, stereo |
| Apple Music | FLAC, AIFF, WAV | 44100 Hz, 16-bit min |
| Tidal | FLAC (MQA preferred) | 44100 Hz |
| Amazon HD | FLAC | 44100 Hz |
| YouTube Music | MP3, FLAC | 320kbps min |

code-music FLAC files: 44100 Hz, stereo, 16-bit PCM. Accepted everywhere.

---

## Metadata

DistroKid and TuneCore both let you set:
- **Song title** — use `song.title` from your song file
- **Genre** — from the album's `genre` field
- **Release date** — future date required
- **Language** — English
- **Explicit** — only if applicable

The `liner_notes.txt` in each album folder has everything you need.

---

## Royalties

All three services (DistroKid, TuneCore, direct Spotify) pay:
- ~$0.003–$0.005 per stream on Spotify
- ~$0.007–$0.010 per stream on Apple Music
- ~$0.01+ on Tidal and Amazon HD

To actually earn money from streams you need tens of thousands of plays.
For a personal project: the point is having your music on platforms,
not the revenue. That said — it's real money once it accumulates.
