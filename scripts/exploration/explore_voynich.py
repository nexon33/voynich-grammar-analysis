#!/usr/bin/env python3
"""
Explore Voynich Manuscript EVA Text
First look at the mysterious text to understand what we're working with
"""

from collections import Counter
from pathlib import Path

# Read the Voynich text
voynich_file = Path("data/voynich/eva_transcription/voynich_eva_takahashi.txt")
print(f"Reading: {voynich_file}\n")

with open(voynich_file, "r", encoding="utf-8") as f:
    text = f.read()

# Basic text statistics
print("=" * 70)
print("BASIC TEXT STATISTICS")
print("=" * 70)

total_chars = len(text)
lines = text.split("\n")
words = text.split()
unique_words = set(words)

print(f"Total characters: {total_chars:,}")
print(f"Total lines: {len(lines):,}")
print(f"Total words: {len(words):,}")
print(f"Unique words: {len(unique_words):,}")
print(f"Repetition ratio: {len(words) / len(unique_words):.2f}x")
print(
    f"  (Each unique word appears ~{len(words) / len(unique_words):.1f} times on average)"
)

# Character frequency analysis
print("\n" + "=" * 70)
print("CHARACTER FREQUENCY (Top 20)")
print("=" * 70)

# Count only alphabetic characters
chars = [c for c in text.lower() if c.isalpha()]
char_freq = Counter(chars)
total_alpha = len(chars)

print(f"Total alphabetic characters: {total_alpha:,}\n")
print(f"{'Char':<6} {'Count':<10} {'Percentage':<12} {'Bar'}")
print("-" * 70)

for char, count in char_freq.most_common(20):
    percentage = count / total_alpha * 100
    bar_length = int(percentage * 2)  # Scale for display
    bar = "█" * bar_length
    print(f"{char:<6} {count:<10,} {percentage:>6.2f}%      {bar}")

# Word length distribution
print("\n" + "=" * 70)
print("WORD LENGTH DISTRIBUTION")
print("=" * 70)

word_lengths = Counter([len(w) for w in words])
print(f"\n{'Length':<8} {'Count':<10} {'Percentage'}")
print("-" * 40)

for length in sorted(word_lengths.keys())[:15]:  # First 15 lengths
    count = word_lengths[length]
    percentage = count / len(words) * 100
    print(f"{length:<8} {count:<10,} {percentage:>6.2f}%")

# Most common words
print("\n" + "=" * 70)
print("MOST COMMON WORDS (Top 30)")
print("=" * 70)
print(f"\n{'Rank':<6} {'Word':<15} {'Count':<10} {'% of Total'}")
print("-" * 50)

word_freq = Counter(words)  # Calculate word frequency
for rank, (word, count) in enumerate(word_freq.most_common(30), 1):
    percentage = count / len(words) * 100
    print(f"{rank:<6} {word:<15} {count:<10,} {percentage:>6.2f}%")

# Look for patterns
print("\n" + "=" * 70)
print("PATTERN OBSERVATIONS")
print("=" * 70)

# Words starting with certain characters
starts_with = {}
for word in words:
    if word:
        first_char = word[0].lower()
        starts_with[first_char] = starts_with.get(first_char, 0) + 1

print("\nWords starting with each character (top 10):")
for char, count in sorted(starts_with.items(), key=lambda x: x[1], reverse=True)[:10]:
    percentage = count / len(words) * 100
    print(f"  {char}: {count:,} words ({percentage:.1f}%)")

# Words ending with certain characters
ends_with = {}
for word in words:
    if word:
        last_char = word[-1].lower()
        ends_with[last_char] = ends_with.get(last_char, 0) + 1

print("\nWords ending with each character (top 10):")
for char, count in sorted(ends_with.items(), key=lambda x: x[1], reverse=True)[:10]:
    percentage = count / len(words) * 100
    print(f"  {char}: {count:,} words ({percentage:.1f}%)")

# Character combinations (bigrams)
print("\n" + "=" * 70)
print("COMMON CHARACTER PAIRS (Bigrams)")
print("=" * 70)

bigrams = []
for word in words:
    for i in range(len(word) - 1):
        bigrams.append(word[i : i + 2].lower())

bigram_freq = Counter(bigrams)

print("\nTop 20 most common two-character sequences:")
for pair, count in bigram_freq.most_common(20):
    percentage = count / len(bigrams) * 100
    print(f"  '{pair}': {count:,} times ({percentage:.2f}%)")

# Sample text snippets
print("\n" + "=" * 70)
print("SAMPLE TEXT SNIPPETS")
print("=" * 70)

print("\nFirst 5 lines:")
print("-" * 70)
for line in lines[:5]:
    if line.strip():
        print(line)

print("\nA random middle section (lines 50-55):")
print("-" * 70)
for line in lines[50:55]:
    if line.strip():
        print(line)

# Special characters
special = [c for c in text if not c.isalpha() and not c.isspace() and c != "\n"]
print("\n" + "=" * 70)
print("SPECIAL CHARACTERS FOUND")
print("=" * 70)
special_freq = Counter(special)
for char, count in special_freq.most_common():
    print(f"  '{char}': {count:,} times")

print("\n" + "=" * 70)
print("KEY OBSERVATIONS")
print("=" * 70)
print("""
What we can see from this analysis:

1. WORD REPETITION: Words repeat frequently (look at repetition ratio)
   - This is unusual for natural text
   - Could indicate: limited vocabulary, formulaic language, or encoding

2. CHARACTER DISTRIBUTION: Some characters are VERY common (o, a, y, d)
   - If this is an alphabet, these might be common sounds
   - English has 'e' as most common; is 'o' the Voynich 'e'?

3. WORD LENGTH: Notice the distribution of word lengths
   - Are these real words or syllables?
   - Compare with Middle English word lengths

4. POSITIONAL PATTERNS: Certain characters prefer word-start or word-end
   - This suggests grammatical function (like English articles, suffixes)
   - Could be prefixes/suffixes if this is real language

5. BIGRAMS: Certain character pairs appear together often
   - 'ch', 'sh', 'dy', 'ol', 'ain' are super common
   - Could these represent single phonemes?

NEXT STEPS:
- Compare these frequencies with English/Middle English
- Look at Margery Kempe's text for similar patterns
- See if we can map high-frequency Voynich → high-frequency English

Run this script, examine the output, and start thinking about what patterns
might match between Voynich and Middle English!
""")
