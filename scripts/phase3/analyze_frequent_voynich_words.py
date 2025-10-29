#!/usr/bin/env python3
"""
Analyze the most frequent Voynich words and attempt to decode them.

Strategy: Work BACKWARDS
1. Find most common Voynich words
2. Apply REVERSE transforms to see what ME words they could be
3. Check if those ME words make sense for a medical text
"""

import json
from pathlib import Path
from collections import Counter
from itertools import product


def load_manuscript():
    """Load full manuscript text."""
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"

    with open(
        results_dir / "full_manuscript_translation.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)

    all_words = []
    for section in data["sections"]:
        words = section["original"].split()
        all_words.extend(words)

    return all_words


def reverse_transforms(voynich_word):
    """
    Apply REVERSE transforms to a Voynich word to get possible ME words.

    Returns possible original English words before transformation.
    """
    possibilities = set()

    # Helper: reverse e↔o
    def reverse_eo(w):
        eo_positions = [(i, c) for i, c in enumerate(w) if c in ["e", "o"]]
        if len(eo_positions) > 5:
            return [w, w.replace("o", "e"), w.replace("e", "o")]

        result = set()
        for combo in product(["e", "o"], repeat=len(eo_positions)):
            variant = list(w)
            for (pos, _), new_char in zip(eo_positions, combo):
                variant[pos] = new_char
            result.add("".join(variant))
            if len(result) >= 30:
                break
        return list(result)

    # Helper: reverse consonants
    def reverse_consonants(w):
        result = {w}
        # ch↔sh
        result.add(w.replace("ch", "sh"))
        result.add(w.replace("sh", "ch"))
        # t↔d
        result.add(w.replace("t", "d"))
        result.add(w.replace("d", "t"))
        # c↔k
        result.add(w.replace("c", "k"))
        result.add(w.replace("k", "c"))
        return list(result)

    # Path 1: Direct (consonants + e↔o, no reversal)
    for cons_var in reverse_consonants(voynich_word):
        for eo_var in reverse_eo(cons_var):
            possibilities.add(eo_var)

    # Path 2: Word reversed (un-reverse it, then consonants + e↔o)
    unreversed = voynich_word[::-1]
    for cons_var in reverse_consonants(unreversed):
        for eo_var in reverse_eo(cons_var):
            possibilities.add(eo_var)

    return list(possibilities)


def main():
    print("=" * 80)
    print("ANALYZING MOST FREQUENT VOYNICH WORDS")
    print("=" * 80)
    print()
    print("Strategy: Work backwards from common Voynich words")
    print("  1. Find most frequent Voynich words")
    print("  2. Apply reverse transforms")
    print("  3. Identify potential Middle English matches")
    print()

    all_words = load_manuscript()

    # Count word frequencies
    word_freq = Counter()
    for word in all_words:
        word_clean = word.lower().strip(".,;:!?")
        if len(word_clean) >= 2:  # Ignore single letters
            word_freq[word_clean] += 1

    # Get top 100 most common words
    top_words = word_freq.most_common(100)

    print(f"Total unique words: {len(word_freq)}")
    print(f"Analyzing top 100 most frequent")
    print()

    # Analyze each
    print("=" * 80)
    print("TOP 100 VOYNICH WORDS - REVERSE ANALYSIS")
    print("=" * 80)
    print()

    # Known medical/common words in Middle English
    medical_vocabulary = {
        # Common words
        "the",
        "and",
        "of",
        "to",
        "a",
        "in",
        "is",
        "it",
        "that",
        "for",
        "with",
        "this",
        "be",
        "as",
        "or",
        "at",
        "by",
        "not",
        "but",
        "from",
        "have",
        "an",
        "they",
        "which",
        "one",
        "all",
        "when",
        "there",
        "can",
        "if",
        "will",
        "more",
        # Instructions
        "take",
        "tak",
        "make",
        "mak",
        "put",
        "do",
        "let",
        "lay",
        "ley",
        "boil",
        "grind",
        "stamp",
        "drink",
        "drynke",
        "mix",
        "meng",
        # Plant parts
        "root",
        "rote",
        "leaf",
        "lef",
        "seed",
        "sed",
        "sede",
        "flower",
        "flour",
        "herb",
        "herbe",
        "bark",
        "stem",
        "stalke",
        # Body parts
        "head",
        "hed",
        "hand",
        "hond",
        "eye",
        "ye",
        "ear",
        "ere",
        "foot",
        "fot",
        "blood",
        "blod",
        "heart",
        "herte",
        "mouth",
        "belly",
        "bely",
        # Conditions
        "pain",
        "peyn",
        "sore",
        "sor",
        "ache",
        "heal",
        "hele",
        "hurt",
        # Quantities
        "much",
        "many",
        "few",
        "some",
        "more",
        "less",
        "all",
        "each",
        "ounce",
        "pound",
        "part",
        "dele",
        # Time
        "day",
        "night",
        "hour",
        "time",
        "year",
        "month",
        "week",
        # Actions
        "give",
        "help",
        "cure",
        "use",
        "add",
        "wash",
        "wasch",
    }

    decoded_count = 0

    for rank, (voynich_word, count) in enumerate(top_words, 1):
        # Get possible ME words
        possibilities = reverse_transforms(voynich_word)

        # Check if any match known vocabulary
        matches = [p for p in possibilities if p in medical_vocabulary]

        if matches:
            decoded_count += 1
            print(
                f"{rank:3d}. {voynich_word:15s} ({count:4d}x) -> {', '.join(matches[:5])}"
            )
            if len(matches) > 5:
                print(f"     ... and {len(matches) - 5} more possibilities")
        elif rank <= 30:  # Show top 30 even if no match
            print(f"{rank:3d}. {voynich_word:15s} ({count:4d}x) -> [no obvious match]")
            # Show some possibilities for inspection
            if len(possibilities) <= 10:
                print(f"     Possibilities: {', '.join(possibilities[:5])}")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"Top 100 words analyzed")
    print(f"Decoded: {decoded_count} words match known ME vocabulary")
    print(
        f"Unmatched: {100 - decoded_count} words (may be rare terms, names, or need different transforms)"
    )
    print()

    # Calculate coverage
    decoded_instances = sum(
        count
        for word, count in top_words
        if any(p in medical_vocabulary for p in reverse_transforms(word))
    )
    total_words = len(all_words)
    coverage = decoded_instances / total_words * 100

    print(
        f"Coverage of decoded top-100 words: {decoded_instances:,} instances ({coverage:.2f}%)"
    )
    print()

    print("INTERPRETATION:")
    print()
    if coverage > 5:
        print("✓✓✓ EXCELLENT!")
        print(f"    The top 100 most common words include {coverage:.2f}% of the text")
        print("    Most are decodable with our known transforms")
    elif coverage > 3:
        print("✓✓ GOOD")
        print(f"    The top 100 words cover {coverage:.2f}% of the text")
        print("    Many common words are within our cipher model")
    else:
        print("✓ EXPECTED")
        print(f"    Top 100 words cover {coverage:.2f}% of text")
        print("    Need to expand beyond most common words")

    print()
    print("Next steps:")
    print("  • Manually inspect unmatched common words")
    print("  • Test variants (spelling variations, dialects)")
    print("  • Look for compound words or abbreviations")
    print("  • Consider words might be Latin/French medical terms")
    print()


if __name__ == "__main__":
    main()
