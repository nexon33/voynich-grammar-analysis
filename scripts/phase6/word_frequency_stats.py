import re
from collections import Counter

# Load
with open(
    "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/ZL3b-n.txt",
    "r",
    encoding="utf-8",
) as f:
    lines = f.readlines()

all_words = []
for line in lines:
    if line.strip().startswith("<f"):
        match = re.search(r"<f\d+[rv]\d*\.[^>]+>\s+(.+)$", line.strip())
        if match:
            text = match.group(1)
            text = re.sub(r"<[^>]+>", "", text)
            text = re.sub(r"\{[^}]+\}", "", text)
            text = re.sub(r"\[[^\]]+\]", "", text)
            text = re.sub(r"[@!]\d+;", "", text)
            words = re.findall(r"[a-z]+", text.lower())
            all_words.extend(words)

# Count unique words
word_counts = Counter(all_words)
print(f"Total words: {len(all_words)}")
print(f"Unique words: {len(word_counts)}")

# Count by frequency bands
bands = [
    ("1000+", lambda c: c >= 1000),
    ("500-999", lambda c: 500 <= c < 1000),
    ("200-499", lambda c: 200 <= c < 500),
    ("100-199", lambda c: 100 <= c < 200),
    ("50-99", lambda c: 50 <= c < 100),
    ("20-49", lambda c: 20 <= c < 50),
    ("10-19", lambda c: 10 <= c < 20),
    ("5-9", lambda c: 5 <= c < 10),
    ("1-4", lambda c: c < 5),
]

print("\nFrequency distribution:")
for band_name, condition in bands:
    count = sum(1 for c in word_counts.values() if condition(c))
    print(f"  {band_name:10} {count:4} words")

# Show coverage
print("\nCoverage analysis:")
cumulative = 0
for band_name, condition in bands:
    band_words = sum(c for c in word_counts.values() if condition(c))
    cumulative += band_words
    pct = 100 * cumulative / len(all_words)
    print(f"  Up to {band_name:10} {cumulative:6} tokens ({pct:.1f}% coverage)")
