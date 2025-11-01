"""
MANUAL PHASE 17 VALIDATION

This script:
1. Samples 50 random words from Phase 17 JSON
2. Shows their morphological decomposition
3. Creates a checklist for manual validation
4. Calculates error rate after manual review

Goal: Determine if Phase 17's root extraction is trustworthy
"""

import json
import random
from collections import Counter

print("=" * 80)
print("MANUAL PHASE 17 ROOT EXTRACTION VALIDATION")
print("=" * 80)
print()

# Set seed for reproducibility
random.seed(42)

# Load Phase 17 data
print("Loading Phase 17 data...")
with open("COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8") as f:
    data = json.load(f)

translations = data.get("translations", [])
print(f"✓ Loaded {len(translations)} sentences")
print()

# Collect all words with their morphology
all_words = []
for sentence in translations:
    for word_data in sentence.get("words", []):
        morphology = word_data.get("morphology", {})
        if morphology.get("root"):  # Only words with extracted roots
            all_words.append(
                {
                    "original": word_data.get("original", ""),
                    "root": morphology.get("root", ""),
                    "prefixes": morphology.get("prefixes", []),
                    "suffixes": morphology.get("suffixes", []),
                    "full_morphology": morphology,
                }
            )

print(f"Total words with morphology: {len(all_words):,}")
print()

# Sample 50 random words (stratified by root length)
# We want to oversample short roots since those are most suspicious

single_letter_words = [w for w in all_words if len(w["root"]) == 1]
two_letter_words = [w for w in all_words if len(w["root"]) == 2]
three_plus_words = [w for w in all_words if len(w["root"]) >= 3]

print(f"Single-letter roots: {len(single_letter_words):,} words")
print(f"Two-letter roots: {len(two_letter_words):,} words")
print(f"Three+ letter roots: {len(three_plus_words):,} words")
print()

# Sample strategy: 20 single-letter, 15 two-letter, 15 three+
sample = []

if len(single_letter_words) >= 20:
    sample.extend(random.sample(single_letter_words, 20))
else:
    sample.extend(single_letter_words)

if len(two_letter_words) >= 15:
    sample.extend(random.sample(two_letter_words, 15))
else:
    sample.extend(two_letter_words)

if len(three_plus_words) >= 15:
    sample.extend(random.sample(three_plus_words, 15))
else:
    sample.extend(three_plus_words)

# Fill to 50 if needed
while len(sample) < 50 and len(all_words) > len(sample):
    additional = random.choice([w for w in all_words if w not in sample])
    sample.append(additional)

print(f"✓ Sampled {len(sample)} words for manual validation")
print()

# Create validation checklist
print("=" * 80)
print("MANUAL VALIDATION CHECKLIST")
print("=" * 80)
print()
print("Instructions:")
print("For each word below, manually assess:")
print("  1. Does the root extraction make sense?")
print("  2. Is the root too short (single letter) to be plausible?")
print("  3. Could this be a whole word (no segmentation needed)?")
print("  4. Are the prefixes/suffixes correctly identified?")
print()
print("Mark each word as:")
print("  ✓ CORRECT   - Root extraction looks good")
print("  ✗ WRONG     - Root extraction is clearly wrong")
print("  ? UNCERTAIN - Hard to tell, needs more context")
print()
print("=" * 80)
print()

# Format validation checklist
validation_checklist = []

for i, word in enumerate(sample, 1):
    original = word["original"]
    root = word["root"]
    prefixes = word["prefixes"]
    suffixes = word["suffixes"]

    # Build decomposition string
    decomp_parts = []
    if prefixes:
        decomp_parts.append(f"[{'-'.join(prefixes)}]")
    decomp_parts.append(f"**{root}**")
    if suffixes:
        decomp_parts.append(f"[{'-'.join(suffixes)}]")

    decomposition = "-".join(decomp_parts)

    # Identify potential issues
    issues = []
    if len(root) == 1:
        issues.append("⚠️ SINGLE-LETTER ROOT")
    if len(root) == 2 and not suffixes:
        issues.append("⚠️ SHORT ROOT, NO SUFFIXES")
    if len(suffixes) >= 3:
        issues.append("⚠️ MANY SUFFIXES (possible over-stripping)")
    if not prefixes and not suffixes:
        issues.append("ℹ️  STANDALONE (no segmentation)")

    # Print checklist entry
    print(f"[{i:2d}] {original:20s} → {decomposition:40s}")
    if issues:
        print(f"     Issues: {', '.join(issues)}")
    print(f"     Assessment: [ ] ✓ CORRECT  [ ] ✗ WRONG  [ ] ? UNCERTAIN")
    print()

    # Store for later
    validation_checklist.append(
        {
            "id": i,
            "original": original,
            "root": root,
            "prefixes": prefixes,
            "suffixes": suffixes,
            "decomposition": decomposition,
            "root_length": len(root),
            "num_suffixes": len(suffixes),
            "num_prefixes": len(prefixes),
            "issues": issues,
            "assessment": None,  # Will be filled manually
        }
    )

print("=" * 80)
print()

