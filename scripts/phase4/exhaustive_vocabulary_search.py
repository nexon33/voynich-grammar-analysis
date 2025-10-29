#!/usr/bin/env python3
"""
Phase 4A: Exhaustive Vocabulary Search

Apply ALL known transforms + extended consonant patterns to expanded vocabulary
Search for matches in Voynich manuscript
"""

import json
from collections import Counter, defaultdict
from pathlib import Path


def load_expanded_vocabulary():
    """Load the expanded ME medical vocabulary."""
    with open(
        "results/phase4/expanded_medical_vocabulary.json", "r", encoding="utf-8"
    ) as f:
        return json.load(f)


def load_voynich_text():
    """Load Voynich transcription."""
    with open(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt",
        "r",
        encoding="utf-8",
    ) as f:
        text = f.read()
    words = text.split()
    return Counter(words), set(words)


def apply_all_transforms(me_word):
    """
    Apply ALL known transforms to ME word to generate Voynich candidates.

    Transforms:
    1. e↔o vowel substitution
    2. Word reversal
    3. Consonant shifts: ch↔sh, t↔d, p↔b, f↔v, g↔k, c↔k
    4. Combinations of above
    """

    candidates = set()

    # Helper functions
    def vowel_swap(word, e_to_o=True):
        """Swap e↔o."""
        if e_to_o:
            return word.replace("e", "o")
        else:
            return word.replace("o", "e")

    def reverse_word(word):
        """Reverse the word."""
        return word[::-1]

    def consonant_shifts(word):
        """Apply all consonant shift patterns."""
        variants = {word}

        # ch ↔ sh
        if "ch" in word:
            variants.add(word.replace("ch", "sh"))
        if "sh" in word:
            variants.add(word.replace("sh", "ch"))

        # t ↔ d
        if "t" in word:
            variants.add(word.replace("t", "d"))
        if "d" in word:
            variants.add(word.replace("d", "t"))

        # p ↔ b
        if "p" in word:
            variants.add(word.replace("p", "b"))
        if "b" in word:
            variants.add(word.replace("b", "p"))

        # f ↔ v
        if "f" in word:
            variants.add(word.replace("f", "v"))
        if "v" in word:
            variants.add(word.replace("v", "f"))

        # g ↔ k
        if "g" in word:
            variants.add(word.replace("g", "k"))
        if "k" in word:
            variants.add(word.replace("k", "g"))

        # c ↔ k (soft c)
        if "c" in word:
            variants.add(word.replace("c", "k"))
        if "k" in word and "c" not in word:
            variants.add(word.replace("k", "c"))

        return variants

    # Layer 1: Direct (no transform)
    candidates.add(me_word)

    # Layer 2: e↔o only
    candidates.add(vowel_swap(me_word, e_to_o=True))
    candidates.add(vowel_swap(me_word, e_to_o=False))

    # Layer 3: Reversal only
    reversed_word = reverse_word(me_word)
    candidates.add(reversed_word)

    # Layer 4: Reversal + e↔o
    candidates.add(vowel_swap(reversed_word, e_to_o=True))
    candidates.add(vowel_swap(reversed_word, e_to_o=False))

    # Layer 5: Consonant shifts
    for consonant_variant in consonant_shifts(me_word):
        candidates.add(consonant_variant)
        # Also apply e↔o to consonant variants
        candidates.add(vowel_swap(consonant_variant, e_to_o=True))
        candidates.add(vowel_swap(consonant_variant, e_to_o=False))

    # Layer 6: Reversal + consonant shifts
    for consonant_variant in consonant_shifts(reversed_word):
        candidates.add(consonant_variant)
        # Also apply e↔o
        candidates.add(vowel_swap(consonant_variant, e_to_o=True))
        candidates.add(vowel_swap(consonant_variant, e_to_o=False))

    # Layer 7: Double consonant shifts (ch→sh + t→d, etc.)
    base_variants = list(consonant_shifts(me_word))
    for variant in base_variants:
        for double_variant in consonant_shifts(variant):
            candidates.add(double_variant)
            candidates.add(vowel_swap(double_variant, e_to_o=True))
            candidates.add(vowel_swap(double_variant, e_to_o=False))

    # Remove the original word (we're looking for transformed versions)
    candidates.discard(me_word)

    # Remove empty strings or very short artifacts
    candidates = {c for c in candidates if len(c) >= 2}

    return candidates


