"""
Phase 5A: Validate Remaining High-Frequency Function Words

Based on breakthrough finding that AMBIGUOUS scores (4-5/8) = function words,
now test the remaining high-frequency words from blocked sentences:

- ol (very high frequency)
- or (very high frequency)
- aiin (suffix appearing frequently)
- iin (suffix appearing frequently)
- ldaiin (compound form in sentence 2)
- dyty (sentence 5 blocker)

Hypothesis: These are additional grammatical morphemes completing the function word system
"""

import re
from collections import defaultdict, Counter


def load_voynich_text(filepath):
    """Load and parse Voynich manuscript"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    all_words = []
    line_breaks = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("<"):
            continue

        words = re.findall(r"[a-z!]+", line.lower())
        line_breaks.append(len(all_words))
        all_words.extend(words)

    return all_words, line_breaks


def analyze_morpheme(morpheme, all_words, line_breaks):
    """Analyze a morpheme (can be word or suffix)"""

    print(f"\n{'=' * 70}")
    print(f"ANALYZING: {morpheme}")
    print(f"{'=' * 70}")

    # Find all instances
    standalone = 0
    as_prefix = 0
    as_suffix = 0
    as_infix = 0
    instances = []

    for word in all_words:
        if morpheme == word:
            standalone += 1
            instances.append(word)
        elif word.startswith(morpheme) and len(word) > len(morpheme):
            as_prefix += 1
            if len(instances) < 30:
                instances.append(word)
        elif word.endswith(morpheme) and len(word) > len(morpheme):
            as_suffix += 1
            if len(instances) < 30:
                instances.append(word)
        elif (
            morpheme in word
            and not word.startswith(morpheme)
            and not word.endswith(morpheme)
        ):
            as_infix += 1
            if len(instances) < 30:
                instances.append(word)

    total = standalone + as_prefix + as_suffix + as_infix

    if total == 0:
        print("NOT FOUND in corpus")
        return None

    print(f"\n1. DISTRIBUTION:")
    print(f"   Standalone: {standalone} ({standalone / total * 100:.1f}%)")
    print(f"   As prefix: {as_prefix} ({as_prefix / total * 100:.1f}%)")
    print(f"   As suffix: {as_suffix} ({as_suffix / total * 100:.1f}%)")
    print(f"   As infix: {as_infix} ({as_infix / total * 100:.1f}%)")
    print(
        f"   TOTAL: {total} instances ({total / len(all_words) * 100:.2f}% of manuscript)"
    )

    # Sample instances
    print(f"\n2. SAMPLE INSTANCES (first 20):")
    for i, inst in enumerate(instances[:20]):
        print(f"   {inst}", end="  ")
        if (i + 1) % 5 == 0:
            print()
    print()

    # Immediate context for standalone forms
    if standalone > 0:
        before = Counter()
        after = Counter()
        positions = {"line_initial": 0, "line_final": 0, "mid_line": 0}

        line_starts = set(line_breaks)
        line_ends = set([pos - 1 for pos in line_breaks[1:]] + [len(all_words) - 1])

        for i, word in enumerate(all_words):
            if word == morpheme:
                # Position
                if i in line_starts:
                    positions["line_initial"] += 1
                elif i in line_ends:
                    positions["line_final"] += 1
                else:
                    positions["mid_line"] += 1

                # Context
                if i > 0:
                    before[all_words[i - 1]] += 1
                if i < len(all_words) - 1:
                    after[all_words[i + 1]] += 1

        print(f"\n3. POSITIONAL DISTRIBUTION (standalone only):")
        for pos_type, count in positions.items():
            pct = count / standalone * 100 if standalone > 0 else 0
            print(f"   {pos_type:15}: {count:4} ({pct:.1f}%)")

        print(f"\n4. IMMEDIATE CONTEXT (standalone, top 10):")
        print(f"   Before: {', '.join(f'{w}({c})' for w, c in before.most_common(10))}")
        print(f"   After: {', '.join(f'{w}({c})' for w, c in after.most_common(10))}")

    # Morphological analysis
    print(f"\n5. MORPHOLOGICAL BEHAVIOR:")

    free_morpheme = standalone / total > 0.3 if total > 0 else False
    bound_morpheme = (as_suffix + as_prefix) / total > 0.7 if total > 0 else False

    if free_morpheme:
        print(f"   ✓ FREE MORPHEME (>30% standalone)")
    if bound_morpheme:
        print(f"   ✓ BOUND MORPHEME (>70% attached)")

    if as_suffix > as_prefix * 2:
        print(f"   ✓ SUFFIX (appears word-finally)")
    elif as_prefix > as_suffix * 2:
        print(f"   ✓ PREFIX (appears word-initially)")
    else:
        print(f"   ≈ MIXED (no clear affix position)")

    # Frequency assessment
    freq_pct = total / len(all_words) * 100
    if freq_pct > 1.0:
        print(f"   ✓✓ VERY HIGH FREQUENCY (>{freq_pct:.2f}% of manuscript)")
    elif freq_pct > 0.5:
        print(f"   ✓ HIGH FREQUENCY ({freq_pct:.2f}% of manuscript)")

    # Function word indicators
    print(f"\n6. FUNCTION WORD INDICATORS:")
    indicators = []

    if freq_pct > 0.5:
        indicators.append("High frequency (typical of function words)")

    if free_morpheme and standalone > 100:
        indicators.append("Frequently standalone (not just bound)")

    if len(instances[0]) <= 3:  # Short
        indicators.append("Short form (typical of grammatical morphemes)")

    if indicators:
        for ind in indicators:
            print(f"   ✓ {ind}")
    else:
        print(f"   ✗ No strong function word indicators")

    # Assessment
    print(f"\n7. PRELIMINARY ASSESSMENT:")

    if freq_pct > 1.0 and free_morpheme:
        assessment = "LIKELY FUNCTION WORD (high frequency + free morpheme)"
    elif freq_pct > 0.5 and bound_morpheme:
        assessment = "LIKELY GRAMMATICAL SUFFIX (high frequency + bound)"
    elif freq_pct > 0.3:
        assessment = "POSSIBLE FUNCTION WORD/MORPHEME (moderate frequency)"
    else:
        assessment = "LIKELY CONTENT WORD (low frequency)"

    print(f"   {assessment}")

    return {
        "morpheme": morpheme,
        "total": total,
        "standalone": standalone,
        "as_prefix": as_prefix,
        "as_suffix": as_suffix,
        "as_infix": as_infix,
        "frequency_pct": freq_pct,
        "assessment": assessment,
        "sample_instances": instances[:20],
    }


def main():
    print("Phase 5A: Remaining High-Frequency Function Word Analysis")
    print("=" * 70)

    filepath = "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/voynich_eva_takahashi.txt"
    all_words, line_breaks = load_voynich_text(filepath)

    print(f"Loaded {len(all_words)} words from manuscript")

    # Target morphemes
    targets = [
        "ol",  # Very high frequency, appears in multiple sentences
        "or",  # Very high frequency, case marker candidate
        "aiin",  # Suffix appearing frequently
        "iin",  # Suffix appearing frequently
        "dy",  # Verbal suffix candidate
        "ain",  # Another common suffix
        "ar",  # Known case marker (directional)
        "al",  # Known case marker (locative)
    ]

    results = {}

    for morpheme in targets:
        result = analyze_morpheme(morpheme, all_words, line_breaks)
        if result:
            results[morpheme] = result

    # Summary
    print(f"\n\n{'=' * 70}")
    print("SUMMARY: High-Frequency Morpheme Classification")
    print(f"{'=' * 70}")

    print(f"\n{'Morpheme':<10} {'Total':<8} {'Freq%':<8} {'Free%':<8} Assessment")
    print("-" * 70)

    for morpheme, data in results.items():
        free_pct = data["standalone"] / data["total"] * 100 if data["total"] > 0 else 0
        print(
            f"{morpheme:<10} {data['total']:<8} {data['frequency_pct']:<8.2f} {free_pct:<8.1f} {data['assessment']}"
        )

    # Function word candidates
    print(f"\n{'=' * 70}")
    print("FUNCTION WORD CANDIDATES (frequency >0.5% + >30% standalone):")
    print(f"{'=' * 70}")

    function_candidates = []
    for morpheme, data in results.items():
        free_pct = data["standalone"] / data["total"] * 100 if data["total"] > 0 else 0
        if data["frequency_pct"] > 0.5 and free_pct > 30:
            function_candidates.append(morpheme)
            print(
                f"  • {morpheme} - {data['total']} instances, {data['frequency_pct']:.2f}% of manuscript"
            )

    # Grammatical suffix candidates
    print(f"\n{'=' * 70}")
    print("GRAMMATICAL SUFFIX CANDIDATES (frequency >0.5% + >70% bound):")
    print(f"{'=' * 70}")

    suffix_candidates = []
    for morpheme, data in results.items():
        bound_pct = (
            (data["as_suffix"] + data["as_prefix"]) / data["total"] * 100
            if data["total"] > 0
            else 0
        )
        if data["frequency_pct"] > 0.5 and bound_pct > 70:
            suffix_candidates.append(morpheme)
            print(f"  • {morpheme} - {data['total']} instances, {bound_pct:.1f}% bound")

    print(f"\n{'=' * 70}")
    print("NEXT STEPS:")
    print(f"{'=' * 70}")
    print("1. Investigate function word candidates for syntactic role")
    print("2. Test grammatical suffixes for morphological function")
    print("3. Re-translate test sentences with expanded function word inventory")


if __name__ == "__main__":
    main()
