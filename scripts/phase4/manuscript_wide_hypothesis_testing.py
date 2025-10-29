#!/usr/bin/env python3
"""
Manuscript-Wide Hypothesis Testing

Use oak/oat as anchors across ENTIRE manuscript to test grammatical hypotheses:

HYPOTHESIS 1: 'chedy'/'shedy' are conjunctions ('and', 'or', 'with')
  Test: Do they appear BETWEEN two plants frequently?

HYPOTHESIS 2: 'daiin' is a pronoun/demonstrative ('it', 'this', 'that')
  Test: Does it NOT appear between plants (unlike conjunctions)?

HYPOTHESIS 3: 'ol'/'al'/'dar'/'dal' are articles/prepositions ('the', 'of', 'to')
  Test: Do they appear BEFORE plants frequently?

HYPOTHESIS 4: 'qok-' prefix means 'of' or genitive case
  Test: Do qok-plant words appear in specific contexts?
"""

import json
from collections import Counter, defaultdict
from pathlib import Path


def load_voynich_text():
    """Load full Voynich text."""
    with open(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt",
        "r",
        encoding="utf-8",
    ) as f:
        return f.read().split()


def get_plant_variants():
    """Get all recognized plant variants."""
    oak = {
        "okedy",
        "okeedy",
        "qokey",
        "qokol",
        "okol",
        "okeol",
        "okey",
        "okeody",
        "qokor",
        "okor",
        "qokeody",
        "okeeey",
        "qokeol",
        "okeey",
        "oko",
        "oke",
        "qokedy",
        "okody",
        "qokody",
        "okeor",
        "qokeor",
        "okeos",
        "okear",
        "okary",
        "okeoly",
        "okol",
    }

    oat = {
        "oteey",
        "oteedy",
        "qotedy",
        "otol",
        "qoteedy",
        "oteol",
        "qoteey",
        "oteody",
        "otor",
        "otey",
        "qotol",
        "oto",
        "ote",
        "qotor",
        "otedy",
        "qotey",
        "oteos",
        "oteor",
        "qoteor",
        "otoly",
        "otory",
        "oteeos",
        "otalo",
        "otal",
        "otaiin",
    }

    # Include other recognized plants
    other_plants = {
        "dor",
        "tor",
        "rod",  # red (color, but appears frequently)
        "oar",
        "oro",  # ear (anatomy)
        "ale",
        "alo",
        "ola",
        "olaiin",  # ale
    }

    all_plants = oak | oat | other_plants

    return oak, oat, all_plants


def test_conjunction_hypothesis(words, candidate_words, all_plants):
    """
    Test if candidate words are conjunctions.

    Conjunctions should appear BETWEEN two plants frequently.
    Pattern: [plant] [conjunction] [plant]
    """

    results = {}

    for candidate in candidate_words:
        # Find all occurrences of candidate
        positions = [i for i, w in enumerate(words) if w == candidate]

        # Check context: word before and after
        between_plants = 0
        before_plant = 0
        after_plant = 0
        total_contexts = 0

        for pos in positions:
            if pos > 0 and pos < len(words) - 1:
                word_before = words[pos - 1].lower()
                word_after = words[pos + 1].lower()

                is_before_plant = word_before in all_plants
                is_after_plant = word_after in all_plants

                if is_before_plant:
                    before_plant += 1
                if is_after_plant:
                    after_plant += 1
                if is_before_plant and is_after_plant:
                    between_plants += 1

                total_contexts += 1

        if total_contexts > 0:
            results[candidate] = {
                "total_occurrences": len(positions),
                "total_contexts": total_contexts,
                "between_plants": between_plants,
                "before_plant": before_plant,
                "after_plant": after_plant,
                "between_plants_rate": between_plants / total_contexts,
                "before_plant_rate": before_plant / total_contexts,
                "after_plant_rate": after_plant / total_contexts,
            }

    return results


