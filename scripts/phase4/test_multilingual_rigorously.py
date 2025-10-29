"""
Rigorous Multilingual Test
===========================

CRITICAL PUSHBACK: One particle similarity isn't enough evidence.

Must test:
1. Are there OTHER Persian particles? (ra, az, ba, ta, be)
2. Are there Turkish/Uralic particles?
3. Are statistics significant or random?
4. Does "dar" have consistent function or multiple native functions?

If multilingual → should find 5-10 Persian morphemes
If single language → "dar" is just a versatile native particle
"""

import json
from pathlib import Path
from collections import Counter
import math


def load_manuscript():
    """Load manuscript"""
    transcription_path = Path(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt"
    )

    with open(transcription_path, "r", encoding="utf-8") as f:
        text = f.read()

    words = text.lower().split()
    return words


def test_persian_particle_inventory(words):
    """
    TEST 1: Search for OTHER Persian particles

    If really Persian, should find:
    - ra (را) - object marker (VERY common in Persian)
    - az (از) - "from"
    - ba (با) - "with"
    - ta (تا) - "until"
    - be (به) - "to"

    These are the 5 most common Persian particles in ANY text.
    If missing → "dar" similarity is coincidence
    """
    persian_particles = {
        "ra": {"meaning": "object marker", "expected_frequency": "very high"},
        "az": {"meaning": "from", "expected_frequency": "high"},
        "ba": {"meaning": "with", "expected_frequency": "high"},
        "ta": {"meaning": "until", "expected_frequency": "medium"},
        "be": {"meaning": "to", "expected_frequency": "medium"},
        "ke": {"meaning": "that/which", "expected_frequency": "very high"},
        "va": {"meaning": "and", "expected_frequency": "very high"},
    }

    word_freq = Counter(words)

    results = {}
    for particle, data in persian_particles.items():
        count = word_freq.get(particle, 0)

        # Check if appears as standalone word
        standalone = sum(1 for w in words if w == particle)

        # Check if appears in compounds
        in_compounds = sum(1 for w in set(words) if particle in w and w != particle)

        results[particle] = {
            "expected": data["expected_frequency"],
            "meaning": data["meaning"],
            "standalone_count": standalone,
            "in_compounds": in_compounds,
            "found": standalone > 0,
        }

    return results


def test_turkish_uralic_particles(words):
    """
    TEST 2: Search for Turkish/Hungarian particles

    If multilingual Uralic+Persian, should find:

    Turkish:
    - de/da - "also, too" (very common)
    - ki - "that, which"
    - mi/mu - question particle
    - ile/le/la - "with"

    Hungarian:
    - is - "also, too"
    - hogy - "that"
    - vagy - "or"
    """
    turkic_particles = {
        "de": {"language": "Turkish", "meaning": "also/too"},
        "da": {"language": "Turkish", "meaning": "also/too"},
        "ki": {"language": "Turkish", "meaning": "that/which"},
        "mi": {"language": "Turkish", "meaning": "question marker"},
        "ile": {"language": "Turkish", "meaning": "with"},
        "le": {"language": "Turkish", "meaning": "with (shortened)"},
        "is": {"language": "Hungarian", "meaning": "also/too"},
        "vagy": {"language": "Hungarian", "meaning": "or"},
    }

    word_freq = Counter(words)

    results = {}
    for particle, data in turkic_particles.items():
        count = word_freq.get(particle, 0)
        standalone = sum(1 for w in words if w == particle)

        results[particle] = {
            "language": data["language"],
            "meaning": data["meaning"],
            "standalone_count": standalone,
            "found": standalone > 0,
        }

    return results