# Save checklist to JSON for tracking
output = {
    "instructions": {
        "task": "Manually validate Phase 17 root extraction accuracy",
        "method": "For each word, assess if morphological decomposition is correct",
        "criteria": [
            "Does root extraction make sense?",
            "Is root too short to be plausible?",
            "Could this be a whole word (no segmentation)?",
            "Are affixes correctly identified?",
        ],
        "scoring": {
            "CORRECT": "Root extraction looks good",
            "WRONG": "Root extraction is clearly wrong",
            "UNCERTAIN": "Hard to tell without more context",
        },
    },
    "sample_statistics": {
        "total_words_sampled": len(sample),
        "single_letter_roots": sum(1 for w in sample if len(w["root"]) == 1),
        "two_letter_roots": sum(1 for w in sample if len(w["root"]) == 2),
        "three_plus_roots": sum(1 for w in sample if len(w["root"]) >= 3),
        "words_with_prefixes": sum(1 for w in sample if w["prefixes"]),
        "words_with_suffixes": sum(1 for w in sample if w["suffixes"]),
        "average_suffixes": sum(len(w["suffixes"]) for w in sample) / len(sample),
    },
    "validation_checklist": validation_checklist,
}

with open("MANUAL_PHASE17_VALIDATION_CHECKLIST.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("✓ Validation checklist saved to: MANUAL_PHASE17_VALIDATION_CHECKLIST.json")
print()

# Print summary instructions
print("=" * 80)
print("NEXT STEPS")
print("=" * 80)
print()
print("1. Review the 50 words above")
print("2. For each word, mark your assessment (✓ CORRECT / ✗ WRONG / ? UNCERTAIN)")
print("3. Edit MANUAL_PHASE17_VALIDATION_CHECKLIST.json:")
print(
    "   - Change 'assessment': null → 'assessment': 'CORRECT' (or 'WRONG' or 'UNCERTAIN')"
)
print("4. Run calculate_error_rate.py to compute results")
print()
print("=" * 80)
print()

# Create the error rate calculator script
calculator_script = '''"""
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
    print(f"⚠️  WARNING: {not_assessed} words not yet assessed!")
    print(f"   Please complete assessment before running this script.")
    print()

if total_assessed == 0:
    print("❌ No assessments found. Please fill in the checklist first.")
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
print(f"✓ CORRECT:   {correct:2d} ({correct_rate:5.1f}%)")
print(f"✗ WRONG:     {wrong:2d} ({wrong_rate:5.1f}%)")
print(f"? UNCERTAIN: {uncertain:2d} ({uncertain_rate:5.1f}%)")
print()
print(f"{'=' * 80}")
print(f"ERROR RATE: {error_rate:.1f}%")
print(f"{'=' * 80}")
print()

# Analyze by root length
single_letter_items = [item for item in checklist if item["root_length"] == 1]
two_letter_items = [item for item in checklist if item["root_length"] == 2]
three_plus_items = [item for item in checklist if item["root_length"] >= 3]

def calc_error_rate(items):
    if not items:
        return 0.0
    assessed = [i for i in items if i.get("assessment")]
    if not assessed:
        return 0.0
    wrong_count = sum(1 for i in assessed if i["assessment"] == "WRONG")
    uncertain_count = sum(1 for i in assessed if i["assessment"] == "UNCERTAIN")
    return (wrong_count + uncertain_count * 0.5) / len(assessed) * 100

single_error = calc_error_rate(single_letter_items)
two_error = calc_error_rate(two_letter_items)
three_error = calc_error_rate(three_plus_items)

print("ERROR RATE BY ROOT LENGTH:")
print(f"  Single-letter roots: {single_error:.1f}%")
print(f"  Two-letter roots:    {two_error:.1f}%")
print(f"  Three+ letter roots: {three_error:.1f}%")
print()

# Show wrong examples
if wrong_examples:
    print("=" * 80)
    print("EXAMPLES OF WRONG EXTRACTIONS:")
    print("=" * 80)
    print()
    for item in wrong_examples[:10]:  # Show first 10
        print(f"  {item['original']:20s} → {item['decomposition']}")
        if item['issues']:
            print(f"    Issues: {', '.join(item['issues'])}")
    print()

# Decision tree
print("=" * 80)
print("RECOMMENDATION:")
print("=" * 80)
print()

if error_rate < 10:
    print("✓ LOW ERROR RATE (<10%)")
    print("  → Phase 17 is MOSTLY TRUSTWORTHY")
    print("  → Can use high-frequency roots (>100 instances)")
    print("  → Filter single-letter roots with <500 instances")
    print("  → Recalculate semantic % (expect ~45-50%)")
elif error_rate < 20:
    print("⚠️ MODERATE ERROR RATE (10-20%)")
    print("  → Phase 17 has ISSUES but is salvageable")
    print("  → Remove all single-letter roots")
    print("  → Use only 3+ character roots with >100 instances")
    print("  → Recalculate semantic % (expect ~40-45%)")
else:
    print("✗ HIGH ERROR RATE (>20%)")
    print("  → Phase 17 is UNRELIABLE")
    print("  → Do NOT trust automatic root extraction")
    print("  → Rebuild morphological analyzer from scratch")
    print("  → Or manually validate each root individually")

print()

# Save results
results = {
    "summary": {
        "total_assessed": total_assessed,
        "correct": correct,
        "wrong": wrong,
        "uncertain": uncertain,
        "error_rate": error_rate,
        "correct_rate": correct_rate
    },
    "by_root_length": {
        "single_letter_error_rate": single_error,
        "two_letter_error_rate": two_error,
        "three_plus_error_rate": three_error
    },
    "wrong_examples": wrong_examples[:20],
    "uncertain_examples": uncertain_examples[:20]
}

with open("PHASE17_ERROR_RATE_RESULTS.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("✓ Results saved to: PHASE17_ERROR_RATE_RESULTS.json")
print()
'''

with open(
    "scripts/validation/calculate_phase17_error_rate.py", "w", encoding="utf-8"
) as f:
    f.write(calculator_script)

print(
    "✓ Created error rate calculator: scripts/validation/calculate_phase17_error_rate.py"
)
print()