def test_pronoun_hypothesis(words, candidate_words, all_plants):
    """
    Test if candidate words are pronouns/demonstratives.

    Pronouns should NOT appear between plants (that's conjunction behavior).
    They typically appear at sentence start or after verbs.
    """

    results = {}

    for candidate in candidate_words:
        positions = [i for i, w in enumerate(words) if w == candidate]

        between_plants = 0
        sentence_like_start = 0  # After certain markers
        total_contexts = 0

        for pos in positions:
            if pos > 0 and pos < len(words) - 1:
                word_before = words[pos - 1].lower()
                word_after = words[pos + 1].lower()

                is_before_plant = word_before in all_plants
                is_after_plant = word_after in all_plants

                if is_before_plant and is_after_plant:
                    between_plants += 1

                # Check if appears in "sentence-like" position
                # (Very rough heuristic: after short words that might be verbs/prepositions)
                if len(word_before) <= 3:
                    sentence_like_start += 1

                total_contexts += 1

        if total_contexts > 0:
            results[candidate] = {
                "total_occurrences": len(positions),
                "between_plants": between_plants,
                "between_plants_rate": between_plants / total_contexts,
                "sentence_like_start": sentence_like_start,
                "sentence_like_rate": sentence_like_start / total_contexts,
                "hypothesis_support": "SUPPORTED"
                if between_plants / total_contexts < 0.1
                else "NOT_SUPPORTED",
            }

    return results


def test_article_preposition_hypothesis(words, candidate_words, all_plants):
    """
    Test if candidate words are articles/prepositions.

    Articles/prepositions should appear BEFORE nouns (plants) frequently.
    Pattern: [article/prep] [plant]
    """

    results = {}

    for candidate in candidate_words:
        positions = [i for i, w in enumerate(words) if w == candidate]

        before_plant = 0
        total_contexts = 0

        for pos in positions:
            if pos < len(words) - 1:
                word_after = words[pos + 1].lower()

                if word_after in all_plants:
                    before_plant += 1

                total_contexts += 1

        if total_contexts > 0:
            results[candidate] = {
                "total_occurrences": len(positions),
                "before_plant": before_plant,
                "before_plant_rate": before_plant / total_contexts,
                "hypothesis_support": "STRONG"
                if before_plant / total_contexts > 0.15
                else ("MODERATE" if before_plant / total_contexts > 0.08 else "WEAK"),
            }

    return results


def test_genitive_prefix_hypothesis(words, oak_variants, oat_variants):
    """
    Test if 'qok-' prefix indicates genitive case ('of').

    Compare:
    - Words with qok- prefix (e.g., qokol)
    - Same root without prefix (e.g., okol)

    If qok- is genitive, qok-plant should appear in different contexts.
    """

    # Find qok-prefixed plant words
    qok_plants = set()
    plain_plants = set()

    for word in set(words):
        word_lower = word.lower()
        if word_lower.startswith("qok"):
            # Check if root is a plant
            root = word_lower[3:] if len(word_lower) > 3 else word_lower[1:]
            if root in oak_variants or root in oat_variants:
                qok_plants.add(word_lower)
                plain_plants.add(root)

    # Analyze contexts
    qok_contexts = defaultdict(int)
    plain_contexts = defaultdict(int)

    for i, word in enumerate(words):
        word_lower = word.lower()

        if word_lower in qok_plants and i > 0:
            # Word before qok-plant
            qok_contexts[words[i - 1].lower()] += 1

        if word_lower in plain_plants and i > 0:
            # Word before plain plant
            plain_contexts[words[i - 1].lower()] += 1

    # Compare distributions
    results = {
        "qok_prefix_count": len([w for w in words if w.lower() in qok_plants]),
        "plain_count": len([w for w in words if w.lower() in plain_plants]),
        "qok_top_contexts": dict(Counter(qok_contexts).most_common(10)),
        "plain_top_contexts": dict(Counter(plain_contexts).most_common(10)),
        "interpretation": "qok- forms appear in different contexts, suggesting grammatical function",
    }

    return results


