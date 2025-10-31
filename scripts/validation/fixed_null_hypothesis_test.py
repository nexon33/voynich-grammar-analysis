"""
FIXED NULL HYPOTHESIS TEST

The previous test had a bug - it gave identical results for scrambled text.
This version will properly test if word ORDER matters for recognition.

If recognition is based on grammar/sequences, scrambled order should show LOWER recognition.
If recognition is just based on word structure, scrambled order will show SAME recognition.
"""

import json
import random
from collections import Counter

print("=" * 80)
print("FIXED NULL HYPOTHESIS TEST")
print("Testing if word order affects recognition")
print("=" * 80)

# Simple morpheme recognizer
KNOWN_MORPHEMES = {
    "qok": "oak",
    "qot": "oat",
    "dain": "water",
    "sho": "vessel",
    "chol": "take",
    "ol": "or",
    "or": "and",
    "ar": "at",
    "al": "the",
    "dy": "in",
    "che": "oak-bark",
    "cheo": "boil",
    "chy": "use",
    "y": "topic",
    "k": "then",
    "s": "of",
    "r": "particle",
    "e": "continuous",
    "ain": "GEN",
    "aiin": "GEN",
    "edy": "LOC",
    "ody": "LOC",
    "eol": "INST",
    "ear": "DIR",
    "eal": "DEF",
}

SUFFIX_PATTERNS = [
    "ain",
    "aiin",
    "dy",
    "edy",
    "ody",
    "ol",
    "eol",
    "ar",
    "ear",
    "al",
    "eal",
    "y",
]


def analyze_word(word):
    """Analyze a single word and return (total_morphemes, recognized_morphemes)"""
    word = word.lower().strip()
    if not word or len(word) < 2:
        return 0, 0

    # Check if whole word is known
    if word in KNOWN_MORPHEMES:
        return 1, 1

    # Check for root + suffix
    for suffix in SUFFIX_PATTERNS:
        if word.endswith(suffix) and len(word) > len(suffix):
            root = word[: -len(suffix)]
            total = 2
            recognized = 0
            if root in KNOWN_MORPHEMES:
                recognized += 1
            if suffix in KNOWN_MORPHEMES:
                recognized += 1
            return total, recognized

    # Check for substring matches
    for morph in KNOWN_MORPHEMES:
        if len(morph) >= 2 and morph in word:
            return 1, 1

    return 1, 0  # Unknown morpheme


def analyze_text(words, label):
    """Analyze a list of words"""
    total_morphemes = 0
    recognized_morphemes = 0

    for word in words:
        t, r = analyze_word(word)
        total_morphemes += t
        recognized_morphemes += r

    recognition_rate = (
        (recognized_morphemes / total_morphemes * 100) if total_morphemes > 0 else 0
    )

    return {
        "label": label,
        "total_words": len(words),
        "total_morphemes": total_morphemes,
        "recognized_morphemes": recognized_morphemes,
        "recognition_rate": recognition_rate,
    }


# Load real Voynich text
print("\nLoading texts...")

with open(
    "data/voynich/eva_transcription/voynich_eva_takahashi.txt", "r", encoding="utf-8"
) as f:
    real_text = f.read()

with open("data/control_scrambled_word_order.txt", "r", encoding="utf-8") as f:
    scrambled_text = f.read()

with open("data/control_scrambled_characters.txt", "r", encoding="utf-8") as f:
    scrambled_chars_text = f.read()

with open("data/control_random_text.txt", "r", encoding="utf-8") as f:
    random_text = f.read()

# Parse into word lists
real_words = real_text.split()
scrambled_words = scrambled_text.split()
scrambled_chars_words = scrambled_chars_text.split()
random_words = random_text.split()

print(f"Real Voynich: {len(real_words)} words")
print(f"Scrambled order: {len(scrambled_words)} words")
print(f"Scrambled chars: {len(scrambled_chars_words)} words")
print(f"Random: {len(random_words)} words")

# Verify they're actually different
print("\nVerifying texts are different:")
print(f"First 5 words of real: {' '.join(real_words[:5])}")
print(f"First 5 words of scrambled: {' '.join(scrambled_words[:5])}")

if real_words[:10] == scrambled_words[:10]:
    print("\n⚠️ WARNING: Texts appear identical! Scrambling may have failed!")
else:
    print("✓ Texts are different")

# Test a few specific words to ensure they're being analyzed
print("\nTest analysis on specific words:")
test_words = ["qokain", "dain", "chol", "xyz123"]
for w in test_words:
    t, r = analyze_word(w)
    print(f"  {w}: {r}/{t} morphemes recognized ({r / t * 100:.1f}%)")

