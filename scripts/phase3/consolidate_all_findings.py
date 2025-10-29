#!/usr/bin/env python3
"""
Consolidate ALL findings from all phases to get true recognition rate.

Combines:
- Initial e↔o + reversal findings
- Consonant pattern findings (ch↔sh, t↔d)
- Predicted reversal findings
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"

print("=" * 80)
print("CONSOLIDATING ALL FINDINGS")
print("=" * 80)
print()

# Load all result files
with open(results_dir / "consonant_pattern_results.json", "r") as f:
    consonant_data = json.load(f)

with open(results_dir / "predicted_reversals_results.json", "r") as f:
    predicted_data = json.load(f)

total_words = consonant_data["total_words"]

print(f"Manuscript: {total_words:,} words")
print()

# Consolidate recognition stats
print("=" * 80)
print("RECOGNITION BY PHASE")
print("=" * 80)
print()

phases = {
    "Phase 1: e↔o + Reversal": {
        "instances": consonant_data["recognition"]["direct"]
        + consonant_data["recognition"]["reversed"],
        "rate": (
            consonant_data["recognition"]["direct"]
            + consonant_data["recognition"]["reversed"]
        )
        / total_words
        * 100,
    },
    "Phase 2: + Consonants (ch↔sh, t↔d)": {
        "instances": consonant_data["recognition"]["consonant"]
        + consonant_data["recognition"]["multi_transform"],
        "rate": (
            consonant_data["recognition"]["consonant"]
            + consonant_data["recognition"]["multi_transform"]
        )
        / total_words
        * 100,
    },
    "Phase 3: + Predicted Reversals": {
        "instances": predicted_data["total_found"],
        "rate": predicted_data["total_found"] / total_words * 100,
    },
}

cumulative = 0
for phase, stats in phases.items():
    cumulative += stats["instances"]
    cumulative_rate = cumulative / total_words * 100
    print(f"{phase}")
    print(f"  New instances: {stats['instances']:4d} (+{stats['rate']:.2f}%)")
    print(f"  Cumulative:    {cumulative:4d} ({cumulative_rate:.2f}%)")
    print()

print("=" * 80)
print("VOCABULARY BREAKDOWN")
print("=" * 80)
print()

# Collect all unique terms found
all_terms = defaultdict(lambda: {"instances": 0, "category": "", "variants": set()})

# From consonant patterns
if "sample_matches" in consonant_data:
    for match_list in ["consonant", "multi_transform"]:
        for match in consonant_data["sample_matches"].get(match_list, []):
            term = match["english"]
            all_terms[term]["instances"] += 1
            all_terms[term]["category"] = match["category"]
            all_terms[term]["variants"].add(match["voynich"])

# From predicted reversals
for cat, terms in predicted_data["detailed_results"].items():
    for term, data in terms.items():
        all_terms[term]["instances"] += data["total"]
        all_terms[term]["category"] = cat
        for v in data["sample_voynich"]:
            all_terms[term]["variants"].add(v)

# Sort by instances
sorted_terms = sorted(all_terms.items(), key=lambda x: x[1]["instances"], reverse=True)

print("Top 30 most frequent terms:")
print()
print(f"{'English':15s} {'Category':20s} {'Instances':>10s} {'Voynich samples':s}")
print("-" * 80)

for term, data in sorted_terms[:30]:
    variants_str = ", ".join(list(data["variants"])[:5])
    if len(data["variants"]) > 5:
        variants_str += f" (+{len(data['variants']) - 5} more)"
    print(f"{term:15s} {data['category']:20s} {data['instances']:10d}   {variants_str}")

print()

# Category breakdown
print("=" * 80)
print("BY SEMANTIC CATEGORY")
print("=" * 80)
print()

category_stats = defaultdict(lambda: {"terms": 0, "instances": 0})
for term, data in all_terms.items():
    cat = data["category"]
    category_stats[cat]["terms"] += 1
    category_stats[cat]["instances"] += data["instances"]

for cat, stats in sorted(
    category_stats.items(), key=lambda x: x[1]["instances"], reverse=True
):
    print(
        f"{cat:25s}: {stats['instances']:4d} instances, {stats['terms']:3d} unique terms"
    )

print()

# Key medical terms
print("=" * 80)
print("KEY MEDICAL/BOTANICAL TERMS")
print("=" * 80)
print()

medical_categories = [
    "PLANT_PARTS",
    "herbs",
    "INSTRUCTIONS",
    "instructions",
    "body_parts",
    "conditions",
]
medical_terms = [
    (term, data)
    for term, data in sorted_terms
    if data["category"] in medical_categories
]

print(f"Found {len(medical_terms)} unique medical/botanical terms")
print(f"Total instances: {sum(data['instances'] for _, data in medical_terms)}")
print()

print("Plant-related terms:")
plant_terms = [
    (term, data)
    for term, data in medical_terms
    if "PLANT" in data["category"] or data["category"] == "herbs"
]
for term, data in plant_terms[:15]:
    print(f"  {term:15s}: {data['instances']:3d} instances")

print()
print("Instruction terms:")
instruction_terms = [
    (term, data)
    for term, data in medical_terms
    if "INSTRUCTION" in data["category"] or data["category"] == "instructions"
]
for term, data in instruction_terms[:15]:
    print(f"  {term:15s}: {data['instances']:3d} instances")

print()

# Final statistics
print("=" * 80)
print("FINAL RECOGNITION STATISTICS")
print("=" * 80)
print()

total_recognized = cumulative
recognition_rate = cumulative / total_words * 100

print(f"Total words in manuscript: {total_words:,}")
print(f"Total words recognized:    {total_recognized:,}")
print(f"Recognition rate:          {recognition_rate:.2f}%")
print()

unique_terms = len(all_terms)
print(f"Unique vocabulary terms:   {unique_terms}")
print(f"Average instances per term: {total_recognized / unique_terms:.1f}")
print()

# Projection to 10%
current_vocab_size = unique_terms
target_recognition = 10.0
current_recognition = recognition_rate

vocab_needed = (target_recognition / current_recognition) * current_vocab_size
additional_vocab = vocab_needed - current_vocab_size

print("=" * 80)
print("PROJECTION TO 10% RECOGNITION")
print("=" * 80)
print()

print(f"Current recognition: {current_recognition:.2f}%")
print(f"Current vocabulary:  {current_vocab_size} unique terms")
print()
print(f"Target recognition:  10.00%")
print(f"Vocabulary needed:   ~{int(vocab_needed)} terms")
print(f"Additional terms:    ~{int(additional_vocab)} terms")
print()

if additional_vocab < 200:
    print("✓✓✓ HIGHLY ACHIEVABLE!")
    print(f"    Need only ~{int(additional_vocab)} more medical terms")
    print("    Can reach 10% with expanded ME medical corpus")
elif additional_vocab < 500:
    print("✓✓ ACHIEVABLE")
    print(f"    Need ~{int(additional_vocab)} more terms")
    print("    Requires comprehensive ME medical vocabulary")
else:
    print("✓ CHALLENGING BUT POSSIBLE")
    print(f"    Need ~{int(additional_vocab)} more terms")
    print("    Requires complete ME corpus + variants")

print()

# Save consolidated results
output = {
    "total_words": total_words,
    "total_recognized": total_recognized,
    "recognition_rate": recognition_rate,
    "unique_terms": unique_terms,
    "by_phase": phases,
    "by_category": dict(category_stats),
    "top_terms": [
        {
            "term": term,
            "instances": data["instances"],
            "category": data["category"],
            "variants": list(data["variants"]),
        }
        for term, data in sorted_terms[:50]
    ],
    "projection": {
        "current_vocab": current_vocab_size,
        "target_recognition": 10.0,
        "vocab_needed": int(vocab_needed),
        "additional_vocab": int(additional_vocab),
    },
}

output_path = results_dir / "consolidated_findings.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(f"Consolidated results saved to: {output_path}")
print()
