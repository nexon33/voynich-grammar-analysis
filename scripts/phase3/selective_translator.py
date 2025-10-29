"""
Selective Translation Tool for Voynich Manuscript

Based on selective obfuscation model:
- Try multiple e↔o combinations for each word
- Rank by ME vocabulary match
- Identify medical terms
- Show most coherent translations
"""

from pathlib import Path
import json
import re
from collections import Counter
from itertools import product


def load_medical_vocabulary():
    """Load medical vocabulary database."""
    vocab_file = Path("results/phase3/medical_vocabulary_database.json")
    with open(vocab_file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_me_vocabulary():
    """Load general ME vocabulary."""
    corpus_dir = Path("data/middle_english_corpus/cmepv/middle_english_text_cmepv/sgml")
    sgml_files = list(corpus_dir.glob("*.sgm"))[:30]  # First 30 for speed

    all_words = set()
    for sgml_file in sgml_files:
        with open(sgml_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            text = re.sub(r"<[^>]+>", " ", content)
            words = re.findall(r"[a-z]+", text.lower())
            all_words.update(words)

    return all_words


def generate_eo_variants(word):
    """
    Generate all possible e↔o combinations for a word.

    For a word with N positions that have 'e' or 'o',
    generate 2^N variants.
    """
    variants = []

    # Find all positions with 'e' or 'o'
    eo_positions = []
    for i, char in enumerate(word):
        if char in ["e", "o"]:
            eo_positions.append(i)

    if not eo_positions:
        # No 'e' or 'o' in word
        return [word]

    # Generate all combinations
    # For each position, try both 'e' and 'o'
    for combination in product(["e", "o"], repeat=len(eo_positions)):
        variant = list(word)
        for pos_idx, char_choice in enumerate(combination):
            variant[eo_positions[pos_idx]] = char_choice
        variants.append("".join(variant))

    # Remove duplicates and return
    return list(set(variants))


def rank_variants(variants, me_vocab, medical_vocab):
    """
    Rank word variants by likelihood.

    Scoring:
    +100: Found in ME vocabulary
    +200: Found in medical vocabulary
    +50: Common word (length < 4)
    +20: Has common ME patterns (ch, sh, -ly, -er)
    """
    scored_variants = []

    # Flatten medical vocabulary for searching
    medical_words = set()
    for category, terms in medical_vocab.items():
        for term_info in terms:
            medical_words.add(term_info["word"])

    for variant in variants:
        score = 0
        reasons = []

        # Check ME vocabulary
        if variant in me_vocab:
            score += 100
            reasons.append("in_ME_corpus")

        # Check medical vocabulary (higher priority!)
        if variant in medical_words:
            score += 200
            reasons.append("MEDICAL_TERM")

        # Short words more likely unchanged
        if len(variant) < 4:
            score += 50
            reasons.append("short_word")

        # Common ME patterns
        if "ch" in variant:
            score += 20
            reasons.append("has_ch")

        if "sh" in variant:
            score += 20
            reasons.append("has_sh")

        if variant.endswith("ly"):
            score += 20
            reasons.append("ends_ly")

        if variant.endswith("er") or variant.endswith("or"):
            score += 15
            reasons.append("agent_suffix")

        if variant.endswith("es") or variant.endswith("os"):
            score += 10
            reasons.append("plural_suffix")

        scored_variants.append({"variant": variant, "score": score, "reasons": reasons})

    # Sort by score (highest first)
    scored_variants.sort(key=lambda x: x["score"], reverse=True)

    return scored_variants


def translate_word(word, me_vocab, medical_vocab):
    """
    Translate a single Voynich word using selective obfuscation.

    Returns top 5 most likely translations.
    """
    # Generate all e↔o variants
    variants = generate_eo_variants(word)

    # Rank them
    ranked = rank_variants(variants, me_vocab, medical_vocab)

    # Return top 5
    return ranked[:5]


def translate_passage(voynich_text, me_vocab, medical_vocab, top_n=3):
    """
    Translate a passage of Voynich text.

    For each word, try top_n most likely translations.
    Show best combinations.
    """
    # Split into words
    words = re.findall(r"[a-z]+", voynich_text.lower())

    # Translate each word
    translations = []
    for word in words:
        word_translations = translate_word(word, me_vocab, medical_vocab)
        translations.append(
            {"original": word, "top_variants": word_translations[:top_n]}
        )

    return translations


def find_medical_terms_in_voynich(voynich_text, medical_vocab):
    """
    Search for medical terms in Voynich text using e↔o variations.
    """
    medical_matches = []

    # Flatten medical vocabulary
    medical_words = {}
    for category, terms in medical_vocab.items():
        for term_info in terms:
            medical_words[term_info["word"]] = {
                "category": category,
                "frequency": term_info["frequency"],
            }

    # Check each Voynich word
    words = re.findall(r"[a-z]+", voynich_text.lower())

    for voyn_word in words:
        # Generate variants
        variants = generate_eo_variants(voyn_word)

        # Check if any variant is a medical term
        for variant in variants:
            if variant in medical_words:
                medical_matches.append(
                    {
                        "voynich": voyn_word,
                        "medical_term": variant,
                        "category": medical_words[variant]["category"],
                        "me_frequency": medical_words[variant]["frequency"],
                    }
                )

    return medical_matches


def main():
    print("\n" + "=" * 70)
    print("SELECTIVE VOYNICH TRANSLATOR")
    print("=" * 70 + "\n")

    # Load vocabularies
    print("Loading vocabularies...")
    medical_vocab = load_medical_vocabulary()
    me_vocab = load_me_vocabulary()
    print(f"✓ Loaded {len(me_vocab):,} general ME words")

    total_medical = sum(len(terms) for terms in medical_vocab.values())
    print(f"✓ Loaded {total_medical:,} medical terms\n")

    # Load Voynich text
    voynich_file = Path("data/voynich/eva_transcription/voynich_eva_takahashi.txt")
    with open(voynich_file, "r", encoding="utf-8") as f:
        voynich_text = f.read().lower()

    print(f"✓ Loaded Voynich text ({len(voynich_text):,} characters)\n")

    # Test on a sample passage (first 500 chars)
    print("=" * 70)
    print("SAMPLE TRANSLATION: First 500 characters")
    print("=" * 70 + "\n")

    sample = voynich_text[:500]

    print("ORIGINAL VOYNICH:")
    print("-" * 70)
    print(sample)
    print()

    # Translate
    print("SELECTIVE TRANSLATION:")
    print("-" * 70)

    translations = translate_passage(sample, me_vocab, medical_vocab, top_n=2)

    # Show word-by-word translation
    for i, trans in enumerate(translations[:30]):  # First 30 words
        original = trans["original"]
        top_variants = trans["top_variants"]

        if top_variants and top_variants[0]["score"] > 0:
            best = top_variants[0]
            print(
                f"{original:15} → {best['variant']:15} (score: {best['score']}, {', '.join(best['reasons'])})"
            )
        else:
            print(f"{original:15} → ???")

    print("\n...")

    # Search for medical terms in full text
    print("\n" + "=" * 70)
    print("SEARCHING FOR MEDICAL TERMS IN FULL VOYNICH TEXT")
    print("=" * 70 + "\n")

    medical_matches = find_medical_terms_in_voynich(voynich_text, medical_vocab)

    # Group by category
    by_category = {}
    for match in medical_matches:
        category = match["category"]
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(match)

    print(f"Found {len(medical_matches):,} potential medical term matches!\n")

    for category in ["herbs", "body_parts", "conditions", "treatments", "women_health"]:
        if category in by_category:
            matches = by_category[category]
            print(f"\n{category.upper().replace('_', ' ')} ({len(matches)} matches):")
            print("-" * 70)

            # Count frequency of each match
            match_counts = Counter([(m["voynich"], m["medical_term"]) for m in matches])

            # Show top 20
            for (voyn, med), count in match_counts.most_common(20):
                print(f"  {voyn:15} → {med:15} (appears {count:>4}x)")

    # Save results
    output_dir = Path("results/phase3")

    # Save medical matches
    matches_file = output_dir / "medical_terms_found.json"
    with open(matches_file, "w", encoding="utf-8") as f:
        json.dump(medical_matches, f, indent=2, ensure_ascii=False)

    print(f"\n\n✓ Medical term matches saved to: {matches_file}")

    # Create readable report
    report_file = output_dir / "medical_terms_found.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("MEDICAL TERMS FOUND IN VOYNICH MANUSCRIPT\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total matches: {len(medical_matches):,}\n\n")

        for category in [
            "herbs",
            "body_parts",
            "conditions",
            "treatments",
            "women_health",
            "substances",
        ]:
            if category in by_category:
                matches = by_category[category]
                f.write(
                    f"\n{category.upper().replace('_', ' ')} ({len(matches)} matches):\n"
                )
                f.write("-" * 70 + "\n")

                match_counts = Counter(
                    [(m["voynich"], m["medical_term"]) for m in matches]
                )
                for (voyn, med), count in match_counts.most_common():
                    f.write(f"{voyn:20} → {med:20} (appears {count:>4}x)\n")

    print(f"✓ Text report saved to: {report_file}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70 + "\n")

    print(f"Total medical term matches: {len(medical_matches):,}")
    print(f"Categories found: {len(by_category)}")
    print()

    if len(medical_matches) > 100:
        print("✓✓✓ SIGNIFICANT medical vocabulary found!")
        print("    This strongly supports the medical content hypothesis.")
    elif len(medical_matches) > 20:
        print("✓✓ Moderate medical vocabulary found.")
        print("   Supports medical content hypothesis.")
    else:
        print("✓ Limited medical vocabulary in current matching.")
        print("  May need refinement or different sections.")

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70 + "\n")
    print("1. Analyze sections with high medical term density")
    print("2. Attempt full passage translation")
    print("3. Check for coherent medical recipes/instructions")
    print("4. Validate against known ME medical texts")
    print()


if __name__ == "__main__":
    main()
