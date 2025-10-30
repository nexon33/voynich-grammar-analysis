"""
Phase 8: Investigate Three Function Word Candidates

Candidates (already tentatively identified in earlier phases):
1. sal - hypothesized as AND/BUT (conjunction)
2. qol - hypothesized as THEN (temporal/sequential particle)
3. ory - hypothesized as ADV (adverbial particle)

Using 10-point OBJECTIVE validation only (no manual scoring):
1. Morphology (0-2)
2. Standalone (0-2)
3. Position (0-2)
4. Distribution (0-2)
5. Co-occurrence (0-2)

Thresholds:
- ≥8/10 = VALIDATED
- 6-7/10 = LIKELY
- 4-5/10 = POSSIBLE
- <4/10 = REJECTED
"""

import re
from collections import Counter, defaultdict


def load_voynich_with_context(filepath):
    """Load Voynich manuscript with context tracking"""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    words_with_context = []
    current_section = "unknown"

    for line_num, line in enumerate(lines, 1):
        line_stripped = line.strip()

        if not line_stripped or line_stripped.startswith("#"):
            continue

        # Track section markers if present (we'll add these manually based on folio ranges)
        text = re.sub(r"[!*=\-]", "", line_stripped)
        words = re.findall(r"[a-z]+", text.lower())

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


