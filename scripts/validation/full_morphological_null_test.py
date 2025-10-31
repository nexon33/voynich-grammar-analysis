"""
COMPREHENSIVE NULL HYPOTHESIS TEST

The quick 'e' position test showed problems.
Now test the FULL morphological recognition claim.

Question: Does the Phase 17 translation system give high recognition to scrambled text?

This is THE CRITICAL TEST.
"""

import json
import re
from collections import Counter

print("=" * 80)
print("COMPREHENSIVE MORPHOLOGICAL NULL HYPOTHESIS TEST")
print("Testing if recognition system over-fits to noise")
print("=" * 80)

# Simple morpheme recognizer (mimics Phase 17 approach)
KNOWN_MORPHEMES = {
    # From Phase 17 and our session
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
    # Case suffixes
    "ain": "GEN",
    "aiin": "GEN",
    "edy": "LOC",
    "ody": "LOC",
    "eol": "INST",
    "ear": "DIR",
    "eal": "DEF",
}

# Suffix patterns
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


def analyze_text_recognition(text_file, label):
    """Analyze recognition rate for a text file"""

    with open(text_file, "r", encoding="utf-8") as f:
        text = f.read()

    words = text.split()

    total_words = 0
    recognized_morphemes = 0
    total_morphemes = 0

    for word in words:
        word = word.lower().strip()
        if not word or len(word) < 2:
            continue

        total_words += 1
        word_recognized = False

        # Check if whole word is known
        if word in KNOWN_MORPHEMES:
            recognized_morphemes += 1
            total_morphemes += 1
            word_recognized = True
            continue

        # Check for root + suffix pattern
        for suffix in SUFFIX_PATTERNS:
            if word.endswith(suffix) and len(word) > len(suffix):
                root = word[: -len(suffix)]
                total_morphemes += 2  # root + suffix

                if root in KNOWN_MORPHEMES:
                    recognized_morphemes += 1  # root known
                if suffix in KNOWN_MORPHEMES:
                    recognized_morphemes += 1  # suffix known

                word_recognized = True
                break

        # Check for substring matches
        if not word_recognized:
            found_any = False
            for morph in KNOWN_MORPHEMES:
                if len(morph) >= 2 and morph in word:
                    recognized_morphemes += 1
                    total_morphemes += 1
                    found_any = True
                    break

            if not found_any:
                total_morphemes += 1  # Count as unknown morpheme

    recognition_rate = (
        (recognized_morphemes / total_morphemes * 100) if total_morphemes > 0 else 0
    )

    return {
        "label": label,
        "total_words": total_words,
        "total_morphemes": total_morphemes,
        "recognized_morphemes": recognized_morphemes,
        "recognition_rate": recognition_rate,
    }


# Test all texts
print("\nAnalyzing recognition rates across all texts...")
print("(If methodology is valid, scrambled should be <10%, real should be >90%)")
print()

# Load and analyze each text
texts = [
    ("data/voynich/eva_transcription/voynich_eva_takahashi.txt", "Real Voynich"),
    ("data/control_scrambled_word_order.txt", "Control 1: Scrambled word order"),
    ("data/control_scrambled_characters.txt", "Control 2: Scrambled characters"),
    ("data/control_random_text.txt", "Control 3: Random text"),
]

results = []
for filepath, label in texts:
    try:
        result = analyze_text_recognition(filepath, label)
        results.append(result)
    except FileNotFoundError:
        print(f"Warning: {filepath} not found")

# Display results
print(f"{'Text':<40} {'Words':<10} {'Morphemes':<12} {'Recognized':<12} {'Rate':<10}")
print("=" * 90)
for r in results:
    print(
        f"{r['label']:<40} {r['total_words']:<10} {r['total_morphemes']:<12} {r['recognized_morphemes']:<12} {r['recognition_rate']:>6.1f}%"
    )

print("\n" + "=" * 80)
print("NULL HYPOTHESIS EVALUATION")
print("=" * 80)

real = results[0]
scrambled_order = results[1]
scrambled_chars = results[2]
random_text = results[3]

print(f"\nReal Voynich recognition:           {real['recognition_rate']:.1f}%")
print(f"Scrambled word order recognition:   {scrambled_order['recognition_rate']:.1f}%")
print(f"Scrambled characters recognition:   {scrambled_chars['recognition_rate']:.1f}%")
print(f"Random text recognition:            {random_text['recognition_rate']:.1f}%")
print(f"\nExpected for scrambled: <10%")
print(f"Expected for real (if valid): >90%")

# Verdict
print("\n" + "=" * 80)
print("VERDICT")
print("=" * 80)

if real["recognition_rate"] > 90 and scrambled_chars["recognition_rate"] < 20:
    print("\n✓ TEST PASSED")
    print("\nReal text shows high recognition (>90%)")
    print("Scrambled text shows low recognition (<20%)")
    print("\nThis suggests the morphological patterns are REAL")
    verdict = "PASS"

elif real["recognition_rate"] > 90 and scrambled_chars["recognition_rate"] > 50:
    print("\n✗ TEST FAILED")
    print("\nBoth real and scrambled text show high recognition")
    print("This suggests OVER-FITTING or ARTIFACT")
    print("\nThe recognition system may be finding patterns in noise!")
    verdict = "FAIL"

elif real["recognition_rate"] < 70:
    print("\n✗ TEST FAILED")
    print("\nReal text shows unexpectedly low recognition")
    print("Original claim of 98% may be incorrect")
    verdict = "FAIL"

else:
    print("\n⚠ UNCERTAIN")
    print("\nResults are mixed - needs deeper analysis")
    verdict = "UNCERTAIN"

# Specific concern: scrambled word order
if scrambled_order["recognition_rate"] > 80:
    print("\n⚠ CRITICAL CONCERN:")
    print(
        f"Scrambled word order shows {scrambled_order['recognition_rate']:.1f}% recognition"
    )
    print("This means recognition is NOT about word sequences/grammar")
    print("It's just about individual word structure!")
    print("\nThis WEAKENS the linguistic claims significantly")

# Save results
output = {
    "test": "comprehensive_morphological_null_hypothesis",
    "date": "2025-01-31",
    "results": results,
    "verdict": verdict,
    "interpretation": {
        "real_recognition": real["recognition_rate"],
        "scrambled_chars_recognition": scrambled_chars["recognition_rate"],
        "random_recognition": random_text["recognition_rate"],
        "threshold_passed": (
            real["recognition_rate"] > 90 and scrambled_chars["recognition_rate"] < 20
        ),
    },
}

with open("NULL_HYPOTHESIS_COMPREHENSIVE_RESULTS.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print("\n" + "=" * 80)
print("FINAL RECOMMENDATION")
print("=" * 80)

if verdict == "PASS":
    print("\n✓ Methodology appears sound")
    print("✓ Include these null hypothesis results in publication")
    print("✓ This strengthens credibility significantly")

elif verdict == "FAIL":
    print("\n✗ Methodology has serious issues")
    print("✗ DO NOT PUBLISH without fixing validation framework")
    print("✗ The recognition system may be broken")

else:
    print("\n⚠ More investigation needed")
    print("⚠ Consider additional null hypothesis tests")
    print("⚠ Proceed with caution")

print(f"\nResults saved to: NULL_HYPOTHESIS_COMPREHENSIVE_RESULTS.json")
print("=" * 80)
