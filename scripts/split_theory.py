#!/usr/bin/env python3
"""Split theory/__init__.py into submodules.

Reads the monolithic __init__.py, extracts line ranges for each
top-level definition, writes submodule files, then rewrites
__init__.py to re-export from submodules.

Run: .venv/bin/python scripts/split_theory.py
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INIT_PY = ROOT / "code_music" / "theory" / "__init__.py"
PKG = INIT_PY.parent

# ── Module assignment ────────────────────────────────────────────────────

CORE_NAMES = {
    "_NOTE_NAMES",
    "_NOTE_TO_SEMI",
    "_semi",
    "_SCALE_INTERVALS",
    "_CHORD_SEMI",
    "_EXOTIC_SCALES",
    "_note_to_abs",
    "_abs_to_note",
    "_find_nearest",
    "_smooth_voice_lead",
    "_diatonic_chords",
    "_SATB_RANGES",
    "_INTERVAL_NAMES",
    "_ROMAN",
    "_QUALITY_MAP",
    "_FUNCTION_MAP",
    "_COMMON_NEXT",
    "_DEGREE_TO_SEMI",
    "_DEGREE_SHAPES",
    "_ROMAN_TO_DEGREE",
    "_ROMAN_PATTERNS",
    "_PERFECT_CONSONANCES",
    "_IMPERFECT_CONSONANCES",
    "_DISSONANCES",
    "_motion_type",
    "_ENHARMONIC_MAP",
    "_KEY_SIGNATURES",
    "_SHAPE_SYMBOLS",
    "_DEGREE_NAMES",
    "_JUST_RATIOS",
    "_VOICING_DB",
    "_INSTRUMENT_RANGES",
    "_GENRE_TEMPLATES",
    "_MOOD_MAP",
    "_MOZART_MINUET_TABLE",
    "_GROOVE_TEMPLATES",
    "_PATTERN_DB",
    "_JUST_RATIOS",
}

HARMONY_NAMES = {
    "chord_scale",
    "available_tensions",
    "generate_chord_voicing",
    "neapolitan_chord",
    "augmented_sixth",
    "picardy_third",
    "voice_lead_satb",
    "check_parallel_fifths",
    "find_pivot_chords",
    "modulation_path",
    "direct_modulation",
    "pivot_modulation",
    "parse_roman",
    "progression_from_roman",
    "rootless_a",
    "rootless_b",
    "quartal_voicing",
    "stride_voicing",
    "optimal_voicing",
    "smooth_voicings",
    "suggest_substitutions",
    "reharmonize",
    "morph_chord",
    "chord_interpolation",
    "format_chord",
    "format_progression",
    "parse_chord_symbol",
    "parse_chord_symbols",
    "chord_tones",
    "is_chord_tone",
    "filter_chord_tones",
    "scale_info",
    "chord_extensions",
    "suggest_next_chord",
    "harmonic_field",
    "chord_relationships",
    "list_scales",
    "scale_search",
    "scale_brightness",
    "scale_modes",
    "suggest_scale",
    "available_notes",
    "avoid_notes",
    "enharmonic_equivalent",
    "key_signature_accidentals",
    "respell_note",
    "detect_key",
    "functional_analysis",
    "detect_cadences",
    "detect_inversion",
    "inversion_label",
    "invert_chord",
    "rotate_voicing",
    "interval_name",
    "classify_interval",
    "interval_sequence",
    "common_intervals",
    "parallel_motion",
    "modal_interchange",
    "secondary_dominant",
    "deceptive_cadence",
    "plagal_cadence",
    "tritone_sub",
    "scale_degree",
    "scale_degree_name",
    "lookup_voicing",
    "random_voicing",
}

RHYTHM_NAMES = {
    "quintuplet",
    "septuplet",
    "generate_polyrhythm",
    "metric_modulation",
    "displace",
    "phase_shift",
    "hemiola",
    "additive_rhythm",
    "aksak",
    "nested_tuplet",
    "irrational_meter",
    "polymetric_overlay",
    "groove_template",
    "apply_groove",
    "extract_groove",
    "quantize_rhythm",
    "swing_quantize",
    "humanize_timing",
    "dotted",
    "double_dotted",
    "tied",
    "split_note",
    "ritardando",
    "accelerando",
    "rubato",
    "generate_rhythm_pattern",
    "swing_notes",
    "accent_pattern",
    "retrograde_rhythm",
    "harmonic_rhythm",
    "chords_per_bar",
    "quantize_harmonic_rhythm",
    "rhythm_string",
    "rhythm_match",
}

MELODY_NAMES = {
    "generate_scale_melody",
    "generate_chord_melody",
    "generate_counterpoint",
    "generate_variation",
    "species_counterpoint",
    "dorian_lick",
    "phrygian_run",
    "lydian_run",
    "mixolydian_lick",
    "blues_lick",
    "whole_tone_run",
    "chromatic_run",
    "diminished_run",
    "arpeggio_pattern",
    "trill",
    "staccato",
    "legato_connect",
    "arpeggiate_chord",
    "canon",
    "hocket",
    "sequence_by_interval",
    "call_and_response",
    "ostinato",
    "pedal_point",
    "normalize_notes",
    "stretch_melody",
    "smooth_melody",
    "fill_leaps",
    "harmonize_melody",
    "target_chord_tones",
    "approach_pattern",
    "dynamics_curve",
    "crescendo",
    "decrescendo",
    "sforzando",
    "dynamics_map",
    "melody_contour",
    "contour_string",
    "contour_match",
    "hammer_on",
    "pull_off",
    "slide",
    "palm_mute",
    "list_patterns",
    "get_pattern",
    "chain_patterns",
    "count_syllables",
    "stress_pattern",
    "text_to_melody",
    "fit_to_range",
    "auto_octave",
    "humanize_velocity",
    "melody_summary",
    "augment",
    "diminish",
    "fragment",
    "motif_similarity",
}

ANALYSIS_NAMES = {
    "analyze_harmony",
    "song_diff",
    "song_patch",
    "Change",
    "song_fingerprint",
    "song_similarity",
    "section_similarity_matrix",
    "detect_sections",
    "label_form",
    "detect_phrases",
    "phrase_lengths",
    "detect_repeated_sections",
    "validate_counterpoint",
    "grade_counterpoint",
    "tension_curve",
    "tension_at",
    "reduce_to_chords",
    "harmonic_skeleton",
    "complexity_score",
    "complexity_curve",
    "complexity_contrast",
    "texture_density",
    "thin_texture",
    "thicken_texture",
    "density_profile",
    "density_contrast",
    "ambiguity_score",
    "key_certainty",
    "count_pitch_classes",
    "melodic_interval_histogram",
    "note_range",
    "rhythmic_density",
    "pitch_histogram",
    "pitch_class_histogram",
    "velocity_stats",
    "velocity_curve",
    "duration_stats",
    "total_duration",
    "rest_ratio",
    "longest_rest",
    "leap_count",
    "step_count",
    "leap_step_ratio",
    "repetition_ratio",
    "unique_pitches",
    "octave_distribution",
    "register_spread",
    "melodic_range",
    "pitch_center",
    "consonance_score",
    "corpus_stats",
    "key_distribution",
    "tempo_distribution",
    "similar_motion_ratio",
    "contrary_motion_ratio",
    "voice_independence_score",
    "compare_progressions",
    "progression_similarity",
    "find_similar_progressions",
    "note_to_midi",
    "midi_to_note",
    "note_to_freq",
    "analysis_report",
}

GENERATION_NAMES = {
    "generate_bass_line",
    "generate_drums",
    "generate_progression",
    "extend_progression",
    "twelve_bar_blues",
    "rhythm_changes",
    "coltrane_changes",
    "andalusian_cadence",
    "song_form",
    "section_bars",
    "SongTemplate",
    "comp_pattern",
    "click_track",
    "backing_track",
    "tempo_trainer",
    "instrument_range",
    "in_range",
    "double_at_octave",
    "string_quartet",
    "ear_training_intervals",
    "ear_training_chords",
    "scale_exercise",
    "quiz_intervals",
    "quiz_chords",
    "grade_quiz",
    "dice_game",
    "classical_minuet",
    "memory_game",
    "verify_playback",
    "density_plan",
    "orchestration_curve",
    "build_transition_matrix",
    "most_likely_next",
    "generate_from_matrix",
    "train_style_from_corpus",
    "continue_in_style",
    "note_probability",
    "next_note_distribution",
    "parse_chord_line",
    "parse_melody_line",
    "song_from_dsl",
    "change_key",
    "double_time",
    "half_time",
    "transpose_progression",
    "detect_tempo",
    "merge_tracks",
    "drone",
    "evolving_pad",
    "just_ratio",
    "cents_from_et",
    "detune_to_just",
    "quarter_tone",
    "bass_line_jazz",
    "bass_line_funk",
    "bass_line_latin",
    "reverse_progression",
    "rotate_progression",
}

SERIAL_NAMES = {
    "tone_row",
    "row_transforms",
    "interval_vector",
    "pc_set",
    "pc_union",
    "pc_intersection",
    "pc_complement",
    "transpose_set",
}


def classify(name: str) -> str:
    if name in CORE_NAMES:
        return "_core"
    if name in HARMONY_NAMES:
        return "harmony"
    if name in RHYTHM_NAMES:
        return "rhythm"
    if name in MELODY_NAMES:
        return "melody"
    if name in ANALYSIS_NAMES:
        return "analysis"
    if name in GENERATION_NAMES:
        return "generation"
    if name in SERIAL_NAMES:
        return "serial"
    return "_unclassified"


def get_items(source: str) -> list[tuple[str, int, int, str]]:
    """Parse AST and return (name, start_line, end_line, kind) for all top-level items."""
    tree = ast.parse(source)
    items = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            items.append((node.name, node.lineno, node.end_lineno, "func"))
        elif isinstance(node, ast.ClassDef):
            items.append((node.name, node.lineno, node.end_lineno, "class"))
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    items.append((target.id, node.lineno, node.end_lineno, "assign"))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            items.append((node.target.id, node.lineno, node.end_lineno, "assign"))
        elif isinstance(node, ast.Expr):
            # Standalone expressions like _SCALE_INTERVALS.update(...)
            if isinstance(node.value, ast.Call):
                # Attach to the object being called on
                if isinstance(node.value.func, ast.Attribute):
                    obj = node.value.func.value
                    if isinstance(obj, ast.Name):
                        items.append(
                            (f"_{obj.id}_stmt_{node.lineno}", node.lineno, node.end_lineno, "stmt")
                        )
    items.sort(key=lambda x: x[1])
    return items


def extract_block(lines: list[str], items: list[tuple[str, int, int, str]], idx: int) -> str:
    """Extract a source block for item at index, including preceding comments."""
    start_line = items[idx][1]  # 1-indexed
    end_line = items[idx][2]  # 1-indexed

    # Walk backwards from start_line to capture comment/blank lines
    # Stop at the previous item's end_line or at line 18 (after imports)
    if idx > 0:
        prev_end = items[idx - 1][2]  # 1-indexed
    else:
        prev_end = 17  # after `from ..engine import Note, euclid`

    # Collect preceding comments and blank lines
    comment_start = start_line
    for line_no in range(start_line - 1, prev_end, -1):
        line = lines[line_no - 1]  # 0-indexed
        stripped = line.strip()
        if stripped == "" or stripped.startswith("#"):
            comment_start = line_no
        else:
            break

    return "".join(lines[comment_start - 1 : end_line])


def scan_refs(text: str) -> set[str]:
    """Find all identifiers referenced in text."""
    # Quick scan for known core names
    found = set()
    core_candidates = [
        "_NOTE_NAMES",
        "_NOTE_TO_SEMI",
        "_semi",
        "_SCALE_INTERVALS",
        "_CHORD_SEMI",
        "_note_to_abs",
        "_abs_to_note",
        "_find_nearest",
        "_smooth_voice_lead",
        "_diatonic_chords",
        "_SATB_RANGES",
        "_INTERVAL_NAMES",
        "_ROMAN",
        "_QUALITY_MAP",
        "_FUNCTION_MAP",
        "_COMMON_NEXT",
        "_DEGREE_TO_SEMI",
        "_DEGREE_SHAPES",
        "_ROMAN_TO_DEGREE",
        "_ROMAN_PATTERNS",
        "_PERFECT_CONSONANCES",
        "_IMPERFECT_CONSONANCES",
        "_DISSONANCES",
        "_motion_type",
        "_ENHARMONIC_MAP",
        "_KEY_SIGNATURES",
        "_SHAPE_SYMBOLS",
        "_DEGREE_NAMES",
        "_JUST_RATIOS",
        "_VOICING_DB",
        "_INSTRUMENT_RANGES",
        "_GENRE_TEMPLATES",
        "_MOOD_MAP",
        "_MOZART_MINUET_TABLE",
        "_GROOVE_TEMPLATES",
        "_PATTERN_DB",
        "_EXOTIC_SCALES",
        "Note",
        "euclid",
    ]
    for name in core_candidates:
        if re.search(rf"\b{re.escape(name)}\b", text):
            found.add(name)
    return found


MODULE_DESC = {
    "harmony": "chords, voicings, voice leading, modulation, scales",
    "rhythm": "rhythmic patterns, displacement, meters, groove, quantization",
    "melody": "melody generation, contour, patterns, smoothing, dynamics",
    "analysis": "analysis, statistics, fingerprinting, similarity, detection",
    "generation": "generators, templates, progressions, DSL, practice tools",
    "serial": "tone rows, pitch class sets, post-tonal operations",
}


def find_cross_module_calls(
    mod_name: str, text: str, all_modules: dict[str, set[str]]
) -> dict[str, set[str]]:
    """Find calls to functions defined in other (non-_core) modules."""
    refs: dict[str, set[str]] = {}
    for other_mod, names in all_modules.items():
        if other_mod == mod_name or other_mod == "_core":
            continue
        for name in names:
            if name.startswith("_"):
                continue
            if re.search(rf"\b{re.escape(name)}\s*\(", text):
                refs.setdefault(other_mod, set()).add(name)
    return refs


def main():
    source = INIT_PY.read_text()
    lines = source.splitlines(keepends=True)
    items = get_items(source)

    # Classify items and standalone statements
    modules: dict[str, list[tuple[int, str, str]]] = {
        "_core": [],
        "harmony": [],
        "rhythm": [],
        "melody": [],
        "analysis": [],
        "generation": [],
        "serial": [],
    }

    # Map standalone statements to their object's module
    stmt_map = {
        "_SCALE_INTERVALS": "_core",
    }

    for idx, (name, start, end, kind) in enumerate(items):
        block = extract_block(lines, items, idx)

        if kind == "stmt":
            # Standalone statement like _SCALE_INTERVALS.update(...)
            # Extract the object name from the special name format
            # e.g. __SCALE_INTERVALS_stmt_4373
            obj = name.split("_stmt_")[0].lstrip("_")
            mod = stmt_map.get(f"_{obj}", "_core")
            modules[mod].append((idx, name, block))
            continue

        mod = classify(name)
        if mod == "_unclassified":
            print(f"WARNING: unclassified '{name}' at line {start}")
            mod = "_core"  # safe default
        modules[mod].append((idx, name, block))

    # ── Write _core.py ──
    core_text = '"""theory._core — shared constants, data, and private helpers."""\n\n'
    core_text += "from __future__ import annotations\n\n"
    core_text += "from ..engine import Note, euclid  # noqa: F401 — re-exported for submodules\n"

    for _, name, block in modules["_core"]:
        core_text += "\n" + block
    core_text += "\n"

    (PKG / "_core.py").write_text(core_text)
    print(f"  _core.py: {len(modules['_core'])} items")

    # ── Build name→module map for cross-ref detection ──
    all_mod_names: dict[str, set[str]] = {}
    for mod_name, items_list in modules.items():
        all_mod_names[mod_name] = {n for _, n, _ in items_list}

    # ── Write submodules ──
    for mod_name in ["harmony", "rhythm", "melody", "analysis", "generation", "serial"]:
        mod_items = modules[mod_name]
        if not mod_items:
            continue

        # Concatenate all blocks
        all_blocks = "\n".join(block for _, _, block in mod_items)

        # Find core imports needed
        core_refs = scan_refs(all_blocks)
        # Remove Note and euclid (they come from _core re-export)
        engine_refs = core_refs & {"Note", "euclid"}
        core_refs -= engine_refs

        # Find cross-module imports
        cross_refs = find_cross_module_calls(mod_name, all_blocks, all_mod_names)

        # Build file
        text = f'"""theory.{mod_name} — {MODULE_DESC[mod_name]}."""\n\n'
        text += "from __future__ import annotations\n\n"

        # Import from _core
        import_names = sorted(core_refs | engine_refs)
        if import_names:
            if len(import_names) <= 4:
                text += f"from ._core import {', '.join(import_names)}\n"
            else:
                text += "from ._core import (\n"
                for n in import_names:
                    text += f"    {n},\n"
                text += ")\n"

        # Import from other modules
        for other_mod in sorted(cross_refs):
            names = sorted(cross_refs[other_mod])
            if len(names) <= 3:
                text += f"from .{other_mod} import {', '.join(names)}\n"
            else:
                text += f"from .{other_mod} import (\n"
                for n in names:
                    text += f"    {n},\n"
                text += ")\n"

        # Write blocks
        for _, name, block in mod_items:
            text += "\n" + block

        text += "\n"
        (PKG / f"{mod_name}.py").write_text(text)
        print(f"  {mod_name}.py: {len(mod_items)} items")

    # ── Write __init__.py ──
    init_text = '"""theory — Music theory intelligence.\n\n'
    init_text += "Split into submodules for maintainability. All public names\n"
    init_text += "are re-exported here for backward compatibility::\n\n"
    init_text += "    from code_music.theory import chord_scale, generate_bass_line\n"
    init_text += '"""\n\n'

    # Collect public names per module
    all_public: list[tuple[str, str]] = []  # (name, module)
    for mod_name in ["_core", "harmony", "rhythm", "melody", "analysis", "generation", "serial"]:
        for _, name, _ in modules[mod_name]:
            if not name.startswith("_") and not name.startswith("_"):
                all_public.append((name, mod_name))

    # Write imports grouped by module
    for mod_name in ["_core", "harmony", "rhythm", "melody", "analysis", "generation", "serial"]:
        public = sorted(n for n, m in all_public if m == mod_name)
        if not public:
            continue
        init_text += f"from .{mod_name} import (  # noqa: F401\n"
        for n in public:
            init_text += f"    {n},\n"
        init_text += ")\n"

    init_text += "\n__all__ = [\n"
    for name, _ in sorted(all_public):
        init_text += f'    "{name}",\n'
    init_text += "]\n"

    INIT_PY.write_text(init_text)
    print(f"  __init__.py: {len(all_public)} public names re-exported")
    print("Done!")


if __name__ == "__main__":
    main()