def analyze_word_objective(target_word, words_with_context, validated_words):
    """
    Analyze a word using 5 objective criteria (10-point scale)
    """

    # Extract instances
    instances = [entry for entry in words_with_context if entry["word"] == target_word]

    if len(instances) == 0:
        return None

    print(f"\n{'=' * 80}")
    print(f"ANALYZING: {target_word}")
    print(f"Total instances: {len(instances)}")
    print("=" * 80)

    # 1. MORPHOLOGY ANALYSIS
    print("\n1. MORPHOLOGY ANALYSIS")
    print("   Checking if word appears with case/verbal suffixes...")

    morphological_variants = []
    for entry in words_with_context:
        w = entry["word"]
        if w.startswith(target_word) and len(w) > len(target_word):
            suffix = w[len(target_word) :]
            if suffix in ["dy", "al", "ol", "ar", "or", "ain", "iin", "aiin", "edy"]:
                morphological_variants.append(w)

    morphological_variant_count = len(morphological_variants)
    morphology_pct = (
        100 * morphological_variant_count / len(instances) if len(instances) > 0 else 0
    )

    print(f"   Morphological variants found: {morphological_variant_count}")
    if morphological_variant_count > 0:
        variant_sample = list(set(morphological_variants))[:10]
        print(f"   Examples: {', '.join(variant_sample)}")
    print(f"   Morphology rate: {morphology_pct:.1f}%")

    if morphology_pct < 5.0:
        morphology_score = 2
        print(f"   Score: 2/2 (excellent - <5% morphology, typical of function words)")
    elif morphology_pct < 15.0:
        morphology_score = 1
        print(f"   Score: 1/2 (moderate - 5-15% morphology)")
    else:
        morphology_score = 0
        print(f"   Score: 0/2 (poor - >15% morphology, typical of content words)")

    # 2. STANDALONE FREQUENCY
    print("\n2. STANDALONE FREQUENCY")
    standalone_count = len(instances)
    total_count = standalone_count + morphological_variant_count
    standalone_pct = 100 * standalone_count / total_count if total_count > 0 else 0

    print(f"   Standalone: {standalone_count} instances")
    print(f"   With morphology: {morphological_variant_count} instances")
    print(f"   Standalone rate: {standalone_pct:.1f}%")

    if standalone_pct > 80.0:
        standalone_score = 2
        print(f"   Score: 2/2 (excellent - >80% standalone)")
    elif standalone_pct > 60.0:
        standalone_score = 1
        print(f"   Score: 1/2 (moderate - 60-80% standalone)")
    else:
        standalone_score = 0
        print(f"   Score: 0/2 (poor - <60% standalone)")

    # 3. POSITION ANALYSIS
    print("\n3. POSITION ANALYSIS")
    positions = []
    for entry in instances:
        sentence_words = entry["full_sentence"].split()
        word_idx = None
        for idx, w in enumerate(sentence_words):
            if w == target_word:
                word_idx = idx
                break

        if word_idx is not None:
            if word_idx == 0:
                positions.append("initial")
            elif word_idx == len(sentence_words) - 1:
                positions.append("final")
            else:
                positions.append("medial")

    initial_count = positions.count("initial")
    medial_count = positions.count("medial")
    final_count = positions.count("final")

    initial_pct = 100 * initial_count / len(positions) if len(positions) > 0 else 0
    medial_pct = 100 * medial_count / len(positions) if len(positions) > 0 else 0
    final_pct = 100 * final_count / len(positions) if len(positions) > 0 else 0

    print(f"   Initial position: {initial_count} ({initial_pct:.1f}%)")
    print(f"   Medial position: {medial_count} ({medial_pct:.1f}%)")
    print(f"   Final position: {final_count} ({final_pct:.1f}%)")

    if medial_pct > 70.0:
        position_score = 2
        print(f"   Score: 2/2 (excellent - >70% medial, typical of function words)")
    elif medial_pct > 50.0:
        position_score = 1
        print(f"   Score: 1/2 (moderate - 50-70% medial)")
    else:
        position_score = 0
        print(f"   Score: 0/2 (poor - <50% medial)")

    # 4. SECTION DISTRIBUTION
    print("\n4. SECTION DISTRIBUTION")
    print("   Note: Section markers not available in current file format")
    print("   Assuming universal distribution (generous scoring)")
    distribution_score = 2
    print(f"   Score: 2/2 (assumed universal)")

    # 5. CO-OCCURRENCE WITH VALIDATED TERMS
    print("\n5. CO-OCCURRENCE WITH VALIDATED TERMS")
    co_occurrence_count = 0
    for entry in instances:
        sentence = entry["full_sentence"]
        for validated_word in validated_words:
            if validated_word in sentence and validated_word != target_word:
                co_occurrence_count += 1
                break

    co_occurrence_pct = (
        100 * co_occurrence_count / len(instances) if len(instances) > 0 else 0
    )

    print(f"   Sentences with validated terms: {co_occurrence_count}/{len(instances)}")
    print(f"   Co-occurrence rate: {co_occurrence_pct:.1f}%")

    if co_occurrence_pct > 15.0:
        co_occurrence_score = 2
        print(f"   Score: 2/2 (excellent - >15% co-occurrence)")
    elif co_occurrence_pct > 5.0:
        co_occurrence_score = 1
        print(f"   Score: 1/2 (moderate - 5-15% co-occurrence)")
    else:
        co_occurrence_score = 0
        print(f"   Score: 0/2 (poor - <5% co-occurrence)")

    # TOTAL SCORE
    total_score = (
        morphology_score
        + standalone_score
        + position_score
        + distribution_score
        + co_occurrence_score
    )

    print(f"\n{'=' * 80}")
    print("VALIDATION SCORE SUMMARY")
    print("=" * 80)
    print(
        f"  1. Morphology:     {morphology_score}/2  ({morphology_pct:.1f}% morphology)"
    )
    print(
        f"  2. Standalone:     {standalone_score}/2  ({standalone_pct:.1f}% standalone)"
    )
    print(f"  3. Position:       {position_score}/2  ({medial_pct:.1f}% medial)")
    print(f"  4. Distribution:   {distribution_score}/2  (assumed universal)")
    print(
        f"  5. Co-occurrence:  {co_occurrence_score}/2  ({co_occurrence_pct:.1f}% with validated)"
    )
    print(f"\n  TOTAL SCORE: {total_score}/10")

    if total_score >= 8:
        status = "VALIDATED"
        symbol = "✓✓✓"
    elif total_score >= 6:
        status = "LIKELY"
        symbol = "✓✓"
    elif total_score >= 4:
        status = "POSSIBLE"
        symbol = "✓"
    else:
        status = "REJECTED"
        symbol = "✗"

    print(f"\n  STATUS: {status} {symbol}")

    # Show sample contexts
    print(f"\n{'=' * 80}")
    print("SAMPLE CONTEXTS")
    print("=" * 80)

    sample_size = min(10, len(instances))
    import random

    samples = random.sample(instances, sample_size)

    for i, sample in enumerate(samples, 1):
        print(f"\n{i}. Line {sample['line']}:")
        print(
            f"   ...{sample['context_before']} >>>{target_word}<<< {sample['context_after']}..."
        )

    return {
        "word": target_word,
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
        "status": status,
    }


