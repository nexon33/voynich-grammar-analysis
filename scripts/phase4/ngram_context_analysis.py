#!/usr/bin/env python3
"""
N-gram Context Analysis: Infer word meanings from oak/oat context

Strategy: Oak/oat are VALIDATED anchors. What words consistently appear
before/after them? In recipes, we expect:
- Verbs: "prepare", "boil", "add", "mix"
- Quantities: "handful", "measure", "parts"
- Prepositions: "with", "in", "of"

If we find Voynich words that consistently appear in these positions,
we can infer their grammatical function even without phonetic matching.
"""

import json
from collections import Counter, defaultdict
from pathlib import Path


def load_voynich_text():
    """Load Voynich text as word list."""
    with open(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt",
        "r",
        encoding="utf-8",
    ) as f:
        return f.read().split()


def get_oak_oat_variants():
    """Get all oak/oat word variants."""
    oak_variants = {
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
    }

    oat_variants = {
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

    return oak_variants, oat_variants


def find_ngrams_around_anchors(words, anchor_variants, window_size=3):
    """
    Find words that appear before/after anchor words.

    Args:
        words: List of all words
        anchor_variants: Set of anchor word variants (oak or oat)
        window_size: How many words before/after to capture

    Returns:
        before_counts: Counter of words appearing before anchors
        after_counts: Counter of words appearing after anchors
        contexts: List of full context windows
    """

    before_counts = Counter()
    after_counts = Counter()
    contexts = []

    for i, word in enumerate(words):
        if word.lower() in anchor_variants:
            # Get context window
            before = words[max(0, i - window_size) : i]
            after = words[i + 1 : min(len(words), i + 1 + window_size)]

            # Count immediate neighbors
            if before:
                before_counts[before[-1]] += 1  # Word immediately before
            if after:
                after_counts[after[0]] += 1  # Word immediately after

            # Store full context
            contexts.append(
                {
                    "position": i,
                    "anchor": word,
                    "before": before,
                    "after": after,
                    "before_1": before[-1] if before else None,
                    "after_1": after[0] if after else None,
                }
            )

    return before_counts, after_counts, contexts


def analyze_positional_patterns(contexts):
    """Analyze patterns in word positions relative to anchors."""

    # Bigram patterns (anchor + next word)
    bigrams_after = Counter()
    bigrams_before = Counter()

    # Trigram patterns
    trigrams = Counter()

    for ctx in contexts:
        anchor = ctx["anchor"]

        # Bigrams
        if ctx["after_1"]:
            bigrams_after[(anchor, ctx["after_1"])] += 1
        if ctx["before_1"]:
            bigrams_before[(ctx["before_1"], anchor)] += 1

        # Trigrams (word before + anchor + word after)
        if ctx["before_1"] and ctx["after_1"]:
            trigrams[(ctx["before_1"], anchor, ctx["after_1"])] += 1

    return bigrams_before, bigrams_after, trigrams


def classify_by_grammatical_function(word_counts, min_freq=5):
    """
    Classify words by likely grammatical function based on frequency.

    High frequency in specific position = likely grammatical word
    Medium frequency = likely content word
    """

    classifications = {}

    for word, count in word_counts.items():
        if count >= 20:
            category = "high_frequency_grammatical"
            hypothesis = "Article, preposition, conjunction, or auxiliary"
        elif count >= 10:
            category = "medium_frequency"
            hypothesis = "Common verb, adjective, or noun"
        elif count >= min_freq:
            category = "low_frequency_content"
            hypothesis = "Specific action, quality, or noun"
        else:
            continue

        classifications[word] = {
            "category": category,
            "hypothesis": hypothesis,
            "frequency": count,
        }

    return classifications


def main():
    print("=" * 80)
    print("N-GRAM CONTEXT ANALYSIS")
    print("=" * 80)
    print("\nStrategy: Use oak/oat as validated anchors")
    print("Find words that consistently appear before/after them")
    print("Infer grammatical function from position and frequency")

    # Load data
    print("\nLoading Voynich text...")
    words = load_voynich_text()
    print(f"Total words: {len(words):,}")

    oak_variants, oat_variants = get_oak_oat_variants()
    print(f"Oak variants: {len(oak_variants)}")
    print(f"Oat variants: {len(oat_variants)}")

    # Analyze oak contexts
    print("\n" + "-" * 80)
    print("OAK CONTEXT ANALYSIS")
    print("-" * 80)

    oak_before, oak_after, oak_contexts = find_ngrams_around_anchors(
        words, oak_variants, window_size=3
    )

    print(f"\nOak instances found: {len(oak_contexts)}")
    print(f"Unique words before oak: {len(oak_before)}")
    print(f"Unique words after oak: {len(oak_after)}")

    print(f"\nTop 20 words BEFORE oak:")
    for word, count in oak_before.most_common(20):
        print(f"  {word:<15} {count:4}x")

    print(f"\nTop 20 words AFTER oak:")
    for word, count in oak_after.most_common(20):
        print(f"  {word:<15} {count:4}x")

    # Analyze oat contexts
    print("\n" + "-" * 80)
    print("OAT CONTEXT ANALYSIS")
    print("-" * 80)

    oat_before, oat_after, oat_contexts = find_ngrams_around_anchors(
        words, oat_variants, window_size=3
    )

    print(f"\nOat instances found: {len(oat_contexts)}")
    print(f"Unique words before oat: {len(oat_before)}")
    print(f"Unique words after oat: {len(oat_after)}")

    print(f"\nTop 20 words BEFORE oat:")
    for word, count in oat_before.most_common(20):
        print(f"  {word:<15} {count:4}x")

    print(f"\nTop 20 words AFTER oat:")
    for word, count in oat_after.most_common(20):
        print(f"  {word:<15} {count:4}x")

    # Find SHARED context words (appear with both oak AND oat)
    print("\n" + "=" * 80)
    print("SHARED CONTEXT WORDS (appear with both oak AND oat)")
    print("=" * 80)

    shared_before = set(oak_before.keys()) & set(oat_before.keys())
    shared_after = set(oak_after.keys()) & set(oat_after.keys())

    print(f"\nWords appearing BEFORE both oak and oat:")
    shared_before_counts = [(w, oak_before[w] + oat_before[w]) for w in shared_before]
    shared_before_counts.sort(key=lambda x: x[1], reverse=True)

    for word, total_count in shared_before_counts[:15]:
        oak_count = oak_before[word]
        oat_count = oat_before[word]
        print(f"  {word:<15} {total_count:4}x (oak:{oak_count:3}, oat:{oat_count:3})")

    print(f"\nWords appearing AFTER both oak and oat:")
    shared_after_counts = [(w, oak_after[w] + oat_after[w]) for w in shared_after]
    shared_after_counts.sort(key=lambda x: x[1], reverse=True)

    for word, total_count in shared_after_counts[:15]:
        oak_count = oak_after[word]
        oat_count = oat_after[word]
        print(f"  {word:<15} {total_count:4}x (oak:{oak_count:3}, oat:{oat_count:3})")

    # Pattern analysis
    print("\n" + "=" * 80)
    print("PATTERN ANALYSIS")
    print("=" * 80)

    oak_bigrams_before, oak_bigrams_after, oak_trigrams = analyze_positional_patterns(
        oak_contexts
    )

    print(f"\nTop 15 patterns: [word] + oak:")
    for (w1, w2), count in oak_bigrams_before.most_common(15):
        print(f"  {w1:<15} + {w2:<15} = {count:3}x")

    print(f"\nTop 15 patterns: oak + [word]:")
    for (w1, w2), count in oak_bigrams_after.most_common(15):
        print(f"  {w1:<15} + {w2:<15} = {count:3}x")

    # Classify context words by likely function
    print("\n" + "=" * 80)
    print("GRAMMATICAL FUNCTION INFERENCE")
    print("=" * 80)

    # Combine before/after counts
    all_context_words = Counter()
    all_context_words.update(oak_before)
    all_context_words.update(oak_after)
    all_context_words.update(oat_before)
    all_context_words.update(oat_after)

    classifications = classify_by_grammatical_function(all_context_words, min_freq=5)

    print(f"\nHIGH-FREQUENCY words (likely grammatical):")
    high_freq = {
        w: c
        for w, c in classifications.items()
        if c["category"] == "high_frequency_grammatical"
    }
    for word in sorted(
        high_freq.keys(), key=lambda w: high_freq[w]["frequency"], reverse=True
    )[:15]:
        print(
            f"  {word:<15} {high_freq[word]['frequency']:4}x - {high_freq[word]['hypothesis']}"
        )

    print(f"\nMEDIUM-FREQUENCY words (likely content):")
    med_freq = {
        w: c for w, c in classifications.items() if c["category"] == "medium_frequency"
    }
    for word in sorted(
        med_freq.keys(), key=lambda w: med_freq[w]["frequency"], reverse=True
    )[:15]:
        print(
            f"  {word:<15} {med_freq[word]['frequency']:4}x - {med_freq[word]['hypothesis']}"
        )

    # Save results
    output = {
        "oak_analysis": {
            "total_instances": len(oak_contexts),
            "before_counts": dict(oak_before.most_common(50)),
            "after_counts": dict(oak_after.most_common(50)),
            "top_bigrams_before": [
                (list(k), v) for k, v in oak_bigrams_before.most_common(30)
            ],
            "top_bigrams_after": [
                (list(k), v) for k, v in oak_bigrams_after.most_common(30)
            ],
        },
        "oat_analysis": {
            "total_instances": len(oat_contexts),
            "before_counts": dict(oat_before.most_common(50)),
            "after_counts": dict(oat_after.most_common(50)),
        },
        "shared_context": {
            "before": [(w, oak_before[w], oat_before[w]) for w in shared_before],
            "after": [(w, oak_after[w], oat_after[w]) for w in shared_after],
        },
        "classifications": classifications,
    }

    output_path = Path("results/phase4/ngram_context_analysis.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\n\nAnalysis saved to: {output_path}")

    print("\n" + "=" * 80)
    print("CONCLUSIONS")
    print("=" * 80)
    print("\n1. High-frequency context words are likely GRAMMATICAL")
    print(
        "   → Articles, prepositions, conjunctions appearing before/after ingredients"
    )

    print("\n2. Words appearing with BOTH oak and oat likely have general function")
    print("   → Not specific to one ingredient, but part of recipe structure")

    print("\n3. Next step: Manually examine high-frequency contexts")
    print("   → Check if they match expected recipe patterns (verbs, quantities, etc.)")


if __name__ == "__main__":
    main()
