"""
Second-Order Frequency Validation
==================================

We've validated that oak/oat are real words (enriched 3x in baths, p<0.001).
Now use them as anchors to validate OTHER words through association patterns.

Second-order validation concept:
- If word X consistently appears with validated words (oak/oat/verbs/pronouns)
- And X shows similar distribution patterns
- Then X is likely REAL and not cipher noise

This is like using a known molecule to find related compounds through
chromatography - we look for co-occurrence and distribution similarity.

Validation methods:
1. Co-occurrence frequency: Does X appear near validated words more than random?
2. Distribution correlation: Does X appear in same sections as validated words?
3. Morphological consistency: Does X follow same affix patterns?
4. Functional consistency: Does X behave like other words of same class?
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
import math


def load_manuscript():
    """Load manuscript as word list"""
    transcription_path = Path(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt"
    )

    with open(transcription_path, "r", encoding="utf-8") as f:
        text = f.read()

    words = text.lower().split()
    return words


def load_validated_anchors():
    """Load all validated words to use as anchors"""

    # Load plant variants
    compounds_path = Path("results/phase4/compound_and_partial_matches.json")
    with open(compounds_path, "r") as f:
        compounds = json.load(f)

    plants = set()
    for match in compounds["partial_matches"]:
        if "oak" in match["meaning"] or "oat" in match["meaning"]:
            plants.add(match["voynich_word"])

    pronouns = {"daiin", "aiin", "saiin"}
    verbs = {"chedy", "shedy", "qokedy", "qokeedy", "qokeey"}

    all_anchors = plants | pronouns | verbs

    return {"plants": plants, "pronouns": pronouns, "verbs": verbs, "all": all_anchors}


def calculate_cooccurrence_scores(words, anchors, window_size=5):
    """
    Calculate how often each word appears near validated anchors

    Returns: {word: cooccurrence_score}
    Score = (times near anchors) / (total occurrences)
    """
    word_freq = Counter(words)
    near_anchor_freq = Counter()

    # Find all words within window of anchors
    for i, word in enumerate(words):
        if word in anchors:
            # Get surrounding words
            start = max(0, i - window_size)
            end = min(len(words), i + window_size + 1)

            for j in range(start, end):
                if j != i and words[j] not in anchors:  # Don't count anchors themselves
                    near_anchor_freq[words[j]] += 1

    # Calculate scores
    cooccurrence_scores = {}
    for word, near_count in near_anchor_freq.items():
        total_count = word_freq[word]
        score = near_count / total_count if total_count > 0 else 0

        cooccurrence_scores[word] = {
            "score": score,
            "near_anchor_count": near_count,
            "total_count": total_count,
            "expected_near": total_count
            * (len(anchors) / len(words))
            * (window_size * 2),
        }

    return cooccurrence_scores


def calculate_distribution_correlation(words, anchors, word_candidates):
    """
    Calculate correlation between candidate word distributions and anchor distributions

    Uses Pearson correlation coefficient on section distributions
    """
    sections = {
        "herbal": (0, 20000),
        "biological": (20000, 25000),
        "pharmaceutical": (25000, 32000),
        "recipes": (32000, 37187),
    }

    # Get anchor distribution
    anchor_dist = {s: 0 for s in sections}
    for i, word in enumerate(words):
        if word in anchors:
            for section_name, (start, end) in sections.items():
                if start <= i < end:
                    anchor_dist[section_name] += 1
                    break

    # Normalize anchor distribution
    anchor_total = sum(anchor_dist.values())
    anchor_dist = {s: count / anchor_total for s, count in anchor_dist.items()}

    # Calculate correlation for each candidate
    correlations = {}

    for candidate in word_candidates:
        cand_dist = {s: 0 for s in sections}

        for i, word in enumerate(words):
            if word == candidate:
                for section_name, (start, end) in sections.items():
                    if start <= i < end:
                        cand_dist[section_name] += 1
                        break

        # Normalize
        cand_total = sum(cand_dist.values())
        if cand_total == 0:
            continue

        cand_dist = {s: count / cand_total for s, count in cand_dist.items()}

        # Pearson correlation
        anchor_vals = [anchor_dist[s] for s in sections]
        cand_vals = [cand_dist[s] for s in sections]

        correlation = pearson_correlation(anchor_vals, cand_vals)

        correlations[candidate] = {
            "correlation": correlation,
            "distribution": cand_dist,
            "total_count": cand_total,
        }

    return correlations, anchor_dist


def pearson_correlation(x, y):
    """Calculate Pearson correlation coefficient"""
    n = len(x)
    if n != len(y):
        return 0

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))

    sum_sq_x = sum((x[i] - mean_x) ** 2 for i in range(n))
    sum_sq_y = sum((y[i] - mean_y) ** 2 for i in range(n))

    denominator = math.sqrt(sum_sq_x * sum_sq_y)

    if denominator == 0:
        return 0

    return numerator / denominator


def test_morphological_consistency(word, known_morphemes):
    """
    Test if word follows known morphological patterns
    """
    suffixes = [
        "y",
        "l",
        "dy",
        "ey",
        "r",
        "n",
        "ol",
        "al",
        "ar",
        "or",
        "in",
        "ed",
        "edy",
        "eey",
    ]
    prefixes = ["qok", "q", "d", "s", "t", "y"]

    score = 0
    matched_affixes = []

    # Check prefixes
    for prefix in sorted(prefixes, key=len, reverse=True):
        if word.startswith(prefix) and len(word) > len(prefix):
            score += 0.3
            matched_affixes.append(f"{prefix}-")
            word = word[len(prefix) :]
            break

    # Check suffixes
    for suffix in sorted(suffixes, key=len, reverse=True):
        if word.endswith(suffix) and len(word) > len(suffix):
            score += 0.3
            matched_affixes.append(f"-{suffix}")
            word = word[: -len(suffix)]
            break

    # Remaining root should be reasonable length
    if 2 <= len(word) <= 6:
        score += 0.4

    return {"score": min(score, 1.0), "affixes": matched_affixes, "root": word}


def validate_candidates(words, anchors, min_freq=20):
    """
    Main validation pipeline: combine all validation methods
    """
    print("Calculating co-occurrence scores...")
    cooccurrence_scores = calculate_cooccurrence_scores(words, anchors["all"])

    # Get candidate words (frequent but not already validated)
    word_freq = Counter(words)
    candidates = [
        w for w, f in word_freq.items() if f >= min_freq and w not in anchors["all"]
    ]

    print(f"Testing {len(candidates)} candidate words...")

    # Calculate distribution correlations
    print("Calculating distribution correlations...")
    correlations, anchor_dist = calculate_distribution_correlation(
        words, anchors["all"], candidates
    )

    # Test morphological consistency
    print("Testing morphological consistency...")
    morphological_scores = {}
    for candidate in candidates:
        morphological_scores[candidate] = test_morphological_consistency(candidate, {})

    # Combine scores
    validated = {}

    for candidate in candidates:
        if candidate not in cooccurrence_scores or candidate not in correlations:
            continue

        cooc = cooccurrence_scores[candidate]
        corr = correlations[candidate]
        morph = morphological_scores[candidate]

        # Weighted composite score
        composite_score = (
            cooc["score"] * 0.4  # Co-occurrence weight
            + (corr["correlation"] + 1)
            / 2
            * 0.3  # Correlation weight (normalize -1 to 1 → 0 to 1)
            + morph["score"] * 0.3  # Morphological weight
        )

        validated[candidate] = {
            "composite_score": composite_score,
            "cooccurrence_score": cooc["score"],
            "near_anchor_count": cooc["near_anchor_count"],
            "total_count": cooc["total_count"],
            "distribution_correlation": corr["correlation"],
            "distribution": corr["distribution"],
            "morphological_score": morph["score"],
            "morphological_affixes": morph["affixes"],
            "morphological_root": morph["root"],
        }

    return validated, anchor_dist


def categorize_validated_words(validated, anchors):
    """
    Try to categorize validated words by comparing to known categories
    """
    # Load morphological data
    morph_path = Path("results/phase4/morphological_decomposition.json")
    with open(morph_path, "r") as f:
        morph_data = json.load(f)

    categorized = {
        "likely_plants": [],
        "likely_verbs": [],
        "likely_function_words": [],
        "unknown_category": [],
    }

    for word, data in validated.items():
        root = data["morphological_root"]

        # Check if root matches known plant roots
        if root in ["ok", "ot", "oke", "ote", "oko", "oto"] or any(
            r in root for r in ["ok", "ot"]
        ):
            categorized["likely_plants"].append(
                {
                    "word": word,
                    "score": data["composite_score"],
                    "reason": "Plant root detected",
                }
            )
        # Check if has verb-like suffixes
        elif "-edy" in " ".join(data["morphological_affixes"]) or "-dy" in " ".join(
            data["morphological_affixes"]
        ):
            categorized["likely_verbs"].append(
                {
                    "word": word,
                    "score": data["composite_score"],
                    "reason": "Verbal suffix detected",
                }
            )
        # Check if short and frequent (function word pattern)
        elif len(word) <= 3 and data["total_count"] > 100:
            categorized["likely_function_words"].append(
                {
                    "word": word,
                    "score": data["composite_score"],
                    "reason": "Short, high-frequency",
                }
            )
        else:
            categorized["unknown_category"].append(
                {
                    "word": word,
                    "score": data["composite_score"],
                    "reason": "No clear category match",
                }
            )

    # Sort each category by score
    for category in categorized:
        categorized[category] = sorted(
            categorized[category], key=lambda x: x["score"], reverse=True
        )

    return categorized


def main():
    print("=" * 80)
    print("SECOND-ORDER FREQUENCY VALIDATION")
    print("=" * 80)
    print()
    print("Using validated anchors (plants, pronouns, verbs) to validate new words")
    print("through co-occurrence, distribution, and morphological consistency")
    print()

    # Load data
    print("Loading manuscript...")
    words = load_manuscript()
    print(f"Total words: {len(words):,}")

    anchors = load_validated_anchors()
    print(f"Validated anchors: {len(anchors['all'])} words")
    print(f"  Plants: {len(anchors['plants'])}")
    print(f"  Pronouns: {len(anchors['pronouns'])}")
    print(f"  Verbs: {len(anchors['verbs'])}")
    print()

    # Validate candidates
    print("=" * 80)
    print("VALIDATION PIPELINE")
    print("=" * 80)
    print()

    validated, anchor_dist = validate_candidates(words, anchors, min_freq=20)

    print(f"Validated {len(validated)} candidate words")
    print()

    # Show anchor distribution baseline
    print("Anchor distribution baseline:")
    for section, prop in anchor_dist.items():
        print(f"  {section}: {prop * 100:.1f}%")
    print()

    # Show top validated words
    print("=" * 80)
    print("TOP 30 VALIDATED WORDS (by composite score)")
    print("=" * 80)
    print()
    print(
        f"{'Word':<15} {'Score':<8} {'Cooc':<8} {'Corr':<8} {'Morph':<8} {'Freq':<8} {'Root':<10}"
    )
    print("-" * 85)

    sorted_validated = sorted(
        validated.items(), key=lambda x: x[1]["composite_score"], reverse=True
    )

    for word, data in sorted_validated[:30]:
        print(
            f"{word:<15} {data['composite_score']:<8.3f} {data['cooccurrence_score']:<8.3f} "
            f"{data['distribution_correlation']:<8.3f} {data['morphological_score']:<8.3f} "
            f"{data['total_count']:<8} {data['morphological_root']:<10}"
        )

    print()

    # Categorize
    print("=" * 80)
    print("CATEGORIZED VALIDATED WORDS")
    print("=" * 80)
    print()

    categorized = categorize_validated_words(validated, anchors)

    for category, words_list in categorized.items():
        if words_list:
            print(f"\n{category.upper().replace('_', ' ')} ({len(words_list)} words):")
            for item in words_list[:10]:
                print(
                    f"  {item['word']:<15} (score: {item['score']:.3f}) - {item['reason']}"
                )

    print()

    # Statistical summary
    print("=" * 80)
    print("VALIDATION STATISTICS")
    print("=" * 80)
    print()

    high_confidence = [w for w, d in validated.items() if d["composite_score"] >= 0.6]
    medium_confidence = [
        w for w, d in validated.items() if 0.4 <= d["composite_score"] < 0.6
    ]
    low_confidence = [w for w, d in validated.items() if d["composite_score"] < 0.4]

    print(f"High confidence (score ≥ 0.6): {len(high_confidence)} words")
    print(f"Medium confidence (0.4-0.6): {len(medium_confidence)} words")
    print(f"Low confidence (< 0.4): {len(low_confidence)} words")
    print()

    # Calculate coverage
    total_instances = sum(validated[w]["total_count"] for w in high_confidence)
    manuscript_coverage = (total_instances / len(words)) * 100

    print(f"High-confidence word instances: {total_instances:,}")
    print(f"Manuscript coverage: {manuscript_coverage:.2f}%")
    print()

    # Validation quality metrics
    avg_cooc = sum(d["cooccurrence_score"] for d in validated.values()) / len(validated)
    avg_corr = sum(d["distribution_correlation"] for d in validated.values()) / len(
        validated
    )
    avg_morph = sum(d["morphological_score"] for d in validated.values()) / len(
        validated
    )

    print("Average validation scores:")
    print(f"  Co-occurrence: {avg_cooc:.3f}")
    print(f"  Distribution correlation: {avg_corr:.3f}")
    print(f"  Morphological consistency: {avg_morph:.3f}")
    print()

    # Cross-validation check
    print("=" * 80)
    print("CROSS-VALIDATION CHECK")
    print("=" * 80)
    print("Testing if known validated words would score high (should be YES)")
    print()

    # Check a few known good words
    test_words = ["okedy", "otedy", "chedy", "daiin"]
    for test_word in test_words:
        if test_word in validated:
            score = validated[test_word]["composite_score"]
            print(f"  {test_word}: {score:.3f} {'✓' if score > 0.5 else '✗'}")

    print()

    # Save results
    results = {
        "anchor_distribution": anchor_dist,
        "validated_words": {
            word: {
                "composite_score": data["composite_score"],
                "cooccurrence_score": data["cooccurrence_score"],
                "near_anchor_count": data["near_anchor_count"],
                "total_count": data["total_count"],
                "distribution_correlation": data["distribution_correlation"],
                "distribution": data["distribution"],
                "morphological_score": data["morphological_score"],
                "morphological_affixes": data["morphological_affixes"],
                "morphological_root": data["morphological_root"],
            }
            for word, data in sorted_validated[:100]  # Top 100
        },
        "categorized": categorized,
        "statistics": {
            "total_candidates": len(validated),
            "high_confidence": len(high_confidence),
            "medium_confidence": len(medium_confidence),
            "low_confidence": len(low_confidence),
            "high_confidence_coverage": manuscript_coverage,
            "avg_cooccurrence": avg_cooc,
            "avg_correlation": avg_corr,
            "avg_morphological": avg_morph,
        },
    }

    output_path = Path("results/phase4/second_order_validation.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {output_path}")
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Validated {len(high_confidence)} high-confidence words")
    print(f"Coverage: {manuscript_coverage:.2f}% of manuscript")
    print(f"These words consistently appear near validated anchors,")
    print(f"show similar distribution patterns, and follow morphological rules")


if __name__ == "__main__":
    main()
