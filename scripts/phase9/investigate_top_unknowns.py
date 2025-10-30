"""
Phase 9: Investigate Top 3 Completely Unknown High-Frequency Words

Top candidates from analysis:
1. chey (350 instances, 0.951% of corpus) - HIGH PRIORITY
2. cheey (184 instances, 0.500% of corpus)
3. chy (166 instances, 0.451% of corpus)

These are 3-4 letter words appearing completely unknown.
Let's apply full 10-point validation to see if they're:
- Function words (low morphology, specific position)
- Morphological roots (high morphology, productive)
"""

import re
from collections import Counter, defaultdict


def load_voynich_with_context(filepath):
    """Load Voynich manuscript with context"""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    words_with_context = []
    current_section = "unknown"

    for line_num, line in enumerate(lines, 1):
        line_stripped = line.strip()

        if not line_stripped or line_stripped.startswith("#"):
            continue

        # Extract folio/section
        folio_match = re.search(r"<f(\d+)[rv]", line_stripped)
        if folio_match:
            folio_num = int(folio_match.group(1))

            if 1 <= folio_num <= 66:
                current_section = "herbal"
            elif 67 <= folio_num <= 73:
                current_section = "astronomical"
            elif 75 <= folio_num <= 84:
                current_section = "biological"
            elif 85 <= folio_num <= 116:
                current_section = "pharmaceutical"
            else:
                current_section = "unknown"

        # Extract words
        text = re.sub(r"\[.*?\]", "", line_stripped)
        text = re.sub(r"\{.*?\}", "", text)
        text = re.sub(r"<.*?>", "", text)
        text = re.sub(r"[!*=\-@$%,.:;()']", " ", text)
        words = re.findall(r"[a-z]{2,}", text.lower())

        for i, word in enumerate(words):
            context_before = " ".join(words[max(0, i - 3) : i])
            context_after = " ".join(words[i + 1 : min(len(words), i + 4)])

            words_with_context.append(
                {
                    "word": word,
                    "line": line_num,
                    "section": current_section,
                    "context_before": context_before,
                    "context_after": context_after,
                    "full_sentence": " ".join(words),
                }
            )

    return words_with_context


def find_morphological_variants(root, words_with_context):
    """Find all morphological variants"""
    suffixes = [
        "dy",
        "al",
        "ol",
        "ar",
        "or",
        "ain",
        "iin",
        "aiin",
        "edy",
        "y",
        "s",
        "d",
        "l",
        "r",
    ]
    variants = []

    word_counts = Counter(entry["word"] for entry in words_with_context)

    for word in word_counts.keys():
        if word.startswith(root) and len(word) > len(root):
            remainder = word[len(root) :]
            if any(remainder.startswith(s) for s in suffixes):
                variants.append(word)

    return list(set(variants))


