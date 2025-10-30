#!/usr/bin/env python3
"""
Batch Decode [?a], [?y], [?k] - The Final Push to 85%!

From remaining unknowns analysis:
- [?a]: 1,057 instances (3.78%) - LIKELY NOMINAL (0.2% VERB)
- [?y]: 622 instances (2.22%) - LIKELY NOMINAL (2.8% VERB, 27.9% standalone)
- [?k]: 525 instances (1.88%) - LIKELY VERBAL (32.2% VERB)

Apply Phase 18-19 classification methodology to all three
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


def analyze_root(root_pattern, translations):
    """
    Comprehensive root analysis
    """
    standalone = []
    affixed = []
    contexts = []

    root_regex = re.compile(rf"\[{root_pattern}\]")

    for idx, trans in enumerate(translations):
        sentence = trans["final_translation"]
        words = sentence.split()

        for i, word in enumerate(words):
            if root_regex.search(word):
                # Context
                before = words[max(0, i - 3) : i]
                after = words[i + 1 : min(len(words), i + 3 + 1)]

                context = {
                    "line": trans.get("line", f"line{idx + 1}"),
                    "word": word,
                    "before": before,
                    "after": after,
                    "full_sentence": sentence,
                }
                contexts.append(context)

                # Standalone vs affixed
                if word == f"[{root_pattern}]":
                    standalone.append(context)
                else:
                    affixed.append(context)

    # Calculate rates
    total = len(contexts)
    standalone_count = len(standalone)
    affixed_count = len(affixed)

    standalone_rate = standalone_count / total * 100 if total > 0 else 0

    # VERB suffix rate
    verb_count = sum(1 for ctx in contexts if "-VERB" in ctx["word"])
    verb_rate = verb_count / total * 100 if total > 0 else 0

    # Co-occurrence
    before_counter = Counter()
    after_counter = Counter()

    for ctx in contexts:
        before_counter.update(ctx["before"])
        after_counter.update(ctx["after"])

    # Classification
    if verb_rate > 30:
        classification = "VERBAL"
        confidence = "MODERATE" if verb_rate > 40 else "LOW"
    elif verb_rate < 10 and standalone_rate > 20:
        classification = "NOMINAL"
        confidence = "MODERATE" if standalone_rate > 30 else "LOW"
    elif verb_rate < 10:
        classification = "LIKELY NOMINAL"
        confidence = "LOW"
    else:
        classification = "UNCERTAIN"
        confidence = "LOW"

    return {
        "total": total,
        "standalone_count": standalone_count,
        "standalone_rate": standalone_rate,
        "affixed_count": affixed_count,
        "verb_count": verb_count,
        "verb_rate": verb_rate,
        "classification": classification,
        "confidence": confidence,
        "top_before": dict(before_counter.most_common(15)),
        "top_after": dict(after_counter.most_common(15)),
        "sample_contexts": [
            {
                "line": ctx["line"],
                "word": ctx["word"],
                "before": ctx["before"],
                "after": ctx["after"],
            }
            for ctx in contexts[:10]
        ],
    }


def main():
    """Main analysis"""
    print("=" * 70)
    print("BATCH DECODE: [?a], [?y], [?k] - FINAL PUSH TO 85%!")
    print("=" * 70)
    print("\nCurrent recognition: 82.2%")
    print("Target: 85%")
    print("\nAnalyzing three high-frequency unknowns:")
    print("  [?a]: 1,057 instances (3.78%)")
    print("  [?y]: 622 instances (2.22%)")
    print("  [?k]: 525 instances (1.88%)")
    print("  Total: 2,204 instances (~6% of corpus)\n")

    print("Loading translations...")
    translations = load_translations()
    print(f"Loaded {len(translations)} translations\n")

    roots_to_analyze = {
        "?a": {"expected": "NOMINAL", "prelim_verb": 0.2},
        "?y": {"expected": "NOMINAL", "prelim_verb": 2.8},
        "?k": {"expected": "VERBAL", "prelim_verb": 32.2},
    }

    results = {}

    for root, info in roots_to_analyze.items():
        print("=" * 70)
        print(f"ANALYZING [{root}]")
        print("=" * 70)
        print(
            f"Preliminary prediction: {info['expected']} ({info['prelim_verb']:.1f}% VERB)\n"
        )

        analysis = analyze_root(root, translations)

        print(f"Total instances: {analysis['total']}")
        print(
            f"Standalone: {analysis['standalone_count']} ({analysis['standalone_rate']:.1f}%)"
        )
        print(f"Affixed: {analysis['affixed_count']}")
        print(f"VERB suffix rate: {analysis['verb_rate']:.1f}%")

        print(
            f"\nClassification: {analysis['classification']} ({analysis['confidence']} confidence)"
        )

        # Compare with known patterns
        print(f"\nComparison with known patterns:")
        if analysis["classification"] == "VERBAL":
            print(f"  [?sh]/[?ch]: 45.2% VERB, 8.1% standalone")
            print(
                f"  [{root}]: {analysis['verb_rate']:.1f}% VERB, {analysis['standalone_rate']:.1f}% standalone"
            )
            if analysis["verb_rate"] > 30:
                print(f"  ✓ Pattern matches VERBAL")
        elif "NOMINAL" in analysis["classification"]:
            print(f"  [?al]: 3.2% VERB, 32.8% standalone")
            print(
                f"  [{root}]: {analysis['verb_rate']:.1f}% VERB, {analysis['standalone_rate']:.1f}% standalone"
            )
            if analysis["verb_rate"] < 10:
                print(f"  ✓ Pattern matches NOMINAL")

        print(f"\nTop 10 words BEFORE [{root}]:")
        for word, count in list(analysis["top_before"].items())[:10]:
            print(f"  {word}: {count}×")

        print(f"\nTop 10 words AFTER [{root}]:")
        for word, count in list(analysis["top_after"].items())[:10]:
            print(f"  {word}: {count}×")

        print(f"\nSample contexts (first 5):")
        for i, ctx in enumerate(analysis["sample_contexts"][:5], 1):
            print(f"\n  {i}. {ctx['line']}")
            print(
                f"     ...{' '.join(ctx['before'])} **{ctx['word']}** {' '.join(ctx['after'])}..."
            )

        print("\n")

        results[root] = analysis

    # SUMMARY
    print("=" * 70)
    print("SUMMARY: FINAL CLASSIFICATIONS")
    print("=" * 70)

    total_instances = sum(r["total"] for r in results.values())
    print(f"\nTotal instances analyzed: {total_instances}")

    confirmed_count = 0

    for root, analysis in results.items():
        print(f"\n[{root}]:")
        print(f"  Instances: {analysis['total']}")
        print(f"  Classification: {analysis['classification']}")
        print(f"  Confidence: {analysis['confidence']}")
        print(f"  VERB rate: {analysis['verb_rate']:.1f}%")
        print(f"  Standalone rate: {analysis['standalone_rate']:.1f}%")

        if analysis["confidence"] in ["MODERATE", "HIGH"]:
            confirmed_count += analysis["total"]

    # Recognition gain
    corpus_size = 37000  # Approximate
    realistic_gain = confirmed_count / corpus_size * 100

    print(f"\n" + "=" * 70)
    print("RECOGNITION GAIN")
    print("=" * 70)

    print(f"\nConfirmed instances (MODERATE+ confidence): {confirmed_count}")
    print(f"Estimated recognition gain: +{realistic_gain:.2f}%")
    print(f"\nCurrent: 82.2%")
    print(
        f"With new decoding: 82.2% + {realistic_gain:.2f}% = {82.2 + realistic_gain:.2f}%"
    )

    if 82.2 + realistic_gain >= 85:
        print(f"\n🎯 TARGET ACHIEVED! Recognition ≥ 85%!")
    elif 82.2 + realistic_gain >= 84:
        print(f"\n✓ VERY CLOSE! Within 1% of target!")
    else:
        print(f"\n⚠ More work needed to reach 85%")

    # RECOMMENDATIONS
    print(f"\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)

    for root, analysis in results.items():
        if analysis["confidence"] == "MODERATE":
            print(f"\n[{root}]: {analysis['classification']} classification is solid")
            print(f"  ✓ Can be added to validated morphemes")
        elif analysis["confidence"] == "LOW":
            print(
                f"\n[{root}]: {analysis['classification']} classification is tentative"
            )
            print(f"  → Needs additional validation")

    print(f"\nTo reach 85%:")
    if 82.2 + realistic_gain < 85:
        remaining = 85 - (82.2 + realistic_gain)
        print(f"  Still need: +{remaining:.2f}%")
        print(f"  Options:")
        print(f"    - Decode [?eo] (170×, 63.9% VERB - strong verbal candidate)")
        print(f"    - Decode [?che] (560×, likely nominal)")
        print(f"    - Decode [?eey] (511×, likely nominal)")
    else:
        print(f"  ✓ Target achieved with current decodings!")

    # Save results
    print(f"\nSaving results to A_Y_K_BATCH_ANALYSIS.json...")
    with open("A_Y_K_BATCH_ANALYSIS.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\nDONE!")

    return results


if __name__ == "__main__":
    main()
