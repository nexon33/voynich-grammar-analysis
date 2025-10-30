#!/usr/bin/env python3
"""
Analyze the difference between -edy and -eedy suffixes.
"""

import json
from collections import Counter

# Load translation data
with open("COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Collect all words
all_words = [w["original"] for t in data["translations"] for w in t["words"]]
word_counts = Counter(all_words)

# Separate -edy and -eedy words
edy_words = {
    w: c for w, c in word_counts.items() if w.endswith("edy") and not w.endswith("eedy")
}
eedy_words = {w: c for w, c in word_counts.items() if w.endswith("eedy")}

print("=" * 80)
print("SUFFIX PATTERN ANALYSIS: -edy vs -eedy")
print("=" * 80)

print(f"\nTotal -edy words: {len(edy_words)} types, {sum(edy_words.values())} tokens")
print(f"Total -eedy words: {len(eedy_words)} types, {sum(eedy_words.values())} tokens")

print("\nTop 20 -edy words:")
for word, count in sorted(edy_words.items(), key=lambda x: x[1], reverse=True)[:20]:
    print(f"  {word:20s}: {count:4d}×")

print("\nTop 20 -eedy words:")
for word, count in sorted(eedy_words.items(), key=lambda x: x[1], reverse=True)[:20]:
    print(f"  {word:20s}: {count:4d}×")

# Check for pairs (same stem with both suffixes)
print("\n" + "=" * 80)
print("STEMS THAT TAKE BOTH -edy AND -eedy")
print("=" * 80)

pairs = []
for eedy_word in eedy_words:
    stem = eedy_word[:-4]  # Remove -eedy
    edy_word = stem + "edy"
    if edy_word in edy_words:
        pairs.append(
            {
                "stem": stem,
                "edy_form": edy_word,
                "edy_count": edy_words[edy_word],
                "eedy_form": eedy_word,
                "eedy_count": eedy_words[eedy_word],
            }
        )

print(f"\nFound {len(pairs)} stems that take BOTH suffixes:")
pairs_sorted = sorted(
    pairs, key=lambda x: x["edy_count"] + x["eedy_count"], reverse=True
)

for pair in pairs_sorted[:15]:
    total = pair["edy_count"] + pair["eedy_count"]
    edy_pct = pair["edy_count"] / total * 100
    eedy_pct = pair["eedy_count"] / total * 100
    print(f"\nStem: '{pair['stem']}'")
    print(f"  {pair['edy_form']:15s}: {pair['edy_count']:4d}× ({edy_pct:5.1f}%)")
    print(f"  {pair['eedy_form']:15s}: {pair['eedy_count']:4d}× ({eedy_pct:5.1f}%)")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)

if len(pairs) > 5:
    print("\nMany stems take BOTH -edy and -eedy!")
    print(
        "This suggests they are DIFFERENT morphemes or in complementary distribution."
    )
    print("\nPossibilities:")
    print("1. -edy and -eedy are different aspect/tense markers")
    print("2. 'e' is an actual root: stem-e-dy vs stem-dy")
    print("3. Phonological conditioning we don't yet understand")
else:
    print("\nFew stems take both suffixes.")
    print("This suggests -edy and -eedy are allomorphs in complementary distribution.")
