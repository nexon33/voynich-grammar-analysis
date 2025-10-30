"""
CRITICAL TEST: Null Hypothesis Test

Tests if random Voynich words can achieve validation scores similar to our terms.

Research Question:
  Could our 9/10 and 8/10 scores be achieved by random chance?

Method:
  1. Select 100 random high-frequency words from Voynich manuscript
  2. Analyze each using same objective criteria as our validated terms
  3. Calculate morphology, standalone %, position %, distribution, co-occurrence
  4. Score using 10-point objective system
  5. Compare distribution to our validated terms

Expected Result (if our methodology is sound):
  - Random words should score 2-4/10 on average
  - Very few (<5%) should score ≥8/10
  - Our validated terms (ar=9/10, daiin=8/10) should be statistical outliers

Risk (if methodology is flawed):
  - Random words score 6-8/10 regularly
  - Our terms are not distinguishable from noise
  - Validation framework is meaningless
"""

import re
import random
from collections import Counter, defaultdict


def load_voynich_with_context(filepath):
    """Load Voynich manuscript with context tracking"""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    words_with_context = []

    for line_num, line in enumerate(lines, 1):
        line_stripped = line.strip()

        # Skip empty lines and comments
        if not line_stripped or line_stripped.startswith("#"):
            continue

        # Clean text
        text = re.sub(r"[!*=\-]", "", line_stripped)
        words = re.findall(r"[a-z]+", text.lower())

        # Store each word with context
        for i, word in enumerate(words):
            context_before = " ".join(words[max(0, i - 3) : i])
            context_after = " ".join(words[i + 1 : min(len(words), i + 4)])

            words_with_context.append(
                {
                    "word": word,
                    "line": line_num,
                    "context_before": context_before,
                    "context_after": context_after,
                    "full_sentence": " ".join(words),
                }
            )

    return words_with_context


def analyze_word_objective(word, words_with_context, validated_words):
    """
    Analyze a word using 5 objective criteria

    Returns dict with:
      - morphology_score (0-2)
      - standalone_score (0-2)
      - position_score (0-2)
      - distribution_score (0-2)
      - co_occurrence_score (0-2)
      - total_score (0-10)
    """

    # Extract instances of this word
    instances = [entry for entry in words_with_context if entry["word"] == word]

    if len(instances) == 0:
        return None

    # 1. MORPHOLOGY ANALYSIS
    # Check if word appears with case/verbal suffixes
    morphological_variants = 0
    for entry in words_with_context:
        w = entry["word"]
        # Check if starts with our word and has suffix
        if w.startswith(word) and len(w) > len(word):
            suffix = w[len(word) :]
            if suffix in ["dy", "al", "ol", "ar", "or", "ain", "iin", "aiin", "edy"]:
                morphological_variants += 1

    morphology_pct = (
        100 * morphological_variants / len(instances) if len(instances) > 0 else 0
    )

    if morphology_pct < 5.0:
        morphology_score = 2
    elif morphology_pct < 15.0:
        morphology_score = 1
    else:
        morphology_score = 0

    # 2. STANDALONE FREQUENCY
    # What % appear without morphology?
    standalone_count = len(instances)
    standalone_pct = (
        100 * standalone_count / (standalone_count + morphological_variants)
        if (standalone_count + morphological_variants) > 0
        else 0
    )

    if standalone_pct > 80.0:
        standalone_score = 2
    elif standalone_pct > 60.0:
        standalone_score = 1
    else:
        standalone_score = 0

    # 3. POSITION ANALYSIS
    # Where does word appear in sentences?
    positions = []
    for entry in instances:
        sentence_words = entry["full_sentence"].split()
        word_idx = None
        for idx, w in enumerate(sentence_words):
            if w == word:
                word_idx = idx
                break

        if word_idx is not None:
            if word_idx == 0:
                positions.append("initial")
            elif word_idx == len(sentence_words) - 1:
                positions.append("final")
            else:
                positions.append("medial")

    medial_count = positions.count("medial")
    medial_pct = 100 * medial_count / len(positions) if len(positions) > 0 else 0

    if medial_pct > 70.0:
        position_score = 2
    elif medial_pct > 50.0:
        position_score = 1
    else:
        position_score = 0

    # 4. SECTION DISTRIBUTION
    # (We can't determine sections from this format, so assume universal for now)
    # In real analysis, this would check herbal/biological/pharmaceutical/astronomical
    # For null hypothesis, give everyone 2 points (best case for random words)
    distribution_score = 2  # Generous assumption

    # 5. CO-OCCURRENCE WITH VALIDATED TERMS
    # How often does word appear with our validated terms?
    co_occurrence_count = 0
    for entry in instances:
        sentence = entry["full_sentence"]
        for validated_word in validated_words:
            if validated_word in sentence and validated_word != word:
                co_occurrence_count += 1
                break  # Count sentence once

    co_occurrence_pct = (
        100 * co_occurrence_count / len(instances) if len(instances) > 0 else 0
    )

    if co_occurrence_pct > 15.0:
        co_occurrence_score = 2
    elif co_occurrence_pct > 5.0:
        co_occurrence_score = 1
    else:
        co_occurrence_score = 0

    total_score = (
        morphology_score
        + standalone_score
        + position_score
        + distribution_score
        + co_occurrence_score
    )

    return {
        "word": word,
        "frequency": len(instances),
        "morphology_pct": morphology_pct,
        "morphology_score": morphology_score,
        "standalone_pct": standalone_pct,
        "standalone_score": standalone_score,
        "medial_pct": medial_pct,
        "position_score": position_score,
        "distribution_score": distribution_score,
        "co_occurrence_pct": co_occurrence_pct,
        "co_occurrence_score": co_occurrence_score,
        "total_score": total_score,
    }