def search_vocabulary_exhaustively():
    """Search for all ME vocabulary in Voynich text with all transforms."""

    print("Loading data...")
    vocab = load_expanded_vocabulary()
    voynich_freqs, voynich_set = load_voynich_text()

    print(f"Expanded vocabulary: {len(vocab)} terms")
    print(f"Voynich unique words: {len(voynich_set)}")
    print(f"Voynich total words: {sum(voynich_freqs.values())}")

    print("\nGenerating transform candidates and searching...")

    matches = []
    me_word_to_matches = defaultdict(list)

    checked = 0
    for me_word, me_data in vocab.items():
        checked += 1
        if checked % 100 == 0:
            print(f"  Processed {checked}/{len(vocab)} ME terms...")

        # Generate all possible Voynich forms
        voynich_candidates = apply_all_transforms(me_word)

        # Check which candidates exist in Voynich
        for candidate in voynich_candidates:
            if candidate in voynich_set:
                freq = voynich_freqs[candidate]
                matches.append(
                    {
                        "me_word": me_word,
                        "meaning": me_data["meaning"],
                        "category": me_data["category"],
                        "voynich_word": candidate,
                        "frequency": freq,
                        "transform_applied": infer_transform(me_word, candidate),
                    }
                )
                me_word_to_matches[me_word].append((candidate, freq))

    print(f"\nSearch complete!")

    return matches, me_word_to_matches


def infer_transform(me_word, voynich_word):
    """Infer which transform(s) were applied."""
    transforms = []

    # Check for reversal
    if me_word[::-1] == voynich_word:
        return "reversal"

    # Check for e↔o
    if me_word.replace("e", "o") == voynich_word:
        return "e→o"
    if me_word.replace("o", "e") == voynich_word:
        return "o→e"

    # Check for vowel swap on reversed
    if me_word[::-1].replace("e", "o") == voynich_word:
        return "reversal + e→o"
    if me_word[::-1].replace("o", "e") == voynich_word:
        return "reversal + o→e"

    # Check consonant patterns
    if "ch" in me_word and "sh" in voynich_word:
        transforms.append("ch→sh")
    if "sh" in me_word and "ch" in voynich_word:
        transforms.append("sh→ch")
    if me_word.replace("t", "d") == voynich_word:
        transforms.append("t→d")
    if me_word.replace("d", "t") == voynich_word:
        transforms.append("d→t")
    if me_word.replace("p", "b") == voynich_word:
        transforms.append("p→b")
    if me_word.replace("b", "p") == voynich_word:
        transforms.append("b→p")
    if me_word.replace("f", "v") == voynich_word:
        transforms.append("f→v")
    if me_word.replace("v", "f") == voynich_word:
        transforms.append("v→f")
    if me_word.replace("g", "k") == voynich_word:
        transforms.append("g→k")
    if me_word.replace("k", "g") == voynich_word:
        transforms.append("k→g")

    if transforms:
        return " + ".join(transforms)

    # Complex multi-transform
    return "multi-transform"


