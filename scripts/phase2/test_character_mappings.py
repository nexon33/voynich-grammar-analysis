"""
Phase 2: Test character mappings and look for Middle English vocabulary in Voynich.

Starting with the confirmed 'o' = 'e' hypothesis, we'll:
1. Apply character substitutions to Voynich text
2. Look for recognizable Middle English words
3. Test additional character mappings based on frequency
4. Extract common ME vocabulary from CMEPV corpus
"""

from collections import Counter
from pathlib import Path
import re


def read_voynich_words():
    """Read Voynich text and return list of words."""
    voynich_file = Path("data/voynich/eva_transcription/voynich_eva_takahashi.txt")
    with open(voynich_file, "r", encoding="utf-8") as f:
        text = f.read().lower()

    # Extract words (alphabetic only)
    words = re.findall(r"[a-z]+", text)
    return words


def read_me_vocabulary(min_freq=10):
    """Extract common Middle English words from CMEPV corpus."""
    corpus_dir = Path("data/middle_english_corpus/cmepv/middle_english_text_cmepv/sgml")
    sgml_files = list(corpus_dir.glob("*.sgm"))

    all_words = []
    for sgml_file in sgml_files:
        with open(sgml_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            # Remove SGML tags
            text = re.sub(r"<[^>]+>", " ", content)
            # Extract words
            words = re.findall(r"[a-z]+", text.lower())
            all_words.extend(words)

    # Count frequencies
    word_freq = Counter(all_words)

    # Return words that appear at least min_freq times
    common_words = {word for word, count in word_freq.items() if count >= min_freq}

    return common_words, word_freq


def apply_substitution(text, mapping):
    """Apply character substitution mapping to text."""
    result = []
    for char in text:
        result.append(mapping.get(char, char))
    return "".join(result)


def test_mapping(voynich_words, me_vocab, mapping, mapping_name):
    """Test a character mapping and see how many ME words we find."""
    print(f"\n{'=' * 70}")
    print(f"TESTING: {mapping_name}")
    print(f"{'=' * 70}")
    print(f"Mapping: {mapping}\n")

    # Apply mapping to Voynich words
    translated_words = [apply_substitution(word, mapping) for word in voynich_words]

    # Find matches with ME vocabulary
    matches = []
    for voyn_word, trans_word in zip(voynich_words, translated_words):
        if trans_word in me_vocab and len(trans_word) >= 3:  # At least 3 letters
            matches.append((voyn_word, trans_word))

    # Count unique matches
    unique_matches = list(set(matches))
    unique_matches.sort(key=lambda x: len(x[1]), reverse=True)

    print(f"Total Voynich words: {len(voynich_words):,}")
    print(f"Unique Voynich words: {len(set(voynich_words)):,}")
    print(f"Words matching ME vocabulary: {len(matches):,}")
    print(f"Unique matches: {len(unique_matches)}")
    print(f"Match rate: {len(matches) / len(voynich_words) * 100:.2f}%")

    if unique_matches:
        print(f"\nTop 20 matches (Voynich → Middle English):")
        print("-" * 70)
        for voyn, me in unique_matches[:20]:
            print(f"  {voyn:15} → {me}")
    else:
        print("\n✗ No matches found")

    return len(matches), unique_matches


def main():
    print("\n" + "=" * 70)
    print("PHASE 2: CHARACTER MAPPING AND VOCABULARY TESTING")
    print("=" * 70 + "\n")

    # Load data
    print("Loading Voynich text...")
    voynich_words = read_voynich_words()
    print(f"✓ Loaded {len(voynich_words):,} Voynich words\n")

    print("Extracting Middle English vocabulary from CMEPV corpus...")
    print("(This may take a minute...)")
    me_vocab, me_freq = read_me_vocabulary(min_freq=10)
    print(f"✓ Extracted {len(me_vocab):,} common ME words\n")

    print("Most common Middle English words:")
    for word, count in me_freq.most_common(20):
        print(f"  {word:15} {count:>8,} occurrences")

    # Test different character mappings
    results = []

    # Mapping 1: Just o = e
    mapping1 = {"o": "e"}
    matches1, unique1 = test_mapping(
        voynich_words, me_vocab, mapping1, "Mapping 1: o → e only"
    )
    results.append(("o → e", matches1, len(unique1)))

    # Mapping 2: Top 2 frequencies
    # Voynich: o(13.3%), e(10.48%)
    # ME: e(13.49%), t(8.71%)
    mapping2 = {"o": "e", "e": "t"}
    matches2, unique2 = test_mapping(
        voynich_words, me_vocab, mapping2, "Mapping 2: o → e, e → t"
    )
    results.append(("o→e, e→t", matches2, len(unique2)))

    # Mapping 3: Top 3 frequencies
    # Add: h(9.32%) → o(8.58%)
    mapping3 = {"o": "e", "e": "t", "h": "o"}
    matches3, unique3 = test_mapping(
        voynich_words, me_vocab, mapping3, "Mapping 3: o → e, e → t, h → o"
    )
    results.append(("o→e, e→t, h→o", matches3, len(unique3)))

    # Mapping 4: Top 5 frequencies
    # Voynich: o, e, h, y(9.22%), a(7.46%)
    # ME: e, t, o, n(7.76%), h(7.28%)
    mapping4 = {"o": "e", "e": "t", "h": "o", "y": "n", "a": "h"}
    matches4, unique4 = test_mapping(
        voynich_words, me_vocab, mapping4, "Mapping 4: o→e, e→t, h→o, y→n, a→h"
    )
    results.append(("5 chars", matches4, len(unique4)))

    # Mapping 5: Bigram-based guess
    # ch is common in both - keep it
    # sh is common in both - keep it
    # Test if word patterns suggest specific mappings
    mapping5 = {
        "o": "e",
        "e": "t",
        "h": "h",  # h might be h (for ch, sh)
        "c": "c",  # c might be c (for ch)
        "s": "s",  # s might be s (for sh)
    }
    matches5, unique5 = test_mapping(
        voynich_words, me_vocab, mapping5, "Mapping 5: Keep common digraphs (ch, sh)"
    )
    results.append(("digraph", matches5, len(unique5)))

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY OF RESULTS")
    print("=" * 70 + "\n")

    print(f"{'Mapping':<20} {'Total Matches':<15} {'Unique Matches':<15} {'Rate'}")
    print("-" * 70)
    for name, total, unique in results:
        rate = (total / len(voynich_words)) * 100
        print(f"{name:<20} {total:<15,} {unique:<15} {rate:.2f}%")

    # Best mapping
    best_idx = max(range(len(results)), key=lambda i: results[i][1])
    best_name, best_total, best_unique = results[best_idx]

    print(f"\n✓ Best mapping: {best_name}")
    print(f"  Total matches: {best_total:,}")
    print(f"  Unique matches: {best_unique}")
    print(f"  Match rate: {(best_total / len(voynich_words)) * 100:.2f}%")

    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70 + "\n")

    if best_total > 100:
        print("✓ Found significant vocabulary matches!")
        print("  This suggests the character mapping is on the right track.")
        print("\nNext steps:")
        print("1. Refine the mapping based on matched words")
        print("2. Look for morphological patterns (-ed, -ing, etc.)")
        print("3. Test against medical vocabulary specifically")
    else:
        print("✗ Limited vocabulary matches found.")
        print("  This suggests:")
        print("  1. The mapping needs refinement")
        print("  2. The obfuscation may be more complex than simple substitution")
        print("  3. We may need to consider word-level transformations")

    # Save results
    output_dir = Path("results/phase2")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save best unique matches
    output_file = output_dir / "vocabulary_matches.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("PHASE 2: Vocabulary Matching Results\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Best mapping: {best_name}\n")
        f.write(f"Total matches: {best_total:,}\n")
        f.write(f"Unique matches: {best_unique}\n\n")
        f.write("Matched words (Voynich → Middle English):\n")
        f.write("-" * 70 + "\n")

        # Get best unique matches based on best_idx
        if best_idx == 0:
            best_matches = unique1
        elif best_idx == 1:
            best_matches = unique2
        elif best_idx == 2:
            best_matches = unique3
        elif best_idx == 3:
            best_matches = unique4
        else:
            best_matches = unique5

        for voyn, me in best_matches:
            f.write(f"{voyn:20} → {me}\n")

    print(f"\n✓ Results saved to: {output_file}")


if __name__ == "__main__":
    main()
