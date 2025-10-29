#!/usr/bin/env python3
"""
Test letter scrambling hypothesis: middle letters scrambled while first/last preserved.

Based on typoglycemia phenomenon - words are readable if first and last letters
are in correct position, even if middle letters are scrambled.

This would be brilliant obfuscation:
- Easy for author to read (brain auto-corrects)
- Hard to detect algorithmically
- Preserves word shape/length
- Combines well with e↔o substitution

We'll test:
1. Pure scrambling (first/last preserved, middle scrambled)
2. Scrambling + e↔o
3. Scrambling + reversal
4. All three combined
"""

import json
from pathlib import Path
from itertools import permutations
from collections import Counter


def load_data():
    """Load specialized vocabulary and Section 4 text."""
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"

    # Load specialized vocabulary
    with open(
        results_dir / "specialized_medical_vocabulary.json", "r", encoding="utf-8"
    ) as f:
        vocab_data = json.load(f)

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
        "day": {"meaning": "day", "category": "time"},
        "night": {"meaning": "night", "category": "time"},
    }

    combined_vocab = {**specialized_vocab, **common_words}

    # Load Section 4 words
    with open(results_dir / "section_4_words.json", "r", encoding="utf-8") as f:
        section_4_data = json.load(f)

    return combined_vocab, section_4_data["words"]


def apply_eo_substitution(word, max_variants=32):
    """Apply e↔o substitution to a word."""
    from itertools import product

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


def generate_scrambled_variants(word, max_variants=50):
    """
    Generate variants with middle letters scrambled, first/last preserved.

    Example: "root" → "root", "roto", "rtoo" (all keep r_t pattern)
    """
    if len(word) <= 3:
        # Too short to scramble meaningfully
        return [word]

    first = word[0]
    last = word[-1]
    middle = word[1:-1]

    if len(middle) <= 1:
        return [word]

    # Generate all permutations of middle letters
    variants = set()
    variants.add(word)  # Include original

    for perm in permutations(middle):
        scrambled = first + "".join(perm) + last
        variants.add(scrambled)
        if len(variants) >= max_variants:
            break

    return list(variants)


def test_scrambling_hypothesis(section_words, vocab):
    """
    Test multiple scrambling strategies:
    1. Baseline (e↔o only)
    2. Pure scrambling (first/last preserved)
    3. Scrambling + e↔o
    4. Scrambling + reversal
    5. Scrambling + e↔o + reversal
    """

    results = {
        "baseline": {"matches": [], "details": []},
        "scrambled": {"matches": [], "details": []},
        "scrambled_eo": {"matches": [], "details": []},
        "scrambled_reversed": {"matches": [], "details": []},
        "all_combined": {"matches": [], "details": []},
    }

    for word_idx, word in enumerate(section_words):
        word_clean = word.lower().strip(".,;:!?")

        # Strategy 1: Baseline (e↔o only)
        for variant in apply_eo_substitution(word_clean):
            if variant in vocab:
                results["baseline"]["details"].append(
                    {
                        "original": word_clean,
                        "variant": variant,
                        "meaning": vocab[variant]["meaning"],
                        "category": vocab[variant]["category"],
                        "transform": "e↔o only",
                        "position": word_idx,
                    }
                )
                break

        # Strategy 2: Pure scrambling (preserve first/last)
        for scrambled in generate_scrambled_variants(word_clean):
            if scrambled in vocab:
                results["scrambled"]["details"].append(
                    {
                        "original": word_clean,
                        "variant": scrambled,
                        "meaning": vocab[scrambled]["meaning"],
                        "category": vocab[scrambled]["category"],
                        "transform": "scrambled",
                        "position": word_idx,
                    }
                )
                break

        # Strategy 3: Scrambling + e↔o
        for scrambled in generate_scrambled_variants(word_clean):
            for eo_variant in apply_eo_substitution(scrambled):
                if eo_variant in vocab:
                    results["scrambled_eo"]["details"].append(
                        {
                            "original": word_clean,
                            "scrambled": scrambled,
                            "variant": eo_variant,
                            "meaning": vocab[eo_variant]["meaning"],
                            "category": vocab[eo_variant]["category"],
                            "transform": "scrambled + e↔o",
                            "position": word_idx,
                        }
                    )
                    break
            else:
                continue
            break

        # Strategy 4: Scrambling + reversal
        reversed_word = word_clean[::-1]
        for scrambled in generate_scrambled_variants(reversed_word):
            if scrambled in vocab:
                results["scrambled_reversed"]["details"].append(
                    {
                        "original": word_clean,
                        "reversed": reversed_word,
                        "variant": scrambled,
                        "meaning": vocab[scrambled]["meaning"],
                        "category": vocab[scrambled]["category"],
                        "transform": "reversed + scrambled",
                        "position": word_idx,
                    }
                )
                break

        # Strategy 5: All combined (scramble + reverse + e↔o)
        for scrambled in generate_scrambled_variants(reversed_word):
            for eo_variant in apply_eo_substitution(scrambled):
                if eo_variant in vocab:
                    results["all_combined"]["details"].append(
                        {
                            "original": word_clean,
                            "reversed": reversed_word,
                            "scrambled": scrambled,
                            "variant": eo_variant,
                            "meaning": vocab[eo_variant]["meaning"],
                            "category": vocab[eo_variant]["category"],
                            "transform": "scrambled + reversed + e↔o",
                            "position": word_idx,
                        }
                    )
                    break
            else:
                continue
            break

    return results