def calculate_dar_cooccurrence_statistics(words):
    """
    TEST 3: Proper statistical test for dar+oak/oat

    Null hypothesis: "dar" appears near oak/oat at random rate

    Calculate:
    - Expected co-occurrence (baseline)
    - Observed co-occurrence
    - Statistical significance
    """
    # Count occurrences
    dar_count = sum(1 for w in words if w == "dar")
    oak_oat_count = sum(1 for w in words if "ok" in w or "ot" in w)
    total_words = len(words)

    # Count co-occurrences (within window of 3)
    window = 3
    cooccurrences = 0

    for i, word in enumerate(words):
        if word == "dar":
            # Check window
            start = max(0, i - window)
            end = min(len(words), i + window + 1)

            for j in range(start, end):
                if j != i and ("ok" in words[j] or "ot" in words[j]):
                    cooccurrences += 1
                    break  # Count each "dar" only once

    # Calculate expected rate
    # Probability that any word is oak/oat
    p_oak_oat = oak_oat_count / total_words

    # For each "dar", expected number of oak/oat in window
    window_size = window * 2  # Before and after
    expected_per_dar = window_size * p_oak_oat
    expected_total = dar_count * expected_per_dar

    # Calculate enrichment
    enrichment = cooccurrences / expected_total if expected_total > 0 else 0

    # Binomial test (is observed significantly > expected?)
    # Simplified: z-score
    if expected_total > 0:
        variance = expected_total * (1 - p_oak_oat)
        std_dev = math.sqrt(variance)
        z_score = (cooccurrences - expected_total) / std_dev if std_dev > 0 else 0

        # z > 3 → p < 0.001 (very significant)
        # z > 2 → p < 0.05 (significant)
        significant = z_score > 2
    else:
        z_score = 0
        significant = False

    return {
        "dar_count": dar_count,
        "oak_oat_count": oak_oat_count,
        "observed_cooccurrence": cooccurrences,
        "expected_cooccurrence": expected_total,
        "enrichment": enrichment,
        "z_score": z_score,
        "significant": significant,
        "p_value_estimate": "p<0.001"
        if z_score > 3
        else ("p<0.05" if z_score > 2 else "not significant"),
    }


def analyze_dar_functional_distribution(words):
    """
    TEST 4: Does "dar" have consistent function or multiple functions?

    If versatile native particle → different contexts should show different meanings
    If Persian borrowing → should be consistently prepositional

    Categorize "dar" instances by context:
    - Before plants (prepositional)
    - After plants (different function)
    - Between repeated words (different function)
    - Sentence-initial (different function)
    """
    dar_contexts = {
        "before_plant": 0,
        "after_plant": 0,
        "between_plants": 0,
        "sentence_initial": 0,
        "after_verb": 0,
        "other": 0,
    }

    examples = {k: [] for k in dar_contexts.keys()}

    for i, word in enumerate(words):
        if word == "dar":
            # Categorize context
            before = words[i - 1] if i > 0 else None
            after = words[i + 1] if i < len(words) - 1 else None
            before2 = words[i - 2] if i > 1 else None
            after2 = words[i + 2] if i < len(words) - 2 else None

            categorized = False

            # Before plant
            if after and ("ok" in after or "ot" in after):
                dar_contexts["before_plant"] += 1
                if len(examples["before_plant"]) < 5:
                    examples["before_plant"].append(f"{before or '?'} | dar {after}")
                categorized = True

            # After plant
            elif before and ("ok" in before or "ot" in before):
                dar_contexts["after_plant"] += 1
                if len(examples["after_plant"]) < 5:
                    examples["after_plant"].append(f"{before} dar | {after or '?'}")
                categorized = True

            # Between plants
            elif (
                before
                and after
                and ("ok" in before or "ot" in before)
                and ("ok" in after or "ot" in after)
            ):
                dar_contexts["between_plants"] += 1
                if len(examples["between_plants"]) < 5:
                    examples["between_plants"].append(f"{before} dar {after}")
                categorized = True

            # Sentence initial (after pronoun)
            elif before in ["daiin", "aiin", "saiin"] or i == 0:
                dar_contexts["sentence_initial"] += 1
                if len(examples["sentence_initial"]) < 5:
                    examples["sentence_initial"].append(
                        f"{before or '[START]'} dar {after or '?'}"
                    )
                categorized = True

            # After verb
            elif before and before.endswith("edy"):
                dar_contexts["after_verb"] += 1
                if len(examples["after_verb"]) < 5:
                    examples["after_verb"].append(f"{before} dar {after or '?'}")
                categorized = True

            if not categorized:
                dar_contexts["other"] += 1
                if len(examples["other"]) < 5:
                    examples["other"].append(f"{before or '?'} dar {after or '?'}")

    total = sum(dar_contexts.values())
    proportions = {k: v / total for k, v in dar_contexts.items()} if total > 0 else {}

    return {
        "contexts": dar_contexts,
        "proportions": proportions,
        "examples": examples,
        "interpretation": "versatile_native"
        if len([v for v in proportions.values() if v > 0.15]) > 2
        else "consistent_preposition",
    }


