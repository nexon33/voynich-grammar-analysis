"""
Phase 8: Find New Morphological Roots

Strategy A: Look for high-frequency morphological roots (like ok, she, che)
Strategy C: Systematically test top 20 most frequent unexplained words

Criteria for morphological roots:
1. High frequency (>50 occurrences)
2. Short length (2-4 letters)
3. Form productive compounds (root + suffix patterns)
4. NOT already validated
5. Score well on structural criteria

Method:
1. Get top 50 high-frequency words
2. Exclude already validated terms
3. Filter for 2-4 letter words (potential roots)
4. Check for productive compounding (do they form variants?)
5. Quick validation scoring
6. Rank by promising candidates
"""

import re
from collections import Counter, defaultdict


def load_voynich_with_context(filepath):
    """Load Voynich manuscript with context tracking"""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    words_with_context = []

    for line_num, line in enumerate(lines, 1):
        line_stripped = line.strip()

        if not line_stripped or line_stripped.startswith("#"):
            continue

        text = re.sub(r"[!*=\-]", "", line_stripped)
        words = re.findall(r"[a-z]+", text.lower())

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


def find_compounds(root, all_words):
    """Find words that start with this root and have known suffixes"""
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
    ]
    compounds = []

    for word in all_words:
        if word.startswith(root) and len(word) > len(root):
            remainder = word[len(root) :]
            # Check if remainder is a known suffix
            if remainder in suffixes:
                compounds.append(word)
            # Or if remainder starts with a suffix
            elif any(remainder.startswith(s) for s in suffixes):
                compounds.append(word)

    return list(set(compounds))


def quick_validation(word, words_with_context, validated_words):
    """Quick validation scoring for root candidates"""

    instances = [entry for entry in words_with_context if entry["word"] == word]

    if len(instances) == 0:
        return None

    # 1. MORPHOLOGY (check for compounds)
    word_counts = Counter(entry["word"] for entry in words_with_context)
    all_words = list(word_counts.keys())
    compounds = find_compounds(word, all_words)

    morphology_pct = 100 * len(compounds) / len(instances) if len(instances) > 0 else 0

    # For ROOTS, we want HIGH morphology (they should form compounds)
    # This is opposite of function words!
    if morphology_pct > 30:
        morphology_score = 2  # Excellent - productive root
    elif morphology_pct > 15:
        morphology_score = 1  # Moderate
    else:
        morphology_score = 0  # Poor - not productive

    # 2. POSITION
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

    # Roots can appear anywhere, so we're less strict
    if medial_pct > 40:
        position_score = 2
    elif medial_pct > 20:
        position_score = 1
    else:
        position_score = 0

    # 3. CO-OCCURRENCE
    co_occurrence_count = 0
    for entry in instances:
        sentence = entry["full_sentence"]
        for validated_word in validated_words:
            if validated_word in sentence and validated_word != word:
                co_occurrence_count += 1
                break

    co_occurrence_pct = (
        100 * co_occurrence_count / len(instances) if len(instances) > 0 else 0
    )

    if co_occurrence_pct > 15:
        co_occurrence_score = 2
    elif co_occurrence_pct > 5:
        co_occurrence_score = 1
    else:
        co_occurrence_score = 0

    # Total (out of 6 for quick validation)
    total_score = morphology_score + position_score + co_occurrence_score

    return {
        "word": word,
        "frequency": len(instances),
        "compounds": compounds,
        "compound_count": len(compounds),
        "morphology_pct": morphology_pct,
        "morphology_score": morphology_score,
        "medial_pct": medial_pct,
        "position_score": position_score,
        "co_occurrence_pct": co_occurrence_pct,
        "co_occurrence_score": co_occurrence_score,
        "total_score": total_score,
        "max_score": 6,
    }


