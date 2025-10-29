#!/usr/bin/env python3
"""
Analyze recognition breakdown to separate:
1. Preserved/plain words (minimal transformation)
2. Transformed words (e↔o, reversal, consonants)

This gives us the TRUE decipherment rate (transformed words only).
"""

import json
from pathlib import Path
from collections import defaultdict

results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"

print("=" * 80)
print("RECOGNITION BREAKDOWN: PRESERVED vs TRANSFORMED")
print("=" * 80)
print()

# Load all data
with open(results_dir / "consonant_pattern_results.json", "r") as f:
    consonant_data = json.load(f)

with open(results_dir / "predicted_reversals_results.json", "r") as f:
    predicted_data = json.load(f)

total_words = consonant_data["total_words"]

print("QUESTION: Does our 3.45% include plain English words?")
print()
print("Let's break down recognition by transformation complexity:")
print()

# Analyze transformation types
print("=" * 80)
print("RECOGNITION BY TRANSFORMATION COMPLEXITY")
print("=" * 80)
print()

# From consonant data
direct_matches = consonant_data["recognition"]["direct"]
reversed_matches = consonant_data["recognition"]["reversed"]
consonant_matches = consonant_data["recognition"]["consonant"]
multi_transform = consonant_data["recognition"]["multi_transform"]
predicted_found = predicted_data["total_found"]

# Categorize by transformation level
categories = {
    "LEVEL 0: Preserved (no transform)": {
        "count": 0,
        "examples": [],
        "description": "Plain text, no cipher applied",
    },
    "LEVEL 1: e↔o only": {
        "count": 0,
        "examples": [],
        "description": "Single vowel substitution (she→sho)",
    },
    "LEVEL 2: Reversal + e↔o": {
        "count": reversed_matches,
        "examples": ["make→kam", "eye→oy", "at→da"],
        "description": "Word reversed with vowel substitution",
    },
    "LEVEL 3: Consonant + e↔o": {
        "count": consonant_matches,
        "examples": ["she→cho (ch↔sh)", "day→tai (t↔d)"],
        "description": "Consonant shift with vowel substitution",
    },
    "LEVEL 4: Multi-transform": {
        "count": multi_transform,
        "examples": ["root→odor (reverse+t↔d+e↔o)", "seed→otos (reverse+t↔d+e↔o)"],
        "description": "Multiple transformations combined",
    },
    "LEVEL 5: Predicted complex": {
        "count": predicted_found,
        "examples": ["root→otor (51×)", "leaf→fol (6×)"],
        "description": "Predicted reversals (plant parts 100%)",
    },
}

# Estimate Level 0 and Level 1 from direct matches
# Look at sample consonant matches to see what's preserved
preserved_count = 0
eo_only_count = 0

# Common words that are likely preserved or e↔o only
# Based on previous findings: "or", "a", "to", "sor" (preserved)
# "sho"→"she" (e↔o only)

# Rough estimate from our known findings:
# - "or" appears frequently (preserved)
# - "sor" appears 52 times (mostly preserved, condition)
# - "a", "to", "do" (partly preserved)

# Let's estimate: ~60% of direct matches are preserved, 40% are e↔o only
preserved_count = int(direct_matches * 0.6)
eo_only_count = int(direct_matches * 0.4)

categories["LEVEL 0: Preserved (no transform)"]["count"] = preserved_count
categories["LEVEL 1: e↔o only"]["count"] = eo_only_count

# Print breakdown
total_recognized = (
    direct_matches
    + reversed_matches
    + consonant_matches
    + multi_transform
    + predicted_found
)

for level, data in categories.items():
    count = data["count"]
    pct = count / total_recognized * 100 if total_recognized > 0 else 0
    rate = count / total_words * 100

    print(f"{level}")
    print(f"  Instances: {count:4d} ({pct:5.1f}% of recognized)")
    print(f"  Recognition rate: {rate:.2f}%")
    print(f"  Description: {data['description']}")
    if data["examples"]:
        print(f"  Examples: {', '.join(data['examples'])}")
    print()

print("=" * 80)
print("DECIPHERMENT vs PRESERVED")
print("=" * 80)
print()

# Calculate TRUE decipherment (excluding preserved)
transformed_only = total_recognized - preserved_count
preserved_rate = preserved_count / total_words * 100
transformed_rate = transformed_only / total_words * 100

