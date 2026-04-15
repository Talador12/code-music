"""The Periodic Table - 118 elements. 118 tracks. One album.

STUB ALBUM - songs not yet written. The magnum opus.

Every element in order by atomic number. Physical and chemical properties
drive every musical decision. Nothing is arbitrary. The science IS the
composition. When we generate these tracks, they should be the best
showcase of what code-music can do.

================================================================================
PHYSICS-TO-MUSIC MAPPING SYSTEM (all values are real, verified)
================================================================================

1. MELTING POINT -> TEMPO (BPM)
   The energy required to break atomic bonds maps to musical energy.
   Normalized: lowest MP (Helium, 0.95 K) = 50 BPM,
   highest MP (Carbon/diamond, 3823 K) = 200 BPM.
   Formula: bpm = 50 + (mp_kelvin / 3823) * 150
   Gases at room temp get 50-70. Soft metals 80-120. Hard metals 140-180.
   Tungsten (3695 K) gets 195. Carbon (sublimes at 3823 K) gets 200.

2. ELECTRONEGATIVITY (Pauling scale) -> HARMONIC TENSION
   How badly an atom wants electrons = how dissonant the harmony.
   Range: 0.7 (Francium) to 3.98 (Fluorine).
   Low EN (< 1.5): consonant, major keys, triads, resolved
   Mid EN (1.5-2.5): moderate tension, 7th chords, some dissonance
   High EN (> 2.5): unresolved dominants, tritones, clusters
   Fluorine (3.98) gets the most dissonant harmony in the album.

3. ELECTRON CONFIGURATION -> RHYTHM STRUCTURE
   Each shell is a rhythmic layer. Each subshell is a subdivision.
   s-block (groups 1-2): 1-2 rhythmic layers, simple patterns
   p-block (groups 13-18): 3-6 layers, moderate complexity
   d-block (groups 3-12): up to 10 layers, polyrhythmic
   f-block (lanthanides/actinides): up to 14 layers, maximum density
   Example: Iron [Ar] 3d6 4s2 = 4 shells (4 rhythm groups),
   d6 subshell = sextuplet subdivision, s2 = binary pulse underneath.

4. ATOMIC MASS (amu) -> BASS WEIGHT
   Heavier atoms get more low-end.
   H (1.008 amu): almost no bass, high register only
   C (12.011 amu): light bass presence
   Fe (55.845 amu): solid bass foundation
   Au (196.97 amu): heavy bass
   Og (294 amu): sub-bass only, chest-rattling

5. STATE AT ROOM TEMPERATURE -> TEXTURE
   Gas: airy pads, space between notes, reverb-heavy, ethereal
   Liquid (only Hg and Br at room temp): fluid arpeggios, legato, flowing
   Solid (crystalline): sharp attacks, defined rhythm, structured
   Solid (amorphous): softer attacks, more legato, less defined
   Solid (metallic): bright, ringing sustain, harmonic overtones

6. DENSITY (g/cm3) -> MIX DENSITY
   Low density (Li, 0.534): sparse arrangement, lots of space
   Medium (Fe, 7.874): full arrangement, balanced
   High (Os, 22.59): wall of sound, every frequency filled
   Osmium gets the densest mix in the entire album.

7. IONIZATION ENERGY (kJ/mol) -> DYNAMIC RANGE
   How hard it is to remove an electron = how wide the volume swings.
   Low IE (Cs, 375.7): narrow dynamics, mostly one volume (easy to ionize)
   High IE (He, 2372.3): enormous pp to ff range (hard to ionize)
   Noble gases have the widest dynamics. Alkali metals the narrowest.

8. EMISSION SPECTRUM / COLOR -> TIMBRE
   Real flame test colors and emission spectra drive instrument choice.
   Li = crimson -> warm, dark instruments (cello, low brass)
   Na = bright yellow -> bright, cutting instruments (trumpet, sax)
   K = violet -> dark with shimmer (rhodes with chorus, muted trumpet)
   Cu = blue-green -> mid-range clarity (clean guitar, piano)
   Sr = red -> aggressive warmth (distorted guitar, overdriven organ)
   Ba = green -> natural, organic (acoustic guitar, flute)
   Elements with no visible emission: determined by other properties.

9. OXIDATION STATES -> KEY CHANGES
   Number of common oxidation states = number of key changes in the track.
   Fe has oxidation states +2, +3, +6 = three key changes.
   Na has only +1 = stays in one key throughout.
   Mn has +2, +3, +4, +6, +7 = five modulations (the most restless).
   Os has +1 through +8 = eight modulations. Maximum harmonic journey.

10. RADIOACTIVITY -> DECAY EFFECTS
    Stable isotopes: clean, pristine sound
    Slightly radioactive (K-40, long half-life): subtle lo-fi artifacts
    Radioactive (U, Th): increasing distortion and bitcrushing
    Very short half-life (Og, 0.7 ms): the track itself decays in real time,
    instruments dropping out, bitrate decreasing, until silence

11. BOND TYPE TENDENCIES -> HOW COMPOUND TRACKS COMBINE THEMES
    Ionic bonds (metal + nonmetal, e.g. NaCl): sharp contrast between the
    two element themes, call-and-response, opposite characters attracting
    Covalent bonds (nonmetal + nonmetal, e.g. H2O): themes blend and merge,
    shared melodic material, cooperative arrangement
    Metallic bonds (metal + metal alloys, e.g. steel): themes layer on top
    of each other, shared rhythm section, additive combination
    Hydrogen bonds (in compounds like water): subtle connections between
    phrases, motifs that echo across sections without directly combining

================================================================================
GENRE FAMILIES BY GROUP (with physical justification)
================================================================================

Group 1  (Alkali metals: Li, Na, K, Rb, Cs, Fr)
    -> Blues. Why: softest metals, lowest ionization energy (easy to strip),
    violently reactive with water, stored in oil to prevent reaction.
    Emotionally volatile, soft exterior, explosive when exposed. That is blues.

Group 2  (Alkaline earth: Be, Mg, Ca, Sr, Ba, Ra)
    -> Country. Why: structural metals. Calcium = bones, limestone, shells.
    Magnesium = chlorophyll (plants). Barium = drilling mud. They build
    things, they support life, they are the foundation. Grounded music.

Groups 3-12 (Transition metals: Sc through Zn, Y through Cd, La through Hg)
    -> Metal subgenres. Why: they ARE metals. The d-block. Multiple
    oxidation states = genre flexibility within the metal family.
    Iron = metalcore. Gold = big band (brass horns). Silver = smooth jazz.
    Tungsten = the hardest, fastest metal track (highest melting point).

Group 13 (Boron group: B, Al, Ga, In, Tl)
    -> Prog rock. Why: metalloids and soft metals. Boron is a semiconductor,
    aluminum is everywhere, gallium melts in your hand, thallium is a
    poison. Identity crisis elements. Prog is genre identity crisis music.

Group 14 (Carbon group: C, Si, Ge, Sn, Pb)
    -> Funk / electronic. Why: carbon = life = groove. Silicon = computers
    = electronic music. Tin = tin can telephone = communication. Lead =
    heaviest, slowest (doom metal exception because lead is THAT heavy).
    The column spans from funk to electronic to doom. Maximum range.

Group 15 (Pnictogens: N, P, As, Sb, Bi)
    -> Jazz. Why: nitrogen is 78% of air. You breathe it through every
    wind instrument. Phosphorus glows (stage presence). Arsenic is the
    poison in a film noir (jazz soundtrack). Bismuth makes rainbow
    crystals (iridescent harmony). They are the breath of music.

Group 16 (Chalcogens: O, S, Se, Te, Po)
    -> Neo-soul / R&B. Why: oxygen = breath = soul. Sulfur = brimstone
    = deep emotion. Selenium = named for the Moon = nocturnal. The
    chalcogens are about depth, warmth, and the things that sustain life
    (oxygen) or destroy it (polonium). Soul music.

Group 17 (Halogens: F, Cl, Br, I, At, Ts)
    -> Punk. Why: most reactive nonmetals. They attack everything.
    Fluorine corrodes glass. Chlorine is a chemical weapon AND pool
    cleaner. Bromine stinks. Iodine sublimes (skips rules). Astatine
    barely exists. Maximum aggression, minimum patience. Punk.

Group 18 (Noble gases: He, Ne, Ar, Kr, Xe, Rn, Og)
    -> Ambient / synthwave. Why: inert. Will not react. Full outer
    shell = complete, self-contained, needing nothing. But they GLOW
    when excited (neon signs, argon lamps). Ambient because they float.
    Synthwave for neon specifically because it defined the aesthetic.

Lanthanides (La through Lu)
    -> Classical. Why: "rare earth" elements (not actually rare, but
    refined). Used in precision optics, magnets, lasers. The 4f subshell
    fills gradually = gradually increasing orchestral complexity. Refined,
    precise, building instrument by instrument. Classical suite.

Actinides (Ac through Lr)
    -> Orchestral epic. Why: radioactive, powerful, dangerous. Uranium
    powers civilizations or destroys them. Plutonium is named for the god
    of death. The 5f subshell = maximum rhythmic complexity. These
    elements carry weight. Full orchestra + full consequences.

================================================================================
NUCLEAR STABILITY ARC (the album's narrative spine)
================================================================================

This album tells the story of matter. From the Big Bang to the edge of
existence. Nuclear stability is the plot.

BINDING ENERGY PER NUCLEON is the key metric. It peaks at Iron-56
(8.79 MeV/nucleon). Everything before iron releases energy by fusing
(getting heavier). Everything after iron releases energy by fissioning
(getting lighter). Iron is the endpoint of stellar fusion - the element
that kills stars. This curve IS the album's dramatic arc.

Act I: The Light Elements (H through C, elements 1-6)
    Origin: Big Bang nucleosynthesis (H, He, traces of Li) + stellar fusion.
    Musical character: SPARSE. ABUNDANT. ENERGETIC. These elements are
    everywhere. They are simple. They are young (cosmically). Hydrogen
    is 75% of all baryonic matter. The tracks are open, spacious, full
    of potential energy. Fusion releases energy here = tracks that GIVE
    more than they take. Bright, generative, forward-moving.
    Stability: Very stable. Long-lived. These nuclei will outlast the stars.
    Sound: Clean, undistorted, natural sustain, wide dynamics.

Act II: The Middle Elements (N through Ca, elements 7-20)
    Origin: Stellar fusion in main sequence and red giant stars.
    Musical character: FULL. ESTABLISHED. FUNCTIONAL. These are the
    elements of life (C, N, O), the elements of geology (Si, Al, Fe),
    the elements of chemistry (Na, Cl, S). Binding energy is climbing
    toward the peak. Each element is more stable than the last. The
    tracks get denser, more arranged, more complex. Full band.
    Stability: Very stable. Abundant. These are the workhorses.
    Sound: Rich arrangements, balanced mix, confident performances.

Act III: The Iron Peak (elements 24-28, Cr through Ni)
    Origin: Silicon burning in massive stars, moments before supernova.
    THE CLIMAX. Iron-56 has the highest binding energy per nucleon of
    any nucleus. Stars can fuse elements up to iron. After iron, fusion
    COSTS energy. The star can no longer support itself against gravity.
    It collapses. Supernova.
    Musical character: MAXIMUM DENSITY. PEAK POWER. PEAK STABILITY.
    Iron is the most stable thing in the universe. The tracks here are
    the loudest, most complex, most heavily arranged in the album.
    Iron's track is the emotional and structural climax. After this,
    everything begins to decay.
    Sound: Wall of sound. Maximum instruments. Maximum dynamics. The
    most "produced" section. Everything the engine can throw at it.

Act IV: The Heavy Stable Elements (Cu through Bi, elements 29-83)
    Origin: Neutron capture in stars (s-process) and supernovae (r-process).
    These elements can only be made by stellar death. Every atom of
    gold, silver, platinum on Earth was forged in a supernova or
    neutron star merger. They are literally stardust funeral gifts.
    Musical character: DECLINING ENERGY but INCREASING RICHNESS.
    Post-climax. The binding energy curve descends. Fusion no longer
    works. But these elements are beautiful - gold, silver, copper.
    The tracks are rich but less energetic. More reflective. The
    arrangements thin slightly with each element. Like autumn.
    Stability: Mostly stable but some show cracks. Bismuth-209 was
    thought to be the heaviest stable isotope until 2003, when its
    radioactivity was detected (half-life: 1.9 x 10^19 years, way
    longer than the age of the universe). It is the last "stable" stop.
    Sound: Warm, detailed, but the distortion starts to creep in.
    Subtle artifacts. Tape hiss. The first signs of decay.

Act V: The Radioactive Elements (Po through U, elements 84-92)
    Origin: Supernovae (r-process) and radioactive decay chains.
    Musical character: UNSTABLE. POWERFUL. DANGEROUS. These elements
    are actively decaying. Alpha particles, beta particles, gamma rays.
    The tracks have audible decay artifacts: bitcrushing that increases,
    notes that shorten, instruments that drop out without warning.
    Uranium is the last naturally abundant radioactive element.
    It powers civilization or destroys it. The dynamics ARE the story.
    Stability: Measurably radioactive. Half-lives from days to billions
    of years. The lo-fi vinyl effect increases. Things are breaking down.
    Sound: Increasing distortion. Bit depth decreasing. Sample rate
    artifacts. The audio itself is decaying.

Act VI: The Transuranics (Np through Lr, elements 93-103)
    Origin: Nuclear reactors and particle accelerators. Humans made these.
    Musical character: SYNTHETIC. POWERFUL. FLEETING. These elements
    do not exist in nature (or exist in trace amounts from U decay).
    Every atom was manufactured. The tracks sound synthetic - more
    electronic, more processed, less "natural" than the earlier elements.
    Plutonium and Americium are the most practically important.
    Stability: Half-lives from millions of years (Pu-244) to minutes.
    Getting shorter. The countdown has started.
    Sound: Increasingly electronic. Less acoustic instruments. More
    synthesis. The organic gives way to the artificial.

Act VII: The Transactinides (Rf through Og, elements 104-118)
    Origin: Particle accelerators ONLY. Atoms created one at a time by
    smashing lighter nuclei together at relativistic speeds.
    Musical character: FRAGMENTING. DISAPPEARING. Each track is shorter
    than the last, proportional to the element's half-life. Rutherfordium
    (1.3 hour half-life) gets 90 seconds. Oganesson (0.7 ms) gets a
    single synthesized tone that lasts 0.7 milliseconds, then silence.
    The album is disintegrating. Notes drop out. Instruments vanish.
    The bit depth decreases. The sample rate drops. Static increases.
    By element 118, you are listening to the sound of matter ceasing
    to exist.
    Stability: Seconds to milliseconds. These atoms are born dying.
    The Island of Stability (around element 114) is a brief rally -
    Flerovium's track is slightly longer than its neighbors, a last
    gasp of coherence before the final dissolution.
    Sound: Glitch. Granular. Fragmenting. The audio format itself degrades.

The album's final silence after Oganesson is not just the end of a
track. It is the end of matter. We have run out of stable configurations
of protons and neutrons. Everything beyond here is theoretical.
The silence is the edge of physics.

================================================================================
COHESION RULES (how the album holds together as one work)
================================================================================

Key signatures by group (all elements in a group share a tonal home):
    Group 1:  E blues scale (alkali metals)
    Group 2:  G major (alkaline earth)
    Group 3:  A minor (early transition)
    Group 4:  B minor (Ti, Zr, Hf, Rf)
    Group 5:  C minor (V, Nb, Ta, Db)
    Group 6:  D minor (Cr, Mo, W, Sg)
    Group 7:  E minor (Mn, Tc, Re, Bh)
    Group 8:  E minor (Fe, Ru, Os, Hs) - shared with 7, darker mode
    Group 9:  F# minor (Co, Rh, Ir, Mt)
    Group 10: G minor (Ni, Pd, Pt, Ds)
    Group 11: Ab major (Cu, Ag, Au, Rg) - the precious metals get major
    Group 12: Bb major (Zn, Cd, Hg, Cn)
    Group 13: C major / C minor alternating (identity crisis)
    Group 14: D major for C/Si (life/digital), D minor for Pb (doom)
    Group 15: F major (pnictogens - the breath key)
    Group 16: Eb major (chalcogens - warm, soulful)
    Group 17: F# minor (halogens - aggressive minor key)
    Group 18: C major drone, no strong key center (noble gases float)
    Lanthanides: progress chromatically La=C through Lu=B
    Actinides: progress through circle of fifths Ac=C, Th=G, U=D...

Period motifs (shared rhythmic DNA within each row):
    Period 1: Whole notes and half notes only. Maximum space.
    Period 2: Quarter note pulse emerges. First real rhythm.
    Period 3: Eighth note patterns. Full groove established.
    Period 4: Sixteenth note layers. First polyrhythm (d-block).
    Period 5: Triplet and sextuplet subdivisions added.
    Period 6: Full polymetric overlay. Maximum complexity.
    Period 7: Tracks decay and shorten. Rhythms fragment.

Transition elements between tracks:
    Adjacent elements share a 2-4 beat crossfade passage where the
    outgoing element's theme morphs into the incoming element's theme.
    This creates continuity across the album. Elements in the same
    group (vertical neighbors) share a recognizable melodic cell that
    gets developed differently in each period.

Compound tracks combine themes using bond-type rules (see mapping #11).
"""

