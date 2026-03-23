# For Listeners

You don't need to write any code. Just press play.

## Setup (one time, ~2 minutes)

```bash
git clone https://github.com/Talador12/code-music
cd code-music
make dev
```

That's it. You now have everything.

## Play a song

```bash
make play-trance_odyssey      # uplifting trance. big build, big drop.
make play-tank_bebop          # big-band jazz. Cowboy Bebop energy.
make play-deep_space_drift    # ambient. very slow. no drums. space.
make play-clarity_drive       # festival EDM. anthemic. 128 BPM.
make play-lollipop_laser      # cosmic disco. euphoric. neon.
make play-symphony_no1        # full orchestra. classical structure.
make play-liquid_dnb          # liquid drum & bass. warm and jazzy.
make play-cinematic_rise      # film trailer. taiko drums. choir swell.
make play-future_bass         # future bass. emotional drop.
make play-lo_fi_loop          # lo-fi hip-hop. chill. late night.
make play-prog_rock           # prog rock. D Dorian. 130 BPM.
make play-deadmau5_house      # slow-burn progressive house.
make play-hello_world         # just a C major scale. short.
```

## Hear all the scales

Every scale plays through all 12 keys. The name and a description show
on screen while it plays.

```bash
make play-scales              # 32 scales, straight (piano)
make play-scales-arp          # same scales, played as arpeggios
```

Want just one group?

```bash
make play-scales-group GROUP=blues      # blues scales only
make play-scales-group GROUP=world      # Japanese, Arabic, Persian...
make play-scales-group GROUP=bebop      # jazz bebop scales
make play-scales-group GROUP=symmetric  # whole tone, diminished, augmented
```

## Hear instrument samples

```bash
make preview-adagio_cello          # solo cello, melancholic
make preview-notturno_rhodes       # late night Rhodes piano
make preview-maestoso_organ        # full pipe organ
make preview-tutti_fortissimo      # full orchestra hit
make preview-con_fuoco             # brass charge, hero arrives
make preview-taiko_war             # battle drums, primal
make preview-choir_swell           # choir swell, minor → major resolution
make preview-dark_arp              # phrygian arpeggio, alluring
make preview-noir_trumpet          # Miles Davis cool jazz trumpet
make preview-war_drums             # low brass + tremolo strings, vast

# Or list everything available:
make list-samples
```

## Export a song to a file

```bash
make songs-flac    # all songs → dist/flac/ (best quality, Spotify-ready)
make songs-mp3     # all songs → dist/mp3/ (320kbps, sharing)
make songs-wav     # all songs → dist/wav/ (lossless PCM)
```

## What am I hearing?

Each song is described in the file itself — open any file in `songs/` and
read the docstring at the top. It explains the style, structure, and
what makes it sound the way it does. No music theory required to read it.

---

*Want to make your own? → [For Creators](for_creators.md)*
