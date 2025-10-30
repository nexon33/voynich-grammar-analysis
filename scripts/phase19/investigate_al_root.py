#!/usr/bin/env python3
"""
Phase 19: Investigation of [?al] Root

OBJECTIVE: Structural analysis of 'al' root distribution
APPROACH: No semantic claims, pattern observation only
PURPOSE: Compare with [?sh] and [?ch] to determine grammatical class

This script analyzes the morphological behavior of the unknown root [?al]
without making semantic interpretations.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter


def load_json_file(filepath):
    """Load JSON data from file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}")
        sys.exit(1)


def find_al_instances(translations):
    """Find all instances where [?al] appears in translations."""
    al_instances = []
    for trans in translations:
        text = trans["final_translation"]
        words = text.split()

        for i, word in enumerate(words):
            if "[?al]" in word:
                al_instances.append(
                    {
                        "sentence_id": trans.get("folio", "unknown"),
                        "word": word,
                        "position": i,
                        "full_sentence": text,
                    }
                )

    return al_instances


def analyze_morphology(al_instances):
    """Analyze morphological patterns of 'al'."""

    # Track different patterns
    standalone = []
    with_suffix = []
    with_prefix = []
    word_forms = Counter()
    suffix_patterns = Counter()
    prefix_patterns = Counter()

    for instance in al_instances:
        word = instance["word"]
        word_forms[word] += 1

        # Check if standalone [?al]
        if word == "[?al]":
            standalone.append(instance)

        # Check for prefixes
        # Format: PREFIX-[?al]-... or just [?al]-...
        if "-[?al]" in word:
            prefix = word.split("-[?al]")[0]
            if prefix:
                prefix_patterns[prefix] += 1
                with_prefix.append(instance)

        # Check for suffixes
        # Format: [?al]-SUFFIX or PREFIX-[?al]-SUFFIX
        if "[?al]-" in word:
            parts = word.split("[?al]-")
            if len(parts) > 1 and parts[1]:
                suffix = parts[1]
                suffix_patterns[suffix] += 1
                with_suffix.append(instance)

    return {
        "standalone": standalone,
        "with_suffix": with_suffix,
        "with_prefix": with_prefix,
        "word_forms": word_forms,
        "suffix_patterns": suffix_patterns,
        "prefix_patterns": prefix_patterns,
    }


def analyze_cooccurrence(al_instances, window=5):
    """Analyze what words appear near 'al' in sentences."""

    before_words = Counter()
    after_words = Counter()
    all_cooccurring = Counter()

    for instance in al_instances:
        words = instance["full_sentence"].split()
        pos = instance["position"]

        # Words before
        for i in range(max(0, pos - window), pos):
            if i < len(words):
                before_words[words[i]] += 1
                all_cooccurring[words[i]] += 1

        # Words after
        for i in range(pos + 1, min(len(words), pos + window + 1)):
            if i < len(words):
                after_words[words[i]] += 1
                all_cooccurring[words[i]] += 1

    return {"before": before_words, "after": after_words, "all": all_cooccurring}


def check_validated_vocabulary(al_instances):
    """Check which validated morphemes appear in sentences with 'al'."""

    # List of validated morphemes to search for
    validated = [
        "T",
        "D",
        "AT",
        "OL",
        "OR",
        "THEN",
        "AND",
        "THERE",
        "VERB",
        "LOC",
        "DEF",
        "DIR",
        "INST",
        "oak-GEN",
        "oat-GEN",
        "botanical-term",
        "vessel",
        "water",
        "DAR",
        "OKAL",
        "DOL",
        "SKY",
        "red",
    ]

    validated_counts = Counter()

    for instance in al_instances:
        sentence = instance["full_sentence"]
        for morpheme in validated:
            # Count occurrences of each validated morpheme in the sentence
            validated_counts[morpheme] += sentence.count(morpheme)

    return validated_counts


