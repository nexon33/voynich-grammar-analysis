"""
Calculate error rate from manual Phase 17 validation

After you've filled in assessments in MANUAL_PHASE17_VALIDATION_CHECKLIST.json,
run this script to calculate the error rate.
"""

import json

print("=" * 80)
print("PHASE 17 ERROR RATE CALCULATION")
print("=" * 80)
print()

# Load checklist with assessments
with open("MANUAL_PHASE17_VALIDATION_CHECKLIST.json", "r", encoding="utf-8") as f:
    data = json.load(f)

checklist = data["validation_checklist"]

# Count assessments
correct = 0
wrong = 0
uncertain = 0
not_assessed = 0

wrong_examples = []
uncertain_examples = []

for item in checklist:
    assessment = item.get("assessment")

    if assessment == "CORRECT":
        correct += 1
    elif assessment == "WRONG":
        wrong += 1
        wrong_examples.append(item)
    elif assessment == "UNCERTAIN":
        uncertain += 1
        uncertain_examples.append(item)
    else:
        not_assessed += 1

total_assessed = correct + wrong + uncertain

if not_assessed > 0:
    print(f"WARNING: {not_assessed} words not yet assessed!")
    print(f"   Please complete assessment before running this script.")
    print()

if total_assessed == 0:
    print("ERROR: No assessments found. Please fill in the checklist first.")
    exit(1)

# Calculate rates
correct_rate = correct / total_assessed * 100
wrong_rate = wrong / total_assessed * 100
uncertain_rate = uncertain / total_assessed * 100

# Error rate = WRONG + (UNCERTAIN / 2)
# We count uncertain as half-wrong
error_rate = (wrong + uncertain * 0.5) / total_assessed * 100

print(f"Total words assessed: {total_assessed}")
print()
print(f"[OK] CORRECT:   {correct:2d} ({correct_rate:5.1f}%)")
print(f"[X]  WRONG:     {wrong:2d} ({wrong_rate:5.1f}%)")
print(f"[?]  UNCERTAIN: {uncertain:2d} ({uncertain_rate:5.1f}%)")
print()
print(f"{'=' * 80}")
print(f"ERROR RATE: {error_rate:.1f}% (counting uncertain as 0.5 wrong)")
print(f"{'=' * 80}")
print()

# Analyze by root length
single_letter_items = [item for item in checklist if item["root_length"] == 1]
two_letter_items = [item for item in checklist if item["root_length"] == 2]
three_plus_items = [item for item in checklist if item["root_length"] >= 3]


def calc_error_rate(items):
    if not items:
        return 0.0, 0, 0, 0
    assessed = [i for i in items if i.get("assessment")]
    if not assessed:
        return 0.0, 0, 0, len(items)
    wrong_count = sum(1 for i in assessed if i["assessment"] == "WRONG")
    uncertain_count = sum(1 for i in assessed if i["assessment"] == "UNCERTAIN")
    correct_count = sum(1 for i in assessed if i["assessment"] == "CORRECT")
    error = (wrong_count + uncertain_count * 0.5) / len(assessed) * 100
    return error, wrong_count, uncertain_count, correct_count


single_error, single_wrong, single_uncertain, single_correct = calc_error_rate(
    single_letter_items
)
two_error, two_wrong, two_uncertain, two_correct = calc_error_rate(two_letter_items)
three_error, three_wrong, three_uncertain, three_correct = calc_error_rate(
    three_plus_items
)

print("ERROR RATE BY ROOT LENGTH:")
print()
print(f"Single-letter roots ({len(single_letter_items)} words):")
print(
    f"  CORRECT: {single_correct}, WRONG: {single_wrong}, UNCERTAIN: {single_uncertain}"
)
print(f"  Error rate: {single_error:.1f}%")
print()
print(f"Two-letter roots ({len(two_letter_items)} words):")
print(f"  CORRECT: {two_correct}, WRONG: {two_wrong}, UNCERTAIN: {two_uncertain}")
print(f"  Error rate: {two_error:.1f}%")
print()
print(f"Three+ letter roots ({len(three_plus_items)} words):")
print(f"  CORRECT: {three_correct}, WRONG: {three_wrong}, UNCERTAIN: {three_uncertain}")
print(f"  Error rate: {three_error:.1f}%")
print()

# Show wrong examples
if wrong_examples:
    print("=" * 80)
    print("EXAMPLES OF WRONG EXTRACTIONS:")
    print("=" * 80)
    print()
    for item in wrong_examples[:10]:  # Show first 10
        print(f"  {item['original']:20s} -> {item['decomposition']}")
        if item["issues"]:
            print(f"    Issues: {', '.join(item['issues'])}")
        if "assessment_reason" in item:
            print(f"    Reason: {item['assessment_reason']}")
        print()

