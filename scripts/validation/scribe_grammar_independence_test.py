#!/usr/bin/env python3
"""
Scribe-Grammar Independence Test

This script tests whether the agglutinative grammar patterns remain consistent
across different scribes/linguistic groups (Currier A vs B). If the grammar is
truly linguistic (not artifacts of individual scribal habits), we expect:

1. Similar suffix attachment rates across both languages
2. Similar morphological productivity patterns
3. Consistent word structure (standalone vs bound)
4. Similar positional distributions for validated terms

This provides INDEPENDENT validation that the grammar is real linguistic structure,
not just patterns specific to one scribe's writing habits.
"""

import re
from collections import defaultdict, Counter

# Phase 9 validated vocabulary (28 terms)
VALIDATED_SUFFIXES = {
    "-dy": "VERBAL",
    "-al": "LOCATIVE",
    "-ol": "LOCATIVE",
    "-ar": "DIRECTIONAL",
    "-or": "INSTRUMENTAL",
    "-ain": "DEFINITENESS",
    "-iin": "DEFINITENESS",
    "-aiin": "DEFINITENESS",
}

GENITIVE_PREFIXES = ["qok", "qot"]

VALIDATED_ROOTS = [
    "okal",
    "or",
    "dol",
    "dar",
    "chol",
    "sho",
    "shedy",
    "daiin",
    "dair",
    "air",
    "teo",
    "keo",
    "sal",
    "qol",
]

VALIDATED_FUNCTION_WORDS = [
    "ar",
    "ory",
    "sal",
    "qol",
    "chey",
    "cheey",
    "chy",
    "shy",
    "am",
    "dam",
    "cthy",
]