ALBUM = {
    "title": "The Periodic Table",
    "artist": "code-music",
    "genre": "Multi-genre / Science",
    "year": 2026,
    "description": (
        "118 elements. 118 tracks. One album. The periodic table as music. "
        "Iron is metal. Neon is synthwave. Fluorine is punk. Gold is big band. "
        "Every physical property maps to a musical parameter. The science "
        "is the composition. The chemistry is the arrangement."
    ),
    "tracks": [
        # ══════════════════════════════════════════════════════════════
        # PERIOD 1 — The Fundamentals
        # Two elements. The simplest things in the universe.
        # ══════════════════════════════════════════════════════════════
        {
            "n": 1,
            "title": "Hydrogen (H)",
            "song": "elem_001_H",
            "bpm": 120,
            "group": 1,
            "genre": "ambient",
            "origin": "Big Bang nucleosynthesis (first 3 minutes of the universe)",
            "stability": "Stable. Proton half-life > 10^34 years (effectively eternal).",
            "binding_energy": "0 MeV/nucleon (single proton, nothing to bind)",
            "notes": "The first element. 75% of all baryonic matter. Born in the first 3 "
            "minutes after the Big Bang. Single proton, single electron. "
            "Single sine wave, one note, one frequency. Everything starts here. "
            "Stars fuse it (4H -> He + 26.7 MeV, the pp chain). That reaction "
            "powers every star including ours. The most energetically generous element. "
            "Sparse, pure, fundamental. The opening note of the universe.",
        },
        {
            "n": 2,
            "title": "Helium (He)",
            "song": "elem_002_He",
            "bpm": 55,
            "group": 18,
            "genre": "ambient",
            "origin": "Big Bang + hydrogen fusion in stars (4H -> He)",
            "stability": "Stable. Doubly magic nucleus (2p, 2n). Extremely tightly bound.",
            "binding_energy": "7.07 MeV/nucleon (huge jump from H - the first fusion product)",
            "notes": "Noble gas. Second most abundant element. Product of hydrogen fusion - "
            "every star is converting H to He right now. Doubly magic nucleus (filled "
            "shells for both protons and neutrons) = exceptionally stable. Binding "
            "energy jumps from 0 to 7.07 MeV/nucleon - the biggest single leap in the "
            "table. Inert, light, floats away. Refuses to bond (full 1s2 shell). "
            "High-pitched (the squeaky voice gas). Celesta and glass pad. "
            "The wide dynamic range (highest ionization energy in the table, 2372 kJ/mol) "
            "means pp to fff swings. Complete, self-contained, needing nothing.",
        },
        # ══════════════════════════════════════════════════════════════
        # PERIOD 2 — First Structures (Li through Ne)
        # The first real chemistry. Bonds form. Personality emerges.
        # ══════════════════════════════════════════════════════════════
        {
            "n": 3,
            "title": "Lithium (Li)",
            "song": "elem_003_Li",
            "bpm": 82,
            "group": 1,
            "genre": "blues",
            "origin": "Big Bang nucleosynthesis (trace amounts) + cosmic ray spallation",
            "stability": "Stable. Li-7 is 92.5% of natural lithium. Li-6 is the rest.",
            "binding_energy": "5.33 MeV/nucleon (climbing the fusion curve)",
            "notes": "Lightest metal. One of only 3 elements made in the Big Bang (H, He, Li). "
            "Soft enough to cut with a knife. Density 0.534 g/cm3 (floats on water). "
            "Used in mood stabilizers (Li2CO3) and batteries (Li-ion, the modern world runs on this). "
            "Stores energy. Stabilizes mood. Two things the world desperately needs. "
            "Slow blues. Medicated groove. Sparse arrangement (lowest density metal = "
            "sparsest arrangement of any metal track). The lightest sadness.",
        },
        {
            "n": 4,
            "title": "Beryllium (Be)",
            "song": "elem_004_Be",
            "bpm": 100,
            "group": 2,
            "genre": "country",
            "origin": "Cosmic ray spallation (heavier nuclei broken apart by cosmic rays)",
            "stability": "Stable. Be-9 is the only stable isotope (odd-Z, odd-N survivor).",
            "binding_energy": "6.46 MeV/nucleon",
            "notes": "Alkaline earth. Made by cosmic rays smashing into heavier atoms (spallation), "
            "NOT by stellar fusion - one of only 3 elements made this way (Li, Be, B). "
            "Hard, brittle, toxic as dust (berylliosis). Emeralds are beryllium aluminum silicate. "
            "X-ray transparent (used in X-ray windows). Country with a sharp edge. "
            "Beautiful but do not breathe it in. The spallation origin = percussive attacks "
            "(things breaking apart to make it).",
        },
        {
            "n": 5,
            "title": "Boron (B)",
            "song": "elem_005_B",
            "bpm": 125,
            "group": 13,
            "genre": "prog_rock",
            "origin": "Cosmic ray spallation (like Be and Li, NOT stellar fusion)",
            "stability": "Stable. B-11 (80.1%) and B-10 (19.9%). B-10 absorbs neutrons (reactor control).",
            "binding_energy": "6.48 MeV/nucleon",
            "notes": "Metalloid. Not metal, not nonmetal. Made by cosmic ray spallation like Li and Be - "
            "the universe finds it hard to make boron in stars. Borosilicate glass (Pyrex). Borax. "
            "B-10 is a strong neutron absorber (nuclear reactor control rods). "
            "Prog rock because boron can not pick a side. Time sig changes. "
            "The 3 spallation elements (Li, Be, B) share a cosmic ray motif - a percussive "
            "break that represents the high-energy impact that created them.",
        },
        {
            "n": 6,
            "title": "Carbon (C)",
            "song": "elem_006_C",
            "bpm": 98,
            "group": 14,
            "genre": "funk",
            "origin": "Triple-alpha process in red giant stars (3 He-4 -> C-12, the Hoyle state)",
            "stability": "Extremely stable. C-12 is doubly magic. The Hoyle resonance at 7.656 MeV "
            "is one of the most important energy levels in physics - without it, carbon "
            "could not form and the universe would have no life.",
            "binding_energy": "7.68 MeV/nucleon (steep climb up the curve)",
            "notes": "THE element of life. Four bonds (sp3 tetrahedral, sp2 planar, sp linear). "
            "Diamond AND graphite from the same atom - different hybridization, different music. "
            "The triple-alpha process that makes carbon requires a specific nuclear resonance "
            "(the Hoyle state) that Fred Hoyle PREDICTED must exist for life to be possible. "
            "He was right. The universe is fine-tuned to make carbon. "
            "Organic chemistry = 10 million known compounds. "
            "Funk because carbon IS groove. Moog bass. Ghost notes. "
            "The most versatile element gets the most versatile genre. "
            "4 bonds = 4 rhythm layers. sp3 sections are 3D (full arrangement). "
            "sp2 sections are planar (stripped to 2 layers). sp sections are linear (solo).",
        },
        {
            "n": 7,
            "title": "Nitrogen (N)",
            "song": "elem_007_N",
            "bpm": 145,
            "group": 15,
            "genre": "jazz",
            "origin": "CNO cycle in stars > 1.3 solar masses (C + 4H -> N in catalytic loop)",
            "stability": "Stable. N-14 (99.6%). Magic number of protons (7... wait, 7 is not magic. "
            "But N-14 has equal protons and neutrons which helps stability).",
            "binding_energy": "7.48 MeV/nucleon",
            "notes": "78% of every breath. Made in the CNO cycle where carbon catalyzes hydrogen "
            "fusion in massive stars. Triple bond in N2 (945 kJ/mol, strongest diatomic bond). "
            "So stable as N2 that it is inert at room temp despite being essential for life. "
            "Jazz because it is the air in every horn. Triple bond = triplet feel. "
            "Saxophone lead. The invisible backbone of the atmosphere. "
            "Amino acids, DNA, proteins - nitrogen is in every living molecule. "
            "Haber process (N2 + 3H2 -> 2NH3) feeds half the world's population.",
        },
        {
            "n": 8,
            "title": "Oxygen (O)",
            "song": "elem_008_O",
            "bpm": 88,
            "group": 16,
            "genre": "neo_soul",
            "origin": "Stellar fusion (CNO cycle and pp chain byproduct). O-16 made in helium burning.",
            "stability": "Stable. O-16 (99.76%) is doubly magic (8p, 8n). Exceptionally stable.",
            "binding_energy": "7.98 MeV/nucleon (climbing steeply toward iron)",
            "notes": "Third most abundant element in the universe. O-16 is doubly magic (8 protons, "
            "8 neutrons, both magic numbers). Made in helium burning in massive stars. "
            "21% of the atmosphere. 65% of the human body by mass. Breath. Fire. Rust. "
            "Life and destruction from the same element. Second most electronegative (3.44). "
            "Neo-soul. Rhodes. Warm bass. Wide dynamics because oxygen feeds both a candle "
            "flame and a forest fire. 2 unpaired electrons = 2 melodic voices in counterpoint. "
            "Paramagnetic (attracted to magnets) = the melody pulls toward the harmony.",
        },
        {
            "n": 9,
            "title": "Fluorine (F)",
            "song": "elem_009_F",
            "bpm": 190,
            "group": 17,
            "genre": "punk",
            "origin": "Stellar fusion (neon burning in massive stars: 20Ne + gamma -> 16O + 4He, "
            "then 19F via proton capture on 18O)",
            "stability": "Stable. F-19 is the only stable isotope (100% natural abundance).",
            "binding_energy": "7.78 MeV/nucleon",
            "notes": "MOST electronegative element in the table (3.98 Pauling). "
            "Most reactive nonmetal. Attacks glass (SiO2 + 4HF -> SiF4 + 2H2O). "
            "Rocket fuel oxidizer. Teflon (PTFE). Toothpaste (NaF). Prozac has fluorine. "
            "Only one stable isotope (F-19) = one-note punk, no variation. "
            "Maximum electronegativity = maximum harmonic tension. The most dissonant "
            "track in the entire album. Unresolved dominants, tritones, cluster chords. "
            "Punk. Maximum speed. Maximum aggression. 90 seconds. "
            "The element that bonds with EVERYTHING including noble gases (XeF2).",
        },
        {
            "n": 10,
            "title": "Neon (Ne)",
            "song": "elem_010_Ne",
            "bpm": 108,
            "group": 18,
            "genre": "synthwave",
            "origin": "Carbon burning in massive stars (12C + 12C -> 20Ne + 4He)",
            "stability": "Stable. Ne-20 (90.48%). High ionization energy (2080.7 kJ/mol) = wide dynamics.",
            "binding_energy": "8.03 MeV/nucleon",
            "notes": "Noble gas that GLOWS red-orange in discharge tubes. Made in carbon burning "
            "in massive stars (two carbon-12 nuclei fuse). Third most abundant element in the "
            "universe (after H and He). Full outer shell (2s2 2p6). "
            "Synthwave. Moog bass, sync lead, retro-futurism. The aesthetic element. "
            "The gas that defined neon signs, 80s movies, and vaporwave playlists. "
            "High ionization energy = enormous dynamic range (pp to fff). "
            "5 stable isotopes = 5 melodic variations on the theme.",
        },
        # ══════════════════════════════════════════════════════════════
        # PERIOD 3 — Full Arrangements (Na through Ar)
        # Established patterns. The elements you know from high school.
        # ══════════════════════════════════════════════════════════════
        {
            "n": 11,
            "title": "Sodium (Na)",
            "song": "elem_011_Na",
            "bpm": 112,
            "group": 1,
            "genre": "blues",
            "origin": "Carbon burning in massive stars (12C + 12C -> 23Na + p)",
            "stability": "Stable. Na-23 is the only stable isotope (100%).",
            "binding_energy": "8.11 MeV/nucleon",
            "notes": "Alkali metal. Explodes in water (2Na + 2H2O -> 2NaOH + H2, exothermic, "
            "H2 ignites from the heat, yellow-orange flame from Na emission at 589 nm). "
            "That 589 nm doublet = the exact frequency of sodium street lights. "
            "Table salt partner (Na+ in NaCl). Essential for nerve impulse transmission "
            "(Na+/K+ pump, 100 billion neurons firing). Blues with sudden explosive fills. "
            "Soft metal (Mohs 0.5), hard reaction. One stable isotope = one-key blues.",
        },
        {
            "n": 12,
            "title": "Magnesium (Mg)",
            "song": "elem_012_Mg",
            "bpm": 118,
            "group": 2,
            "genre": "country",
            "origin": "Carbon/neon burning in massive stars",
            "stability": "Stable. Mg-24 (79%), Mg-25 (10%), Mg-26 (11%). 3 stable isotopes.",
            "binding_energy": "8.26 MeV/nucleon",
            "notes": "Burns blinding white at 3100 K (2Mg + O2 -> 2MgO). Fireworks. "
            "Camera flash bulbs (before digital). Center of chlorophyll molecule (photosynthesis). "
            "Eighth most abundant element in Earth's crust. "
            "Country anthem that blazes. 3 stable isotopes = 3 verse structure. "
            "Chlorophyll connection: this element is why plants are green = organic, grounded, country.",
        },
        {
            "n": 13,
            "title": "Aluminum (Al)",
            "song": "elem_013_Al",
            "bpm": 130,
            "group": 13,
            "genre": "ska",
            "origin": "Carbon/neon burning in massive stars + supernova nucleosynthesis",
            "stability": "Stable. Al-27 (100%). Only one stable isotope.",
            "binding_energy": "8.33 MeV/nucleon",
            "notes": "Most abundant metal in Earth's crust (8.1% by mass). Third most abundant element "
            "overall. Lightweight (2.7 g/cm3). Cans, foil, aircraft, power lines. "
            "Only one stable isotope = one key, no modulation, straightforward. "
            "Ska because aluminum is light, recyclable, everywhere. "
            "The upbeat of metals. Horn stabs. Walking bass.",
        },
        {
            "n": 14,
            "title": "Silicon (Si)",
            "song": "elem_014_Si",
            "bpm": 128,
            "group": 14,
            "genre": "electronic",
            "origin": "Oxygen burning in massive stars (28Si is the primary product of O+O fusion)",
            "stability": "Stable. Si-28 (92.2%). 3 stable isotopes. Si-28 is doubly magic-adjacent.",
            "binding_energy": "8.45 MeV/nucleon (climbing toward the iron peak)",
            "notes": "Semiconductor. Every computer chip. Solar panels. Glass (SiO2). "
            "Second most abundant element in Earth's crust (27.7%). "
            "Silicon burning is the LAST fusion stage before iron core collapse and supernova. "
            "Electronic. 128 BPM four-on-the-floor. Binary rhythm patterns. "
            "3 stable isotopes = verse/chorus/bridge structure. "
            "Silicon runs the digital world. This track runs on silicon.",
        },
        {
            "n": 15,
            "title": "Phosphorus (P)",
            "song": "elem_015_P",
            "bpm": 148,
            "group": 15,
            "genre": "jazz",
            "origin": "Neon burning in massive stars + neutron capture processes",
            "stability": "Stable. P-31 (100%). Only one stable isotope.",
            "binding_energy": "8.48 MeV/nucleon",
            "notes": "Glows in the dark (white form, chemiluminescence from slow oxidation in air). "
            "DNA backbone (phosphodiester bonds). Matches (P4S3 strikes). Fertilizer. ATP. "
            "Two allotropes: white P4 (tetrahedral, pyrophoric, toxic) and red (amorphous, stable). "
            "One stable isotope = one underlying key. Two allotropes = two contrasting jazz sections. "
            "White phosphorus = fast, dangerous. Red phosphorus = controlled, warm.",
        },
        {
            "n": 16,
            "title": "Sulfur (S)",
            "song": "elem_016_S",
            "bpm": 92,
            "group": 16,
            "genre": "blues",
            "origin": "Oxygen burning in massive stars (32S is a direct O+O fusion product)",
            "stability": "Stable. S-32 (94.9%). 4 stable isotopes. S-32 has magic N=16.",
            "binding_energy": "8.49 MeV/nucleon",
            "notes": "Brimstone. Volcanoes (SO2, H2S). Hot springs. Rotten egg smell (H2S). "
            "Gunpowder component. Vulcanized rubber. Amino acids (cysteine, methionine). "
            "S-32 has a magic neutron number (16) = extra nuclear stability. "
            "4 stable isotopes = 4 blues verses. "
            "Dirty delta blues. Slide guitar. The devil's element needs "
            "the devil's music. Low, rumbling, sulfurous.",
        },
        {
            "n": 17,
            "title": "Chlorine (Cl)",
            "song": "elem_017_Cl",
            "bpm": 178,
            "group": 17,
            "genre": "punk",
            "origin": "Oxygen burning in massive stars + supernova nucleosynthesis",
            "stability": "Stable. Cl-35 (75.8%) and Cl-37 (24.2%). 2 stable isotopes.",
            "binding_energy": "8.52 MeV/nucleon",
            "notes": "Pool water smell. Bleach (NaClO). WWI chemical weapon. Water purifier. "
            "Stomach acid (HCl). PVC plastic. Table salt partner (Cl- in NaCl). "
            "2 stable isotopes = verse/chorus call-and-response punk structure. "
            "Punk. Cleans AND destroys. The element of contradictions "
            "at maximum tempo. Essential for survival, lethal in concentration.",
        },
        {
            "n": 18,
            "title": "Argon (Ar)",
            "song": "elem_018_Ar",
            "bpm": 62,
            "group": 18,
            "genre": "ambient",
            "origin": "Stellar nucleosynthesis (40Ar from 40K decay; 36Ar from silicon burning)",
            "stability": "Stable. Ar-40 (99.6%) from K-40 decay. Ar-36 (0.33%) primordial. 3 stable isotopes.",
            "binding_energy": "8.60 MeV/nucleon",
            "notes": "Noble gas. 0.93% of the atmosphere (third most abundant gas after N2 and O2). "
            "Ar-40 is produced by radioactive decay of K-40 in Earth's crust - most atmospheric "
            "argon is radiogenic, not primordial. Welding shield gas. Incandescent light bulb fill. "
            "3 stable isotopes = 3 layered ambient textures. "
            "Ambient. Warm, protective glow. Prevents oxidation. "
            "The invisible shield. A blanket of inert sound.",
        },
        # ══════════════════════════════════════════════════════════════
        # PERIOD 4 — The Transition Metal Era (K through Kr)
        # First d-block. The workhorses. The metal section.
        # ══════════════════════════════════════════════════════════════
        {
            "n": 19,
            "title": "Potassium (K)",
            "song": "elem_019_K",
            "bpm": 108,
            "group": 1,
            "genre": "blues",
            "origin": "Oxygen burning in massive stars (39K) + s-process",
            "stability": "Stable. K-39 (93.3%). 3 isotopes (K-40 is radioactive, t1/2=1.25 billion years, "
            "0.012% natural abundance - used for K-Ar radiometric dating of rocks).",
            "binding_energy": "8.56 MeV/nucleon",
            "notes": "Alkali metal. Bananas. Nerve impulses (Na+/K+ pump in every neuron). "
            "K-40 is naturally radioactive - your body contains about 0.01 microcuries of it. "
            "Explodes in water (violet flame). K-Ar dating determines the age of rocks. "
            "Blues with violet-lit fills. Essential for every heartbeat.",
        },
        {
            "n": 20,
            "title": "Calcium (Ca)",
            "song": "elem_020_Ca",
            "bpm": 105,
            "group": 2,
            "genre": "country",
            "origin": "Silicon burning + oxygen burning in massive stars",
            "stability": "Stable. Ca-40 (96.9%). 6 stable isotopes. Ca-40 is doubly magic (20p, 20n).",
            "binding_energy": "8.55 MeV/nucleon",
            "notes": "Bones. Teeth. Limestone. Chalk. Marble. Seashells. Eggshells. Cement. "
            "Fifth most abundant element in Earth's crust. Ca-40 is doubly magic (20 protons, "
            "20 neutrons, both magic numbers) = exceptionally stable. "
            "6 stable isotopes = 6 verse structure. "
            "Country with backbone. Structural, dependable, the skeleton of life.",
        },
        {
            "n": 21,
            "title": "Scandium (Sc)",
            "song": "elem_021_Sc",
            "bpm": 142,
            "group": 3,
            "genre": "prog_metal",
            "origin": "Silicon burning + s-process in massive stars",
            "stability": "Stable. Sc-45 (100%). Only one stable isotope.",
            "binding_energy": "8.62 MeV/nucleon",
            "notes": "First transition metal. Rare (22 ppm in crust). Aerospace alloys (Sc-Al). "
            "Scandium lights (metal halide lamps, stadium lighting). "
            "Named for Scandinavia. One stable isotope = one rhythmic pulse. "
            "Prog metal. Odd time signatures. Technical playing. Flying.",
        },
        {
            "n": 22,
            "title": "Titanium (Ti)",
            "song": "elem_022_Ti",
            "bpm": 158,
            "group": 4,
            "genre": "melodic_metalcore",
            "origin": "Oxygen burning in massive stars and supernovae (both s-process and r-process)",
            "stability": "Stable. Ti-48 (73.7%). 5 stable isotopes.",
            "binding_energy": "8.72 MeV/nucleon (approaching the peak)",
            "notes": "Named for the Titans of Greek myth. Strong as steel at 45% less weight. "
            "Biocompatible (bone implants, dental posts). Aircraft (SR-71 Blackbird, 93% Ti). "
            "TiO2 is the whitest white (paint, sunscreen). Corrosion resistant (passivating oxide). "
            "Melodic metalcore. Dual guitar harmony. The Killswitch element. "
            "5 stable isotopes = 5 sections in the arrangement. Beautiful AND indestructible. "
            "Clean breakdown because titanium does not corrode. The tone stays pristine.",
        },
        {
            "n": 23,
            "title": "Vanadium (V)",
            "song": "elem_023_V",
            "bpm": 160,
            "group": 5,
            "genre": "nwoahm",
            "origin": "Silicon burning + explosive nucleosynthesis in supernovae",
            "stability": "Stable. V-51 (99.75%). 2 isotopes (V-50 is radioactive, t1/2=1.4x10^17 years).",
            "binding_energy": "8.74 MeV/nucleon (closing in on the iron peak)",
            "notes": "Strengthens steel. Named for Vanadis (Norse goddess of beauty and fertility). "
            "Vanadium redox flow batteries (grid-scale energy storage). Vanadium steel in cars, "
            "tools, springs. V-50 is very slightly radioactive (one of the rarest natural decays). "
            "NWOAHM groove. Lamb of God energy. Strength through alloy.",
        },
        {
            "n": 24,
            "title": "Chromium (Cr)",
            "song": "elem_024_Cr",
            "bpm": 152,
            "group": 6,
            "genre": "metal",
            "origin": "Silicon burning in massive stars (directly precedes the iron peak)",
            "stability": "Stable. Cr-52 (83.8%). 4 stable isotopes. Cr-52 has magic N=28.",
            "binding_energy": "8.76 MeV/nucleon (nearly at the summit)",
            "notes": "Chrome plating (Cr2O3 passive layer, self-healing like stainless steel). "
            "Stainless steel essential (18% Cr minimum). Emerald green (Cr3+ in Al2O3). "
            "Ruby red (Cr3+ in different crystal field). Same ion, different colors depending on "
            "the crystal environment = same riff, different arrangements. "
            "6 oxidation states (+1 through +6) = 6 key changes. "
            "Polished metal. Mirror-finish guitar tone. Hard and shiny. "
            "Cr-52 has a magic neutron number (28) = extra stability = extra sustain.",
        },
        {
            "n": 25,
            "title": "Manganese (Mn)",
            "song": "elem_025_Mn",
            "bpm": 148,
            "group": 7,
            "genre": "metal",
            "origin": "Silicon burning (just before the iron peak). Last element before the climax.",
            "stability": "Stable. Mn-55 (100%). Only one stable isotope.",
            "binding_energy": "8.77 MeV/nucleon (one step from the summit)",
            "notes": "Steel hardener. Batteries (MnO2 in alkaline cells). Brittle alone but "
            "transforms alloys. 7 oxidation states (+1 through +7) = SEVEN key changes, "
            "the most harmonically restless track in the album. The element right before iron "
            "on the binding energy curve. One step from the peak. The penultimate ascent. "
            "Permanganate (KMnO4) is deep purple = purple-lit stage. "
            "Only one stable isotope = one unwavering rhythmic pulse under all the modulations.",
        },
        {
            "n": 26,
            "title": "Iron (Fe)",
            "song": "elem_026_Fe",
            "bpm": 165,
            "group": 8,
            "genre": "melodic_metalcore",
            "origin": "Silicon burning in massive stars (final stage before supernova)",
            "stability": "Iron-56: highest binding energy per nucleon (8.79 MeV). THE most stable nucleus.",
            "binding_energy": "8.79 MeV/nucleon (THE PEAK. Stars die here.)",
            "notes": "THE metal. THE climax of the album. THE most stable nucleus in the universe. "
            "Iron-56 sits at the peak of the binding energy curve at 8.79 MeV/nucleon. "
            "Everything lighter releases energy by fusing toward iron. Everything heavier "
            "releases energy by fissioning away from iron. Iron is the endpoint. "
            "Stars fuse elements in shells: H -> He -> C -> O -> Si -> Fe. When the core "
            "becomes iron, fusion stops - it would COST energy to go further. The star "
            "collapses. Supernova. Iron is the element that kills stars. "
            "Core of the Earth (inner core is solid Fe-Ni at 5700 K). Hemoglobin. Steel. "
            "THE metalcore track. Drop C. Dual guitar harmony in thirds. "
            "Double bass drums. Maximum arrangement density. Maximum dynamic range. "
            "The breakdown has literal gravitational pull (iron core collapse). "
            "This is the loudest, densest, most fully orchestrated track on the album. "
            "Everything before it was building toward this. Everything after is declining. "
            "Iron IS metal. The star died to make this. So did the album.",
        },
        {
            "n": 27,
            "title": "Cobalt (Co)",
            "song": "elem_027_Co",
            "bpm": 142,
            "group": 9,
            "genre": "metal",
            "origin": "s-process in AGB stars + r-process in supernovae",
            "stability": "Stable. Co-59 (100%). Co-60 is radioactive (gamma source, t1/2=5.27 years).",
            "binding_energy": "8.77 MeV/nucleon (just past the peak - the decline begins)",
            "notes": "First element PAST the iron peak. Binding energy has peaked and is now "
            "declining. From here on, every element is slightly less stable than the one before. "
            "Cobalt blue pigment. Magnets (AlNiCo, SmCo). Co-60 gamma radiation (food sterilization). "
            "Named from kobold (German for goblin, because the ore was cursed). "
            "Dark metal with blue tinge. The first track where the arrangement thins slightly. "
            "One stable isotope = one key. The decline is subtle but it has begun.",
        },
        {
            "n": 28,
            "title": "Nickel (Ni)",
            "song": "elem_028_Ni",
            "bpm": 138,
            "group": 10,
            "genre": "metal",
            "origin": "Silicon burning + nuclear statistical equilibrium in supernovae",
            "stability": "Stable. Ni-58 (68.1%). 5 stable isotopes. Ni-56 -> Co-56 -> Fe-56 "
            "decay chain is what makes supernovae bright (the light curve is powered by Ni-56 decay).",
            "binding_energy": "8.77 MeV/nucleon (virtually tied with Fe and Co at the summit)",
            "notes": "Fun fact: Ni-62 actually has the highest binding energy per nucleon of any "
            "nuclide (8.7945 vs Fe-56 at 8.7903). The 'iron peak' should really be the 'nickel peak.' "
            "But Fe-56 is more abundant because Ni-56 is what stars actually make, then it "
            "decays to Fe-56 after the supernova. Nickel is the secret king. "
            "Coins. Guitar strings (nickel-wound). Magnets. Stainless steel. "
            "Nickel-wound string brightness = the guitar tone. Ringing harmonics. "
            "5 stable isotopes = 5 guitar voices in the arrangement.",
        },
        {
            "n": 29,
            "title": "Copper (Cu)",
            "song": "elem_029_Cu",
            "bpm": 120,
            "group": 11,
            "genre": "fusion",
            "origin": "s-process in AGB stars (slow neutron capture over thousands of years)",
            "stability": "Stable. Cu-63 (69.2%) and Cu-65 (30.8%). 2 stable isotopes.",
            "binding_energy": "8.75 MeV/nucleon (declining from the peak)",
            "notes": "THE conductor. Highest electrical conductivity after silver. Wires. Pipes. "
            "Statue of Liberty (Cu -> CuO -> Cu2(OH)2CO3, the green patina takes 20 years). "
            "Fusion because copper conducts everything - genres, electricity, heat. "
            "Warm tone (copper is warm-colored, literally) that develops green patina over the "
            "track = the genre shifts from metal-warm to jazz-green as the arrangement ages. "
            "2 stable isotopes = verse/chorus structure. "
            "First element in Group 11 (precious metals column: Cu, Ag, Au). The working-class "
            "precious metal. Not as flashy as gold, but civilization runs on copper wire.",
        },
        {
            "n": 30,
            "title": "Zinc (Zn)",
            "song": "elem_030_Zn",
            "bpm": 140,
            "group": 12,
            "genre": "ska",
            "origin": "s-process in AGB stars (slow neutron capture)",
            "stability": "Stable. Zn-64 (49.2%). 5 stable isotopes.",
            "binding_energy": "8.76 MeV/nucleon (near the iron peak)",
            "notes": "Galvanizes steel (protective coating, prevents rust). Sunscreen (ZnO). "
            "Pennies (97.5% zinc since 1982). Immune system essential. Brass alloy (Cu + Zn). "
            "5 stable isotopes = 5 horn voices in the ska section. "
            "Ska because zinc protects and energizes. Upbeat, bouncing, defensive. "
            "Horn stabs. The bodyguard element.",
        },
        {
            "n": 31,
            "title": "Gallium (Ga)",
            "song": "elem_031_Ga",
            "bpm": 78,
            "group": 13,
            "genre": "lofi",
            "origin": "s-process in AGB stars",
            "stability": "Stable. Ga-69 (60.1%). 2 stable isotopes.",
            "binding_energy": "8.73 MeV/nucleon",
            "notes": "Melts in your hand (29.76C melting point - body temperature liquefies it). "
            "GaAs semiconductors (faster than silicon for RF and LEDs). Blue LEDs use GaN. "
            "2 stable isotopes = two-part lofi structure. "
            "Lofi. Everything dissolving. Warm, soft, barely holding together. "
            "The element that melts when you touch it.",
        },
        {
            "n": 32,
            "title": "Germanium (Ge)",
            "song": "elem_032_Ge",
            "bpm": 128,
            "group": 14,
            "genre": "electronic",
            "origin": "s-process in AGB stars + r-process in supernovae",
            "stability": "Stable. Ge-74 (36.5%). 5 stable isotopes.",
            "binding_energy": "8.71 MeV/nucleon",
            "notes": "Semiconductor. Early transistors before silicon took over (first transistor 1947 "
            "used germanium). Fiber optics (GeO2 dopant). Infrared optics (transparent to IR). "
            "5 stable isotopes = 5-part arrangement. "
            "Retro electronic. The proto-digital element. Germanium diode warmth.",
        },
        {
            "n": 33,
            "title": "Arsenic (As)",
            "song": "elem_033_As",
            "bpm": 155,
            "group": 15,
            "genre": "jazz",
            "origin": "s-process in AGB stars",
            "stability": "Stable. As-75 (100%). Only one stable isotope.",
            "binding_energy": "8.70 MeV/nucleon",
            "notes": "The poison. Murder mystery staple (Napoleon, Medici, Marsh test 1836). "
            "Also in semiconductors (GaAs) and CCA wood preservative. Metalloid. "
            "One stable isotope = one dark key throughout. "
            "Dark jazz. Film noir saxophone. Suspenseful, dangerous, beautiful. "
            "The cocktail you should not have ordered.",
        },
        {
            "n": 34,
            "title": "Selenium (Se)",
            "song": "elem_034_Se",
            "bpm": 90,
            "group": 16,
            "genre": "neo_soul",
            "origin": "s-process in AGB stars + r-process in supernovae",
            "stability": "Stable. Se-80 (49.6%). 6 stable isotopes.",
            "binding_energy": "8.69 MeV/nucleon",
            "notes": "Named for the Moon (Selene). Photovoltaic (CdSe solar cells). "
            "Photocopiers (photoconductor drums). Essential trace element (selenocysteine, "
            "the 21st amino acid). Toxic in excess, essential in trace amounts. "
            "6 stable isotopes = 6 sections with lunar phases as structure. "
            "Neo-soul with lunar quality. Soft, reflective, light-sensitive.",
        },
        {
            "n": 35,
            "title": "Bromine (Br)",
            "song": "elem_035_Br",
            "bpm": 170,
            "group": 17,
            "genre": "punk",
            "origin": "s-process in AGB stars + r-process in supernovae",
            "stability": "Stable. Br-79 (50.7%) and Br-81 (49.3%). 2 stable isotopes.",
            "binding_energy": "8.68 MeV/nucleon",
            "notes": "Only nonmetal liquid at room temperature (MP -7.2C, BP 58.8C). Red-brown. "
            "Named from Greek bromos (stench). Flame retardants. Photography (AgBr). "
            "One of only two elements liquid at room temperature (the other is mercury). "
            "2 stable isotopes = verse/chorus punk. Aggressive. "
            "The element that smells like trouble.",
        },
        {
            "n": 36,
            "title": "Krypton (Kr)",
            "song": "elem_036_Kr",
            "bpm": 68,
            "group": 18,
            "genre": "ambient",
            "origin": "s-process in AGB stars + r-process in supernovae",
            "stability": "Stable. Kr-84 (57.0%). 6 stable isotopes.",
            "binding_energy": "8.68 MeV/nucleon",
            "notes": "Noble gas. White-green glow. Used to define the meter (1960-1983, Kr-86 "
            "emission line). Insulating window fill. Flash photography fill gas. "
            "Not Superman's planet (that is Krypton-with-a-K and it is fictional). "
            "6 stable isotopes = 6 layered ambient textures. "
            "Ambient. The measurement element. Precise and glowing.",
        },
        # ══════════════════════════════════════════════════════════════
        # PERIOD 5 — Richer Textures (Rb through Xe)
        # Second row of transition metals. Silver, tin, iodine.
        # ══════════════════════════════════════════════════════════════
        {
            "n": 37,
            "title": "Rubidium (Rb)",
            "song": "elem_037_Rb",
            "bpm": 95,
            "group": 1,
            "genre": "blues",
            "notes": "Alkali metal. Melts at 39C (hot day). Atomic clocks. GPS timing. "
            "Blues with impeccable time. The most precisely timed blues ever played.",
        },
        {
            "n": 38,
            "title": "Strontium (Sr)",
            "song": "elem_038_Sr",
            "bpm": 110,
            "group": 2,
            "genre": "country",
            "notes": "Red flame test. Fireworks (red ones). Bones accumulate it. "
            "Country with red fireworks. The celebratory element.",
        },
        {
            "n": 39,
            "title": "Yttrium (Y)",
            "song": "elem_039_Y",
            "bpm": 140,
            "group": 3,
            "genre": "prog_metal",
            "notes": "Named for Ytterby, Sweden (4 elements named for one village). "
            "Superconductors. LED phosphors. Red in TVs. "
            "Prog metal. Scandinavian. Technical. Precise.",
        },
        {
            "n": 40,
            "title": "Zirconium (Zr)",
            "song": "elem_040_Zr",
            "bpm": 155,
            "group": 4,
            "genre": "metal",
            "notes": "Nuclear reactor cladding. Cubic zirconia (fake diamonds). "
            "Extreme heat resistance. Metal that survives the reactor core.",
        },
        {
            "n": 41,
            "title": "Niobium (Nb)",
            "song": "elem_041_Nb",
            "bpm": 150,
            "group": 5,
            "genre": "metal",
            "notes": "Superconducting magnets (LHC, MRI). Named for Niobe (Greek myth). "
            "Metal with superconducting sustain. Notes that never decay.",
        },
        {
            "n": 42,
            "title": "Molybdenum (Mo)",
            "song": "elem_042_Mo",
            "bpm": 162,
            "group": 6,
            "genre": "metal",
            "notes": "Highest melting point of commonly used metals. Alloy steel. Enzymes. "
            "Metal that refuses to melt. Relentless. The endurance element.",
        },
        {
            "n": 43,
            "title": "Technetium (Tc)",
            "song": "elem_043_Tc",
            "bpm": 135,
            "group": 7,
            "genre": "electronic",
            "notes": "First artificially produced element. No stable isotopes. Radioactive. "
            "Medical imaging tracer. Electronic. Synthetic. Does not exist in nature. "
            "The element that humanity had to build.",
        },
        {
            "n": 44,
            "title": "Ruthenium (Ru)",
            "song": "elem_044_Ru",
            "bpm": 148,
            "group": 8,
            "genre": "metal",
            "notes": "Platinum group. Hard. Catalysts. Electronics contacts. "
            "Rare, precise, industrial metal. Tight, machined riffs.",
        },
        {
            "n": 45,
            "title": "Rhodium (Rh)",
            "song": "elem_045_Rh",
            "bpm": 145,
            "group": 9,
            "genre": "smooth_jazz",
            "notes": "Most expensive precious metal per gram. Catalytic converters. Mirrors. "
            "Smooth jazz. Expensive, reflective, rare. The luxury element.",
        },
        {
            "n": 46,
            "title": "Palladium (Pd)",
            "song": "elem_046_Pd",
            "bpm": 130,
            "group": 10,
            "genre": "fusion",
            "notes": "Catalytic converters. Hydrogen absorption (holds 900x its volume). "
            "Fusion. Absorbs everything. Genre sponge. Named for asteroid Pallas.",
        },
        {
            "n": 47,
            "title": "Silver (Ag)",
            "song": "elem_047_Ag",
            "bpm": 132,
            "group": 11,
            "genre": "smooth_jazz",
            "origin": "s-process in AGB stars (slow neutron capture, thousands of years per step)",
            "stability": "Stable. Ag-107 (51.8%) and Ag-109 (48.2%). 2 stable isotopes.",
            "binding_energy": "8.55 MeV/nucleon",
            "notes": "Highest electrical conductivity of all elements (1.59 x 10^-8 ohm-m). "
            "Highest thermal conductivity of all metals. Highest reflectivity (95% visible light). "
            "Photography (AgBr/AgCl darken in light). Mirrors. Sterling silver (92.5% Ag). "
            "Smooth jazz. Soprano sax. The most conductive music - every note transmits perfectly. "
            "2 stable isotopes = call-and-response between soprano and tenor voices. "
            "Tarnishes (Ag2S, black) = the arrangement darkens gradually over the track. "
            "Sterling quality. Reflective. The mirror element.",
        },
        {
            "n": 48,
            "title": "Cadmium (Cd)",
            "song": "elem_048_Cd",
            "bpm": 115,
            "group": 12,
            "genre": "blues",
            "notes": "Toxic heavy metal. Yellow pigment (cadmium yellow). NiCd batteries. "
            "Heavy blues. Toxic beauty. The paint that poisons the painter.",
        },
        {
            "n": 49,
            "title": "Indium (In)",
            "song": "elem_049_In",
            "bpm": 85,
            "group": 13,
            "genre": "lofi",
            "notes": "Soft, malleable. Touchscreens (ITO). Low melting point. "
            "Lofi. Your phone screen is made of this. Digital intimacy. "
            "Cries when bent (tin cry). The emotional metal.",
        },
        {
            "n": 50,
            "title": "Tin (Sn)",
            "song": "elem_050_Sn",
            "bpm": 120,
            "group": 14,
            "genre": "ska",
            "notes": "Tin cans. Solder. Bronze (tin + copper). Tin whistle. "
            "Ska. The tin whistle is literally a ska instrument. "
            "Bronze age energy. The alloy that started civilization.",
        },
        {
            "n": 51,
            "title": "Antimony (Sb)",
            "song": "elem_051_Sb",
            "bpm": 125,
            "group": 15,
            "genre": "jazz",
            "notes": "Metalloid. Ancient eye makeup (kohl). Flame retardant. Alloys. "
            "Dark jazz. Smoky eyes. The cosmetic element with a dangerous past.",
        },
        {
            "n": 52,
            "title": "Tellurium (Te)",
            "song": "elem_052_Te",
            "bpm": 88,
            "group": 16,
            "genre": "neo_soul",
            "notes": "Named for Earth (Tellus). Rare. Thermoelectric. Solar panels. "
            "Makes your breath smell like garlic for weeks if you handle it. "
            "Neo-soul with earthy warmth. The planet's namesake.",
        },
        {
            "n": 53,
            "title": "Iodine (I)",
            "song": "elem_053_I",
            "bpm": 165,
            "group": 17,
            "genre": "punk",
            "notes": "Purple vapor. Antiseptic. Thyroid essential. Sublimes directly to gas. "
            "Punk with purple lighting. Skips liquid phase entirely (like punk "
            "skipped the rules). Necessary medicine delivered aggressively.",
        },
        {
            "n": 54,
            "title": "Xenon (Xe)",
            "song": "elem_054_Xe",
            "bpm": 72,
            "group": 18,
            "genre": "ambient",
            "notes": "Noble gas but CAN form compounds (xenon fluorides). Blue glow. "
            "Anesthetic. Spacecraft ion propulsion. Ambient that occasionally "
            "reacts. The noble gas that broke the rules. Spacefaring.",
        },
        # ══════════════════════════════════════════════════════════════
        # PERIOD 6 — Maximum Complexity (Cs through Rn)
        # Lanthanides. Gold. Mercury. Lead. Radon.
        # ══════════════════════════════════════════════════════════════
        {
            "n": 55,
            "title": "Cesium (Cs)",
            "song": "elem_055_Cs",
            "bpm": 88,
            "group": 1,
            "genre": "blues",
            "notes": "Most electropositive. Melts at 28C (room temperature liquid metal). "
            "Atomic clocks (defines the second). Explodes in water spectacularly. "
            "Blues that keeps perfect time while falling apart.",
        },
        {
            "n": 56,
            "title": "Barium (Ba)",
            "song": "elem_056_Ba",
            "bpm": 112,
            "group": 2,
            "genre": "country",
            "notes": "Green flame test. Barium meals (X-ray contrast). Rat poison. "
            "Heavy. Country ballad with toxic undertones. Green-lit stage.",
        },
        # Lanthanides 57-71: classical suite
        {
            "n": 57,
            "title": "Lanthanum (La)",
            "song": "elem_057_La",
            "bpm": 96,
            "group": "lanthanide",
            "genre": "classical",
            "notes": "First lanthanide. Lighter flints. Camera lenses. "
            "Classical overture. The rare earth suite begins. Sets the theme.",
        },
        {
            "n": 58,
            "title": "Cerium (Ce)",
            "song": "elem_058_Ce",
            "bpm": 100,
            "group": "lanthanide",
            "genre": "classical",
            "notes": "Most abundant rare earth. Self-cleaning ovens. Lighter flints. "
            "Classical. Bright, common (for a rare earth), sparking.",
        },
        {
            "n": 59,
            "title": "Praseodymium (Pr)",
            "song": "elem_059_Pr",
            "bpm": 104,
            "group": "lanthanide",
            "genre": "classical",
            "notes": "Green glass. Magnets. Welding goggles. "
            "Classical with green tinted tone. Protective and colorful.",
        },
        {
            "n": 60,
            "title": "Neodymium (Nd)",
            "song": "elem_060_Nd",
            "bpm": 115,
            "group": "lanthanide",
            "genre": "classical",
            "notes": "THE magnet element. Every speaker, every hard drive, every headphone. "
            "Classical that pulls you in. Magnetic. You are listening through "
            "neodymium magnets right now.",
        },
        {
            "n": 61,
            "title": "Promethium (Pm)",
            "song": "elem_061_Pm",
            "bpm": 108,
            "group": "lanthanide",
            "genre": "classical",
            "notes": "Only radioactive lanthanide. Named for Prometheus. No stable isotopes. "
            "Classical that decays. The stolen fire. Each repeat loses a voice.",
        },
        {
            "n": 62,
            "title": "Samarium (Sm)",
            "song": "elem_062_Sm",
            "bpm": 106,
            "group": "lanthanide",
            "genre": "classical",
            "notes": "Magnets (SmCo). Neutron absorber in reactors. "
            "Classical with magnetic pull. Controlled power.",
        },
        {
            "n": 63,
            "title": "Europium (Eu)",
            "song": "elem_063_Eu",
            "bpm": 102,
            "group": "lanthanide",
            "genre": "classical",
            "notes": "Euro banknote anti-counterfeiting (fluoresces red). Named for Europe. "
            "Classical with European grandeur. Authenticating. Red glow.",
        },
        {
            "n": 64,
            "title": "Gadolinium (Gd)",
            "song": "elem_064_Gd",
            "bpm": 110,
            "group": "lanthanide",
            "genre": "classical",
            "notes": "MRI contrast agent. Most magnetic of rare earths. Neutron absorber. "
            "Classical that reveals hidden structure. Diagnostic.",
        },
        {
            "n": 65,
            "title": "Terbium (Tb)",
            "song": "elem_065_Tb",
            "bpm": 105,
            "group": "lanthanide",
            "genre": "classical",
            "notes": "Green phosphor in screens. Named for Ytterby (element 2 of 4). "
            "Classical with green luminescence. Screen glow.",
        },
        {
            "n": 66,
            "title": "Dysprosium (Dy)",
            "song": "elem_066_Dy",
            "bpm": 112,
            "group": "lanthanide",
            "genre": "classical",
            "notes": "Name means 'hard to get.' Magnets. Nuclear reactor control rods. "
            "Classical that plays hard to get. Elusive melody.",
        },
        {
            "n": 67,
            "title": "Holmium (Ho)",
            "song": "elem_067_Ho",
            "bpm": 108,
            "group": "lanthanide",
            "genre": "classical",
            "notes": "Highest magnetic moment of any element. Lasers. Yellow oxide. "
            "Classical with the strongest pull. Maximum magnetic melody.",
        },
        {
            "n": 68,
            "title": "Erbium (Er)",
            "song": "elem_068_Er",
            "bpm": 104,
            "group": "lanthanide",
            "genre": "classical",
            "notes": "Pink glass. Fiber optic amplifiers. Named for Ytterby (3 of 4). "
            "Classical with pink warmth. Amplifying. The signal booster.",
        },
        {
            "n": 69,
            "title": "Thulium (Tm)",
            "song": "elem_069_Tm",
            "bpm": 100,
            "group": "lanthanide",
            "genre": "classical",
            "notes": "Rarest naturally occurring lanthanide. Portable X-ray sources. "
            "Sparse classical. Barely there. The rarest voice in the suite.",
        },
        {
            "n": 70,
            "title": "Ytterbium (Yb)",
            "song": "elem_070_Yb",
            "bpm": 98,
            "group": "lanthanide",
            "genre": "classical",
            "notes": "Named for Ytterby (4 of 4). Atomic clocks. Stress sensors. "
            "Classical that measures its own tempo with atomic precision.",
        },
        {
            "n": 71,
            "title": "Lutetium (Lu)",
            "song": "elem_071_Lu",
            "bpm": 114,
            "group": "lanthanide",
            "genre": "classical",
            "notes": "Last lanthanide. Densest, hardest, highest melting point of the group. "
            "Classical finale. Full orchestra. Maximum density. "
            "The rare earth suite closes with its heaviest member.",
        },
        {
            "n": 72,
            "title": "Hafnium (Hf)",
            "song": "elem_072_Hf",
            "bpm": 158,
            "group": 4,
            "genre": "metal",
            "notes": "Nuclear reactor control rods. Always found with zirconium. "
            "Identical twins, different destiny. Metal with nuclear restraint.",
        },
        {
            "n": 73,
            "title": "Tantalum (Ta)",
            "song": "elem_073_Ta",
            "bpm": 155,
            "group": 5,
            "genre": "metal",
            "notes": "Phone capacitors. Surgical implants. Highly corrosion resistant. "
            "Named for Tantalus. Metal that resists everything. Untouchable.",
        },
        {
            "n": 74,
            "title": "Tungsten (W)",
            "song": "elem_074_W",
            "bpm": 180,
            "group": 6,
            "genre": "metal",
            "origin": "r-process in supernovae and neutron star mergers",
            "stability": "Stable. W-184 (30.6%). 5 stable isotopes.",
            "binding_energy": "8.01 MeV/nucleon",
            "notes": "HIGHEST melting point of ALL elements: 3695 K (3422 C). "
            "Light bulb filaments (Edison chose tungsten because nothing else survives). "
            "Armor-piercing rounds (density 19.3 g/cm3, nearly as dense as gold). "
            "Chemical symbol W from wolfram (German, wolf's cream - it ate tin in smelting). "
            "Mapping: 3695 K melting point = ~195 BPM (near maximum tempo in the album). "
            "5 stable isotopes = 5-part arrangement. "
            "The hardest, most heat-resistant metal track. Maximum sustain. "
            "Notes that refuse to decay. The guitar tone that will not melt.",
        },
        {
            "n": 75,
            "title": "Rhenium (Re)",
            "song": "elem_075_Re",
            "bpm": 170,
            "group": 7,
            "genre": "metal",
            "notes": "Jet engine turbine blades. Fourth highest melting point. "
            "Extremely rare. Metal that flies. Turbine riff. Screaming lead.",
        },
        {
            "n": 76,
            "title": "Osmium (Os)",
            "song": "elem_076_Os",
            "bpm": 165,
            "group": 8,
            "genre": "metal",
            "notes": "Densest naturally occurring element. Blue-silver. Pen tips. "
            "The heaviest metal track by mass. Maximum low-end. "
            "Sub bass so dense it warps spacetime.",
        },
        {
            "n": 77,
            "title": "Iridium (Ir)",
            "song": "elem_077_Ir",
            "bpm": 162,
            "group": 9,
            "genre": "metal",
            "notes": "Most corrosion resistant metal. Asteroid impact layer (K-Pg boundary). "
            "The element that killed the dinosaurs. Metal. Extinction-level riff. "
            "Iridium layer = the breakdown that ended an era.",
        },
        {
            "n": 78,
            "title": "Platinum (Pt)",
            "song": "elem_078_Pt",
            "bpm": 132,
            "group": 10,
            "genre": "big_band",
            "notes": "Catalysts. Jewelry. Record certification (going platinum). "
            "Big band because going platinum means the album succeeded. "
            "Rich, prestigious, the element of achievement.",
        },
        {
            "n": 79,
            "title": "Gold (Au)",
            "song": "elem_079_Au",
            "bpm": 108,
            "group": 11,
            "genre": "big_band",
            "origin": "r-process in neutron star mergers (confirmed by GW170817 in 2017). "
            "Every gold atom on Earth came from colliding neutron stars.",
            "stability": "Stable. Au-197 (100%). Only one stable isotope. Incorruptible.",
            "binding_energy": "7.92 MeV/nucleon (well past the peak, declining)",
            "notes": "THE precious metal. Only one stable isotope (Au-197). Currency for 5000 years. "
            "Does not tarnish, does not corrode, does not react with air or water. "
            "Made in neutron star mergers - confirmed when LIGO detected gravitational waves "
            "from GW170817 and the kilonova afterglow showed gold spectral lines. "
            "Every gold atom on Earth came from dead neutron stars smashing together. "
            "Big band. Brass section (golden horns = literally brass, which is Cu-Zn, not gold, "
            "but the color matches). Rich, warm, eternal. "
            "One stable isotope = one key, no modulation. Stays in Ab major the entire time. "
            "The most noble of the noble metals. Will outlast the sun.",
        },
        {
            "n": 80,
            "title": "Mercury (Hg)",
            "song": "elem_080_Hg",
            "bpm": 140,
            "group": 12,
            "genre": "bossa_nova",
            "notes": "ONLY metal liquid at room temperature. Quicksilver. Thermometers. "
            "Bossa nova because mercury flows. Impossible to hold. "
            "Freddie would approve of the genre choice.",
        },
        {
            "n": 81,
            "title": "Thallium (Tl)",
            "song": "elem_081_Tl",
            "bpm": 80,
            "group": 13,
            "genre": "trip_hop",
            "notes": "The poisoner's poison. Odorless, tasteless, lethal. Detective novels. "
            "Trip-hop. Dark, slow, sinister. Massive Attack energy. "
            "You do not know it is there until it is too late.",
        },
        {
            "n": 82,
            "title": "Lead (Pb)",
            "song": "elem_082_Pb",
            "bpm": 68,
            "group": 14,
            "genre": "doom_metal",
            "origin": "s-process and r-process. End product of multiple radioactive decay chains "
            "(U-238 -> ... -> Pb-206, U-235 -> ... -> Pb-207, Th-232 -> ... -> Pb-208).",
            "stability": "Stable. 4 stable isotopes (204, 206, 207, 208). Pb-208 is doubly magic "
            "(82p, 126n). Lead is where radioactive decay chains END. The final product.",
            "binding_energy": "7.87 MeV/nucleon",
            "notes": "Dense (11.34 g/cm3). Heavy. Toxic (neurotoxin, no safe exposure level). "
            "Radiation shielding. Roman pipes (plumbum -> plumbing). Bullets. Car batteries. "
            "Pb-208 is doubly magic (82 protons, 126 neutrons) = the most stable heavy nucleus. "
            "Lead is where uranium, thorium, and other radioactive elements DECAY TO. "
            "It is the graveyard of radioactive decay chains. The final resting place. "
            "The SLOWEST, HEAVIEST track. Doom metal. Down-tuned to Drop A. "
            "Maximum bass (atomic mass 207.2 = maximum low-end weight). Minimum tempo. "
            "4 stable isotopes = 4 grinding doom riffs. "
            "Lead is the opposite of helium in every measurable way. This track proves it.",
        },
        {
            "n": 83,
            "title": "Bismuth (Bi)",
            "song": "elem_083_Bi",
            "bpm": 95,
            "group": 15,
            "genre": "jazz",
            "origin": "r-process in supernovae and neutron star mergers",
            "stability": "Once thought stable. Actually radioactive: half-life 1.9 x 10^19 years "
            "(1.4 billion times the age of the universe). The LAST 'effectively stable' element.",
            "binding_energy": "7.85 MeV/nucleon (declining from iron's peak, but still bound)",
            "notes": "Rainbow oxidation crystals (staircase-shaped hopper crystals). Pepto-Bismol. "
            "Least toxic heavy metal. Element 83 is the last stop before everything is "
            "permanently radioactive. Bi-209 was considered the heaviest stable isotope "
            "until 2003, when its alpha decay was measured: half-life of 1.9 x 10^19 years. "
            "That is so long it functionally does not matter - but it IS decaying. "
            "The beautiful one. Jazz with iridescent harmony. Staircase crystals = "
            "staircase chord voicings that ascend chromatically. "
            "The last element with clean audio. After bismuth, every track has audible "
            "decay artifacts. This is the final sunset before the radioactive night.",
        },
        {
            "n": 84,
            "title": "Polonium (Po)",
            "song": "elem_084_Po",
            "bpm": 92,
            "group": 16,
            "genre": "neo_soul",
            "notes": "Discovered by Marie Curie. Named for Poland. Extremely radioactive. "
            "Used to assassinate Alexander Litvinenko. Neo-soul with danger underneath. "
            "Beautiful surface, lethal core.",
        },
        {
            "n": 85,
            "title": "Astatine (At)",
            "song": "elem_085_At",
            "bpm": 160,
            "group": 17,
            "genre": "punk",
            "notes": "Rarest naturally occurring element. Less than 30g on entire Earth. "
            "Halogen but barely exists. Punk that is over before you notice it. "
            "30 seconds. Gone.",
        },
        {
            "n": 86,
            "title": "Radon (Rn)",
            "song": "elem_086_Rn",
            "bpm": 58,
            "group": 18,
            "genre": "ambient",
            "notes": "Radioactive noble gas. Seeps from the ground. Invisible. Odorless. "
            "Second leading cause of lung cancer. Ambient that is dangerous to sit in. "
            "The gas in your basement you should test for.",
        },
        # ══════════════════════════════════════════════════════════════
        # PERIOD 7 — Extreme Territory (Fr through Og)
        # Actinides. Synthetic elements. Increasing instability.
        # The tracks get shorter as half-lives get shorter.
        # ══════════════════════════════════════════════════════════════
        {
            "n": 87,
            "title": "Francium (Fr)",
            "song": "elem_087_Fr",
            "bpm": 95,
            "group": 1,
            "genre": "blues",
            "notes": "Most unstable naturally occurring element. 22-minute half-life. "
            "Most electropositive. Would explode harder than any alkali metal "
            "if you could collect enough. Blues that decays in real time.",
        },
        {
            "n": 88,
            "title": "Radium (Ra)",
            "song": "elem_088_Ra",
            "bpm": 100,
            "group": 2,
            "genre": "country",
            "notes": "Marie Curie's element. Glows blue-green. Watch dials (Radium Girls). "
            "Country with a glow-in-the-dark quality. Beautiful, deadly history.",
        },
        # Actinides 89-103: orchestral/epic suite
        {
            "n": 89,
            "title": "Actinium (Ac)",
            "song": "elem_089_Ac",
            "bpm": 108,
            "group": "actinide",
            "genre": "orchestral",
            "notes": "First actinide. Glows blue (Cherenkov radiation). Cancer therapy. "
            "Orchestral overture for the radioactive suite. Blue glow. Powerful.",
        },
        {
            "n": 90,
            "title": "Thorium (Th)",
            "song": "elem_090_Th",
            "bpm": 120,
            "group": "actinide",
            "genre": "orchestral",
            "notes": "Named for Thor. Proposed nuclear fuel (safer than uranium). "
            "Orchestral. Thunder god energy. Power waiting to be harnessed.",
        },
        {
            "n": 91,
            "title": "Protactinium (Pa)",
            "song": "elem_091_Pa",
            "bpm": 115,
            "group": "actinide",
            "genre": "orchestral",
            "notes": "Rare, radioactive, toxic. Proto-actinium. The precursor. "
            "Orchestral building tension. Something bigger is coming.",
        },
        {
            "n": 92,
            "title": "Uranium (U)",
            "song": "elem_092_U",
            "bpm": 175,
            "group": "actinide",
            "genre": "orchestral",
            "origin": "r-process in supernovae. Every atom on Earth is from a dead star.",
            "stability": "U-238 half-life: 4.468 billion years (roughly age of Earth). "
            "U-235 half-life: 703.8 million years. U-235 is fissile (chain reactions).",
            "binding_energy": "7.57 MeV/nucleon (past the peak, wants to split)",
            "notes": "The element that changed history. U-235 undergoes fission when struck by a "
            "neutron: 235U + n -> 141Ba + 92Kr + 3n + 200 MeV. Those 3 neutrons hit 3 more "
            "uranium atoms. Chain reaction. Controlled = 440 nuclear reactors powering 10% of "
            "world electricity. Uncontrolled = 15 kilotons over Hiroshima. "
            "Full orchestra + full metal band. The most dynamically extreme track in the "
            "actinide suite. Starts pp (fuel rods in water). Controlled crescendo through the "
            "fission chain (each generation of neutrons adds instruments). "
            "But the dynamics have two endings: the controlled version plateaus at ff "
            "(steady-state reactor). The uncontrolled version hits ffff and clips. "
            "Both endings are in the track. The listener chooses which to hear.",
        },
        {
            "n": 93,
            "title": "Neptunium (Np)",
            "song": "elem_093_Np",
            "bpm": 130,
            "group": "actinide",
            "genre": "orchestral",
            "notes": "First transuranic element. Nuclear waste. Named for Neptune. "
            "Orchestral with oceanic depth. The byproduct nobody wanted.",
        },
        {
            "n": 94,
            "title": "Plutonium (Pu)",
            "song": "elem_094_Pu",
            "bpm": 200,
            "group": "actinide",
            "genre": "djent",
            "origin": "Reactor: U-238 + n -> U-239 -> Np-239 -> Pu-239. 100% manufactured.",
            "stability": "Pu-239: t1/2 = 24,110 yr. Pu-244: t1/2 = 80.8M yr. "
            "Critical mass: 11 kg sphere. Fat Man used 6.2 kg.",
            "binding_energy": "7.56 MeV/nucleon",
            "notes": "Named for Pluto, god of death (following U=Uranus, Np=Neptune). "
            "11 kg sphere = critical mass = nuclear detonation. "
            "Warm to the touch from alpha decay. 6 allotropes (most of any element) = 6 sections. "
            "Djent. Polyrhythmic. Precision is not optional - wrong mass = bomb vs reactor. "
            "The most dangerous element as the most precise music.",
        },
        {
            "n": 95,
            "title": "Americium (Am)",
            "song": "elem_095_Am",
            "bpm": 120,
            "group": "actinide",
            "genre": "country",
            "notes": "In every smoke detector. Named for America. "
            "Country because it is in every American home. "
            "Quietly saving lives from your ceiling.",
        },
        {
            "n": 96,
            "title": "Curium (Cm)",
            "song": "elem_096_Cm",
            "bpm": 110,
            "group": "actinide",
            "genre": "classical",
            "notes": "Named for Marie and Pierre Curie. Glows purple. Mars rovers. "
            "Classical tribute to the Curies. Purple glow. Scientific nobility.",
        },
        {
            "n": 97,
            "title": "Berkelium (Bk)",
            "song": "elem_097_Bk",
            "bpm": 125,
            "group": "actinide",
            "genre": "funk",
            "notes": "Named for Berkeley, California. Produced in microgram quantities. "
            "Bay Area funk. Atomic 510 area code energy.",
        },
        {
            "n": 98,
            "title": "Californium (Cf)",
            "song": "elem_098_Cf",
            "bpm": 128,
            "group": "actinide",
            "genre": "electronic",
            "notes": "Named for California. Neutron source. Portable nuclear reactor. "
            "West coast electronic. Gold Rush energy. Expensive ($27M per gram).",
        },
        {
            "n": 99,
            "title": "Einsteinium (Es)",
            "song": "elem_099_Es",
            "bpm": 140,
            "group": "actinide",
            "genre": "prog_metal",
            "notes": "Named for Einstein. Discovered in nuclear fallout (H-bomb debris). "
            "Genius forged in destruction. Prog metal. Complex, brilliant, born from violence.",
        },
        {
            "n": 100,
            "title": "Fermium (Fm)",
            "song": "elem_100_Fm",
            "bpm": 135,
            "group": "actinide",
            "genre": "fusion",
            "notes": "Named for Enrico Fermi. Also discovered in H-bomb debris. "
            "Fusion (genre and nuclear). The father of the reactor.",
        },
        {
            "n": 101,
            "title": "Mendelevium (Md)",
            "song": "elem_101_Md",
            "bpm": 110,
            "group": "actinide",
            "genre": "classical",
            "notes": "Named for Mendeleev (periodic table creator). "
            "Classical. THE element that honors the man who organized all the others. "
            "A theme that references every previous track.",
        },
        {
            "n": 102,
            "title": "Nobelium (No)",
            "song": "elem_102_No",
            "bpm": 100,
            "group": "actinide",
            "genre": "ambient",
            "notes": "Named for Alfred Nobel. Half-life: 58 minutes. "
            "Ambient. Peaceful. The dynamite inventor's redemption. "
            "The Nobel Peace Prize as music.",
        },
        {
            "n": 103,
            "title": "Lawrencium (Lr)",
            "song": "elem_103_Lr",
            "bpm": 105,
            "group": "actinide",
            "genre": "orchestral",
            "notes": "Last actinide. Named for Ernest Lawrence (cyclotron inventor). "
            "Orchestral finale for the actinide suite. The particle accelerator closes.",
        },
        # Transactinides 104-118: increasingly unstable, tracks get shorter
        {
            "n": 104,
            "title": "Rutherfordium (Rf)",
            "song": "elem_104_Rf",
            "bpm": 160,
            "group": 4,
            "genre": "metal",
            "notes": "Named for Rutherford. Half-life: 1.3 hours. Synthetic. "
            "Metal that decays. 90 seconds long. Fading.",
        },
        {
            "n": 105,
            "title": "Dubnium (Db)",
            "song": "elem_105_Db",
            "bpm": 155,
            "group": 5,
            "genre": "metal",
            "notes": "Named for Dubna, Russia. Half-life: 28 hours. Cold War element. "
            "Soviet-American metal. 80 seconds.",
        },
        {
            "n": 106,
            "title": "Seaborgium (Sg)",
            "song": "elem_106_Sg",
            "bpm": 150,
            "group": 6,
            "genre": "metal",
            "notes": "Named for Glenn Seaborg (only living person with an element). "
            "Half-life: 2.4 minutes. Metal tribute. 70 seconds.",
        },
        {
            "n": 107,
            "title": "Bohrium (Bh)",
            "song": "elem_107_Bh",
            "bpm": 165,
            "group": 7,
            "genre": "metal",
            "notes": "Named for Niels Bohr. Half-life: 61 seconds. "
            "Quantum metal. 60 seconds. Probability cloud riff.",
        },
        {
            "n": 108,
            "title": "Hassium (Hs)",
            "song": "elem_108_Hs",
            "bpm": 170,
            "group": 8,
            "genre": "metal",
            "notes": "Named for Hesse, Germany. Half-life: 16 seconds. "
            "Metal. 45 seconds. Accelerating decay.",
        },
        {
            "n": 109,
            "title": "Meitnerium (Mt)",
            "song": "elem_109_Mt",
            "bpm": 175,
            "group": 9,
            "genre": "metal",
            "notes": "Named for Lise Meitner (nuclear fission, robbed of Nobel Prize). "
            "Metal tribute to an overlooked genius. 40 seconds. Justice unserved.",
        },
        {
            "n": 110,
            "title": "Darmstadtium (Ds)",
            "song": "elem_110_Ds",
            "bpm": 180,
            "group": 10,
            "genre": "metal",
            "notes": "Half-life: 14 seconds. Named for Darmstadt. "
            "Speed metal. 35 seconds. Fragmenting.",
        },
        {
            "n": 111,
            "title": "Roentgenium (Rg)",
            "song": "elem_111_Rg",
            "bpm": 185,
            "group": 11,
            "genre": "metal",
            "notes": "Named for Roentgen (X-rays). Half-life: 26 seconds. "
            "Metal that sees through you. 30 seconds. X-ray vision.",
        },
        {
            "n": 112,
            "title": "Copernicium (Cn)",
            "song": "elem_112_Cn",
            "bpm": 190,
            "group": 12,
            "genre": "electronic",
            "notes": "Named for Copernicus. Half-life: 29 seconds. "
            "Electronic. The heliocentric element. Everything revolves. 28 seconds.",
        },
        {
            "n": 113,
            "title": "Nihonium (Nh)",
            "song": "elem_113_Nh",
            "bpm": 180,
            "group": 13,
            "genre": "electronic",
            "notes": "Named for Japan (Nihon). Half-life: 20 seconds. "
            "First element named for an East Asian country. "
            "J-electronic. Precision. 25 seconds.",
        },
        {
            "n": 114,
            "title": "Flerovium (Fl)",
            "song": "elem_114_Fl",
            "bpm": 185,
            "group": 14,
            "genre": "electronic",
            "notes": "Named for Flerov. Half-life: 2.1 seconds. Island of stability candidate. "
            "Electronic pulse. 20 seconds. Barely stable.",
        },
        {
            "n": 115,
            "title": "Moscovium (Mc)",
            "song": "elem_115_Mc",
            "bpm": 190,
            "group": 15,
            "genre": "electronic",
            "notes": "Named for Moscow. Half-life: 0.65 seconds. "
            "Electronic burst. 15 seconds. Disintegrating.",
        },
        {
            "n": 116,
            "title": "Livermorium (Lv)",
            "song": "elem_116_Lv",
            "bpm": 195,
            "group": 16,
            "genre": "electronic",
            "notes": "Named for Livermore, California. Half-life: 57 milliseconds. "
            "Electronic glitch. 10 seconds. Almost gone.",
        },
        {
            "n": 117,
            "title": "Tennessine (Ts)",
            "song": "elem_117_Ts",
            "bpm": 200,
            "group": 17,
            "genre": "punk",
            "notes": "Named for Tennessee. Half-life: 51 milliseconds. Halogen that barely exists. "
            "5-second punk blast. The fastest, shortest track. "
            "Blink and you missed it. The decay catches the sound.",
        },
        {
            "n": 118,
            "title": "Oganesson (Og)",
            "song": "elem_118_Og",
            "bpm": 60,
            "group": 18,
            "genre": "ambient",
            "origin": "Particle accelerator: 249Cf + 48Ca -> 294Og + 3n. Created ONE ATOM AT A TIME.",
            "stability": "Half-life: 0.69 milliseconds. 5 atoms ever confirmed. "
            "Predicted to be a solid at room temp despite being a 'noble gas' "
            "(relativistic electron effects collapse the outer shell).",
            "binding_energy": "~7.1 MeV/nucleon (estimated, barely bound)",
            "notes": "Last element. End of the periodic table. End of stable matter. End of the album. "
            "Created by bombarding californium-249 with calcium-48 ions at Dubna. "
            "Five atoms have ever existed. Each lasted less than a millisecond. "
            "Theoretically a noble gas but relativistic effects on its electrons mean it "
            "might actually be a solid - we have never had enough atoms to check. "
            "The album ends with a single synthesized tone at the element's predicted "
            "emission frequency. The tone lasts 0.69 milliseconds. Then silence. "
            "The bit depth has been decreasing since element 104. By now it is 1-bit. "
            "The sample rate has dropped to near-nothing. The last sound is a square wave "
            "at minimum resolution that clicks once and stops. "
            "The periodic table dissolves into nothing. We have run out of stable "
            "configurations of protons and neutrons. The silence after this track is "
            "the silence at the edge of physics. There is no element 119. Not yet.",
        },
        # ══════════════════════════════════════════════════════════════
        # COMPOUNDS AND REACTIONS
        # Every formula verified. Every property real. Bond types drive
        # how the element themes combine (see mapping system #11).
        # ══════════════════════════════════════════════════════════════
        # ── Covalent compounds (nonmetal + nonmetal: themes merge) ────
        {
            "n": "C01",
            "title": "H2O - Water",
            "song": "compound_H2O",
            "bpm": 90,
            "group": "compound",
            "genre": "bossa_nova",
            "bond": "covalent (polar)",
            "mp": "273 K",
            "bp": "373 K",
            "notes": "2H + O -> H2O. Polar covalent. Bent geometry (104.5 degree bond angle). "
            "Universal solvent. Hydrogen ambient + Oxygen neo-soul merge into flowing bossa. "
            "The bent bond angle = a melodic phrase that bends and returns. "
            "Cohesion (hydrogen bonding) = motifs that connect across sections. "
            "Three atoms, two bonds, one molecule that makes life possible.",
        },
        {
            "n": "C02",
            "title": "CO2 - Carbon Dioxide",
            "song": "compound_CO2",
            "bpm": 95,
            "group": "compound",
            "genre": "neo_soul",
            "bond": "covalent (double bonds)",
            "mp": "194.7 K (sublimes)",
            "notes": "C + 2O -> CO2. Linear geometry (180 degrees). Double bonds on each side. "
            "Carbon funk + Oxygen neo-soul = greenhouse groove. "
            "Sublimes directly from solid to gas (dry ice) = the track skips "
            "from sparse to full with no transition. Temperature rises through the arrangement. "
            "Symmetrical molecule = palindromic melody.",
        },
        {
            "n": "C03",
            "title": "CH4 - Methane",
            "song": "compound_CH4",
            "bpm": 100,
            "group": "compound",
            "genre": "funk",
            "bond": "covalent (nonpolar)",
            "mp": "90.7 K",
            "bp": "111.7 K",
            "notes": "C + 4H -> CH4. Tetrahedral geometry (109.5 degrees). Simplest hydrocarbon. "
            "Natural gas. Swamp gas. Cow farts. Carbon funk at its most basic. "
            "4 equivalent C-H bonds = 4/4 time, perfectly symmetrical groove. "
            "Nonpolar = no tension in the harmony. Pure consonant funk.",
        },
        {
            "n": "C04",
            "title": "NH3 - Ammonia",
            "song": "compound_NH3",
            "bpm": 138,
            "group": "compound",
            "genre": "jazz",
            "bond": "covalent (polar)",
            "mp": "195.4 K",
            "bp": "239.8 K",
            "notes": "N + 3H -> NH3. Trigonal pyramidal (107.8 degrees). Strong base. "
            "Pungent smell that hits you. Nitrogen jazz + Hydrogen ambient. "
            "The lone pair on nitrogen = a rest in the melody that changes everything. "
            "Pyramidal shape = ascending chord voicing (root-3rd-5th-space).",
        },
        {
            "n": "C05",
            "title": "C2H5OH - Ethanol",
            "song": "compound_C2H5OH",
            "bpm": 120,
            "group": "compound",
            "genre": "ska",
            "bond": "covalent (hydrogen bonding)",
            "mp": "159 K",
            "bp": "351.4 K",
            "notes": "2C + 6H + O -> C2H5OH. The drinking alcohol. Fermentation product. "
            "Carbon funk + Hydrogen ambient + Oxygen neo-soul = party ska. "
            "Hydrogen bonding with water = miscible = the genres blend completely. "
            "The OH group = the hook that makes it mix. Timing gets progressively "
            "sloppier as the track goes on. The wobble is ethanol doing its job.",
        },
        {
            "n": "C06",
            "title": "H2SO4 - Sulfuric Acid",
            "song": "compound_H2SO4",
            "bpm": 155,
            "group": "compound",
            "genre": "metal",
            "bond": "covalent (strong acid)",
            "mp": "283.5 K",
            "bp": "610 K",
            "notes": "2H + S + 4O -> H2SO4. King of chemicals. Most produced industrial chemical. "
            "Dehydrates organic matter on contact (turns sugar black). "
            "Sulfur blues + Oxygen neo-soul + Hydrogen ambient = corrosive metal. "
            "The arrangement strips instruments away one by one (dehydration). "
            "Exothermic when mixed with water = the track gets louder if you add reverb.",
        },
        {
            "n": "C07",
            "title": "O3 - Ozone",
            "song": "compound_O3",
            "bpm": 82,
            "group": "compound",
            "genre": "ambient",
            "bond": "covalent (resonance)",
            "mp": "80.2 K",
            "bp": "161.3 K",
            "notes": "3O -> O3. Three oxygens. Resonance structure (bonds alternate). "
            "UV shield at 20-30 km altitude. Sharp smell after lightning. "
            "Oxygen neo-soul tripled = ambient protection. The ozone layer is "
            "a thin shield of sound protecting everything beneath it. "
            "Resonance = the chord voicing oscillates between two forms.",
        },
        {
            "n": "C08",
            "title": "C6H12O6 - Glucose",
            "song": "compound_C6H12O6",
            "bpm": 135,
            "group": "compound",
            "genre": "funk",
            "bond": "covalent (ring structure)",
            "mp": "423 K (decomposes)",
            "notes": "6C + 12H + 6O -> C6H12O6. Blood sugar. Cellular fuel. Photosynthesis product. "
            "Six carbons in a ring = 6/8 time signature, cycling groove. "
            "C-H-O ratio of 1:2:1 = rhythmic ratio of the layers. "
            "Energy source of all life = the funk that powers the album. "
            "Ring structure = the melody loops back to where it started.",
        },
        {
            "n": "C09",
            "title": "C8H10N4O2 - Caffeine",
            "song": "compound_C8H10N4O2",
            "bpm": 168,
            "group": "compound",
            "genre": "bebop",
            "bond": "covalent (fused ring)",
            "mp": "508 K (sublimes)",
            "notes": "8C + 10H + 4N + 2O -> C8H10N4O2. The real fuel. Adenosine receptor antagonist. "
            "Carbon funk + Nitrogen jazz + Oxygen neo-soul at SPEED. "
            "Fused purine ring = interlocking polyrhythmic layers. "
            "4 nitrogen atoms = 4 jazz horn voices in the arrangement. "
            "Blocks adenosine (sleepiness) = the track refuses to slow down. "
            "Half-life 5 hours = the energy sustains for exactly that long.",
        },
        {
            "n": "C10",
            "title": "SiO2 - Silicon Dioxide",
            "song": "compound_SiO2",
            "bpm": 128,
            "group": "compound",
            "genre": "electronic",
            "bond": "covalent network (giant structure)",
            "mp": "1986 K",
            "notes": "Si + 2O -> SiO2. Quartz. Sand. Glass. 60% of Earth's crust. "
            "Silicon electronic + Oxygen neo-soul = crystalline electronic. "
            "Network covalent = every atom bonded to every neighbor = every "
            "track element connected to every other. No isolated parts. "
            "Piezoelectric (quartz oscillators keep time) = the master clock. "
            "Amorphous form = glass = transparent arrangement you can see through.",
        },
        {
            "n": "C11",
            "title": "N2O - Nitrous Oxide",
            "song": "compound_N2O",
            "bpm": 145,
            "group": "compound",
            "genre": "jazz",
            "bond": "covalent (linear)",
            "mp": "182.3 K",
            "bp": "184.7 K",
            "notes": "2N + O -> N2O. Laughing gas. Dental anesthetic. Whipped cream propellant. "
            "Nitro boost in engines. Nitrogen jazz + Oxygen neo-soul = giddy jazz. "
            "Linear molecule = straight-ahead bebop. The track is funny. "
            "Literally causes euphoria. The harmony gets increasingly silly.",
        },
        {
            "n": "C12",
            "title": "C2H4 - Ethylene",
            "song": "compound_C2H4",
            "bpm": 108,
            "group": "compound",
            "genre": "funk",
            "bond": "covalent (double bond, planar)",
            "mp": "104 K",
            "bp": "169.4 K",
            "notes": "2C + 4H -> C2H4. Plant hormone that ripens fruit. One banana ripens the bag. "
            "Simplest alkene (double bond). Planar geometry. "
            "Carbon funk with double-time feel on the double bond. "
            "Catalyzes change in everything around it = the groove infects other tracks.",
        },
        # ── Ionic compounds (metal + nonmetal: themes contrast) ───────
        {
            "n": "C13",
            "title": "NaCl - Sodium Chloride (Table Salt)",
            "song": "compound_NaCl",
            "bpm": 110,
            "group": "compound",
            "genre": "blues",
            "bond": "ionic",
            "mp": "1074 K",
            "bp": "1686 K",
            "notes": "Na+ + Cl- -> NaCl. Ionic bond. FCC crystal lattice. "
            "Sodium blues + Chlorine punk = salt blues. Opposites attracting. "
            "Ionic bond = call-and-response (Na theme, Cl response, never blending). "
            "Cubic crystal = strict 4/4 grid. Essential for nerve impulses. "
            "Dissolves in water (ions separate) = when reverb is added, the two "
            "themes drift apart. Salt is tears. The oldest seasoning. The first trade good.",
        },
        {
            "n": "C14",
            "title": "CaCO3 - Calcium Carbonate",
            "song": "compound_CaCO3",
            "bpm": 105,
            "group": "compound",
            "genre": "country",
            "bond": "ionic + covalent",
            "mp": "1098 K (decomposes to CaO + CO2)",
            "notes": "Ca2+ + CO3(2-) -> CaCO3. Limestone. Marble. Chalk. Seashells. Eggshells. "
            "Calcium country + Carbon funk = fossil country. "
            "Ionic between Ca and carbonate, covalent within carbonate. "
            "Decomposes to quicklime (CaO) + CO2 when heated = the country track "
            "breaks into two separate songs at the bridge. The Parthenon is made of this.",
        },
        {
            "n": "C15",
            "title": "KNO3 - Potassium Nitrate",
            "song": "compound_KNO3",
            "bpm": 170,
            "group": "compound",
            "genre": "metal",
            "bond": "ionic",
            "mp": "607 K (decomposes)",
            "notes": "K+ + NO3- -> KNO3. Saltpeter. Gunpowder component (75%). Fertilizer. "
            "Potassium blues + Nitrogen jazz + Oxygen neo-soul = explosive metal. "
            "Oxidizer = feeds fire = the arrangement gets more intense when other "
            "instruments enter. Used in gunpowder since the 9th century. "
            "Deflagration (fast burn, not detonation) = accelerando, not a wall of sound.",
        },
        {
            "n": "C16",
            "title": "NaOH - Sodium Hydroxide (Lye)",
            "song": "compound_NaOH",
            "bpm": 125,
            "group": "compound",
            "genre": "blues",
            "bond": "ionic",
            "mp": "596 K",
            "bp": "1661 K",
            "notes": "Na+ + OH- -> NaOH. Strong base. Saponification (makes soap from fat). "
            "Drain cleaner. Sodium blues + Oxygen neo-soul + Hydrogen ambient. "
            "Caustic = the blues hurts. Exothermic dissolving = heat builds. "
            "Makes soap = takes something dirty and makes it clean. "
            "The blues that purifies.",
        },
        {
            "n": "C17",
            "title": "HCl - Hydrochloric Acid",
            "song": "compound_HCl",
            "bpm": 165,
            "group": "compound",
            "genre": "punk",
            "bond": "covalent (strong acid, ionizes completely in water)",
            "notes": "H + Cl -> HCl. Stomach acid (pH 1.5-3.5). Muriatic acid. "
            "Hydrogen ambient + Chlorine punk = acid punk. "
            "Monoprotic (donates one H+) = one-note riff, pounding. "
            "Complete dissociation in water = the themes split entirely. "
            "Your stomach makes this. You are a chemical factory.",
        },
        # ── Metallic alloys (metal + metal: themes layer additively) ──
        {
            "n": "C18",
            "title": "Fe-C (0.2-2.1%) - Steel",
            "song": "compound_steel",
            "bpm": 160,
            "group": "compound",
            "genre": "melodic_metalcore",
            "bond": "metallic (interstitial alloy)",
            "mp": "~1700 K",
            "notes": "Fe + C (0.2-2.1% by mass) -> steel. Carbon atoms fit in the gaps between "
            "iron atoms (interstitial). Not a compound, an alloy. The carbon distorts "
            "the iron lattice, preventing dislocation movement = hardness. "
            "Iron metalcore + Carbon funk = steel metalcore with groove. "
            "Themes layer additively (metallic bond). The carbon funk rhythm sits "
            "INSIDE the iron riff. Skyscrapers, bridges, railways, civilization.",
        },
        {
            "n": "C19",
            "title": "Cu3Sn + Cu6Sn5 - Bronze",
            "song": "compound_bronze",
            "bpm": 130,
            "group": "compound",
            "genre": "fusion",
            "bond": "metallic (substitutional alloy)",
            "mp": "~1223 K",
            "notes": "Cu + Sn (typically 88% Cu, 12% Sn) -> bronze. Substitutional alloy "
            "(tin atoms replace copper atoms in the lattice). "
            "Copper fusion + Tin ska = bronze fusion. Themes substitute for each other. "
            "Harder than either component alone = the combined track hits harder. "
            "Bells, statues, ship propellers. The Bronze Age. "
            "The alloy that ended stone tools and started civilization.",
        },
        {
            "n": "C20",
            "title": "Au-Ag (20-80%) - Electrum",
            "song": "compound_electrum",
            "bpm": 120,
            "group": "compound",
            "genre": "big_band",
            "bond": "metallic (solid solution)",
            "mp": "~1273 K",
            "notes": "Au + Ag (naturally occurring, typically 20-80% Au). Solid solution alloy. "
            "First coins ever minted (Lydia, 600 BCE). "
            "Gold big band + Silver smooth jazz = electrum big band with smooth edges. "
            "Both noble metals, both Group 11, same key signature (Ab major). "
            "The themes are already harmonically compatible. Currency. Power. History.",
        },
        {
            "n": "C21",
            "title": "Fe-Cr-Ni - Stainless Steel (Type 304)",
            "song": "compound_stainless",
            "bpm": 155,
            "group": "compound",
            "genre": "metal",
            "bond": "metallic (ternary alloy)",
            "mp": "~1700 K",
            "notes": "Fe (66-74%) + Cr (18-20%) + Ni (8-10.5%) -> 304 stainless steel. "
            "Chromium forms Cr2O3 passive layer (self-healing oxide film). "
            "Iron metalcore + Chromium metal + Nickel metal = three guitar tracks "
            "layered. The chromium part acts as a protective overdub that prevents "
            "the iron from rusting (distortion from degrading). "
            "Surgical instruments, kitchen sinks, skyscrapers. Incorruptible.",
        },
        {
            "n": "C22",
            "title": "Cu-Zn (15-40% Zn) - Brass",
            "song": "compound_brass",
            "bpm": 145,
            "group": "compound",
            "genre": "big_band",
            "bond": "metallic (substitutional alloy)",
            "mp": "~1173-1223 K",
            "notes": "Cu + Zn -> brass. THE music alloy. Trumpets, trombones, tubas, saxophones. "
            "Copper fusion + Zinc ska = brass big band. This is the only compound "
            "track where the alloy IS a musical instrument. The horn section "
            "plays instruments literally made of the compound being described. "
            "Self-referential. Beautiful. The compound that makes music.",
        },
        # ── Molecular/organic (complex covalent) ──────────────────────
        {
            "n": "C23",
            "title": "FeS2 - Iron Pyrite (Fool's Gold)",
            "song": "compound_FeS2",
            "bpm": 140,
            "group": "compound",
            "genre": "blues",
            "bond": "ionic/covalent (S-S bond within S2(2-))",
            "mp": "873 K (decomposes)",
            "notes": "Fe2+ + S2(2-) -> FeS2. Fool's gold. Looks like gold but is not. "
            "Iron metalcore + Sulfur blues = deceptive blues. "
            "The track SOUNDS like the Gold (Au) track but it is not. Same key, "
            "similar melody, but wrong instrument, wrong voicing. The imposter. "
            "Strikes sparks when hit with steel = percussion accents on impact.",
        },
        {
            "n": "C24",
            "title": "C12H22O11 - Sucrose (Table Sugar)",
            "song": "compound_sucrose",
            "bpm": 125,
            "group": "compound",
            "genre": "funk",
            "bond": "covalent (glycosidic bond between glucose + fructose)",
            "notes": "12C + 22H + 11O -> C12H22O11. Glucose + Fructose linked by glycosidic bond. "
            "Disaccharide. Carbon funk at its sweetest. "
            "Two ring structures (glucose + fructose) = two interlocking groove loops. "
            "Hydrolysis breaks it into components = bridge section splits the groove. "
            "Caramelizes at 459 K = warm overdrive at the climax. "
            "The most popular molecule on Earth after water.",
        },
        {
            "n": "C25",
            "title": "NaHCO3 + CH3COOH -> CO2 + H2O + NaCH3COO",
            "song": "compound_volcano",
            "bpm": 175,
            "group": "compound",
            "genre": "metal",
            "bond": "acid-base reaction (proton transfer)",
            "notes": "Sodium bicarbonate + acetic acid -> carbon dioxide + water + sodium acetate. "
            "The baking soda volcano. REAL reaction, properly balanced. "
            "Acid-base neutralization releases CO2 gas (the bubbles). "
            "Builds pressure as reactants accumulate. Crescendo. ERUPTION at the "
            "moment of mixing. Then the products settle: CO2 escapes (ambient fade), "
            "water remains (bossa undertone), sodium acetate crystalizes (clean piano). "
            "Every kid's first chemistry experiment. Still satisfying.",
        },
        {
            "n": "C26",
            "title": "2H2 + O2 -> 2H2O (Combustion)",
            "song": "compound_combustion",
            "bpm": 185,
            "group": "compound",
            "genre": "metal",
            "bond": "exothermic reaction (572 kJ/mol)",
            "notes": "Hydrogen combustion. The reaction that powers rockets (Space Shuttle main engines). "
            "2 moles H2 + 1 mole O2 -> 2 moles H2O + 572 kJ of energy. "
            "Hydrogen ambient EXPLODES into Oxygen neo-soul = water bossa... eventually. "
            "But the reaction itself is violent metal. Flame temp 3073 K. "
            "The product is peaceful (water). The process is not. "
            "Clean energy: the only exhaust is water vapor.",
        },
        {
            "n": "C27",
            "title": "6CO2 + 6H2O -> C6H12O6 + 6O2 (Photosynthesis)",
            "song": "compound_photosynthesis",
            "bpm": 108,
            "group": "compound",
            "genre": "ambient",
            "bond": "endothermic (light-driven, 2803 kJ/mol input)",
            "notes": "THE reaction. Sunlight + carbon dioxide + water -> glucose + oxygen. "
            "Requires 2803 kJ/mol of light energy (680 nm red + 430 nm blue photons). "
            "CO2 neo-soul + H2O bossa + LIGHT = glucose funk + oxygen neo-soul. "
            "Endothermic = the track absorbs energy (starts quiet, needs input to grow). "
            "Chlorophyll absorbs red and blue, reflects green = green-tinted mix. "
            "The reaction that makes Earth habitable. The foundation of all food chains.",
        },
        {
            "n": "C28",
            "title": "2Na + 2H2O -> 2NaOH + H2 (Alkali + Water)",
            "song": "compound_na_water",
            "bpm": 170,
            "group": "compound",
            "genre": "metal",
            "bond": "single displacement (exothermic, violent)",
            "notes": "Sodium in water. The YouTube reaction. Exothermic, produces hydrogen gas "
            "which ignites from the heat. Na blues + H2O bossa = explosion metal. "
            "VIOLENTLY exothermic. The sodium catches fire on the water surface. "
            "Bigger alkali metals = bigger explosion (Cs > Rb > K > Na > Li). "
            "The track starts as a gentle blues ballad, then WATER ENTERS and everything "
            "detonates. The louder the alkali metal's blues, the bigger the boom.",
        },
        {
            "n": "C29",
            "title": "4Fe + 3O2 -> 2Fe2O3 (Rusting)",
            "song": "compound_rust",
            "bpm": 72,
            "group": "compound",
            "genre": "blues",
            "bond": "oxidation (slow, requires water catalyst)",
            "mp": "1839 K",
            "notes": "Iron oxidation. SLOW reaction (days to years, requires moisture). "
            "4 atoms of iron + 3 molecules of oxygen = 2 units of rust. "
            "Iron metalcore SLOWLY degrades into blues. The guitar distortion "
            "decreases 1% per bar over the entire track. By the end, the metal "
            "tone is pure clean blues. Entropy wins. Time corrodes everything. "
            "Water is the catalyst = reverb accelerates the degradation.",
        },
        {
            "n": "C30",
            "title": "2Mg + O2 -> 2MgO (Magnesium Burning)",
            "song": "compound_mg_burn",
            "bpm": 160,
            "group": "compound",
            "genre": "country",
            "bond": "combustion (exothermic, 601.6 kJ/mol)",
            "mp": "3125 K product",
            "notes": "Magnesium + oxygen = magnesium oxide. Burns at 3100 K with blinding white light. "
            "So bright you can not look at it. Camera flash bulbs. Incendiary. "
            "Magnesium country + Oxygen neo-soul = white-hot country. "
            "The brightest, loudest moment in the country suite. Every instrument at FF. "
            "MgO product has melting point of 3125 K = the highest-tempo result. "
            "The country track that melts your face off (scientifically accurate).",
        },
    ],
}
