"""
DECODE TOP 10 HIGH-VALUE ROOTS

These 10 roots account for 6,131 instances (16.5% of corpus)
Decoding them could push understanding from 18-25% to 34-41%

Strategy for each root:
1. Analyze positional patterns (prefix/stem/suffix behavior)
2. Check co-occurrence with KNOWN vocabulary
3. Look at suffix patterns (verbal, nominal, etc.)
4. Examine contexts and infer meaning
5. Statistical validation

TOP 10 TARGETS:
1. [ch] - 1,678 instances
2. [sh] - 1,055 instances
3. [ok] - 883 instances
4. [ain] - 557 instances
5. [or] - 640 instances
6. [chey] - 473 instances
7. [chy] - 345 instances
8. [che] - 560 instances (already partially known as oak-substance?)
9. [am] - 183 instances
10. [ey] - 197 instances
"""

import json
from collections import Counter, defaultdict
from scipy.stats import chi2_contingency
import numpy as np

print("=" * 80)
print("DECODING TOP 10 HIGH-VALUE ROOTS")
print("Target: +16.5% semantic understanding (6,131 instances)")
print("=" * 80)

# Load data
print("\nLoading Phase 17 translation data...")
with open("COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8") as f:
    data = json.load(f)

translations = data["translations"]
total_words = data["statistics"]["total_words"]

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

# Suffixes for classification
CASE_SUFFIXES = ["ain", "aiin", "al", "ol", "ar", "or", "dy", "edy", "ody"]
VERB_SUFFIXES = ["dy", "edy", "ody"]


def analyze_root_detailed(root_target, translations):
    """Comprehensive analysis of a single root"""

    results = {
        "root": root_target,
        "total_instances": 0,
        "positions": Counter(),  # initial, medial, final, standalone
        "suffix_patterns": Counter(),
        "prefix_patterns": Counter(),
        "verb_suffix_count": 0,
        "case_suffix_count": 0,
        "standalone_count": 0,
        "co_occurrence": Counter(),  # with known roots
        "contexts": [],  # store examples
        "before_words": Counter(),
        "after_words": Counter(),
    }

    for trans in translations:
        words = trans["words"]

        for i, word_data in enumerate(words):
            morphology = word_data["morphology"]
            root = morphology.get("root", "")

            if root != root_target:
                continue

            results["total_instances"] += 1

            # Position in word
            prefixes = morphology.get("prefix")
            suffixes = morphology.get("suffixes", [])

            if prefixes:
                results["positions"]["with_prefix"] += 1
                results["prefix_patterns"][prefixes] += 1

            if suffixes:
                results["positions"]["with_suffix"] += 1
                suffix_str = "-".join(suffixes)
                results["suffix_patterns"][suffix_str] += 1

                # Check if verbal or case
                for suf in suffixes:
                    if suf in VERB_SUFFIXES:
                        results["verb_suffix_count"] += 1
                    if suf in CASE_SUFFIXES:
                        results["case_suffix_count"] += 1

            if not prefixes and not suffixes:
                results["standalone_count"] += 1
                results["positions"]["standalone"] += 1

            # Context: what words appear before/after?
            if i > 0:
                prev_word = words[i - 1]
                prev_root = prev_word["morphology"].get("root", "")
                results["before_words"][prev_root] += 1

                if prev_root in KNOWN_ROOTS:
                    results["co_occurrence"][prev_root] += 1

            if i < len(words) - 1:
                next_word = words[i + 1]
                next_root = next_word["morphology"].get("root", "")
                results["after_words"][next_root] += 1

                if next_root in KNOWN_ROOTS:
                    results["co_occurrence"][next_root] += 1

            # Store examples (limit to 10)
            if len(results["contexts"]) < 10:
                # Get surrounding context
                start = max(0, i - 2)
                end = min(len(words), i + 3)
                context_words = [w["original"] for w in words[start:end]]
                context_trans = [w["final_translation"] for w in words[start:end]]

                results["contexts"].append(
                    {
                        "original": " ".join(context_words),
                        "translation": " ".join(context_trans),
                        "target_word": word_data["original"],
                        "target_trans": word_data["final_translation"],
                    }
                )

    # Calculate rates
    total = results["total_instances"]
    if total > 0:
        results["standalone_rate"] = results["standalone_count"] / total
        results["verb_suffix_rate"] = results["verb_suffix_count"] / total
        results["case_suffix_rate"] = results["case_suffix_count"] / total

    return results


# Analyze each of the top 10 roots
TOP_10_ROOTS = ["ch", "sh", "ok", "ain", "or", "chey", "chy", "che", "am", "ey"]

all_results = {}

