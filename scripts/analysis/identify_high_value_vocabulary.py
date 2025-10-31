"""
IDENTIFY HIGH-VALUE VOCABULARY TARGETS

Goal: Increase semantic understanding from 18% to 30%+

Strategy:
1. Find most frequent unknown roots (high impact)
2. Look for roots in recognizable contexts
3. Prioritize roots that co-occur with KNOWN vocabulary
4. Focus on roots in high-confidence suffix patterns

This will identify the ~50-100 most valuable roots to decode next.
"""

import json
from collections import Counter, defaultdict

print("=" * 80)
print("HIGH-VALUE VOCABULARY TARGET IDENTIFICATION")
print("Current: 18-25% semantic understanding")
print("Goal: Identify targets to reach 30-40%")
print("=" * 80)

# Load Phase 17 translations
print("\nLoading Phase 17 translation data...")
with open("COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8") as f:
    data = json.load(f)

translations = data["translations"]
print(f"Loaded {len(translations)} lines")

# Known roots (HIGH confidence vocabulary)
KNOWN_ROOTS = {
    "qok": "oak",
    "qot": "oat",
    "dain": "water",
    "daiin": "this/that",
    "sho": "vessel",
    "cho": "vessel",
    "ar": "at/in",
    "dair": "there",
    "air": "sky",
    "dor": "red",
    "she": "water",
    "shee": "water",
    "ol": "or",
    "qol": "then",
    "sal": "and",
}

# Analyze unknown roots
unknown_roots = Counter()
unknown_with_known_context = defaultdict(list)
unknown_by_suffix = defaultdict(Counter)
unknown_standalone_rate = Counter()
unknown_total_occurrences = Counter()

print("\nAnalyzing unknown roots...")

for trans in translations:
    words = trans["words"]

    for i, word_data in enumerate(words):
        morphology = word_data["morphology"]
        root = morphology.get("root", "")
        confidence = word_data["confidence"]

        # Skip if root is known or empty
        if root in KNOWN_ROOTS or not root or len(root) < 2:
            continue

        # Count this unknown root
        unknown_roots[root] += 1
        unknown_total_occurrences[root] += 1

        # Track if it appears standalone
        if confidence == "unknown" and len(morphology.get("suffixes", [])) == 0:
            unknown_standalone_rate[root] += 1

        # Track suffix patterns
        suffixes = morphology.get("suffixes", [])
        if suffixes:
            suffix_pattern = "-".join(suffixes)
            unknown_by_suffix[root][suffix_pattern] += 1

        # Check context: does it appear near KNOWN words?
        context_words = []
        if i > 0:
            prev_root = words[i - 1]["morphology"].get("root", "")
            if prev_root in KNOWN_ROOTS:
                context_words.append(prev_root)
        if i < len(words) - 1:
            next_root = words[i + 1]["morphology"].get("root", "")
            if next_root in KNOWN_ROOTS:
                context_words.append(next_root)

        if context_words:
            # Store example with known context
            original = word_data["original"]
            translation = word_data["final_translation"]
            context = " ".join(
                [words[max(0, i - 2)]["original"] for _ in range(1)]
                + [original]
                + [words[min(len(words) - 1, i + 2)]["original"] for _ in range(1)]
            )

            if len(unknown_with_known_context[root]) < 5:  # Store up to 5 examples
                unknown_with_known_context[root].append(
                    {
                        "context": context,
                        "translation": translation,
                        "known_neighbors": context_words,
                    }
                )

# Calculate priority scores
priority_scores = {}

for root, freq in unknown_roots.most_common(200):  # Top 200 unknown roots
    score = 0

    # Factor 1: Frequency (more = better)
    score += min(freq / 100, 10)  # Cap at 10 points

    # Factor 2: Appears with known vocabulary (better for inference)
    if root in unknown_with_known_context:
        score += min(len(unknown_with_known_context[root]) * 2, 10)

    # Factor 3: Has consistent suffix patterns (easier to classify)
    if root in unknown_by_suffix:
        patterns = unknown_by_suffix[root]
        if len(patterns) <= 3:  # Consistent pattern
            score += 5

    # Factor 4: NOT mostly standalone (bound morphemes are harder)
    standalone = unknown_standalone_rate.get(root, 0)
    if standalone / freq < 0.2:  # Less than 20% standalone
        score += 3

    priority_scores[root] = {
        "score": score,
        "frequency": freq,
        "with_known_context": len(unknown_with_known_context.get(root, [])),
        "suffix_patterns": len(unknown_by_suffix.get(root, {})),
        "standalone_rate": standalone / freq if freq > 0 else 0,
    }

