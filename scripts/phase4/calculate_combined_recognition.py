#!/usr/bin/env python3
"""
Calculate combined recognition from Phase 3 + Phase 4A
Determine true new coverage and updated statistics
"""

import json
from collections import Counter, defaultdict
from pathlib import Path


def load_voynich_text():
    """Load Voynich transcription."""
    with open(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt",
        "r",
        encoding="utf-8",
    ) as f:
        text = f.read()
    return text.split()


def load_phase3_recognized():
    """Load all Phase 3 recognized words."""
    recognized_words = set()

    # Load from various Phase 3 result files
    phase3_files = [
        "results/phase2/middle_english_matches.json",
        "results/phase3/reversed_terms_search_results.json",
        "results/phase3/consonant_pattern_results.json",
        "results/phase3/predicted_reversal_results.json",
    ]

    for filepath in phase3_files:
        try:
            with open(filepath, "r") as f:
                data = json.load(f)

                # Extract recognized words based on file structure
                if "findings" in data:
                    for finding in data["findings"]:
                        if "voynich_word" in finding:
                            recognized_words.add(finding["voynich_word"])
                        elif "word" in finding:
                            recognized_words.add(finding["word"])

                if "results" in data:
                    for result in data["results"]:
                        if "voynich_word" in result:
                            recognized_words.add(result["voynich_word"])
                        elif "word" in result:
                            recognized_words.add(result["word"])

                if "matches" in data:
                    for match in data["matches"]:
                        if "voynich_word" in match:
                            recognized_words.add(match["voynich_word"])
                        elif "word" in match:
                            recognized_words.add(match["word"])

        except FileNotFoundError:
            print(f"  (File not found: {filepath})")
            continue
        except Exception as e:
            print(f"  (Error loading {filepath}: {e})")
            continue

    # Also add known preserved ME words
    preserved_words = {
        "or",
        "and",
        "in",
        "of",
        "the",
        "is",
        "with",
        "for",
        "to",
        "at",
        "a",
        "an",
        "on",
        "by",
        "from",
        "as",
        "be",
        "not",
        "but",
        "all",
        "so",
        "if",
        "this",
        "that",
        "which",
        "who",
        "what",
        "where",
        "when",
        "there",
        "here",
        "then",
        "than",
        "them",
        "these",
        "those",
        "they",
    }
    recognized_words.update(preserved_words)

    return recognized_words


def load_phase4_results():
    """Load Phase 4A exhaustive search results."""
    with open("results/phase4/exhaustive_search_results.json", "r") as f:
        return json.load(f)


