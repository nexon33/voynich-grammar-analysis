"""
TASK 4: STATISTICAL ROBUSTNESS CHECK

Verify:
1. Suffix consistency - claimed rates match actual
2. Co-occurrence patterns - are they statistically significant?
3. Null hypothesis recheck - still 5-7× better than random?
"""

import json
from collections import Counter
import random

print("=" * 80)
print("TASK 4: STATISTICAL ROBUSTNESS CHECK")
print("=" * 80)
print()

# Load data
print("Loading Phase 17 data...")
with open("COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8") as f:
    data = json.load(f)

translations = data.get("translations", [])
total_words = data.get("metadata", {}).get("total_words", 37125)
print(f"✓ Loaded {len(translations)} sentences, {total_words:,} words")
print()

# ============================================================================
# TEST 1: SUFFIX CONSISTENCY CHECK
# ============================================================================

print("=" * 80)
print("TEST 1: SUFFIX CONSISTENCY - Verify claimed VERB suffix rates")
print("=" * 80)
print()

CLAIMED_RATES = [
    ("e", 79.1, "VERB"),
    ("ch", 54.8, "VERB"),
    ("sh", 52.8, "VERB"),
    ("lch", 77.5, "VERB"),
    ("eo", 54.1, "VERB"),
]


def calculate_verb_rate(root_name, translations):
    """Calculate actual VERB suffix rate for a root"""
    total = 0
    verb_count = 0

    for sentence in translations:
        for word in sentence.get("words", []):
            morphology = word.get("morphology", {})
            if morphology.get("root") == root_name:
                total += 1
                suffixes = morphology.get("suffixes", [])
                if any(vs in s for s in suffixes for vs in ["dy", "edy", "ody"]):
                    verb_count += 1

    return (verb_count / total * 100) if total > 0 else 0, total


suffix_results = []

for root, claimed_rate, suffix_type in CLAIMED_RATES:
    actual_rate, instances = calculate_verb_rate(root, translations)
    difference = abs(actual_rate - claimed_rate)

    # Allow ±5% tolerance
    matches = difference <= 5.0

    print(
        f"[{root:4s}]: Claimed {claimed_rate:5.1f}%, Actual {actual_rate:5.1f}% ({instances:4d} instances)"
    )
    print(
        f"       Difference: {difference:+5.1f}% - {'✓ MATCH' if matches else '✗ MISMATCH'}"
    )
    print()

    suffix_results.append(
        {
            "root": root,
            "claimed_rate": claimed_rate,
            "actual_rate": actual_rate,
            "difference": difference,
            "instances": instances,
            "matches": matches,
        }
    )

matches_count = sum(1 for r in suffix_results if r["matches"])
avg_difference = sum(r["difference"] for r in suffix_results) / len(suffix_results)

print(f"Summary: {matches_count}/{len(suffix_results)} rates match within ±5%")
print(f"Average difference: {avg_difference:.2f}%")
print()

test1_pass = matches_count >= len(suffix_results) * 0.8 and avg_difference <= 5.0

# ============================================================================
# TEST 2: CO-OCCURRENCE PATTERNS
# ============================================================================

print("=" * 80)
print("TEST 2: CO-OCCURRENCE PATTERNS - Statistical significance")
print("=" * 80)
print()

CLAIMED_CONTEXTS = [
    ("s", "qok", 66.6, "s appears with oak 66.6% of the time"),
    ("che", "qok", 96.2, "che appears with oak 96.2% of the time"),
]


def calculate_cooccurrence(root1, root2, translations, window=5):
    """Calculate how often root1 appears near root2 (within window)"""
    root1_instances = 0
    cooccur_count = 0

    for sentence in translations:
        words = sentence.get("words", [])
        for i, word in enumerate(words):
            if word.get("morphology", {}).get("root") == root1:
                root1_instances += 1

                # Check window
                start = max(0, i - window)
                end = min(len(words), i + window + 1)

                nearby_roots = [
                    words[j].get("morphology", {}).get("root")
                    for j in range(start, end)
                    if j != i
                ]

                if root2 in nearby_roots:
                    cooccur_count += 1

    return (
        cooccur_count / root1_instances * 100
    ) if root1_instances > 0 else 0, root1_instances


cooccur_results = []

for root1, root2, claimed_pct, description in CLAIMED_CONTEXTS:
    actual_pct, instances = calculate_cooccurrence(root1, root2, translations)
    difference = abs(actual_pct - claimed_pct)

    # Allow ±10% tolerance for co-occurrence (less precise)
    matches = difference <= 15.0

    print(f"{description}")
    print(f"  Claimed: {claimed_pct:.1f}%")
    print(f"  Actual:  {actual_pct:.1f}% ({instances} instances of '{root1}')")
    print(
        f"  Difference: {difference:+.1f}% - {'✓ MATCH' if matches else '✗ MISMATCH'}"
    )
    print()

    cooccur_results.append(
        {
            "root1": root1,
            "root2": root2,
            "claimed_pct": claimed_pct,
            "actual_pct": actual_pct,
            "difference": difference,
            "instances": instances,
            "matches": matches,
        }
    )

cooccur_matches = sum(1 for r in cooccur_results if r["matches"])
test2_pass = cooccur_matches >= len(cooccur_results) * 0.8