def analyze_full_10point(target_word, words_with_context, validated_words):
    """Full 10-point validation"""

    instances = [entry for entry in words_with_context if entry["word"] == target_word]

    if len(instances) == 0:
        print(f"No instances found for '{target_word}'")
        return None

    print(f"\n{'=' * 70}")
    print(f"ANALYZING: {target_word.upper()}")
    print(f"{'=' * 70}")
    print(f"Total instances: {len(instances)}")

    # Count all words
    all_word_counts = Counter(entry["word"] for entry in words_with_context)

    # 1. MORPHOLOGY ANALYSIS (0-2 points)
    # Check if this word appears with suffixes (morphological productivity)
    variants = find_morphological_variants(target_word, words_with_context)

    # Calculate case-marking and verbal percentages
    case_marked = sum(
        1
        for w in variants
        if w.endswith(("al", "ol", "ar", "or")) and len(w) > len(target_word)
    )
    verbal = sum(
        1 for w in variants if w.endswith(("dy", "edy")) and len(w) > len(target_word)
    )

    total_variants = len(variants)
    case_marking_pct = 100 * case_marked / total_variants if total_variants > 0 else 0
    verbal_pct = 100 * verbal / total_variants if total_variants > 0 else 0

    # For roots: HIGH morphology = good (inverted scoring)
    # For function words: LOW morphology = good
    # Let's check both and decide based on other criteria

    morphology_instances = sum(all_word_counts[v] for v in variants)
    total_instances = len(instances) + morphology_instances
    morphology_pct = (
        100 * morphology_instances / total_instances if total_instances > 0 else 0
    )

    print(f"\n1. MORPHOLOGY ANALYSIS:")
    print(f"   Morphological variants found: {len(variants)}")
    if len(variants) > 0:
        print(f"   Top variants: {', '.join(list(variants)[:10])}")
    print(f"   Case-marking variants: {case_marking_pct:.1f}%")
    print(f"   Verbal variants: {verbal_pct:.1f}%")
    print(f"   Total with morphology: {morphology_instances:,} instances")
    print(f"   Morphology percentage: {morphology_pct:.1f}%")

    # Score morphology (will decide if root or function word based on other criteria)
    if morphology_pct > 30:
        morphology_score_root = 2  # Good for root
        morphology_score_func = 0  # Bad for function word
    elif morphology_pct > 15:
        morphology_score_root = 1
        morphology_score_func = 1
    elif morphology_pct < 5:
        morphology_score_root = 0  # Bad for root
        morphology_score_func = 2  # Good for function word
    else:
        morphology_score_root = 0
        morphology_score_func = 1

    # 2. STANDALONE FREQUENCY (0-2 points)
    standalone_pct = (
        100 * len(instances) / total_instances if total_instances > 0 else 0
    )

    print(f"\n2. STANDALONE FREQUENCY:")
    print(f"   Standalone instances: {len(instances):,}")
    print(f"   Total instances (with variants): {total_instances:,}")
    print(f"   Standalone percentage: {standalone_pct:.1f}%")

    if standalone_pct > 80:
        standalone_score = 2
    elif standalone_pct > 60:
        standalone_score = 1
    else:
        standalone_score = 0

    # 3. POSITION ANALYSIS (0-2 points)
    positions = {"initial": 0, "medial": 0, "final": 0}

    for entry in instances:
        sentence = entry["full_sentence"].split()
        try:
            idx = sentence.index(target_word)
            if idx == 0:
                positions["initial"] += 1
            elif idx == len(sentence) - 1:
                positions["final"] += 1
            else:
                positions["medial"] += 1
        except ValueError:
            pass

    total_pos = sum(positions.values())
    initial_pct = 100 * positions["initial"] / total_pos if total_pos > 0 else 0
    medial_pct = 100 * positions["medial"] / total_pos if total_pos > 0 else 0
    final_pct = 100 * positions["final"] / total_pos if total_pos > 0 else 0

    print(f"\n3. POSITION ANALYSIS:")
    print(f"   Initial: {positions['initial']:,} ({initial_pct:.1f}%)")
    print(f"   Medial: {positions['medial']:,} ({medial_pct:.1f}%)")
    print(f"   Final: {positions['final']:,} ({final_pct:.1f}%)")

    # Function words tend to be medial (>70%)
    # Sentence-final particles are final (>50%)
    if medial_pct > 70:
        position_score = 2  # Function word pattern
    elif final_pct > 50:
        position_score = 2  # Sentence-final particle pattern
    elif medial_pct > 50 or final_pct > 30:
        position_score = 1
    else:
        position_score = 0

    # 4. SECTION DISTRIBUTION (0-2 points)
    section_counts = Counter(entry["section"] for entry in instances)

    print(f"\n4. SECTION DISTRIBUTION:")
    for section in ["herbal", "biological", "pharmaceutical", "astronomical"]:
        count = section_counts.get(section, 0)
        pct = 100 * count / len(instances) if len(instances) > 0 else 0
        print(f"   {section:<18}: {count:>4} ({pct:>5.1f}%)")

    num_sections = sum(1 for count in section_counts.values() if count > 0)
    print(f"   Appears in {num_sections}/4 sections")

    if num_sections == 4:
        distribution_score = 2  # Universal
    elif num_sections >= 3:
        distribution_score = 1
    else:
        distribution_score = 0

    # 5. CO-OCCURRENCE WITH VALIDATED TERMS (0-2 points)
    cooccurrence_count = 0

    for entry in instances:
        sentence = entry["full_sentence"].split()
        if any(word in validated_words for word in sentence if word != target_word):
            cooccurrence_count += 1

    cooccurrence_pct = (
        100 * cooccurrence_count / len(instances) if len(instances) > 0 else 0
    )

    print(f"\n5. CO-OCCURRENCE WITH VALIDATED TERMS:")
    print(
        f"   Sentences with validated terms: {cooccurrence_count:,}/{len(instances):,}"
    )
    print(f"   Co-occurrence percentage: {cooccurrence_pct:.1f}%")

    if cooccurrence_pct > 15:
        cooccurrence_score = 2
    elif cooccurrence_pct > 5:
        cooccurrence_score = 1
    else:
        cooccurrence_score = 0

    # DETERMINE TYPE AND CALCULATE SCORE
    # If low morphology + medial position → function word
    # If high morphology → root
    is_function_word = morphology_pct < 15 and medial_pct > 50
    is_root = morphology_pct > 15

    if is_function_word:
        morphology_score = morphology_score_func
        interpretation = "FUNCTION WORD"
    elif is_root:
        morphology_score = morphology_score_root
        interpretation = "MORPHOLOGICAL ROOT"
    else:
        # Ambiguous - use average
        morphology_score = (morphology_score_root + morphology_score_func) // 2
        interpretation = "AMBIGUOUS (could be either)"

    total_score = (
        morphology_score
        + standalone_score
        + position_score
        + distribution_score
        + cooccurrence_score
    )

    print(f"\n{'=' * 70}")
    print(f"VALIDATION SCORE: {total_score}/10")
    print(f"{'=' * 70}")
    print(f"Morphology:       {morphology_score}/2")
    print(f"Standalone:       {standalone_score}/2")
    print(f"Position:         {position_score}/2")
    print(f"Distribution:     {distribution_score}/2")
    print(f"Co-occurrence:    {cooccurrence_score}/2")

    print(f"\nINTERPRETATION: {interpretation}")

    if total_score >= 8:
        print("STATUS: ✓✓✓ VALIDATED")
    elif total_score >= 6:
        print("STATUS: ✓ LIKELY")
    else:
        print("STATUS: ✗ NOT VALIDATED")

    # Show sample contexts
    print(f"\n{'=' * 70}")
    print("SAMPLE CONTEXTS (First 10)")
    print(f"{'=' * 70}")

    for i, entry in enumerate(instances[:10], 1):
        print(f"\n{i}. [{entry['section']}]")
        print(f"   Before: {entry['context_before']}")
        print(f"   → {target_word} ←")
        print(f"   After:  {entry['context_after']}")

    return {
        "word": target_word,
        "total_score": total_score,
        "instances": len(instances),
        "morphology_pct": morphology_pct,
        "variants": len(variants),
        "interpretation": interpretation,
        "scores": {
            "morphology": morphology_score,
            "standalone": standalone_score,
            "position": position_score,
            "distribution": distribution_score,
            "cooccurrence": cooccurrence_score,
        },
        "position_dist": {
            "initial": initial_pct,
            "medial": medial_pct,
            "final": final_pct,
        },
    }


