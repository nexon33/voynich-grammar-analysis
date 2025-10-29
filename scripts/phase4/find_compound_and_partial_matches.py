#!/usr/bin/env python3
"""
Phase 4A: Find Compound Words and Partial Matches

Strategy: Many Voynich words might be:
1. Compound words: "root+flower" → "roteflor"
2. Prefixed/suffixed words: known root + grammatical affix
3. Partial matches: Voynich word contains known ME word as substring
"""

import json
from collections import Counter, defaultdict
from pathlib import Path


def load_data():
    """Load vocabulary and Voynich text."""
    with open(
        "results/phase4/expanded_medical_vocabulary.json", "r", encoding="utf-8"
    ) as f:
        vocab = json.load(f)

    with open(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt",
        "r",
        encoding="utf-8",
    ) as f:
        voynich_words = f.read().split()

    return vocab, Counter(voynich_words)


def apply_basic_transforms(word):
    """Apply basic transforms to get variations."""
    variants = {word}
    # e↔o
    variants.add(word.replace("e", "o"))
    variants.add(word.replace("o", "e"))
    # Reversal
    variants.add(word[::-1])
    variants.add(word[::-1].replace("e", "o"))
    variants.add(word[::-1].replace("o", "e"))
    return variants


def find_compound_words(vocab, voynich_freqs):
    """Find Voynich words that might be compounds of known ME words."""

    print("\n" + "=" * 80)
    print("SEARCHING FOR COMPOUND WORDS")
    print("=" * 80)

    # Generate all transform variants of vocab words
    me_variants = {}
    for me_word in vocab.keys():
        for variant in apply_basic_transforms(me_word):
            if len(variant) >= 3:  # Minimum length
                me_variants[variant] = me_word

    print(f"\nGenerated {len(me_variants)} ME word variants")

    # Check for compounds
    compounds = []

    # Get mid-to-high frequency Voynich words (10-200 instances)
    target_words = [
        (w, f) for w, f in voynich_freqs.items() if 10 <= f <= 200 and len(w) >= 6
    ]

    print(
        f"Checking {len(target_words)} mid-frequency Voynich words (10-200 instances, 6+ chars)..."
    )

    checked = 0
    for voynich_word, freq in target_words:
        checked += 1
        if checked % 100 == 0:
            print(f"  Checked {checked}/{len(target_words)}...")

        # Try to split into two known parts
        for i in range(3, len(voynich_word) - 2):  # Min 3 chars each part
            part1 = voynich_word[:i]
            part2 = voynich_word[i:]

            if part1 in me_variants and part2 in me_variants:
                compounds.append(
                    {
                        "voynich_word": voynich_word,
                        "frequency": freq,
                        "part1": part1,
                        "part1_me": me_variants[part1],
                        "part2": part2,
                        "part2_me": me_variants[part2],
                        "split_point": i,
                    }
                )

    print(f"\nFound {len(compounds)} potential compound words")

    if compounds:
        # Sort by frequency
        compounds.sort(key=lambda x: x["frequency"], reverse=True)

        print("\nTop 20 compound word candidates:")
        print(
            f"{'Voynich':<15} {'Freq':>5} {'Part1':<10} {'=':<10} {'Part2':<10} {'=':<10} {'Split'}"
        )
        print("-" * 80)
        for c in compounds[:20]:
            print(
                f"{c['voynich_word']:<15} {c['frequency']:5} "
                f"{c['part1']:<10} {c['part1_me']:<10} "
                f"{c['part2']:<10} {c['part2_me']:<10} "
                f"{c['split_point']}"
            )

    return compounds


