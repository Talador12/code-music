"""Basic drum kit: standard 4/4 kick-snare-hat pattern at 120 BPM."""

from code_music import Note, Song, Track

song = Song(title="basic_kit", bpm=120)

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.95))
snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.85))
hat = song.add_track(Track(name="hat", instrument="drums_hat", volume=0.6))

k = Note("C", 2, 1.0)
s = Note("D", 3, 1.0)
h = Note("F", 5, 0.5)
r = Note.rest

kick_beat = [k, r(1.0), k, r(1.0)]
snare_beat = [r(1.0), s, r(1.0), s]
hat_beat = [h, h, h, h, h, h, h, h]  # 8th notes

for _ in range(4):
    kick.extend(kick_beat)
    snare.extend(snare_beat)
    hat.extend(hat_beat)