def main():
    print("=" * 80)
    print("PHASE 8: FINDING NEW MORPHOLOGICAL ROOTS")
    print("=" * 80)
    print("\nStrategy:")
    print("  A) Look for high-frequency morphological roots (like ok, she, che)")
    print("  C) Systematically test top 50 most frequent unexplained words")
    print("\nCriteria:")
    print("  - High frequency (>50 occurrences)")
    print("  - Short length (2-4 letters) - potential roots")
    print("  - Forms productive compounds (root + suffix)")
    print("  - NOT already validated")
    print("\n" + "=" * 80)

    # Load manuscript
    print("\nLoading Voynich manuscript...")
    voynich_path = "data/voynich/eva_transcription/voynich_eva_takahashi.txt"
    words_with_context = load_voynich_with_context(voynich_path)

    word_counts = Counter(entry["word"] for entry in words_with_context)
    print(f"Loaded {len(words_with_context):,} word instances")
    print(f"Unique words: {len(word_counts):,}")

    # Already validated terms
    validated_words = [
        # Nouns/roots
        "ok",
        "qok",
        "ot",
        "qot",
        "she",
        "shee",
        "cho",
        "dor",
        "sho",
        "keo",
        "teo",
        "cheo",
        # Function words
        "ar",
        "daiin",
        "dain",
        "y",
        "dair",
        "air",
        "sal",
        "qol",
        "ory",
        # Known morphological variants we've seen
        "che",  # We've seen this in compounds
    ]

    print(f"\nExcluding {len(validated_words)} already validated terms")

    # Get top 50 high-frequency words
    top_words = word_counts.most_common(100)

    # Filter for root candidates
    print("\nFiltering for root candidates:")
    print("  - Frequency > 50")
    print("  - Length 2-4 letters")
    print("  - Not already validated")

    candidates = []
    for word, count in top_words:
        if count > 50 and 2 <= len(word) <= 4 and word not in validated_words:
            candidates.append((word, count))

    print(f"\nFound {len(candidates)} candidates")

    # Quick validation scoring
    print("\nAnalyzing candidates...")
    print("(Looking for productive roots that form compounds)\n")

    results = []
    for word, count in candidates[:30]:  # Analyze top 30
        result = quick_validation(word, words_with_context, validated_words)
        if result:
            results.append(result)

    # Sort by total score
    results.sort(
        key=lambda x: (x["total_score"], x["compound_count"], x["frequency"]),
        reverse=True,
    )

    # Display results
    print("=" * 80)
    print("TOP ROOT CANDIDATES (Sorted by Score)")
    print("=" * 80)
    print(
        f"\n{'Rank':<5} {'Word':<8} {'Freq':<7} {'Score':<7} {'Compounds':<11} {'Morph%':<9} {'Sample Compounds'}"
    )
    print("-" * 80)

    for i, r in enumerate(results[:20], 1):
        sample_compounds = ", ".join(r["compounds"][:5])
        if len(r["compounds"]) > 5:
            sample_compounds += "..."

        score_str = f"{r['total_score']}/{r['max_score']}"

        print(
            f"{i:<5} {r['word']:<8} {r['frequency']:<7} {score_str:<7} {r['compound_count']:<11} {r['morphology_pct']:>6.1f}%  {sample_compounds}"
        )

    # Detailed analysis of top 10
    print("\n\n" + "=" * 80)
    print("DETAILED ANALYSIS: TOP 10 ROOT CANDIDATES")
    print("=" * 80)

    for i, r in enumerate(results[:10], 1):
        print(f"\n{'-' * 80}")
        print(f"{i}. {r['word'].upper()} (frequency: {r['frequency']:,})")
        print(f"{'-' * 80}")
        print(f"  Quick Validation Score: {r['total_score']}/6")
        print(
            f"  Morphology: {r['morphology_score']}/2 ({r['morphology_pct']:.1f}% forms compounds)"
        )
        print(f"  Position: {r['position_score']}/2 ({r['medial_pct']:.1f}% medial)")
        print(
            f"  Co-occurrence: {r['co_occurrence_score']}/2 ({r['co_occurrence_pct']:.1f}%)"
        )

        print(f"\n  Compound forms ({r['compound_count']} total):")
        for compound in r["compounds"][:10]:
            suffix = compound[len(r["word"]) :]
            print(f"    {compound} = {r['word']} + {suffix}")
        if r["compound_count"] > 10:
            print(f"    ... and {r['compound_count'] - 10} more")

        # Categorize by suffix
        suffix_counts = defaultdict(int)
        for compound in r["compounds"]:
            suffix = compound[len(r["word"]) :]
            # Get first suffix type
            if suffix.startswith("dy"):
                suffix_counts["dy (VERBAL)"] += 1
            elif (
                suffix.startswith("ain")
                or suffix.startswith("iin")
                or suffix.startswith("aiin")
            ):
                suffix_counts["ain/iin (DEF)"] += 1
            elif suffix.startswith("al") or suffix.startswith("ol"):
                suffix_counts["al/ol (LOC)"] += 1
            elif suffix.startswith("ar"):
                suffix_counts["ar (DIR)"] += 1
            elif suffix.startswith("or"):
                suffix_counts["or (INST)"] += 1
            elif suffix.startswith("y"):
                suffix_counts["y (?)"] += 1
            else:
                suffix_counts[f"{suffix} (?)"] += 1

        if suffix_counts:
            print(f"\n  Suffix distribution:")
            for suffix, count in sorted(
                suffix_counts.items(), key=lambda x: x[1], reverse=True
            ):
                print(f"    {suffix}: {count}")

    # Recommendations
    print("\n\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)

    high_scorers = [r for r in results if r["total_score"] >= 5]
    moderate_scorers = [r for r in results if 3 <= r["total_score"] < 5]

    print(f"\nHIGH PRIORITY (score ≥5/6): {len(high_scorers)} candidates")
    for r in high_scorers[:10]:
        print(
            f"  - {r['word']} ({r['frequency']:,} instances, {r['compound_count']} compounds, {r['total_score']}/6)"
        )

    print(f"\nMODERATE PRIORITY (score 3-4/6): {len(moderate_scorers)} candidates")
    for r in moderate_scorers[:5]:
        print(
            f"  - {r['word']} ({r['frequency']:,} instances, {r['compound_count']} compounds, {r['total_score']}/6)"
        )

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("\n1. Run FULL 10-point validation on top 5-10 candidates")
    print("2. Check for semantic patterns (section enrichment)")
    print("3. Test phonetic intuitions for meanings")
    print("4. Add validated roots to translation framework")
    print("\nTop candidates to investigate first:")
    for i, r in enumerate(results[:5], 1):
        print(
            f"  {i}. {r['word']} ({r['total_score']}/6, {r['compound_count']} compounds)"
        )


if __name__ == "__main__":
    main()
