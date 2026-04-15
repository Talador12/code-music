"""2004 Melodic Metalcore - The End of Heartache meets Ascendancy.

Two guitars panned hard L/R harmonizing in thirds. Palm-muted chugs.
Clean arpeggiated breakdown. Double bass drums. Drop C tuning.
If this does not make you want to windmill headbang, the gain is not high enough.
"""

from code_music import (
    Note,
    Chord,
    Track,
    Song,
    EffectsChain,
    scale,
    distortion,
    reverb,
    delay,
    compress,
    F,
    FF,
    MF,
    MP,
    P,
)
from code_music.theory.rhythm import (
    harmonize_lead,
    dual_guitar,
    drop_tuning,
    metal_drum_pattern,
    palm_mute_chug,
    clean_arpeggio,
)

song = Song(title="The End of Ascendancy (2004 Metalcore)", bpm=160, key_sig="E", time_sig=(4, 4))

# === SECTION 1: Dual guitar harmony lead (Killswitch/Trivium style) ===
# Lead melody in E minor - the soaring part
lead_melody = [
    Note("E", 5, 0.5, FF),
    Note("G", 5, 0.5, F),
    Note("A", 5, 0.5, FF),
    Note("B", 5, 1.0, FF),
    Note("A", 5, 0.5, F),
    Note("G", 5, 0.5, MF),
    Note("F#", 5, 0.5, F),
    Note("E", 5, 1.0, FF),
    Note("D", 5, 0.5, F),
    Note("E", 5, 0.5, MF),
    Note("G", 5, 0.5, F),
    Note("A", 5, 0.5, FF),
    Note("B", 5, 1.5, FF),
]

# Drop C tuning on the lead
lead_drop = drop_tuning(lead_melody, "drop_c")

# Harmonize in thirds - two guitars panned hard L/R
left, right, pan_l, pan_r = dual_guitar(lead_drop, interval=-3, key="E", scale_name="minor")

gtr_left = song.add_track(
    Track(name="guitar_lead_L", instrument="sawtooth", volume=0.65, pan=pan_l)
)
gtr_left.extend(left)

gtr_right = song.add_track(
    Track(name="guitar_lead_R", instrument="sawtooth", volume=0.6, pan=pan_r)
)
gtr_right.extend(right)

# === SECTION 2: Palm-muted chug rhythm under the leads ===
chug = palm_mute_chug("E", 2, bars=2, pattern="gallop")
chug_drop = drop_tuning(chug, "drop_c")
rhythm = song.add_track(Track(name="rhythm_guitar", instrument="sawtooth", volume=0.75, pan=0.0))
rhythm.extend(chug_drop)

# === SECTION 3: Clean arpeggio breakdown ===
# The quiet part. Delay. Reverb. The crowd raises their lighters.
clean = clean_arpeggio("E", "min", 4, bars=2, style="fingerpick")
clean_gtr = song.add_track(
    Track(name="clean_guitar", instrument="guitar_acoustic", volume=0.45, pan=-0.1)
)
clean_gtr.extend(clean)

# Second clean guitar: ascending arpeggio, slightly delayed
clean2 = clean_arpeggio("C", "maj", 4, bars=2, style="ascending")
clean_gtr2 = song.add_track(
    Track(name="clean_guitar_2", instrument="guitar_acoustic", volume=0.4, pan=0.15)
)
clean_gtr2.extend(clean2)

# === SECTION 4: Breakdown - half-time, open chugs ===
breakdown = palm_mute_chug("E", 2, bars=2, pattern="breakdown")
breakdown_drop = drop_tuning(breakdown, "drop_c")
bd_gtr = song.add_track(Track(name="breakdown_guitar", instrument="sawtooth", volume=0.85, pan=0.0))
bd_gtr.extend(breakdown_drop)

# === Bass: following the rhythm guitar ===
bass = song.add_track(Track(name="bass", instrument="moog_bass", volume=0.7, pan=0.0))
bass_notes = drop_tuning(
    [
        Note("E", 2, 0.5, F),
        Note("E", 2, 0.5, MF),
        Note("G", 2, 0.5, F),
        Note("A", 2, 1.0, F),
        Note("E", 2, 0.5, MF),
        Note("D", 2, 0.5, F),
        Note("E", 2, 1.0, FF),
    ]
    * 4,
    "drop_c",
)
bass.extend(bass_notes)

# === Drums: double bass into half-time breakdown ===
drums_verse = metal_drum_pattern(bars=2, style="double_bass", seed=42)
drums_lead = metal_drum_pattern(bars=2, style="gallop", seed=42)
drums_bd = metal_drum_pattern(bars=2, style="half_time", seed=42)
drums_clean = metal_drum_pattern(bars=2, style="breakdown", seed=42)

kick = song.add_track(Track(name="kick", instrument="drums_kick", volume=0.85))
kick.extend(drums_verse["kick"] + drums_lead["kick"] + drums_clean["kick"] + drums_bd["kick"])

snare = song.add_track(Track(name="snare", instrument="drums_snare", volume=0.8))
snare.extend(drums_verse["snare"] + drums_lead["snare"] + drums_clean["snare"] + drums_bd["snare"])

hat = song.add_track(Track(name="ride", instrument="drums_ride", volume=0.4))
hat.extend(drums_verse["hat"] + drums_lead["hat"] + drums_clean["hat"] + drums_bd["hat"])

# === Effects ===
song.effects = {
    "guitar_lead_L": EffectsChain()
    .add(distortion, drive=4.0, tone=0.6, wet=0.7)
    .add(compress, threshold=0.4, ratio=6.0),
    "guitar_lead_R": EffectsChain()
    .add(distortion, drive=4.0, tone=0.6, wet=0.7)
    .add(compress, threshold=0.4, ratio=6.0),
    "rhythm_guitar": EffectsChain()
    .add(distortion, drive=5.0, tone=0.5, wet=0.8)
    .add(compress, threshold=0.3, ratio=8.0),
    "clean_guitar": EffectsChain()
    .add(delay, delay_ms=375.0, feedback=0.35, wet=0.3)
    .add(reverb, room_size=0.6, wet=0.3),
    "clean_guitar_2": EffectsChain()
    .add(delay, delay_ms=500.0, feedback=0.3, wet=0.25)
    .add(reverb, room_size=0.5, wet=0.25),
    "breakdown_guitar": EffectsChain().add(distortion, drive=6.0, tone=0.4, wet=0.85),
    "bass": EffectsChain()
    .add(distortion, drive=2.0, tone=0.3, wet=0.4)
    .add(compress, threshold=0.3, ratio=6.0),
}