def find_partial_matches(vocab, voynich_freqs):
    """Find Voynich words containing known ME words as substrings."""

    print("\n" + "=" * 80)
    print("SEARCHING FOR PARTIAL MATCHES (AFFIXED WORDS)")
    print("=" * 80)

    # Generate ME word variants
    me_variants = {}
    for me_word, me_data in vocab.items():
        for variant in apply_basic_transforms(me_word):
            if len(variant) >= 3:
                me_variants[variant] = (me_word, me_data)

    partial_matches = []

    # Get mid-frequency Voynich words
    target_words = [
        (w, f) for w, f in voynich_freqs.items() if 5 <= f <= 150 and len(w) >= 4
    ]

    print(f"Checking {len(target_words)} Voynich words for known ME roots...")

    checked = 0
    for voynich_word, freq in target_words:
        checked += 1
        if checked % 200 == 0:
            print(f"  Checked {checked}/{len(target_words)}...")

        # Check if any ME variant is substring
        for me_variant, (me_word, me_data) in me_variants.items():
            if (
                len(me_variant) >= 3
                and me_variant in voynich_word
                and me_variant != voynich_word
            ):
                # Found partial match
                position = voynich_word.index(me_variant)
                prefix = voynich_word[:position]
                suffix = voynich_word[position + len(me_variant) :]

                partial_matches.append(
                    {
                        "voynich_word": voynich_word,
                        "frequency": freq,
                        "me_word": me_word,
                        "me_variant": me_variant,
                        "meaning": me_data["meaning"],
                        "category": me_data["category"],
                        "prefix": prefix,
                        "suffix": suffix,
                        "position": "prefix"
                        if prefix
                        else ("suffix" if suffix else "both"),
                    }
                )

    print(f"\nFound {len(partial_matches)} partial matches")

    if partial_matches:
        # Remove duplicates (same Voynich word might match multiple ME words)
        unique_voynich = {}
        for pm in partial_matches:
            vw = pm["voynich_word"]
            if (
                vw not in unique_voynich
                or pm["frequency"] > unique_voynich[vw]["frequency"]
            ):
                unique_voynich[vw] = pm

        partial_matches = list(unique_voynich.values())
        partial_matches.sort(key=lambda x: x["frequency"], reverse=True)

        print(f"Unique Voynich words with partial matches: {len(partial_matches)}")

        print("\nTop 30 partial matches:")
        print(
            f"{'Voynich':<15} {'Freq':>5} {'Prefix':<8} {'Root':<10} {'Suffix':<8} {'ME Word':<12} {'Meaning'}"
        )
        print("-" * 95)
        for pm in partial_matches[:30]:
            print(
                f"{pm['voynich_word']:<15} {pm['frequency']:5} "
                f"{pm['prefix']:<8} {pm['me_variant']:<10} {pm['suffix']:<8} "
                f"{pm['me_word']:<12} {pm['meaning']}"
            )

    return partial_matches


def analyze_affixes(partial_matches):
    """Analyze common prefixes and suffixes."""

    if not partial_matches:
        return

    print("\n" + "=" * 80)
    print("AFFIX ANALYSIS")
    print("=" * 80)

    prefix_counts = Counter()
    suffix_counts = Counter()

    for pm in partial_matches:
        if pm["prefix"]:
            prefix_counts[pm["prefix"]] += pm["frequency"]
        if pm["suffix"]:
            suffix_counts[pm["suffix"]] += pm["frequency"]

    print("\nMost common PREFIXES:")
    for prefix, count in prefix_counts.most_common(20):
        print(f"  {prefix:<10} {count:5} instances")

    print("\nMost common SUFFIXES:")
    for suffix, count in suffix_counts.most_common(20):
        print(f"  {suffix:<10} {count:5} instances")


def calculate_coverage(compounds, partial_matches, voynich_freqs):
    """Calculate additional coverage from compounds and partials."""

    print("\n" + "=" * 80)
    print("COVERAGE ANALYSIS")
    print("=" * 80)

    compound_words = {c["voynich_word"] for c in compounds}
    partial_words = {pm["voynich_word"] for pm in partial_matches}

    compound_instances = sum(c["frequency"] for c in compounds)
    partial_instances = sum(pm["frequency"] for pm in partial_matches)

    # Remove overlap
    both = compound_words & partial_words
    overlap_instances = sum(voynich_freqs[w] for w in both)

    total_new_words = len(compound_words | partial_words)
    total_new_instances = compound_instances + partial_instances - overlap_instances

    total_voynich = sum(voynich_freqs.values())

    print(
        f"\nCompound words: {len(compound_words)} types, {compound_instances} instances"
    )
    print(f"Partial matches: {len(partial_words)} types, {partial_instances} instances")
    print(f"Overlap: {len(both)} types, {overlap_instances} instances")
    print(
        f"\nCombined unique: {total_new_words} types, {total_new_instances} instances"
    )
    print(f"Additional coverage: {100 * total_new_instances / total_voynich:.2f}%")

    # Save results
    output = {
        "compounds": compounds,
        "partial_matches": partial_matches,
        "summary": {
            "compound_types": len(compound_words),
            "compound_instances": compound_instances,
            "partial_types": len(partial_words),
            "partial_instances": partial_instances,
            "total_unique_types": total_new_words,
            "total_instances": total_new_instances,
            "coverage_percent": 100 * total_new_instances / total_voynich,
        },
    }

    output_path = Path("results/phase4/compound_and_partial_matches.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_path}")


def main():
    print("=" * 80)
    print("PHASE 4A: COMPOUND WORDS AND PARTIAL MATCHES")
    print("=" * 80)

    vocab, voynich_freqs = load_data()

    compounds = find_compound_words(vocab, voynich_freqs)
    partial_matches = find_partial_matches(vocab, voynich_freqs)

    analyze_affixes(partial_matches)
    calculate_coverage(compounds, partial_matches, voynich_freqs)

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
