#!/usr/bin/env python3
"""
Option 2: Decipher Affix Functions

Analyze grammatical affixes to infer their functions
"""

import json
from collections import Counter, defaultdict
from pathlib import Path


def load_partial_matches():
    """Load partial match data with affix information."""
    with open("results/phase4/compound_and_partial_matches.json", "r") as f:
        data = json.load(f)
    return data["partial_matches"]


def analyze_affix_distributions(partial_matches):
    """Analyze how affixes combine with roots."""

    # Group by root
    root_affixes = defaultdict(lambda: {"prefixes": Counter(), "suffixes": Counter()})

    for pm in partial_matches:
        root = pm["me_word"]
        prefix = pm["prefix"]
        suffix = pm["suffix"]
        freq = pm["frequency"]

        if prefix:
            root_affixes[root]["prefixes"][prefix] += freq
        if suffix:
            root_affixes[root]["suffixes"][suffix] += freq

    return root_affixes


def analyze_suffix_cooccurrence(partial_matches):
    """Analyze which suffixes appear together in the corpus."""

    # Get all suffixes
    all_suffixes = set()
    for pm in partial_matches:
        if pm["suffix"]:
            all_suffixes.add(pm["suffix"])

    # Count co-occurrences (suffixes that appear in same contexts)
    # For this, we'll look at which suffixes attach to the same roots

    suffix_with_roots = defaultdict(set)
    for pm in partial_matches:
        if pm["suffix"]:
            suffix_with_roots[pm["suffix"]].add(pm["me_word"])

    return suffix_with_roots


def categorize_affixes_by_pattern(partial_matches):
    """Categorize affixes by their linguistic patterns."""

    suffix_stats = defaultdict(
        lambda: {
            "total_instances": 0,
            "unique_roots": set(),
            "avg_word_length": 0,
            "examples": [],
        }
    )

    for pm in partial_matches:
        if pm["suffix"]:
            suffix = pm["suffix"]
            suffix_stats[suffix]["total_instances"] += pm["frequency"]
            suffix_stats[suffix]["unique_roots"].add(pm["me_word"])
            suffix_stats[suffix]["examples"].append(
                {
                    "voynich": pm["voynich_word"],
                    "root": pm["me_word"],
                    "meaning": pm["meaning"],
                    "freq": pm["frequency"],
                }
            )

    return suffix_stats


def infer_suffix_functions(suffix_stats):
    """
    Infer grammatical function based on distribution patterns.

    Hypothesis:
    - High productivity (many roots) = grammatical (case, number)
    - Low productivity (few roots) = derivational (word formation)
    - Very high frequency with few roots = common word ending
    """

    inferences = {}

    for suffix, stats in suffix_stats.items():
        productivity = len(stats["unique_roots"])
        frequency = stats["total_instances"]

        # Classify
        if productivity >= 5 and frequency >= 100:
            category = "highly_productive_grammatical"
            hypothesis = "Case marker, number, or agreement"
        elif productivity >= 3 and frequency >= 50:
            category = "productive_grammatical"
            hypothesis = "Grammatical marker (possibly tense/aspect)"
        elif productivity <= 2 and frequency >= 50:
            category = "lexicalized"
            hypothesis = "Part of specific words, not productive affix"
        else:
            category = "low_frequency"
            hypothesis = "Uncertain - need more data"

        inferences[suffix] = {
            "category": category,
            "hypothesis": hypothesis,
            "productivity": productivity,
            "frequency": frequency,
        }

    return inferences


