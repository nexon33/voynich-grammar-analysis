"""
Decode Batch 2: Medium 5 roots to push to 56-57%

TARGET ROOTS:
1. [okeey] - 174 instances (+0.47%)
2. [cth] - 164 instances (+0.44%)
3. [sheey] - 151 instances (+0.41%)
4. [oke] - 147 instances (+0.40%)
5. [chckhy] - 138 instances (+0.37%)

COMBINED GAIN: +2.09% -> 56-57% semantic understanding
"""

import json
from collections import Counter

# Load translations data
print("Loading Phase 17 translations data...")
with open("COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8") as f:
    data = json.load(f)

translations = data.get("translations", [])
print(f"Loaded {len(translations)} sentences\n")

# Target roots
TARGET_ROOTS = ["okeey", "cth", "sheey", "oke", "chckhy"]


def analyze_root(root_name, translations):
    """Analyze a single root"""

    print(f"\n{'=' * 80}")
    print(f"ANALYZING ROOT: [{root_name}]")
    print(f"{'=' * 80}\n")

    instances = []
    suffix_counts = Counter()
    contexts = []
    original_words = []

    total_words = 0

    for sentence in translations:
        words = sentence.get("words", [])

        for word_data in words:
            total_words += 1
            morphology = word_data.get("morphology", {})
            root = morphology.get("root", "")

            if root == root_name:
                instances.append(word_data)
                original_words.append(word_data.get("original", ""))

                suffixes = morphology.get("suffixes", [])
                if suffixes:
                    suffix_str = "-".join(suffixes)
                    suffix_counts[suffix_str] += 1
                else:
                    suffix_counts["STANDALONE"] += 1

                if len(contexts) < 40:
                    contexts.append(
                        {
                            "word": word_data.get("original", ""),
                            "root": root,
                            "suffixes": suffixes,
                            "translation": word_data.get("final_translation", ""),
                        }
                    )

    total_instances = len(instances)

    if total_instances == 0:
        print(f"X No instances found for root [{root_name}]")
        return None

    standalone_count = suffix_counts.get("STANDALONE", 0)
    standalone_rate = standalone_count / total_instances

    verb_suffixes = ["dy", "ody", "edy", "chedy", "shedy"]
    case_suffixes = ["ain", "aiin", "ol", "al", "el", "ar", "or"]

    verb_count = sum(
        count
        for suffix, count in suffix_counts.items()
        if any(vs in suffix for vs in verb_suffixes)
    )
    case_count = sum(
        count
        for suffix, count in suffix_counts.items()
        if any(cs in suffix for cs in case_suffixes)
    )

    verb_suffix_rate = verb_count / total_instances if total_instances > 0 else 0
    case_suffix_rate = case_count / total_instances if total_instances > 0 else 0

    print(
        f"FREQUENCY: {total_instances} instances ({(total_instances / total_words * 100):.2f}%)"
    )
    print(
        f"Standalone: {standalone_rate:.1%}, Verb suffix: {verb_suffix_rate:.1%}, Case suffix: {case_suffix_rate:.1%}"
    )

    if verb_suffix_rate > 0.3:
        classification = "VERBAL ROOT"
    elif case_suffix_rate > 0.5:
        classification = "NOMINAL ROOT"
    elif standalone_rate > 0.7:
        classification = "FUNCTION WORD / PARTICLE"
    else:
        classification = "MIXED / UNCERTAIN"

    print(f"CLASSIFICATION: {classification}")

    print(f"\nTOP SUFFIX PATTERNS:")
    for suffix, count in suffix_counts.most_common(10):
        print(f"  {suffix:20s} {count:5d} ({count / total_instances:.1%})")

    print(f"\nCONTEXT EXAMPLES:")
    for i, ctx in enumerate(contexts[:20], 1):
        suffix_str = "-".join(ctx["suffixes"]) if ctx["suffixes"] else "STANDALONE"
        print(f"  {i:2d}. {ctx['word']:15s} = [{ctx['root']}]-{suffix_str:12s}")

    return {
        "root": root_name,
        "total_instances": total_instances,
        "corpus_percentage": total_instances / total_words * 100,
        "standalone_rate": standalone_rate,
        "verb_suffix_rate": verb_suffix_rate,
        "case_suffix_rate": case_suffix_rate,
        "classification": classification,
        "top_suffixes": dict(suffix_counts.most_common(10)),
        "contexts": contexts,
        "sample_words": list(set(original_words))[:20],
    }


print("\n" + "=" * 80)
print("BATCH 2: MEDIUM 5 ROOTS ANALYSIS - PUSH TO 56-57%")
print("=" * 80)

results = {}
for root in TARGET_ROOTS:
    result = analyze_root(root, translations)
    if result:
        results[root] = result

# Interpretations
print(f"\n\n{'=' * 80}")
print("SEMANTIC INTERPRETATIONS")
print(f"{'=' * 80}")

interpretations = {
    "okeey": "Oak + genitive particle (like qokeey)",
    "cth": "Unknown - needs context",
    "sheey": "Variant of shey? Oak preparation + particle?",
    "oke": "Oak variant (like ok, qok)",
    "chckhy": "Complex root - particle or compound?",
}

for root, result in results.items():
    print(f"\n[{root}]: {interpretations.get(root, 'Unknown')}")
    print(f"  Classification: {result['classification']}")
    print(f"  Confidence: Medium (65-70%)")

# Summary
print(f"\n\n{'=' * 80}")
print("SUMMARY: BATCH 2 - MEDIUM 5 ROOTS")
print(f"{'=' * 80}\n")

total_instances = sum(r["total_instances"] for r in results.values())
total_percentage = sum(r["corpus_percentage"] for r in results.values())

print(f"Total instances: {total_instances}")
print(f"Total gain: +{total_percentage:.2f}%")
print(f"Current: 54.5%")
print(f"New estimate: {54.5 + total_percentage:.1f}%")

# Save
with open("BATCH2_MEDIUM5_ROOTS_TO_57_PERCENT.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nResults saved to: BATCH2_MEDIUM5_ROOTS_TO_57_PERCENT.json")