def main():
    print("=" * 80)
    print("TESTING LETTER SCRAMBLING HYPOTHESIS")
    print("=" * 80)
    print()
    print("Hypothesis: Middle letters scrambled while first/last preserved.")
    print("Based on typoglycemia - 'Aoccdrnig to rscheearch...' is still readable.")
    print()
    print("This would be brilliant obfuscation:")
    print("  • Easy for author to read (brain auto-corrects)")
    print("  • Hard to detect algorithmically")
    print("  • Preserves word shape and length")
    print("  • Combines perfectly with e↔o substitution")
    print()

    vocab, section_4_words = load_data()
    total_words = len(section_4_words)

    print(f"Section 4 statistics:")
    print(f"  Total words: {total_words}")
    print(f"  Vocabulary size: {len(vocab)}")
    print()

    print("Testing strategies...")
    print()

    results = test_scrambling_hypothesis(section_4_words, vocab)

    # Report results
    print("=" * 80)
    print("STRATEGY 1: Baseline (e↔o only)")
    print("=" * 80)
    baseline_count = len(results["baseline"]["details"])
    baseline_rate = 100 * baseline_count / total_words
    print(f"Recognition: {baseline_count}/{total_words} = {baseline_rate:.2f}%")
    if results["baseline"]["details"][:5]:
        print("\nSample matches:")
        for d in results["baseline"]["details"][:5]:
            print(f"  {d['original']:15s} → {d['variant']:15s} = {d['meaning']}")
    print()

    print("=" * 80)
    print("STRATEGY 2: Pure scrambling (first/last preserved)")
    print("=" * 80)
    scrambled_count = len(results["scrambled"]["details"])
    scrambled_rate = 100 * scrambled_count / total_words
    print(f"Recognition: {scrambled_count}/{total_words} = {scrambled_rate:.2f}%")

    # Find NEW matches
    baseline_variants = set([d["variant"] for d in results["baseline"]["details"]])
    new_scrambled = [
        d
        for d in results["scrambled"]["details"]
        if d["variant"] not in baseline_variants
    ]

    if new_scrambled:
        print(f"\n✓ NEW MATCHES ({len(new_scrambled)}):")
        for d in new_scrambled[:10]:
            print(
                f"  {d['original']:15s} → {d['variant']:15s} (scrambled) = {d['meaning']:20s} ({d['category']})"
            )
    else:
        print("\n  (All matches already found in baseline)")
    print()

    print("=" * 80)
    print("STRATEGY 3: Scrambling + e↔o")
    print("=" * 80)
    scr_eo_count = len(results["scrambled_eo"]["details"])
    scr_eo_rate = 100 * scr_eo_count / total_words
    print(f"Recognition: {scr_eo_count}/{total_words} = {scr_eo_rate:.2f}%")

    all_previous = baseline_variants.copy()
    all_previous.update([d["variant"] for d in results["scrambled"]["details"]])
    new_scr_eo = [
        d
        for d in results["scrambled_eo"]["details"]
        if d["variant"] not in all_previous
    ]

    if new_scr_eo:
        print(f"\n✓ NEW MATCHES ({len(new_scr_eo)}):")
        for d in new_scr_eo[:10]:
            print(
                f"  {d['original']:15s} → {d.get('scrambled', '?'):15s} → {d['variant']:15s}"
            )
            print(f"    = {d['meaning']:20s} ({d['category']})")
    else:
        print("\n  (All matches already found)")
    print()

    print("=" * 80)
    print("STRATEGY 4: Scrambling + reversal")
    print("=" * 80)
    scr_rev_count = len(results["scrambled_reversed"]["details"])
    scr_rev_rate = 100 * scr_rev_count / total_words
    print(f"Recognition: {scr_rev_count}/{total_words} = {scr_rev_rate:.2f}%")

    all_previous.update([d["variant"] for d in results["scrambled_eo"]["details"]])
    new_scr_rev = [
        d
        for d in results["scrambled_reversed"]["details"]
        if d["variant"] not in all_previous
    ]

    if new_scr_rev:
        print(f"\n✓ NEW MATCHES ({len(new_scr_rev)}):")
        for d in new_scr_rev[:10]:
            print(
                f"  {d['original']:15s} → {d.get('reversed', '?'):15s} (rev) → {d['variant']:15s}"
            )
            print(f"    = {d['meaning']:20s} ({d['category']})")
    else:
        print("\n  (All matches already found)")
    print()

    print("=" * 80)
    print("STRATEGY 5: ALL COMBINED (scramble + reverse + e↔o)")
    print("=" * 80)
    all_count = len(results["all_combined"]["details"])
    all_rate = 100 * all_count / total_words
    print(f"Recognition: {all_count}/{total_words} = {all_rate:.2f}%")

    all_previous.update(
        [d["variant"] for d in results["scrambled_reversed"]["details"]]
    )
    new_all = [
        d
        for d in results["all_combined"]["details"]
        if d["variant"] not in all_previous
    ]

    if new_all:
        print(f"\n✓✓✓ NEW MATCHES ({len(new_all)}):")
        for d in new_all[:10]:
            print(f"  {d['original']:15s} → {d.get('reversed', '?'):15s} (rev)")
            print(
                f"    → {d.get('scrambled', '?'):15s} (scr) → {d['variant']:15s} (e↔o)"
            )
            print(f"    = {d['meaning']:20s} ({d['category']})")
    else:
        print("\n  (All matches already found)")
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
        f"Baseline (e↔o only):              {baseline_count:3d} ({baseline_rate:.2f}%)"
    )
    print(
        f"Pure scrambling:                  {scrambled_count:3d} ({scrambled_rate:.2f}%)"
    )
    print(f"Scrambling + e↔o:                 {scr_eo_count:3d} ({scr_eo_rate:.2f}%)")
    print(f"Scrambling + reversal:            {scr_rev_count:3d} ({scr_rev_rate:.2f}%)")
    print(f"All combined:                     {all_count:3d} ({all_rate:.2f}%)")
    print(f"TOTAL UNIQUE MATCHES:             {total_unique:3d} ({total_rate:.2f}%)")
    print()

    improvement = total_rate - baseline_rate
    print(f"Improvement from scrambling: +{improvement:.2f} percentage points")
    print()

    # Interpretation
    if improvement > 10:
        print("✓✓✓ VERY STRONG EVIDENCE FOR SCRAMBLING")
        print("Letter scrambling significantly increases recognition.")
        print("This is likely a major component of the cipher.")
    elif improvement > 5:
        print("✓✓ STRONG EVIDENCE FOR SCRAMBLING")
        print("Scrambling appears to be part of the obfuscation strategy.")
    elif improvement > 2:
        print("✓ MODERATE EVIDENCE FOR SCRAMBLING")
        print("Some benefit from scrambling hypothesis.")
    elif improvement > 0.5:
        print("~ WEAK EVIDENCE FOR SCRAMBLING")
        print("Slight improvement, possibly coincidental.")
    else:
        print("✗ NO EVIDENCE FOR SCRAMBLING")
        print("Scrambling does not improve recognition.")

    # Save results
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"
    output = {
        "section_id": 4,
        "total_words": total_words,
        "strategies": {
            "baseline": {
                "count": baseline_count,
                "rate": baseline_rate,
                "matches": results["baseline"]["details"],
            },
            "scrambled": {
                "count": scrambled_count,
                "rate": scrambled_rate,
                "matches": results["scrambled"]["details"],
            },
            "scrambled_eo": {
                "count": scr_eo_count,
                "rate": scr_eo_rate,
                "matches": results["scrambled_eo"]["details"],
            },
            "scrambled_reversed": {
                "count": scr_rev_count,
                "rate": scr_rev_rate,
                "matches": results["scrambled_reversed"]["details"],
            },
            "all_combined": {
                "count": all_count,
                "rate": all_rate,
                "matches": results["all_combined"]["details"],
            },
        },
        "summary": {
            "total_unique": total_unique,
            "total_rate": total_rate,
            "improvement": improvement,
        },
    }

    output_path = results_dir / "letter_scrambling_test_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to: {output_path}")
    print()


if __name__ == "__main__":
    main()
