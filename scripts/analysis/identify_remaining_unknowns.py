#!/usr/bin/env python3
"""
Identify Remaining High-Frequency Unknowns

Goal: Find what's left to decode to reach 85%

Current recognition: 82.2%
Target: 85%
Needed: +2.8%

Already decoded:
- [?e] = continuous aspect (1,365 instances, +3.1%)
- [?r] = liquid/contents (289 instances, +0.8%)
- [?s] = plant/herb (694 instances, +1.9%)
- T- = instrumental/locative prefix (973 instances, +2.6%)
- [?lch] = VERB (582 instances, +1.6%)
- [?sh], [?ch] = VERBs
- [?al] = NOUN

Find: What unknowns remain with >100 instances?
"""

import json
import re
from collections import Counter


def load_translations():
    """Load translations"""
    with open(
        "COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)
        return data["translations"]


def extract_all_unknowns(translations):
    """
    Extract all [?...] unknowns from corpus
    """
    unknown_counter = Counter()
    word_examples = {}

    for trans in translations:
        sentence = trans["final_translation"]
        words = sentence.split()

        for word in words:
            # Find all [?...] patterns
            unknowns = re.findall(r"\[\?[^\]]+\]", word)

            for unknown in unknowns:
                unknown_counter[unknown] += 1

                if unknown not in word_examples:
                    word_examples[unknown] = []

                if len(word_examples[unknown]) < 5:
                    word_examples[unknown].append(word)

    return unknown_counter, word_examples


def classify_unknowns(unknown_counter, word_examples):
    """
    Classify unknowns by what we know
    """
    decoded = {
        "[?e]": "ASPECT (continuous)",
        "[?r]": "NOUN (liquid)",
        "[?s]": "NOUN (plant/herb)",
        "[?lch]": "VERB",
        "[?ch]": "VERB (prepare)",
        "[?sh]": "VERB (apply)",
        "[?al]": "NOUN (substance)",
    }

    categories = {
        "DECODED": [],
        "HIGH_FREQ_UNKNOWN": [],  # >100 instances
        "MED_FREQ_UNKNOWN": [],  # 50-100 instances
        "LOW_FREQ_UNKNOWN": [],  # <50 instances
    }

    for unknown, count in unknown_counter.items():
        if unknown in decoded:
            categories["DECODED"].append((unknown, count, decoded[unknown]))
        elif count > 100:
            categories["HIGH_FREQ_UNKNOWN"].append((unknown, count))
        elif count >= 50:
            categories["MED_FREQ_UNKNOWN"].append((unknown, count))
        else:
            categories["LOW_FREQ_UNKNOWN"].append((unknown, count))

    return categories


def analyze_unknown_contexts(unknown, translations, word_examples):
    """
    Analyze contexts of a specific unknown
    """
    before = Counter()
    after = Counter()
    with_verb_suffix = 0
    standalone = 0

    for trans in translations:
        sentence = trans["final_translation"]
        words = sentence.split()

        for i, word in enumerate(words):
            if unknown in word:
                # Context
                before.update(words[max(0, i - 3) : i])
                after.update(words[i + 1 : min(len(words), i + 3 + 1)])

                # VERB suffix?
                if "-VERB" in word:
                    with_verb_suffix += 1

                # Standalone?
                if word == unknown:
                    standalone += 1

    total = sum(1 for t in translations if unknown in t["final_translation"])
    verb_rate = with_verb_suffix / total * 100 if total > 0 else 0
    standalone_rate = standalone / total * 100 if total > 0 else 0

    # Predict classification
    if verb_rate > 30:
        prediction = "LIKELY VERBAL"
    elif standalone_rate > 30 or verb_rate < 10:
        prediction = "LIKELY NOMINAL"
    else:
        prediction = "UNCERTAIN"

    return {
        "total": total,
        "verb_rate": verb_rate,
        "standalone_rate": standalone_rate,
        "prediction": prediction,
        "top_before": dict(before.most_common(10)),
        "top_after": dict(after.most_common(10)),
        "examples": word_examples.get(unknown, []),
    }


def calculate_potential_gain(categories):
    """
    Calculate potential recognition gain from remaining unknowns
    """
    high_freq_total = sum(count for _, count in categories["HIGH_FREQ_UNKNOWN"])
    med_freq_total = sum(count for _, count in categories["MED_FREQ_UNKNOWN"])

    # Estimate total corpus size (~37,000 words)
    total_corpus = 37000

    high_gain = high_freq_total / total_corpus * 100
    med_gain = med_freq_total / total_corpus * 100

    return high_gain, med_gain


def main():
    """Main analysis"""
    print("=" * 70)
    print("IDENTIFY REMAINING HIGH-FREQUENCY UNKNOWNS")
    print("=" * 70)
    print("\nCurrent recognition: 82.2%")
    print("Target: 85%")
    print("Needed: +2.8%\n")

    print("Loading translations...")
    translations = load_translations()
    print(f"Loaded {len(translations)} translations\n")

    # EXTRACT ALL UNKNOWNS
    print("Extracting all unknowns...")
    unknown_counter, word_examples = extract_all_unknowns(translations)

    print(f"Total unique unknowns: {len(unknown_counter)}")
    print(f"Total unknown instances: {sum(unknown_counter.values())}\n")

    # CLASSIFY
    categories = classify_unknowns(unknown_counter, word_examples)

    # DECODED (for reference)
    print("=" * 70)
    print("ALREADY DECODED")
    print("=" * 70)

    decoded_total = sum(count for _, count, _ in categories["DECODED"])
    print(f"\nTotal decoded instances: {decoded_total}\n")

    for unknown, count, classification in sorted(
        categories["DECODED"], key=lambda x: x[1], reverse=True
    ):
        pct = count / sum(unknown_counter.values()) * 100
        print(f"  {unknown:15s}: {count:5d} ({pct:5.2f}%) - {classification}")

    # HIGH FREQUENCY UNKNOWN
    print("\n" + "=" * 70)
    print("HIGH-FREQUENCY UNKNOWNS (>100 instances)")
    print("=" * 70)

    if categories["HIGH_FREQ_UNKNOWN"]:
        print(f"\nFound {len(categories['HIGH_FREQ_UNKNOWN'])} high-frequency unknowns")
        print(
            f"Total instances: {sum(c for _, c in categories['HIGH_FREQ_UNKNOWN'])}\n"
        )

        # Analyze each
        for unknown, count in sorted(
            categories["HIGH_FREQ_UNKNOWN"], key=lambda x: x[1], reverse=True
        ):
            pct = count / sum(unknown_counter.values()) * 100
            print(f"\n{unknown} ({count} instances, {pct:.2f}%)")

            # Analyze
            analysis = analyze_unknown_contexts(unknown, translations, word_examples)

            print(f"  Prediction: {analysis['prediction']}")
            print(f"  VERB suffix rate: {analysis['verb_rate']:.1f}%")
            print(f"  Standalone rate: {analysis['standalone_rate']:.1f}%")

            print(f"  Top 5 BEFORE:")
            for word, cnt in list(analysis["top_before"].items())[:5]:
                print(f"    {word}: {cnt}×")

            print(f"  Top 5 AFTER:")
            for word, cnt in list(analysis["top_after"].items())[:5]:
                print(f"    {word}: {cnt}×")

            print(f"  Examples:")
            for ex in analysis["examples"][:3]:
                print(f"    {ex}")
    else:
        print("\nNo high-frequency unknowns remaining!")
        print("All major elements have been classified! ✓")

    # MEDIUM FREQUENCY
    print("\n" + "=" * 70)
    print("MEDIUM-FREQUENCY UNKNOWNS (50-100 instances)")
    print("=" * 70)

    if categories["MED_FREQ_UNKNOWN"]:
        print(
            f"\nFound {len(categories['MED_FREQ_UNKNOWN'])} medium-frequency unknowns"
        )
        print(f"Total instances: {sum(c for _, c in categories['MED_FREQ_UNKNOWN'])}\n")

        for unknown, count in sorted(
            categories["MED_FREQ_UNKNOWN"], key=lambda x: x[1], reverse=True
        )[:10]:
            pct = count / sum(unknown_counter.values()) * 100
            print(f"  {unknown:20s}: {count:4d} ({pct:5.2f}%)")

    # POTENTIAL GAIN
    print("\n" + "=" * 70)
    print("POTENTIAL RECOGNITION GAIN")
    print("=" * 70)

    high_gain, med_gain = calculate_potential_gain(categories)

    print(f"\nHigh-frequency unknowns: +{high_gain:.2f}%")
    print(f"Medium-frequency unknowns: +{med_gain:.2f}%")
    print(f"Total potential: +{high_gain + med_gain:.2f}%")

    if high_gain > 0:
        print(
            f"\nWith high-frequency decoded: 82.2% + {high_gain:.2f}% = {82.2 + high_gain:.2f}%"
        )

    if high_gain + med_gain >= 2.8:
        print(f"\n✓ TARGET ACHIEVABLE: Decoding these unknowns could reach 85%+")
    else:
        print(f"\n⚠ TARGET DIFFICULT: Only {high_gain + med_gain:.2f}% available")
        print(f"    May need to look at other elements (prefixes, compounds, etc.)")

    # RECOMMENDATIONS
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)

    if categories["HIGH_FREQ_UNKNOWN"]:
        print("\n1. DECODE HIGH-FREQUENCY UNKNOWNS:")
        for unknown, count in sorted(
            categories["HIGH_FREQ_UNKNOWN"], key=lambda x: x[1], reverse=True
        )[:5]:
            analysis = analyze_unknown_contexts(unknown, translations, word_examples)
            print(f"   {unknown} ({count}×) - {analysis['prediction']}")
        print(f"   Potential gain: +{high_gain:.2f}%")
    else:
        print("\n1. NO HIGH-FREQUENCY UNKNOWNS REMAIN")
        print("   Major morphemes already decoded! ✓")

    if categories["MED_FREQ_UNKNOWN"]:
        print(f"\n2. CONSIDER MEDIUM-FREQUENCY UNKNOWNS:")
        print(
            f"   {len(categories['MED_FREQ_UNKNOWN'])} unknowns (50-100 instances each)"
        )
        print(f"   Potential gain: +{med_gain:.2f}%")

    print("\n3. OTHER STRATEGIES:")
    print("   - Investigate compound morphemes")
    print("   - Refine allomorph identification")
    print("   - Cross-validate with illustrations")

    # Save results
    results = {
        "decoded": [(u, c, cl) for u, c, cl in categories["DECODED"]],
        "high_freq_unknown": [(u, c) for u, c in categories["HIGH_FREQ_UNKNOWN"]],
        "med_freq_unknown": [(u, c) for u, c in categories["MED_FREQ_UNKNOWN"]],
        "potential_gain": {
            "high_freq": high_gain,
            "med_freq": med_gain,
            "total": high_gain + med_gain,
        },
        "detailed_analysis": {
            unknown: analyze_unknown_contexts(unknown, translations, word_examples)
            for unknown, _ in categories["HIGH_FREQ_UNKNOWN"]
        },
    }

    print("\nSaving results to REMAINING_UNKNOWNS_ANALYSIS.json...")
    with open("REMAINING_UNKNOWNS_ANALYSIS.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"\nCurrent recognition: 82.2%")
    if high_gain > 0:
        print(f"Realistic target with high-freq: {82.2 + high_gain:.2f}%")
    print(f"Maximum potential: {82.2 + high_gain + med_gain:.2f}%")

    print("\nDONE!")


if __name__ == "__main__":
    main()
