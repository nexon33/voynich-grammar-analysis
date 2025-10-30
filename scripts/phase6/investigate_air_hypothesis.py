#!/usr/bin/env python3
"""
Investigate AIR as Proximal Spatial Particle: "here / at this place"
====================================================================

Hypothesis: "air" = proximal spatial particle meaning "here" (complement to "dair" = "there")

Evidence to check:
1. Morphological behavior (should be LOW like "dair")
2. Co-occurrence with "dair" (already know: 100%)
3. Frequency ratio (proximal terms typically more common)
4. Section distribution
5. Position patterns
6. Contextual usage

Author: Voynich Research Team
Date: 2025-10-29
"""

import re
from collections import Counter, defaultdict


def load_voynich_with_context(filepath):
    """Load Voynich text with full sentence context and section tracking"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    words_with_context = []
    current_section = "unknown"

    for line in lines:
        line_stripped = line.strip()

        # Track sections from comments
        if "# herbal" in line_stripped.lower():
            current_section = "herbal"
        elif "# astronomical" in line_stripped.lower():
            current_section = "astronomical"
        elif "# biological" in line_stripped.lower():
            current_section = "biological"
        elif "# pharmaceutical" in line_stripped.lower():
            current_section = "pharmaceutical"
        elif "# recipes" in line_stripped.lower():
            current_section = "recipes"

        # Parse actual text lines
        if line_stripped.startswith("<f"):
            # Extract locator and text
            match = re.search(r"(<f\d+[rv]\d*\.[^>]+>)\s+(.+)$", line_stripped)
            if match:
                locator = match.group(1)
                text = match.group(2)

                # Clean text
                text = re.sub(r"<[^>]+>", "", text)  # Remove tags
                text = re.sub(r"\{[^}]+\}", "", text)  # Remove curly braces
                text = re.sub(r"\[[^\]]+\]", "", text)  # Remove square brackets
                text = re.sub(r"[@!]\d+;", "", text)  # Remove special markers
                text = re.sub(r"[.,;:!?<>]", " ", text)  # Remove punctuation

                words = re.findall(r"[a-z]+", text.lower())

                # Store each word with context
                for i, word in enumerate(words):
                    context_before = " ".join(words[max(0, i - 3) : i])
                    context_after = " ".join(words[i + 1 : min(len(words), i + 4)])

                    words_with_context.append(
                        {
                            "word": word,
                            "locator": locator,
                            "section": current_section,
                            "context_before": context_before,
                            "context_after": context_after,
                            "full_sentence": " ".join(words),
                        }
                    )

    return words_with_context


def analyze_air_patterns(words_with_context):
    """Analyze AIR usage patterns"""

    # Find all AIR instances (must filter to avoid "dair", "chair", etc.)
    air_instances = []
    for entry in words_with_context:
        word = entry["word"]
        # Only count if "air" appears as standalone or at word boundary
        if word == "air" or word.startswith("air") or word.endswith("air"):
            # Exclude "dair" and other compounds where "air" is not the root
            if "dair" not in word and "chair" not in word and "shair" not in word:
                air_instances.append(entry)

    print("=" * 80)
    print("AIR PROXIMAL SPATIAL HYPOTHESIS INVESTIGATION")
    print("=" * 80)
    print(f"\nTotal AIR instances found: {len(air_instances)}")

    if len(air_instances) == 0:
        print("\nERROR: No AIR instances found!")
        return

    # 1. Section distribution
    print("\n" + "=" * 80)
    print("1. SECTION DISTRIBUTION")
    print("=" * 80)

    section_dist = Counter(inst["section"] for inst in air_instances)
    for section, count in section_dist.most_common():
        pct = (count / len(air_instances)) * 100
        print(f"  {section:20s}: {count:4d} ({pct:5.1f}%)")

    # 2. Form variants
    print("\n" + "=" * 80)
    print("2. FORM VARIANTS (Pure vs. affixed)")
    print("=" * 80)

    form_dist = Counter(inst["word"] for inst in air_instances)
    standalone = form_dist.get("air", 0)
    print(
        f"\nStandalone 'air': {standalone} instances ({standalone / len(air_instances) * 100:.1f}%)"
    )
    print(f"\nTop 25 forms containing 'air':")
    for form, count in form_dist.most_common(25):
        pct = (count / len(air_instances)) * 100
        print(f"  {form:20s}: {count:4d} ({pct:5.1f}%)")

    # 3. Position analysis
    print("\n" + "=" * 80)
    print("3. POSITION ANALYSIS")
    print("=" * 80)

    positions = {"phrase_initial": 0, "phrase_medial": 0, "phrase_final": 0}
    for inst in air_instances:
        before = inst["context_before"].strip()
        after = inst["context_after"].strip()

        if not before or before == "":
            positions["phrase_initial"] += 1
        elif not after or after == "":
            positions["phrase_final"] += 1
        else:
            positions["phrase_medial"] += 1

    for pos, count in positions.items():
        pct = (count / len(air_instances)) * 100
        print(f"  {pos:20s}: {count:4d} ({pct:5.1f}%)")

    # 4. Co-occurrence with "dair"
    print("\n" + "=" * 80)
    print("4. CO-OCCURRENCE WITH 'DAIR' (Testing complementary system)")
    print("=" * 80)

    dair_cooc = sum(1 for inst in air_instances if "dair" in inst["full_sentence"])
    dair_pct = (dair_cooc / len(air_instances)) * 100

    print(
        f"\nSentences with both 'air' AND 'dair': {dair_cooc}/{len(air_instances)} ({dair_pct:.1f}%)"
    )
    print(
        f"Sentences with 'air' but NO 'dair': {len(air_instances) - dair_cooc}/{len(air_instances)} ({100 - dair_pct:.1f}%)"
    )

    # 5. Co-occurrence with validated nouns
    print("\n" + "=" * 80)
    print("5. CO-OCCURRENCE WITH VALIDATED NOUNS")
    print("=" * 80)

    validated_nouns = [
        "ok",
        "qok",
        "ot",
        "qot",
        "shee",
        "she",
        "dor",
        "cho",
        "cheo",
        "sho",
        "keo",
        "teo",
    ]
    cooc_nouns = Counter()

    for inst in air_instances:
        sentence_words = inst["full_sentence"].split()
        for noun in validated_nouns:
            if any(noun in w for w in sentence_words):
                cooc_nouns[noun] += 1

    for noun, count in cooc_nouns.most_common():
        pct = (count / len(air_instances)) * 100
        print(f"  {noun:15s}: {count:4d} sentences ({pct:5.1f}%)")

    # 6. Morphological behavior
    print("\n" + "=" * 80)
    print("6. MORPHOLOGICAL BEHAVIOR (Function words = LOW morphology)")
    print("=" * 80)

    case_suffixes = ["ol", "al", "or", "ar", "ody", "eody"]
    verbal_suffixes = ["y", "edy", "dy"]

    case_count = 0
    verbal_count = 0

    for inst in air_instances:
        word = inst["word"]

        # Check case-marking
        for suffix in case_suffixes:
            if word.endswith(suffix):
                case_count += 1
                break

        # Check verbal
        for suffix in verbal_suffixes:
            if word.endswith(suffix):
                verbal_count += 1
                break

    case_pct = (case_count / len(air_instances)) * 100
    verbal_pct = (verbal_count / len(air_instances)) * 100

    print(f"\nCase-marking rate: {case_count}/{len(air_instances)} ({case_pct:.1f}%)")
    print(f"Verbal rate: {verbal_count}/{len(air_instances)} ({verbal_pct:.1f}%)")
    print(f"\nExpected for function words: <10% case, <10% verbal")
    print(f"Comparison to 'dair': 8.0% case, 5.0% verbal")

    # 7. Sample contexts with "dair" (complementary spatial system)
    print("\n" + "=" * 80)
    print("7. SAMPLE CONTEXTS WITH 'DAIR' (Spatial system)")
    print("=" * 80)

    both_instances = [inst for inst in air_instances if "dair" in inst["full_sentence"]]
    print(f"\nShowing 10 examples with BOTH 'air' and 'dair':")

    for i, inst in enumerate(both_instances[:10], 1):
        sentence = inst["full_sentence"]
        # Highlight both words
        sentence_highlight = sentence.replace(" air ", " [AIR] ").replace(
            " dair ", " [DAIR] "
        )
        print(f"\n{i}. {inst['locator']} ({inst['section']})")
        print(f"   {sentence_highlight}")

    # 8. Frequency ratio comparison
    print("\n" + "=" * 80)
    print("8. FREQUENCY RATIO: 'air' vs 'dair'")
    print("=" * 80)

    # We know from previous analysis: dair = 201 instances
    dair_count = 201
    ratio = len(air_instances) / dair_count

    print(f"\n  'air':  {len(air_instances)} instances")
    print(f"  'dair': {dair_count} instances")
    print(f"  Ratio:  {ratio:.2f}x ('air' is {ratio:.1f}× more common)")
    print(
        f"\nExpected: Proximal terms ('here') are typically 2-3× more common than distal ('there')"
    )
    print(
        f"Result: {'✓ MATCHES expectation' if 2 <= ratio <= 4 else '✗ Does not match'}"
    )


def main():
    filepath = (
        r"C:\Users\adria\Documents\manuscript\data\voynich\eva_transcription\ZL3b-n.txt"
    )

    print("Loading Voynich manuscript with context...")
    words_with_context = load_voynich_with_context(filepath)
    print(f"Loaded {len(words_with_context)} words\n")

    analyze_air_patterns(words_with_context)

    print("\n" + "=" * 80)
    print("HYPOTHESIS EVALUATION")
    print("=" * 80)
    print("""
HYPOTHESIS: "air" = proximal spatial particle meaning "here/at this place"
            (complement to "dair" = "there")

Evidence in favor:
  ✓ LOW morphology (<10% case, <10% verbal = function word)
  ✓ 100% co-occurrence WITH 'dair' (complementary spatial system)
  ✓ 2-3× more frequent than 'dair' (proximal typically more common)
  ✓ Similar section distribution (universal spatial reference)
  ✓ Similar position patterns (spatial particles)

Evidence against:
  ✗ HIGH morphology (>20% case = nominal pattern)
  ✗ No co-occurrence with 'dair' (not complementary)
  ✗ Very different frequency (not related)

Final assessment will be based on the data above.
    """)


if __name__ == "__main__":
    main()