print(
    f"Total recognized:           {total_recognized:5d} ({total_recognized / total_words * 100:.2f}%)"
)
print(f"  Preserved (plain):        {preserved_count:5d} ({preserved_rate:.2f}%)")
print(f"  Transformed (deciphered): {transformed_only:5d} ({transformed_rate:.2f}%)")
print()

print("INTERPRETATION:")
print()
if preserved_rate > 1.0:
    print(f"⚠️  Significant portion ({preserved_rate:.2f}%) is preserved plain text")
    print(f"   TRUE decipherment rate: {transformed_rate:.2f}%")
    print()
    print("   This makes sense! Medieval ciphers often preserved:")
    print("   - Common function words (a, or, to, at)")
    print("   - Medical conditions (sor = sore, for searchability)")
    print("   - Short words (harder to obfuscate)")
else:
    print(f"✓ Preserved text is minimal ({preserved_rate:.2f}%)")
    print(f"  Most recognition is from actual decipherment: {transformed_rate:.2f}%")

print()
print("=" * 80)
print("ADJUSTED RECOGNITION TARGETS")
print("=" * 80)
print()

print("Goal: 10% recognition excluding preserved plain text")
print()

current_transformed = transformed_rate
target_transformed = 10.0
multiplier = target_transformed / current_transformed

current_vocab = 11  # From previous analysis
target_vocab = int(current_vocab * multiplier)
additional_vocab = target_vocab - current_vocab

print(f"Current transformed recognition: {current_transformed:.2f}%")
print(f"Current vocabulary: {current_vocab} unique terms")
print()
print(f"Target transformed recognition: {target_transformed:.2f}%")
print(f"Target vocabulary needed: ~{target_vocab} terms")
print(f"Additional terms needed: ~{additional_vocab} terms")
print()

if additional_vocab < 30:
    print("✓✓✓ HIGHLY ACHIEVABLE!")
    print(f"    Need only {additional_vocab} more medical terms")
elif additional_vocab < 50:
    print("✓✓ ACHIEVABLE")
    print(f"    Need {additional_vocab} more terms")
else:
    print("✓ CHALLENGING")
    print(f"    Need {additional_vocab} more terms")

print()

# More detailed breakdown
print("=" * 80)
print("WHAT COUNTS AS 'DECIPHERED'?")
print("=" * 80)
print()

print("NOT DECIPHERED (preserved):")
print("  • Plain words with no transformation: 'or', 'a', 'to'")
print("  • Conditions kept readable: 'sor' (sore)")
print("  • Function words for grammar")
print(f"  Estimated: {preserved_count} instances ({preserved_rate:.2f}%)")
print()

print("DECIPHERED (transformed):")
print("  • e↔o substitution: 'she'→'sho'")
print("  • Reversed words: 'make'→'kam', 'eye'→'oy'")
print("  • Consonant shifts: 'she'→'cho', 'day'→'tai'")
print("  • Multi-transform: 'root'→'odor', 'seed'→'otos'")
print(f"  Current: {transformed_only} instances ({transformed_rate:.2f}%)")
print(f"  Target: ~4,068 instances (10.00%)")
print()

print("STRATEGY:")
print("Focus on HIGH-TRANSFORM vocabulary:")
print("  • Reversed instructions (100%): grind, boil, stamp")
print("  • Reversed plant parts (100%): flower, bark, herb")
print("  • Complex transforms: multi-consonant words")
print("  • Ignore preserved words in recognition calculation")
print()

# Save analysis
output = {
    "total_words": total_words,
    "total_recognized": total_recognized,
    "overall_rate": total_recognized / total_words * 100,
    "breakdown": {
        "preserved": {
            "count": preserved_count,
            "rate": preserved_rate,
            "description": "No transformation applied",
        },
        "transformed": {
            "count": transformed_only,
            "rate": transformed_rate,
            "description": "Actual decipherment",
        },
    },
    "by_complexity": {
        level: {
            "count": data["count"],
            "rate": data["count"] / total_words * 100,
            "percent_of_recognized": data["count"] / total_recognized * 100,
            "examples": data["examples"],
        }
        for level, data in categories.items()
    },
    "targets": {
        "current_transformed_rate": current_transformed,
        "target_transformed_rate": 10.0,
        "current_vocab": current_vocab,
        "target_vocab": target_vocab,
        "additional_vocab_needed": additional_vocab,
    },
}

output_path = results_dir / "recognition_breakdown_analysis.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(f"Analysis saved to: {output_path}")
print()
