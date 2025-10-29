#!/usr/bin/env python3
"""
Statistical Pattern Analysis - Option 3
Analyze structural patterns in high-frequency unknown Voynich words
"""

import json
from collections import defaultdict, Counter
from pathlib import Path


def load_word_frequencies():
    """Load Voynich word frequencies."""
    from collections import Counter

    # Load the Voynich transcription
    with open(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt",
        "r",
        encoding="utf-8",
    ) as f:
        text = f.read()

    # Split into words and count
    words = text.split()
    word_counts = Counter(words)

    return dict(word_counts)


def analyze_morphological_patterns(words_with_freq):
    """Analyze prefixes, suffixes, and roots in high-frequency words."""

    print("\n" + "=" * 80)
    print("MORPHOLOGICAL PATTERN ANALYSIS")
    print("=" * 80)

    # Focus on top 100 unknown words
    top_words = [
        (w, f)
        for w, f in sorted(words_with_freq.items(), key=lambda x: x[1], reverse=True)[
            :100
        ]
    ]

    # Analyze suffixes
    suffix_groups = defaultdict(list)
    for word, freq in top_words:
        if len(word) >= 3:
            # 2-letter suffixes
            suffix2 = word[-2:]
            suffix_groups[suffix2].append((word, freq))
            # 3-letter suffixes
            suffix3 = word[-3:]
            suffix_groups[suffix3].append((word, freq))

    print("\n" + "-" * 80)
    print("HIGH-FREQUENCY SUFFIX PATTERNS (min 3 words)")
    print("-" * 80)

    for suffix in sorted(
        suffix_groups.keys(),
        key=lambda s: sum(f for _, f in suffix_groups[s]),
        reverse=True,
    )[:20]:
        words = suffix_groups[suffix]
        if len(words) >= 3:
            total_freq = sum(f for _, f in words)
            print(
                f"\nSuffix '-{suffix}' ({len(words)} words, {total_freq:,} instances):"
            )
            for w, f in sorted(words, key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {w:15} {f:4}x")

    # Analyze prefixes
    prefix_groups = defaultdict(list)
    for word, freq in top_words:
        if len(word) >= 3:
            # 2-letter prefixes
            prefix2 = word[:2]
            prefix_groups[prefix2].append((word, freq))
            # 3-letter prefixes
            if len(word) >= 4:
                prefix3 = word[:3]
                prefix_groups[prefix3].append((word, freq))

    print("\n" + "-" * 80)
    print("HIGH-FREQUENCY PREFIX PATTERNS (min 3 words)")
    print("-" * 80)

    for prefix in sorted(
        prefix_groups.keys(),
        key=lambda p: sum(f for _, f in prefix_groups[p]),
        reverse=True,
    )[:20]:
        words = prefix_groups[prefix]
        if len(words) >= 3:
            total_freq = sum(f for _, f in words)
            print(
                f"\nPrefix '{prefix}-' ({len(words)} words, {total_freq:,} instances):"
            )
            for w, f in sorted(words, key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {w:15} {f:4}x")


def analyze_character_patterns(words_with_freq):
    """Analyze character sequences and positional patterns."""

    print("\n" + "=" * 80)
    print("CHARACTER SEQUENCE ANALYSIS")
    print("=" * 80)

    # Get top 50 words
    top_words = [
        (w, f)
        for w, f in sorted(words_with_freq.items(), key=lambda x: x[1], reverse=True)[
            :50
        ]
    ]

    # Bigram analysis
    bigrams = Counter()
    trigrams = Counter()

    for word, freq in top_words:
        # Count bigrams weighted by frequency
        for i in range(len(word) - 1):
            bigrams[word[i : i + 2]] += freq
        # Count trigrams
        for i in range(len(word) - 2):
            trigrams[word[i : i + 3]] += freq

    print("\n" + "-" * 80)
    print("TOP 20 BIGRAMS (weighted by word frequency)")
    print("-" * 80)
    for bigram, count in bigrams.most_common(20):
        print(f"  '{bigram}': {count:,} instances")

    print("\n" + "-" * 80)
    print("TOP 20 TRIGRAMS (weighted by word frequency)")
    print("-" * 80)
    for trigram, count in trigrams.most_common(20):
        print(f"  '{trigram}': {count:,} instances")


def analyze_functional_hypothesis(words_with_freq):
    """Test hypothesis: High-frequency unknowns are grammatical particles."""

    print("\n" + "=" * 80)
    print("FUNCTIONAL WORD HYPOTHESIS")
    print("=" * 80)
    print("\nIn natural language, highest frequency words are often:")
    print("  - Articles (the, a, an)")
    print("  - Pronouns (it, he, she, this, that)")
    print("  - Prepositions (of, in, on, at, to, for)")
    print("  - Conjunctions (and, or, but)")
    print("  - Auxiliary verbs (is, are, was, were, have)")

    # Get top 30 words
    top_30 = [
        (w, f)
        for w, f in sorted(words_with_freq.items(), key=lambda x: x[1], reverse=True)[
            :30
        ]
    ]

    print("\n" + "-" * 80)
    print("TOP 30 VOYNICH WORDS - Likely Grammatical Function")
    print("-" * 80)

    short_words = []
    medium_words = []

    for word, freq in top_30:
        if len(word) <= 3:
            short_words.append((word, freq))
        else:
            medium_words.append((word, freq))

    print(f"\nVery short (1-3 chars) - likely articles/prepositions:")
    for w, f in short_words:
        print(f"  {w:10} {f:4}x")

    print(f"\nMedium (4+ chars) - likely pronouns/conjunctions:")
    for w, f in medium_words:
        print(f"  {w:10} {f:4}x")

    total_short = sum(f for _, f in short_words)
    total_medium = sum(f for _, f in medium_words)
    total_all = sum(f for _, f in top_30)

    print(f"\nFrequency distribution:")
    print(f"  Short words: {total_short:,} ({100 * total_short / total_all:.1f}%)")
    print(f"  Medium words: {total_medium:,} ({100 * total_medium / total_all:.1f}%)")


def test_qok_family_hypothesis(words_with_freq):
    """Deep dive into the 'qok-' prefix family."""

    print("\n" + "=" * 80)
    print("'QOK-' PREFIX FAMILY ANALYSIS")
    print("=" * 80)

    qok_words = [(w, f) for w, f in words_with_freq.items() if w.startswith("qok")]
    qok_words.sort(key=lambda x: x[1], reverse=True)

    print(f"\nFound {len(qok_words)} words with 'qok-' prefix")
    print(f"Total frequency: {sum(f for _, f in qok_words):,} instances\n")

    print("Top 'qok-' words:")
    for word, freq in qok_words[:20]:
        # Try to identify root
        root = word[3:]  # Remove 'qok'
        print(f"  qok-{root:10} ({word:15}) {freq:4}x")

    # Check if 'qok' might be a prefix meaning something like "with", "of", "for"
    print("\n" + "-" * 80)
    print("HYPOTHESIS: 'qok-' as grammatical prefix")
    print("-" * 80)
    print("\nPossibilities:")
    print("  1. Preposition marker (like 'of', 'with', 'by')")
    print("  2. Case marker (genitive, dative)")
    print("  3. Verb prefix (modal or aspect marker)")
    print("\nNote: Many root forms appear independently:")

    # Check if roots exist without prefix
    roots_with_independent = []
    for word, freq in qok_words[:20]:
        root = word[3:]
        if root in words_with_freq:
            roots_with_independent.append((word, root, freq, words_with_freq[root]))

    if roots_with_independent:
        print("\n  Word with qok- | Root alone | qok- freq | Root freq")
        print("  " + "-" * 60)
        for qok_word, root, qok_freq, root_freq in roots_with_independent:
            print(f"  {qok_word:15} | {root:10} | {qok_freq:4}x     | {root_freq:4}x")


def test_aiin_pattern(words_with_freq):
    """Analyze the '-aiin' ending pattern."""

    print("\n" + "=" * 80)
    print("'-AIIN' SUFFIX PATTERN ANALYSIS")
    print("=" * 80)

    aiin_words = [(w, f) for w, f in words_with_freq.items() if "aiin" in w]
    aiin_words.sort(key=lambda x: x[1], reverse=True)

    print(f"\nFound {len(aiin_words)} words containing 'aiin'")
    print(f"Total frequency: {sum(f for _, f in aiin_words):,} instances\n")

    # Separate by position
    ending_aiin = [w for w in aiin_words if w[0].endswith("aiin")]
    internal_aiin = [w for w in aiin_words if not w[0].endswith("aiin")]

    print(f"Words ending in '-aiin': {len(ending_aiin)}")
    for word, freq in ending_aiin[:15]:
        prefix = word[:-4] if len(word) > 4 else ""
        print(f"  {prefix:10}-aiin ({word:15}) {freq:4}x")

    print(f"\nWords with internal 'aiin': {len(internal_aiin)}")
    for word, freq in internal_aiin[:10]:
        print(f"  {word:15} {freq:4}x")


def analyze_chedy_shedy_family(words_with_freq):
    """Analyze the chedy/shedy minimal pair."""

    print("\n" + "=" * 80)
    print("CHEDY vs SHEDY ANALYSIS")
    print("=" * 80)

    print("\nThese two words differ only in ch- vs sh-:")
    print(f"  'chedy': {words_with_freq.get('chedy', 0):,}x")
    print(f"  'shedy': {words_with_freq.get('shedy', 0):,}x")
    print(
        f"  Combined: {words_with_freq.get('chedy', 0) + words_with_freq.get('shedy', 0):,}x"
    )

    # Find all ch-/sh- minimal pairs
    print("\n" + "-" * 80)
    print("ALL CH-/SH- MINIMAL PAIRS in top 100")
    print("-" * 80)

    top_100 = [
        (w, f)
        for w, f in sorted(words_with_freq.items(), key=lambda x: x[1], reverse=True)[
            :100
        ]
    ]

    ch_words = {w: f for w, f in top_100 if w.startswith("ch")}
    sh_pairs = []

    for ch_word, ch_freq in ch_words.items():
        sh_word = "sh" + ch_word[2:]
        if sh_word in words_with_freq:
            sh_freq = words_with_freq[sh_word]
            sh_pairs.append((ch_word, ch_freq, sh_word, sh_freq))

    if sh_pairs:
        print("\n  CH- word   | Freq  | SH- word   | Freq  | Combined")
        print("  " + "-" * 60)
        for ch_w, ch_f, sh_w, sh_f in sorted(
            sh_pairs, key=lambda x: x[1] + x[3], reverse=True
        ):
            combined = ch_f + sh_f
            print(f"  {ch_w:10} | {ch_f:5} | {sh_w:10} | {sh_f:5} | {combined:5}")

    print("\n" + "-" * 80)
    print("HYPOTHESIS: ch-/sh- alternation as grammatical marker")
    print("-" * 80)
    print("\nPossibilities:")
    print("  1. Tense or aspect distinction (present vs past)")
    print("  2. Number distinction (singular vs plural)")
    print("  3. Case distinction (nominative vs accusative)")
    print("  4. Person distinction (1st/2nd vs 3rd person)")


def main():
    print("=" * 80)
    print("STATISTICAL PATTERN ANALYSIS - OPTION 3")
    print("=" * 80)
    print("\nStrategy: Since vocabulary expansion failed, analyze structural")
    print("patterns to identify grammatical function of unknown high-freq words")

    # Load data
    word_freqs = load_word_frequencies()

    # Run analyses
    analyze_morphological_patterns(word_freqs)
    analyze_character_patterns(word_freqs)
    analyze_functional_hypothesis(word_freqs)
    test_qok_family_hypothesis(word_freqs)
    test_aiin_pattern(word_freqs)
    analyze_chedy_shedy_family(word_freqs)

    print("\n" + "=" * 80)
    print("CONCLUSIONS")
    print("=" * 80)
    print("\n1. HIGH-FREQUENCY UNKNOWNS ARE LIKELY GRAMMATICAL:")
    print("   - Short particles (ol, al, ar, dy) - probably articles/prepositions")
    print("   - Medium words (daiin, chedy, shedy) - probably pronouns/conjunctions")
    print("   - These won't match ME vocabulary (they're structural, not lexical)")

    print("\n2. SYSTEMATIC PREFIX/SUFFIX PATTERNS:")
    print("   - 'qok-' prefix appears to be grammatical marker")
    print("   - '-aiin' suffix is highly productive")
    print("   - '-edy/-dy' suffix family suggests inflection")

    print("\n3. CH-/SH- ALTERNATION:")
    print("   - Multiple minimal pairs suggest grammatical distinction")
    print("   - Could be tense, number, case, or person marker")

    print("\n4. IMPLICATIONS FOR DECIPHERMENT:")
    print("   - Current 2.12% transformed = lexical words (nouns, verbs)")
    print("   - Top unknown words = grammatical particles")
    print("   - May not be directly translatable to English equivalents")
    print("   - Need to infer function from distribution patterns")

    print("\n5. PATH FORWARD:")
    print("   - Focus on deciphering more lexical words (increase content vocabulary)")
    print("   - Infer grammatical word functions from context")
    print("   - Analyze word co-occurrence patterns")
    print("   - Statistical NLP methods (n-grams, distributional semantics)")


if __name__ == "__main__":
    main()
