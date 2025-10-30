#!/usr/bin/env python3
"""
Investigate [?a], [?y], [?k] affixation patterns.

These elements appear almost exclusively AFFIXED (not standalone),
suggesting they might be BOUND morphemes (suffixes/prefixes) rather
than independent roots.

Analysis:
1. What positions do they appear in? (prefix, suffix, infix)
2. What do they attach to? (stems, other affixes)
3. Do they form consistent patterns?
"""

import json
import re
from collections import Counter


def load_translations():
    with open(
        "COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)
        return data["translations"]


def analyze_affixation_patterns(root_pattern, translations):
    """
    Analyze WHERE this element appears in words.

    Position types:
    - PREFIX: word starts with root-
    - SUFFIX: word ends with -root
    - INFIX: root appears between other morphemes
    - STANDALONE: root appears alone
    """

    positions = {
        "prefix": 0,  # ?a-something
        "suffix": 0,  # something-?a
        "infix": 0,  # something-?a-something
        "standalone": 0,  # ?a by itself
    }

    prefix_stems = Counter()  # What comes AFTER when prefix
    suffix_stems = Counter()  # What comes BEFORE when suffix

    for trans in translations:
        words = trans["final_translation"].replace("[", " [").replace("]", "] ").split()

        for word in words:
            if root_pattern not in word:
                continue

            # Clean up word
            word = word.strip(".,;:!?")

            # Standalone
            if word == root_pattern:
                positions["standalone"] += 1
                continue

            # Split on hyphens to analyze structure
            parts = word.split("-")

            # Find position of root
            try:
                idx = parts.index(root_pattern)
            except ValueError:
                # Root is part of a compound, skip for now
                continue

            if idx == 0:
                # PREFIX: ?a-STEM-...
                positions["prefix"] += 1
                if len(parts) > 1:
                    prefix_stems[parts[1]] += 1
            elif idx == len(parts) - 1:
                # SUFFIX: STEM-?a
                positions["suffix"] += 1
                if len(parts) > 1:
                    suffix_stems[parts[-2]] += 1
            else:
                # INFIX: STEM-?a-SUFFIX
                positions["infix"] += 1

    total = sum(positions.values())

    return {
        "positions": positions,
        "total": total,
        "prefix_stems": prefix_stems.most_common(10),
        "suffix_stems": suffix_stems.most_common(10),
    }


def main():
    print("=" * 70)
    print("AFFIXATION PATTERN INVESTIGATION: [?a], [?y], [?k]")
    print("=" * 70)
    print()
    print("Goal: Determine if these are BOUND morphemes (affixes)")
    print("      rather than independent roots")
    print()

    translations = load_translations()

    for root in ["?a", "?y", "?k"]:
        print("=" * 70)
        print(f"ANALYZING [{root}]")
        print("=" * 70)

        results = analyze_affixation_patterns(root, translations)

        total = results["total"]
        positions = results["positions"]

        print(f"\nTotal instances: {total}")
        print(f"\nPosition distribution:")
        print(
            f"  PREFIX ({root}-STEM):     {positions['prefix']:4d} ({positions['prefix'] / total * 100:5.1f}%)"
        )
        print(
            f"  SUFFIX (STEM-{root}):     {positions['suffix']:4d} ({positions['suffix'] / total * 100:5.1f}%)"
        )
        print(
            f"  INFIX (STEM-{root}-AFF):  {positions['infix']:4d} ({positions['infix'] / total * 100:5.1f}%)"
        )
        print(
            f"  STANDALONE ({root}):      {positions['standalone']:4d} ({positions['standalone'] / total * 100:5.1f}%)"
        )

        # Classification
        print(f"\n{'=' * 70}")
        print("CLASSIFICATION:")

        prefix_pct = positions["prefix"] / total * 100
        suffix_pct = positions["suffix"] / total * 100
        infix_pct = positions["infix"] / total * 100
        standalone_pct = positions["standalone"] / total * 100

        if suffix_pct > 70:
            print(f"  → LIKELY SUFFIX (appears after stems {suffix_pct:.1f}% of time)")
            print(f"\n  Top stems that take -{root}:")
            for stem, count in results["suffix_stems"]:
                print(f"    {stem}-{root}: {count}×")
        elif prefix_pct > 70:
            print(f"  → LIKELY PREFIX (appears before stems {prefix_pct:.1f}% of time)")
            print(f"\n  Top stems after {root}-:")
            for stem, count in results["prefix_stems"]:
                print(f"    {root}-{stem}: {count}×")
        elif infix_pct > 50:
            print(
                f"  → LIKELY INFIX/DERIVATIONAL (appears between morphemes {infix_pct:.1f}% of time)"
            )
        elif standalone_pct > 30:
            print(f"  → LIKELY ROOT (appears standalone {standalone_pct:.1f}% of time)")
        else:
            print(f"  → UNCLEAR PATTERN")
            print(f"    Suffix: {suffix_pct:.1f}%")
            print(f"    Prefix: {prefix_pct:.1f}%")
            print(f"    Infix: {infix_pct:.1f}%")
            print(f"    Standalone: {standalone_pct:.1f}%")

        print()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("If any of these are SUFFIXES, they may explain why they have")
    print("low VERB suffix rates - they themselves ARE suffixes!")
    print()
    print("This would be a major classification error in previous analysis.")
    print()


if __name__ == "__main__":
    main()
