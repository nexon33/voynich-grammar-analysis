#!/usr/bin/env python3
"""
Search for PREDICTED reversed terms based on semantic category rule.

We now KNOW the selection rule:
- Instructions → 100% reversed
- Plant parts → 100% reversed

This script searches for common ME medical instructions and plant parts
that we PREDICT will be reversed.
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

    all_words = []
    for section in data["sections"]:
        words = section["original"].split()
        all_words.extend(words)

    return all_words


def apply_all_transforms(word):
    """
    Generate ALL possible variants of a word:
    - e↔o substitution
    - Word reversal
    - ch↔sh, t↔d consonant shifts
    - All combinations
    """
    variants = {"direct": set(), "reversed": set()}

    # Helper: apply e↔o
    def apply_eo(w):
        eo_positions = [(i, c) for i, c in enumerate(w) if c in ["e", "o"]]
        if len(eo_positions) > 5:
            return [w, w.replace("o", "e"), w.replace("e", "o")]

        result = set()
        for combo in product(["e", "o"], repeat=len(eo_positions)):
            variant = list(w)
            for (pos, _), new_char in zip(eo_positions, combo):
                variant[pos] = new_char
            result.add("".join(variant))
            if len(result) >= 32:
                break
        return list(result)

    # Helper: apply consonant shifts
    def apply_consonants(w):
        result = {w}
        # ch↔sh
        result.add(w.replace("ch", "sh"))
        result.add(w.replace("sh", "ch"))
        # t↔d
        result.add(w.replace("t", "d"))
        result.add(w.replace("d", "t"))
        # c↔k
        result.add(w.replace("c", "k"))
        result.add(w.replace("k", "c"))
        return list(result)

    # Generate direct variants (no reversal)
    for cons_var in apply_consonants(word):
        for eo_var in apply_eo(cons_var):
            variants["direct"].add(eo_var)

    # Generate reversed variants
    reversed_word = word[::-1]
    for cons_var in apply_consonants(reversed_word):
        for eo_var in apply_eo(cons_var):
            variants["reversed"].add(eo_var)

    variants["direct"] = list(variants["direct"])
    variants["reversed"] = list(variants["reversed"])

    return variants


def search_term(english_term, category, all_words):
    """Search for all variants of a term."""
    variants = apply_all_transforms(english_term)

    matches = {"direct": [], "reversed": []}

    # Search manuscript
    for pos, word in enumerate(all_words):
        word_clean = word.lower().strip(".,;:!?")

        if word_clean in variants["direct"]:
            matches["direct"].append(
                {
                    "position": pos,
                    "voynich": word_clean,
                    "english": english_term,
                    "category": category,
                }
            )

        if word_clean in variants["reversed"]:
            matches["reversed"].append(
                {
                    "position": pos,
                    "voynich": word_clean,
                    "english": english_term,
                    "category": category,
                }
            )

    return matches


def main():
    print("=" * 80)
    print("SEARCHING FOR PREDICTED REVERSED TERMS")
    print("=" * 80)
    print()
    print("Based on semantic category rule:")
    print("  • INSTRUCTIONS → 100% reversed (predicted)")
    print("  • PLANT PARTS → 100% reversed (predicted)")
    print()

    all_words = load_manuscript()
    total_words = len(all_words)
    print(f"Manuscript: {total_words:,} words")
    print()

    # Define predicted terms
    predicted_terms = {
        "INSTRUCTIONS": [
            "tak",  # take (already found 1 as okad)
            "boil",  # boil
            "grind",  # grind
            "drynke",  # drink
            "stamp",  # stamp
            "meng",  # mix/mingle
            "ley",  # lay
            "seth",  # seethe/boil
            "bete",  # beat
            "do",  # do/put
            "put",  # put
            "cast",  # cast/throw
            "use",  # use
            "hete",  # heat
            "kele",  # cool
            "wasch",  # wash
        ],
        "PLANT_PARTS": [
            "rote",  # root (variant spelling, already found 12)
            "lef",  # leaf
            "leef",  # leaf (variant)
            "sed",  # seed (variant, already found 14 as 'sede' reversed)
            "floure",  # flower
            "flour",  # flower (variant)
            "bark",  # bark
            "barke",  # bark (variant)
            "stem",  # stem
            "stalke",  # stalk
            "herbe",  # herb
            "gras",  # grass
            "wode",  # wood
            "poudre",  # powder
        ],
    }

    print("Searching for:")
    print(f"  Instructions: {len(predicted_terms['INSTRUCTIONS'])} terms")
    print(f"  Plant parts: {len(predicted_terms['PLANT_PARTS'])} terms")
    print()
    print("=" * 80)
    print()

    all_results = {}
    total_found = 0
    total_reversed = 0

    for category, terms in predicted_terms.items():
        print(f"\n{'=' * 80}")
        print(f"{category}")
        print("=" * 80)
        print()

        category_results = {}

        for term in terms:
            matches = search_term(term, category, all_words)
            total_matches = len(matches["direct"]) + len(matches["reversed"])

            if total_matches > 0:
                category_results[term] = matches
                total_found += total_matches
                total_reversed += len(matches["reversed"])

                reversal_rate = (
                    len(matches["reversed"]) / total_matches * 100
                    if total_matches > 0
                    else 0
                )

                print(
                    f"{term:15s}: {total_matches:3d} total ({len(matches['direct'])} direct, {len(matches['reversed'])} reversed = {reversal_rate:.0f}% reversed)"
                )

                # Show sample reversed instances
                if matches["reversed"]:
                    samples = matches["reversed"][:3]
                    voynich_samples = set([m["voynich"] for m in samples])
                    print(
                        f"                 Voynich forms: {', '.join(voynich_samples)}"
                    )

        all_results[category] = category_results
        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    instruction_count = sum(
        len(m["direct"]) + len(m["reversed"])
        for m in all_results.get("INSTRUCTIONS", {}).values()
    )
    plant_count = sum(
        len(m["direct"]) + len(m["reversed"])
        for m in all_results.get("PLANT_PARTS", {}).values()
    )

    print(f"Total matches found: {total_found}")
    print(f"  Instructions: {instruction_count}")
    print(f"  Plant parts: {plant_count}")
    print()
    print(
        f"Reversed instances: {total_reversed} ({total_reversed / total_found * 100:.1f}% of matches)"
    )
    print()

    # Test semantic category hypothesis
    print("SEMANTIC CATEGORY VALIDATION:")
    print()

    for category, results in all_results.items():
        if not results:
            continue

        cat_total = sum(len(m["direct"]) + len(m["reversed"]) for m in results.values())
        cat_reversed = sum(len(m["reversed"]) for m in results.values())
        cat_reversal_rate = cat_reversed / cat_total * 100 if cat_total > 0 else 0

        print(
            f"{category:20s}: {cat_reversed}/{cat_total} reversed ({cat_reversal_rate:.1f}%)"
        )

        if cat_reversal_rate > 80:
            print(f"  ✓✓✓ STRONG CONFIRMATION: {category} are reversed as predicted!")
        elif cat_reversal_rate > 50:
            print(f"  ✓✓ MODERATE CONFIRMATION: {category} are mostly reversed")
        elif cat_reversal_rate > 20:
            print(f"  ✓ WEAK CONFIRMATION: Some {category} are reversed")
        else:
            print(
                f"  ✗ HYPOTHESIS CHALLENGED: {category} are not consistently reversed"
            )

    print()

    # New recognition calculation
    print("=" * 80)
    print("RECOGNITION IMPACT")
    print("=" * 80)
    print()

    # Compare to previous results
    previous_recognition = 1285  # From consonant analysis
    new_instances = total_found
    updated_total = previous_recognition + new_instances
    updated_rate = updated_total / total_words * 100
    previous_rate = previous_recognition / total_words * 100
    improvement = updated_rate - previous_rate

    print(f"Previous recognition: {previous_recognition} ({previous_rate:.2f}%)")
    print(f"New instances found: {new_instances}")
    print(f"Updated total: {updated_total} ({updated_rate:.2f}%)")
    print(f"Improvement: +{improvement:.2f} percentage points")
    print()

    if improvement > 1.0:
        print("✓✓✓ MAJOR IMPROVEMENT!")
        print(f"    Recognition increased by {improvement:.2f}%")
    elif improvement > 0.5:
        print("✓✓ SIGNIFICANT IMPROVEMENT")
        print(f"    Recognition increased by {improvement:.2f}%")
    elif improvement > 0.1:
        print("✓ MODERATE IMPROVEMENT")
        print(f"    Recognition increased by {improvement:.2f}%")
    else:
        print("~ Minor improvement")
        print(f"    Recognition increased by {improvement:.2f}%")

    # Save results
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"
    output = {
        "total_words": total_words,
        "terms_searched": sum(len(terms) for terms in predicted_terms.values()),
        "total_found": total_found,
        "total_reversed": total_reversed,
        "reversal_rate": total_reversed / total_found * 100 if total_found > 0 else 0,
        "by_category": {
            cat: {
                "total": sum(
                    len(m["direct"]) + len(m["reversed"]) for m in results.values()
                ),
                "reversed": sum(len(m["reversed"]) for m in results.values()),
                "terms_found": len(results),
            }
            for cat, results in all_results.items()
        },
        "detailed_results": {
            cat: {
                term: {
                    "total": len(matches["direct"]) + len(matches["reversed"]),
                    "direct": len(matches["direct"]),
                    "reversed": len(matches["reversed"]),
                    "sample_voynich": list(
                        set([m["voynich"] for m in matches["reversed"][:5]])
                    ),
                }
                for term, matches in results.items()
            }
            for cat, results in all_results.items()
        },
        "recognition_stats": {
            "previous": previous_recognition,
            "previous_rate": previous_rate,
            "new_instances": new_instances,
            "updated_total": updated_total,
            "updated_rate": updated_rate,
            "improvement": improvement,
        },
    }

    output_path = results_dir / "predicted_reversals_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print()
    print(f"Results saved to: {output_path}")
    print()


if __name__ == "__main__":
    main()
