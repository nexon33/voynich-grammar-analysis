"""
TASK 3: ROOT CONFIDENCE AUDIT

Review 10 lowest-confidence roots for problems:
- e, o, p, r (single-letter ambiguous)
- kch, dch, opch, pch (complex compounds)
- ee, chckhy (questionable particles)

Determine: KEEP / LOWER confidence / REMOVE
"""

import json
from collections import Counter

print("=" * 80)
print("TASK 3: ROOT CONFIDENCE AUDIT")
print("=" * 80)
print()

# Load data
print("Loading Phase 17 data...")
with open("COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8") as f:
    data = json.load(f)

translations = data.get("translations", [])
print(f"✓ Loaded {len(translations)} sentences")
print()

# Roots to audit (lowest confidence 60-70%)
AUDIT_ROOTS = [
    ("e", "process/prepare", 70, "VERBAL", "79.1% VERB suffix - but very general"),
    (
        "o",
        "oak-variant/particle",
        65,
        "MIXED",
        "Mixed patterns - 21% standalone, 46.5% case",
    ),
    ("p", "substance", 65, "NOMINAL", "95.6% case suffix - unclear meaning"),
    ("r", "substance", 65, "NOMINAL", "Speculative liquid-related"),
    ("kch", "container-process", 65, "COMPOUND", "k+ch compound - 48.6% verbal"),
    ("dch", "place-process", 60, "COMPOUND", "d+ch compound - claimed N-V"),
    ("opch", "complex-process", 60, "COMPOUND", "Unclear compound"),
    ("pch", "substance-process", 60, "COMPOUND", "p+ch compound - 55.8% verbal"),
    ("ee", "e-variant?", 60, "NOMINAL", "Possibly orthographic variant"),
    ("chckhy", "complex-particle", 60, "PARTICLE", "100% standalone - meaning unknown"),
]


def audit_root(
    root_name, claimed_meaning, claimed_confidence, claimed_class, notes, translations
):
    """Deep audit of a single root"""

    # Collect all instances
    instances = []
    suffix_distribution = Counter()
    contexts_before = []
    contexts_after = []

    for sent_idx, sentence in enumerate(translations):
        words = sentence.get("words", [])
        for word_idx, word_data in enumerate(words):
            morphology = word_data.get("morphology", {})
            root = morphology.get("root", "")

            if root == root_name:
                suffixes = morphology.get("suffixes", [])

                # Count suffixes
                if suffixes:
                    suffix_distribution["-".join(suffixes)] += 1
                else:
                    suffix_distribution["STANDALONE"] += 1

                # Context words
                if word_idx > 0:
                    prev_root = (
                        words[word_idx - 1].get("morphology", {}).get("root", "")
                    )
                    contexts_before.append(prev_root)

                if word_idx < len(words) - 1:
                    next_root = (
                        words[word_idx + 1].get("morphology", {}).get("root", "")
                    )
                    contexts_after.append(next_root)

                instances.append(
                    {
                        "original": word_data.get("original", ""),
                        "suffixes": suffixes,
                        "sent_idx": sent_idx,
                        "word_idx": word_idx,
                    }
                )

    total = len(instances)
    if total == 0:
        return None

    # Calculate statistics
    standalone_count = suffix_distribution.get("STANDALONE", 0)
    standalone_rate = standalone_count / total

    verb_count = sum(
        count
        for suffix, count in suffix_distribution.items()
        if any(vs in suffix for vs in ["dy", "edy", "ody"])
    )
    verb_rate = verb_count / total

    case_count = sum(
        count
        for suffix, count in suffix_distribution.items()
        if any(cs in suffix for cs in ["ain", "aiin", "ol", "al", "ar", "or"])
    )
    case_rate = case_count / total

    # Top co-occurring roots
    before_common = Counter(contexts_before).most_common(5)
    after_common = Counter(contexts_after).most_common(5)

    # Assess classification accuracy
    actual_class = "UNKNOWN"
    if verb_rate > 0.4:
        actual_class = "VERBAL"
    elif case_rate > 0.5:
        actual_class = "NOMINAL"
    elif standalone_rate > 0.7:
        actual_class = "PARTICLE"
    else:
        actual_class = "MIXED"

    class_matches = (actual_class == claimed_class) or (claimed_class == "MIXED")

    return {
        "root": root_name,
        "claimed_meaning": claimed_meaning,
        "claimed_confidence": claimed_confidence,
        "claimed_class": claimed_class,
        "notes": notes,
        "statistics": {
            "total_instances": total,
            "standalone_rate": standalone_rate,
            "verb_rate": verb_rate,
            "case_rate": case_rate,
            "actual_class": actual_class,
            "class_matches": class_matches,
        },
        "top_suffixes": dict(suffix_distribution.most_common(5)),
        "co_occurs_before": [{"root": r, "count": c} for r, c in before_common],
        "co_occurs_after": [{"root": r, "count": c} for r, c in after_common],
        "sample_instances": [inst["original"] for inst in instances[:5]],
    }


