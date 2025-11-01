"""
MANUAL PHASE 17 VALIDATION - Simple version without Unicode

This script:
1. Samples 50 random words from Phase 17 JSON
2. Shows their morphological decomposition
3. Creates a checklist for manual validation
4. Calculates error rate after manual review
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
print(f"[OK] Loaded {len(translations)} sentences")
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

print(f"[OK] Sampled {len(sample)} words for manual validation")
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
print("  [OK] CORRECT   - Root extraction looks good")
print("  [X]  WRONG     - Root extraction is clearly wrong")
print("  [?]  UNCERTAIN - Hard to tell, needs more context")
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
        issues.append("! SINGLE-LETTER ROOT")
    if len(root) == 2 and not suffixes:
        issues.append("! SHORT ROOT, NO SUFFIXES")
    if len(suffixes) >= 3:
        issues.append("! MANY SUFFIXES (possible over-stripping)")
    if not prefixes and not suffixes:
        issues.append("(i) STANDALONE (no segmentation)")

    # Print checklist entry
    print(f"[{i:2d}] {original:20s} -> {decomposition:45s}")
    if issues:
        print(f"     Issues: {', '.join(issues)}")
    print(f"     Assessment: [ ] CORRECT  [ ] WRONG  [ ] UNCERTAIN")
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

print("[OK] Validation checklist saved to: MANUAL_PHASE17_VALIDATION_CHECKLIST.json")
print()

# Print summary instructions
print("=" * 80)
print("NEXT STEPS")
print("=" * 80)
print()
print("1. Review the 50 words above")
print("2. For each word, mark your assessment (CORRECT / WRONG / UNCERTAIN)")
print("3. Edit MANUAL_PHASE17_VALIDATION_CHECKLIST.json:")
print(
    "   - Change 'assessment': null -> 'assessment': 'CORRECT' (or 'WRONG' or 'UNCERTAIN')"
)
print("4. Run calculate_phase17_error_rate.py to compute results")
print()
print("=" * 80)
print()