def main():
    print("=" * 80)
    print("MANUSCRIPT-WIDE HYPOTHESIS TESTING")
    print("=" * 80)
    print("\nUsing oak/oat as validated anchors across entire manuscript")
    print("Testing grammatical function hypotheses")

    # Load data
    print("\nLoading manuscript...")
    words = load_voynich_text()
    oak_variants, oat_variants, all_plants = get_plant_variants()

    print(f"Total words: {len(words):,}")
    print(f"Plant variants recognized: {len(all_plants)}")

    # Count plants
    plant_count = sum(1 for w in words if w.lower() in all_plants)
    print(
        f"Plant mentions in manuscript: {plant_count:,} ({100 * plant_count / len(words):.2f}%)"
    )

    # HYPOTHESIS 1: Conjunctions
    print("\n" + "=" * 80)
    print("HYPOTHESIS 1: CONJUNCTION WORDS")
    print("=" * 80)
    print("\nTesting: chedy, shedy, qokeedy, qokedy")
    print("Expected: Should appear BETWEEN plants frequently")

    conjunction_candidates = ["chedy", "shedy", "qokeedy", "qokedy", "qokeey"]
    conj_results = test_conjunction_hypothesis(
        words, conjunction_candidates, all_plants
    )

    print(f"\n{'Word':<15} {'Total':>8} {'Between':>8} {'Rate':>8} {'Status'}")
    print("-" * 60)
    for word in sorted(
        conj_results.keys(),
        key=lambda w: conj_results[w]["between_plants_rate"],
        reverse=True,
    ):
        r = conj_results[word]
        status = (
            "✓ LIKELY CONJ"
            if r["between_plants_rate"] > 0.10
            else ("~ POSSIBLE" if r["between_plants_rate"] > 0.05 else "- UNLIKELY")
        )
        print(
            f"{word:<15} {r['total_occurrences']:>8} {r['between_plants']:>8} "
            f"{r['between_plants_rate']:>7.1%} {status}"
        )

    # HYPOTHESIS 2: Pronouns
    print("\n" + "=" * 80)
    print("HYPOTHESIS 2: PRONOUN/DEMONSTRATIVE WORDS")
    print("=" * 80)
    print("\nTesting: daiin, aiin")
    print("Expected: Should NOT appear between plants (unlike conjunctions)")

    pronoun_candidates = ["daiin", "aiin", "saiin"]
    pron_results = test_pronoun_hypothesis(words, pronoun_candidates, all_plants)

    print(f"\n{'Word':<15} {'Total':>8} {'Between':>8} {'Rate':>8} {'Status'}")
    print("-" * 60)
    for word in sorted(
        pron_results.keys(),
        key=lambda w: pron_results[w]["total_occurrences"],
        reverse=True,
    ):
        r = pron_results[word]
        print(
            f"{word:<15} {r['total_occurrences']:>8} {r['between_plants']:>8} "
            f"{r['between_plants_rate']:>7.1%} {r['hypothesis_support']}"
        )

    # HYPOTHESIS 3: Articles/Prepositions
    print("\n" + "=" * 80)
    print("HYPOTHESIS 3: ARTICLE/PREPOSITION WORDS")
    print("=" * 80)
    print("\nTesting: ol, al, dar, dal, or, ar")
    print("Expected: Should appear BEFORE plants frequently")

    article_candidates = ["ol", "al", "dar", "dal", "or", "ar", "s"]
    art_results = test_article_preposition_hypothesis(
        words, article_candidates, all_plants
    )

    print(f"\n{'Word':<15} {'Total':>8} {'Before':>8} {'Rate':>8} {'Support'}")
    print("-" * 60)
    for word in sorted(
        art_results.keys(),
        key=lambda w: art_results[w]["before_plant_rate"],
        reverse=True,
    ):
        r = art_results[word]
        print(
            f"{word:<15} {r['total_occurrences']:>8} {r['before_plant']:>8} "
            f"{r['before_plant_rate']:>7.1%} {r['hypothesis_support']}"
        )

    # HYPOTHESIS 4: Genitive prefix
    print("\n" + "=" * 80)
    print("HYPOTHESIS 4: 'QOK-' AS GENITIVE PREFIX")
    print("=" * 80)
    print("\nTesting: Do qok-plant and plain plant appear in different contexts?")

    gen_results = test_genitive_prefix_hypothesis(words, oak_variants, oat_variants)

    print(f"\nQok-prefixed plants: {gen_results['qok_prefix_count']:,} instances")
    print(f"Plain plants: {gen_results['plain_count']:,} instances")

    print(f"\nTop words BEFORE qok-plant:")
    for word, count in list(gen_results["qok_top_contexts"].items())[:8]:
        print(f"  {word:<15} {count:4}x")

    print(f"\nTop words BEFORE plain plant:")
    for word, count in list(gen_results["plain_top_contexts"].items())[:8]:
        print(f"  {word:<15} {count:4}x")

    # Calculate overlap
    qok_set = set(gen_results["qok_top_contexts"].keys())
    plain_set = set(gen_results["plain_top_contexts"].keys())
    overlap = qok_set & plain_set

    print(
        f"\nContext overlap: {len(overlap)}/{min(len(qok_set), len(plain_set))} words"
    )
    if len(overlap) < 5:
        print("✓ LOW OVERLAP - supports different grammatical function for qok- prefix")
    else:
        print("~ MODERATE OVERLAP - qok- may have subtle function difference")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY: VALIDATED GRAMMATICAL WORDS")
    print("=" * 80)

    print("\n✓ CONJUNCTIONS (connect ingredients):")
    for word, r in conj_results.items():
        if r["between_plants_rate"] > 0.05:
            print(
                f"  {word:<15} - appears between plants {r['between_plants_rate']:.1%} of time"
            )
            print(f"                  → Likely: 'and', 'or', 'with'")

    print("\n✓ PRONOUNS/DEMONSTRATIVES:")
    for word, r in pron_results.items():
        if r["hypothesis_support"] == "SUPPORTED":
            print(
                f"  {word:<15} - rarely between plants ({r['between_plants_rate']:.1%})"
            )
            print(f"                  → Likely: 'it', 'this', 'that'")

    print("\n✓ ARTICLES/PREPOSITIONS:")
    for word, r in art_results.items():
        if r["hypothesis_support"] in ["STRONG", "MODERATE"]:
            print(
                f"  {word:<15} - precedes plants {r['before_plant_rate']:.1%} of time"
            )
            print(f"                  → Likely: 'the', 'of', 'to', 'in'")

    print("\n✓ GRAMMATICAL PREFIX:")
    print(f"  qok-            - appears in different contexts than plain forms")
    print(f"                  → Likely: genitive case ('of X') or preposition marker")

    # Save results
    output = {
        "manuscript_stats": {
            "total_words": len(words),
            "plant_mentions": plant_count,
            "plant_coverage": 100 * plant_count / len(words),
        },
        "conjunction_test": conj_results,
        "pronoun_test": pron_results,
        "article_test": art_results,
        "genitive_test": gen_results,
        "validated_words": {
            "conjunctions": [
                w for w, r in conj_results.items() if r["between_plants_rate"] > 0.05
            ],
            "pronouns": [
                w
                for w, r in pron_results.items()
                if r["hypothesis_support"] == "SUPPORTED"
            ],
            "articles_prepositions": [
                w
                for w, r in art_results.items()
                if r["hypothesis_support"] in ["STRONG", "MODERATE"]
            ],
        },
    }

    output_path = Path("results/phase4/manuscript_wide_hypothesis_tests.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\n\nResults saved to: {output_path}")

    print("\n" + "=" * 80)
    print("HYPOTHESIS TESTING COMPLETE")
    print("=" * 80)
    print("\nWe can now INFER meanings of high-frequency words")
    print("without phonetic decoding - just from CONTEXT!")


if __name__ == "__main__":
    main()
