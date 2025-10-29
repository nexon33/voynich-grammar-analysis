#!/usr/bin/env python3
"""
Analyze Middle English Corpus (CMEPV)
Extract character frequencies from actual ME texts (1400-1450)
"""

from collections import Counter
from pathlib import Path
import re

# Find all SGML files in CMEPV corpus
corpus_dir = Path("data/middle_english_corpus/cmepv/middle_english_text_cmepv/sgml")

print("=" * 70)
print("ANALYZING MIDDLE ENGLISH CORPUS (CMEPV)")
print("=" * 70)

sgml_files = list(corpus_dir.glob("*.sgm"))
print(f"\nFound {len(sgml_files)} SGML files in corpus")

if len(sgml_files) == 0:
    print("\n✗ No files found! Check if CMEPV downloaded correctly.")
    print(f"Looking in: {corpus_dir.absolute()}")
    exit(1)

# Read and combine all texts
print("\nReading all Middle English texts...")
all_text = []

for sgml_file in sgml_files:
    try:
        with open(sgml_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

            # Extract text between tags (simple approach)
            # Remove XML/SGML tags
            text = re.sub(r"<[^>]+>", " ", content)
            all_text.append(text)

    except Exception as e:
        print(f"  ✗ Error reading {sgml_file.name}: {e}")
        continue

combined_text = " ".join(all_text)

print(f"✓ Combined {len(sgml_files)} texts")
print(f"  Total characters: {len(combined_text):,}")

# Analyze character frequencies
print("\n" + "=" * 70)
print("MIDDLE ENGLISH CHARACTER FREQUENCIES")
print("=" * 70)

# Get only alphabetic characters, normalize to lowercase
chars = [c for c in combined_text.lower() if c.isalpha()]
char_freq = Counter(chars)
total_chars = len(chars)

print(f"\nTotal alphabetic characters: {total_chars:,}")
print(f"Unique characters: {len(char_freq)}")

print("\n" + "=" * 70)
print("TOP 20 CHARACTER FREQUENCIES")
print("=" * 70)
print(f"\n{'Char':<6} {'Count':<12} {'Percentage':<12} {'Bar'}")
print("-" * 70)

for char, count in char_freq.most_common(20):
    percentage = count / total_chars * 100
    bar_length = int(percentage * 2)
    bar = "█" * bar_length
    print(f"{char:<6} {count:<12,} {percentage:>6.2f}%      {bar}")

# Compare with Voynich
print("\n" + "=" * 70)
print("COMPARISON WITH VOYNICH")
print("=" * 70)

# Voynich top frequencies (from our earlier analysis)
voynich_freq = {
    "o": 13.30,
    "e": 10.48,
    "h": 9.32,
    "y": 9.22,
    "a": 7.46,
    "c": 6.95,
    "d": 6.77,
    "i": 6.12,
    "k": 5.71,
    "l": 5.49,
}

print("\nTop 10 Side-by-Side:")
print(f"\n{'ME Char':<10} {'ME %':<10} {'Voyn Char':<12} {'Voyn %':<10} {'Match?'}")
print("-" * 60)

me_top = char_freq.most_common(10)
voyn_sorted = sorted(voynich_freq.items(), key=lambda x: x[1], reverse=True)

for i in range(10):
    me_char, me_count = me_top[i]
    me_pct = me_count / total_chars * 100
    voyn_char, voyn_pct = voyn_sorted[i]

    # Check if they match
    match = "✓" if me_char == voyn_char else "✗"

    print(
        f"{me_char:<10} {me_pct:>6.2f}%    {voyn_char:<12} {voyn_pct:>6.2f}%    {match}"
    )

# Test the 'o' = 'e' hypothesis
print("\n" + "=" * 70)
print("TESTING THE 'o' = 'e' HYPOTHESIS")
print("=" * 70)

me_e_pct = (char_freq["e"] / total_chars * 100) if "e" in char_freq else 0
voyn_o_pct = 13.30

print(f"\nMiddle English 'e' frequency: {me_e_pct:.2f}%")
print(f"Voynich 'o' frequency:         {voyn_o_pct:.2f}%")
print(f"Difference:                    {abs(me_e_pct - voyn_o_pct):.2f}%")

if abs(me_e_pct - voyn_o_pct) < 2.0:
    print("\n✓✓✓ STRONG MATCH! The hypothesis is supported!")
    print("    Voynich 'o' could indeed represent ME 'e'")
else:
    print(f"\n⚠ Difference is {abs(me_e_pct - voyn_o_pct):.2f}% - larger than expected")
    print("    May need to revise hypothesis or check data")

# Word analysis
print("\n" + "=" * 70)
print("MIDDLE ENGLISH WORD STATISTICS")
print("=" * 70)

words = combined_text.lower().split()
words = [w for w in words if w and any(c.isalpha() for c in w)]

print(f"\nTotal words: {len(words):,}")
print(f"Unique words: {len(set(words)):,}")
print(f"Repetition ratio: {len(words) / len(set(words)):.2f}x")

# Compare with Voynich repetition ratio (3.93x)
print(f"\nVoynich repetition ratio: 3.93x")
print(f"ME repetition ratio:      {len(words) / len(set(words)):.2f}x")

# Word length distribution
word_lengths = Counter([len(w) for w in words if w.isalpha()])
print("\nWord length distribution (top 10):")
for length in sorted(word_lengths.keys())[:10]:
    count = word_lengths[length]
    pct = count / len(words) * 100
    print(f"  {length} letters: {count:,} words ({pct:.1f}%)")

# Save results
output_file = Path("results/phase1/me_character_frequencies.txt")
output_file.parent.mkdir(parents=True, exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
    f.write("MIDDLE ENGLISH CHARACTER FREQUENCIES\n")
    f.write("Source: CMEPV Corpus\n")
    f.write("=" * 70 + "\n\n")

    for char, count in char_freq.most_common():
        percentage = count / total_chars * 100
        f.write(f"{char}: {percentage:.4f}%\n")

print(f"\n✓ Results saved to: {output_file}")

print("\n" + "=" * 70)
print("KEY FINDINGS")
print("=" * 70)
print("""
1. We now have reliable ME character frequencies from actual texts
2. We can compare these directly with Voynich
3. The 'o' = 'e' hypothesis can be tested statistically

NEXT STEPS:
- Create visualization comparing Voynich vs ME
- Run correlation tests
- Test if the match is statistically significant
- If significant → Proceed to Phase 2!
""")
