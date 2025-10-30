#!/usr/bin/env python3
"""
Recipe Sequence Deep Dive Analysis

Analyze the 71 complete recipe sequences ([?al] + [?ch]-VERB + [?sh]-VERB)
to find patterns, sub-structures, and attempt readable translations.
"""

import json
import re
from collections import Counter, defaultdict


def load_translations():
    with open(
        "COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)
    return data["translations"]


def find_recipe_sequences(translations):
    """Find sentences with [?al] + [?ch]-VERB + [?sh]-VERB pattern"""
    sequences = []

    for trans in translations:
        sentence = trans["final_translation"]

        # Check if contains all three elements
        has_al = "[?al]" in sentence or "al-" in sentence or "-al " in sentence
        has_ch_verb = "[?ch]" in sentence and "VERB" in sentence
        has_sh_verb = "[?sh]" in sentence and "VERB" in sentence

        if has_al and has_ch_verb and has_sh_verb:
            sequences.append(
                {
                    "folio": trans.get("folio", "unknown"),
                    "sentence": sentence,
                    "original": trans.get("original", ""),
                }
            )

    return sequences


def analyze_sequence_structure(sequences):
    """Analyze structural patterns in recipe sequences"""

    patterns = {
        "with_vessel": [],
        "with_water": [],
        "with_botanical": [],
        "with_oak_gen": [],
        "with_oat_gen": [],
        "with_multiple_actions": [],  # More than 2 verbs
        "with_or": [],  # Contains alternatives
        "with_then": [],  # Sequential markers
        "short": [],  # < 10 words
        "medium": [],  # 10-20 words
        "long": [],  # > 20 words
    }

    for seq in sequences:
        sentence = seq["sentence"]
        word_count = len(sentence.split())

        # Categorize by features
        if "vessel" in sentence.lower():
            patterns["with_vessel"].append(seq)

        if "water" in sentence.lower():
            patterns["with_water"].append(seq)

        if "botanical-term" in sentence:
            patterns["with_botanical"].append(seq)

        if "oak-GEN" in sentence:
            patterns["with_oak_gen"].append(seq)

        if "oat-GEN" in sentence:
            patterns["with_oat_gen"].append(seq)

        # Count verbs
        verb_count = sentence.count("-VERB")
        if verb_count > 2:
            patterns["with_multiple_actions"].append(seq)

        if "OR" in sentence:
            patterns["with_or"].append(seq)

        if "THEN" in sentence:
            patterns["with_then"].append(seq)

        # Length categories
        if word_count < 10:
            patterns["short"].append(seq)
        elif word_count < 20:
            patterns["medium"].append(seq)
        else:
            patterns["long"].append(seq)

    return patterns


def extract_sub_patterns(sequences):
    """Extract common sub-patterns (bigrams, trigrams)"""

    bigrams = Counter()
    trigrams = Counter()

    for seq in sequences:
        words = seq["sentence"].split()

        # Extract bigrams
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i + 1]}"
            bigrams[bigram] += 1

        # Extract trigrams
        for i in range(len(words) - 2):
            trigram = f"{words[i]} {words[i + 1]} {words[i + 2]}"
            trigrams[trigram] += 1

    return bigrams, trigrams


