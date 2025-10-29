#!/usr/bin/env python3
"""
Test systematic consonant pattern substitutions.

Consonant shifts common in Middle English:
- ch ↔ sh (dialectal variation, very common)
- c ↔ k (spelling variation)
- ph ↔ f (Greek vs English spelling)
- t ↔ d (voicing variation)

These can combine with:
- e↔o vowel substitution
- Word reversal (by semantic category)

This could significantly increase recognition rate.
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from itertools import product
import re


def load_data():
    """Load specialized vocabulary and full manuscript."""
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"

    # Load specialized vocabulary
    with open(
        results_dir / "specialized_medical_vocabulary.json", "r", encoding="utf-8"
    ) as f:
        vocab_data = json.load(f)

    specialized_vocab = {}
    for term, info in vocab_data.items():
        specialized_vocab[term] = info

    # Common words with expanded list
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
        "day": {"meaning": "day", "category": "time"},
        "night": {"meaning": "night", "category": "time"},
    }

    combined_vocab = {**specialized_vocab, **common_words}

    # Load full manuscript
    with open(
        results_dir / "full_manuscript_translation.json", "r", encoding="utf-8"
    ) as f:
        manuscript = json.load(f)

    all_words = []
    for section in manuscript["sections"]:
        words = section["original"].split()
        all_words.extend(words)

    return combined_vocab, all_words


def apply_eo_substitution(word, max_variants=32):
    """Apply e↔o substitution to a word."""
    eo_positions = [(i, c) for i, c in enumerate(word) if c in ["e", "o"]]

    if len(eo_positions) > 5:
        return [word, word.replace("o", "e"), word.replace("e", "o")]

    variants = set()
    for combination in product(["e", "o"], repeat=len(eo_positions)):
        variant = list(word)
        for (pos, _), new_char in zip(eo_positions, combination):
            variant[pos] = new_char
        variants.add("".join(variant))
        if len(variants) >= max_variants:
            break

    return list(variants)


def apply_consonant_shift(word, shift_type):
    """
    Apply consonant shift to a word.

    shift_type: 'ch_sh', 'c_k', 'ph_f', 't_d'
    """
    if shift_type == "ch_sh":
        # ch ↔ sh
        variants = []
        # Replace ch with sh
        variants.append(word.replace("ch", "sh"))
        # Replace sh with ch
        variants.append(word.replace("sh", "ch"))
        return variants

    elif shift_type == "c_k":
        # c ↔ k
        variants = []
        variants.append(word.replace("c", "k"))
        variants.append(word.replace("k", "c"))
        return variants

    elif shift_type == "ph_f":
        # ph ↔ f
        variants = []
        variants.append(word.replace("ph", "f"))
        variants.append(word.replace("f", "ph"))
        return variants

    elif shift_type == "t_d":
        # t ↔ d
        variants = []
        variants.append(word.replace("t", "d"))
        variants.append(word.replace("d", "t"))
        return variants

    return [word]


def generate_full_variants(word, include_reversal=True, include_consonants=True):
    """
    Generate all possible variants of a word with:
    - e↔o substitution
    - Consonant shifts
    - Word reversal (optional)
    """
    variants = {"direct": set(), "reversed": set() if include_reversal else None}

    base_words = [word]
    if include_reversal:
        base_words.append(word[::-1])

    consonant_shifts = ["ch_sh", "c_k", "ph_f", "t_d"] if include_consonants else []

    for base in base_words:
        # Start with e↔o variants of base
        for eo_var in apply_eo_substitution(base):
            if base == word:
                variants["direct"].add(eo_var)
            elif include_reversal:
                variants["reversed"].add(eo_var)

            # Apply each consonant shift
            if include_consonants:
                for shift_type in consonant_shifts:
                    for cons_var in apply_consonant_shift(eo_var, shift_type):
                        if cons_var != eo_var:  # Only add if actually changed
                            if base == word:
                                variants["direct"].add(cons_var)
                            elif include_reversal:
                                variants["reversed"].add(cons_var)

    # Convert sets to lists
    variants["direct"] = list(variants["direct"])
    if include_reversal:
        variants["reversed"] = list(variants["reversed"])

    return variants


def search_with_transforms(
    vocab, all_words, include_consonants=False, sample_size=None
):
    """
    Search manuscript with various transforms.

    sample_size: If set, only search first N words (for faster testing)
    """
    results = {
        "direct_matches": [],
        "reversed_matches": [],
        "consonant_matches": [],
        "multi_transform_matches": [],
    }

    # Limit search if sample_size specified
    search_words = all_words[:sample_size] if sample_size else all_words

    for pos, word in enumerate(search_words):
        word_clean = word.lower().strip(".,;:!?")

        # Strategy 1: Direct match (baseline)
        if word_clean in vocab:
            results["direct_matches"].append(
                {
                    "position": pos,
                    "voynich": word_clean,
                    "english": vocab[word_clean]["meaning"],
                    "category": vocab[word_clean]["category"],
                    "transform": "none",
                }
            )
            continue

        # Strategy 2: e↔o only
        found = False
        for eo_var in apply_eo_substitution(word_clean):
            if eo_var in vocab:
                results["direct_matches"].append(
                    {
                        "position": pos,
                        "voynich": word_clean,
                        "english": vocab[eo_var]["meaning"],
                        "category": vocab[eo_var]["category"],
                        "transform": "e↔o",
                    }
                )
                found = True
                break

        if found:
            continue

        # Strategy 3: Reversal + e↔o (we know this works)
        reversed_word = word_clean[::-1]
        for eo_var in apply_eo_substitution(reversed_word):
            if eo_var in vocab:
                results["reversed_matches"].append(
                    {
                        "position": pos,
                        "voynich": word_clean,
                        "english": vocab[eo_var]["meaning"],
                        "category": vocab[eo_var]["category"],
                        "transform": "reversed + e↔o",
                    }
                )
                found = True
                break

        if found or not include_consonants:
            continue

        # Strategy 4: Consonant shifts (NEW!)
        for shift_type in ["ch_sh", "c_k", "ph_f", "t_d"]:
            for cons_var in apply_consonant_shift(word_clean, shift_type):
                if cons_var in vocab:
                    results["consonant_matches"].append(
                        {
                            "position": pos,
                            "voynich": word_clean,
                            "english": vocab[cons_var]["meaning"],
                            "category": vocab[cons_var]["category"],
                            "transform": f"consonant ({shift_type})",
                        }
                    )
                    found = True
                    break

                # Try consonant + e↔o
                for eo_var in apply_eo_substitution(cons_var):
                    if eo_var in vocab:
                        results["consonant_matches"].append(
                            {
                                "position": pos,
                                "voynich": word_clean,
                                "english": vocab[eo_var]["meaning"],
                                "category": vocab[eo_var]["category"],
                                "transform": f"consonant ({shift_type}) + e↔o",
                            }
                        )
                        found = True
                        break

                if found:
                    break

            if found:
                break

        if found:
            continue

        # Strategy 5: Multi-transform (consonant + e↔o + reversal)
        if include_consonants:
            for shift_type in ["ch_sh", "c_k", "ph_f", "t_d"]:
                # Try reversal + consonant
                for cons_var in apply_consonant_shift(reversed_word, shift_type):
                    if cons_var in vocab:
                        results["multi_transform_matches"].append(
                            {
                                "position": pos,
                                "voynich": word_clean,
                                "english": vocab[cons_var]["meaning"],
                                "category": vocab[cons_var]["category"],
                                "transform": f"reversed + consonant ({shift_type})",
                            }
                        )
                        found = True
                        break

                    # Try reversal + consonant + e↔o
                    for eo_var in apply_eo_substitution(cons_var):
                        if eo_var in vocab:
                            results["multi_transform_matches"].append(
                                {
                                    "position": pos,
                                    "voynich": word_clean,
                                    "english": vocab[eo_var]["meaning"],
                                    "category": vocab[eo_var]["category"],
                                    "transform": f"reversed + consonant ({shift_type}) + e↔o",
                                }
                            )
                            found = True
                            break

                    if found:
                        break

                if found:
                    break

    return results


def main():
    print("=" * 80)
    print("CONSONANT PATTERN ANALYSIS")
    print("=" * 80)
    print()
    print("Testing systematic consonant shifts:")
    print("  • ch ↔ sh (Middle English dialectal variation)")
    print("  • c ↔ k (spelling variation)")
    print("  • ph ↔ f (Greek vs English)")
    print("  • t ↔ d (voicing variation)")
    print()
    print("Combined with:")
    print("  • e↔o vowel substitution")
    print("  • Word reversal (semantic category-based)")
    print()

    vocab, all_words = load_data()
    total_words = len(all_words)

    print(f"Manuscript: {total_words:,} words")
    print(f"Vocabulary: {len(vocab)} terms")
    print()

    # First, test on sample to see if it's worth full analysis
    print("=" * 80)
    print("PHASE 1: Sample Test (first 5,000 words)")
    print("=" * 80)
    print()

    sample_results = search_with_transforms(
        vocab, all_words, include_consonants=True, sample_size=5000
    )

    sample_total = (
        len(sample_results["direct_matches"])
        + len(sample_results["reversed_matches"])
        + len(sample_results["consonant_matches"])
        + len(sample_results["multi_transform_matches"])
    )

    print(
        f"Direct matches (none/e↔o):        {len(sample_results['direct_matches']):4d}"
    )
    print(
        f"Reversed matches (reverse+e↔o):   {len(sample_results['reversed_matches']):4d}"
    )
    print(
        f"Consonant matches (NEW!):         {len(sample_results['consonant_matches']):4d}"
    )
    print(
        f"Multi-transform matches (NEW!):   {len(sample_results['multi_transform_matches']):4d}"
    )
    print(f"TOTAL:                            {sample_total:4d}")
    print()

    sample_rate = sample_total / 5000 * 100
    print(f"Recognition rate: {sample_rate:.2f}%")
    print()

    # Show sample consonant matches
    if sample_results["consonant_matches"]:
        print("Sample consonant matches:")
        for match in sample_results["consonant_matches"][:10]:
            print(
                f"  Position {match['position']:6d}: '{match['voynich']}' → {match['english']}"
            )
            print(f"    Transform: {match['transform']}, Category: {match['category']}")
        print()

    # Show sample multi-transform matches
    if sample_results["multi_transform_matches"]:
        print("Sample multi-transform matches:")
        for match in sample_results["multi_transform_matches"][:10]:
            print(
                f"  Position {match['position']:6d}: '{match['voynich']}' → {match['english']}"
            )
            print(f"    Transform: {match['transform']}, Category: {match['category']}")
        print()

    # Decide if full analysis is warranted
    new_matches = len(sample_results["consonant_matches"]) + len(
        sample_results["multi_transform_matches"]
    )

    if new_matches == 0:
        print("=" * 80)
        print("RESULT: No new matches found with consonant patterns")
        print("=" * 80)
        print()
        print("✗ Consonant substitutions (ch↔sh, c↔k, ph↔f, t↔d) do not appear")
        print("  to be part of the cipher.")
        print()
        print("Possible reasons:")
        print("  1. Consonants are preserved in the cipher")
        print("  2. Our vocabulary doesn't contain the right terms")
        print("  3. Consonant patterns are more complex than simple substitution")
        print()

    elif new_matches > 0 and new_matches < 10:
        print("=" * 80)
        print("RESULT: Minimal new matches (possibly noise)")
        print("=" * 80)
        print()
        print("~ WEAK EVIDENCE for consonant patterns")
        print(f"  Found {new_matches} new matches in 5,000 words")
        print("  Could be coincidental or rare pattern")
        print()

    else:
        print("=" * 80)
        print("RESULT: Significant new matches found!")
        print("=" * 80)
        print()
        print(f"✓ Found {new_matches} new matches with consonant patterns")
        print("  This justifies full manuscript analysis.")
        print()
        print("Proceeding to Phase 2: Full manuscript scan...")
        print()

        # Run full analysis
        print("=" * 80)
        print("PHASE 2: Full Manuscript Analysis")
        print("=" * 80)
        print()
        print(f"Searching {total_words:,} words...")
        print("(This may take a minute...)")
        print()

        full_results = search_with_transforms(vocab, all_words, include_consonants=True)

        full_total = (
            len(full_results["direct_matches"])
            + len(full_results["reversed_matches"])
            + len(full_results["consonant_matches"])
            + len(full_results["multi_transform_matches"])
        )

        print(
            f"Direct matches (none/e↔o):        {len(full_results['direct_matches']):4d}"
        )
        print(
            f"Reversed matches (reverse+e↔o):   {len(full_results['reversed_matches']):4d}"
        )
        print(
            f"Consonant matches:                {len(full_results['consonant_matches']):4d}"
        )
        print(
            f"Multi-transform matches:          {len(full_results['multi_transform_matches']):4d}"
        )
        print(f"TOTAL:                            {full_total:4d}")
        print()

        full_rate = full_total / total_words * 100
        baseline_rate = (
            (
                len(full_results["direct_matches"])
                + len(full_results["reversed_matches"])
            )
            / total_words
            * 100
        )
        improvement = full_rate - baseline_rate

        print(f"Baseline recognition (e↔o + reversal): {baseline_rate:.2f}%")
        print(f"With consonant patterns:                {full_rate:.2f}%")
        print(f"Improvement:                            +{improvement:.2f}%")
        print()

        # Analyze consonant match categories
        if full_results["consonant_matches"]:
            print("Consonant matches by category:")
            cat_counter = Counter(
                [m["category"] for m in full_results["consonant_matches"]]
            )
            for cat, count in cat_counter.most_common():
                print(f"  {cat:20s}: {count:3d}")
            print()

        # Save full results
        results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"
        output = {
            "total_words": total_words,
            "recognition": {
                "direct": len(full_results["direct_matches"]),
                "reversed": len(full_results["reversed_matches"]),
                "consonant": len(full_results["consonant_matches"]),
                "multi_transform": len(full_results["multi_transform_matches"]),
                "total": full_total,
            },
            "rates": {
                "baseline": baseline_rate,
                "with_consonants": full_rate,
                "improvement": improvement,
            },
            "sample_matches": {
                "consonant": full_results["consonant_matches"][:50],
                "multi_transform": full_results["multi_transform_matches"][:50],
            },
        }

        output_path = results_dir / "consonant_pattern_results.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

        print(f"Full results saved to: {output_path}")
        print()

    # Save sample results regardless
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"
    sample_output = {
        "sample_size": 5000,
        "recognition": {
            "direct": len(sample_results["direct_matches"]),
            "reversed": len(sample_results["reversed_matches"]),
            "consonant": len(sample_results["consonant_matches"]),
            "multi_transform": len(sample_results["multi_transform_matches"]),
            "total": sample_total,
        },
        "rate": sample_rate,
        "matches": sample_results,
    }

    sample_path = results_dir / "consonant_pattern_sample_results.json"
    with open(sample_path, "w", encoding="utf-8") as f:
        json.dump(sample_output, f, indent=2)

    print(f"Sample results saved to: {sample_path}")
    print()


if __name__ == "__main__":
    main()