# Decision tree
print("=" * 80)
print("RECOMMENDATION:")
print("=" * 80)
print()

# Adjust for biased sample
# We oversampled single-letter roots (20/50 = 40% of sample)
# But in real corpus: single-letter = 5,954/37,119 = 16%
# Adjust error rate for real distribution

real_single_pct = 0.16
real_two_pct = 0.255  # 9,459/37,119
real_three_pct = 0.585  # 21,706/37,119

adjusted_error = (
    single_error * real_single_pct
    + two_error * real_two_pct
    + three_error * real_three_pct
)

print(f"BIASED SAMPLE ERROR RATE: {error_rate:.1f}%")
print(f"  (We oversampled single-letter roots to stress-test Phase 17)")
print()
print(f"ADJUSTED FOR REAL CORPUS DISTRIBUTION: {adjusted_error:.1f}%")
print(f"  Single-letter: 16% of corpus, error rate {single_error:.1f}%")
print(f"  Two-letter:    25.5% of corpus, error rate {two_error:.1f}%")
print(f"  Three+ letter: 58.5% of corpus, error rate {three_error:.1f}%")
print()

if adjusted_error < 10:
    print("[OK] LOW ERROR RATE (<10%)")
    print()
    print("  -> Phase 17 is MOSTLY TRUSTWORTHY")
    print("  -> Can use high-frequency roots (>100 instances)")
    print("  -> MUST filter single-letter roots with <500 instances")
    print("  -> Recalculate semantic % (expect ~45-50%)")
    print()
    print("ACTION ITEMS:")
    print("  1. Remove single-letter roots with <500 instances")
    print(
        "  2. Keep only: qok, qot, ok, sho, cho, dain, ar, ch, sh, or, ol, dar, ain, al"
    )
    print("  3. Add validated single letters IF frequency >500 (check: e, a, y, eey)")
    print("  4. Recalculate semantic % with filtered vocabulary")

elif adjusted_error < 20:
    print("[!] MODERATE ERROR RATE (10-20%)")
    print()
    print("  -> Phase 17 has ISSUES but is salvageable")
    print("  -> Remove ALL single-letter roots")
    print("  -> Use only 2+ character roots with >100 instances")
    print("  -> Recalculate semantic % (expect ~40-45%)")
    print()
    print("ACTION ITEMS:")
    print("  1. Remove ALL single-letter roots")
    print("  2. Keep only 2+ character roots with >100 instances")
    print("  3. Manually validate 2-letter roots (check patterns)")
    print("  4. Recalculate semantic % with filtered vocabulary")

else:
    print("[X] HIGH ERROR RATE (>20%)")
    print()
    print("  -> Phase 17 is UNRELIABLE")
    print("  -> Do NOT trust automatic root extraction")
    print("  -> Rebuild morphological analyzer from scratch")
    print("  -> Or manually validate each root individually")
    print()
    print("ACTION ITEMS:")
    print("  1. Do NOT use Phase 17 data for vocabulary")
    print("  2. Rebuild morphological analyzer with validation")
    print("  3. Or manually decode roots one by one")
    print("  4. Start from high-confidence core only")

print()

# Save results
results = {
    "summary": {
        "total_assessed": total_assessed,
        "correct": correct,
        "wrong": wrong,
        "uncertain": uncertain,
        "error_rate_biased_sample": error_rate,
        "error_rate_adjusted": adjusted_error,
        "correct_rate": correct_rate,
    },
    "by_root_length": {
        "single_letter": {
            "count": len(single_letter_items),
            "error_rate": single_error,
            "wrong": single_wrong,
            "uncertain": single_uncertain,
            "correct": single_correct,
        },
        "two_letter": {
            "count": len(two_letter_items),
            "error_rate": two_error,
            "wrong": two_wrong,
            "uncertain": two_uncertain,
            "correct": two_correct,
        },
        "three_plus": {
            "count": len(three_plus_items),
            "error_rate": three_error,
            "wrong": three_wrong,
            "uncertain": three_uncertain,
            "correct": three_correct,
        },
    },
    "wrong_examples": [
        {
            "original": ex["original"],
            "decomposition": ex["decomposition"],
            "reason": ex.get("assessment_reason", ""),
        }
        for ex in wrong_examples[:20]
    ],
    "uncertain_examples": [
        {
            "original": ex["original"],
            "decomposition": ex["decomposition"],
            "reason": ex.get("assessment_reason", ""),
        }
        for ex in uncertain_examples[:20]
    ],
}

with open("PHASE17_ERROR_RATE_RESULTS.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("=" * 80)
print("[OK] Results saved to: PHASE17_ERROR_RATE_RESULTS.json")
print("=" * 80)
print()