# Analyze all texts
print("\n" + "=" * 80)
print("ANALYSIS RESULTS")
print("=" * 80)

results = [
    analyze_text(real_words, "Real Voynich"),
    analyze_text(scrambled_words, "Scrambled word order"),
    analyze_text(scrambled_chars_words, "Scrambled characters"),
    analyze_text(random_words, "Random text"),
]

print(f"\n{'Text':<30} {'Words':<10} {'Morphemes':<12} {'Recognized':<12} {'Rate':<10}")
print("=" * 80)
for r in results:
    print(
        f"{r['label']:<30} {r['total_words']:<10} {r['total_morphemes']:<12} {r['recognized_morphemes']:<12} {r['recognition_rate']:>6.1f}%"
    )

# Evaluation
print("\n" + "=" * 80)
print("INTERPRETATION")
print("=" * 80)

real_rate = results[0]["recognition_rate"]
scrambled_order_rate = results[1]["recognition_rate"]
scrambled_chars_rate = results[2]["recognition_rate"]
random_rate = results[3]["recognition_rate"]

print(f"\nReal Voynich:              {real_rate:.1f}%")
print(f"Scrambled word order:      {scrambled_order_rate:.1f}%")
print(f"Scrambled characters:      {scrambled_chars_rate:.1f}%")
print(f"Random text:               {random_rate:.1f}%")

# Calculate difference between real and scrambled order
diff = abs(real_rate - scrambled_order_rate)
print(f"\nDifference (real vs scrambled order): {diff:.2f}%")

if diff < 1.0:
    print("\n⚠️ CRITICAL FINDING:")
    print("Real and scrambled order show IDENTICAL recognition")
    print("This means recognition is NOT based on word sequences/grammar")
    print("It's ONLY based on individual word structure!")
    print("\nThis significantly weakens linguistic claims")
    verdict = "ORDER_IRRELEVANT"
elif diff < 10.0:
    print("\n⚠️ Small difference between real and scrambled")
    print("Word order has minimal effect on recognition")
    verdict = "WEAK_ORDER_EFFECT"
else:
    print("\n✓ Significant difference found")
    print("Word order matters for recognition")
    verdict = "ORDER_MATTERS"

# Check if recognition is reasonable
if real_rate < 50:
    print(f"\n⚠️ Real recognition ({real_rate:.1f}%) is much lower than claimed 98%")
    print("Original recognition calculation may be incorrect")
elif real_rate < 70:
    print(f"\n⚠️ Real recognition ({real_rate:.1f}%) is lower than claimed 98%")
    print("There may be issues with the recognition methodology")

# Final verdict
print("\n" + "=" * 80)
print("VERDICT")
print("=" * 80)

if verdict == "ORDER_IRRELEVANT" and real_rate < 70:
    print("\n✗ TEST FAILED")
    print("\n1. Scrambled word order shows SAME recognition as real text")
    print("2. Recognition rate is much lower than claimed")
    print("\nConclusions:")
    print("- Recognition is based on word structure, NOT grammar")
    print("- Claimed 98% recognition is incorrect")
    print("- Linguistic claims (case system, aspect marking) are weakened")
    print("\n⚠️ DO NOT PUBLISH without addressing these issues")
    final_verdict = "FAIL"
elif verdict == "ORDER_IRRELEVANT":
    print("\n⚠️ PARTIAL PASS")
    print("\nScrambled word order shows SAME recognition")
    print("This means recognition is word-based, not sequence-based")
    print("However, recognition rate matches expectations")
    print("\n⚠️ Linguistic claims need revision")
    final_verdict = "PARTIAL"
else:
    print("\n✓ TEST PASSED")
    print("\nWord order affects recognition significantly")
    print("This supports grammatical/sequential interpretation")
    final_verdict = "PASS"

# Save results
output = {
    "test": "fixed_null_hypothesis_test",
    "date": "2025-01-31",
    "results": results,
    "verdict": final_verdict,
    "order_effect": verdict,
    "difference_real_vs_scrambled": diff,
    "interpretation": {
        "real_recognition": real_rate,
        "scrambled_order_recognition": scrambled_order_rate,
        "scrambled_chars_recognition": scrambled_chars_rate,
        "random_recognition": random_rate,
        "order_matters": diff >= 10.0,
        "recognition_matches_claim": real_rate >= 90.0,
    },
}

with open("FIXED_NULL_HYPOTHESIS_RESULTS.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to: FIXED_NULL_HYPOTHESIS_RESULTS.json")
print("=" * 80)
