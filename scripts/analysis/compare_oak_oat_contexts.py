#!/usr/bin/env python3
"""
Context Comparison: oak-GEN and oat-GEN across Manuscript Sections

Goal: Determine if oak-GEN and oat-GEN have different meanings in different sections
by analyzing what words appear near them.

If botanical: Should appear with botanical-term, vessel, water, preparation verbs
If astrological: Should appear with different co-occurrence patterns
"""

import json
import re
from collections import defaultdict, Counter


def load_translations():
    with open(
        "COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)
    return data["translations"]


def build_folio_mapping():
    """Build mapping from line numbers to folios using ZL3b-n.txt"""
    line_to_folio = {}

    with open(
        "data/voynich/eva_transcription/ZL3b-n.txt",
        "r",
        encoding="utf-8",
        errors="ignore",
    ) as f:
        line_num = 0
        for file_line in f:
            if file_line.startswith("#") or not file_line.strip():
                continue

            folio_match = re.search(r"<(f\d+[rv])\.?\d*[^>]*>", file_line)
            if folio_match:
                folio = folio_match.group(1)
                line_num += 1
                line_to_folio[line_num] = folio

    return line_to_folio


def classify_folio(folio):
    """Classify folio into manuscript sections"""
    if not folio:
        return "unknown"

    match = re.search(r"f(\d+)", folio)
    if not match:
        return "unknown"

    num = int(match.group(1))

    if 1 <= num <= 66:
        return "herbal"
    elif 67 <= num <= 73:
        return "astronomical"
    elif 75 <= num <= 84:
        return "biological"
    elif 87 <= num <= 102:
        return "pharmaceutical"
    elif 103 <= num <= 116:
        return "stars"
    else:
        return "other"


def find_oak_oat_contexts(translations, line_to_folio, window=5):
    """Find all sentences with oak-GEN or oat-GEN and their contexts"""

    contexts = {
        "herbal": {"oak": [], "oat": []},
        "stars": {"oak": [], "oat": []},
        "biological": {"oak": [], "oat": []},
        "pharmaceutical": {"oak": [], "oat": []},
        "astronomical": {"oak": [], "oat": []},
    }

    for idx, trans in enumerate(translations):
        sentence = trans["final_translation"]

        # Get section
        folio_id = trans.get("folio", "unknown")
        line_match = re.search(r"line(\d+)", folio_id)
        line_num = int(line_match.group(1)) if line_match else idx + 1
        folio = line_to_folio.get(line_num)
        section = classify_folio(folio)

        if section not in contexts:
            continue

        words = sentence.split()

        # Find oak-GEN or oat-GEN
        for i, word in enumerate(words):
            if "oak-GEN" in word:
                # Get context window
                before = words[max(0, i - window) : i]
                after = words[i + 1 : min(len(words), i + window + 1)]

                contexts[section]["oak"].append(
                    {
                        "folio": folio,
                        "word": word,
                        "before": before,
                        "after": after,
                        "full_sentence": sentence,
                    }
                )

            elif "oat-GEN" in word:
                before = words[max(0, i - window) : i]
                after = words[i + 1 : min(len(words), i + window + 1)]

                contexts[section]["oat"].append(
                    {
                        "folio": folio,
                        "word": word,
                        "before": before,
                        "after": after,
                        "full_sentence": sentence,
                    }
                )

    return contexts


def analyze_context_patterns(contexts):
    """Analyze what words appear near oak-GEN/oat-GEN in each section"""

    analysis = {}

    for section in ["herbal", "stars", "biological", "pharmaceutical"]:
        analysis[section] = {
            "oak": {"before": Counter(), "after": Counter(), "count": 0},
            "oat": {"before": Counter(), "after": Counter(), "count": 0},
        }

        # Analyze oak-GEN
        for ctx in contexts[section]["oak"]:
            analysis[section]["oak"]["count"] += 1
            for word in ctx["before"]:
                analysis[section]["oak"]["before"][word] += 1
            for word in ctx["after"]:
                analysis[section]["oak"]["after"][word] += 1

        # Analyze oat-GEN
        for ctx in contexts[section]["oat"]:
            analysis[section]["oat"]["count"] += 1
            for word in ctx["before"]:
                analysis[section]["oat"]["before"][word] += 1
            for word in ctx["after"]:
                analysis[section]["oat"]["after"][word] += 1

    return analysis


def main():
    print("=" * 80)
    print("CONTEXT COMPARISON: oak-GEN and oat-GEN across Sections")
    print("=" * 80)
    print()
    print("Goal: Determine if oak-GEN and oat-GEN have different meanings")
    print("      in different manuscript sections")
    print()

    # Load data
    print("Loading data...")
    translations = load_translations()
    line_to_folio = build_folio_mapping()
    print(f"Loaded {len(translations)} sentences")
    print()

    # Find contexts
    print("Finding oak-GEN and oat-GEN contexts...")
    contexts = find_oak_oat_contexts(translations, line_to_folio)

    # Count by section
    print("=" * 80)
    print("FREQUENCY BY SECTION")
    print("=" * 80)
    print()

    for section in ["herbal", "stars", "biological", "pharmaceutical"]:
        oak_count = len(contexts[section]["oak"])
        oat_count = len(contexts[section]["oat"])
        print(f"{section.upper()}:")
        print(f"  oak-GEN: {oak_count} instances")
        print(f"  oat-GEN: {oat_count} instances")
        print()

    # Analyze patterns
    print("=" * 80)
    print("CONTEXT ANALYSIS")
    print("=" * 80)
    print()

    analysis = analyze_context_patterns(contexts)

    # Compare Herbal vs Stars for oak-GEN
    print("OAK-GEN CONTEXT COMPARISON:")
    print()
    print("In HERBAL section (f1r-f66v):")
    print(f"  Total instances: {analysis['herbal']['oak']['count']}")
    print("  Most common words BEFORE oak-GEN:")
    for word, count in analysis["herbal"]["oak"]["before"].most_common(10):
        print(f"    {word}: {count}×")
    print("  Most common words AFTER oak-GEN:")
    for word, count in analysis["herbal"]["oak"]["after"].most_common(10):
        print(f"    {word}: {count}×")
    print()

    print("In STARS section (f103r-f116r):")
    print(f"  Total instances: {analysis['stars']['oak']['count']}")
    print("  Most common words BEFORE oak-GEN:")
    for word, count in analysis["stars"]["oak"]["before"].most_common(10):
        print(f"    {word}: {count}×")
    print("  Most common words AFTER oak-GEN:")
    for word, count in analysis["stars"]["oak"]["after"].most_common(10):
        print(f"    {word}: {count}×")
    print()

    print("In BIOLOGICAL section (f75r-f84v):")
    print(f"  Total instances: {analysis['biological']['oak']['count']}")
    print("  Most common words BEFORE oak-GEN:")
    for word, count in analysis["biological"]["oak"]["before"].most_common(10):
        print(f"    {word}: {count}×")
    print("  Most common words AFTER oak-GEN:")
    for word, count in analysis["biological"]["oak"]["after"].most_common(10):
        print(f"    {word}: {count}×")
    print()

    # Compare Herbal vs Stars for oat-GEN
    print("=" * 80)
    print("OAT-GEN CONTEXT COMPARISON:")
    print()
    print("In HERBAL section:")
    print(f"  Total instances: {analysis['herbal']['oat']['count']}")
    print("  Most common words BEFORE oat-GEN:")
    for word, count in analysis["herbal"]["oat"]["before"].most_common(10):
        print(f"    {word}: {count}×")
    print("  Most common words AFTER oat-GEN:")
    for word, count in analysis["herbal"]["oat"]["after"].most_common(10):
        print(f"    {word}: {count}×")
    print()

    print("In STARS section:")
    print(f"  Total instances: {analysis['stars']['oat']['count']}")
    print("  Most common words BEFORE oat-GEN:")
    for word, count in analysis["stars"]["oat"]["before"].most_common(10):
        print(f"    {word}: {count}×")
    print("  Most common words AFTER oat-GEN:")
    for word, count in analysis["stars"]["oat"]["after"].most_common(10):
        print(f"    {word}: {count}×")
    print()

    print("In BIOLOGICAL section:")
    print(f"  Total instances: {analysis['biological']['oat']['count']}")
    print("  Most common words BEFORE oat-GEN:")
    for word, count in analysis["biological"]["oat"]["before"].most_common(10):
        print(f"    {word}: {count}×")
    print("  Most common words AFTER oat-GEN:")
    for word, count in analysis["biological"]["oat"]["after"].most_common(10):
        print(f"    {word}: {count}×")
    print()

    # Sample sentences
    print("=" * 80)
    print("SAMPLE SENTENCES")
    print("=" * 80)
    print()

    print("OAK-GEN in HERBAL section (5 examples):")
    for i, ctx in enumerate(contexts["herbal"]["oak"][:5], 1):
        print(f"\n{i}. {ctx['folio']}: {ctx['full_sentence']}")

    print("\n" + "=" * 80)
    print("OAK-GEN in STARS section (5 examples):")
    for i, ctx in enumerate(contexts["stars"]["oak"][:5], 1):
        print(f"\n{i}. {ctx['folio']}: {ctx['full_sentence']}")

    print("\n" + "=" * 80)
    print("OAK-GEN in BIOLOGICAL section (5 examples):")
    for i, ctx in enumerate(contexts["biological"]["oak"][:5], 1):
        print(f"\n{i}. {ctx['folio']}: {ctx['full_sentence']}")

    print("\n" + "=" * 80)
    print("OAT-GEN in HERBAL section (5 examples):")
    for i, ctx in enumerate(contexts["herbal"]["oat"][:5], 1):
        print(f"\n{i}. {ctx['folio']}: {ctx['full_sentence']}")

    print("\n" + "=" * 80)
    print("OAT-GEN in STARS section (5 examples):")
    for i, ctx in enumerate(contexts["stars"]["oat"][:5], 1):
        print(f"\n{i}. {ctx['folio']}: {ctx['full_sentence']}")

    # Save detailed results
    output = {
        "frequency_by_section": {
            section: {
                "oak_count": len(contexts[section]["oak"]),
                "oat_count": len(contexts[section]["oat"]),
            }
            for section in ["herbal", "stars", "biological", "pharmaceutical"]
        },
        "context_patterns": {
            section: {
                "oak": {
                    "before_top10": dict(
                        analysis[section]["oak"]["before"].most_common(10)
                    ),
                    "after_top10": dict(
                        analysis[section]["oak"]["after"].most_common(10)
                    ),
                },
                "oat": {
                    "before_top10": dict(
                        analysis[section]["oat"]["before"].most_common(10)
                    ),
                    "after_top10": dict(
                        analysis[section]["oat"]["after"].most_common(10)
                    ),
                },
            }
            for section in ["herbal", "stars", "biological", "pharmaceutical"]
        },
    }

    with open("OAK_OAT_CONTEXT_ANALYSIS.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("Analysis complete. Results saved to: OAK_OAT_CONTEXT_ANALYSIS.json")
    print("=" * 80)


if __name__ == "__main__":
    main()
