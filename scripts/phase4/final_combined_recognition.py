#!/usr/bin/env python3
"""
Calculate FINAL combined recognition from ALL Phase 4A findings
"""

import json
from collections import Counter
from pathlib import Path


def load_all_results():
    """Load all Phase 4A results."""

    # Voynich text
    with open(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt",
        "r",
        encoding="utf-8",
    ) as f:
        voynich_words = f.read().split()
    voynich_freqs = Counter(voynich_words)
    total_words = len(voynich_words)

    # Phase 3 consolidated (from original analysis)
    with open("results/phase3/consolidated_findings.json", "r") as f:
        phase3_data = json.load(f)

    # Phase 4A exhaustive search
    with open("results/phase4/exhaustive_search_results.json", "r") as f:
        exhaustive_results = json.load(f)

    # Phase 4A compound/partial matches
    with open("results/phase4/compound_and_partial_matches.json", "r") as f:
        compound_data = json.load(f)

    return voynich_freqs, total_words, phase3_data, exhaustive_results, compound_data


def main():
    print("=" * 80)
    print("FINAL PHASE 4A RECOGNITION CALCULATION")
    print("=" * 80)

    voynich_freqs, total_words, phase3_data, exhaustive_results, compound_data = (
        load_all_results()
    )

    print(f"\nTotal Voynich words in current transcription: {total_words:,}")

    # Collect all recognized words
    all_recognized = set()

    # From exhaustive search
    exhaustive_words = {r["voynich_word"] for r in exhaustive_results}
    exhaustive_instances = sum(r["frequency"] for r in exhaustive_results)
    all_recognized.update(exhaustive_words)

    print(f"\nExhaustive vocabulary search:")
    print(f"  Word types: {len(exhaustive_words)}")
    print(f"  Instances: {exhaustive_instances:,}")

    # From partial matches
    partial_words = {pm["voynich_word"] for pm in compound_data["partial_matches"]}
    partial_instances = sum(pm["frequency"] for pm in compound_data["partial_matches"])
    all_recognized.update(partial_words)

    print(f"\nPartial matches (affixed words):")
    print(f"  Word types: {len(partial_words)}")
    print(f"  Instances: {partial_instances:,}")

    # Calculate combined (removing overlap)
    combined_instances = sum(
        voynich_freqs[w] for w in all_recognized if w in voynich_freqs
    )

    print(f"\n" + "-" * 80)
    print("COMBINED PHASE 4A RESULTS")
    print("-" * 80)
    print(f"\nTotal unique words recognized: {len(all_recognized)}")
    print(f"Total instances: {combined_instances:,}")
    print(f"Recognition rate: {100 * combined_instances / total_words:.2f}%")

    # Breakdown by source
    exhaustive_only = exhaustive_words - partial_words
    partial_only = partial_words - exhaustive_words
    both = exhaustive_words & partial_words

    print(f"\nBreakdown:")
    print(f"  Exhaustive search only: {len(exhaustive_only)} words")
    print(f"  Partial matches only: {len(partial_only)} words")
    print(f"  Both: {len(both)} words")

    # Estimate transformed vs preserved
    # Words 1-3 chars are likely preserved
    # Words 4+ chars with matches are likely transformed
    preserved_words = {w for w in all_recognized if len(w) <= 3}
    transformed_words = all_recognized - preserved_words

    preserved_instances = sum(
        voynich_freqs[w] for w in preserved_words if w in voynich_freqs
    )
    transformed_instances = sum(
        voynich_freqs[w] for w in transformed_words if w in voynich_freqs
    )

    print(f"\n" + "-" * 80)
    print("TRANSFORMED VS PRESERVED")
    print("-" * 80)
    print(
        f"\nPreserved (plain ME, 1-3 chars): {len(preserved_words)} types, {preserved_instances:,} instances ({100 * preserved_instances / total_words:.2f}%)"
    )
    print(
        f"Transformed (deciphered, 4+ chars): {len(transformed_words)} types, {transformed_instances:,} instances ({100 * transformed_instances / total_words:.2f}%)"
    )

    # Goal progress
    goal_3pct = int(0.03 * total_words)
    goal_4pct = int(0.04 * total_words)

    print(f"\n" + "-" * 80)
    print("PROGRESS TOWARD GOALS")
    print("-" * 80)
    print(f"\nGoal: 3-4% transformed recognition")
    print(f"  3% target: {goal_3pct:,} instances")
    print(f"  4% target: {goal_4pct:,} instances")
    print(
        f"\nCurrent transformed: {transformed_instances:,} instances ({100 * transformed_instances / total_words:.2f}%)"
    )

    if transformed_instances >= goal_4pct:
        print("\n✓✓ ACHIEVED 4% TRANSFORMED RECOGNITION!")
    elif transformed_instances >= goal_3pct:
        print("\n✓ ACHIEVED 3% TRANSFORMED RECOGNITION!")
        shortfall = goal_4pct - transformed_instances
        print(f"  ({shortfall:,} more instances needed for 4%)")
    else:
        shortfall = goal_3pct - transformed_instances
        print(f"\nNeed {shortfall:,} more instances to reach 3% goal")

    # Category breakdown
    print(f"\n" + "-" * 80)
    print("TOP CATEGORIES (from partial matches)")
    print("-" * 80)

    category_counts = {}
    for pm in compound_data["partial_matches"]:
        cat = pm["category"]
        category_counts[cat] = category_counts.get(cat, 0) + pm["frequency"]

    for cat in sorted(
        category_counts.keys(), key=lambda c: category_counts[c], reverse=True
    ):
        count = category_counts[cat]
        print(f"  {cat:20} {count:5,} instances ({100 * count / total_words:.2f}%)")

    # Top words
    print(f"\n" + "-" * 80)
    print("TOP 30 RECOGNIZED WORDS (all sources)")
    print("-" * 80)

    all_with_freq = [
        (w, voynich_freqs[w]) for w in all_recognized if w in voynich_freqs
    ]
    all_with_freq.sort(key=lambda x: x[1], reverse=True)

    # Map to meanings
    exhaustive_map = {r["voynich_word"]: r for r in exhaustive_results}
    partial_map = {pm["voynich_word"]: pm for pm in compound_data["partial_matches"]}

    print(f"\n{'Voynich':<15} {'Freq':>6} {'Source':<12} {'ME/Root':<12} {'Meaning'}")
    print("-" * 80)
    for voynich_word, freq in all_with_freq[:30]:
        if voynich_word in partial_map:
            pm = partial_map[voynich_word]
            source = "partial"
            me_word = pm["me_word"]
            meaning = pm["meaning"]
        elif voynich_word in exhaustive_map:
            ex = exhaustive_map[voynich_word]
            source = "exhaustive"
            me_word = ex["me_word"]
            meaning = ex["meaning"]
        else:
            source = "unknown"
            me_word = "?"
            meaning = "?"

        print(f"{voynich_word:<15} {freq:6} {source:<12} {me_word:<12} {meaning}")

    # Save final stats
    output = {
        "total_voynich_words": total_words,
        "recognized_word_types": len(all_recognized),
        "recognized_instances": combined_instances,
        "overall_recognition_rate": 100 * combined_instances / total_words,
        "transformed_instances": transformed_instances,
        "transformed_rate": 100 * transformed_instances / total_words,
        "preserved_instances": preserved_instances,
        "preserved_rate": 100 * preserved_instances / total_words,
        "sources": {
            "exhaustive_search": {
                "types": len(exhaustive_words),
                "instances": exhaustive_instances,
            },
            "partial_matches": {
                "types": len(partial_words),
                "instances": partial_instances,
            },
        },
        "goals": {
            "3pct_target": goal_3pct,
            "4pct_target": goal_4pct,
            "achieved_3pct": transformed_instances >= goal_3pct,
            "achieved_4pct": transformed_instances >= goal_4pct,
        },
    }

    output_path = Path("results/phase4/final_recognition_stats.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\nFinal stats saved to: {output_path}")

    print("\n" + "=" * 80)
    print("PHASE 4A COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