# Main execution
print("=" * 70)
print("PHASE 9: INVESTIGATING TOP 3 COMPLETELY UNKNOWN WORDS")
print("=" * 70)

print("\nLoading Voynich manuscript...")
words_with_context = load_voynich_with_context(
    "data/voynich/eva_transcription/ZL3b-n.txt"
)
print(f"Loaded {len(words_with_context):,} words")

# Validated words from Phase 8
validated_words = [
    "ok",
    "qok",
    "ot",
    "qot",
    "she",
    "shee",
    "dor",
    "cho",
    "cheo",
    "sho",
    "keo",
    "teo",
    "okal",
    "or",
    "dol",
    "dar",
    "chol",
    "dair",
    "air",
    "ar",
    "daiin",
    "dain",
    "sal",
    "qol",
    "ory",
    "y",
]

# Investigate top 3
candidates = ["chey", "cheey", "chy"]

results = []
for candidate in candidates:
    result = analyze_full_10point(candidate, words_with_context, validated_words)
    if result:
        results.append(result)

# Summary
print(f"\n\n{'=' * 70}")
print("SUMMARY OF ALL 3 CANDIDATES")
print(f"{'=' * 70}")

print(
    f"\n{'Word':<10} {'Score':<8} {'Instances':<12} {'Morphology':<15} {'Interpretation':<25}"
)
print("-" * 80)

for r in results:
    print(
        f"{r['word']:<10} {r['total_score']}/10   {r['instances']:<12} {r['morphology_pct']:>6.1f}%        {r['interpretation']:<25}"
    )

# Recommendations
print(f"\n{'=' * 70}")
print("RECOMMENDATIONS FOR PHASE 9")
print(f"{'=' * 70}")

validated = [r for r in results if r["total_score"] >= 8]
likely = [r for r in results if 6 <= r["total_score"] < 8]

if validated:
    print(f"\n✓✓✓ VALIDATED ({len(validated)} terms):")
    for r in validated:
        print(f"  - {r['word']} ({r['total_score']}/10) - {r['interpretation']}")
        print(f"    Add to Phase 9 vocabulary immediately")

if likely:
    print(f"\n✓ LIKELY ({len(likely)} terms):")
    for r in likely:
        print(f"  - {r['word']} ({r['total_score']}/10) - {r['interpretation']}")
        print(f"    Consider for Phase 9 vocabulary with hedging")

not_validated = [r for r in results if r["total_score"] < 6]
if not_validated:
    print(f"\n✗ NOT VALIDATED ({len(not_validated)} terms):")
    for r in not_validated:
        print(f"  - {r['word']} ({r['total_score']}/10)")
        print(f"    Requires more investigation or may be complex compound")

print(f"\n{'=' * 70}")
print("END OF PHASE 9 INVESTIGATION - TOP 3 UNKNOWNS")
print(f"{'=' * 70}")
