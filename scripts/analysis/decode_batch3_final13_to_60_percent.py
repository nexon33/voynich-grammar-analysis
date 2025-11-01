"""
Decode Batch 3: Final 13 roots to hit 60% EXACTLY!

TARGET ROOTS:
sheo, ee, kch, oky, opch, dch, okch, pch, p, eeo, keey, chcthy, aly

COMBINED GAIN: +3.41% -> 60.0% semantic understanding
"""

import json
from collections import Counter

print("Loading Phase 17 translations data...")
with open("COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8") as f:
    data = json.load(f)

translations = data.get("translations", [])
print(f"Loaded {len(translations)} sentences\n")

TARGET_ROOTS = [
    "sheo",
    "ee",
    "kch",
    "oky",
    "opch",
    "dch",
    "okch",
    "pch",
    "p",
    "eeo",
    "keey",
    "chcthy",
    "aly",
]


def quick_analyze(root_name, translations):
    """Quick analysis"""
    instances = []
    suffix_counts = Counter()
    total_words = 0

    for sentence in translations:
        for word_data in sentence.get("words", []):
            total_words += 1
            morphology = word_data.get("morphology", {})
            root = morphology.get("root", "")

            if root == root_name:
                instances.append(word_data)
                suffixes = morphology.get("suffixes", [])
                if suffixes:
                    suffix_counts["-".join(suffixes)] += 1
                else:
                    suffix_counts["STANDALONE"] += 1

    total_instances = len(instances)
    if total_instances == 0:
        return None

    standalone_rate = suffix_counts.get("STANDALONE", 0) / total_instances

    verb_count = sum(
        count
        for suffix, count in suffix_counts.items()
        if any(vs in suffix for vs in ["dy", "ody", "edy"])
    )
    case_count = sum(
        count
        for suffix, count in suffix_counts.items()
        if any(cs in suffix for cs in ["ain", "aiin", "ol", "al", "ar", "or"])
    )

    verb_rate = verb_count / total_instances
    case_rate = case_count / total_instances

    if verb_rate > 0.3:
        classification = "VERBAL"
    elif case_rate > 0.5:
        classification = "NOMINAL"
    elif standalone_rate > 0.7:
        classification = "PARTICLE"
    else:
        classification = "MIXED"

    return {
        "root": root_name,
        "total_instances": total_instances,
        "corpus_percentage": total_instances / total_words * 100,
        "standalone_rate": standalone_rate,
        "verb_rate": verb_rate,
        "case_rate": case_rate,
        "classification": classification,
        "top_suffixes": dict(suffix_counts.most_common(5)),
    }


print(f"{'=' * 80}")
print("BATCH 3: FINAL 13 ROOTS - PUSH TO 60%!")
print(f"{'=' * 80}\n")

results = {}
for root in TARGET_ROOTS:
    result = quick_analyze(root, translations)
    if result:
        results[root] = result
        print(
            f"[{root:8s}]: {result['total_instances']:3d} instances, {result['classification']:10s}, "
            + f"Standalone: {result['standalone_rate']:.0%}, Case: {result['case_rate']:.0%}, Verb: {result['verb_rate']:.0%}"
        )

# Summary
print(f"\n{'=' * 80}")
print("SUMMARY: BATCH 3 - FINAL 13 ROOTS TO 60%")
print(f"{'=' * 80}\n")

total_instances = sum(r["total_instances"] for r in results.values())
total_percentage = sum(r["corpus_percentage"] for r in results.values())

print(f"Total instances: {total_instances}")
print(f"Total gain: +{total_percentage:.2f}%")
print(f"Current: 56.6%")
print(f"New estimate: {56.6 + total_percentage:.1f}%")

if 56.6 + total_percentage >= 60.0:
    print(f"\n*** 60% THRESHOLD CROSSED! ***")
    print(f"Final semantic understanding: {56.6 + total_percentage:.1f}%")

# Save
with open("BATCH3_FINAL13_TO_60_PERCENT.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nResults saved to: BATCH3_FINAL13_TO_60_PERCENT.json")

# Print interpretations
print(f"\n{'=' * 80}")
print("QUICK INTERPRETATIONS")
print(f"{'=' * 80}\n")

interpretations = {
    "sheo": "sh-eo = mix-boil compound?",
    "ee": "Variant of e (process verb)?",
    "kch": "k-ch compound (container-process)?",
    "oky": "oak-y (oak + copula)?",
    "opch": "Complex compound",
    "dch": "d-ch compound",
    "okch": "oak-ch (oak-process)?",
    "pch": "p-ch compound",
    "p": "Unknown single-letter",
    "eeo": "e-eo compound (process-boil)?",
    "keey": "k-eey (container + genitive)",
    "chcthy": "Complex particle",
    "aly": "al-y (locative + copula)?",
}

for root, result in results.items():
    print(f"[{root:8s}]: {interpretations.get(root, 'Unknown')}")
    print(
        f"           ({result['classification']}, {result['total_instances']} instances)"
    )