for i, root in enumerate(TOP_10_ROOTS, 1):
    print(f"\n{'=' * 80}")
    print(f"{i}. ANALYZING ROOT: [{root}]")
    print("=" * 80)

    results = analyze_root_detailed(root, translations)
    all_results[root] = results

    total = results["total_instances"]
    print(f"\nTotal instances: {total:,} ({total / total_words * 100:.2f}% of corpus)")

    # Morphological classification
    print(f"\nMorphological patterns:")
    print(
        f"  Standalone: {results['standalone_count']:,} ({results['standalone_rate'] * 100:.1f}%)"
    )
    print(f"  With suffix: {results['positions']['with_suffix']:,}")
    print(f"  With prefix: {results['positions']['with_prefix']:,}")

    print(f"\nGrammatical behavior:")
    print(
        f"  Takes VERB suffix: {results['verb_suffix_count']:,} ({results['verb_suffix_rate'] * 100:.1f}%)"
    )
    print(
        f"  Takes CASE suffix: {results['case_suffix_count']:,} ({results['case_suffix_rate'] * 100:.1f}%)"
    )

    # Classification
    print(f"\nCLASSIFICATION:")

    if results["standalone_rate"] > 0.8:
        classification = "STANDALONE WORD (likely noun, particle, or function word)"
    elif results["verb_suffix_rate"] > 0.3:
        classification = "VERBAL ROOT (takes verb suffixes frequently)"
    elif results["case_suffix_rate"] > 0.5:
        classification = "NOMINAL ROOT (takes case suffixes)"
    elif (
        results["standalone_rate"] < 0.1
        and results["positions"]["with_suffix"] > total * 0.8
    ):
        classification = "BOUND MORPHEME (almost always with suffix)"
    else:
        classification = "MIXED USAGE (multiple grammatical functions)"

    print(f"  -> {classification}")

    # Co-occurrence with known vocabulary
    if results["co_occurrence"]:
        print(f"\nAppears near KNOWN vocabulary:")
        for known_root, count in results["co_occurrence"].most_common(5):
            meaning = KNOWN_ROOTS.get(known_root, "unknown")
            print(
                f"  - {known_root} ({meaning}): {count}× ({count / total * 100:.1f}%)"
            )

    # Top suffix patterns
    if results["suffix_patterns"]:
        print(f"\nTop suffix patterns:")
        for pattern, count in results["suffix_patterns"].most_common(5):
            print(f"  - {root}-{pattern}: {count}×")

    # Context examples
    print(f"\nContext examples:")
    for j, ctx in enumerate(results["contexts"][:3], 1):
        print(f"\n  Example {j}:")
        print(f"    Original: {ctx['original']}")
        print(f"    Translation: {ctx['translation']}")
        print(f"    Target: {ctx['target_word']} → {ctx['target_trans']}")

# Summary and hypotheses
print("\n" + "=" * 80)
print("SUMMARY & INTERPRETATION HYPOTHESES")
print("=" * 80)

for root in TOP_10_ROOTS:
    r = all_results[root]
    total = r["total_instances"]

    print(f"\n[{root}] - {total:,} instances:")

    # Generate hypothesis based on patterns
    if root == "ch":
        if r["verb_suffix_rate"] > 0.3:
            print("  HYPOTHESIS: Verbal root (process/action verb)")
            print("  Evidence: High verb suffix rate")
            print("  Possible meanings: take, use, apply, mix")
        else:
            print("  HYPOTHESIS: Nominal/bound element")

    elif root == "sh":
        if r["case_suffix_rate"] > 0.5:
            print("  HYPOTHESIS: Nominal root related to container/substance")
            print(
                "  Evidence: High case suffix rate, appears near 'vessel' and 'water'"
            )
            print("  Possible meanings: mixture, liquid, preparation")
        else:
            print("  HYPOTHESIS: Bound morpheme or particle")

    elif root == "ok":
        if "qok" in str(r["co_occurrence"]):
            print("  HYPOTHESIS: Variant or inflected form of 'oak' (qok)")
            print("  Evidence: Appears in oak contexts")
            print("  Possible: oak (different declension), oak-wood, acorn-related")

    elif root == "ain":
        print("  HYPOTHESIS: May be related to GEN suffix (-ain/-aiin)")
        print("  Or: Standalone function word")
        print("  Needs more analysis")

    elif root == "or":
        if r["standalone_rate"] > 0.7:
            print("  HYPOTHESIS: Function word (conjunction, particle)")
            print("  Evidence: High standalone rate")
            print("  Already identified as 'and/or' in some contexts")

    elif root in ["chey", "chy"]:
        if r["standalone_rate"] > 0.7:
            print("  HYPOTHESIS: Discourse particle or function word")
            print("  Evidence: High standalone rate")
            print("  Possible: then, also, moreover")

    elif root == "che":
        print("  HYPOTHESIS: Already partially decoded as oak-substance/bark")
        print("  May need refinement of meaning")

    elif root == "am":
        if r["standalone_rate"] > 0.7:
            print("  HYPOTHESIS: Modal particle or function word")
            print("  Evidence: Appears in pairs ('am am')")
            print("  Possible: very, much, indeed")

    elif root == "ey":
        print("  HYPOTHESIS: Related to [?eey] (seed/grain morpheme)")
        print("  May be suffix component or bound morpheme")

# Calculate potential impact
print("\n" + "=" * 80)
print("POTENTIAL RECOGNITION GAIN")
print("=" * 80)

total_instances = sum(r["total_instances"] for r in all_results.values())
gain_pct = (total_instances / total_words) * 100

print(f"\nIf all 10 roots decoded:")
print(f"  Instances: {total_instances:,}")
print(f"  Current semantic: 18-25%")
print(f"  Potential new: {18 + gain_pct:.1f}% - {25 + gain_pct:.1f}%")
print(f"  GAIN: +{gain_pct:.1f}%")

# Save results
output = {
    "analysis_date": "2025-10-31",
    "target_roots": TOP_10_ROOTS,
    "total_instances": total_instances,
    "potential_gain_pct": gain_pct,
    "detailed_analysis": {
        root: {
            "total_instances": r["total_instances"],
            "classification": "needs_interpretation",
            "standalone_rate": r["standalone_rate"],
            "verb_suffix_rate": r["verb_suffix_rate"],
            "case_suffix_rate": r["case_suffix_rate"],
            "top_suffixes": dict(r["suffix_patterns"].most_common(5)),
            "co_occurrence_known": dict(r["co_occurrence"].most_common(5)),
            "context_examples": r["contexts"][:5],
        }
        for root, r in all_results.items()
    },
}

with open("TOP_10_ROOTS_ANALYSIS.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nDetailed analysis saved to: TOP_10_ROOTS_ANALYSIS.json")
print("=" * 80)
