#!/usr/bin/env python3
"""
Direct test of vowel mappings on known medical terms from Section 4.
"""

import json
from pathlib import Path
from itertools import product


def load_medical_vocab():
    """Load medical vocabulary."""
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"
    with open(
        results_dir / "medical_vocabulary_database.json", "r", encoding="utf-8"
    ) as f:
        return json.load(f)


def test_known_words():
    """Test known words from Section 4 with different vowel mappings."""

    # Known medical terms found in Section 4 (from our analysis)
    test_words = {
        "sor": "conditions",  # Already identified
        "ched": "body_parts",  # Already identified
        "chod": "body_parts (variant of ched)",
        "oro": "body_parts (ere)",
        "orom": "body_parts (erem)",
        "poror": "body_parts (perer)",
        "toror": "body_parts (terer)",
        "chotol": "conditions (chetel)",
    }

    medical_vocab = load_medical_vocab()

    print("=" * 80)
    print("TESTING VOWEL MAPPINGS ON KNOWN SECTION 4 MEDICAL TERMS")
    print("=" * 80)
    print()

    for original, expected_category in test_words.items():
        print(f"Testing: {original}")
        print(f"Expected: {expected_category}")
        print()

        # Test e↔o only
        variants_eo = generate_variants_eo(original)
        matches_eo = [(v, medical_vocab[v]) for v in variants_eo if v in medical_vocab]

        # Test multi-vowel
        variants_multi = generate_variants_multi(original)
        matches_multi = [
            (v, medical_vocab[v]) for v in variants_multi if v in medical_vocab
        ]

        print(f"  e↔o variants ({len(variants_eo)}): {', '.join(variants_eo[:10])}")
        if matches_eo:
            print(f"  ✓ MATCHES (e↔o):")
            for v, info in matches_eo[:5]:
                print(f"    {v} → {info['category']}")
        else:
            print(f"  ✗ No matches with e↔o")
        print()

        print(
            f"  Multi-vowel variants ({len(variants_multi)}): {', '.join(variants_multi[:10])}"
        )
        if matches_multi:
            print(f"  ✓ MATCHES (multi-vowel):")
            for v, info in matches_multi[:5]:
                print(f"    {v} → {info['category']}")
        else:
            print(f"  ✗ No matches with multi-vowel")

        # Check if multi found more than eo
        new_matches = set(v for v, _ in matches_multi) - set(v for v, _ in matches_eo)
        if new_matches:
            print(f"  ✓✓ NEW with multi-vowel: {', '.join(new_matches)}")

        print()
        print("-" * 80)
        print()


def generate_variants_eo(word):
    """Generate e↔o variants."""
    eo_positions = [(i, c) for i, c in enumerate(word) if c in ["e", "o"]]
    if len(eo_positions) > 5:
        return [word, word.replace("o", "e"), word.replace("e", "o")]

    variants = set([word])
    for combination in product(["e", "o"], repeat=len(eo_positions)):
        variant = list(word)
        for (pos, _), new_char in zip(eo_positions, combination):
            variant[pos] = new_char
        variants.add("".join(variant))
    return list(variants)


def generate_variants_multi(word):
    """Generate multi-vowel variants (e↔o, a↔e, i↔y)."""
    substitutions = {
        "e": ["e", "o", "a"],
        "o": ["o", "e"],
        "a": ["a", "e"],
        "i": ["i", "y"],
        "y": ["y", "i"],
    }

    positions = []
    for i, char in enumerate(word):
        if char in substitutions:
            positions.append((i, substitutions[char]))
        else:
            positions.append((i, [char]))

    # Limit to 100 variants
    total = 1
    for _, chars in positions:
        total *= len(chars)

    if total > 100:
        return generate_variants_eo(word)

    variants = set()
    for combo in product(*[chars for _, chars in positions]):
        variants.add("".join(combo))

    return list(variants)


def test_sample_text():
    """Test a sample of actual Section 4 text."""

    # Sample text from Section 4 (f20v area based on proper mapping)
    # This should contain the medical terms
    sample_text = (
        "ol chy kchey kchor dal pcho daiin chopol shoiin daiin sor chod oro orom"
    )

    medical_vocab = load_medical_vocab()

    print("=" * 80)
    print("TESTING SAMPLE TEXT FROM SECTION 4")
    print("=" * 80)
    print()
    print(f"Sample: {sample_text}")
    print()

    words = sample_text.split()
    recognized_eo = []
    recognized_multi = []

    for word in words:
        # e↔o
        for v in generate_variants_eo(word):
            if v in medical_vocab:
                recognized_eo.append((word, v, medical_vocab[v]["category"]))
                break

        # multi
        for v in generate_variants_multi(word):
            if v in medical_vocab:
                recognized_multi.append((word, v, medical_vocab[v]["category"]))
                break

    print(f"e↔o recognition: {len(recognized_eo)}/{len(words)}")
    for orig, variant, cat in recognized_eo:
        print(f"  {orig} → {variant} ({cat})")
    print()

    print(f"Multi-vowel recognition: {len(recognized_multi)}/{len(words)}")
    for orig, variant, cat in recognized_multi:
        print(f"  {orig} → {variant} ({cat})")
    print()


if __name__ == "__main__":
    test_known_words()
    test_sample_text()