def calculate_combined_coverage():
    """Calculate combined Phase 3 + Phase 4A coverage."""

    print("=" * 80)
    print("COMBINED PHASE 3 + PHASE 4A RECOGNITION ANALYSIS")
    print("=" * 80)

    # Load data
    print("\nLoading data...")
    voynich_words = load_voynich_text()
    voynich_freqs = Counter(voynich_words)
    total_words = len(voynich_words)

    print(f"Total Voynich words: {total_words:,}")

    # Phase 3 recognized
    phase3_recognized = load_phase3_recognized()
    print(f"Phase 3 recognized word types: {len(phase3_recognized)}")

    # Count Phase 3 instances
    phase3_instances = sum(
        voynich_freqs[word] for word in phase3_recognized if word in voynich_freqs
    )
    print(
        f"Phase 3 instances: {phase3_instances:,} ({100 * phase3_instances / total_words:.2f}%)"
    )

    # Phase 4A results
    phase4_results = load_phase4_results()
    phase4_words = {r["voynich_word"] for r in phase4_results}
    phase4_instances = sum(r["frequency"] for r in phase4_results)

    print(f"\nPhase 4A word types: {len(phase4_words)}")
    print(f"Phase 4A instances: {phase4_instances:,}")

    # Find NEW words (not in Phase 3)
    new_words = phase4_words - phase3_recognized
    new_instances = sum(voynich_freqs[word] for word in new_words)

    print(f"\nNEW in Phase 4A:")
    print(f"  Word types: {len(new_words)}")
    print(f"  Instances: {new_instances:,}")

    # Combined total
    combined_words = phase3_recognized | phase4_words
    combined_instances = sum(
        voynich_freqs[word] for word in combined_words if word in voynich_freqs
    )

    print(f"\nCOMBINED (Phase 3 + 4A):")
    print(f"  Unique words: {len(combined_words)}")
    print(f"  Total instances: {combined_instances:,}")
    print(f"  Recognition rate: {100 * combined_instances / total_words:.2f}%")

    # Top NEW discoveries
    print("\n" + "-" * 80)
    print("TOP 20 NEW DISCOVERIES (Phase 4A only)")
    print("-" * 80)

    new_with_freq = [
        (word, voynich_freqs[word]) for word in new_words if word in voynich_freqs
    ]
    new_with_freq.sort(key=lambda x: x[1], reverse=True)

    # Map to ME words
    voynich_to_me = {r["voynich_word"]: r for r in phase4_results}

    print(f"{'Voynich':<15} {'Freq':>6} {'ME Word':<15} {'Meaning':<25} {'Category'}")
    print("-" * 80)
    for voynich_word, freq in new_with_freq[:20]:
        if voynich_word in voynich_to_me:
            r = voynich_to_me[voynich_word]
            print(
                f"{voynich_word:<15} {freq:6} {r['me_word']:<15} {r['meaning']:<25} {r['category']}"
            )

    # Breakdown by transform type
    print("\n" + "-" * 80)
    print("NEW WORDS BY TRANSFORM TYPE")
    print("-" * 80)

    transform_breakdown = defaultdict(lambda: {"count": 0, "instances": 0})
    for voynich_word in new_words:
        if voynich_word in voynich_to_me:
            trans = voynich_to_me[voynich_word]["transform_applied"]
            transform_breakdown[trans]["count"] += 1
            transform_breakdown[trans]["instances"] += voynich_freqs[voynich_word]

    for trans in sorted(
        transform_breakdown.keys(),
        key=lambda t: transform_breakdown[t]["instances"],
        reverse=True,
    ):
        data = transform_breakdown[trans]
        print(f"{trans:30} {data['count']:3} words, {data['instances']:5} instances")

    # Category breakdown
    print("\n" + "-" * 80)
    print("NEW WORDS BY CATEGORY")
    print("-" * 80)

    category_breakdown = defaultdict(lambda: {"count": 0, "instances": 0})
    for voynich_word in new_words:
        if voynich_word in voynich_to_me:
            cat = voynich_to_me[voynich_word]["category"]
            category_breakdown[cat]["count"] += 1
            category_breakdown[cat]["instances"] += voynich_freqs[voynich_word]

    for cat in sorted(
        category_breakdown.keys(),
        key=lambda c: category_breakdown[c]["instances"],
        reverse=True,
    ):
        data = category_breakdown[cat]
        print(f"{cat:20} {data['count']:3} words, {data['instances']:5} instances")

    # Calculate improvement
    print("\n" + "=" * 80)
    print("PHASE 4A IMPROVEMENT")
    print("=" * 80)

    improvement_pct = (new_instances / total_words) * 100
    print(f"\nPhase 3 recognition: {100 * phase3_instances / total_words:.2f}%")
    print(f"Phase 4A added: +{improvement_pct:.2f}%")
    print(f"Combined total: {100 * combined_instances / total_words:.2f}%")

    # Estimate transformed vs preserved
    # Rough estimate: preserved words are common English function words
    preserved_estimate = {
        word for word in combined_words if len(word) <= 3 and word.isalpha()
    }
    preserved_count = sum(
        voynich_freqs[word] for word in preserved_estimate if word in voynich_freqs
    )

    transformed_count = combined_instances - preserved_count

    print(f"\nEstimated breakdown:")
    print(f"  Transformed (deciphered): ~{100 * transformed_count / total_words:.2f}%")
    print(f"  Preserved (plain ME): ~{100 * preserved_count / total_words:.2f}%")

    # Progress toward goal
    print("\n" + "-" * 80)
    print("PROGRESS TOWARD 3-4% TRANSFORMED GOAL")
    print("-" * 80)

    goal_low = 0.03 * total_words  # 3%
    goal_high = 0.04 * total_words  # 4%

    print(
        f"\nCurrent transformed: {transformed_count:,} words ({100 * transformed_count / total_words:.2f}%)"
    )
    print(f"Goal (3%): {int(goal_low):,} words")
    print(f"Goal (4%): {int(goal_high):,} words")
    print(f"Progress: {100 * transformed_count / goal_high:.1f}% of 4% goal")

    if transformed_count >= goal_low:
        print("\n✓ Achieved 3% transformed recognition!")
    if transformed_count >= goal_high:
        print("✓ Achieved 4% transformed recognition!")
    else:
        needed = int(goal_high - transformed_count)
        print(f"\nNeed {needed:,} more instances to reach 4% goal")

    # Save combined results
    output = {
        "total_words": total_words,
        "phase3_instances": phase3_instances,
        "phase4_new_instances": new_instances,
        "combined_instances": combined_instances,
        "combined_recognition_rate": 100 * combined_instances / total_words,
        "transformed_estimate": transformed_count,
        "transformed_rate": 100 * transformed_count / total_words,
        "preserved_estimate": preserved_count,
        "new_word_types": len(new_words),
        "new_words_list": list(new_words),
    }

    output_path = Path("results/phase4/combined_recognition_stats.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nStats saved to: {output_path}")


def main():
    calculate_combined_coverage()


if __name__ == "__main__":
    main()
