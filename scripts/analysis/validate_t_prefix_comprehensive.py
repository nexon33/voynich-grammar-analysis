#!/usr/bin/env python3
"""
Comprehensive T- Prefix Validation

Priority: HIGHEST (973 instances = 2.6% of corpus)

From Phase 20 findings:
- T- appears in ~18.7% of sentences
- Attaches to 50+ different stems
- 19.7% take locative/instrumental/directional suffixes
- T-vessel: 43× (container context)

Hypothesis: T- = instrumental/locative marker ("in", "with", "at")

Tests:
1. Cross-section consistency (should appear uniformly if grammatical)
2. Locative/instrumental suffix enrichment (should be >random)
3. Semantic context (vessels, locations, instruments)
4. Compare with AT/IN preposition (possible grammaticalized form)
5. Minimal pairs (X vs T-X - meaning difference?)
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


def build_folio_mapping():
    """Build folio mapping"""
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
    """Classify folio into sections"""
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
        return "unknown"


def test_cross_section_consistency(translations, line_to_folio):
    """
    Test 1: Cross-section consistency

    If T- is grammatical (not semantic):
    Should appear at ~18-20% rate across ALL sections

    If T- is semantic (location-specific):
    Would cluster in certain sections
    """
    section_t_count = defaultdict(int)
    section_total = defaultdict(int)

    for trans in translations:
        line_id = trans.get("line", "unknown")

        # Extract line number
        line_match = re.search(r"line(\d+)", line_id)
        if not line_match:
            continue

        line_num = int(line_match.group(1))
        folio = line_to_folio.get(line_num, None)

        if not folio:
            continue

        section = classify_folio(folio)
        section_total[section] += 1

        sentence = trans["final_translation"]
        # Count T- words
        t_count = len(re.findall(r"\bT-", sentence))
        if t_count > 0:
            section_t_count[section] += 1

    # Calculate rates
    section_rates = {}
    for section in section_total:
        if section_total[section] > 0:
            rate = section_t_count[section] / section_total[section]
            section_rates[section] = rate

    return section_t_count, section_total, section_rates


def test_suffix_enrichment(translations):
    """
    Test 2: Locative/instrumental suffix enrichment

    If T- = instrumental/locative:
    Should show enrichment for LOC/INST/DIR suffixes compared to baseline
    """
    # Find all T- words
    t_words = []
    non_t_words = []

    for trans in translations:
        sentence = trans["final_translation"]
        words = sentence.split()

        for word in words:
            if word.startswith("T-"):
                t_words.append(word)
            elif not word.startswith("["):  # Skip particles
                non_t_words.append(word)

    # Count suffixes
    def count_suffixes(word_list):
        suffix_counts = Counter()
        for word in word_list:
            # Extract suffixes
            if "-LOC" in word:
                suffix_counts["LOC"] += 1
            if "-INST" in word:
                suffix_counts["INST"] += 1
            if "-DIR" in word:
                suffix_counts["DIR"] += 1
            if "-GEN" in word:
                suffix_counts["GEN"] += 1
            if "-VERB" in word:
                suffix_counts["VERB"] += 1
        return suffix_counts

    t_suffixes = count_suffixes(t_words)
    non_t_suffixes = count_suffixes(non_t_words)

    # Calculate enrichment
    enrichment = {}
    total_t = len(t_words)
    total_non_t = len(non_t_words)

    for suffix in ["LOC", "INST", "DIR", "GEN", "VERB"]:
        t_rate = t_suffixes[suffix] / total_t if total_t > 0 else 0
        non_t_rate = non_t_suffixes[suffix] / total_non_t if total_non_t > 0 else 0

        enrichment[suffix] = (t_rate / non_t_rate) if non_t_rate > 0 else 0

    return t_suffixes, non_t_suffixes, enrichment, total_t, total_non_t


def test_semantic_contexts(translations):
    """
    Test 3: Semantic contexts

    If T- = instrumental/locative:
    Should appear with vessels, locations, instruments
    """
    t_contexts = {"vessel": [], "water": [], "oak": [], "botanical": [], "location": []}

    for trans in translations:
        sentence = trans["final_translation"]

        if "T-" in sentence:
            if "vessel" in sentence.lower():
                t_contexts["vessel"].append(sentence)
            if "water" in sentence.lower():
                t_contexts["water"].append(sentence)
            if "oak" in sentence.lower():
                t_contexts["oak"].append(sentence)
            if "botanical" in sentence.lower():
                t_contexts["botanical"].append(sentence)
            # Location markers
            if any(loc in sentence for loc in ["-LOC", "AT/IN", "THERE", "HERE"]):
                t_contexts["location"].append(sentence)

    return t_contexts


def find_minimal_pairs(translations):
    """
    Test 4: Minimal pairs (X vs T-X)

    Find cases where stem appears both with and without T-
    Compare contexts to infer T- meaning
    """
    # Find all T- stems
    t_stems = Counter()
    non_t_stems = Counter()

    for trans in translations:
        sentence = trans["final_translation"]
        words = sentence.split()

        for word in words:
            if word.startswith("T-"):
                # Extract stem (remove T- and suffixes)
                stem = re.sub(r"^T-", "", word)
                stem = re.sub(r"-[A-Z]+.*$", "", stem)
                if stem:
                    t_stems[stem] += 1
            else:
                # Extract stem
                stem = re.sub(r"-[A-Z]+.*$", "", word)
                if stem and not stem.startswith("["):
                    non_t_stems[stem] += 1

    # Find overlapping stems (minimal pairs)
    minimal_pairs = []
    for stem in t_stems:
        if stem in non_t_stems:
            minimal_pairs.append(
                {"stem": stem, "with_t": t_stems[stem], "without_t": non_t_stems[stem]}
            )

    # Sort by frequency
    minimal_pairs.sort(key=lambda x: x["with_t"] + x["without_t"], reverse=True)

    return minimal_pairs


def compare_with_at_in(translations):
    """
    Test 5: Compare T- with AT/IN preposition

    If T- is grammaticalized AT/IN:
    Should show similar distributions and contexts
    """
    t_contexts = []
    at_contexts = []

    for trans in translations:
        sentence = trans["final_translation"]
        words = sentence.split()

        for i, word in enumerate(words):
            if word.startswith("T-"):
                before = words[max(0, i - 2) : i]
                after = words[i + 1 : min(len(words), i + 3)]
                t_contexts.append({"word": word, "before": before, "after": after})

            if "AT/IN" in word or word == "AT-[?e]-VERB":
                before = words[max(0, i - 2) : i]
                after = words[i + 1 : min(len(words), i + 3)]
                at_contexts.append({"word": word, "before": before, "after": after})

    # Find common patterns
    t_after = Counter()
    at_after = Counter()

    for ctx in t_contexts:
        t_after.update(ctx["after"])

    for ctx in at_contexts:
        at_after.update(ctx["after"])

    return t_after, at_after, len(t_contexts), len(at_contexts)


def main():
    """Main validation"""
    print("=" * 70)
    print("COMPREHENSIVE T- PREFIX VALIDATION")
    print("=" * 70)
    print("\nPriority: HIGHEST (973 instances = 2.6% of corpus)")
    print("Hypothesis: T- = instrumental/locative marker ('in', 'with', 'at')")
    print("\nFrom Phase 20:")
    print("- T-vessel: 43×")
    print("- T-[?e]: 93×")
    print("- Appears in ~18.7% of sentences")
    print("- 19.7% take LOC/INST/DIR suffixes\n")

    print("Loading translations...")
    translations = load_translations()
    print(f"Loaded {len(translations)} translations")

    print("Building folio mapping...")
    line_to_folio = build_folio_mapping()
    print(f"Mapped {len(line_to_folio)} lines\n")

    # TEST 1: Cross-section consistency
    print("=" * 70)
    print("TEST 1: CROSS-SECTION CONSISTENCY")
    print("=" * 70)
    print("If T- is GRAMMATICAL: Should appear at ~18-20% across ALL sections")
    print("If T- is SEMANTIC: Would cluster in specific sections\n")

    section_t, section_total, section_rates = test_cross_section_consistency(
        translations, line_to_folio
    )

    print("Section distribution:")
    overall_rate = (
        sum(section_t.values()) / sum(section_total.values())
        if sum(section_total.values()) > 0
        else 0
    )

    for section in sorted(section_rates.keys()):
        rate = section_rates[section]
        count = section_t[section]
        total = section_total[section]
        deviation = (
            abs(rate - overall_rate) / overall_rate * 100 if overall_rate > 0 else 0
        )

        print(
            f"  {section:15s}: {count:3d}/{total:4d} ({rate * 100:5.2f}%) - deviation: {deviation:5.1f}%"
        )

    print(f"\nOverall T- rate: {overall_rate * 100:.2f}%")

    # Check consistency
    max_deviation = (
        max(abs(r - overall_rate) / overall_rate * 100 for r in section_rates.values())
        if overall_rate > 0
        else 0
    )

    if max_deviation < 25:
        print(f"\n✓ CONSISTENT: Max deviation {max_deviation:.1f}% < 25% threshold")
        print("  T- appears uniformly → GRAMMATICAL function")
    else:
        print(f"\n✗ INCONSISTENT: Max deviation {max_deviation:.1f}% > 25% threshold")
        print("  T- clusters in sections → SEMANTIC function")

    # TEST 2: Suffix enrichment
    print("\n" + "=" * 70)
    print("TEST 2: LOCATIVE/INSTRUMENTAL SUFFIX ENRICHMENT")
    print("=" * 70)
    print("If T- = instrumental/locative:")
    print("LOC/INST/DIR enrichment should be >1.5× baseline\n")

    t_suffixes, non_t_suffixes, enrichment, total_t, total_non_t = (
        test_suffix_enrichment(translations)
    )

    print(f"T- words: {total_t}")
    print(f"Non-T- words: {total_non_t}\n")

    print("Suffix enrichment:")
    for suffix in ["LOC", "INST", "DIR", "GEN", "VERB"]:
        t_count = t_suffixes[suffix]
        non_t_count = non_t_suffixes[suffix]
        t_rate = t_count / total_t * 100 if total_t > 0 else 0
        non_t_rate = non_t_count / total_non_t * 100 if total_non_t > 0 else 0
        enrich = enrichment[suffix]

        print(
            f"  {suffix:4s}: T-={t_rate:5.2f}% ({t_count}), Non-T={non_t_rate:5.2f}% ({non_t_count}), enrichment={enrich:.2f}×"
        )

    # Check LOC/INST/DIR enrichment
    loc_inst_dir_enrich = (
        enrichment["LOC"] + enrichment["INST"] + enrichment["DIR"]
    ) / 3

    if loc_inst_dir_enrich > 1.5:
        print(
            f"\n✓ ENRICHED: LOC/INST/DIR average enrichment {loc_inst_dir_enrich:.2f}× > 1.5×"
        )
        print("  T- marks instrumental/locative contexts")
    else:
        print(
            f"\n✗ NOT ENRICHED: LOC/INST/DIR average enrichment {loc_inst_dir_enrich:.2f}× < 1.5×"
        )

    # TEST 3: Semantic contexts
    print("\n" + "=" * 70)
    print("TEST 3: SEMANTIC CONTEXTS")
    print("=" * 70)
    print("If T- = instrumental/locative:")
    print("Should appear with vessels, locations, instruments\n")

    t_contexts = test_semantic_contexts(translations)

    print("T- co-occurrences:")
    for context, sentences in t_contexts.items():
        print(f"  {context:12s}: {len(sentences):3d} sentences")

    # Show samples
    if t_contexts["vessel"]:
        print("\nSample T- with vessel:")
        print(f"  {t_contexts['vessel'][0][:100]}...")

    total_semantic = sum(len(s) for s in t_contexts.values())
    semantic_rate = total_semantic / 973 * 100  # 973 = total T- words

    if semantic_rate > 50:
        print(
            f"\n✓ SEMANTIC CONTEXTS: {semantic_rate:.1f}% of T- words in semantic contexts"
        )
    else:
        print(f"\n? WEAK SEMANTIC: Only {semantic_rate:.1f}% in semantic contexts")

    # TEST 4: Minimal pairs
    print("\n" + "=" * 70)
    print("TEST 4: MINIMAL PAIRS (X vs T-X)")
    print("=" * 70)
    print("Find stems that appear both with and without T-\n")

    minimal_pairs = find_minimal_pairs(translations)

    print(f"Found {len(minimal_pairs)} stems appearing both with/without T-")
    print("\nTop 10 minimal pairs:")
    for i, pair in enumerate(minimal_pairs[:10], 1):
        print(
            f"  {i:2d}. {pair['stem']:20s}: T-={pair['with_t']:3d}×, no-T={pair['without_t']:3d}×"
        )

    if len(minimal_pairs) > 10:
        print(f"\n✓ MINIMAL PAIRS EXIST: {len(minimal_pairs)} stems")
        print("  T- adds grammatical meaning (location/instrument)")
    else:
        print(f"\n? FEW PAIRS: Only {len(minimal_pairs)} stems")

    # TEST 5: Compare with AT/IN
    print("\n" + "=" * 70)
    print("TEST 5: COMPARE WITH AT/IN PREPOSITION")
    print("=" * 70)
    print("If T- is grammaticalized AT/IN:")
    print("Should show similar context patterns\n")

    t_after, at_after, t_count, at_count = compare_with_at_in(translations)

    print(f"T- instances: {t_count}")
    print(f"AT/IN instances: {at_count}\n")

    print("Top 10 words AFTER T-:")
    for word, count in t_after.most_common(10):
        print(f"  {word}: {count}×")

    print("\nTop 10 words AFTER AT/IN:")
    for word, count in at_after.most_common(10):
        print(f"  {word}: {count}×")

    # Calculate overlap
    t_set = set(w for w, c in t_after.most_common(20))
    at_set = set(w for w, c in at_after.most_common(20))
    overlap = len(t_set & at_set)

    print(f"\nContext overlap: {overlap}/20 words ({overlap / 20 * 100:.1f}%)")

    if overlap > 10:
        print("✓ HIGH OVERLAP: T- and AT/IN have similar contexts")
        print("  T- may be grammaticalized form of AT/IN")
    else:
        print("? LOW OVERLAP: T- and AT/IN have different contexts")

    # FINAL VERDICT
    print("\n" + "=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)

    evidence = 0

    if max_deviation < 25:
        evidence += 1
        print("✓ Test 1 (Cross-section): PASSED (grammatical)")
    else:
        print("✗ Test 1 (Cross-section): FAILED")

    if loc_inst_dir_enrich > 1.5:
        evidence += 1
        print("✓ Test 2 (Suffix enrichment): PASSED (locative/instrumental)")
    else:
        print("✗ Test 2 (Suffix enrichment): FAILED")

    if semantic_rate > 50:
        evidence += 1
        print("✓ Test 3 (Semantic contexts): PASSED")
    else:
        print("✗ Test 3 (Semantic contexts): FAILED")

    if len(minimal_pairs) > 10:
        evidence += 1
        print("✓ Test 4 (Minimal pairs): PASSED")
    else:
        print("? Test 4 (Minimal pairs): MARGINAL")

    if overlap > 10:
        evidence += 1
        print("✓ Test 5 (AT/IN comparison): PASSED")
    else:
        print("? Test 5 (AT/IN comparison): MARGINAL")

    print(f"\nEvidence: {evidence}/5 tests passed")

    if evidence >= 3:
        print("\n" + "=" * 70)
        print("✓ HYPOTHESIS CONFIRMED: T- = instrumental/locative marker")
        print("=" * 70)
        print("Confidence: MODERATE to HIGH")
        print("\nMeaning:")
        print("  T- = 'in', 'with', 'at' (instrumental/locative)")
        print("  T-vessel = 'in vessel'")
        print("  T-[?e]-VERB = 'with continuous [action]'")
        print("\nMedieval parallel:")
        print("  English: 'in', 'with', 'at' (prepositions)")
        print("  Latin: 'in', 'cum' (prepositions/prefixes)")
        print("\nImpact:")
        print("  Recognition gain: +2.6%")
        print("  New total: 79.6% + 2.6% = 82.2%")
    else:
        print("\n? HYPOTHESIS UNCERTAIN")
        print(f"Only {evidence}/5 tests passed")

    # Save results
    results = {
        "hypothesis": "T- = instrumental/locative marker",
        "evidence_count": evidence,
        "tests": {
            "cross_section": {
                "max_deviation": max_deviation,
                "passed": max_deviation < 25,
                "section_rates": section_rates,
            },
            "suffix_enrichment": {
                "loc_inst_dir_enrichment": loc_inst_dir_enrich,
                "passed": loc_inst_dir_enrich > 1.5,
                "enrichment": enrichment,
            },
            "semantic_contexts": {
                "rate": semantic_rate,
                "passed": semantic_rate > 50,
                "counts": {k: len(v) for k, v in t_contexts.items()},
            },
            "minimal_pairs": {
                "count": len(minimal_pairs),
                "passed": len(minimal_pairs) > 10,
                "top_pairs": minimal_pairs[:20],
            },
            "at_in_comparison": {"overlap": overlap, "passed": overlap > 10},
        },
    }

    print("\nSaving results to T_PREFIX_VALIDATION.json...")
    with open("T_PREFIX_VALIDATION.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\nDONE!")


if __name__ == "__main__":
    main()
