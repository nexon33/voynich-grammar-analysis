#!/usr/bin/env python3
"""
Test word reversal hypothesis: some words may be written backwards.

This would be a simple obfuscation technique that's easily reversible
for the author but hard to detect without checking.

We'll test:
1. Pure reversal (word → drow)
2. Reversal + e↔o (word → werd → drew)
3. e↔o + reversal (word → werd reversed = drew)
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


def apply_eo_substitution(word):
    """Apply e↔o substitution to a word."""
    # Generate variants by substituting e↔o
    eo_positions = [(i, c) for i, c in enumerate(word) if c in ["e", "o"]]

    if len(eo_positions) > 5:
        # Too many combinations, just try simple swaps
        variants = [
            word,
            word.replace("o", "e"),
            word.replace("e", "o"),
        ]
        return variants

    variants = set()
    for combination in product(["e", "o"], repeat=len(eo_positions)):
        variant = list(word)
        for (pos, _), new_char in zip(eo_positions, combination):
            variant[pos] = new_char
        variants.add("".join(variant))
        if len(variants) >= 32:
            break

    return list(variants)


def test_reversal_hypothesis(section_words, vocab):
    """
    Test multiple reversal strategies:
    1. Direct match (baseline)
    2. Pure reversal
    3. Reversal + e↔o
    4. e↔o + reversal
    """

    results = {
        "direct": {"matches": [], "details": []},
        "reversed": {"matches": [], "details": []},
        "reversed_then_eo": {"matches": [], "details": []},
        "eo_then_reversed": {"matches": [], "details": []},
    }

    for word in section_words:
        word_clean = word.lower().strip(".,;:!?")

        # Strategy 1: Direct match with e↔o
        for variant in apply_eo_substitution(word_clean):
            if variant in vocab:
                results["direct"]["matches"].append(variant)
                results["direct"]["details"].append(
                    {
                        "original": word_clean,
                        "variant": variant,
                        "meaning": vocab[variant]["meaning"],
                        "category": vocab[variant]["category"],
                        "transform": "e↔o only",
                    }
                )
                break

        # Strategy 2: Pure reversal (reverse then check)
        reversed_word = word_clean[::-1]
        if reversed_word in vocab:
            results["reversed"]["matches"].append(reversed_word)
            results["reversed"]["details"].append(
                {
                    "original": word_clean,
                    "variant": reversed_word,
                    "meaning": vocab[reversed_word]["meaning"],
                    "category": vocab[reversed_word]["category"],
                    "transform": "reversed",
                }
            )

        # Strategy 3: Reverse THEN apply e↔o
        for variant in apply_eo_substitution(reversed_word):
            if variant in vocab:
                results["reversed_then_eo"]["matches"].append(variant)
                results["reversed_then_eo"]["details"].append(
                    {
                        "original": word_clean,
                        "reversed": reversed_word,
                        "variant": variant,
                        "meaning": vocab[variant]["meaning"],
                        "category": vocab[variant]["category"],
                        "transform": "reversed + e↔o",
                    }
                )
                break

        # Strategy 4: Apply e↔o THEN reverse
        for eo_variant in apply_eo_substitution(word_clean):
            eo_reversed = eo_variant[::-1]
            if eo_reversed in vocab:
                results["eo_then_reversed"]["matches"].append(eo_reversed)
                results["eo_then_reversed"]["details"].append(
                    {
                        "original": word_clean,
                        "eo_variant": eo_variant,
                        "variant": eo_reversed,
                        "meaning": vocab[eo_reversed]["meaning"],
                        "category": vocab[eo_reversed]["category"],
                        "transform": "e↔o + reversed",
                    }
                )
                break

    return results


def main():
    print("=" * 80)
    print("TESTING WORD REVERSAL HYPOTHESIS")
    print("=" * 80)
    print()
    print("Hypothesis: Some words may be intentionally reversed as obfuscation.")
    print("This would be easy for the author to read/write but hard to detect.")
    print()

    vocab, section_4_words = load_data()
    total_words = len(section_4_words)

    print(f"Section 4 statistics:")
    print(f"  Total words: {total_words}")
    print(f"  Vocabulary size: {len(vocab)}")
    print()

    results = test_reversal_hypothesis(section_4_words, vocab)

    # Report results for each strategy
    print("=" * 80)
    print("STRATEGY 1: Direct match with e↔o (BASELINE)")
    print("=" * 80)
    direct_count = len(results["direct"]["matches"])
    direct_rate = 100 * direct_count / total_words
    print(f"Recognition: {direct_count}/{total_words} = {direct_rate:.2f}%")
    print()
    if results["direct"]["details"]:
        print("Matches:")
        for detail in results["direct"]["details"][:15]:
            print(
                f"  {detail['original']:15s} → {detail['variant']:15s} = {detail['meaning']:20s} ({detail['category']})"
            )
    print()

    print("=" * 80)
    print("STRATEGY 2: Pure reversal (no e↔o)")
    print("=" * 80)
    reversed_count = len(results["reversed"]["matches"])
    reversed_rate = 100 * reversed_count / total_words
    print(f"Recognition: {reversed_count}/{total_words} = {reversed_rate:.2f}%")
    print()
    if results["reversed"]["details"]:
        print("NEW MATCHES (not in baseline):")
        new_reversed = [
            d
            for d in results["reversed"]["details"]
            if d["variant"] not in [x["variant"] for x in results["direct"]["details"]]
        ]
        if new_reversed:
            for detail in new_reversed[:15]:
                print(
                    f"  {detail['original']:15s} → {detail['variant']:15s} (REVERSED) = {detail['meaning']:20s} ({detail['category']})"
                )
        else:
            print("  (All matches already found in baseline)")
    else:
        print("  No matches found")
    print()

    print("=" * 80)
    print("STRATEGY 3: Reverse THEN apply e↔o")
    print("=" * 80)
    rev_eo_count = len(results["reversed_then_eo"]["matches"])
    rev_eo_rate = 100 * rev_eo_count / total_words
    print(f"Recognition: {rev_eo_count}/{total_words} = {rev_eo_rate:.2f}%")
    print()
    if results["reversed_then_eo"]["details"]:
        print("NEW MATCHES (not in baseline or pure reversal):")
        baseline_variants = set([x["variant"] for x in results["direct"]["details"]])
        reversed_variants = set([x["variant"] for x in results["reversed"]["details"]])
        new_rev_eo = [
            d
            for d in results["reversed_then_eo"]["details"]
            if d["variant"] not in baseline_variants
            and d["variant"] not in reversed_variants
        ]
        if new_rev_eo:
            for detail in new_rev_eo[:15]:
                print(
                    f"  {detail['original']:15s} → {detail['reversed']:15s} (rev) → {detail['variant']:15s} (e↔o) = {detail['meaning']:20s}"
                )
                print(f"    Category: {detail['category']}")
        else:
            print("  (All matches already found in previous strategies)")
    else:
        print("  No matches found")
    print()

    print("=" * 80)
    print("STRATEGY 4: Apply e↔o THEN reverse")
    print("=" * 80)
    eo_rev_count = len(results["eo_then_reversed"]["matches"])
    eo_rev_rate = 100 * eo_rev_count / total_words
    print(f"Recognition: {eo_rev_count}/{total_words} = {eo_rev_rate:.2f}%")
    print()
    if results["eo_then_reversed"]["details"]:
        print("NEW MATCHES (not in any previous strategy):")
        all_previous = set([x["variant"] for x in results["direct"]["details"]])
        all_previous.update([x["variant"] for x in results["reversed"]["details"]])
        all_previous.update(
            [x["variant"] for x in results["reversed_then_eo"]["details"]]
        )
        new_eo_rev = [
            d
            for d in results["eo_then_reversed"]["details"]
            if d["variant"] not in all_previous
        ]
        if new_eo_rev:
            for detail in new_eo_rev[:15]:
                print(
                    f"  {detail['original']:15s} → {detail['eo_variant']:15s} (e↔o) → {detail['variant']:15s} (rev) = {detail['meaning']:20s}"
                )
                print(f"    Category: {detail['category']}")
        else:
            print("  (All matches already found in previous strategies)")
    else:
        print("  No matches found")
    print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    # Calculate total unique matches
    all_matches = set()
    for strategy in results.values():
        all_matches.update([d["variant"] for d in strategy["details"]])

    total_unique = len(all_matches)
    total_rate = 100 * total_unique / total_words

    print(
        f"Baseline (e↔o only):           {direct_count:3d} words ({direct_rate:.2f}%)"
    )
    print(
        f"Pure reversal:                 {reversed_count:3d} words ({reversed_rate:.2f}%)"
    )
    print(
        f"Reversed + e↔o:                {rev_eo_count:3d} words ({rev_eo_rate:.2f}%)"
    )
    print(
        f"e↔o + reversed:                {eo_rev_count:3d} words ({eo_rev_rate:.2f}%)"
    )
    print(f"TOTAL UNIQUE MATCHES:          {total_unique:3d} words ({total_rate:.2f}%)")
    print()

    improvement = total_rate - direct_rate
    print(f"Improvement from reversal hypothesis: +{improvement:.2f} percentage points")
    print()

    # Interpretation
    if improvement > 5:
        print("✓✓✓ STRONG EVIDENCE FOR REVERSAL")
        print("Word reversal significantly increases recognition rate.")
        print("This is likely a real obfuscation technique.")
    elif improvement > 2:
        print("✓✓ MODERATE EVIDENCE FOR REVERSAL")
        print("Some benefit from reversal hypothesis.")
        print("Worth investigating further.")
    elif improvement > 0.5:
        print("✓ WEAK EVIDENCE FOR REVERSAL")
        print("Slight improvement, possibly coincidental.")
    else:
        print("✗ NO EVIDENCE FOR REVERSAL")
        print("Reversal does not improve recognition.")
        print("Words are likely not reversed.")

    # Save results
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"
    output = {
        "section_id": 4,
        "total_words": total_words,
        "strategies": {
            "direct": {
                "count": direct_count,
                "rate": direct_rate,
                "matches": results["direct"]["details"],
            },
            "reversed": {
                "count": reversed_count,
                "rate": reversed_rate,
                "matches": results["reversed"]["details"],
            },
            "reversed_then_eo": {
                "count": rev_eo_count,
                "rate": rev_eo_rate,
                "matches": results["reversed_then_eo"]["details"],
            },
            "eo_then_reversed": {
                "count": eo_rev_count,
                "rate": eo_rev_rate,
                "matches": results["eo_then_reversed"]["details"],
            },
        },
        "summary": {
            "total_unique_matches": total_unique,
            "total_rate": total_rate,
            "improvement": improvement,
        },
    }

    output_path = results_dir / "word_reversal_test_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print()
    print(f"Results saved to: {output_path}")
    print()


if __name__ == "__main__":
    main()
