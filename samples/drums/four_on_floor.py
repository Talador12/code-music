"""Four on the floor: techno kick pattern with open hat offbeats, 128 BPM."""

from code_music import Note, Song, Track

song = Song(title="four_on_floor", bpm=128)

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=1.0))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.55))

k = Note("C", 2, 1.0)
h = Note("F", 5, 0.5)
r = Note.rest

kick_pat = [k, k, k, k]  # every beat
hat_pat = [r(0.5), h] * 4  # offbeat 8th notes

for _ in range(4):
    kick.extend(kick_pat)
    hat.extend(hat_pat)