# Sort by priority score
sorted_targets = sorted(
    priority_scores.items(), key=lambda x: x[1]["score"], reverse=True
)

print("\n" + "=" * 80)
print("TOP 50 HIGH-VALUE VOCABULARY TARGETS")
print("=" * 80)
print()
print(
    f"{'Root':<10} {'Freq':<8} {'Score':<8} {'w/Known':<10} {'Patterns':<10} {'Standalone%':<12} {'Priority':<10}"
)
print("-" * 95)

for i, (root, metrics) in enumerate(sorted_targets[:50], 1):
    freq = metrics["frequency"]
    score = metrics["score"]
    with_known = metrics["with_known_context"]
    patterns = metrics["suffix_patterns"]
    standalone = metrics["standalone_rate"] * 100

    # Priority category
    if score >= 20:
        priority = "CRITICAL"
    elif score >= 15:
        priority = "HIGH"
    elif score >= 10:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    print(
        f"{root:<10} {freq:<8} {score:<8.1f} {with_known:<10} {patterns:<10} {standalone:>10.1f}% {priority:<10}"
    )

# Show examples for top 10
print("\n" + "=" * 80)
print("TOP 10 TARGETS WITH CONTEXT EXAMPLES")
print("=" * 80)

for i, (root, metrics) in enumerate(sorted_targets[:10], 1):
    print(f"\n{i}. ROOT: [{root}]")
    print(f"   Frequency: {metrics['frequency']}")
    print(f"   Priority Score: {metrics['score']:.1f}")
    print(f"   Appears with known vocabulary: {metrics['with_known_context']} times")

    if root in unknown_with_known_context:
        examples = unknown_with_known_context[root][:3]
        print(f"\n   Context examples:")
        for j, ex in enumerate(examples, 1):
            print(f"   {j}. {ex['context']}")
            print(f"      → {ex['translation']}")
            print(f"      Near: {', '.join(ex['known_neighbors'])}")

# Calculate potential impact
print("\n" + "=" * 80)
print("POTENTIAL IMPACT ANALYSIS")
print("=" * 80)

# If we decode top 50 roots
top_50_instances = sum(
    priority_scores[root]["frequency"] for root, _ in sorted_targets[:50]
)
corpus_size = 37125
potential_gain = (top_50_instances / corpus_size) * 100

print(f"\nCurrent semantic understanding: 18-25%")
print(
    f"Top 50 roots account for: {top_50_instances:,} instances ({potential_gain:.1f}% of corpus)"
)
print(
    f"Potential new understanding: {18 + potential_gain:.1f}% - {25 + potential_gain:.1f}%"
)
print()
print(f"If we decode:")
print(
    f"  Top 10 roots: +{sum(priority_scores[root]['frequency'] for root, _ in sorted_targets[:10]) / corpus_size * 100:.1f}%"
)
print(
    f"  Top 20 roots: +{sum(priority_scores[root]['frequency'] for root, _ in sorted_targets[:20]) / corpus_size * 100:.1f}%"
)
print(f"  Top 50 roots: +{potential_gain:.1f}%")
print(
    f"  Top 100 roots: +{sum(priority_scores[root]['frequency'] for root, _ in sorted_targets[:100]) / corpus_size * 100:.1f}%"
)

# Save results
output = {
    "current_semantic_understanding": "18-25%",
    "known_roots": list(KNOWN_ROOTS.keys()),
    "total_unknown_roots_analyzed": len(unknown_roots),
    "top_50_targets": [
        {
            "root": root,
            "frequency": metrics["frequency"],
            "priority_score": metrics["score"],
            "with_known_context": metrics["with_known_context"],
            "suffix_patterns": metrics["suffix_patterns"],
            "standalone_rate": metrics["standalone_rate"],
            "context_examples": unknown_with_known_context.get(root, [])[:3],
        }
        for root, metrics in sorted_targets[:50]
    ],
    "impact_analysis": {
        "top_10_gain_pct": sum(
            priority_scores[root]["frequency"] for root, _ in sorted_targets[:10]
        )
        / corpus_size
        * 100,
        "top_20_gain_pct": sum(
            priority_scores[root]["frequency"] for root, _ in sorted_targets[:20]
        )
        / corpus_size
        * 100,
        "top_50_gain_pct": potential_gain,
        "top_100_gain_pct": sum(
            priority_scores[root]["frequency"] for root, _ in sorted_targets[:100]
        )
        / corpus_size
        * 100,
    },
}

with open("HIGH_VALUE_VOCABULARY_TARGETS.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nResults saved to: HIGH_VALUE_VOCABULARY_TARGETS.json")
print("=" * 80)