def main():
    print("=" * 80)
    print("RECIPE SEQUENCE DEEP DIVE: Analyzing 71 Complete Recipe Patterns")
    print("=" * 80)
    print()

    # Load data
    print("Loading translations...")
    translations = load_translations()
    print(f"Total sentences: {len(translations)}")
    print()

    # Find recipe sequences
    print("Finding complete recipe sequences ([?al] + [?ch]-VERB + [?sh]-VERB)...")
    sequences = find_recipe_sequences(translations)
    print(f"Found: {len(sequences)} sequences")
    print()

    # Analyze structure
    print("=" * 80)
    print("STRUCTURAL ANALYSIS")
    print("=" * 80)
    print()

    patterns = analyze_sequence_structure(sequences)

    print("FEATURE ANALYSIS:")
    print(
        f"  With vessel: {len(patterns['with_vessel'])} ({len(patterns['with_vessel']) / len(sequences) * 100:.1f}%)"
    )
    print(
        f"  With water: {len(patterns['with_water'])} ({len(patterns['with_water']) / len(sequences) * 100:.1f}%)"
    )
    print(
        f"  With botanical-term: {len(patterns['with_botanical'])} ({len(patterns['with_botanical']) / len(sequences) * 100:.1f}%)"
    )
    print(
        f"  With oak-GEN: {len(patterns['with_oak_gen'])} ({len(patterns['with_oak_gen']) / len(sequences) * 100:.1f}%)"
    )
    print(
        f"  With oat-GEN: {len(patterns['with_oat_gen'])} ({len(patterns['with_oat_gen']) / len(sequences) * 100:.1f}%)"
    )
    print(
        f"  With >2 verbs: {len(patterns['with_multiple_actions'])} ({len(patterns['with_multiple_actions']) / len(sequences) * 100:.1f}%)"
    )
    print(
        f"  With OR (alternatives): {len(patterns['with_or'])} ({len(patterns['with_or']) / len(sequences) * 100:.1f}%)"
    )
    print(
        f"  With THEN (sequential): {len(patterns['with_then'])} ({len(patterns['with_then']) / len(sequences) * 100:.1f}%)"
    )
    print()

    print("LENGTH DISTRIBUTION:")
    print(f"  Short (< 10 words): {len(patterns['short'])}")
    print(f"  Medium (10-20 words): {len(patterns['medium'])}")
    print(f"  Long (> 20 words): {len(patterns['long'])}")
    print()

    # Common sub-patterns
    print("=" * 80)
    print("COMMON SUB-PATTERNS")
    print("=" * 80)
    print()

    bigrams, trigrams = extract_sub_patterns(sequences)

    print("TOP 20 BIGRAMS (2-word sequences):")
    for bigram, count in bigrams.most_common(20):
        print(f"  {bigram}: {count}×")
    print()

    print("TOP 20 TRIGRAMS (3-word sequences):")
    for trigram, count in trigrams.most_common(20):
        print(f"  {trigram}: {count}×")
    print()

    # Examples by category
    print("=" * 80)
    print("EXAMPLE SEQUENCES BY TYPE")
    print("=" * 80)
    print()

    print("SIMPLE RECIPES (with vessel):")
    for i, seq in enumerate(patterns["with_vessel"][:5], 1):
        print(f"\n{i}. {seq['folio']}:")
        print(f"   {seq['sentence']}")

    print("\n" + "=" * 80)
    print("COMPLEX RECIPES (>2 verbs):")
    for i, seq in enumerate(patterns["with_multiple_actions"][:5], 1):
        print(f"\n{i}. {seq['folio']}:")
        print(f"   {seq['sentence']}")

    print("\n" + "=" * 80)
    print("RECIPES WITH ALTERNATIVES (OR):")
    for i, seq in enumerate(patterns["with_or"][:5], 1):
        print(f"\n{i}. {seq['folio']}:")
        print(f"   {seq['sentence']}")

    print("\n" + "=" * 80)
    print("BOTANICAL RECIPES (with botanical-term):")
    for i, seq in enumerate(patterns["with_botanical"][:5], 1):
        print(f"\n{i}. {seq['folio']}:")
        print(f"   {seq['sentence']}")

    print("\n" + "=" * 80)
    print("RECIPES WITH BOTH oak-GEN AND oat-GEN:")
    both = [
        s
        for s in sequences
        if "oak-GEN" in s["sentence"] and "oat-GEN" in s["sentence"]
    ]
    for i, seq in enumerate(both[:5], 1):
        print(f"\n{i}. {seq['folio']}:")
        print(f"   {seq['sentence']}")

    # Attempt readable translations
    print("\n" + "=" * 80)
    print("ATTEMPTED READABLE TRANSLATIONS")
    print("=" * 80)
    print()
    print("Using semantic interpretations:")
    print("  [?al] = substance/preparation")
    print("  [?ch]-VERB = prepare/make/mix")
    print("  [?sh]-VERB = apply/use/place")
    print("  oak-GEN = oak-related (or similar)")
    print("  oat-GEN = oat-related (or similar)")
    print()

    # Pick diverse examples
    simple = patterns["short"][0] if patterns["short"] else None
    with_vessel_ex = patterns["with_vessel"][0] if patterns["with_vessel"] else None
    complex_ex = (
        patterns["with_multiple_actions"][0]
        if patterns["with_multiple_actions"]
        else None
    )

    examples = [
        (simple, "Simple short recipe"),
        (with_vessel_ex, "Recipe with vessel"),
        (complex_ex, "Complex multi-step recipe"),
    ]

    for seq, description in examples:
        if seq:
            print(f"\n{description}:")
            print(f"Folio: {seq['folio']}")
            print(f"\nStructural parse:")
            print(f"  {seq['sentence']}")
            print(f"\nAttempted translation:")
            # Simple substitution for demo
            translation = seq["sentence"]
            translation = translation.replace("[?al]", "[substance]")
            translation = translation.replace("[?ch]-VERB", "[prepare]")
            translation = translation.replace("[?sh]-VERB", "[apply]")
            translation = translation.replace("oak-GEN", "oak-related")
            translation = translation.replace("oat-GEN", "oat-related")
            translation = translation.replace("[PARTICLE]", "")
            translation = translation.replace("THIS/THAT", "this")
            print(f"  {translation}")
            print()

    # Save detailed analysis
    output = {
        "total_sequences": len(sequences),
        "patterns": {k: len(v) for k, v in patterns.items()},
        "top_bigrams": dict(bigrams.most_common(20)),
        "top_trigrams": dict(trigrams.most_common(20)),
        "examples": {
            "simple": [s["sentence"] for s in patterns["short"][:10]],
            "with_vessel": [s["sentence"] for s in patterns["with_vessel"][:10]],
            "complex": [s["sentence"] for s in patterns["with_multiple_actions"][:10]],
            "with_botanical": [s["sentence"] for s in patterns["with_botanical"][:10]],
        },
    }

    with open("RECIPE_SEQUENCE_ANALYSIS.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("=" * 80)
    print("Analysis saved to: RECIPE_SEQUENCE_ANALYSIS.json")
    print("=" * 80)


if __name__ == "__main__":
    main()
