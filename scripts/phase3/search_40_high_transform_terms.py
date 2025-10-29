#!/usr/bin/env python3
"""
Search for 40+ HIGH-TRANSFORM medical terms to reach 10% TRANSFORMED recognition.

Strategy:
- Focus on terms that MUST be transformed (instructions, plant parts)
- Avoid preserved words (conditions, function words)
- Target high-frequency medical vocabulary
- Apply all known transforms (reversal, e↔o, ch↔sh, t↔d, c↔k)
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
    """Generate ALL possible transformed variants (excluding preserved)."""
    variants = set()

    # Helper: apply e↔o
    def apply_eo(w):
        eo_positions = [(i, c) for i, c in enumerate(w) if c in ["e", "o"]]
        if len(eo_positions) > 6:
            return [w, w.replace("o", "e"), w.replace("e", "o")]

        result = set()
        for combo in product(["e", "o"], repeat=len(eo_positions)):
            variant = list(w)
            for (pos, _), new_char in zip(eo_positions, combo):
                variant[pos] = new_char
            result.add("".join(variant))
            if len(result) >= 50:
                break
        return list(result)

    # Helper: apply all consonant shifts
    def apply_consonants(w):
        result = {w}
        # ch↔sh
        if "ch" in w:
            result.add(w.replace("ch", "sh"))
        if "sh" in w:
            result.add(w.replace("sh", "ch"))
        # t↔d
        if "t" in w:
            result.add(w.replace("t", "d"))
        if "d" in w:
            result.add(w.replace("d", "t"))
        # c↔k
        if "c" in w:
            result.add(w.replace("c", "k"))
        if "k" in w:
            result.add(w.replace("k", "c"))
        # ph↔f
        if "ph" in w:
            result.add(w.replace("ph", "f"))
        if "f" in w and "f" not in ["ff"]:
            result.add(w.replace("f", "ph"))
        return list(result)

    # REVERSED + transforms (this is where most decipherment happens)
    reversed_word = word[::-1]
    for cons_var in apply_consonants(reversed_word):
        for eo_var in apply_eo(cons_var):
            variants.add(eo_var)

    # Also check e↔o + consonants WITHOUT reversal (less common but exists)
    for cons_var in apply_consonants(word):
        for eo_var in apply_eo(cons_var):
            # Only add if it's actually transformed
            if eo_var != word:
                variants.add(eo_var)

    return list(variants)


def search_term(english_term, category, all_words):
    """Search for all transformed variants of a term."""
    variants = apply_all_transforms(english_term)

    matches = []

    for pos, word in enumerate(all_words):
        word_clean = word.lower().strip(".,;:!?")

        if word_clean in variants:
            matches.append(
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
    print("SEARCHING FOR 40+ HIGH-TRANSFORM MEDICAL TERMS")
    print("=" * 80)
    print()
    print("Target: 10% TRANSFORMED recognition (excluding preserved plain text)")
    print()
    print("Strategy:")
    print("  • Focus on INSTRUCTIONS (100% transformed)")
    print("  • Focus on PLANT PARTS (100% transformed)")
    print("  • Focus on BODY PARTS (70%+ transformed)")
    print("  • Include medical processes and treatments")
    print("  • Apply ALL transforms: reversal + e↔o + ch↔sh + t↔d + c↔k")
    print()

    all_words = load_manuscript()
    total_words = len(all_words)
    print(f"Manuscript: {total_words:,} words")
    print()

    # Comprehensive high-frequency medical vocabulary
    # Organized by category for systematic coverage
    target_terms = {
        "INSTRUCTIONS": [
            # Recipe verbs (very common in medieval herbals)
            "grind",
            "grynde",
            "boil",
            "boile",
            "boyle",
            "stamp",
            "stampe",
            "drynke",
            "drink",
            "meng",
            "menge",
            "mingel",  # mix/mingle
            "seth",
            "sethe",  # seethe/boil
            "bete",
            "beat",
            "wasch",
            "wash",
            "wasshe",
            "stamp",
            "stompe",
            "hete",
            "heat",
            "kele",
            "cool",
            "cole",
            "temper",
            "tempre",
            "strayn",
            "strain",
            "streyne",
            "presse",
            "press",
            "drie",
            "dry",
            "drye",
            "wete",
            "wet",
            "pound",
            "poune",
            "breke",
            "break",
            "brek",
            "kutte",
            "cut",
            "kut",
            "slice",
            "slise",
        ],
        "PLANT_PARTS": [
            # Plant anatomy (essential for herbals)
            "flour",
            "floure",
            "flower",
            "herbe",
            "herb",
            "erbe",
            "bark",
            "barke",
            "stalke",
            "stalk",
            "stem",
            "branch",
            "braunche",
            "poudre",
            "pouder",
            "powder",  # ground plant matter
            "jus",
            "juice",
            "juce",
            "sap",
            "sappe",
            "gum",
            "gomme",
            "rinde",
            "rind",  # bark/peel
        ],
        "BODY_PARTS": [
            # High-frequency anatomy terms
            "hond",
            "hand",
            "hed",
            "head",
            "heed",
            "blod",
            "blood",
            "blode",
            "herte",
            "heart",
            "hert",
            "mouth",
            "muthe",
            "tunge",
            "tongue",
            "tonge",
            "throte",
            "throat",
            "thrот",
            "brest",
            "breast",
            "breste",
            "bely",
            "belly",
            "belee",
            "wombe",
            "womb",
            "wome",
            "stomak",
            "stomach",
            "stomac",
            "liver",
            "lyver",
            "lung",
            "longe",
            "lungen",
            "bone",
            "bon",
            "boon",
            "flesh",
            "flessh",
            "flesch",
            "skin",
            "skyn",
            "vein",
            "veyne",
            "vayn",
        ],
        "TREATMENTS": [
            # Medical actions/treatments (likely transformed)
            "hele",
            "heal",
            "hel",
            "cure",
            "kure",
            "helpe",
            "help",
            "ease",
            "ese",
            "swage",
            "aswage",  # reduce swelling
            "purge",
            "p purge",
            "dense",
            "clense",
            "clens",  # cleanse
            "comforte",
            "comfort",
            "strengthe",
            "strength",
            "feble",
            "feeble",
        ],
        "MEASUREMENTS": [
            # Quantities in recipes
            "ounce",
            "unce",
            "pound",
            "pund",
            "dragme",
            "dram",  # unit of weight
            "handful",
            "handful",
            "quantite",
            "quantity",
            "porcioun",
            "portion",
            "dele",
            "deal",
            "part",  # portion
        ],
    }

    total_targets = sum(len(terms) for terms in target_terms.values())
    print(f"Searching for {total_targets} terms across 5 categories")
    print()
    print("=" * 80)
    print()

    all_results = {}
    category_stats = defaultdict(lambda: {"terms_found": 0, "instances": 0})

    for category, terms in target_terms.items():
        print(f"\n{category}")
        print("-" * 80)

        found_count = 0
        instance_count = 0

        for term in terms:
            matches = search_term(term, category, all_words)

            if matches:
                if term not in all_results:
                    all_results[term] = {
                        "category": category,
                        "matches": matches,
                        "count": len(matches),
                    }
                    found_count += 1
                    instance_count += len(matches)

                    # Show findings
                    voynich_samples = list(set([m["voynich"] for m in matches[:5]]))
                    print(
                        f"  {term:20s}: {len(matches):3d} instances - {', '.join(voynich_samples)}"
                    )

        category_stats[category]["terms_found"] = found_count
        category_stats[category]["instances"] = instance_count

        if found_count > 0:
            print(
                f"\n  Category total: {found_count} terms, {instance_count} instances"
            )
        else:
            print(f"\n  No matches found in this category")

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    total_terms_found = len(all_results)
    total_instances_found = sum(data["count"] for data in all_results.values())

    print(f"Total unique terms found: {total_terms_found}")
    print(f"Total instances found: {total_instances_found}")
    print()

    print("By category:")
    for cat, stats in category_stats.items():
        if stats["terms_found"] > 0:
            print(
                f"  {cat:20s}: {stats['terms_found']:2d} terms, {stats['instances']:4d} instances"
            )
    print()

    # Calculate recognition impact
    print("=" * 80)
    print("RECOGNITION IMPACT")
    print("=" * 80)
    print()

    # Previous transformed recognition (from breakdown analysis)
    previous_transformed = 861  # 2.12%
    new_instances = total_instances_found
    updated_transformed = previous_transformed + new_instances

    previous_rate = previous_transformed / total_words * 100
    new_rate = new_instances / total_words * 100
    updated_rate = updated_transformed / total_words * 100

    print(
        f"Previous TRANSFORMED recognition: {previous_transformed:4d} ({previous_rate:.2f}%)"
    )
    print(f"New instances found:              {new_instances:4d} (+{new_rate:.2f}%)")
    print(
        f"Updated TRANSFORMED total:        {updated_transformed:4d} ({updated_rate:.2f}%)"
    )
    print()

    improvement = updated_rate - previous_rate
    print(f"Improvement: +{improvement:.2f} percentage points")
    print()

    # Progress to 10%
    target_rate = 10.0
    progress_pct = (updated_rate / target_rate) * 100
    remaining = target_rate - updated_rate

    print(f"Target: 10.00% transformed recognition")
    print(f"Current: {updated_rate:.2f}%")
    print(f"Progress: {progress_pct:.1f}% of target")
    print(f"Remaining: {remaining:.2f} percentage points")
    print()

    if updated_rate >= target_rate:
        print("🎉 TARGET ACHIEVED! 🎉")
        print("We have reached 10% TRANSFORMED recognition!")
    elif updated_rate >= target_rate * 0.8:
        print("✓✓✓ ALMOST THERE!")
        print(f"Only {remaining:.2f}% away from 10% target!")
    elif updated_rate >= target_rate * 0.5:
        print("✓✓ MAJOR PROGRESS")
        print(f"Halfway to target! {remaining:.2f}% remaining")
    else:
        print("✓ GOOD PROGRESS")
        print(f"Continue searching for more high-frequency terms")

    # Save results
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"
    output = {
        "total_words": total_words,
        "total_terms_found": total_terms_found,
        "total_instances": total_instances_found,
        "by_category": {
            cat: {"terms": stats["terms_found"], "instances": stats["instances"]}
            for cat, stats in category_stats.items()
        },
        "detailed_results": {
            term: {
                "category": data["category"],
                "count": data["count"],
                "sample_voynich": list(
                    set([m["voynich"] for m in data["matches"][:10]])
                ),
            }
            for term, data in all_results.items()
        },
        "recognition_stats": {
            "previous_transformed": previous_transformed,
            "previous_rate": previous_rate,
            "new_instances": new_instances,
            "new_rate": new_rate,
            "updated_transformed": updated_transformed,
            "updated_rate": updated_rate,
            "improvement": improvement,
            "target_rate": target_rate,
            "progress_percent": progress_pct,
            "remaining": remaining,
        },
    }

    output_path = results_dir / "high_transform_search_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print()
    print(f"Results saved to: {output_path}")
    print()


if __name__ == "__main__":
    main()
