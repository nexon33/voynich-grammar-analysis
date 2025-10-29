#!/usr/bin/env python3
"""
Explore Margery Kempe's Middle English Text
Compare patterns with Voynich to see if there are similarities
"""

from collections import Counter
from pathlib import Path

# Read Margery Kempe text
kempe_file = Path("data/margery_kempe/middle_english/complete_text.txt")
print(f"Reading: {kempe_file}\n")

with open(kempe_file, "r", encoding="utf-8") as f:
    text = f.read()

# Basic statistics
print("=" * 70)
print("MARGERY KEMPE - BASIC STATISTICS")
print("=" * 70)

total_chars = len(text)
lines = text.split("\n")
words = [w.lower() for w in text.split() if w.strip()]  # Normalize to lowercase
unique_words = set(words)

print(f"Total characters: {total_chars:,}")
print(f"Total lines: {len(lines):,}")
print(f"Total words: {len(words):,}")
print(f"Unique words: {len(unique_words):,}")
print(f"Repetition ratio: {len(words) / len(unique_words):.2f}x")

# Character frequency
print("\n" + "=" * 70)
print("CHARACTER FREQUENCY (Top 20)")
print("=" * 70)

chars = [c for c in text.lower() if c.isalpha()]
char_freq = Counter(chars)
total_alpha = len(chars)

print(f"Total alphabetic characters: {total_alpha:,}\n")
print(f"{'Char':<6} {'Count':<10} {'Percentage':<12} {'Bar'}")
print("-" * 70)

for char, count in char_freq.most_common(20):
    percentage = count / total_alpha * 100
    bar_length = int(percentage * 2)
    bar = "█" * bar_length
    print(f"{char:<6} {count:<10,} {percentage:>6.2f}%      {bar}")

# Compare with expected English frequencies
print("\n" + "=" * 70)
print("COMPARISON WITH STANDARD ENGLISH")
print("=" * 70)

# Standard English letter frequencies (approximate)
english_freq = {
    "e": 12.7,
    "t": 9.1,
    "a": 8.2,
    "o": 7.5,
    "i": 7.0,
    "n": 6.7,
    "s": 6.3,
    "h": 6.1,
    "r": 6.0,
    "d": 4.3,
}

print("\nTop 10 in Middle English vs. Standard Modern English:")
print(f"{'ME Char':<10} {'ME %':<10} {'Eng Char':<12} {'Eng %':<10} {'Difference'}")
print("-" * 60)

me_top = char_freq.most_common(10)
eng_sorted = sorted(english_freq.items(), key=lambda x: x[1], reverse=True)

for i in range(10):
    me_char, me_count = me_top[i]
    me_pct = me_count / total_alpha * 100
    eng_char, eng_pct = eng_sorted[i]
    diff = me_pct - eng_pct
    print(
        f"{me_char:<10} {me_pct:>6.2f}%    {eng_char:<12} {eng_pct:>6.2f}%    {diff:>+6.2f}%"
    )

# Most common words
print("\n" + "=" * 70)
print("MOST COMMON WORDS (Top 30)")
print("=" * 70)

word_freq = Counter(words)
print(f"\n{'Rank':<6} {'Word':<15} {'Count':<10} {'% of Total'}")
print("-" * 50)

for rank, (word, count) in enumerate(word_freq.most_common(30), 1):
    percentage = count / len(words) * 100
    print(f"{rank:<6} {word:<15} {count:<10,} {percentage:>6.2f}%")

# Word length distribution
print("\n" + "=" * 70)
print("WORD LENGTH DISTRIBUTION")
print("=" * 70)

word_lengths = Counter([len(w) for w in words])
print(f"\n{'Length':<8} {'Count':<10} {'Percentage'}")
print("-" * 40)

for length in sorted(word_lengths.keys())[:15]:
    count = word_lengths[length]
    percentage = count / len(words) * 100
    print(f"{length:<8} {count:<10,} {percentage:>6.2f}%")

# Search for medical/childbirth terms
print("\n" + "=" * 70)
print("MEDICAL & CHILDBIRTH VOCABULARY")
print("=" * 70)

medical_terms = {
    "child": ["child", "childe", "childryn", "chyld"],
    "birth": ["birth", "berth", "born", "bor"],
    "pain": ["peyn", "payn", "peyne", "payne", "sorwe"],
    "sick": ["seke", "syk", "sekenes"],
    "heal": ["hele", "helyd", "helyn"],
    "body": ["body", "bodily"],
    "womb": ["wombe", "womb"],
    "mother": ["modyr", "modir", "moder"],
    "blood": ["blod", "blood"],
}

print("\nSearching for medical vocabulary...")
found_terms = {}

for category, variants in medical_terms.items():
    count = 0
    found = []
    for variant in variants:
        for word in words:
            if variant in word:
                count += 1
                if word not in found:
                    found.append(word)
    if count > 0:
        found_terms[category] = (count, found[:10])  # Top 10 examples

for category, (count, examples) in sorted(
    found_terms.items(), key=lambda x: x[1][0], reverse=True
):
    print(f"\n{category.upper()}: {count} occurrences")
    print(f"  Examples: {', '.join(examples[:5])}")

# Sample passages
print("\n" + "=" * 70)
print("SAMPLE TEXT (First few lines)")
print("=" * 70)

for line in lines[5:15]:  # Skip header lines
    if line.strip() and len(line) > 20:
        print(line[:120] + "..." if len(line) > 120 else line)

print("\n" + "=" * 70)
print("KEY OBSERVATIONS - MARGERY KEMPE")
print("=" * 70)
print("""
What we notice about Middle English:

1. CHARACTER FREQUENCY: 'e' is most common (like modern English)
   - Compare this with Voynich where 'o' is most common
   - Is Voynich 'o' actually encoding ME 'e'?

2. COMMON WORDS: Function words dominate (and, the, of, to, her)
   - These are grammatical "glue" words
   - Does Voynich have similar patterns?

3. MEDICAL VOCABULARY: Present but needs deeper search
   - Words related to childbirth, pain, healing
   - These are the themes we expect in Voynich

4. WORD LENGTHS: Similar distribution to Voynich?
   - Compare the patterns
   - Could help identify if same language

COMPARISON QUESTIONS:
- Does Voynich 'o' frequency match ME 'e' frequency?
- Do common Voynich words behave like ME function words?
- Are the bigram patterns similar?

Next: Create a side-by-side frequency comparison!
""")