def main():
    print("=" * 80)
    print("RIGOROUS MULTILINGUAL TEST")
    print("=" * 80)
    print()
    print("CRITICAL TEST: Is Voynich really multilingual or is 'dar' just coincidence?")
    print()

    # Load manuscript
    words = load_manuscript()
    print(f"Total words: {len(words):,}")
    print()

    # TEST 1: Persian particle inventory
    print("=" * 80)
    print("TEST 1: PERSIAN PARTICLE INVENTORY")
    print("=" * 80)
    print()
    print("If Persian-influenced, should find the 5 most common Persian particles")
    print()

    persian = test_persian_particle_inventory(words)

    print(f"{'Particle':<8} {'Meaning':<20} {'Expected':<15} {'Found':<8} {'Count':<8}")
    print("-" * 70)
    for particle, data in persian.items():
        found_str = "✓ YES" if data["found"] else "✗ NO"
        print(
            f"{particle:<8} {data['meaning']:<20} {data['expected']:<15} {found_str:<8} {data['standalone_count']:<8}"
        )

    persian_found = sum(1 for d in persian.values() if d["found"])

    print()
    print(f"Persian particles found: {persian_found}/7")
    print()

    if persian_found >= 4:
        print("✓✓ Strong Persian vocabulary presence")
    elif persian_found >= 2:
        print("~ Weak Persian vocabulary presence")
    else:
        print("✗ No Persian vocabulary detected (besides possible 'dar')")

    print()

    # TEST 2: Turkish/Uralic particles
    print("=" * 80)
    print("TEST 2: TURKISH/URALIC PARTICLE INVENTORY")
    print("=" * 80)
    print()
    print("If Turkic-influenced, should find common particles")
    print()

    turkic = test_turkish_uralic_particles(words)

    print(f"{'Particle':<8} {'Language':<15} {'Meaning':<20} {'Found':<8} {'Count':<8}")
    print("-" * 70)
    for particle, data in turkic.items():
        found_str = "✓ YES" if data["found"] else "✗ NO"
        print(
            f"{particle:<8} {data['language']:<15} {data['meaning']:<20} {found_str:<8} {data['standalone_count']:<8}"
        )

    turkic_found = sum(1 for d in turkic.values() if d["found"])

    print()
    print(f"Turkic particles found: {turkic_found}/8")
    print()

    if turkic_found >= 3:
        print("✓✓ Strong Turkic vocabulary presence")
    elif turkic_found >= 1:
        print("~ Weak Turkic vocabulary presence")
    else:
        print("✗ No Turkic vocabulary detected")

    print()

    # TEST 3: Statistical significance
    print("=" * 80)
    print("TEST 3: DAR+OAK/OAT CO-OCCURRENCE STATISTICS")
    print("=" * 80)
    print()
    print("Proper statistical test: Is co-occurrence significant or random?")
    print()

    stats = calculate_dar_cooccurrence_statistics(words)

    print(f"'dar' occurrences: {stats['dar_count']}")
    print(f"Oak/oat occurrences: {stats['oak_oat_count']}")
    print(f"Observed co-occurrence: {stats['observed_cooccurrence']}")
    print(f"Expected (random): {stats['expected_cooccurrence']:.1f}")
    print(f"Enrichment: {stats['enrichment']:.2f}x")
    print(f"Z-score: {stats['z_score']:.2f}")
    print(f"Significance: {stats['p_value_estimate']}")
    print()

    if stats["significant"]:
        print(
            f"✓✓ Co-occurrence is STATISTICALLY SIGNIFICANT ({stats['p_value_estimate']})"
        )
        print("   'dar' and oak/oat appear together more than chance")
    else:
        print("✗ Co-occurrence is NOT significant (could be random)")

    print()

    # TEST 4: Functional distribution
    print("=" * 80)
    print("TEST 4: DAR FUNCTIONAL DISTRIBUTION")
    print("=" * 80)
    print()
    print("Does 'dar' have one consistent function or multiple functions?")
    print()

    functions = analyze_dar_functional_distribution(words)

    print(f"{'Context':<20} {'Count':<10} {'Proportion':<15} {'Examples':<50}")
    print("-" * 95)
    for context, count in functions["contexts"].items():
        prop = functions["proportions"].get(context, 0)
        example = (
            functions["examples"][context][0] if functions["examples"][context] else ""
        )
        print(f"{context:<20} {count:<10} {prop * 100:>6.1f}%         {example:<50}")

    print()

    if functions["interpretation"] == "versatile_native":
        print("~ INTERPRETATION: 'dar' shows MULTIPLE functions")
        print("  → Suggests native versatile particle (like Turkish 'de')")
        print("  → NOT consistent with borrowed Persian preposition")
    else:
        print("✓ INTERPRETATION: 'dar' shows CONSISTENT prepositional function")
        print("  → Could be Persian borrowing")

    print()

    # FINAL VERDICT
    print("=" * 80)
    print("FINAL VERDICT: MULTILINGUAL HYPOTHESIS")
    print("=" * 80)
    print()

    evidence_score = 0

    # Score each test
    if persian_found >= 4:
        evidence_score += 3
        print("✓✓✓ Strong Persian particle inventory (weight: 3)")
    elif persian_found >= 2:
        evidence_score += 1
        print("~ Weak Persian presence (weight: 1)")
    else:
        print("✗ No Persian particles found (weight: 0)")

    if turkic_found >= 3:
        evidence_score += 2
        print("✓✓ Turkic particles present (weight: 2)")
    elif turkic_found >= 1:
        evidence_score += 1
        print("~ Some Turkic presence (weight: 1)")
    else:
        print("✗ No Turkic particles found (weight: 0)")

    if stats["significant"]:
        evidence_score += 2
        print(f"✓✓ Dar+oak/oat significant (weight: 2)")
    else:
        print("✗ Dar+oak/oat not significant (weight: 0)")

    if functions["interpretation"] == "consistent_preposition":
        evidence_score += 1
        print("✓ Dar shows consistent function (weight: 1)")
    else:
        print("~ Dar shows multiple functions (weight: 0)")

    print()
    print(f"TOTAL EVIDENCE SCORE: {evidence_score}/8")
    print()

    if evidence_score >= 6:
        print("✓✓✓ MULTILINGUAL HYPOTHESIS STRONGLY SUPPORTED")
        print()
        print("Evidence shows presence of both Persian and Turkic/Uralic elements")
        print("Recommendation: Analyze as multilingual text")
    elif evidence_score >= 3:
        print("~ MULTILINGUAL HYPOTHESIS WEAKLY SUPPORTED")
        print()
        print("Some evidence but not conclusive")
        print("Recommendation: Consider contact language or borrowing")
    else:
        print("✗ MULTILINGUAL HYPOTHESIS NOT SUPPORTED")
        print()
        print("Insufficient evidence for multiple languages")
        print("Recommendation: Analyze as single language with possible borrowings")
        print()
        print("'dar' similarity to Persian is likely:")
        print("  - Coincidental")
        print("  - Historical borrowing into native language")
        print("  - Convergent evolution (many languages have 'dar'-like particles)")

    # Save results
    results = {
        "persian_particles": persian,
        "turkic_particles": turkic,
        "cooccurrence_stats": stats,
        "dar_functions": {
            "contexts": functions["contexts"],
            "proportions": functions["proportions"],
            "interpretation": functions["interpretation"],
        },
        "verdict": {
            "evidence_score": evidence_score,
            "max_score": 8,
            "hypothesis_supported": evidence_score >= 3,
            "persian_found": persian_found,
            "turkic_found": turkic_found,
        },
    }

    output_path = Path("results/phase4/multilingual_rigorous_test.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print()
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
