"""Centennial — the v100 milestone song. Uses 25+ theory functions in one composition."""

from code_music import Chord, EffectsChain, Note, Song, Track, delay, reverb
from code_music.theory import (
    SongTemplate,
    additive_rhythm,
    analysis_report,
    andalusian_cadence,
    apply_groove,
    approach_pattern,
    augment,
    bass_line_jazz,
    comp_pattern,
    crescendo,
    detect_cadences,
    diminish,
    dotted,
    drone,
    generate_scale_melody,
    groove_template,
    harmonize_melody,
    neapolitan_chord,
    picardy_third,
    progression_from_roman,
    reharmonize,
    rubato,
    split_note,
    target_chord_tones,
    tension_curve,
    twelve_bar_blues,
)

song = Song(title="Centennial", bpm=108)

# === Section 1: Jazz reharmonization of a pop progression ===
pop_prog = progression_from_roman(["I", "V", "vi", "IV"], "C")
jazz_prog = reharmonize(pop_prog, key="C", style="jazz")

# Comp pattern: bossa style
comp_notes = comp_pattern(jazz_prog, style="bossa", octave=3)
comp_track = song.add_track(Track(name="comp", instrument="piano", volume=0.4, pan=0.1))
comp_track.extend(comp_notes)

# Jazz walking bass
bass = song.add_track(Track(name="bass", instrument="bass", volume=0.5))
bass.extend(bass_line_jazz(jazz_prog, seed=100))

# === Section 2: Generated melody with arch contour + harmony ===
melody = generate_scale_melody("C", "dorian", length=16, octave=5, contour="arch", seed=100)
# Add rubato for expression
melody = rubato(melody, amount=0.1, seed=100)
# Crescendo the first half
melody[:8] = crescendo(melody[:8], start_vel=50, end_vel=100)

voices = harmonize_melody(melody, key="C", style="thirds")
lead = song.add_track(Track(name="lead", instrument="sawtooth", volume=0.5, pan=0.15))
lead.extend(voices[0])
harmony = song.add_track(Track(name="harmony", instrument="sawtooth", volume=0.35, pan=-0.15))
harmony.extend(voices[1])

# === Section 3: Andalusian cadence with Neapolitan color ===
andal = andalusian_cadence("A")
pad = song.add_track(Track(name="pad", instrument="pad", volume=0.35, pan=0.0))
for root, shape in andal:
    pad.add(Chord(root, shape, 3, duration=4.0))
# Neapolitan chord as surprise
pad.extend([Note(n.pitch, n.octave, n.duration) for n in neapolitan_chord("A", duration=4.0)])
# Picardy third ending
pad.extend([Note(n.pitch, n.octave, n.duration) for n in picardy_third("A", duration=8.0)])

# === Section 4: Motif development ===
motif = [Note("C", 5, 0.5), Note("E", 5, 0.5), Note("G", 5, 0.5)]
motif_track = song.add_track(Track(name="motif", instrument="pluck", volume=0.4, pan=0.2))
motif_track.extend(motif)  # original
motif_track.extend(augment(motif, factor=2.0))  # grand
motif_track.extend(diminish(motif, factor=2.0))  # urgent
# Dotted note + split for rhythmic interest
motif_track.add(dotted(Note("C", 5, 1.0)))
motif_track.extend(split_note(Note("E", 5, 2.0), 4))
# Approach pattern ornament
motif_track.extend(approach_pattern("C", octave=5, direction="enclosure"))

# === Section 5: Chord tone targeting over blues ===
blues = twelve_bar_blues("E")
targeting = target_chord_tones(blues, key="E", notes_per_chord=4, seed=100)
solo = song.add_track(Track(name="solo", instrument="sawtooth", volume=0.4, pan=-0.2))
solo.extend(targeting[:32])

# === Section 6: Grooved additive rhythm ===
aksak_pattern = additive_rhythm([2, 2, 3], "C", 4)
grooved = apply_groove(aksak_pattern, groove_template("motown"))
perc = song.add_track(Track(name="perc", instrument="drums_kick", volume=0.5))
for _ in range(4):
    perc.extend(grooved)

# === Section 7: Drone ending ===
drone_notes = drone("C", octave=2, duration=16.0, overtones=4)
bed = song.add_track(Track(name="drone", instrument="pad", volume=0.25))
bed.extend(drone_notes)

# Effects
song.effects = {
    "comp": EffectsChain().add(reverb, room_size=0.4, wet=0.2),
    "lead": EffectsChain().add(delay, delay_ms=300, feedback=0.2, wet=0.15),
    "pad": EffectsChain().add(reverb, room_size=0.8, wet=0.4),
    "drone": EffectsChain().add(reverb, room_size=0.95, wet=0.5),
}

# Analysis — tension curve and cadence detection for the jazz section
_tension = tension_curve(jazz_prog, key="C")
_cadences = detect_cadences(jazz_prog, key="C")
_report = analysis_report(jazz_prog, key="C", bpm=108, title="Centennial Jazz Section")