# Audit each root
audit_results = []

for root_name, meaning, confidence, root_class, notes in AUDIT_ROOTS:
    print(f"{'=' * 80}")
    print(f"Auditing [{root_name}]: {meaning} ({confidence}% confidence)")
    print(f"{'=' * 80}")
    print(f"Claimed class: {root_class}")
    print(f"Notes: {notes}")
    print()

    result = audit_root(root_name, meaning, confidence, root_class, notes, translations)

    if not result:
        print(f"  ⚠ No instances found!")
        continue

    stats = result["statistics"]

    print(f"  Total instances: {stats['total_instances']}")
    print(f"  Standalone rate: {stats['standalone_rate']:.1%}")
    print(f"  Verb suffix rate: {stats['verb_rate']:.1%}")
    print(f"  Case suffix rate: {stats['case_rate']:.1%}")
    print(f"  Actual class: {stats['actual_class']}")
    print(f"  Class match: {'✓' if stats['class_matches'] else '✗'}")
    print()

    print(
        f"  Top suffixes: {', '.join(f'{s}({c})' for s, c in list(result['top_suffixes'].items())[:3])}"
    )
    print(
        f"  Often before: {', '.join(r['root'] for r in result['co_occurs_before'][:3])}"
    )
    print(
        f"  Often after: {', '.join(r['root'] for r in result['co_occurs_after'][:3])}"
    )
    print()

    # Recommendation
    recommendation = "UNKNOWN"
    confidence_adjustment = 0

    if not stats["class_matches"]:
        recommendation = "REMOVE or RECLASSIFY"
        confidence_adjustment = -20
        print(f"  ⚠ ISSUE: Claimed class doesn't match actual behavior")
    elif stats["total_instances"] < 50:
        recommendation = "LOWER confidence"
        confidence_adjustment = -10
        print(f"  ⚠ Low instance count (<50) - reduce confidence")
    elif stats["total_instances"] >= 100 and stats["class_matches"]:
        recommendation = "KEEP"
        confidence_adjustment = 0
        print(f"  ✓ Sufficient instances and consistent class")
    else:
        recommendation = "KEEP with caution"
        confidence_adjustment = -5
        print(f"  ⚠ Moderate confidence - pattern holds but could be clearer")

    new_confidence = max(50, min(95, confidence + confidence_adjustment))

    print(f"  RECOMMENDATION: {recommendation}")
    print(f"  Suggested confidence: {confidence}% → {new_confidence}%")
    print()

    result["recommendation"] = recommendation
    result["confidence_adjustment"] = confidence_adjustment
    result["suggested_confidence"] = new_confidence

    audit_results.append(result)

# Summary
print("=" * 80)
print("ROOT CONFIDENCE AUDIT SUMMARY")
print("=" * 80)
print()

recommendations_count = Counter([r["recommendation"] for r in audit_results])

print(f"Total roots audited: {len(audit_results)}")
print()
print("Recommendations:")
for rec, count in recommendations_count.most_common():
    print(f"  {rec}: {count}")
print()

remove_count = sum(1 for r in audit_results if "REMOVE" in r["recommendation"])
lower_count = sum(1 for r in audit_results if "LOWER" in r["recommendation"])
keep_count = sum(1 for r in audit_results if r["recommendation"] == "KEEP")

print(f"REMOVE/RECLASSIFY: {remove_count}")
print(f"LOWER confidence: {lower_count}")
print(f"KEEP: {keep_count}")
print()

# Determine result
if remove_count <= 2 and (keep_count + lower_count) >= 7:
    task3_result = "✓ PASS"
    task3_status = "STRONG - Most roots justified"
elif remove_count <= 4:
    task3_result = "⚠ MODERATE"
    task3_status = "Some roots need revision"
else:
    task3_result = "✗ FAIL"
    task3_status = "Too many problematic roots"

print(f"Task 3 Result: {task3_result}")
print(f"Status: {task3_status}")
print()

# Save
output = {
    "summary": {
        "total_audited": len(audit_results),
        "remove_count": remove_count,
        "lower_count": lower_count,
        "keep_count": keep_count,
        "recommendations": dict(recommendations_count),
        "result": task3_result,
        "status": task3_status,
    },
    "audited_roots": audit_results,
}

with open("VALIDATION_TASK3_ROOT_CONFIDENCE_AUDIT.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("✓ Detailed results saved to: VALIDATION_TASK3_ROOT_CONFIDENCE_AUDIT.json")
print()
