#!/usr/bin/env python3
"""
Detailed Pattern Analysis - What's ACTUALLY in the sentences?

Look at sentences containing key pharmaceutical elements and analyze their structure.
"""

import json


def load_data():
    with open(
        "COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)
    return data["translations"]


def analyze_al_sentences(translations):
    """Analyze sentences containing [?al]"""

    al_sentences = []
    for trans in translations:
        sentence = trans["final_translation"]
        if "[?al]" in sentence or "al-" in sentence or "-al" in sentence:
            al_sentences.append(
                {
                    "folio": trans.get("folio", "unknown"),
                    "sentence": sentence,
                    "original": trans.get("original", ""),
                }
            )

    return al_sentences


def categorize_al_patterns(al_sentences):
    """Categorize how [?al] appears in sentences"""

    categories = {
        "with_ch_verb": [],
        "with_sh_verb": [],
        "with_both_verbs": [],
        "with_vessel": [],
        "with_water": [],
        "with_botanical": [],
        "with_oak_gen": [],
        "with_oat_gen": [],
        "standalone": [],
        "other": [],
    }

    for item in al_sentences:
        sentence = item["sentence"]

        has_ch = "[?ch]" in sentence and "VERB" in sentence
        has_sh = "[?sh]" in sentence and "VERB" in sentence

        if has_ch and has_sh:
            categories["with_both_verbs"].append(item)
        elif has_ch:
            categories["with_ch_verb"].append(item)
        elif has_sh:
            categories["with_sh_verb"].append(item)

        if "vessel" in sentence.lower():
            categories["with_vessel"].append(item)
        if "water" in sentence.lower():
            categories["with_water"].append(item)
        if "botanical-term" in sentence:
            categories["with_botanical"].append(item)
        if "oak-GEN" in sentence:
            categories["with_oak_gen"].append(item)
        if "oat-GEN" in sentence:
            categories["with_oat_gen"].append(item)

        # Check if standalone [?al]
        if (
            sentence.strip() == "[?al]"
            or sentence.count("[?al]") > 0
            and sentence.count(" ") < 5
        ):
            categories["standalone"].append(item)

    return categories


def main():
    print("=" * 80)
    print("DETAILED PATTERN ANALYSIS: What's in sentences with [?al]?")
    print("=" * 80)
    print()

    translations = load_data()
    print(f"Total sentences: {len(translations)}")
    print()

    # Find all sentences with [?al]
    al_sentences = analyze_al_sentences(translations)
    print(f"Sentences containing [?al]: {len(al_sentences)}")
    print(f"Percentage of corpus: {len(al_sentences) / len(translations) * 100:.1f}%")
    print()

    # Categorize patterns
    categories = categorize_al_patterns(al_sentences)

    print("=" * 80)
    print("PATTERN CATEGORIES")
    print("=" * 80)
    print()

    for cat_name, items in categories.items():
        if items:
            print(
                f"{cat_name}: {len(items)} sentences ({len(items) / len(al_sentences) * 100:.1f}% of [?al] sentences)"
            )
            print()
            print("  Examples:")
            for i, item in enumerate(items[:3], 1):
                print(f"    {i}. {item['folio']}: {item['sentence'][:120]}...")
            print()

    # Look for recipe-like sequences
    print("=" * 80)
    print("RECIPE-LIKE SEQUENCES (Manual Inspection)")
    print("=" * 80)
    print()

    print("Sentences with [?al] + [?ch]-VERB + [?sh]-VERB:")
    print(f"Found: {len(categories['with_both_verbs'])}")
    print()
    for i, item in enumerate(categories["with_both_verbs"][:10], 1):
        print(f"{i}. {item['folio']}")
        print(f"   {item['sentence']}")
        print()

    # Oak-GEN-al analysis
    print("=" * 80)
    print("OAK-GEN with [?al] - Most Common Patterns")
    print("=" * 80)
    print()

    oak_al_sentences = [s for s in al_sentences if "oak-GEN" in s["sentence"]]
    print(f"Total oak-GEN + [?al] sentences: {len(oak_al_sentences)}")
    print()
    print("Examples:")
    for i, item in enumerate(oak_al_sentences[:15], 1):
        print(f"{i}. {item['sentence'][:150]}")
        print()

    # Save detailed results
    output = {
        "total_al_sentences": len(al_sentences),
        "categories": {k: len(v) for k, v in categories.items()},
        "sample_sentences": {
            "with_both_verbs": [
                s["sentence"] for s in categories["with_both_verbs"][:10]
            ],
            "with_vessel": [s["sentence"] for s in categories["with_vessel"][:10]],
            "with_water": [s["sentence"] for s in categories["with_water"][:10]],
            "oak_gen": [s["sentence"] for s in oak_al_sentences[:20]],
        },
    }

    with open("DETAILED_AL_PATTERN_ANALYSIS.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("Results saved to: DETAILED_AL_PATTERN_ANALYSIS.json")


if __name__ == "__main__":
    main()
