#!/usr/bin/env python3
"""
Complete Suffix Inventory Analysis

Goal: Identify ALL suffixes and their functions
Expected gain: +0.5-1% through better suffix classification

Current known suffixes:
- Case markers: -GEN, -DAT, -ACC, -LOC, -ABL, -INST
- Verbal: -VERB
- Definiteness: -DEF, -D
- Directional: -DIR

Questions:
1. Are there unrecognized suffix patterns?
2. Can we distinguish suffix allomorphs? (-dy, -edy, -eedy)
3. Are there compound suffixes? (-DEF-D, -LOC-DIR)
4. What's the frequency distribution?
"""

import json
import re
from collections import Counter, defaultdict


def load_translations():
    """Load translations"""
    with open(
        "COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)
        return data["translations"]


def extract_all_suffixes(translations):
    """
    Extract ALL suffix patterns from the corpus

    Suffix pattern: anything after a hyphen in a word
    """
    suffix_counter = Counter()
    suffix_sequences = Counter()  # For compound suffixes
    word_examples = defaultdict(list)

    for trans in translations:
        sentence = trans["final_translation"]
        words = sentence.split()

        for word in words:
            # Skip particles and unknowns without suffixes
            if word.startswith("[") and "-" not in word:
                continue

            # Find all suffixes in word
            if "-" in word:
                parts = word.split("-")

                # Skip first part (stem)
                suffixes = parts[1:]

                # Count individual suffixes
                for suffix in suffixes:
                    if suffix:  # Skip empty
                        suffix_counter[suffix] += 1

                        # Store example
                        if len(word_examples[suffix]) < 10:
                            word_examples[suffix].append(word)

                # Count suffix sequences (compound suffixes)
                if len(suffixes) > 1:
                    suffix_seq = "-".join(suffixes)
                    suffix_sequences[suffix_seq] += 1

    return suffix_counter, suffix_sequences, word_examples


def classify_suffixes(suffix_counter):
    """
    Classify suffixes by function based on known patterns
    """
    classification = {
        "CASE": [],
        "VERBAL": [],
        "DEFINITENESS": [],
        "DIRECTIONAL": [],
        "UNKNOWN": [],
    }

    # Known patterns
    case_markers = ["GEN", "DAT", "ACC", "LOC", "ABL", "INST", "NOM"]
    verbal_markers = ["VERB"]
    def_markers = ["DEF", "D"]
    dir_markers = ["DIR"]

    for suffix, count in suffix_counter.items():
        if suffix in case_markers:
            classification["CASE"].append((suffix, count))
        elif suffix in verbal_markers:
            classification["VERBAL"].append((suffix, count))
        elif suffix in def_markers:
            classification["DEFINITENESS"].append((suffix, count))
        elif suffix in dir_markers:
            classification["DIRECTIONAL"].append((suffix, count))
        else:
            # Check for patterns
            if "VERB" in suffix:
                classification["VERBAL"].append((suffix, count))
            elif any(case in suffix for case in case_markers):
                classification["CASE"].append((suffix, count))
            else:
                classification["UNKNOWN"].append((suffix, count))

    return classification


def analyze_allomorphs(suffix_counter, word_examples):
    """
    Identify potential allomorphs (different forms of same suffix)

    Known example: -dy, -edy, -eedy (variants)
    """
    # Look for patterns with similar endings
    potential_allomorphs = defaultdict(list)

    for suffix in suffix_counter.keys():
        # Extract ending pattern
        if suffix.endswith("dy"):
            potential_allomorphs["*dy"].append(suffix)
        elif suffix.endswith("edy"):
            potential_allomorphs["*edy"].append(suffix)
        elif suffix.endswith("eedy"):
            potential_allomorphs["*eedy"].append(suffix)
        elif suffix.endswith("y"):
            potential_allomorphs["*y"].append(suffix)
        elif suffix.endswith("ol"):
            potential_allomorphs["*ol"].append(suffix)
        elif suffix.endswith("ain"):
            potential_allomorphs["*ain"].append(suffix)

    return potential_allomorphs


def analyze_compound_suffixes(suffix_sequences):
    """
    Analyze compound suffix patterns

    Example: -DEF-D, -LOC-DIR, -GEN-VERB
    """
    # Categorize by pattern
    patterns = {
        "DEF compounds": [],
        "CASE compounds": [],
        "VERB compounds": [],
        "Other compounds": [],
    }

    for seq, count in suffix_sequences.items():
        if "DEF" in seq:
            patterns["DEF compounds"].append((seq, count))
        elif any(
            case in seq for case in ["GEN", "LOC", "INST", "DIR", "DAT", "ABL", "ACC"]
        ):
            patterns["CASE compounds"].append((seq, count))
        elif "VERB" in seq:
            patterns["VERB compounds"].append((seq, count))
        else:
            patterns["Other compounds"].append((seq, count))

    return patterns


def identify_unknown_patterns(classification):
    """
    Analyze UNKNOWN suffixes to see if they form patterns
    """
    unknown_suffixes = [s for s, c in classification["UNKNOWN"]]

    # Look for common patterns
    patterns = defaultdict(list)

    for suffix in unknown_suffixes:
        # Check length
        length = len(suffix)
        patterns[f"length_{length}"].append(suffix)

        # Check if contains brackets (unknown roots)
        if "[" in suffix:
            patterns["contains_unknown"].append(suffix)

        # Check if all caps (might be morpheme label)
        if suffix.isupper():
            patterns["all_caps"].append(suffix)

        # Check for numbers
        if any(c.isdigit() for c in suffix):
            patterns["contains_number"].append(suffix)

    return patterns


def calculate_suffix_coverage(suffix_counter, translations):
    """
    Calculate how much of the corpus is covered by known vs unknown suffixes
    """
    known_suffixes = [
        "GEN",
        "DAT",
        "ACC",
        "LOC",
        "ABL",
        "INST",
        "NOM",
        "VERB",
        "DEF",
        "D",
        "DIR",
    ]

    known_count = sum(
        count for suffix, count in suffix_counter.items() if suffix in known_suffixes
    )
    total_count = sum(suffix_counter.values())

    known_coverage = known_count / total_count * 100 if total_count > 0 else 0
    unknown_coverage = 100 - known_coverage

    # Count words with suffixes
    total_words = 0
    words_with_suffixes = 0

    for trans in translations:
        words = trans["final_translation"].split()
        total_words += len(words)
        words_with_suffixes += sum(1 for w in words if "-" in w)

    suffix_rate = words_with_suffixes / total_words * 100 if total_words > 0 else 0

    return known_coverage, unknown_coverage, suffix_rate, words_with_suffixes


def main():
    """Main analysis"""
    print("=" * 70)
    print("COMPLETE SUFFIX INVENTORY ANALYSIS")
    print("=" * 70)
    print("\nGoal: Identify all suffixes and improve classification")
    print("Expected gain: +0.5-1% recognition\n")

    print("Loading translations...")
    translations = load_translations()
    print(f"Loaded {len(translations)} translations\n")

    # EXTRACT ALL SUFFIXES
    print("=" * 70)
    print("EXTRACTING ALL SUFFIXES")
    print("=" * 70)

    suffix_counter, suffix_sequences, word_examples = extract_all_suffixes(translations)

    print(f"\nTotal unique suffixes: {len(suffix_counter)}")
    print(f"Total suffix instances: {sum(suffix_counter.values())}")
    print(f"Total compound suffix patterns: {len(suffix_sequences)}")

    # CLASSIFY SUFFIXES
    print("\n" + "=" * 70)
    print("SUFFIX CLASSIFICATION")
    print("=" * 70)

    classification = classify_suffixes(suffix_counter)

    for category, suffixes in classification.items():
        if suffixes:
            total = sum(count for _, count in suffixes)
            print(f"\n{category} ({len(suffixes)} suffixes, {total} instances):")

            # Sort by frequency
            suffixes_sorted = sorted(suffixes, key=lambda x: x[1], reverse=True)

            for suffix, count in suffixes_sorted[:20]:  # Top 20
                pct = count / sum(suffix_counter.values()) * 100
                print(f"  -{suffix:20s}: {count:5d} ({pct:5.2f}%)")

            if len(suffixes) > 20:
                print(f"  ... and {len(suffixes) - 20} more")

    # ALLOMORPH ANALYSIS
    print("\n" + "=" * 70)
    print("ALLOMORPH ANALYSIS")
    print("=" * 70)
    print("Identifying suffix variants (allomorphs)\n")

    allomorphs = analyze_allomorphs(suffix_counter, word_examples)

    for pattern, variants in sorted(allomorphs.items()):
        if len(variants) > 1:
            print(f"\n{pattern} variants:")
            for variant in variants:
                count = suffix_counter[variant]
                print(f"  -{variant:15s}: {count:5d}×")
                # Show example
                if word_examples[variant]:
                    print(f"    Example: {word_examples[variant][0]}")

    # COMPOUND SUFFIXES
    print("\n" + "=" * 70)
    print("COMPOUND SUFFIX ANALYSIS")
    print("=" * 70)
    print("Multi-suffix sequences\n")

    compound_patterns = analyze_compound_suffixes(suffix_sequences)

    for category, compounds in compound_patterns.items():
        if compounds:
            print(f"\n{category} ({len(compounds)} patterns):")
            compounds_sorted = sorted(compounds, key=lambda x: x[1], reverse=True)

            for seq, count in compounds_sorted[:15]:  # Top 15
                print(f"  -{seq:30s}: {count:4d}×")

    # UNKNOWN PATTERN ANALYSIS
    print("\n" + "=" * 70)
    print("UNKNOWN SUFFIX PATTERNS")
    print("=" * 70)

    unknown_patterns = identify_unknown_patterns(classification)

    print(f"\nTotal UNKNOWN suffixes: {len(classification['UNKNOWN'])}")
    print("\nPattern analysis:")

    for pattern_name, suffixes in sorted(unknown_patterns.items()):
        if suffixes:
            print(f"\n{pattern_name}: {len(suffixes)} suffixes")
            for suffix in suffixes[:10]:
                count = suffix_counter[suffix]
                print(f"  -{suffix:20s}: {count:5d}×")

    # COVERAGE ANALYSIS
    print("\n" + "=" * 70)
    print("SUFFIX COVERAGE")
    print("=" * 70)

    known_cov, unknown_cov, suffix_rate, words_with_suff = calculate_suffix_coverage(
        suffix_counter, translations
    )

    print(f"\nSuffix coverage:")
    print(f"  Known suffixes: {known_cov:.2f}%")
    print(f"  Unknown suffixes: {unknown_cov:.2f}%")
    print(f"\nWord-level statistics:")
    print(f"  Words with suffixes: {words_with_suff} ({suffix_rate:.2f}%)")

    # POTENTIAL RECOGNITION GAIN
    print("\n" + "=" * 70)
    print("RECOGNITION GAIN ANALYSIS")
    print("=" * 70)

    # Count high-frequency unknowns that could be reclassified
    high_freq_unknown = [(s, c) for s, c in classification["UNKNOWN"] if c > 50]

    if high_freq_unknown:
        total_instances = sum(c for _, c in high_freq_unknown)
        total_corpus_words = sum(
            len(t["final_translation"].split()) for t in translations
        )
        potential_gain = total_instances / total_corpus_words * 100

        print(f"\nHigh-frequency UNKNOWN suffixes (>50 instances):")
        print(f"  Count: {len(high_freq_unknown)}")
        print(f"  Total instances: {total_instances}")
        print(f"  Potential recognition gain: +{potential_gain:.2f}%")

        print("\nTop candidates for reclassification:")
        high_freq_sorted = sorted(high_freq_unknown, key=lambda x: x[1], reverse=True)
        for suffix, count in high_freq_sorted[:15]:
            print(f"  -{suffix:20s}: {count:5d}×")
            if word_examples[suffix]:
                print(f"    Examples: {', '.join(word_examples[suffix][:3])}")
    else:
        print("\nNo high-frequency unknown suffixes found")
        print("Most suffixes are already classified!")

    # RECOMMENDATIONS
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)

    print("\n1. ALLOMORPH CONSOLIDATION:")
    print("   Variants like -dy, -edy, -eedy can be recognized as same function")
    print("   Gain: Clarity in analysis (no recognition gain)")

    print("\n2. COMPOUND SUFFIX PATTERNS:")
    print("   -DEF-D, -LOC-DIR patterns are systematic")
    print("   These are already counted, so no gain")

    if high_freq_unknown:
        print("\n3. HIGH-FREQUENCY UNKNOWN RECLASSIFICATION:")
        print(f"   {len(high_freq_unknown)} suffixes with >50 instances")
        print(f"   Manual review could clarify function")
        print(f"   Potential gain: +{potential_gain:.2f}%")
    else:
        print("\n3. SUFFIX INVENTORY COMPLETE:")
        print("   No significant unknown suffixes remain")
        print("   Gain: ~0% (inventory is complete)")

    # Save results
    results = {
        "total_suffixes": len(suffix_counter),
        "total_instances": sum(suffix_counter.values()),
        "classification": {
            cat: [(s, c) for s, c in suffixes]
            for cat, suffixes in classification.items()
        },
        "allomorphs": {k: list(v) for k, v in allomorphs.items()},
        "compound_patterns": {
            cat: [(seq, c) for seq, c in patterns]
            for cat, patterns in compound_patterns.items()
        },
        "coverage": {
            "known": known_cov,
            "unknown": unknown_cov,
            "suffix_rate": suffix_rate,
        },
        "high_frequency_unknown": high_freq_unknown if high_freq_unknown else [],
    }

    print("\nSaving results to SUFFIX_INVENTORY_COMPLETE.json...")
    with open("SUFFIX_INVENTORY_COMPLETE.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

    if high_freq_unknown:
        print(f"\nPotential gain from suffix analysis: +{potential_gain:.2f}%")
        print(
            f"Would bring recognition to: 82.2% + {potential_gain:.2f}% = {82.2 + potential_gain:.2f}%"
        )
    else:
        print("\nSuffix inventory is already comprehensive!")
        print("Focus on other morphemes for further gains")

    print("\nDONE!")


if __name__ == "__main__":
    main()
