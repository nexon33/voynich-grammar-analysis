#!/usr/bin/env python3
"""
Phase 18B: Systematic Investigation of [?ch] Root

GOAL: Analyze distributional patterns of 'ch' root WITHOUT making semantic claims.
APPROACH: Objective structural analysis only, compare with [?sh] patterns.
OUTPUT: Data for comparison and future semantic validation.

Note: This is STRUCTURAL ANALYSIS, not semantic interpretation.
"""

import json
import re
from collections import Counter, defaultdict


def load_translation_data():
    """Load Phase 17 translation data."""
    with open(
        "COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8"
    ) as f:
        return json.load(f)


def load_sentences():
    """Load EVA sentences."""
    sentences = []
    with open(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt",
        "r",
        encoding="utf-8",
    ) as f:
        line_number = 0
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            line_number += 1
            match = re.match(r"<(f\d+[rv]?)[\.\d,@]*>\s+(.+)$", line)
            if match:
                folio = match.group(1)
                text = match.group(2).strip()
            else:
                folio = f"line{line_number}"
                text = line

            sentences.append({"folio": folio, "text": text})

    return sentences


def find_ch_instances(translations):
    """Find all instances where [?ch] appears in translations."""
    ch_instances = []

    for trans in translations:
        text = trans["final_translation"]
        original = trans["original"]
        folio = trans["folio"]

        # Look for [?ch] in translation
        if "[?ch]" in text:
            ch_instances.append(
                {
                    "folio": folio,
                    "original": original,
                    "translation": text,
                    "words": trans["words"],
                }
            )

    return ch_instances


def analyze_morphological_patterns(ch_instances):
    """Analyze how 'ch' combines with affixes."""

    prefix_combinations = Counter()
    suffix_combinations = Counter()
    standalone_count = 0

    # Collect all word forms containing 'ch'
    word_forms = Counter()

    for instance in ch_instances:
        for word in instance["words"]:
            # Check if this word contains [?ch] in its translation
            if word["morphology"]["root"] == "ch":
                orig = word["original"]
                word_forms[orig] += 1

                # Check for prefix
                prefix = word["morphology"]["prefix"]
                if prefix:
                    prefix_combinations[prefix] += 1

                # Check for suffixes
                suffixes = word["morphology"]["suffixes"]
                if suffixes:
                    suffix_str = "-".join(suffixes)
                    suffix_combinations[suffix_str] += 1
                else:
                    standalone_count += 1

    return {
        "prefix_combinations": prefix_combinations,
        "suffix_combinations": suffix_combinations,
        "standalone_count": standalone_count,
        "word_forms": word_forms,
    }


def analyze_cooccurrence(ch_instances):
    """Analyze what words co-occur with 'ch' in sentences."""

    # Words that appear in same sentence as 'ch'
    cooccurrence = Counter()

    # Position patterns: what comes before/after 'ch'
    before_ch = Counter()
    after_ch = Counter()

    for instance in ch_instances:
        words = instance["translation"].split()

        # Find position of [?ch] words
        for i, word in enumerate(words):
            if "[?ch]" in word:
                # What comes before?
                if i > 0:
                    before_ch[words[i - 1]] += 1

                # What comes after?
                if i < len(words) - 1:
                    after_ch[words[i + 1]] += 1

        # Count all words in sentences with 'ch'
        for word in words:
            if "[?ch]" not in word:
                cooccurrence[word] += 1

    return {"cooccurrence": cooccurrence, "before_ch": before_ch, "after_ch": after_ch}


