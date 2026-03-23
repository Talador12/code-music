"""Breakbeat: syncopated hip-hop style break pattern, 93 BPM."""

from code_music import Note, Song, Track

song = Song(title="breakbeat", bpm=93)

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.95))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.8))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.55))

k = Note("C", 2, 0.5)
s = Note("D", 3, 0.5)
h = Note("F", 5, 0.5)
r = Note.rest

# Syncopated break: kick on 1, 1.5, 3; snare on 2, 4
kick_pat = [k, k, r(0.5), r(0.5), k, r(0.5), r(0.5), r(0.5)]
snare_pat = [r(0.5), r(0.5), s, r(0.5), r(0.5), r(0.5), s, r(0.5)]
hat_pat = [h, r(0.5)] * 4  # every other 8th

for _ in range(4):
    kick.extend(kick_pat)
    snare.extend(snare_pat)
    hat.extend(hat_pat)
