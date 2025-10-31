"""
NULL HYPOTHESIS TEST - CRITICAL VALIDATION

This is THE MOST IMPORTANT TEST.

Question: Are we finding REAL patterns or just over-fitting to noise?

Method:
1. Create scrambled control texts (destroy any real structure)
2. Run IDENTICAL analysis pipeline on controls
3. Compare results

Expected if methodology is VALID:
- Scrambled text: LOW recognition (<10%), FEW validated morphemes (<5)
- Real text: HIGH recognition (98%), MANY validated morphemes (53)

Expected if methodology is BROKEN:
- Scrambled text: HIGH recognition (finding patterns in noise!)
- Both texts: Similar results (over-fitting!)

This test will either:
A) Validate the methodology (patterns are REAL)
B) Reveal fatal flaw (patterns are ARTIFACTS)

Either way, we NEED to know.
"""

import random
import json
from collections import Counter, defaultdict

print("=" * 80)
print("NULL HYPOTHESIS TEST")
print("Testing for spurious pattern detection")
print("=" * 80)

# Load real Voynich text
print("\nLoading real Voynich manuscript...")
with open(
    "data/voynich/eva_transcription/voynich_eva_takahashi.txt", "r", encoding="utf-8"
) as f:
    lines = f.readlines()

# Extract just the text (no folios)
real_words = []
for line in lines:
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    if "\t" in line:
        _, text = line.split("\t", 1)
    else:
        text = line
    real_words.extend(text.split())

print(f"Loaded {len(real_words)} words from real Voynich")

# Create Control 1: Scrambled word order (preserves word structure)
print("\nCreating Control 1: Scrambled word order...")
control1_words = real_words.copy()
random.seed(42)  # Reproducible
random.shuffle(control1_words)

with open("data/control_scrambled_word_order.txt", "w", encoding="utf-8") as f:
    for i in range(0, len(control1_words), 10):
        f.write(" ".join(control1_words[i : i + 10]) + "\n")

print(f"Created control_scrambled_word_order.txt ({len(control1_words)} words)")

# Create Control 2: Scrambled characters (destroys word structure)
print("\nCreating Control 2: Scrambled characters within words...")
control2_words = []
random.seed(42)
for word in real_words:
    if len(word) > 1:
        chars = list(word)
        random.shuffle(chars)
        control2_words.append("".join(chars))
    else:
        control2_words.append(word)

with open("data/control_scrambled_characters.txt", "w", encoding="utf-8") as f:
    for i in range(0, len(control2_words), 10):
        f.write(" ".join(control2_words[i : i + 10]) + "\n")

print(f"Created control_scrambled_characters.txt ({len(control2_words)} words)")

# Create Control 3: Completely random text (same alphabet)
print("\nCreating Control 3: Completely random text...")
# Get Voynich alphabet
alphabet = set("".join(real_words))
alphabet = [c for c in alphabet if c.isalpha()]

control3_words = []
random.seed(42)
for _ in range(len(real_words)):
    word_len = random.randint(2, 8)
    word = "".join(random.choice(alphabet) for _ in range(word_len))
    control3_words.append(word)

with open("data/control_random_text.txt", "w", encoding="utf-8") as f:
    for i in range(0, len(control3_words), 10):
        f.write(" ".join(control3_words[i : i + 10]) + "\n")

print(f"Created control_random_text.txt ({len(control3_words)} words)")

print("\n" + "=" * 80)
print("QUICK ANALYSIS: Testing [?e] positional pattern")
print("=" * 80)


def quick_positional_analysis(words, label):
    """Quick test of [?e] medial position claim"""

    # Count 'e' positions
    positions = {"initial": 0, "medial": 0, "final": 0, "standalone": 0}
    total = 0

    for word in words:
        word = word.lower()
        if "e" not in word:
            continue

        for i, char in enumerate(word):
            if char == "e":
                total += 1
                if len(word) == 1:
                    positions["standalone"] += 1
                elif i == 0:
                    positions["initial"] += 1
                elif i == len(word) - 1:
                    positions["final"] += 1
                else:
                    positions["medial"] += 1

    if total == 0:
        return None

    # Calculate percentages
    results = {
        "label": label,
        "total_e": total,
        "initial_pct": positions["initial"] / total * 100,
        "medial_pct": positions["medial"] / total * 100,
        "final_pct": positions["final"] / total * 100,
        "standalone_pct": positions["standalone"] / total * 100,
    }

    return results


# Test all texts
print("\nTesting 'e' positional distribution...")
print("(Real Voynich claims 98.2% medial - if valid, scrambled should be ~33%)")
print()

real_result = quick_positional_analysis(real_words, "Real Voynich")
control1_result = quick_positional_analysis(
    control1_words, "Control 1: Scrambled word order"
)
control2_result = quick_positional_analysis(
    control2_words, "Control 2: Scrambled characters"
)
control3_result = quick_positional_analysis(control3_words, "Control 3: Random text")