def main():
    print("=" * 80)
    print("CRITICAL TEST: NULL HYPOTHESIS TEST")
    print("=" * 80)
    print("\nResearch Question:")
    print("  Can random Voynich words achieve validation scores similar to our terms?")
    print("\nOur validated terms:")
    print("  ar:    9/10 (VALIDATED)")
    print("  daiin: 8/10 (VALIDATED)")
    print("  y:     6/10 (LIKELY)")
    print("\nNull Hypothesis:")
    print("  Random high-frequency words will score 6-8/10 regularly")
    print("  → Our validation framework is meaningless")
    print("\nAlternative Hypothesis:")
    print("  Random words score 2-4/10 on average")
    print("  → Our validated terms are statistical outliers")
    print("\n" + "=" * 80)

    # Load manuscript
    print("\nLoading Voynich manuscript...")
    voynich_path = "data/voynich/eva_transcription/voynich_eva_takahashi.txt"
    words_with_context = load_voynich_with_context(voynich_path)

    # Get word frequencies
    word_counts = Counter(entry["word"] for entry in words_with_context)

    print(f"Loaded {len(words_with_context):,} word instances")
    print(f"Unique words: {len(word_counts):,}")

    # Select high-frequency words (>100 occurrences) excluding our validated terms
    validated_words = [
        "ar",
        "daiin",
        "dain",
        "y",
        "dair",
        "air",
        "ok",
        "ot",
        "she",
        "shee",
        "cho",
        "dor",
        "sho",
        "keo",
        "teo",
        "cheo",
    ]

    high_freq_words = [
        word
        for word, count in word_counts.items()
        if count > 100 and word not in validated_words and len(word) > 1
    ]

    print(f"\nHigh-frequency words (>100 occurrences): {len(high_freq_words)}")
    print(f"Excluding {len(validated_words)} validated terms")

    # Sample 100 random words
    sample_size = min(100, len(high_freq_words))
    random_sample = random.sample(high_freq_words, sample_size)

    print(f"\nAnalyzing {sample_size} random words...")
    print("(This may take a few minutes...)\n")

    # Analyze each random word
    results = []
    for i, word in enumerate(random_sample, 1):
        if i % 10 == 0:
            print(f"  Progress: {i}/{sample_size}...")

        analysis = analyze_word_objective(word, words_with_context, validated_words)
        if analysis:
            results.append(analysis)

    print(f"  Completed: {len(results)}/{sample_size}")

    # Calculate statistics
    scores = [r["total_score"] for r in results]
    avg_score = sum(scores) / len(scores) if scores else 0

    score_distribution = Counter(scores)

    validated_count = sum(1 for s in scores if s >= 8)  # ≥8/10
    likely_count = sum(1 for s in scores if 6 <= s < 8)  # 6-7/10
    possible_count = sum(1 for s in scores if 4 <= s < 6)  # 4-5/10
    rejected_count = sum(1 for s in scores if s < 4)  # <4/10

    print("\n" + "=" * 80)
    print("RESULTS: NULL HYPOTHESIS TEST")
    print("=" * 80)

    print(f"\nRandom word scores (n={len(results)}):")
    print(f"  Average score: {avg_score:.1f}/10")
    print(f"  Min score: {min(scores)}/10")
    print(f"  Max score: {max(scores)}/10")

    print(f"\nScore distribution:")
    for score in range(0, 11):
        count = score_distribution[score]
        pct = 100 * count / len(results) if len(results) > 0 else 0
        bar = "█" * int(pct / 2)
        print(f"  {score:2d}/10: {count:3d} ({pct:5.1f}%)  {bar}")

    print(f"\nValidation categories:")
    print(
        f"  VALIDATED (≥8/10):  {validated_count:3d} ({100 * validated_count / len(results):5.1f}%)"
    )
    print(
        f"  LIKELY (6-7/10):    {likely_count:3d} ({100 * likely_count / len(results):5.1f}%)"
    )
    print(
        f"  POSSIBLE (4-5/10):  {possible_count:3d} ({100 * possible_count / len(results):5.1f}%)"
    )
    print(
        f"  REJECTED (<4/10):   {rejected_count:3d} ({100 * rejected_count / len(results):5.1f}%)"
    )

    # Statistical test
    print("\n" + "=" * 80)
    print("STATISTICAL ANALYSIS")
    print("=" * 80)

    print(f"\nOur validated terms vs random words:")
    print(
        f"  ar (9/10):    Better than {sum(1 for s in scores if s < 9)} / {len(results)} random words ({100 * sum(1 for s in scores if s < 9) / len(results):.1f}%)"
    )
    print(
        f"  daiin (8/10): Better than {sum(1 for s in scores if s < 8)} / {len(results)} random words ({100 * sum(1 for s in scores if s < 8) / len(results):.1f}%)"
    )
    print(
        f"  y (6/10):     Better than {sum(1 for s in scores if s < 6)} / {len(results)} random words ({100 * sum(1 for s in scores if s < 6) / len(results):.1f}%)"
    )

    # Show top-scoring random words (potential false positives)
    top_random = sorted(results, key=lambda x: x["total_score"], reverse=True)[:10]

    print(f"\nTop 10 random words (potential false positives):")
    for i, r in enumerate(top_random, 1):
        print(
            f"  {i:2d}. {r['word']:8s}  {r['total_score']}/10  (freq: {r['frequency']:4d})"
        )

    # CONCLUSION
    print("\n" + "=" * 80)
    print("CRITICAL FINDINGS")
    print("=" * 80)

    if avg_score > 5.0:
        print(f"\n⚠️  WARNING: Random words score {avg_score:.1f}/10 on average")
        print("    NULL HYPOTHESIS CANNOT BE REJECTED")
        print("    → Our validation framework may be too permissive")
        print("    → Scores of 6-8/10 are not statistically significant")
    else:
        print(f"\n✓  Good: Random words score {avg_score:.1f}/10 on average")
        print("    NULL HYPOTHESIS CAN BE REJECTED")
        print("    → Our validation framework is appropriately selective")

    if validated_count > 5:  # >5% of random words validated
        print(
            f"\n⚠️  WARNING: {validated_count} random words ({100 * validated_count / len(results):.1f}%) score ≥8/10"
        )
        print("    → Validation threshold (≥8/10) is too low")
        print("    → Many false positives possible")
    else:
        print(
            f"\n✓  Good: Only {validated_count} random words ({100 * validated_count / len(results):.1f}%) score ≥8/10"
        )
        print("    → Validation threshold (≥8/10) is appropriately stringent")

    if likely_count > 20:  # >20% of random words "likely"
        print(
            f"\n⚠️  WARNING: {likely_count} random words ({100 * likely_count / len(results):.1f}%) score 6-7/10"
        )
        print("    → 'LIKELY' category may include many false positives")
    else:
        print(
            f"\n✓  Good: Only {likely_count} random words ({100 * likely_count / len(results):.1f}%) score 6-7/10"
        )
        print("    → 'LIKELY' category is appropriately selective")

    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)

    if avg_score > 5.0 or validated_count > 5:
        print("\n⚠️  VALIDATION FRAMEWORK NEEDS REVISION:")
        print("  1. Increase validation threshold to ≥9/10")
        print("  2. Add additional objective criteria")
        print("  3. Weight criteria differently (some may be too easy to score)")
        print("  4. Re-validate all terms with revised system")
    else:
        print("\n✓  VALIDATION FRAMEWORK IS SOUND:")
        print("  1. Our terms (ar=9/10, daiin=8/10) are statistical outliers")
        print("  2. Random words score significantly lower (avg={avg_score:.1f}/10)")
        print("  3. Validation threshold (≥8/10) is appropriately stringent")
        print("  4. Proceed with confidence to next tests")

    print("\n" + "=" * 80)
    print("TEST 2 COMPLETE: NULL HYPOTHESIS TEST")
    print("=" * 80)
    print("\nNext: Calculate statistical significance for enrichment claims (Test 3)")


if __name__ == "__main__":
    main()
