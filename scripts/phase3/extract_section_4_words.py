#!/usr/bin/env python3
"""Extract all 500 words from Section 4 (words 2000-2500)."""

import json
from pathlib import Path

results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"

# Load full manuscript translation which has the original text
with open(results_dir / "full_manuscript_translation.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Find Section 4 (should be section_id 20 based on 100-word sections)
# Words 2000-2500 = section 20-25 (100 words each)
# Let's extract based on word ranges

all_words = []
for section in data["sections"]:
    words = section["original"].split()
    all_words.extend(words)

print(f"Total words in manuscript: {len(all_words)}")

# Extract words 2000-2500
section_4_words = all_words[2000:2500]
print(f"Section 4 (words 2000-2500): {len(section_4_words)} words")

# Save to file
output = {
    "section_id": 4,
    "word_range": "2000-2500",
    "total_words": len(section_4_words),
    "words": section_4_words,
}

output_path = results_dir / "section_4_words.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(f"Saved to: {output_path}")
print(f"\nFirst 20 words: {' '.join(section_4_words[:20])}")
