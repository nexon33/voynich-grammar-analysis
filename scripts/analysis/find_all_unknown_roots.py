"""
Find all roots in Phase 17 data and identify which ones are NOT in the current 35-root list
"""

import json
from collections import Counter

# Load translations data
print("Loading Phase 17 translations data...")
with open("COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8") as f:
    data = json.load(f)

translations = data.get("translations", [])
print(f"Loaded {len(translations)} word translations\n")

# Current 35 decoded roots
current_roots = [
    "qok",
    "qot",
    "ok",
    "che",
    "ey",
    "ch",
    "sh",
    "lch",
    "eo",
    "sho",
    "cho",
    "chol",
    "dain",
    "she",
    "shee",
    "lk",
    "ar",
    "dair",
    "dar",
    "air",
    "al",
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
    "yk",
    "yt",
]

# Count all roots in the corpus
all_roots = Counter()
unknown_roots = Counter()

for word_data in translations:
    morphology = word_data.get("morphology", {})
    root = morphology.get("root", "")

    if root and root != "?":
        all_roots[root] += 1

        # Check if root is unknown
        if root not in current_roots and not root.startswith("?"):
            unknown_roots[root] += 1

print(f"{'=' * 80}")
print(f"ROOT ANALYSIS")
print(f"{'=' * 80}\n")

print(f"Total unique roots in corpus: {len(all_roots)}")
print(
    f"Known roots (in current 35): {len([r for r in all_roots if r in current_roots])}"
)
print(f"Unknown roots: {len(unknown_roots)}")

# Top 30 unknown roots by frequency
print(f"\n{'=' * 80}")
print(f"TOP 30 UNKNOWN ROOTS (by frequency)")
print(f"{'=' * 80}\n")

print(f"{'Rank':<6} {'Root':<15} {'Instances':<10} {'% of Corpus':<12}")
print(f"{'-' * 50}")

total_words = len(translations)
cumulative_percentage = 0

for i, (root, count) in enumerate(unknown_roots.most_common(30), 1):
    percentage = (count / total_words) * 100
    cumulative_percentage += percentage
    print(f"{i:<6} {root:<15} {count:<10} {percentage:>6.2f}%")

print(f"\n{'=' * 80}")
print(f"Cumulative gain from top 30 unknown roots: +{cumulative_percentage:.2f}%")
print(f"Current understanding: 42-49%")
print(
    f"Potential new understanding: {42 + cumulative_percentage:.1f}-{49 + cumulative_percentage:.1f}%"
)
print(f"{'=' * 80}")

# Check if any of the "target" roots exist as compound roots
print(f"\n{'=' * 80}")
print(f"CHECKING FOR 'e', 'a', 's', 'y' AS PART OF COMPOUND ROOTS")
print(f"{'=' * 80}\n")

target_letters = ["e", "a", "s", "y", "d", "o", "l", "r"]

for letter in target_letters:
    # Find roots containing this letter
    containing = [
        (root, count) for root, count in unknown_roots.most_common(50) if letter in root
    ]

    if containing:
        print(f"\nRoots containing '{letter}':")
        for root, count in containing[:10]:
            percentage = (count / total_words) * 100
            print(f"  {root:<15} {count:>5} instances ({percentage:.2f}%)")
    else:
        print(f"\nNo unknown roots contain '{letter}'")

# Save detailed results
output = {
    "total_unique_roots": len(all_roots),
    "known_roots_count": len([r for r in all_roots if r in current_roots]),
    "unknown_roots_count": len(unknown_roots),
    "top_30_unknown": [
        {
            "rank": i,
            "root": root,
            "instances": count,
            "percentage": (count / total_words) * 100,
        }
        for i, (root, count) in enumerate(unknown_roots.most_common(30), 1)
    ],
    "cumulative_gain_top30": cumulative_percentage,
}

with open("UNKNOWN_ROOTS_ANALYSIS.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n\nDetailed results saved to: UNKNOWN_ROOTS_ANALYSIS.json")