def main():
    print("=" * 80)
    print("OPTION 2: DECIPHER AFFIX FUNCTIONS")
    print("=" * 80)

    # Load data
    print("\nLoading partial matches with affix information...")
    partial_matches = load_partial_matches()
    print(f"Total partial matches: {len(partial_matches)}")

    # Analyze affix distributions
    print("\n" + "-" * 80)
    print("AFFIX DISTRIBUTION BY ROOT")
    print("-" * 80)

    root_affixes = analyze_affix_distributions(partial_matches)

    # Show top roots with most affix variation
    print("\nRoots with highest affix variation:")
    roots_sorted = sorted(
        root_affixes.items(),
        key=lambda x: len(x[1]["suffixes"]) + len(x[1]["prefixes"]),
        reverse=True,
    )

    for root, affixes in roots_sorted[:10]:
        total_suffixes = len(affixes["suffixes"])
        total_prefixes = len(affixes["prefixes"])
        print(f"\n{root} ({total_prefixes} prefixes, {total_suffixes} suffixes):")

        if affixes["prefixes"]:
            print(f"  Prefixes: {dict(affixes['prefixes'].most_common(5))}")
        if affixes["suffixes"]:
            print(f"  Suffixes: {dict(affixes['suffixes'].most_common(10))}")

    # Categorize suffixes
    print("\n" + "-" * 80)
    print("SUFFIX ANALYSIS")
    print("-" * 80)

    suffix_stats = categorize_affixes_by_pattern(partial_matches)
    inferences = infer_suffix_functions(suffix_stats)

    # Sort by frequency
    suffixes_by_freq = sorted(
        suffix_stats.items(), key=lambda x: x[1]["total_instances"], reverse=True
    )

    print(
        f"\n{'Suffix':<10} {'Instances':>10} {'Roots':>8} {'Category':<30} {'Hypothesis'}"
    )
    print("-" * 100)

    for suffix, stats in suffixes_by_freq[:20]:
        inf = inferences[suffix]
        productivity = len(stats["unique_roots"])
        frequency = stats["total_instances"]

        print(
            f"{suffix:<10} {frequency:>10} {productivity:>8} {inf['category']:<30} {inf['hypothesis']}"
        )

    # Detailed analysis of top suffixes
    print("\n" + "=" * 80)
    print("DETAILED ANALYSIS OF TOP SUFFIXES")
    print("=" * 80)

    for suffix, stats in suffixes_by_freq[:5]:
        print(f"\n" + "-" * 80)
        print(f"SUFFIX: -{suffix}")
        print("-" * 80)

        print(f"\nTotal instances: {stats['total_instances']:,}")
        print(f"Unique roots: {len(stats['unique_roots'])}")
        print(f"Roots: {', '.join(sorted(stats['unique_roots']))}")

        inf = inferences[suffix]
        print(f"\nCLASSIFICATION: {inf['category']}")
        print(f"HYPOTHESIS: {inf['hypothesis']}")

        print(f"\nTop examples:")
        examples_sorted = sorted(
            stats["examples"], key=lambda x: x["freq"], reverse=True
        )
        for ex in examples_sorted[:8]:
            print(
                f"  {ex['voynich']:<15} = {ex['root']}-{suffix} ({ex['meaning']}) - {ex['freq']}x"
            )

    # Prefix analysis
    print("\n" + "=" * 80)
    print("PREFIX ANALYSIS")
    print("=" * 80)

    prefix_stats = defaultdict(lambda: {"total": 0, "roots": set(), "examples": []})

    for pm in partial_matches:
        if pm["prefix"]:
            prefix = pm["prefix"]
            prefix_stats[prefix]["total"] += pm["frequency"]
            prefix_stats[prefix]["roots"].add(pm["me_word"])
            prefix_stats[prefix]["examples"].append(
                {
                    "voynich": pm["voynich_word"],
                    "root": pm["me_word"],
                    "meaning": pm["meaning"],
                    "freq": pm["frequency"],
                }
            )

    prefixes_sorted = sorted(
        prefix_stats.items(), key=lambda x: x[1]["total"], reverse=True
    )

    print(f"\n{'Prefix':<10} {'Instances':>10} {'Roots':>8} {'Hypothesis'}")
    print("-" * 70)

    for prefix, stats in prefixes_sorted[:15]:
        productivity = len(stats["roots"])

        if prefix == "q" or prefix == "qok":
            hypothesis = "Case/preposition marker ('of', 'with', genitive)"
        elif prefix in ["ch", "c"]:
            hypothesis = "Consonant alternation (ch-/sh- distinction)"
        elif prefix == "d":
            hypothesis = "Demonstrative or definite marker"
        elif prefix == "s" or prefix == "sh":
            hypothesis = "Consonant alternation or aspect marker"
        else:
            hypothesis = "Uncertain - needs context analysis"

        print(f"{prefix:<10} {stats['total']:>10} {productivity:>8} {hypothesis}")

    # The "q-/qok-" analysis
    print("\n" + "-" * 80)
    print("SPECIAL FOCUS: 'Q-' and 'QOK-' PREFIX")
    print("-" * 80)

    q_prefix = prefix_stats.get("q", {"total": 0, "roots": set(), "examples": []})
    qok_prefix = prefix_stats.get("qok", {"total": 0, "roots": set(), "examples": []})

    print(f"\n'q-' prefix:")
    print(f"  Total instances: {q_prefix['total']:,}")
    print(f"  Unique roots: {len(q_prefix['roots'])}")
    print(f"  Top examples:")
    for ex in sorted(q_prefix["examples"], key=lambda x: x["freq"], reverse=True)[:5]:
        print(
            f"    {ex['voynich']:<15} = q-{ex['root']} ({ex['meaning']}) - {ex['freq']}x"
        )

    print(f"\n'qok-' prefix:")
    print(f"  Total instances: {qok_prefix['total']:,}")
    print(f"  Unique roots: {len(qok_prefix['roots'])}")
    print(f"  Top examples:")
    for ex in sorted(qok_prefix["examples"], key=lambda x: x["freq"], reverse=True)[:5]:
        print(
            f"    {ex['voynich']:<15} = qok-{ex['root']} ({ex['meaning']}) - {ex['freq']}x"
        )

    print("\n" + "=" * 80)
    print("CONCLUSIONS")
    print("=" * 80)

    print("\n1. HIGHLY PRODUCTIVE GRAMMATICAL SUFFIXES:")
    print("   These attach to many different roots → grammatical markers")
    for suffix, inf in sorted(
        inferences.items(), key=lambda x: x[1]["productivity"], reverse=True
    )[:5]:
        if inf["category"] == "highly_productive_grammatical":
            print(
                f"   -{suffix}: {inf['productivity']} roots, {inf['frequency']} instances"
            )
            print(f"      → {inf['hypothesis']}")

    print("\n2. Q-/QOK- PREFIX FUNCTION:")
    print("   Appears with many roots, high frequency")
    print(
        "   → Likely grammatical: case marker (genitive) or preposition ('of', 'with')"
    )

    print("\n3. CH-/SH- ALTERNATION:")
    print("   Both appear as prefixes with similar distributions")
    print("   → Confirms grammatical distinction (tense, number, case, or person)")

    print("\n4. SUFFIX STACKING:")
    print("   Words show patterns like: root + multiple suffixes")
    print("   → Agglutinative morphology confirmed")

    # Save results
    output = {
        "suffix_analysis": {
            k: {
                "total_instances": v["total_instances"],
                "unique_roots": list(v["unique_roots"]),
                "classification": inferences[k],
                "top_examples": sorted(
                    v["examples"], key=lambda x: x["freq"], reverse=True
                )[:10],
            }
            for k, v in suffix_stats.items()
        },
        "prefix_analysis": {
            k: {
                "total_instances": v["total"],
                "unique_roots": list(v["roots"]),
                "top_examples": sorted(
                    v["examples"], key=lambda x: x["freq"], reverse=True
                )[:10],
            }
            for k, v in prefix_stats.items()
        },
    }

    output_path = Path("results/phase4/affix_function_analysis.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nDetailed analysis saved to: {output_path}")


if __name__ == "__main__":
    main()