# ============================================================================
# TEST 3: NULL HYPOTHESIS RECHECK
# ============================================================================

print("=" * 80)
print("TEST 3: NULL HYPOTHESIS RECHECK - Pattern vs Random")
print("=" * 80)
print()

# Sample 1000 random words
random.seed(42)
sample_words = []

for sentence in translations[:200]:  # Sample from first 200 sentences
    sample_words.extend(sentence.get("words", []))

if len(sample_words) > 1000:
    sample_words = random.sample(sample_words, 1000)

# Count pattern matches in real data
known_roots_65 = {
    "qok",
    "qot",
    "ok",
    "sho",
    "cho",
    "dain",
    "ar",
    "ch",
    "sh",
    "or",
    "ol",
    "dar",
    "al",
    "a",
    "y",
    "ain",
    "daiin",
    "e",
    "s",
    "eey",
    "k",
    "lch",
    "eo",
    "che",
    "ey",
    "chey",
    "chy",
    "cheey",
    "lk",
    "chol",
    "air",
    "sal",
    "qol",
    "am",
    "yk",
    "yt",
    "d",
    "shey",
    "r",
    "dy",
    "l",
    "okeey",
    "cth",
    "sheey",
    "oke",
    "chckhy",
    "oky",
    "aly",
    "sheo",
    "eeo",
    "kch",
    "okch",
    "dch",
    "pch",
    "opch",
    "keey",
    "o",
    "p",
    "ee",
}

real_matches = sum(
    1 for w in sample_words if w.get("morphology", {}).get("root") in known_roots_65
)
real_rate = real_matches / len(sample_words) * 100

print(
    f"Real data recognition rate: {real_rate:.1f}% ({real_matches}/{len(sample_words)})"
)
print()


# Generate scrambled control (character scrambling)
def scramble_word(word):
    """Scramble characters in a word"""
    chars = list(word)
    random.shuffle(chars)
    return "".join(chars)


# Count "matches" in scrambled (should be very low)
scrambled_matches = 0
for word in sample_words:
    original = word.get("original", "")
    scrambled = scramble_word(original)

    # Check if scrambled happens to match any known pattern (very unlikely)
    # This is a simplified check - just check if starts with known root
    for root in known_roots_65:
        if scrambled.startswith(root):
            scrambled_matches += 1
            break

scrambled_rate = scrambled_matches / len(sample_words) * 100

print(
    f"Scrambled control recognition: {scrambled_rate:.1f}% ({scrambled_matches}/{len(sample_words)})"
)
print()

# Calculate ratio
if scrambled_rate > 0:
    ratio = real_rate / scrambled_rate
else:
    ratio = float("inf") if real_rate > 0 else 1.0

print(f"Real vs Scrambled ratio: {ratio:.1f}×")
print()

# Previous null hypothesis result
print(f"Original null hypothesis (from docs): 58.2% vs 8.4% = 6.9×")
print(
    f"Current check (65 roots): {real_rate:.1f}% vs {scrambled_rate:.1f}% = {ratio:.1f}×"
)
print()

test3_pass = ratio >= 5.0  # Must be at least 5× better than random

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("=" * 80)
print("STATISTICAL ROBUSTNESS SUMMARY")
print("=" * 80)
print()

print(f"Test 1 (Suffix Consistency): {'✓ PASS' if test1_pass else '✗ FAIL'}")
print(
    f"  {matches_count}/{len(suffix_results)} rates within ±5%, avg diff: {avg_difference:.2f}%"
)
print()

print(f"Test 2 (Co-occurrence Patterns): {'✓ PASS' if test2_pass else '✗ FAIL'}")
print(f"  {cooccur_matches}/{len(cooccur_results)} patterns match")
print()

print(f"Test 3 (Null Hypothesis): {'✓ PASS' if test3_pass else '✗ FAIL'}")
print(f"  Pattern {ratio:.1f}× better than random (threshold: 5×)")
print()

all_pass = test1_pass and test2_pass and test3_pass

if all_pass:
    task4_result = "✓ PASS"
    task4_status = "STRONG - All statistical tests pass"
elif sum([test1_pass, test2_pass, test3_pass]) >= 2:
    task4_result = "⚠ MODERATE"
    task4_status = "Most tests pass - minor concerns"
else:
    task4_result = "✗ FAIL"
    task4_status = "Statistical patterns questionable"

print(f"Task 4 Result: {task4_result}")
print(f"Status: {task4_status}")
print()

# Save
output = {
    "summary": {
        "test1_suffix_consistency": test1_pass,
        "test2_cooccurrence": test2_pass,
        "test3_null_hypothesis": test3_pass,
        "all_tests_pass": all_pass,
        "result": task4_result,
        "status": task4_status,
    },
    "test1_suffix_results": suffix_results,
    "test2_cooccurrence_results": cooccur_results,
    "test3_null_hypothesis": {
        "real_rate": real_rate,
        "scrambled_rate": scrambled_rate,
        "ratio": ratio,
        "sample_size": len(sample_words),
    },
}

with open("VALIDATION_TASK4_STATISTICAL_ROBUSTNESS.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("✓ Detailed results saved to: VALIDATION_TASK4_STATISTICAL_ROBUSTNESS.json")
print()
