#!/usr/bin/env python3
"""
Debug scrambling to see what variants are being generated.
"""

from itertools import permutations


def generate_scrambled_variants(word, max_variants=50):
    """Generate variants with middle letters scrambled, first/last preserved."""
    if len(word) <= 3:
        return [word]

    first = word[0]
    last = word[-1]
    middle = word[1:-1]

    if len(middle) <= 1:
        return [word]

    variants = set()
    variants.add(word)

    for perm in permutations(middle):
        scrambled = first + "".join(perm) + last
        variants.add(scrambled)
        if len(variants) >= max_variants:
            break

    return sorted(list(variants))


# Test with some medical terms
test_words = ["root", "pain", "sore", "blood", "take", "drink", "boil", "grind"]

print("=" * 80)
print("SCRAMBLING VARIANT GENERATOR TEST")
print("=" * 80)
print()

for word in test_words:
    variants = generate_scrambled_variants(word)
    print(f"{word:10s} → {len(variants):2d} variants: {', '.join(variants)}")

print()
print("=" * 80)
print("REVERSE THESE VOYNICH WORDS:")
print("=" * 80)
print()

# Check what happens when we reverse some Voynich words and then scramble
voynich_words = [
    "teor",  # Found to match "root" with reversal
    "otor",  # Found to match "root" with reversal
    "oy",  # Found to match "eye" with reversal
    "daiin",  # Common Voynich pattern
    "chol",  # Common Voynich pattern
]

for word in voynich_words:
    reversed_word = word[::-1]
    variants = generate_scrambled_variants(reversed_word)
    print(f"{word:10s} → reversed: {reversed_word:10s}")
    print(
        f"           → scrambled variants ({len(variants)}): {', '.join(variants[:10])}"
    )
    print()
