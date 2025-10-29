#!/usr/bin/env python3
"""
Test expanded vowel mappings (a↔e, i↔y, u↔o) on Section 4 to measure
recognition rate improvement.
"""

import json
from pathlib import Path
from itertools import product
from collections import Counter


def load_data():
    """Load medical vocabulary and Section 4 text."""
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"

    with open(
        results_dir / "medical_vocabulary_database.json", "r", encoding="utf-8"
    ) as f:
        medical_vocab = json.load(f)

    # Load Section 4 from translation
    with open(
        results_dir / "full_manuscript_translation.json", "r", encoding="utf-8"
    ) as f:
        translation = json.load(f)

    # Get Section 4
    section_4 = next((s for s in translation["sections"] if s["section_id"] == 4), None)

    return medical_vocab, section_4


def generate_variants_multi_vowel(word, max_variants=64):
    """
    Generate variants with multiple vowel substitutions:
    - e ↔ o (existing)
    - a ↔ e (new)
    - i ↔ y (new)
    - u ↔ o (optional)
    """
    # Find positions for each vowel pair
    substitutions = {
        "e": ["e", "o"],  # e can become o
        "o": ["o", "e"],  # o can become e
        "a": ["a", "e"],  # a can become e
        "i": ["i", "y"],  # i can become y
        "y": ["y", "i"],  # y can become i
        "u": ["u", "o"],  # u can become o (rare)
    }

    # Build list of (position, possible_chars)
    positions = []
    for i, char in enumerate(word.lower()):
        if char in substitutions:
            positions.append((i, substitutions[char]))
        else:
            positions.append((i, [char]))

    # Limit combinatorial explosion
    total_combinations = 1
    for pos, chars in positions:
        total_combinations *= len(chars)

    if total_combinations > max_variants:
        # Just try e↔o only
        return generate_variants_eo_only(word, max_variants)

    # Generate all combinations
    variants = set()
    for combo in product(*[chars for _, chars in positions]):
        variant = "".join(combo)
        variants.add(variant)
        if len(variants) >= max_variants:
            break

    return list(variants)


def generate_variants_eo_only(word, max_variants=32):
    """Generate variants with e↔o only (existing method)."""
    eo_positions = [(i, c) for i, c in enumerate(word.lower()) if c in ["e", "o"]]

    if len(eo_positions) > 5:
        return [
            word.lower(),
            word.lower().replace("o", "e"),
            word.lower().replace("e", "o"),
        ]

    variants = set()
    for combination in product(["e", "o"], repeat=len(eo_positions)):
        variant = list(word.lower())
        for (pos, _), new_char in zip(eo_positions, combination):
            variant[pos] = new_char
        variants.add("".join(variant))
        if len(variants) >= max_variants:
            break

    return list(variants)


def test_section_4_with_mapping(section_4, medical_vocab, mapping_type="eo_only"):
    """Test Section 4 with different vowel mapping strategies."""

    original_words = section_4["original"].split()

    recognized = []
    recognition_details = []

    for word in original_words:
        word_clean = word.lower().strip(".,;:!?")

        # Generate variants based on mapping type
        if mapping_type == "eo_only":
            variants = generate_variants_eo_only(word_clean)
        elif mapping_type == "multi_vowel":
            variants = generate_variants_multi_vowel(word_clean)
        else:
            variants = [word_clean]

        # Check each variant
        best_match = None
        for variant in variants:
            if variant in medical_vocab:
                best_match = {
                    "original": word_clean,
                    "variant": variant,
                    "category": medical_vocab[variant]["category"],
                    "frequency": medical_vocab[variant]["frequency"],
                }
                recognized.append(variant)
                break

        if best_match:
            recognition_details.append(best_match)

    return recognized, recognition_details


