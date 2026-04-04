"""v100 Centennial — integration mega-test verifying cross-feature composition."""

from code_music.theory import (
    SongTemplate,
    additive_rhythm,
    analysis_report,
    andalusian_cadence,
    apply_groove,
    approach_pattern,
    augment,
    available_notes,
    bass_line_jazz,
    build_transition_matrix,
    change_key,
    classify_interval,
    comp_pattern,
    complexity_score,
    corpus_stats,
    crescendo,
    detect_cadences,
    detect_phrases,
    detect_sections,
    diminish,
    dotted,
    drone,
    ear_training_intervals,
    functional_analysis,
    generate_from_matrix,
    generate_progression,
    generate_scale_melody,
    groove_template,
    harmonic_field,
    harmonize_melody,
    interval_vector,
    list_patterns,
    list_scales,
    lookup_voicing,
    memory_game,
    neapolitan_chord,
    parse_chord_line,
    picardy_third,
    progression_from_roman,
    quiz_intervals,
    reharmonize,
    rubato,
    scale_brightness,
    suggest_scale,
    target_chord_tones,
    tension_curve,
    tone_row,
    twelve_bar_blues,
)


def test_centennial_integration():
    """The centennial mega-test: 50+ functions working together."""

    # 1. Generate a progression and analyze it
    prog = generate_progression(key="C", genre="jazz", seed=100)
    assert len(prog) >= 4

    # 2. Functional analysis
    analysis = functional_analysis(prog, key="C")
    assert all("function" in a for a in analysis)

    # 3. Tension curve
    curve = tension_curve(prog, key="C")
    assert all(0.0 <= v <= 1.0 for v in curve)

    # 4. Cadence detection
    cadences = detect_cadences(prog, key="C")
    assert isinstance(cadences, list)

    # 5. Reharmonize
    jazz_prog = reharmonize(prog, key="C", style="jazz")
    assert len(jazz_prog) >= len(prog)

    # 6. Complexity scoring
    comp_a = complexity_score(prog, key="C")
    assert 0 <= comp_a <= 100
    assert 0 <= complexity_score(jazz_prog, key="C") <= 100

    # 7. Bass line generation
    bass = bass_line_jazz(prog, seed=100)
    assert len(bass) > 0

    # 8. Comp pattern
    comp = comp_pattern(prog, style="bossa")
    assert len(comp) > 0

    # 9. Scale melody + harmonize
    melody = generate_scale_melody("C", "dorian", length=8, seed=100)
    voices = harmonize_melody(melody, key="C", style="thirds")
    assert len(voices) == 2

    # 10. Rubato + crescendo
    rubato_mel = rubato(melody, amount=0.1, seed=100)
    cresc_mel = crescendo(melody, start_vel=40, end_vel=100)
    assert len(rubato_mel) == len(melody)
    assert cresc_mel[-1].velocity > cresc_mel[0].velocity

    # 11. Motif development
    motif = melody[:3]
    aug = augment(motif, 2.0)
    dim = diminish(motif, 2.0)
    dot = dotted(melody[0])
    assert aug[0].duration == melody[0].duration * 2
    assert dim[0].duration == melody[0].duration / 2
    assert dot.duration == melody[0].duration * 1.5

    # 12. Approach patterns
    ap = approach_pattern("C", direction="enclosure")
    assert len(ap) == 3

    # 13. Chord tone targeting
    blues = twelve_bar_blues("E")
    targeting = target_chord_tones(blues[:4], key="E", seed=100)
    assert len(targeting) > 0

    # 14. Groove application
    gt = groove_template("j_dilla")
    grooved = apply_groove(melody, gt)
    assert len(grooved) == len(melody)

    # 15. Additive rhythm
    aksak = additive_rhythm([2, 2, 3])
    assert len(aksak) == 7

    # 16. Drone
    dr = drone("C", overtones=3)
    assert len(dr) == 4

    # 17. Neapolitan + Picardy
    neap = neapolitan_chord("C")
    pic = picardy_third("C")
    assert len(neap) == 3
    assert len(pic) == 3

    # 18. Andalusian
    andal = andalusian_cadence("A")
    assert len(andal) == 4

    # 19. Roman numerals
    roman_prog = progression_from_roman(["I", "IV", "V7", "I"], "G")
    assert roman_prog[0] == ("G", "maj")

    # 20. Chord parsing
    chords = parse_chord_line("| Cmaj7 | Dm7 | G7 | Cmaj7 |")
    assert len(chords) == 4

    # 21. Tone row + interval vector
    row = tone_row(seed=100)
    assert len(row) == 12
    iv = interval_vector([0, 4, 7])
    assert sum(iv) == 3

    # 22. Scale atlas
    scales = list_scales()
    assert len(scales) >= 44
    brightness = scale_brightness("lydian")
    assert brightness > scale_brightness("locrian")

    # 23. Scale suggestion
    suggestions = suggest_scale(["C", "E", "G"], key="C")
    assert len(suggestions) > 0

    # 24. Available notes
    avail = available_notes("C", "major")
    assert len(avail) == 7

    # 25. Pattern database
    patterns = list_patterns(genre="jazz")
    assert len(patterns) > 0

    # 26. Voicing lookup
    voicing = lookup_voicing("C", "maj7", position=0)
    assert len(voicing) >= 3

    # 27. Memory game
    game = memory_game(length=4, seed=100)
    assert len(game) == 4

    # 28. Harmonic field
    field = harmonic_field("C")
    assert len(field) == 7

    # 29. Phrase detection
    phrases = detect_phrases(melody)
    assert isinstance(phrases, list)

    # 30. Section detection
    sections = detect_sections(prog * 4, bars_per_section=4)
    assert len(sections) > 0

    # 31. Song template
    t = SongTemplate("aaba")
    t.fill("A", chords=[("C", "maj")]).fill("B", chords=[("F", "maj")])
    result = t.render()
    assert len(result["chords"]) == 4

    # 32. Transition matrix
    matrix = build_transition_matrix([prog, jazz_prog])
    generated = generate_from_matrix(matrix, length=8, seed=100)
    assert len(generated) == 8

    # 33. Corpus stats
    stats = corpus_stats([prog, jazz_prog, blues])
    assert stats["total_progressions"] == 3

    # 34. Quiz + ear training
    quiz = quiz_intervals(count=3, seed=100)
    assert len(quiz) == 3
    ear = ear_training_intervals(count=3, seed=100)
    assert len(ear) == 3

    # 35. Key transposition
    transposed = change_key(melody, "C", "G")
    assert len(transposed) == len(melody)

    # 36. Classify interval
    assert classify_interval(7) == "perfect"

    # 37. Analysis report
    report = analysis_report(prog, key="C", title="Centennial Test")
    assert "Centennial Test" in report
    assert "Complexity" in report
