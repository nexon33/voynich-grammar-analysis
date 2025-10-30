#!/usr/bin/env python3
"""
Investigate DAIR as Spatial/Directional Function Word
=====================================================

User's intuition: "dair... reminds me of there (like in there in the sky)"

Hypothesis: "dair" = spatial/locative particle meaning "there/in that place"

Evidence to check:
1. Contextual usage patterns
2. Co-occurrence with spatial/astronomical terms
3. Morphological behavior (should be LOW like function words)
4. Comparison to related forms (air, aly, tey)
5. Position in phrases (demonstratives typically phrase-initial)

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


def analyze_dair_patterns(words_with_context):
    """Analyze DAIR usage patterns"""

    # Find all DAIR instances
    dair_instances = []
    for entry in words_with_context:
        word = entry["word"]
        if "dair" in word:
            dair_instances.append(entry)

    print("=" * 80)
    print("DAIR SPATIAL HYPOTHESIS INVESTIGATION")
    print("=" * 80)
    print(f"\nTotal DAIR instances found: {len(dair_instances)}")

    if len(dair_instances) == 0:
        print("\nERROR: No DAIR instances found!")
        return

    # 1. Section distribution
    print("\n" + "=" * 80)
    print("1. SECTION DISTRIBUTION (Testing astronomical enrichment)")
    print("=" * 80)

    section_dist = Counter(inst["section"] for inst in dair_instances)
    for section, count in section_dist.most_common():
        pct = (count / len(dair_instances)) * 100
        print(f"  {section:20s}: {count:4d} ({pct:5.1f}%)")

    # 2. Form variants
    print("\n" + "=" * 80)
    print("2. FORM VARIANTS (Pure vs. affixed)")
    print("=" * 80)

    form_dist = Counter(inst["word"] for inst in dair_instances)
    standalone = form_dist.get("dair", 0)
    print(
        f"\nStandalone 'dair': {standalone} instances ({standalone / len(dair_instances) * 100:.1f}%)"
    )
    print(f"\nTop 20 forms containing 'dair':")
    for form, count in form_dist.most_common(20):
        pct = (count / len(dair_instances)) * 100
        print(f"  {form:20s}: {count:4d} ({pct:5.1f}%)")

    # 3. Position analysis (word-initial = demonstrative pattern)
    print("\n" + "=" * 80)
    print("3. POSITION ANALYSIS (Demonstratives = phrase-initial)")
    print("=" * 80)

    positions = {"phrase_initial": 0, "phrase_medial": 0, "phrase_final": 0}
    for inst in dair_instances:
        before = inst["context_before"].strip()
        after = inst["context_after"].strip()

        if not before or before == "":
            positions["phrase_initial"] += 1
        elif not after or after == "":
            positions["phrase_final"] += 1
        else:
            positions["phrase_medial"] += 1

    for pos, count in positions.items():
        pct = (count / len(dair_instances)) * 100
        print(f"  {pos:20s}: {count:4d} ({pct:5.1f}%)")

    # 4. Co-occurrence with astronomical terms
    print("\n" + "=" * 80)
    print("4. CO-OCCURRENCE WITH ASTRONOMICAL/SPATIAL TERMS")
    print("=" * 80)

    astronomical_terms = [
        "ykeody",
        "yteody",
        "otey",
        "tey",
        "air",
        "aly",
        "ary",
        "okain",
        "okeey",
    ]
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

    cooc_astro = Counter()
    cooc_nouns = Counter()

    for inst in dair_instances:
        sentence_words = inst["full_sentence"].split()

        # Check astronomical terms
        for term in astronomical_terms:
            if any(term in w for w in sentence_words):
                cooc_astro[term] += 1

        # Check validated nouns
        for noun in validated_nouns:
            if any(noun in w for w in sentence_words):
                cooc_nouns[noun] += 1

    print("\nCo-occurrence with astronomical terms:")
    if cooc_astro:
        for term, count in cooc_astro.most_common():
            pct = (count / len(dair_instances)) * 100
            print(f"  {term:15s}: {count:4d} sentences ({pct:5.1f}%)")
    else:
        print("  No significant co-occurrence found")

    print("\nCo-occurrence with validated nouns:")
    if cooc_nouns:
        for noun, count in cooc_nouns.most_common():
            pct = (count / len(dair_instances)) * 100
            print(f"  {noun:15s}: {count:4d} sentences ({pct:5.1f}%)")
    else:
        print("  No significant co-occurrence found")

    # 5. Sample contexts (astronomical section)
    print("\n" + "=" * 80)
    print("5. SAMPLE CONTEXTS (Astronomical section)")
    print("=" * 80)

    astro_instances = [
        inst for inst in dair_instances if inst["section"] == "astronomical"
    ]
    print(
        f"\nShowing up to 15 astronomical instances (found {len(astro_instances)} total):"
    )
    for i, inst in enumerate(astro_instances[:15], 1):
        word = inst["word"]
        before = inst["context_before"][-40:] if inst["context_before"] else ""
        after = inst["context_after"][:40] if inst["context_after"] else ""
        print(f"\n{i}. {inst['locator']}")
        print(f"   ...{before} [{word}] {after}...")

    # 6. Morphological behavior
    print("\n" + "=" * 80)
    print("6. MORPHOLOGICAL BEHAVIOR (Function words = LOW morphology)")
    print("=" * 80)

    case_suffixes = ["ol", "al", "or", "ar", "ody", "eody"]
    verbal_suffixes = ["y", "edy", "dy"]

    case_count = 0
    verbal_count = 0

    for inst in dair_instances:
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

    case_pct = (case_count / len(dair_instances)) * 100
    verbal_pct = (verbal_count / len(dair_instances)) * 100

    print(f"\nCase-marking rate: {case_count}/{len(dair_instances)} ({case_pct:.1f}%)")
    print(f"Verbal rate: {verbal_count}/{len(dair_instances)} ({verbal_pct:.1f}%)")
    print(f"\nExpected for function words: <10% case, <5% verbal")
    print(f"Expected for nouns: 30-60% case, <15% verbal")

    # 7. Comparison with related forms
    print("\n" + "=" * 80)
    print("7. COMPARISON WITH RELATED FORMS")
    print("=" * 80)

    related_forms = ["air", "aly", "tey", "odair", "daiin"]
    print("\nComparing morphological behavior:")
    print(f"{'Form':15s} {'Instances':>10s} {'Case%':>10s} {'Verbal%':>10s}")
    print("-" * 50)

    for form in related_forms:
        form_instances = [
            entry for entry in words_with_context if form in entry["word"]
        ]
        if not form_instances:
            continue

        case_count = sum(
            1
            for inst in form_instances
            if any(inst["word"].endswith(suf) for suf in case_suffixes)
        )
        verbal_count = sum(
            1
            for inst in form_instances
            if any(inst["word"].endswith(suf) for suf in verbal_suffixes)
        )

        case_pct = (case_count / len(form_instances)) * 100
        verbal_pct = (verbal_count / len(form_instances)) * 100

        print(
            f"{form:15s} {len(form_instances):>10d} {case_pct:>9.1f}% {verbal_pct:>9.1f}%"
        )

    # Show DAIR for comparison
    case_count = sum(
        1
        for inst in dair_instances
        if any(inst["word"].endswith(suf) for suf in case_suffixes)
    )
    verbal_count = sum(
        1
        for inst in dair_instances
        if any(inst["word"].endswith(suf) for suf in verbal_suffixes)
    )
    case_pct = (case_count / len(dair_instances)) * 100
    verbal_pct = (verbal_count / len(dair_instances)) * 100
    print(
        f"{'dair (reference)':15s} {len(dair_instances):>10d} {case_pct:>9.1f}% {verbal_pct:>9.1f}%"
    )


def main():
    filepath = (
        r"C:\Users\adria\Documents\manuscript\data\voynich\eva_transcription\ZL3b-n.txt"
    )

    print("Loading Voynich manuscript with context...")
    words_with_context = load_voynich_with_context(filepath)
    print(f"Loaded {len(words_with_context)} words\n")

    analyze_dair_patterns(words_with_context)

    print("\n" + "=" * 80)
    print("HYPOTHESIS EVALUATION")
    print("=" * 80)
    print("""
HYPOTHESIS: "dair" = spatial/locative particle meaning "there/in that place"

Evidence in favor:
  ✓ Astronomical enrichment (if >20%)
  ✓ LOW morphology (<10% case, <5% verbal = function word)
  ✓ Phrase-initial position (if >40% = demonstrative pattern)
  ✓ Co-occurs with astronomical terms (spatial context)
  ✓ Similar behavior to other particles (air, aly, tey)

Evidence against:
  ✗ HIGH morphology (>20% case = nominal pattern)
  ✗ Phrase-medial position (>60% = not demonstrative)
  ✗ No astronomical enrichment
  ✗ Different behavior from particles

Final assessment will be based on the data above.
    """)


if __name__ == "__main__":
    main()
