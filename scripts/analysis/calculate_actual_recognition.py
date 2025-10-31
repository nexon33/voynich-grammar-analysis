"""
Calculate ACTUAL recognition percentage based on:
1. Phase 17 baseline (73.81% / 27,402 words)
2. Morphemes decoded THIS SESSION (from 88.2% to 98.3%)

This will verify our 98.3% claim is accurate
"""

import json

print("=" * 70)
print("RECOGNITION CALCULATION")
print("=" * 70)

# Starting point (from session summary)
starting_recognition = 88.2
starting_words_decoded = 32614
total_corpus = 37000  # approximate

print(f"\nSTARTING POINT (beginning of this session):")
print(f"  Recognition: {starting_recognition}%")
print(f"  Words decoded: {starting_words_decoded:,}")
print(f"  Total corpus: ~{total_corpus:,} words")

# Morphemes decoded THIS SESSION with instance counts
morphemes_decoded = [
    ("eo", 170, "boil/cook"),
    ("che", 560, "oak-substance"),
    ("eey", 511, "seed/grain (acorn when oak-GEN)"),
    ("o", 510, "oak-related term"),
    ("d", 417, "container/vessel location"),
    ("shey", 315, "oak-preparation"),
    ("dy", 276, "nominal"),
    ("l", 243, "nominal"),
    ("qo", 216, "nominal/mixed"),
    ("lk", 200, "verbal"),
    ("ey", 196, "nominal suffix"),
    ("yk", 182, "bound morpheme (verbal)"),
    ("yt", 176, "bound morpheme (verbal)"),
    ("okeey", 174, "acorn variant"),
    ("cth", 164, "bound morpheme"),
    ("sheey", 151, "nominal (oak/oat product)"),
]

print(f"\n{'=' * 70}")
print("MORPHEMES DECODED THIS SESSION:")
print(f"{'=' * 70}")

total_instances_decoded = 0
for morpheme, count, meaning in morphemes_decoded:
    print(f"  [{morpheme:8s}] = {meaning:40s} (+{count:4d} instances)")
    total_instances_decoded += count

print(f"\n  TOTAL NEW INSTANCES: {total_instances_decoded:,}")

# Calculate new recognition
final_words_decoded = starting_words_decoded + total_instances_decoded
final_recognition = (final_words_decoded / total_corpus) * 100

print(f"\n{'=' * 70}")
print("FINAL CALCULATION:")
print(f"{'=' * 70}")

print(f"\n  Starting: {starting_words_decoded:,} words decoded")
print(f"  Added:    +{total_instances_decoded:,} words decoded")
print(f"  ────────────────────")
print(f"  Final:    {final_words_decoded:,} words decoded")
print()
print(
    f"  Recognition: {final_words_decoded:,} / {total_corpus:,} = {final_recognition:.2f}%"
)

# More precise calculation with actual corpus size
print(f"\n{'=' * 70}")
print("VERIFICATION WITH ACTUAL CORPUS SIZE:")
print(f"{'=' * 70}")

# From Phase 17 data
actual_corpus = 37125
print(f"\n  Actual corpus size: {actual_corpus:,} words")
print(f"  Starting recognition: {starting_recognition}%")
print(f"    = {int(starting_recognition / 100 * actual_corpus):,} words")
print(f"  Added: +{total_instances_decoded:,} words")

starting_decoded_precise = int(starting_recognition / 100 * actual_corpus)
final_decoded_precise = starting_decoded_precise + total_instances_decoded
final_recognition_precise = (final_decoded_precise / actual_corpus) * 100

print(f"  ────────────────────")
print(f"  Final: {final_decoded_precise:,} words decoded")
print(
    f"  Recognition: {final_decoded_precise:,} / {actual_corpus:,} = {final_recognition_precise:.2f}%"
)

# Check against our claim
claimed_recognition = 98.3
claimed_decoded = int(claimed_recognition / 100 * actual_corpus)

print(f"\n{'=' * 70}")
print("COMPARISON WITH CLAIMED NUMBERS:")
print(f"{'=' * 70}")

print(f"\n  CLAIMED:  {claimed_recognition}% ({claimed_decoded:,} words)")
print(
    f"  CALCULATED: {final_recognition_precise:.2f}% ({final_decoded_precise:,} words)"
)
print()

difference = claimed_decoded - final_decoded_precise
if abs(difference) < 100:
    print(
        f"  ✓ MATCH! Difference: {difference:+,} words (~{abs(difference / actual_corpus) * 100:.2f}%)"
    )
    print(f"    This is within rounding error.")
else:
    print(
        f"  ✗ DISCREPANCY: {difference:+,} words ({difference / actual_corpus * 100:+.2f}%)"
    )
    print(f"    Need to investigate...")

# Summary
print(f"\n{'=' * 70}")
print("SUMMARY:")
print(f"{'=' * 70}")

print(f"\n  This session decoded: {len(morphemes_decoded)} morphemes")
print(f"  Total instances: +{total_instances_decoded:,} words")
print(f"  Recognition gain: +{final_recognition_precise - starting_recognition:.2f}%")
print(f"  Final recognition: {final_recognition_precise:.2f}%")
print()

if final_recognition_precise >= 98.0:
    print("  ✓ 98%+ MILESTONE CONFIRMED!")
elif final_recognition_precise >= 97.0:
    print("  ⚠ Close to 98%, but slightly under")
else:
    print("  ✗ Recognition lower than expected")

print(f"\n{'=' * 70}")
