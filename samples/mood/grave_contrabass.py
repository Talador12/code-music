"""Contrabass alone: arco, open fifths, Dm, 50 BPM.

Chill. The lowest orchestral voice by itself.
Deep, warm, slightly rough at the bow. A sound that lives in your chest.
No harmony. Just the note and the air around it.
"""

from code_music import Note, Song, Track, humanize, reverb

song = Song(title="contrabass_alone", bpm=50)

cb = song.add_track(Track(name="cb", instrument="contrabass", volume=0.88, pan=0.0))

# Breathe in — breathe out
phrase = [
    Note("D", 2, 3.0),
    Note.rest(1.0),
    Note("A", 1, 2.0),
    Note("D", 2, 1.0),
    Note.rest(1.0),
    Note("F", 2, 4.0),
    Note.rest(2.0),
    Note("C", 2, 2.0),
    Note("A", 1, 1.0),
    Note.rest(1.0),
    Note("D", 2, 6.0),
    Note.rest(2.0),
]
cb.extend(humanize(phrase, vel_spread=0.06, timing_spread=0.04))

song.effects = {
    "cb": lambda s, sr: reverb(s, sr, room_size=0.88, damping=0.3, wet=0.4),
}
