"""
Verify which high-value roots are missing from current 35-root list
"""

# Current 35 decoded roots from VOCABULARY_35_ROOTS_COMPLETE.md
current_roots = [
    # BOTANICAL
    "qok",
    "qot",
    "ok",
    "che",
    "ey",
    # PROCESSES
    "ch",
    "sh",
    "lch",
    "eo",
    # CONTAINERS
    "sho",
    "cho",
    "chol",
    "dain",
    "she",
    "shee",
    "lk",
    # SPATIAL
    "ar",
    "dair",
    "dar",
    "air",
    "al",
    # FUNCTION WORDS
    "or",
    "ol",
    "sal",
    "qol",
    "chey",
    "chy",
    "cheey",
    "daiin",
    "ain",
    "am",
    "qo",
    # BOUND MORPHEMES
    "yk",
    "yt",
]

high_value_targets = ["s", "r", "a", "y", "d", "o", "shey", "dy", "l", "eey", "e"]

print("=== HIGH-VALUE ROOT VERIFICATION ===\n")
print("Already decoded:")
decoded_count = 0
for root in high_value_targets:
    if root in current_roots:
        print(f"  ✓ {root} - ALREADY IN 35 ROOTS")
        decoded_count += 1

print("\n❌ NOT YET DECODED (HIGH PRIORITY):")
missing = []
for root in high_value_targets:
    if root not in current_roots:
        print(f"  ✗ {root} - NOT DECODED YET")
        missing.append(root)

print(f"\n=== SUMMARY ===")
print(f"Current roots: {len(current_roots)}")
print(f"High-value targets checked: {len(high_value_targets)}")
print(f"Already decoded: {decoded_count}")
print(f"Missing high-value roots: {len(missing)}")
print(f"Missing roots: {missing}")

# Estimated gain
print(f"\n=== ESTIMATED GAINS ===")
estimated_gains = {
    "s": 1.87,
    "r": 0.78,
    "a": 2.85,
    "y": 1.68,
    "d": 1.13,
    "o": 1.38,
    "shey": 0.85,
    "dy": 0.74,
    "l": 1.0,
    "eey": 0.5,
    "e": 3.0,
}

total_potential = sum(estimated_gains.get(root, 0) for root in missing)
print(f"Total potential gain from missing roots: +{total_potential:.2f}%")
print(f"\nIf all missing roots decoded:")
print(f"  Current: 42-49%")
print(f"  New estimate: {42 + total_potential:.1f}-{49 + total_potential:.1f}%")
