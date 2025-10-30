#!/usr/bin/env python3
"""
Identify remaining unknowns to push from 91.6% to 95%.

Currently decoded (91.6%):
- [?e]: continuous aspect
- [?r]: liquid/contents
- [?s]: plant/herb
- [?a]: generic noun ("thing")
- [?y]: discourse suffix
- [?k]: sequential prefix
- [?al]: nominal root
- [?ch]: prepare/make (verb)
- [?sh]: apply/heat (verb)
- [?lch]: unknown action (verb)
- [?eo]: boil/cook (verb)
- [?che]: oak-substance
- [?eey]: seed/grain
- T-: instrumental prefix

Need: ~3-4% more → 95%

Target: High-frequency unknowns (>50 instances)
"""

import json
import re
from collections import Counter


def load_translations():
    with open(
        "COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)
        return data["translations"]


def extract_unknowns(translations):
    """Extract all [?...] patterns that aren't already decoded"""

    decoded = {
        "?e",
        "?r",
        "?s",
        "?a",
        "?y",
        "?k",
        "?al",
        "?ch",
        "?sh",
        "?lch",
        "?eo",
        "?che",
        "?eey",
    }

    unknown_counter = Counter()

    for trans in translations:
        text = trans["final_translation"]

        # Find all [?...] patterns
        unknowns = re.findall(r"\[(\?[^\]]+)\]", text)

        for unk in unknowns:
            if unk not in decoded:
                unknown_counter[unk] += 1

    return unknown_counter


def classify_unknown(pattern, translations):
    """Quick classification for unknown pattern"""

    verb_suffix_count = 0
    total_count = 0
    standalone_count = 0

    contexts_before = Counter()
    contexts_after = Counter()

    for trans in translations:
        text = trans["final_translation"]
        words = text.split()

        for i, word in enumerate(words):
            if f"[{pattern}]" in word:
                total_count += 1

                # VERB suffix?
                if "-VERB" in word:
                    verb_suffix_count += 1

                # Standalone?
                if word == f"[{pattern}]":
                    standalone_count += 1

                # Context
                prev = words[i - 1] if i > 0 else "<START>"
                next_word = words[i + 1] if i < len(words) - 1 else "<END>"
                contexts_before[prev] += 1
                contexts_after[next_word] += 1

    verb_rate = verb_suffix_count / total_count if total_count > 0 else 0
    standalone_rate = standalone_count / total_count if total_count > 0 else 0

    # Classification
    if verb_rate > 0.3:
        classification = "VERBAL"
    elif standalone_rate > 0.2:
        classification = "NOMINAL (root)"
    elif standalone_rate < 0.05:
        classification = "AFFIX or BOUND"
    else:
        classification = "NOMINAL or MIXED"

    return {
        "total": total_count,
        "verb_rate": verb_rate,
        "standalone_rate": standalone_rate,
        "classification": classification,
        "top_before": contexts_before.most_common(5),
        "top_after": contexts_after.most_common(5),
    }


def main():
    print("=" * 70)
    print("IDENTIFY REMAINING UNKNOWNS: PUSH TO 95%")
    print("=" * 70)
    print()
    print("Current recognition: 91.6%")
    print("Target: 95%")
    print("Need: ~3-4% more (~1,200-1,500 instances)")
    print()
    print("=" * 70)

    translations = load_translations()

    # Extract unknowns
    print("\nExtracting unknowns...")
    unknowns = extract_unknowns(translations)

    total_unknown = sum(unknowns.values())
    corpus_size = 37000  # Approximate
    unknown_pct = total_unknown / corpus_size * 100

    print(f"Total unknown instances: {total_unknown} (~{unknown_pct:.1f}% of corpus)")
    print()

    # High-frequency unknowns
    print("=" * 70)
    print("HIGH-FREQUENCY UNKNOWNS (>50 instances)")
    print("=" * 70)
    print()

    high_freq = [(pat, count) for pat, count in unknowns.most_common(50) if count > 50]

    cumulative = 0
    priority_targets = []

    for i, (pattern, count) in enumerate(high_freq[:20], 1):
        cumulative += count
        pct = count / corpus_size * 100
        cumulative_pct = cumulative / corpus_size * 100

        # Quick classify
        info = classify_unknown(pattern, translations)

        print(f"{i:2d}. [{pattern}]: {count:4d} instances ({pct:.2f}%)")
        print(f"    Classification: {info['classification']}")
        print(
            f"    VERB: {info['verb_rate']:.1%}, Standalone: {info['standalone_rate']:.1%}"
        )

        if i <= 10:
            print(
                f"    Context before: {info['top_before'][0][0] if info['top_before'] else 'N/A'}"
            )
            print(
                f"    Context after: {info['top_after'][0][0] if info['top_after'] else 'N/A'}"
            )

        print(
            f"    Cumulative if decoded: 91.6% + {cumulative_pct:.2f}% = {91.6 + cumulative_pct:.2f}%"
        )
        print()

        # Priority for 95% push
        if cumulative_pct < 3.5:  # Need ~3.4% to hit 95%
            priority_targets.append(
                {
                    "pattern": pattern,
                    "count": count,
                    "pct": pct,
                    "classification": info["classification"],
                    "verb_rate": info["verb_rate"],
                    "standalone_rate": info["standalone_rate"],
                }
            )

    print("=" * 70)
    print("PRIORITY TARGETS FOR 95%")
    print("=" * 70)
    print()
    print("To reach 95%, decode these in order:")
    print()

    for i, target in enumerate(priority_targets, 1):
        print(
            f"{i}. [{target['pattern']}]: {target['count']} instances ({target['pct']:.2f}%)"
        )
        print(f"   → {target['classification']}")
        print()

    cumulative_priority = sum(t["count"] for t in priority_targets)
    cumulative_pct_priority = cumulative_priority / corpus_size * 100

    print(f"Total priority targets: {len(priority_targets)}")
    print(f"Total instances: {cumulative_priority} (~{cumulative_pct_priority:.2f}%)")
    print(
        f"Expected recognition: 91.6% + {cumulative_pct_priority:.2f}% = {91.6 + cumulative_pct_priority:.2f}%"
    )
    print()

    if 91.6 + cumulative_pct_priority >= 95:
        print("✓ THIS WILL GET US TO 95%!")
    else:
        print(f"⚠ Need {95 - (91.6 + cumulative_pct_priority):.2f}% more")

    print()
    print("=" * 70)
    print("RECOMMENDED DECODING ORDER")
    print("=" * 70)
    print()

    # Group by classification
    verbal_targets = [t for t in priority_targets if "VERBAL" in t["classification"]]
    nominal_targets = [t for t in priority_targets if "NOMINAL" in t["classification"]]
    affix_targets = [
        t
        for t in priority_targets
        if "AFFIX" in t["classification"] or "BOUND" in t["classification"]
    ]

    if verbal_targets:
        print("VERBAL ROOTS (decode first - complete verb inventory):")
        for t in verbal_targets:
            print(
                f"  [{t['pattern']}]: {t['count']} instances, {t['verb_rate']:.1%} VERB"
            )
        print()

    if nominal_targets:
        print("NOMINAL ROOTS (decode second - substance identification):")
        for t in nominal_targets:
            print(
                f"  [{t['pattern']}]: {t['count']} instances, {t['standalone_rate']:.1%} standalone"
            )
        print()

    if affix_targets:
        print("AFFIXES/BOUND MORPHEMES (decode last - grammatical):")
        for t in affix_targets:
            print(f"  [{t['pattern']}]: {t['count']} instances")
        print()

    # Save results
    results = {
        "current_recognition": 91.6,
        "target_recognition": 95.0,
        "unknown_instances": total_unknown,
        "unknown_percentage": unknown_pct,
        "priority_targets": priority_targets,
        "expected_recognition": round(91.6 + cumulative_pct_priority, 2),
        "verbal_targets": [t["pattern"] for t in verbal_targets],
        "nominal_targets": [t["pattern"] for t in nominal_targets],
        "affix_targets": [t["pattern"] for t in affix_targets],
    }

    with open("FINAL_UNKNOWNS_95PCT.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("Results saved to FINAL_UNKNOWNS_95PCT.json")
    print()


if __name__ == "__main__":
    main()