def analyze_results(matches):
    """Analyze and display results."""

    print("\n" + "=" * 80)
    print("EXHAUSTIVE VOCABULARY SEARCH RESULTS")
    print("=" * 80)

    # Sort by frequency
    matches_sorted = sorted(matches, key=lambda x: x["frequency"], reverse=True)

    print(f"\nTotal ME terms with matches: {len(set(m['me_word'] for m in matches))}")
    print(
        f"Total Voynich words matched: {len(set(m['voynich_word'] for m in matches))}"
    )
    print(f"Total instances covered: {sum(m['frequency'] for m in matches):,}")

    # By category
    category_counts = defaultdict(lambda: {"terms": set(), "instances": 0})
    for match in matches:
        cat = match["category"]
        category_counts[cat]["terms"].add(match["me_word"])
        category_counts[cat]["instances"] += match["frequency"]

    print("\n" + "-" * 80)
    print("MATCHES BY CATEGORY")
    print("-" * 80)
    for cat in sorted(
        category_counts.keys(),
        key=lambda c: category_counts[c]["instances"],
        reverse=True,
    ):
        data = category_counts[cat]
        print(
            f"\n{cat.upper()}: {len(data['terms'])} ME terms, {data['instances']:,} instances"
        )

    # By transform type
    transform_counts = defaultdict(lambda: {"matches": 0, "instances": 0})
    for match in matches:
        trans = match["transform_applied"]
        transform_counts[trans]["matches"] += 1
        transform_counts[trans]["instances"] += match["frequency"]

    print("\n" + "-" * 80)
    print("MATCHES BY TRANSFORM TYPE")
    print("-" * 80)
    for trans in sorted(
        transform_counts.keys(),
        key=lambda t: transform_counts[t]["instances"],
        reverse=True,
    ):
        data = transform_counts[trans]
        print(
            f"{trans:30} {data['matches']:4} matches, {data['instances']:6,} instances"
        )

    # Top matches
    print("\n" + "-" * 80)
    print("TOP 50 MATCHES (by frequency)")
    print("-" * 80)
    print(
        f"{'ME Word':<15} {'Voynich':<15} {'Freq':>6} {'Category':<15} {'Transform':<25} {'Meaning'}"
    )
    print("-" * 80)

    for match in matches_sorted[:50]:
        print(
            f"{match['me_word']:<15} {match['voynich_word']:<15} {match['frequency']:6} "
            f"{match['category']:<15} {match['transform_applied']:<25} {match['meaning']}"
        )

    # NEW matches (not in Phase 3)
    print("\n" + "-" * 80)
    print("NEW DISCOVERIES (Top 30)")
    print("-" * 80)
    print("(These are matches we didn't find in Phase 3)")
    print(f"\n{'ME Word':<15} {'Voynich':<15} {'Freq':>6} {'Category':<15} {'Meaning'}")
    print("-" * 80)

    # List of Phase 3 known words (simplified - major ones)
    phase3_known = {
        "or",
        "and",
        "in",
        "of",
        "the",
        "is",
        "with",
        "for",  # Preserved
        "oy",
        "ye",
        "oyo",
        "eyo",  # eye variants
        "otor",
        "teor",
        "rote",
        "odor",  # root variants
        "fol",
        "lef",  # leaf variants
        "tos",
        "dos",
        "sed",  # seed variants
        "sor",
        "sore",  # sore
        "kam",
        "mak",  # make
        "kat",
        "tak",  # take
        "lot",
        "let",  # let
        "dol",
        "tol",  # dole/tell
        "cho",
        "she",  # she
    }

    new_count = 0
    for match in matches_sorted:
        if match["voynich_word"] not in phase3_known and new_count < 30:
            print(
                f"{match['me_word']:<15} {match['voynich_word']:<15} {match['frequency']:6} "
                f"{match['category']:<15} {match['meaning']}"
            )
            new_count += 1

    return matches_sorted


def save_results(matches):
    """Save results to JSON."""
    output_path = Path("results/phase4/exhaustive_search_results.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(matches, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_path}")


def main():
    print("=" * 80)
    print("PHASE 4A: EXHAUSTIVE VOCABULARY SEARCH")
    print("=" * 80)
    print("\nApplying ALL transforms to 764 expanded ME medical terms:")
    print("  - e↔o vowel substitution")
    print("  - Word reversal")
    print("  - Consonant shifts: ch↔sh, t↔d, p↔b, f↔v, g↔k, c↔k")
    print("  - All combinations")

    # Search
    matches, me_word_to_matches = search_vocabulary_exhaustively()

    # Analyze
    matches_sorted = analyze_results(matches)

    # Save
    save_results(matches_sorted)

    print("\n" + "=" * 80)
    print("SEARCH COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
