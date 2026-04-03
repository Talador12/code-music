"""Drop-2 Jazz — classic jazz voicings with walking bass."""

from code_music import EffectsChain, Note, Song, Track, delay, reverb
from code_music.theory import generate_bass_line, generate_chord_voicing

song = Song(title="Drop-2 Jazz", bpm=130, sample_rate=44100)
prog = [("D", "min7"), ("G", "dom7"), ("C", "maj7"), ("A", "min7")]
tr_chords = song.add_track(Track(name="chords", instrument="piano", volume=0.45))
for root, shape in prog:
    tr_chords.extend(generate_chord_voicing(root, shape, voicing="drop2"))
song.add_track(Track(name="bass", instrument="bass", volume=0.5)).extend(
    generate_bass_line(prog, style="walking", seed=42)
)
song.add_track(Track(name="ride", instrument="drums_hat", volume=0.3)).extend(
    [Note("F#", 6, 0.5) for _ in range(32)]
)
song.effects = {
    "chords": EffectsChain().add(reverb, room_size=0.5, wet=0.2),
    "bass": EffectsChain().add(delay, delay_ms=100, feedback=0.1, wet=0.05),
}