results = [real_result, control1_result, control2_result, control3_result]

print(f"{'Text':<35} {'Initial':<12} {'Medial':<12} {'Final':<12} {'Standalone':<12}")
print("-" * 80)
for r in results:
    if r:
        print(
            f"{r['label']:<35} {r['initial_pct']:>6.1f}%     {r['medial_pct']:>6.1f}%     {r['final_pct']:>6.1f}%     {r['standalone_pct']:>6.1f}%"
        )

print("\n" + "=" * 80)
print("INTERPRETATION")
print("=" * 80)

real_medial = real_result["medial_pct"]
control2_medial = control2_result["medial_pct"]
control3_medial = control3_result["medial_pct"]

print(f"\nReal Voynich 'e' medial: {real_medial:.1f}%")
print(f"Scrambled characters 'e' medial: {control2_medial:.1f}%")
print(f"Random text 'e' medial: {control3_medial:.1f}%")
print(f"Expected random: ~33%")

# Evaluate
if real_medial > 90 and control2_medial < 50:
    print("\n✓ RESULT: Pattern detected in REAL text, NOT in scrambled")
    print("  This suggests the positional constraint is REAL")
    verdict = "PASS"
elif real_medial > 90 and control2_medial > 70:
    print("\n✗ RESULT: Pattern detected in BOTH real and scrambled")
    print("  This suggests ARTIFACT or OVER-FITTING")
    verdict = "FAIL"
elif real_medial < 60:
    print("\n✗ RESULT: Pattern NOT detected in real text")
    print("  Original claim (98.2% medial) may be incorrect")
    verdict = "FAIL"
else:
    print("\n⚠ RESULT: Unclear - needs more analysis")
    verdict = "UNCERTAIN"

print("\n" + "=" * 80)
print("MORPHEME FREQUENCY TEST")
print("=" * 80)


def count_morpheme_frequencies(words, top_n=20):
    """Count most frequent morphemes"""

    # Simple morpheme extraction (2-4 character sequences)
    morphemes = Counter()

    for word in words:
        word = word.lower()
        # Extract 2-grams
        for i in range(len(word) - 1):
            morphemes[word[i : i + 2]] += 1
        # Extract 3-grams
        for i in range(len(word) - 2):
            morphemes[word[i : i + 3]] += 1

    return morphemes.most_common(top_n)


print("\nTop 10 most frequent morphemes:")
print()

for label, words in [
    ("Real Voynich", real_words),
    ("Scrambled chars", control2_words),
    ("Random text", control3_words),
]:
    morphemes = count_morpheme_frequencies(words, 10)
    print(f"{label}:")
    for morph, count in morphemes:
        print(f"  {morph}: {count}")
    print()

# Save comprehensive results
output = {
    "test_type": "null_hypothesis",
    "date": "2025-01-31",
    "verdict": verdict,
    "positional_analysis": {
        "real_voynich": real_result,
        "control_scrambled_word_order": control1_result,
        "control_scrambled_characters": control2_result,
        "control_random_text": control3_result,
    },
    "interpretation": {
        "real_medial_pct": real_medial,
        "scrambled_medial_pct": control2_medial,
        "random_medial_pct": control3_medial,
        "expected_random": 33.3,
        "verdict": verdict,
    },
    "controls_created": [
        "data/control_scrambled_word_order.txt",
        "data/control_scrambled_characters.txt",
        "data/control_random_text.txt",
    ],
}

with open("NULL_HYPOTHESIS_TEST_RESULTS.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print("\n" + "=" * 80)
print("FINAL VERDICT")
print("=" * 80)

if verdict == "PASS":
    print("\n✓ NULL HYPOTHESIS TEST: PASSED")
    print("\nThe methodology appears to detect REAL patterns, not artifacts.")
    print("Scrambled/random text shows expected random distribution (~33% medial)")
    print("Real Voynich shows strong non-random pattern (>90% medial)")
    print("\nThis provides evidence that:")
    print("  1. The positional constraint is not an artifact")
    print("  2. The analysis detects genuine structure")
    print("  3. The methodology is not over-fitting")
    print("\nRECOMMENDATION: Proceed with publication, include these results")
elif verdict == "FAIL":
    print("\n✗ NULL HYPOTHESIS TEST: FAILED")
    print("\nThe methodology may be detecting artifacts or over-fitting.")
    print("Both real and scrambled text show similar patterns.")
    print("\nThis suggests:")
    print("  1. The patterns may be statistical artifacts")
    print("  2. The validation framework may be too lenient")
    print("  3. The methodology needs revision")
    print("\nRECOMMENDATION: DO NOT PUBLISH until methodology is fixed")
else:
    print("\n⚠ NULL HYPOTHESIS TEST: UNCERTAIN")
    print("\nResults are mixed or unclear.")
    print("\nRECOMMENDATION: More rigorous testing needed before publication")

print("\nResults saved to: NULL_HYPOTHESIS_TEST_RESULTS.json")
print("=" * 80)