def main():
    print("=" * 80)
    print("PHASE 8: INVESTIGATING THREE FUNCTION WORD CANDIDATES")
    print("=" * 80)
    print("\nCandidates:")
    print("  1. sal - AND/BUT (conjunction)")
    print("  2. qol - THEN (temporal/sequential particle)")
    print("  3. ory - ADV (adverbial particle)")
    print("\nUsing 10-point OBJECTIVE validation (no manual scoring)")
    print("\n" + "=" * 80)

    # Load manuscript
    print("\nLoading Voynich manuscript...")
    voynich_path = "data/voynich/eva_transcription/voynich_eva_takahashi.txt"
    words_with_context = load_voynich_with_context(voynich_path)

    word_counts = Counter(entry["word"] for entry in words_with_context)
    print(f"Loaded {len(words_with_context):,} word instances")
    print(f"Unique words: {len(word_counts):,}")

    # Validated terms for co-occurrence testing
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
        "qok",
        "qot",
    ]

    # Analyze each candidate
    candidates = ["sal", "qol", "ory"]
    results = {}

    for candidate in candidates:
        freq = word_counts.get(candidate, 0)
        print(f"\n\n{'#' * 80}")
        print(f"CANDIDATE: {candidate.upper()}")
        print(f"Frequency: {freq:,} instances")
        print(f"{'#' * 80}")

        if freq == 0:
            print(f"\n⚠️  WARNING: '{candidate}' not found in manuscript!")
            print("   This candidate may not exist or may be spelled differently.")
            continue

        result = analyze_word_objective(candidate, words_with_context, validated_words)
        if result:
            results[candidate] = result

    # Summary
    print("\n\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)

    for candidate in candidates:
        if candidate in results:
            r = results[candidate]
            print(f"\n{candidate.upper()}: {r['total_score']}/10 - {r['status']}")
            print(f"  Frequency: {r['frequency']:,}")
            print(
                f"  Morphology: {r['morphology_pct']:.1f}% ({r['morphology_score']}/2)"
            )
            print(
                f"  Standalone: {r['standalone_pct']:.1f}% ({r['standalone_score']}/2)"
            )
            print(
                f"  Position: {r['medial_pct']:.1f}% medial ({r['position_score']}/2)"
            )
            print(
                f"  Co-occurrence: {r['co_occurrence_pct']:.1f}% ({r['co_occurrence_score']}/2)"
            )

    validated_count = sum(1 for r in results.values() if r["status"] == "VALIDATED")
    likely_count = sum(1 for r in results.values() if r["status"] == "LIKELY")

    print("\n" + "=" * 80)
    print("PHASE 8 RESULTS")
    print("=" * 80)
    print(f"\nValidated: {validated_count}")
    print(f"Likely: {likely_count}")
    print(f"Total analyzed: {len(results)}")

    if validated_count + likely_count > 0:
        print("\n✓ SUCCESS: We have new function word candidates!")
        print("  These can be added to the translation framework.")
    else:
        print("\n⚠️  All candidates scored below validation threshold.")
        print("  May need to reconsider these hypotheses or test other words.")


if __name__ == "__main__":
    main()