def load_voynich_with_currier(eva_filepath, currier_filepath):
    """
    Load Voynich data with Currier A/B classifications.

    Returns:
        dict: {'A': [...], 'B': [...]} with word context data for each language
    """
    # First load Currier classifications
    currier_map = {}
    with open(currier_filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or line.startswith("Folio"):
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 2:
                folio, language = parts[0], parts[1]
                currier_map[folio] = language

    # Now load EVA data grouped by Currier language
    data = {"A": [], "B": []}
    current_folio = None
    current_language = None

    with open(eva_filepath, "r", encoding="utf-8") as f:
        for line in f:
            line_stripped = line.strip()

            # Skip comments and metadata
            if line_stripped.startswith("#") or not line_stripped:
                continue

            # Extract folio
            folio_match = re.match(r"<f(\d+[rv])>", line_stripped)
            if folio_match:
                current_folio = f"f{folio_match.group(1)}"
                current_language = currier_map.get(current_folio)
                continue

            # Parse text line
            if current_folio and current_language and line_stripped.startswith("<"):
                # Extract words from line
                text_match = re.search(r">\s+(.+)$", line_stripped)
                if text_match:
                    text = text_match.group(1)
                    # Clean text
                    text = re.sub(r"<[^>]+>", "", text)  # Remove tags
                    text = re.sub(r"\[.*?\]", "", text)  # Remove uncertain readings
                    text = re.sub(
                        r"[{}!@#\$%^&*()<>]", "", text
                    )  # Remove special chars
                    text = re.sub(
                        r"[.,;:\-]", " ", text
                    )  # Replace punctuation with space

                    words = text.split()
                    for i, word in enumerate(words):
                        if word and len(word) >= 2:
                            position = (
                                "initial"
                                if i == 0
                                else ("final" if i == len(words) - 1 else "medial")
                            )
                            data[current_language].append(
                                {
                                    "word": word,
                                    "folio": current_folio,
                                    "position": position,
                                }
                            )

    return data


def analyze_suffix_attachment_rate(words, language_name):
    """
    Measure what percentage of words have validated suffixes attached.
    """
    total_words = len(words)
    words_with_suffix = 0
    suffix_counts = Counter()

    for item in words:
        word = item["word"]
        for suffix in VALIDATED_SUFFIXES:
            if word.endswith(suffix):
                words_with_suffix += 1
                suffix_counts[suffix] += 1
                break  # Count each word only once

    attachment_rate = 100 * words_with_suffix / total_words if total_words > 0 else 0

    print(f"\n{language_name} - Suffix Attachment Analysis:")
    print(f"  Total words: {total_words}")
    print(f"  Words with validated suffix: {words_with_suffix}")
    print(f"  Attachment rate: {attachment_rate:.1f}%")
    print(f"  Most common suffixes:")
    for suffix, count in suffix_counts.most_common(5):
        pct = 100 * count / total_words
        print(f"    {suffix}: {count} ({pct:.1f}%)")

    return attachment_rate


def analyze_morphological_productivity(words, language_name):
    """
    For each validated root, measure what % appears in compound forms.
    """
    root_stats = {}

    for root in VALIDATED_ROOTS:
        standalone_count = 0
        compound_count = 0

        for item in words:
            word = item["word"]
            if word == root:
                standalone_count += 1
            elif root in word and word != root:
                compound_count += 1

        total = standalone_count + compound_count
        if total >= 5:  # Only report roots with sufficient data
            productivity = 100 * compound_count / total if total > 0 else 0
            root_stats[root] = {
                "standalone": standalone_count,
                "compound": compound_count,
                "total": total,
                "productivity": productivity,
            }

    if root_stats:
        print(f"\n{language_name} - Morphological Productivity (top roots):")
        sorted_roots = sorted(
            root_stats.items(), key=lambda x: x[1]["total"], reverse=True
        )
        for root, stats in sorted_roots[:8]:
            print(
                f"  {root}: {stats['productivity']:.1f}% productive ({stats['compound']}/{stats['total']} compounds)"
            )

        avg_productivity = sum(s["productivity"] for s in root_stats.values()) / len(
            root_stats
        )
        return avg_productivity
    else:
        return 0


def analyze_function_word_distribution(words, language_name):
    """
    Analyze position distribution of validated function words.
    """
    function_word_positions = defaultdict(
        lambda: {"initial": 0, "medial": 0, "final": 0}
    )

    for item in words:
        word = item["word"]
        if word in VALIDATED_FUNCTION_WORDS:
            function_word_positions[word][item["position"]] += 1

    print(f"\n{language_name} - Function Word Position Distribution:")
    for fw in ["ar", "ory", "sal", "chey", "am", "dam"]:
        if fw in function_word_positions:
            stats = function_word_positions[fw]
            total = sum(stats.values())
            if total >= 5:
                initial_pct = 100 * stats["initial"] / total
                medial_pct = 100 * stats["medial"] / total
                final_pct = 100 * stats["final"] / total
                print(
                    f"  {fw}: I={initial_pct:.0f}% M={medial_pct:.0f}% F={final_pct:.0f}% (n={total})"
                )


def analyze_genitive_prefix_usage(words, language_name):
    """
    Measure usage of genitive prefix qok-/qot-.
    """
    total_words = len(words)
    genitive_count = 0

    for item in words:
        word = item["word"]
        for prefix in GENITIVE_PREFIXES:
            if word.startswith(prefix):
                genitive_count += 1
                break

    genitive_rate = 100 * genitive_count / total_words if total_words > 0 else 0
    print(f"\n{language_name} - Genitive Prefix Usage:")
    print(f"  Words with qok-/qot-: {genitive_count} ({genitive_rate:.2f}%)")

    return genitive_rate


def compare_languages(data_a, data_b):
    """
    Compare grammar consistency between Currier A and B.
    """
    print("\n" + "=" * 70)
    print("SCRIBE-GRAMMAR INDEPENDENCE TEST")
    print("Testing whether grammar is consistent across Currier A vs B")
    print("=" * 70)

    print(f"\nDataset sizes:")
    print(f"  Currier A: {len(data_a)} words")
    print(f"  Currier B: {len(data_b)} words")

    # Test 1: Suffix attachment rates
    print("\n" + "-" * 70)
    print("TEST 1: SUFFIX ATTACHMENT CONSISTENCY")
    print("-" * 70)
    rate_a = analyze_suffix_attachment_rate(data_a, "Currier A")
    rate_b = analyze_suffix_attachment_rate(data_b, "Currier B")
    diff_suffix = abs(rate_a - rate_b)
    print(f"\n  → Difference: {diff_suffix:.1f} percentage points")
    print(
        f"  → Result: {'CONSISTENT' if diff_suffix < 5 else 'INCONSISTENT'} (threshold: 5%)"
    )

    # Test 2: Morphological productivity
    print("\n" + "-" * 70)
    print("TEST 2: MORPHOLOGICAL PRODUCTIVITY CONSISTENCY")
    print("-" * 70)
    prod_a = analyze_morphological_productivity(data_a, "Currier A")
    prod_b = analyze_morphological_productivity(data_b, "Currier B")
    diff_prod = abs(prod_a - prod_b)
    print(f"\n  Average productivity - Currier A: {prod_a:.1f}%")
    print(f"  Average productivity - Currier B: {prod_b:.1f}%")
    print(f"  → Difference: {diff_prod:.1f} percentage points")
    print(
        f"  → Result: {'CONSISTENT' if diff_prod < 10 else 'INCONSISTENT'} (threshold: 10%)"
    )

    # Test 3: Function word position
    print("\n" + "-" * 70)
    print("TEST 3: FUNCTION WORD POSITION CONSISTENCY")
    print("-" * 70)
    analyze_function_word_distribution(data_a, "Currier A")
    analyze_function_word_distribution(data_b, "Currier B")
    print(f"\n  → Qualitative assessment: Check if patterns match")

    # Test 4: Genitive usage
    print("\n" + "-" * 70)
    print("TEST 4: GENITIVE PREFIX CONSISTENCY")
    print("-" * 70)
    gen_a = analyze_genitive_prefix_usage(data_a, "Currier A")
    gen_b = analyze_genitive_prefix_usage(data_b, "Currier B")
    diff_gen = abs(gen_a - gen_b)
    print(f"\n  → Difference: {diff_gen:.2f} percentage points")
    print(
        f"  → Result: {'CONSISTENT' if diff_gen < 1 else 'INCONSISTENT'} (threshold: 1%)"
    )

    # Overall assessment
    print("\n" + "=" * 70)
    print("OVERALL ASSESSMENT")
    print("=" * 70)

    tests_passed = 0
    if diff_suffix < 5:
        tests_passed += 1
    if diff_prod < 10:
        tests_passed += 1
    if diff_gen < 1:
        tests_passed += 1

    print(f"\nQuantitative tests passed: {tests_passed}/3")

    if tests_passed >= 2:
        print("\n✓ CONCLUSION: Grammar shows strong consistency across Currier A and B")
        print("  This validates that the identified grammatical patterns are NOT")
        print("  artifacts of individual scribal habits, but represent genuine")
        print("  linguistic structure that transcends scribal hands.")
        print(
            "\n  RECOMMENDATION: Include this as independent validation in grammar paper."
        )
    else:
        print("\n✗ CONCLUSION: Grammar shows inconsistency between Currier A and B")
        print("  Further investigation needed to understand dialect differences.")

    return tests_passed >= 2


def main():
    eva_filepath = "data/voynich/eva_transcription/ZL3b-n.txt"
    currier_filepath = "data/voynich/currier_classifications.txt"

    # Load data
    print("Loading Voynich data with Currier A/B classifications...")
    data = load_voynich_with_currier(eva_filepath, currier_filepath)

    # Run comparison
    result = compare_languages(data["A"], data["B"])

    # Save detailed results
    output_file = "SCRIBE_GRAMMAR_INDEPENDENCE_RESULTS.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Scribe-Grammar Independence Test Results\n\n")
        f.write("## Test Purpose\n\n")
        f.write(
            "This test validates whether the identified agglutinative grammar patterns\n"
        )
        f.write(
            "remain consistent across different scribal hands (Currier A vs B). If the\n"
        )
        f.write(
            "grammar is truly linguistic rather than artifacts of scribal habits, we\n"
        )
        f.write("expect similar patterns in both language groups.\n\n")
        f.write("## Methodology\n\n")
        f.write(
            "We compared four grammatical metrics across Currier A (101 folios, ~"
            + str(len(data["A"]))
            + " words)\n"
        )
        f.write("and Currier B (68 folios, ~" + str(len(data["B"])) + " words):\n\n")
        f.write("1. **Suffix Attachment Rate**: % of words with validated suffixes\n")
        f.write(
            "2. **Morphological Productivity**: % of root appearances in compounds\n"
        )
        f.write(
            "3. **Function Word Position**: Position distribution (initial/medial/final)\n"
        )
        f.write("4. **Genitive Prefix Usage**: % of words with qok-/qot- prefix\n\n")
        f.write("## Results\n\n")
        f.write(f"Test passed: {'YES' if result else 'NO'}\n\n")
        f.write("See console output for detailed statistics.\n\n")
        f.write("## Implications\n\n")
        if result:
            f.write(
                "The grammar shows strong consistency across both Currier languages,\n"
            )
            f.write(
                "providing independent validation that the identified patterns represent\n"
            )
            f.write("genuine linguistic structure rather than scribal artifacts.\n")
        else:
            f.write(
                "The grammar shows some inconsistency, suggesting possible dialect\n"
            )
            f.write(
                "differences between Currier A and B, or that some patterns may be\n"
            )
            f.write("scribe-specific rather than linguistic.\n")

    print(f"\n\nDetailed results saved to: {output_file}")


if __name__ == "__main__":
    main()