def main():
    print("=" * 80)
    print("TESTING EXPANDED VOWEL MAPPINGS ON SECTION 4")
    print("=" * 80)
    print()

    medical_vocab, section_4 = load_data()
    total_words = len(section_4["original"].split())

    print(f"Section 4 statistics:")
    print(f"  Total words: {total_words}")
    print(f"  Medical density: 1.6%")
    print()

    # Test 1: e↔o only (baseline)
    print("TEST 1: e↔o substitution only (baseline)")
    print("-" * 80)
    recognized_eo, details_eo = test_section_4_with_mapping(
        section_4, medical_vocab, "eo_only"
    )
    rate_eo = 100 * len(recognized_eo) / total_words
    print(f"Recognition rate: {len(recognized_eo)}/{total_words} = {rate_eo:.2f}%")
    print(f"Unique medical terms: {len(set(recognized_eo))}")
    print()
    print("Top matches:")
    for detail in details_eo[:10]:
        print(
            f"  {detail['original']:15s} → {detail['variant']:15s} ({detail['category']})"
        )
    print()

    # Test 2: Multi-vowel (e↔o, a↔e, i↔y)
    print("TEST 2: Multi-vowel substitution (e↔o, a↔e, i↔y)")
    print("-" * 80)
    recognized_multi, details_multi = test_section_4_with_mapping(
        section_4, medical_vocab, "multi_vowel"
    )
    rate_multi = 100 * len(recognized_multi) / total_words
    print(
        f"Recognition rate: {len(recognized_multi)}/{total_words} = {rate_multi:.2f}%"
    )
    print(f"Unique medical terms: {len(set(recognized_multi))}")
    print()
    print("Top matches:")
    for detail in details_multi[:10]:
        print(
            f"  {detail['original']:15s} → {detail['variant']:15s} ({detail['category']})"
        )
    print()

    # Analysis
    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print()

    improvement = rate_multi - rate_eo
    improvement_pct = (improvement / rate_eo * 100) if rate_eo > 0 else 0

    print(f"Baseline (e↔o only):     {rate_eo:.2f}%")
    print(f"Multi-vowel mapping:     {rate_multi:.2f}%")
    print(f"Improvement:             +{improvement:.2f} percentage points")
    print(f"Relative improvement:    {improvement_pct:.1f}%")
    print()

    # New matches found only with multi-vowel
    new_matches = set(recognized_multi) - set(recognized_eo)
    if new_matches:
        print(f"NEW MATCHES with multi-vowel ({len(new_matches)}):")
        for match in list(new_matches)[:20]:
            detail = next((d for d in details_multi if d["variant"] == match), None)
            if detail:
                print(
                    f"  {detail['original']:15s} → {detail['variant']:15s} ({detail['category']})"
                )
        print()

    # Interpretation
    print("INTERPRETATION:")
    print()
    if improvement > 5:
        print("✓✓✓ STRONG IMPROVEMENT")
        print("Multi-vowel obfuscation is likely present.")
        print("Recognition rate increase suggests a↔e and i↔y are real patterns.")
    elif improvement > 2:
        print("✓✓ MODERATE IMPROVEMENT")
        print("Some benefit from expanded mappings.")
        print("May warrant further investigation.")
    elif improvement > 0.5:
        print("✓ SLIGHT IMPROVEMENT")
        print("Minimal benefit from expanded mappings.")
        print("e↔o may be primary transformation.")
    else:
        print("✗ NO SIGNIFICANT IMPROVEMENT")
        print("e↔o appears to be the main substitution.")
        print("Other vowel mappings don't add value.")

    # Save results
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"
    output = {
        "section_id": 4,
        "total_words": total_words,
        "eo_only": {
            "recognized": len(recognized_eo),
            "rate": rate_eo,
            "unique_terms": len(set(recognized_eo)),
        },
        "multi_vowel": {
            "recognized": len(recognized_multi),
            "rate": rate_multi,
            "unique_terms": len(set(recognized_multi)),
        },
        "improvement": {"absolute": improvement, "relative_pct": improvement_pct},
        "new_matches": list(new_matches),
    }

    output_path = results_dir / "vowel_mapping_test_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print()
    print(f"Results saved to: {output_path}")
    print()


if __name__ == "__main__":
    main()
