"""Practice Session — click track with tempo trainer sections."""

from code_music import EffectsChain, Song, Track, reverb
from code_music.theory import tempo_trainer

song = Song(title="Practice Session", bpm=80)

# Tempo trainer: 80 → 120 BPM in steps of 10
plan = tempo_trainer(start_bpm=80, end_bpm=120, bars_per_step=2, bpm_increment=10)

click = song.add_track(Track(name="click", instrument="drums_hat", volume=0.5))
for section in plan:
    click.extend(section["click"])

song.effects = {"click": EffectsChain().add(reverb, room_size=0.1, wet=0.05)}
