#!/usr/bin/env python3
"""
Investigate prefix semantics: qok-, qot-, ot-, t-
Analyze what roots/stems they attach to and their distributional patterns
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


def extract_prefix_instances(translations):
    """
    Extract all instances of words with specific prefixes
    Returns: prefix_data dict with instances categorized by prefix
    """
    prefix_patterns = {
        "qok-": re.compile(r"\bqok"),
        "qot-": re.compile(r"\bqot"),
        "ot-": re.compile(r"\bot(?!-PREP)"),  # Exclude ot-PREP (separate morpheme)
        "t-": re.compile(r"\bt-"),  # Match t- prefix
    }

    prefix_data = {"qok-": [], "qot-": [], "ot-": [], "t-": []}

    for idx, trans in enumerate(translations):
        sentence = trans["final_translation"]
        words = sentence.split()

        for i, word in enumerate(words):
            # Check each prefix pattern
            for prefix_name, pattern in prefix_patterns.items():
                if pattern.search(word.lower()):
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

                    prefix_data[prefix_name].append(context)

    return prefix_data


def analyze_stem_distribution(prefix_instances):
    """
    Analyze what stems/roots appear with each prefix
    """
    stem_counter = Counter()

    for instance in prefix_instances:
        word = instance["word"]
        # Try to extract the stem (everything after the prefix)
        # Handle different formats: qok-X, qokX-SUFFIX, etc.

        # Remove known suffixes first
        base_word = re.sub(
            r"-(VERB|GEN|DAT|ACC|LOC|ABL|INST|DEF|DIR|D|NOM|PREP)", "", word
        )

        stem_counter[base_word] += 1

    return stem_counter


def analyze_suffix_patterns(prefix_instances):
    """
    What suffixes appear with each prefix?
    """
    suffix_counter = Counter()

    for instance in prefix_instances:
        word = instance["word"]
        # Extract suffixes
        suffixes = re.findall(
            r"-(VERB|GEN|DAT|ACC|LOC|ABL|INST|DEF|DIR|D|NOM|PREP)", word
        )
        for suffix in suffixes:
            suffix_counter[suffix] += 1

    return suffix_counter


def analyze_grammatical_class(prefix_instances):
    """
    Are prefixed words more likely to be VERBS or NOUNS?
    """
    verb_count = sum(1 for inst in prefix_instances if "-VERB" in inst["word"])
    noun_indicators = sum(
        1
        for inst in prefix_instances
        if any(
            case in inst["word"]
            for case in ["-GEN", "-DAT", "-ACC", "-LOC", "-ABL", "-INST"]
        )
    )

    total = len(prefix_instances)
    verb_rate = (verb_count / total * 100) if total > 0 else 0
    noun_rate = (noun_indicators / total * 100) if total > 0 else 0

    return verb_rate, noun_rate


def compare_prefixes(prefix_data):
    """
    Compare the four prefixes to find patterns
    """
    comparison = {}

    for prefix_name, instances in prefix_data.items():
        total = len(instances)

        if total == 0:
            comparison[prefix_name] = {"total": 0, "message": "No instances found"}
            continue

        stem_dist = analyze_stem_distribution(instances)
        suffix_dist = analyze_suffix_patterns(instances)
        verb_rate, noun_rate = analyze_grammatical_class(instances)

        # Co-occurrence
        before_words = []
        after_words = []
        for inst in instances:
            before_words.extend(inst["before"])
            after_words.extend(inst["after"])

        before_counter = Counter(before_words)
        after_counter = Counter(after_words)

        comparison[prefix_name] = {
            "total": total,
            "top_stems": dict(stem_dist.most_common(10)),
            "top_suffixes": dict(suffix_dist.most_common(10)),
            "verb_rate": verb_rate,
            "noun_rate": noun_rate,
            "top_before": dict(before_counter.most_common(10)),
            "top_after": dict(after_counter.most_common(10)),
            "sample_contexts": [
                {
                    "line": inst["line"],
                    "word": inst["word"],
                    "before": inst["before"],
                    "after": inst["after"],
                }
                for inst in instances[:10]
            ],
        }

    return comparison


def main():
    """Main analysis"""
    print("Loading translations...")
    translations = load_translations()
    print(f"Loaded {len(translations)} translations\n")

    print("Extracting prefix instances...")
    prefix_data = extract_prefix_instances(translations)

    print("Analyzing prefix patterns...\n")
    comparison = compare_prefixes(prefix_data)

    # Print results
    for prefix_name in ["qok-", "qot-", "ot-", "t-"]:
        data = comparison[prefix_name]

        print("=" * 60)
        print(f"PREFIX: {prefix_name}")
        print("=" * 60)

        if data["total"] == 0:
            print("No instances found\n")
            continue

        print(f"\nTotal instances: {data['total']}")
        print(f"VERB rate: {data['verb_rate']:.1f}%")
        print(f"NOUN indicators rate: {data['noun_rate']:.1f}%")

        print(f"\nTop 10 stems/words with {prefix_name}:")
        for stem, count in data["top_stems"].items():
            print(f"  {stem}: {count}")

        print(f"\nTop suffixes with {prefix_name}:")
        for suffix, count in data["top_suffixes"].items():
            print(f"  {suffix}: {count}")

        print(f"\nTop 10 words BEFORE {prefix_name}:")
        for word, count in data["top_before"].items():
            print(f"  {word}: {count}")

        print(f"\nTop 10 words AFTER {prefix_name}:")
        for word, count in data["top_after"].items():
            print(f"  {word}: {count}")

        print(f"\nSample contexts (first 5):")
        for i, ctx in enumerate(data["sample_contexts"][:5]):
            print(f"\n  {i + 1}. {ctx['line']}")
            print(
                f"     ...{' '.join(ctx['before'])} **{ctx['word']}** {' '.join(ctx['after'])}..."
            )

        print("\n")

    # Save results
    print("=" * 60)
    print("Saving results to PREFIX_ANALYSIS.json...")
    with open("PREFIX_ANALYSIS.json", "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)

    # Comparison summary
    print("\n" + "=" * 60)
    print("COMPARATIVE SUMMARY")
    print("=" * 60)

    print("\nFrequency ranking:")
    freq_ranking = sorted(comparison.items(), key=lambda x: x[1]["total"], reverse=True)
    for i, (prefix, data) in enumerate(freq_ranking, 1):
        print(f"  {i}. {prefix}: {data['total']} instances")

    print("\nGrammatical preferences:")
    for prefix_name in ["qok-", "qot-", "ot-", "t-"]:
        data = comparison[prefix_name]
        if data["total"] > 0:
            classification = (
                "VERBAL" if data["verb_rate"] > data["noun_rate"] else "NOMINAL"
            )
            print(
                f"  {prefix_name}: {classification} ({data['verb_rate']:.1f}% VERB, {data['noun_rate']:.1f}% NOUN)"
            )

    # Check for semantic patterns
    print("\nPotential semantic patterns:")

    # Check if qok- and qot- share similar stems (might be allomorphs)
    if comparison["qok-"]["total"] > 0 and comparison["qot-"]["total"] > 0:
        qok_stems = set(comparison["qok-"]["top_stems"].keys())
        qot_stems = set(comparison["qot-"]["top_stems"].keys())

        # Check if they have similar patterns (after removing prefix)
        qok_roots = set(
            stem.replace("qok", "").replace("oak", "") for stem in qok_stems
        )
        qot_roots = set(
            stem.replace("qot", "").replace("oat", "") for stem in qot_stems
        )

        overlap = qok_roots & qot_roots
        if overlap:
            print(f"  qok-/qot- may be allomorphs (shared roots: {len(overlap)})")

    # Check if ot- and t- are related
    if comparison["ot-"]["total"] > 0 and comparison["t-"]["total"] > 0:
        print(f"  ot- vs t-: May be phonological variants")
        print(f"    ot-: {comparison['ot-']['total']} instances")
        print(f"    t-: {comparison['t-']['total']} instances")


if __name__ == "__main__":
    main()
