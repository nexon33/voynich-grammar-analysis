#!/usr/bin/env python3
"""
Phase 17: Investigate the [?e] root - the most frequent unknown element.

This root appears 1,165+ times, primarily in oak-GEN-[?e]-VERB pattern.
Goal: Determine if "e" is a standalone root that should be validated.
"""

import json
import re
from collections import Counter, defaultdict


def load_translation_data():
    """Load Phase 16 translation data."""
    with open(
        "COMPLETE_MANUSCRIPT_TRANSLATION_PHASE16.json", "r", encoding="utf-8"
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


def find_e_instances(translations):
    """Find all instances where [?e] appears."""
    e_instances = []

    for trans in translations:
        text = trans["final_translation"]
        original = trans["original"]
        folio = trans["folio"]

        # Look for [?e] in translation
        if "[?e]" in text:
            e_instances.append(
                {
                    "folio": folio,
                    "original": original,
                    "translation": text,
                    "words": trans["words"],
                }
            )

    return e_instances


def analyze_e_contexts(e_instances):
    """Analyze the contexts where 'e' appears."""

    # What comes before [?e]?
    before_pattern = Counter()
    # What comes after [?e]?
    after_pattern = Counter()
    # What prefixes combine with e?
    prefix_combinations = Counter()
    # What suffixes combine with e?
    suffix_combinations = Counter()

    # Full word forms containing 'e'
    word_forms = Counter()

    for instance in e_instances:
        translation_words = instance["translation"].split()
        original_words = instance["original"].split()

        # Find position of [?e] in translation
        for i, trans_word in enumerate(translation_words):
            if "[?e]" in trans_word:
                # What comes before in the sentence?
                if i > 0:
                    before_pattern[translation_words[i - 1]] += 1

                # What comes after in the sentence?
                if i < len(translation_words) - 1:
                    after_pattern[translation_words[i + 1]] += 1

                # Analyze the structure of this word
                # Look for patterns like "oak-GEN-[?e]-VERB"
                parts = trans_word.split("-")
                if len(parts) > 1:
                    for j, part in enumerate(parts):
                        if part == "[?e]":
                            # What's before in this word?
                            if j > 0:
                                prefix_combinations["-".join(parts[:j])] += 1
                            # What's after in this word?
                            if j < len(parts) - 1:
                                suffix_combinations["-".join(parts[j + 1 :])] += 1

                # Record the full word form from original
                if i < len(original_words):
                    word_forms[original_words[i]] += 1

    return {
        "before_pattern": before_pattern,
        "after_pattern": after_pattern,
        "prefix_combinations": prefix_combinations,
        "suffix_combinations": suffix_combinations,
        "word_forms": word_forms,
    }


def find_standalone_e(sentences):
    """Find instances of standalone 'e' in the original text."""
    standalone_e = []

    for sent in sentences:
        words = sent["text"].lower().split()
        for i, word in enumerate(words):
            # Look for 'e' as a standalone word or very short form
            if word == "e":
                context_before = words[i - 3 : i] if i >= 3 else words[:i]
                context_after = (
                    words[i + 1 : i + 4] if i < len(words) - 3 else words[i + 1 :]
                )

                standalone_e.append(
                    {
                        "folio": sent["folio"],
                        "full_text": sent["text"],
                        "before": " ".join(context_before),
                        "word": word,
                        "after": " ".join(context_after),
                    }
                )

    return standalone_e


def check_e_morphology(sentences):
    """Check if 'e' combines with validated suffixes to form words."""

    # Known suffixes
    suffixes = ["al", "ol", "ar", "or", "dy", "edy", "ain", "iin", "aiin", "d"]

    e_forms = Counter()

    for sent in sentences:
        words = sent["text"].lower().split()
        for word in words:
            # Check if word starts with 'e' and ends with a known suffix
            if word.startswith("e") and len(word) > 1:
                for suffix in suffixes:
                    if word.endswith(suffix):
                        # Extract the stem
                        stem = word[: len(word) - len(suffix)]
                        if stem == "e":
                            e_forms[word] += 1
                            break

    return e_forms


def main():
    print("=" * 80)
    print("PHASE 17: INVESTIGATING THE [?e] ROOT")
    print("=" * 80)
    print("Goal: Determine if 'e' is a standalone root that should be validated\n")

    # Load data
    print("Loading translation data...")
    translation_data = load_translation_data()

    print("Loading EVA sentences...")
    sentences = load_sentences()

    print(f"Loaded {len(translation_data['translations'])} translations")
    print(f"Loaded {len(sentences)} sentences\n")

    # Find [?e] instances in translations
    print("Finding [?e] instances in translations...")
    e_instances = find_e_instances(translation_data["translations"])
    print(f"Found {len(e_instances)} sentences containing [?e]\n")

    # Analyze contexts
    print("=" * 80)
    print("CONTEXT ANALYSIS")
    print("=" * 80)
    contexts = analyze_e_contexts(e_instances)

    print("\nTop 20 PREFIXES that combine with [?e]:")
    for prefix, count in contexts["prefix_combinations"].most_common(20):
        print(f"  {prefix:30s}: {count:4d}×")

    print("\nTop 20 SUFFIXES that combine with [?e]:")
    for suffix, count in contexts["suffix_combinations"].most_common(20):
        print(f"  {suffix:30s}: {count:4d}×")

    print("\nTop 20 WORDS that come BEFORE [?e]:")
    for word, count in contexts["before_pattern"].most_common(20):
        print(f"  {word:40s}: {count:4d}×")

    print("\nTop 20 WORDS that come AFTER [?e]:")
    for word, count in contexts["after_pattern"].most_common(20):
        print(f"  {word:40s}: {count:4d}×")

    # Check standalone 'e'
    print("\n" + "=" * 80)
    print("STANDALONE 'e' ANALYSIS")
    print("=" * 80)
    standalone = find_standalone_e(sentences)
    print(f"\nFound {len(standalone)} instances of standalone 'e' word")

    if len(standalone) > 0:
        print("\nFirst 10 examples:")
        for i, ex in enumerate(standalone[:10], 1):
            print(f"{i:2d}. [{ex['folio']}]")
            print(f"    Before: {ex['before']}")
            print(f"    Word:   '{ex['word']}'")
            print(f"    After:  {ex['after']}")
            print()

    # Check e + suffix forms
    print("=" * 80)
    print("'e' + SUFFIX FORMS")
    print("=" * 80)
    e_forms = check_e_morphology(sentences)
    print(f"\nFound {len(e_forms)} different forms of 'e' + suffix")
    print("\nTop 20 forms:")
    for form, count in e_forms.most_common(20):
        print(f"  {form:20s}: {count:4d}×")

    # Check original word forms
    print("\n" + "=" * 80)
    print("ORIGINAL WORD FORMS (containing 'e')")
    print("=" * 80)
    print("\nTop 30 most common word forms translated as containing [?e]:")
    for form, count in contexts["word_forms"].most_common(30):
        print(f"  {form:20s}: {count:4d}×")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    total_prefix_combos = sum(contexts["prefix_combinations"].values())
    total_suffix_combos = sum(contexts["suffix_combinations"].values())

    print(f"\n[?e] Statistics:")
    print(f"  Sentences containing [?e]: {len(e_instances)}")
    print(f"  Prefix combinations: {total_prefix_combos}")
    print(f"  Suffix combinations: {total_suffix_combos}")
    print(f"  Standalone 'e' instances: {len(standalone)}")
    print(f"  'e' + suffix forms: {len(e_forms)} types, {sum(e_forms.values())} tokens")

    # Most common pattern
    if len(contexts["prefix_combinations"]) > 0:
        top_prefix = contexts["prefix_combinations"].most_common(1)[0]
        print(f"\n  Most common prefix pattern: {top_prefix[0]} ({top_prefix[1]}×)")

    if len(contexts["suffix_combinations"]) > 0:
        top_suffix = contexts["suffix_combinations"].most_common(1)[0]
        print(f"  Most common suffix pattern: {top_suffix[0]} ({top_suffix[1]}×)")

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("\nBased on this analysis:")
    print("1. If 'e' + suffix forms are common → 'e' is likely a ROOT")
    print("2. If 'e' only appears in compounds → 'e' might be part of compound roots")
    print("3. Check if the most common forms suggest a semantic meaning")
    print()

    # Save results
    results = {
        "total_instances": len(e_instances),
        "prefix_combinations": dict(contexts["prefix_combinations"].most_common(30)),
        "suffix_combinations": dict(contexts["suffix_combinations"].most_common(30)),
        "standalone_count": len(standalone),
        "e_suffix_forms": dict(e_forms.most_common(30)),
        "original_word_forms": dict(contexts["word_forms"].most_common(50)),
    }

    with open("PHASE17_E_ROOT_INVESTIGATION.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("Results saved to: PHASE17_E_ROOT_INVESTIGATION.json")


if __name__ == "__main__":
    main()
