#!/usr/bin/env python3
"""
Search full manuscript for reversed common medical terms.

Tests the WORD FREQUENCY hypothesis: High-frequency medical terms
are more likely to be reversed.

Strategy:
1. Identify most common medical terms in Middle English herbals
2. Generate reversed + e↔o variants for each
3. Search full manuscript for these patterns
4. Calculate frequency and distribution
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from itertools import product


def load_manuscript():
    """Load full manuscript text."""
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"

    with open(
        results_dir / "full_manuscript_translation.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)

    # Extract all words
    all_words = []
    for section in data["sections"]:
        words = section["original"].split()
        all_words.extend(words)

    return all_words, data["sections"]


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


def generate_reversal_variants(word):
    """
    Generate all reversal + e↔o variants for a word.

    Example: "root" generates:
    - Direct: root, reet, ruut, rout
    - Reversed: toor, teor, teur, taor
    """
    variants = {"direct": [], "reversed": []}

    # Direct with e↔o
    for eo_var in apply_eo_substitution(word):
        variants["direct"].append(eo_var)

    # Reversed with e↔o
    reversed_word = word[::-1]
    for eo_var in apply_eo_substitution(reversed_word):
        variants["reversed"].append(eo_var)

    return variants


def search_term_in_manuscript(term, variants, all_words):
    """
    Search for all variants of a term in the manuscript.
    Returns matches with positions and transform types.
    """
    matches = {"direct": [], "reversed": []}

    # Create word position map
    for pos, word in enumerate(all_words):
        word_clean = word.lower().strip(".,;:!?")

        # Check direct matches
        if word_clean in variants["direct"]:
            matches["direct"].append(
                {
                    "position": pos,
                    "voynich": word_clean,
                    "english": term,
                    "variant": word_clean,
                }
            )

        # Check reversed matches
        if word_clean in variants["reversed"]:
            matches["reversed"].append(
                {
                    "position": pos,
                    "voynich": word_clean,
                    "english": term,
                    "variant": word_clean,
                    "reversed_from": word_clean[::-1],
                }
            )

    return matches


def main():
    print("=" * 80)
    print("SEARCHING FULL MANUSCRIPT FOR REVERSED MEDICAL TERMS")
    print("=" * 80)
    print()
    print("Testing WORD FREQUENCY hypothesis:")
    print("High-frequency medical terms are more likely to be reversed.")
    print()

    # Define most common medical terms in Middle English herbals
    # (based on frequency in medieval medical texts)
    high_frequency_terms = {
        # Plant parts (very common)
        "root": {"category": "plant_parts", "frequency": "very_high"},
        "leaf": {"category": "plant_parts", "frequency": "very_high"},
        "sede": {"category": "plant_parts", "frequency": "high"},  # seed
        "flour": {"category": "plant_parts", "frequency": "high"},  # flower
        "bark": {"category": "plant_parts", "frequency": "medium"},
        "stem": {"category": "plant_parts", "frequency": "medium"},
        # Body parts (very common)
        "hed": {"category": "body_parts", "frequency": "very_high"},  # head
        "ye": {"category": "body_parts", "frequency": "high"},  # eye
        "ere": {"category": "body_parts", "frequency": "high"},  # ear
        "hond": {"category": "body_parts", "frequency": "high"},  # hand
        "blod": {"category": "body_parts", "frequency": "very_high"},  # blood
        "herte": {"category": "body_parts", "frequency": "high"},  # heart
        # Common conditions
        "peyn": {"category": "conditions", "frequency": "very_high"},  # pain
        "sor": {"category": "conditions", "frequency": "very_high"},  # sore
        "ache": {"category": "conditions", "frequency": "high"},
        "fevir": {"category": "conditions", "frequency": "high"},  # fever
        # Recipe instructions (very common)
        "tak": {"category": "instructions", "frequency": "very_high"},  # take
        "boil": {"category": "instructions", "frequency": "very_high"},
        "drynke": {"category": "instructions", "frequency": "very_high"},  # drink
        "grind": {"category": "instructions", "frequency": "high"},
        "mak": {"category": "instructions", "frequency": "very_high"},  # make
    }

    print(f"Searching for {len(high_frequency_terms)} high-frequency medical terms")
    print()

    # Load manuscript
    all_words, sections = load_manuscript()
    total_words = len(all_words)
    print(f"Manuscript: {total_words:,} words")
    print()

    # Search for each term
    results = {}

    for term, info in high_frequency_terms.items():
        variants = generate_reversal_variants(term)
        matches = search_term_in_manuscript(term, variants, all_words)

        total_matches = len(matches["direct"]) + len(matches["reversed"])

        results[term] = {
            "info": info,
            "variants": variants,
            "matches": matches,
            "total": total_matches,
            "direct_count": len(matches["direct"]),
            "reversed_count": len(matches["reversed"]),
            "reversal_rate": len(matches["reversed"]) / total_matches
            if total_matches > 0
            else 0,
        }

    # Sort by total matches (most frequent first)
    sorted_results = sorted(results.items(), key=lambda x: x[1]["total"], reverse=True)

    print("=" * 80)
    print("RESULTS: Terms Found in Manuscript")
    print("=" * 80)
    print()

    found_terms = [(term, data) for term, data in sorted_results if data["total"] > 0]
    not_found = [(term, data) for term, data in sorted_results if data["total"] == 0]

    if found_terms:
        print(f"FOUND {len(found_terms)} terms:")
        print()

        for term, data in found_terms:
            print(f"{term:15s} ({data['info']['category']:15s}):")
            print(f"  Total matches: {data['total']:3d}")
            print(
                f"  Direct (e↔o):  {data['direct_count']:3d} ({data['direct_count'] / data['total'] * 100:.1f}%)"
            )
            print(
                f"  Reversed:      {data['reversed_count']:3d} ({data['reversed_count'] / data['total'] * 100:.1f}%)"
            )

            if data["reversed_count"] > 0:
                print(f"  ⚠️  REVERSAL DETECTED! {data['reversed_count']} instances")
                print(f"     Sample reversed matches:")
                for match in data["matches"]["reversed"][:3]:
                    print(
                        f"       Position {match['position']:6d}: '{match['voynich']}'"
                    )
            print()

    if not_found:
        print(f"\nNOT FOUND ({len(not_found)} terms):")
        for term, data in not_found[:5]:
            print(f"  {term:15s} ({data['info']['category']})")
        if len(not_found) > 5:
            print(f"  ... and {len(not_found) - 5} more")
        print()

    # Analyze reversal patterns
    print("=" * 80)
    print("REVERSAL PATTERN ANALYSIS")
    print("=" * 80)
    print()

    # Group by category
    category_stats = defaultdict(lambda: {"total": 0, "direct": 0, "reversed": 0})

    for term, data in found_terms:
        cat = data["info"]["category"]
        category_stats[cat]["total"] += data["total"]
        category_stats[cat]["direct"] += data["direct_count"]
        category_stats[cat]["reversed"] += data["reversed_count"]

    if category_stats:
        print("By semantic category:")
        for cat, stats in sorted(category_stats.items()):
            rev_rate = (
                stats["reversed"] / stats["total"] * 100 if stats["total"] > 0 else 0
            )
            print(
                f"  {cat:20s}: {stats['total']:4d} total, {stats['reversed']:3d} reversed ({rev_rate:.1f}%)"
            )
        print()

    # Group by frequency
    freq_stats = defaultdict(lambda: {"total": 0, "direct": 0, "reversed": 0})

    for term, data in found_terms:
        freq = data["info"]["frequency"]
        freq_stats[freq]["total"] += data["total"]
        freq_stats[freq]["direct"] += data["direct_count"]
        freq_stats[freq]["reversed"] += data["reversed_count"]

    if freq_stats:
        print("By term frequency (in medical texts):")
        for freq in ["very_high", "high", "medium"]:
            if freq in freq_stats:
                stats = freq_stats[freq]
                rev_rate = (
                    stats["reversed"] / stats["total"] * 100
                    if stats["total"] > 0
                    else 0
                )
                print(
                    f"  {freq:15s}: {stats['total']:4d} total, {stats['reversed']:3d} reversed ({rev_rate:.1f}%)"
                )
        print()

    # Test hypothesis
    print("=" * 80)
    print("HYPOTHESIS TEST: Word Frequency → Reversal Rate")
    print("=" * 80)
    print()

    if freq_stats:
        very_high_rev = (
            freq_stats["very_high"]["reversed"] / freq_stats["very_high"]["total"] * 100
            if freq_stats["very_high"]["total"] > 0
            else 0
        )
        high_rev = (
            freq_stats["high"]["reversed"] / freq_stats["high"]["total"] * 100
            if freq_stats["high"]["total"] > 0
            else 0
        )
        medium_rev = (
            freq_stats["medium"]["reversed"] / freq_stats["medium"]["total"] * 100
            if freq_stats["medium"]["total"] > 0
            else 0
        )

        print("Reversal rate by frequency:")
        print(f"  Very high frequency: {very_high_rev:.1f}%")
        print(f"  High frequency:      {high_rev:.1f}%")
        print(f"  Medium frequency:    {medium_rev:.1f}%")
        print()

        if very_high_rev > high_rev > medium_rev:
            print("✓✓✓ STRONG SUPPORT for frequency hypothesis")
            print("Higher frequency terms ARE more likely to be reversed.")
        elif very_high_rev > medium_rev:
            print("✓ MODERATE SUPPORT for frequency hypothesis")
            print("Some correlation between frequency and reversal.")
        else:
            print("✗ NO SUPPORT for frequency hypothesis")
            print("Reversal rate does not correlate with term frequency.")

    # Save results
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"
    output = {
        "total_words": total_words,
        "terms_searched": len(high_frequency_terms),
        "terms_found": len(found_terms),
        "results": {
            term: {
                "category": data["info"]["category"],
                "frequency": data["info"]["frequency"],
                "total_matches": data["total"],
                "direct_matches": data["direct_count"],
                "reversed_matches": data["reversed_count"],
                "reversal_rate": data["reversal_rate"],
                "sample_positions": [
                    m["position"] for m in data["matches"]["reversed"][:10]
                ],
            }
            for term, data in results.items()
        },
        "category_stats": dict(category_stats),
        "frequency_stats": dict(freq_stats),
    }

    output_path = results_dir / "reversed_terms_search_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print()
    print(f"Results saved to: {output_path}")
    print()


if __name__ == "__main__":
    main()