def check_validated_vocabulary_cooccurrence(ch_instances):
    """Check which validated vocabulary items co-occur with 'ch'."""

    # Known validated vocabulary
    validated = [
        "oak-GEN",
        "oat-GEN",
        "AT",
        "T",  # Prefixes
        "LOC",
        "DIR",
        "INST",
        "VERB",
        "DEF",
        "D",  # Suffixes
        "THIS/THAT",
        "THERE",
        "SKY",
        "OR",
        "AND",
        "THEN",  # Function words
        "botanical-term",
        "vessel",
        "water",
        "red",  # Semantic terms
        "DAR",
        "DOL",
        "OL",
        "OKAL",  # Known words (meaning unclear)
    ]

    cooccurrence = defaultdict(int)

    for instance in ch_instances:
        words = instance["translation"].split()

        # Check for validated vocabulary in same sentence
        for word in words:
            for val in validated:
                if val in word:
                    cooccurrence[val] += 1

    return dict(cooccurrence)


def main():
    print("=" * 80)
    print("PHASE 18B: INVESTIGATION OF [?ch] ROOT")
    print("=" * 80)
    print("OBJECTIVE: Structural analysis of 'ch' root distribution")
    print("APPROACH: No semantic claims, pattern observation only")
    print("PURPOSE: Compare with [?sh] root patterns")
    print()

    # Load data
    print("Loading translation data...")
    translation_data = load_translation_data()

    print("Loading EVA sentences...")
    sentences = load_sentences()

    print(f"Loaded {len(translation_data['translations'])} translations")
    print(f"Loaded {len(sentences)} sentences\n")

    # Find [?ch] instances
    print("Finding [?ch] instances in translations...")
    ch_instances = find_ch_instances(translation_data["translations"])
    print(f"Found {len(ch_instances)} sentences containing [?ch]\n")

    # Morphological patterns
    print("=" * 80)
    print("MORPHOLOGICAL PATTERNS")
    print("=" * 80)
    print("Analyzing how 'ch' combines with affixes...\n")

    morph_patterns = analyze_morphological_patterns(ch_instances)

    print("PREFIX COMBINATIONS:")
    if morph_patterns["prefix_combinations"]:
        for prefix, count in morph_patterns["prefix_combinations"].most_common(10):
            print(f"  {prefix:15s}: {count:4d}×")
    else:
        print("  No prefixes found")

    print(
        f"\nSTANDALONE 'ch' (no affixes): {morph_patterns['standalone_count']} instances"
    )

    print("\nSUFFIX COMBINATIONS (Top 20):")
    for suffix, count in morph_patterns["suffix_combinations"].most_common(20):
        print(f"  {suffix:15s}: {count:4d}×")

    print("\nWORD FORMS (Top 30):")
    for form, count in morph_patterns["word_forms"].most_common(30):
        print(f"  {form:20s}: {count:4d}×")

    # Co-occurrence analysis
    print("\n" + "=" * 80)
    print("CO-OCCURRENCE PATTERNS")
    print("=" * 80)
    print("Analyzing what appears near 'ch' in sentences...\n")

    cooccur = analyze_cooccurrence(ch_instances)

    print("WORDS APPEARING BEFORE [?ch] (Top 20):")
    for word, count in cooccur["before_ch"].most_common(20):
        print(f"  {word:40s}: {count:4d}×")

    print("\nWORDS APPEARING AFTER [?ch] (Top 20):")
    for word, count in cooccur["after_ch"].most_common(20):
        print(f"  {word:40s}: {count:4d}×")

    print("\nMOST COMMON CO-OCCURRING WORDS (Top 30):")
    for word, count in cooccur["cooccurrence"].most_common(30):
        print(f"  {word:40s}: {count:4d}×")

    # Validated vocabulary co-occurrence
    print("\n" + "=" * 80)
    print("VALIDATED VOCABULARY CO-OCCURRENCE")
    print("=" * 80)
    print("Checking which validated elements appear with 'ch'...\n")

    validated_cooccur = check_validated_vocabulary_cooccurrence(ch_instances)

    print("VALIDATED ELEMENTS IN SENTENCES WITH [?ch]:")
    for word, count in sorted(
        validated_cooccur.items(), key=lambda x: x[1], reverse=True
    )[:30]:
        print(f"  {word:30s}: {count:4d}×")

    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    total_suffix_combos = sum(morph_patterns["suffix_combinations"].values())
    total_prefix_combos = len(morph_patterns["prefix_combinations"])

    print(f"\n[?ch] ROOT STATISTICS:")
    print(f"  Total sentences with [?ch]: {len(ch_instances)}")
    print(f"  Standalone instances: {morph_patterns['standalone_count']}")
    print(f"  With suffix: {total_suffix_combos} instances")
    print(f"  With prefix: {total_prefix_combos} different prefixes")
    print(f"  Unique word forms: {len(morph_patterns['word_forms'])}")
    print(f"  Total token count: {sum(morph_patterns['word_forms'].values())}")

    # Most productive patterns
    if morph_patterns["suffix_combinations"]:
        top_suffix = morph_patterns["suffix_combinations"].most_common(1)[0]
        print(f"\n  Most common suffix pattern: '{top_suffix[0]}' ({top_suffix[1]}×)")

    if morph_patterns["word_forms"]:
        top_form = morph_patterns["word_forms"].most_common(1)[0]
        print(f"  Most common word form: '{top_form[0]}' ({top_form[1]}×)")

    # Observations (structural only, no semantic claims)
    print("\n" + "=" * 80)
    print("STRUCTURAL OBSERVATIONS")
    print("=" * 80)
    print("\nOBJECTIVE PATTERNS (No semantic interpretation):\n")

    # Check if 'ch' is primarily a verb root
    verb_count = (
        morph_patterns["suffix_combinations"].get("edy", 0)
        + morph_patterns["suffix_combinations"].get("dy", 0)
        + morph_patterns["suffix_combinations"].get("eedy", 0)
    )

    if verb_count > total_suffix_combos * 0.5:
        print(
            f"1. 'ch' frequently takes VERB suffix ({verb_count}/{total_suffix_combos} = {verb_count / total_suffix_combos * 100:.1f}%)"
        )
        print("   → Suggests possible verbal function")

    # Check locative patterns
    loc_count = morph_patterns["suffix_combinations"].get("ol", 0) + morph_patterns[
        "suffix_combinations"
    ].get("al", 0)

    if loc_count > 50:
        print(f"\n2. 'ch' appears with LOC suffix {loc_count} times")
        print("   → Can function in locative constructions")

    # Check if primarily root vs. affix
    if morph_patterns["standalone_count"] > 10:
        print(
            f"\n3. 'ch' appears standalone {morph_patterns['standalone_count']} times"
        )
        print("   → Likely a ROOT, not an affix")
    else:
        print(
            f"\n3. 'ch' rarely standalone ({morph_patterns['standalone_count']} times)"
        )
        print("   → Primarily appears with affixes")

    print("\n" + "=" * 80)
    print("NO SEMANTIC CLAIMS MADE")
    print("=" * 80)
    print("\nThis analysis provides STRUCTURAL DATA only.")
    print("Semantic interpretation requires:")
    print("  - Expert consultation")
    print("  - Comparative analysis")
    print("  - Contextual validation")
    print("  - Inter-rater reliability testing")
    print()

    # Save results
    results = {
        "total_instances": len(ch_instances),
        "morphological_patterns": {
            "prefix_combinations": dict(
                morph_patterns["prefix_combinations"].most_common(20)
            ),
            "suffix_combinations": dict(
                morph_patterns["suffix_combinations"].most_common(30)
            ),
            "standalone_count": morph_patterns["standalone_count"],
            "word_forms": dict(morph_patterns["word_forms"].most_common(50)),
        },
        "cooccurrence": {
            "before": dict(cooccur["before_ch"].most_common(30)),
            "after": dict(cooccur["after_ch"].most_common(30)),
            "general": dict(cooccur["cooccurrence"].most_common(50)),
        },
        "validated_cooccurrence": validated_cooccur,
    }

    with open("PHASE18B_CH_ROOT_INVESTIGATION.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("Results saved to: PHASE18B_CH_ROOT_INVESTIGATION.json")


if __name__ == "__main__":
    main()
