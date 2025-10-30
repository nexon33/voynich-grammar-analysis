#!/usr/bin/env python3
"""
Investigate high-frequency unknown roots: [?lch], [?s], [?r]
Following Phase 18-19 methodology for grammatical classification
"""

import json
import re
from collections import Counter, defaultdict


def load_translations():
    """Load the complete manuscript translation"""
    with open(
        "COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)
        return data["translations"]


def extract_root_instances(translations, root_pattern):
    """
    Extract all instances of a root pattern
    Returns: standalone instances, affixed instances, and contexts
    """
    standalone = []
    affixed = []
    contexts = []

    root_regex = re.compile(root_pattern)

    for idx, trans in enumerate(translations):
        sentence = trans["final_translation"]
        words = sentence.split()

        for i, word in enumerate(words):
            if root_regex.search(word):
                # Get context
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

                # Check if standalone or affixed
                # Standalone: just [?root] with no other morphemes (except maybe case)
                # Affixed: contains suffixes like -VERB, prefixes, etc.
                if word == f"[{root_pattern}]":
                    standalone.append(context)
                elif (
                    "-VERB" in word
                    or "-NOM" in word
                    or re.search(r"-(ing|ed|er|or|tion|ness)", word)
                ):
                    affixed.append(context)
                else:
                    # Check for case markers (might be standalone with case)
                    if any(
                        case in word
                        for case in ["-GEN", "-DAT", "-ACC", "-LOC", "-ABL", "-INST"]
                    ):
                        standalone.append(context)
                    else:
                        affixed.append(context)

    return standalone, affixed, contexts


def analyze_verb_suffix_rate(contexts):
    """Calculate percentage with VERB suffix"""
    verb_count = sum(1 for ctx in contexts if "-VERB" in ctx["word"])
    return (verb_count / len(contexts) * 100) if contexts else 0


def analyze_cooccurrence(contexts):
    """Analyze what words co-occur with this root"""
    before_words = []
    after_words = []

    for ctx in contexts:
        before_words.extend(ctx["before"])
        after_words.extend(ctx["after"])

    before_counter = Counter(before_words)
    after_counter = Counter(after_words)

    return before_counter, after_counter


def compare_with_known_patterns(root_stats, known_verbal, known_nominal):
    """
    Compare root statistics with known verbal ([?sh], [?ch])
    and nominal ([?al]) patterns
    """
    # Verbal roots: high VERB suffix rate (>30%), low standalone rate (<20%)
    # Nominal roots: low VERB suffix rate (<10%), high standalone rate (>30%)

    classification = "UNKNOWN"
    confidence = "LOW"

    verb_rate = root_stats["verb_suffix_rate"]
    standalone_rate = root_stats["standalone_rate"]

    if verb_rate > 30 and standalone_rate < 20:
        classification = "VERBAL"
        confidence = "MODERATE" if verb_rate > 40 else "LOW"
    elif verb_rate < 10 and standalone_rate > 30:
        classification = "NOMINAL"
        confidence = "MODERATE" if standalone_rate > 40 else "LOW"
    elif verb_rate > 20:
        classification = "LIKELY VERBAL"
        confidence = "LOW"
    elif standalone_rate > 20:
        classification = "LIKELY NOMINAL"
        confidence = "LOW"

    return classification, confidence


def main():
    """Main analysis"""
    print("Loading translations...")
    translations = load_translations()
    print(f"Loaded {len(translations)} translations")

    # Define roots to investigate
    roots = {
        "?lch": r"\?\w*lch\w*",
        "?s": r"\?s\b",  # Word boundary to avoid matching other roots
        "?r": r"\?r\b",
    }

    # Known patterns for comparison
    known_verbal = {
        "name": "[?sh] and [?ch]",
        "verb_suffix_rate": 45.2,  # Average from Phase 18
        "standalone_rate": 8.1,
    }

    known_nominal = {
        "name": "[?al]",
        "verb_suffix_rate": 3.2,  # From Phase 19
        "standalone_rate": 32.8,
    }

    results = {}

    for root_name, root_pattern in roots.items():
        print(f"\n{'=' * 60}")
        print(f"Analyzing [{root_name}]")
        print("=" * 60)

        standalone, affixed, contexts = extract_root_instances(
            translations, root_pattern
        )

        total = len(contexts)
        standalone_count = len(standalone)
        affixed_count = len(affixed)

        print(f"\nTotal instances: {total}")
        print(f"Standalone: {standalone_count} ({standalone_count / total * 100:.1f}%)")
        print(f"Affixed: {affixed_count} ({affixed_count / total * 100:.1f}%)")

        verb_rate = analyze_verb_suffix_rate(contexts)
        print(f"VERB suffix rate: {verb_rate:.1f}%")

        before_counter, after_counter = analyze_cooccurrence(contexts)
        print(f"\nTop 10 words BEFORE [{root_name}]:")
        for word, count in before_counter.most_common(10):
            print(f"  {word}: {count}")

        print(f"\nTop 10 words AFTER [{root_name}]:")
        for word, count in after_counter.most_common(10):
            print(f"  {word}: {count}")

        # Classification
        root_stats = {
            "verb_suffix_rate": verb_rate,
            "standalone_rate": standalone_count / total * 100 if total > 0 else 0,
        }

        classification, confidence = compare_with_known_patterns(
            root_stats, known_verbal, known_nominal
        )

        print(f"\nCLASSIFICATION: {classification} (confidence: {confidence})")
        print(f"Reasoning:")
        print(
            f"  - VERB suffix rate: {verb_rate:.1f}% (verbal threshold: >30%, nominal: <10%)"
        )
        print(
            f"  - Standalone rate: {standalone_count / total * 100:.1f}% (verbal threshold: <20%, nominal: >30%)"
        )

        # Sample contexts
        print(f"\nSample contexts (first 5):")
        for i, ctx in enumerate(contexts[:5]):
            print(f"\n  {i + 1}. {ctx['line']}")
            print(
                f"     ...{' '.join(ctx['before'])} **{ctx['word']}** {' '.join(ctx['after'])}..."
            )

        # Store results
        results[root_name] = {
            "total_instances": total,
            "standalone_count": standalone_count,
            "standalone_rate": standalone_count / total * 100 if total > 0 else 0,
            "affixed_count": affixed_count,
            "verb_suffix_rate": verb_rate,
            "classification": classification,
            "confidence": confidence,
            "top_before": dict(before_counter.most_common(10)),
            "top_after": dict(after_counter.most_common(10)),
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

    # Save results
    print(f"\n{'=' * 60}")
    print("Saving results to LCH_S_R_ANALYSIS.json...")
    with open("LCH_S_R_ANALYSIS.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for root_name, data in results.items():
        print(f"\n[{root_name}]:")
        print(f"  Total: {data['total_instances']}")
        print(f"  Standalone: {data['standalone_rate']:.1f}%")
        print(f"  VERB suffix: {data['verb_suffix_rate']:.1f}%")
        print(
            f"  Classification: {data['classification']} ({data['confidence']} confidence)"
        )

    print("\nKnown patterns for comparison:")
    print(
        f"  Verbal roots ([?sh], [?ch]): {known_verbal['verb_suffix_rate']:.1f}% VERB, {known_verbal['standalone_rate']:.1f}% standalone"
    )
    print(
        f"  Nominal roots ([?al]): {known_nominal['verb_suffix_rate']:.1f}% VERB, {known_nominal['standalone_rate']:.1f}% standalone"
    )


if __name__ == "__main__":
    main()
