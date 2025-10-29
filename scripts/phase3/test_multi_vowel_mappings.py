#!/usr/bin/env python3
"""
Test expanded vowel mappings (e↔o, a↔e, i↔y) on Section 4 to measure
recognition rate improvement.
"""

import json
from pathlib import Path
from itertools import product
from collections import Counter


def load_data():
    """Load specialized vocabulary and Section 4 text."""
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"

    # Load specialized vocabulary
    with open(
        results_dir / "specialized_medical_vocabulary.json", "r", encoding="utf-8"
    ) as f:
        vocab_data = json.load(f)

    # Flatten into lookup dict
    specialized_vocab = {}
    for term, info in vocab_data.items():
        specialized_vocab[term] = info

    # Common words
    common_words = {
        "a": {"meaning": "a", "category": "COMMON"},
        "an": {"meaning": "an", "category": "COMMON"},
        "the": {"meaning": "the", "category": "COMMON"},
        "and": {"meaning": "and", "category": "COMMON"},
        "or": {"meaning": "or", "category": "COMMON"},
        "of": {"meaning": "of", "category": "COMMON"},
        "to": {"meaning": "to", "category": "COMMON"},
        "in": {"meaning": "in", "category": "COMMON"},
        "for": {"meaning": "for", "category": "COMMON"},
        "with": {"meaning": "with", "category": "COMMON"},
        "is": {"meaning": "is", "category": "COMMON"},
        "it": {"meaning": "it", "category": "COMMON"},
        "that": {"meaning": "that", "category": "COMMON"},
        "this": {"meaning": "this", "category": "COMMON"},
        "she": {"meaning": "she", "category": "COMMON"},
        "he": {"meaning": "he", "category": "COMMON"},
        "her": {"meaning": "her", "category": "COMMON"},
        "his": {"meaning": "his", "category": "COMMON"},
        "if": {"meaning": "if", "category": "COMMON"},
        "be": {"meaning": "be", "category": "COMMON"},
        "as": {"meaning": "as", "category": "COMMON"},
        "at": {"meaning": "at", "category": "COMMON"},
        "by": {"meaning": "by", "category": "COMMON"},
        "do": {"meaning": "do", "category": "COMMON"},
        "so": {"meaning": "so", "category": "COMMON"},
        "on": {"meaning": "on", "category": "COMMON"},
        "up": {"meaning": "up", "category": "COMMON"},
        "out": {"meaning": "out", "category": "COMMON"},
        "not": {"meaning": "not", "category": "COMMON"},
        "all": {"meaning": "all", "category": "COMMON"},
    }

    combined_vocab = {**specialized_vocab, **common_words}

    # Load Section 4 words (2000-2500)
    with open(results_dir / "section_4_words.json", "r", encoding="utf-8") as f:
        section_4_data = json.load(f)

    section_4_words = section_4_data["words"]

    return combined_vocab, section_4_words


def generate_variants_eo_only(word, max_variants=32):
    """Generate variants with e↔o only (baseline)."""
    word_clean = word.lower().strip(".,;:!?")

    eo_positions = [(i, c) for i, c in enumerate(word_clean) if c in ["e", "o"]]

    if len(eo_positions) > 5:
        return [
            word_clean,
            word_clean.replace("o", "e"),
            word_clean.replace("e", "o"),
        ]

    variants = set()
    for combination in product(["e", "o"], repeat=len(eo_positions)):
        variant = list(word_clean)
        for (pos, _), new_char in zip(eo_positions, combination):
            variant[pos] = new_char
        variants.add("".join(variant))
        if len(variants) >= max_variants:
            break

    return list(variants)


def generate_variants_multi_vowel(word, max_variants=128):
    """
    Generate variants with multiple vowel substitutions:
    - e ↔ o (existing)
    - a ↔ e (new)
    - i ↔ y (new)
    """
    word_clean = word.lower().strip(".,;:!?")

    # Find positions for each vowel pair
    substitutions = {
        "e": ["e", "o", "a"],  # e can become o or a
        "o": ["o", "e"],  # o can become e
        "a": ["a", "e"],  # a can become e
        "i": ["i", "y"],  # i can become y
        "y": ["y", "i"],  # y can become i
    }

    # Build list of (position, possible_chars)
    positions = []
    for i, char in enumerate(word_clean):
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


def test_section_with_mapping(section_words, vocab, mapping_type="eo_only"):
    """Test Section 4 with different vowel mapping strategies."""

    recognized = []
    recognition_details = []

    for word in section_words:
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
            if variant in vocab:
                best_match = {
                    "original": word_clean,
                    "variant": variant,
                    "meaning": vocab[variant]["meaning"],
                    "category": vocab[variant]["category"],
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

    vocab, section_4_words = load_data()
    total_words = len(section_4_words)

    print(f"Section 4 statistics:")
    print(f"  Total words: {total_words}")
    print(f"  Vocabulary size: {len(vocab)}")
    print()

    # Test 1: e↔o only (baseline)
    print("TEST 1: e↔o substitution only (baseline)")
    print("-" * 80)
    recognized_eo, details_eo = test_section_with_mapping(
        section_4_words, vocab, "eo_only"
    )
    rate_eo = 100 * len(recognized_eo) / total_words
    print(f"Recognition rate: {len(recognized_eo)}/{total_words} = {rate_eo:.2f}%")
    print(f"Unique terms: {len(set(recognized_eo))}")
    print()
    print("Top matches:")
    for detail in details_eo[:15]:
        print(
            f"  {detail['original']:15s} → {detail['variant']:15s} = {detail['meaning']:20s} ({detail['category']})"
        )
    print()

    # Test 2: Multi-vowel (e↔o, a↔e, i↔y)
    print("TEST 2: Multi-vowel substitution (e↔o, a↔e, i↔y)")
    print("-" * 80)
    recognized_multi, details_multi = test_section_with_mapping(
        section_4_words, vocab, "multi_vowel"
    )
    rate_multi = 100 * len(recognized_multi) / total_words
    print(
        f"Recognition rate: {len(recognized_multi)}/{total_words} = {rate_multi:.2f}%"
    )
    print(f"Unique terms: {len(set(recognized_multi))}")
    print()
    print("Top matches:")
    for detail in details_multi[:15]:
        print(
            f"  {detail['original']:15s} → {detail['variant']:15s} = {detail['meaning']:20s} ({detail['category']})"
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
    new_matches_multi = [
        d
        for d in details_multi
        if d["variant"] not in [e["variant"] for e in details_eo]
    ]
    if new_matches_multi:
        print(f"NEW MATCHES with multi-vowel ({len(new_matches_multi)}):")
        for detail in new_matches_multi[:20]:
            print(
                f"  {detail['original']:15s} → {detail['variant']:15s} = {detail['meaning']:20s} ({detail['category']})"
            )
        print()

    # Category breakdown
    print("CATEGORY BREAKDOWN (multi-vowel):")
    categories = Counter([d["category"] for d in details_multi])
    for cat, count in categories.most_common():
        print(f"  {cat:20s}: {count:3d} words")
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
            "matches": details_eo,
        },
        "multi_vowel": {
            "recognized": len(recognized_multi),
            "rate": rate_multi,
            "unique_terms": len(set(recognized_multi)),
            "matches": details_multi,
        },
        "improvement": {"absolute": improvement, "relative_pct": improvement_pct},
        "new_matches": new_matches_multi,
    }

    output_path = results_dir / "multi_vowel_test_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print()
    print(f"Results saved to: {output_path}")
    print()


if __name__ == "__main__":
    main()
