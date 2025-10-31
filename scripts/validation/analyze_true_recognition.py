"""
ANALYZE TRUE RECOGNITION vs CLAIMED RECOGNITION

The Phase 17 system counts words as "recognized" if:
- Whole word is known (HIGH confidence)
- Root is unknown but suffix is known (MEDIUM confidence)

But "root unknown + suffix known" doesn't mean we understand the word!

Example: [?yk]-LOC means "unknown thing in location"
This is NOT the same as understanding what the word actually means.

Let's calculate:
1. TRUE recognition: Only words where we know the ROOT meaning
2. MORPHOLOGICAL recognition: Words with any recognized morpheme
3. Compare the two
"""

import json

print("=" * 80)
print("TRUE RECOGNITION ANALYSIS")
print("Comparing semantic understanding vs morphological matching")
print("=" * 80)

# Load Phase 17 translations
with open("COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8") as f:
    data = json.load(f)

translations = data["translations"]

print(f"\nLoaded {len(translations)} lines")
print(
    f"Claimed overall recognition: {data['statistics']['overall_recognition_rate']:.1f}%"
)
print()

# Analyze true vs claimed recognition
total_words = 0
claimed_recognized = 0  # high + medium confidence
true_recognized = 0  # only if root meaning is known

# Known roots (from the vocabulary)
KNOWN_ROOTS = {
    "qok": "oak",
    "qot": "oat",
    "dain": "water",
    "sho": "vessel",
    "cho": "vessel",
    "ar": "at/in",
    "daiin": "this/that",
    "dair": "there",
    "air": "sky",
    "dor": "red",
    "she": "water",
    "shee": "water",
    # Add more from actual vocabulary
    "ol": "or",
    "qol": "then",
    "sal": "and",
}

for trans in translations:
    for word_data in trans["words"]:
        total_words += 1

        confidence = word_data["confidence"]
        morphology = word_data["morphology"]

        # Claimed recognition: high or medium confidence
        if confidence in ["high", "medium"]:
            claimed_recognized += 1

        # True recognition: root meaning is known
        root = morphology.get("root", "")
        if root in KNOWN_ROOTS:
            true_recognized += 1
        # Also count if it's a whole-word match
        elif morphology.get("method") == "whole-word" and confidence == "high":
            true_recognized += 1

claimed_rate = (claimed_recognized / total_words * 100) if total_words > 0 else 0
true_rate = (true_recognized / total_words * 100) if total_words > 0 else 0

print("=" * 80)
print("RESULTS")
print("=" * 80)
print()
print(f"Total words analyzed: {total_words:,}")
print()
print(
    f"CLAIMED recognition (high + medium): {claimed_recognized:,} words ({claimed_rate:.1f}%)"
)
print(
    f"TRUE recognition (known root meaning):  {true_recognized:,} words ({true_rate:.1f}%)"
)
print()
print(f"Difference: {claimed_rate - true_rate:.1f}%")
print()

# Calculate the breakdown
print("=" * 80)
print("WHAT'S BEING COUNTED AS 'RECOGNIZED'?")
print("=" * 80)
print()

high_conf = sum(
    1 for t in translations for w in t["words"] if w["confidence"] == "high"
)
medium_conf = sum(
    1 for t in translations for w in t["words"] if w["confidence"] == "medium"
)
unknown = sum(
    1 for t in translations for w in t["words"] if w["confidence"] == "unknown"
)

print(
    f"HIGH confidence (fully known words):     {high_conf:,} ({high_conf / total_words * 100:.1f}%)"
)
print(
    f"MEDIUM confidence (unknown root + known suffix): {medium_conf:,} ({medium_conf / total_words * 100:.1f}%)"
)
print(
    f"UNKNOWN (no morphemes recognized):       {unknown:,} ({unknown / total_words * 100:.1f}%)"
)
print()

# Sample some medium confidence words to show the problem
print("=" * 80)
print("EXAMPLES OF 'MEDIUM CONFIDENCE' WORDS")
print("=" * 80)
print()
print("These are counted as 'recognized' but we don't know what they mean:")
print()

medium_samples = []
for trans in translations:
    for word_data in trans["words"]:
        if word_data["confidence"] == "medium":
            root = word_data["morphology"].get("root", "")
            if root not in KNOWN_ROOTS and len(medium_samples) < 10:
                medium_samples.append(
                    {
                        "original": word_data["original"],
                        "translation": word_data["final_translation"],
                        "root": root,
                    }
                )

for i, sample in enumerate(medium_samples[:10], 1):
    print(f"{i}. {sample['original']} → {sample['translation']}")
    print(f"   Root '{sample['root']}' is UNKNOWN (only suffix recognized)")

print()
print("=" * 80)
print("INTERPRETATION")
print("=" * 80)
print()

if claimed_rate - true_rate > 30:
    print("⚠️ MAJOR DISCREPANCY")
    print()
    print(f"The claimed {claimed_rate:.1f}% recognition is INFLATED.")
    print(f"True semantic understanding is only {true_rate:.1f}%")
    print()
    print(
        "The {:.1f}% difference is from words like '[?yk]-LOC'".format(
            claimed_rate - true_rate
        )
    )
    print("where we recognize the suffix (-LOC) but NOT the root meaning.")
    print()
    print("This is like saying you 'understand' the English sentence:")
    print("  'The glorb is blicking in the flarney'")
    print("because you recognize 'the', 'is', 'in', 'the' (grammar)")
    print("even though you don't know glorb, blicking, or flarney (meaning)!")
    print()
    print(
        "VERDICT: Recognition rate should be reported as ~{:.1f}%, not {:.1f}%".format(
            true_rate, claimed_rate
        )
    )
elif claimed_rate - true_rate > 10:
    print("⚠️ MODERATE DISCREPANCY")
    print()
    print(f"Claimed: {claimed_rate:.1f}%")
    print(f"True: {true_rate:.1f}%")
    print()
    print("There's some inflation from morphological matches")
    print("without semantic understanding.")
else:
    print("✓ Rates are similar")
    print()
    print("Claimed and true recognition are close.")
    print("Most recognized words have known root meanings.")

# Save results
output = {
    "total_words": total_words,
    "claimed_recognition": {"count": claimed_recognized, "rate": claimed_rate},
    "true_recognition": {"count": true_recognized, "rate": true_rate},
    "breakdown": {
        "high_confidence": high_conf,
        "medium_confidence": medium_conf,
        "unknown": unknown,
    },
    "discrepancy": claimed_rate - true_rate,
    "medium_samples": medium_samples[:10],
}

with open("TRUE_RECOGNITION_ANALYSIS.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print()
print("Results saved to: TRUE_RECOGNITION_ANALYSIS.json")
print("=" * 80)
