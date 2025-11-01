"""
Find the final 6-8 roots needed to push from 56.6% to 60%
"""

import json

# Load the priority list
with open("UNKNOWN_ROOTS_PRIORITY.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Already decoded roots
decoded = {
    "e",
    "a",
    "s",
    "y",
    "k",
    "eey",
    "o",  # Critical 7
    "d",
    "shey",
    "r",
    "dy",
    "l",  # Batch 1
    "okeey",
    "cth",
    "sheey",
    "oke",
    "chckhy",  # Batch 2
}

print("NEXT HIGHEST PRIORITY ROOTS (for 60% push):\n")
print(f"{'Rank':<6} {'Root':<15} {'Instances':<10} {'% Gain':<10} {'Cumulative %':<12}")
print("-" * 60)

current = 56.6
cumulative = current
count = 0
targets = []

for item in data["top_30_unknown"]:
    root = item["root"]
    if root not in decoded:
        count += 1
        instances = item["instances"]
        gain = item["percentage_gain"]
        cumulative += gain
        targets.append(root)
        print(
            f"{count:<6} {root:<15} {instances:<10} {gain:>6.2f}%    {cumulative:>6.2f}%"
        )

        if cumulative >= 60.0:
            break

print(f"\n{'=' * 60}")
print(f"Need {count} more roots to hit 60%")
print(f"Targets: {', '.join(targets)}")
print(f"Expected: 56.6% + {cumulative - current:.2f}% = {cumulative:.1f}%")
print(f"{'=' * 60}")