def main():
    print("=" * 80)
    print("PHASE 19: INVESTIGATION OF [?al] ROOT")
    print("=" * 80)
    print("OBJECTIVE: Structural analysis of 'al' root distribution")
    print("APPROACH: No semantic claims, pattern observation only")
    print("PURPOSE: Compare with [?sh] and [?ch] patterns")
    print()

    # Load data
    print("Loading translation data...")
    data = load_json_file("COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json")
    translations = data["translations"]
    print(f"Loaded {len(translations)} translations")
    print()

    # Find all [?al] instances
    print("Finding [?al] instances in translations...")
    al_instances = find_al_instances(translations)
    print(f"Found {len(al_instances)} sentences containing [?al]")
    print()

    # Analyze morphology
    print("=" * 80)
    print("MORPHOLOGICAL PATTERNS")
    print("=" * 80)
    print("Analyzing how 'al' combines with affixes...")
    print()

    morph = analyze_morphology(al_instances)

    print(f"STANDALONE '[?al]' (no affixes): {len(morph['standalone'])} instances")
    print()

    print("PREFIX COMBINATIONS:")
    for prefix, count in morph["prefix_patterns"].most_common(10):
        print(f"  {prefix:15s}: {count:4d}×")
    print()

    print("SUFFIX COMBINATIONS (Top 20):")
    for suffix, count in morph["suffix_patterns"].most_common(20):
        print(f"  {suffix:15s}: {count:4d}×")
    print()

    print("WORD FORMS (Top 30):")
    for word, count in morph["word_forms"].most_common(30):
        # Clean up the display
        display_word = word.replace("[?al]", "al")
        print(f"  {display_word:20s}: {count:4d}×")
    print()

    # Co-occurrence analysis
    print("=" * 80)
    print("CO-OCCURRENCE PATTERNS")
    print("=" * 80)
    print("Analyzing what appears near 'al' in sentences...")
    print()

    cooccur = analyze_cooccurrence(al_instances)

    print("WORDS APPEARING BEFORE [?al] (Top 20):")
    for word, count in cooccur["before"].most_common(20):
        print(f"  {word:40s}: {count:4d}×")
    print()

    print("WORDS APPEARING AFTER [?al] (Top 20):")
    for word, count in cooccur["after"].most_common(20):
        print(f"  {word:40s}: {count:4d}×")
    print()

    print("MOST COMMON CO-OCCURRING WORDS (Top 30):")
    for word, count in cooccur["all"].most_common(30):
        print(f"  {word:40s}: {count:4d}×")
    print()

    # Validated vocabulary
    print("=" * 80)
    print("VALIDATED VOCABULARY CO-OCCURRENCE")
    print("=" * 80)
    print("Checking which validated elements appear with 'al'...")
    print()

    validated = check_validated_vocabulary(al_instances)

    print("VALIDATED ELEMENTS IN SENTENCES WITH [?al]:")
    for morpheme, count in validated.most_common():
        if count > 0:
            print(f"  {morpheme:30s}: {count:4d}×")
    print()

    # Summary statistics
    print("=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    print()

    total_with_suffix = len(morph["with_suffix"])
    total_instances = len(al_instances)

    print(f"[?al] ROOT STATISTICS:")
    print(f"  Total sentences with [?al]: {total_instances}")
    print(f"  Standalone instances: {len(morph['standalone'])}")
    print(f"  With suffix: {total_with_suffix} instances")
    print(f"  With prefix: {len(morph['with_prefix'])} instances")
    print(f"  Unique word forms: {len(morph['word_forms'])}")
    print()

    # Calculate suffix type percentages
    suffix_counts = morph["suffix_patterns"]
    verb_count = sum(
        count
        for suffix, count in suffix_counts.items()
        if "VERB" in suffix or suffix in ["edy", "dy", "eedy"]
    )
    loc_count = sum(
        count
        for suffix, count in suffix_counts.items()
        if "LOC" in suffix or suffix in ["ol"]
    )
    inst_count = sum(
        count
        for suffix, count in suffix_counts.items()
        if "INST" in suffix or suffix in ["or", "ar"]
    )

    if total_with_suffix > 0:
        verb_pct = (verb_count / total_with_suffix) * 100
        loc_pct = (loc_count / total_with_suffix) * 100
        inst_pct = (inst_count / total_with_suffix) * 100

        print(f"  VERB suffix rate: {verb_pct:.1f}% ({verb_count}/{total_with_suffix})")
        print(f"  LOC suffix rate: {loc_pct:.1f}% ({loc_count}/{total_with_suffix})")
        print(f"  INST suffix rate: {inst_pct:.1f}% ({inst_count}/{total_with_suffix})")
    print()

    # Most common patterns
    if morph["suffix_patterns"]:
        most_common_suffix = morph["suffix_patterns"].most_common(1)[0]
        print(
            f"  Most common suffix pattern: '{most_common_suffix[0]}' ({most_common_suffix[1]}×)"
        )

    if morph["word_forms"]:
        most_common_form = morph["word_forms"].most_common(1)[0]
        display_form = most_common_form[0].replace("[?al]", "al")
        print(f"  Most common word form: '{display_form}' ({most_common_form[1]}×)")
    print()

    # Structural observations
    print("=" * 80)
    print("STRUCTURAL OBSERVATIONS")
    print("=" * 80)
    print()
    print("OBJECTIVE PATTERNS (No semantic interpretation):")
    print()

    if len(morph["standalone"]) > 0:
        print(f"1. 'al' appears standalone {len(morph['standalone'])} times")
        print("   → Likely a ROOT, not an affix")
        print()

    if total_with_suffix > 0 and verb_count > 0:
        print(f"2. 'al' takes VERB suffix {verb_count} times ({verb_pct:.1f}%)")
        if verb_pct > 50:
            print("   → Suggests possible verbal function")
        elif verb_pct > 30:
            print("   → Can function verbally (moderate frequency)")
        else:
            print("   → Verbal function less common than [?sh]/[?ch]")
        print()

    if inst_count > 0:
        print(f"3. 'al' appears with INST suffix {inst_count} times ({inst_pct:.1f}%)")
        print("   → Can function in instrumental constructions")
        print()

    if loc_count > 0:
        print(f"4. 'al' appears with LOC suffix {loc_count} times ({loc_pct:.1f}%)")
        print("   → Can function in locative constructions")
        print()

    # Comparison note
    print("=" * 80)
    print("COMPARISON WITH [?sh] AND [?ch]")
    print("=" * 80)
    print()
    print("For reference:")
    print("  [?sh]: 60.4% VERB suffix, 16.5% INST, 8.7% LOC")
    print("  [?ch]: 57.9% VERB suffix, 16.1% INST, 5.8% LOC")
    if total_with_suffix > 0:
        print(
            f"  [?al]: {verb_pct:.1f}% VERB suffix, {inst_pct:.1f}% INST, {loc_pct:.1f}% LOC"
        )
        print()

        if abs(verb_pct - 60) < 10:
            print("→ [?al] shows SIMILAR verbal behavior to [?sh] and [?ch]")
            print("  Likely same grammatical class (verbal roots)")
        elif verb_pct > 40:
            print("→ [?al] shows MODERATE verbal behavior")
            print("  May be verbal but with different distribution")
        else:
            print("→ [?al] shows DIFFERENT behavior from [?sh] and [?ch]")
            print("  Likely different grammatical class")
    print()

    print("=" * 80)
    print("NO SEMANTIC CLAIMS MADE")
    print("=" * 80)
    print()
    print("This analysis provides STRUCTURAL DATA only.")
    print("Semantic interpretation requires:")
    print("  - Expert consultation")
    print("  - Comparative analysis")
    print("  - Contextual validation")
    print("  - Inter-rater reliability testing")
    print()

    # Save results
    output_file = "PHASE19_AL_ROOT_INVESTIGATION.json"
    output_data = {
        "total_instances": total_instances,
        "standalone_count": len(morph["standalone"]),
        "with_suffix_count": total_with_suffix,
        "with_prefix_count": len(morph["with_prefix"]),
        "unique_word_forms": len(morph["word_forms"]),
        "verb_percentage": verb_pct if total_with_suffix > 0 else 0,
        "inst_percentage": inst_pct if total_with_suffix > 0 else 0,
        "loc_percentage": loc_pct if total_with_suffix > 0 else 0,
        "suffix_patterns": dict(morph["suffix_patterns"].most_common(20)),
        "word_forms": dict(morph["word_forms"].most_common(30)),
        "cooccurrence_before": dict(cooccur["before"].most_common(20)),
        "cooccurrence_after": dict(cooccur["after"].most_common(20)),
        "validated_vocabulary": dict(validated.most_common()),
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {output_file}")
    print()


if __name__ == "__main__":
    main()
