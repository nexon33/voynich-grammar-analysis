"""
Find all UNKNOWN roots in Phase 17 data (marked with [?...])
Identify highest-frequency unknown roots that should be decoded next
"""

import json
from collections import Counter

# Load translations data
print("Loading Phase 17 translations data...")
with open("COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8") as f:
    data = json.load(f)

translations = data.get("translations", [])
print(f"Loaded {len(translations)} sentences\n")

# Current 35 decoded roots
current_roots = {
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
}

# Count all roots
all_roots = Counter()
unknown_roots = Counter()
known_roots = Counter()

total_words = 0

for sentence in translations:
    words = sentence.get("words", [])

    for word_data in words:
        total_words += 1
        morphology = word_data.get("morphology", {})
        root = morphology.get("root", "")
        confidence = word_data.get("confidence", "unknown")

        if root:
            all_roots[root] += 1

            # Check if root is in our known list
            if root in current_roots:
                known_roots[root] += 1
            else:
                # Unknown root - check if it's marked as unknown in translation
                if confidence in ["unknown", "medium"]:
                    # Medium confidence means suffix known but root unknown
                    unknown_roots[root] += 1

print(f"{'=' * 80}")
print(f"ROOT ANALYSIS")
print(f"{'=' * 80}\n")

print(f"Total words analyzed: {total_words}")
print(f"Total unique roots: {len(all_roots)}")
print(f"Known roots (in current 35): {len(known_roots)}")
print(f"Unknown roots needing decoding: {len(unknown_roots)}")

# Calculate current semantic understanding
known_instances = sum(known_roots.values())
current_semantic = (known_instances / total_words) * 100
print(f"\nCurrent semantic understanding: {current_semantic:.1f}%")

# Top 30 unknown roots by frequency
print(f"\n{'=' * 80}")
print(f"TOP 30 UNKNOWN ROOTS (HIGHEST PRIORITY FOR DECODING)")
print(f"{'=' * 80}\n")

print(f"{'Rank':<6} {'Root':<15} {'Instances':<10} {'% Gain':<10} {'Cumulative %':<12}")
print(f"{'-' * 60}")

cumulative_percentage = current_semantic

for i, (root, count) in enumerate(unknown_roots.most_common(30), 1):
    percentage = (count / total_words) * 100
    cumulative_percentage += percentage
    print(
        f"{i:<6} {root:<15} {count:<10} {percentage:>6.2f}%    {cumulative_percentage:>6.2f}%"
    )

print(f"\n{'=' * 80}")
top30_gain = sum(
    (count / total_words) * 100 for root, count in unknown_roots.most_common(30)
)
print(f"Decoding top 30 unknown roots would add: +{top30_gain:.2f}%")
print(f"Current: {current_semantic:.1f}%")
print(f"After top 30: {current_semantic + top30_gain:.1f}%")
print(f"{'=' * 80}")

# How many roots to hit 50%?
print(f"\n{'=' * 80}")
print(f"HOW MANY ROOTS TO HIT 50%+ SEMANTIC UNDERSTANDING?")
print(f"{'=' * 80}\n")

target = 50.0
needed = target - current_semantic

cumulative = 0
roots_needed = 0

for root, count in unknown_roots.most_common(50):
    gain = (count / total_words) * 100
    cumulative += gain
    roots_needed += 1

    if current_semantic + cumulative >= target:
        print(f"Need to decode {roots_needed} more roots to hit {target}%")
        print(f"\nThose roots are:")
        for i, (r, c) in enumerate(unknown_roots.most_common(roots_needed), 1):
            g = (c / total_words) * 100
            print(f"  {i}. {r:<15} ({c:>5} instances, +{g:.2f}%)")
        print(f"\nTotal gain: +{cumulative:.2f}%")
        print(f"New semantic understanding: {current_semantic + cumulative:.1f}%")
        break

# Save detailed results
output = {
    "total_words": total_words,
    "total_unique_roots": len(all_roots),
    "known_roots_count": len(known_roots),
    "unknown_roots_count": len(unknown_roots),
    "current_semantic_percentage": current_semantic,
    "top_30_unknown": [
        {
            "rank": i,
            "root": root,
            "instances": count,
            "percentage_gain": (count / total_words) * 100,
        }
        for i, (root, count) in enumerate(unknown_roots.most_common(30), 1)
    ],
    "roots_to_hit_50": roots_needed,
    "gain_to_hit_50": cumulative,
}

with open("UNKNOWN_ROOTS_PRIORITY.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n\nDetailed results saved to: UNKNOWN_ROOTS_PRIORITY.json")
