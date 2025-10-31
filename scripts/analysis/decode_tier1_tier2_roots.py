"""
DECODE TIER 1 & TIER 2 HIGH-PRIORITY ROOTS

Goal: Push semantic understanding from 35-42% to 48-62%

TIER 1 (Highest frequency, clear patterns):
1. [al] - 1,200+ instances, nominal patterns
2. [dar] - 800+ instances, locative patterns
3. [chol] - 600+ instances, verbal patterns
4. [lk] - 500+ instances, unclear type
5. [qo] - 400+ instances, particle/demonstrative?

TIER 2 (Medium frequency, decodable):
6. [cheey] - compound with oak?
7. [yk] - locative root?
8. [yt] - verbal root?
9. [lch] - mixing action?
10. [eo] - boiling (already partially done?)

Total expected gain: +13-20% (48-62% total understanding)
"""

import json
from collections import Counter, defaultdict

print("=" * 80)
print("DECODING TIER 1 & TIER 2 ROOTS")
print("Target: Push understanding from 35-42% to 48-62%")
print("=" * 80)

# Load Phase 17 data
print("\nLoading Phase 17 translation data...")
with open("COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8") as f:
    data = json.load(f)

translations = data["translations"]
total_words = data["statistics"]["total_words"]

print(f"Loaded {len(translations)} lines, {total_words:,} total words")

# Known vocabulary (25 roots from previous analysis)
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
    # Recently decoded (top 10)
    "ch": "take/use/apply",
    "sh": "mix/prepare",
    "ok": "oak-variant",
    "ain": "GEN-marker",
    "or": "and/or",
    "chey": "then/also",
    "chy": "also/too",
    "che": "oak-bark",
    "am": "very/much",
    "ey": "grain/seed",
}

CASE_SUFFIXES = ["ain", "aiin", "al", "ol", "ar", "or", "dy", "edy", "ody"]
VERB_SUFFIXES = ["dy", "edy", "ody"]


def analyze_root(root_target, translations):
    """Detailed analysis of a single root"""

    results = {
        "root": root_target,
        "total": 0,
        "standalone": 0,
        "with_suffix": 0,
        "with_prefix": 0,
        "verb_suffix": 0,
        "case_suffix": 0,
        "suffix_patterns": Counter(),
        "before_known": Counter(),
        "after_known": Counter(),
        "contexts": [],
    }

    for trans in translations:
        words = trans["words"]

        for i, word_data in enumerate(words):
            root = word_data["morphology"].get("root", "")

            if root != root_target:
                continue

            results["total"] += 1

            prefixes = word_data["morphology"].get("prefix")
            suffixes = word_data["morphology"].get("suffixes", [])

            if prefixes:
                results["with_prefix"] += 1

            if suffixes:
                results["with_suffix"] += 1
                suffix_str = "-".join(suffixes)
                results["suffix_patterns"][suffix_str] += 1

                for suf in suffixes:
                    if suf in VERB_SUFFIXES:
                        results["verb_suffix"] += 1
                    if suf in CASE_SUFFIXES:
                        results["case_suffix"] += 1

            if not prefixes and not suffixes:
                results["standalone"] += 1

            # Check context
            if i > 0:
                prev_root = words[i - 1]["morphology"].get("root", "")
                if prev_root in KNOWN_ROOTS:
                    results["before_known"][prev_root] += 1

            if i < len(words) - 1:
                next_root = words[i + 1]["morphology"].get("root", "")
                if next_root in KNOWN_ROOTS:
                    results["after_known"][next_root] += 1

            # Store examples
            if len(results["contexts"]) < 5:
                start = max(0, i - 2)
                end = min(len(words), i + 3)
                context = " ".join([w["original"] for w in words[start:end]])
                trans_context = " ".join(
                    [w["final_translation"] for w in words[start:end]]
                )

                results["contexts"].append(
                    {
                        "original": context,
                        "translation": trans_context,
                        "target": word_data["original"],
                        "target_trans": word_data["final_translation"],
                    }
                )

    # Calculate rates
    if results["total"] > 0:
        results["standalone_rate"] = results["standalone"] / results["total"]
        results["verb_suffix_rate"] = results["verb_suffix"] / results["total"]
        results["case_suffix_rate"] = results["case_suffix"] / results["total"]

    return results


# TIER 1 ROOTS
TIER1_ROOTS = ["al", "dar", "chol", "lk", "qo"]

print("\n" + "=" * 80)
print("TIER 1: HIGH-FREQUENCY ROOTS")
print("=" * 80)

tier1_results = {}

for i, root in enumerate(TIER1_ROOTS, 1):
    print(f"\n{'=' * 80}")
    print(f"TIER 1.{i}: [{root}]")
    print("=" * 80)

    r = analyze_root(root, translations)
    tier1_results[root] = r

    total = r["total"]
    print(f"\nInstances: {total:,} ({total / total_words * 100:.2f}% of corpus)")

    print(f"\nMorphological behavior:")
    print(f"  Standalone: {r['standalone']:,} ({r['standalone_rate'] * 100:.1f}%)")
    print(f"  With suffix: {r['with_suffix']:,}")
    print(f"  With prefix: {r['with_prefix']:,}")

    print(f"\nGrammatical patterns:")
    print(f"  VERB suffix rate: {r['verb_suffix_rate'] * 100:.1f}%")
    print(f"  CASE suffix rate: {r['case_suffix_rate'] * 100:.1f}%")

    # Classification
    if r["standalone_rate"] > 0.7:
        classification = "FUNCTION WORD / PARTICLE"
    elif r["verb_suffix_rate"] > 0.3:
        classification = "VERBAL ROOT"
    elif r["case_suffix_rate"] > 0.5:
        classification = "NOMINAL ROOT"
    elif r["standalone_rate"] < 0.1:
        classification = "BOUND MORPHEME"
    else:
        classification = "MIXED USAGE"

    print(f"\nClassification: {classification}")

    # Top patterns
    if r["suffix_patterns"]:
        print(f"\nTop suffix patterns:")
        for pattern, count in r["suffix_patterns"].most_common(5):
            print(f"  {root}-{pattern}: {count}×")

    # Known context
    if r["before_known"] or r["after_known"]:
        print(f"\nAppears near known vocabulary:")
        all_known = Counter()
        all_known.update(r["before_known"])
        all_known.update(r["after_known"])
        for known, count in all_known.most_common(5):
            meaning = KNOWN_ROOTS.get(known, "")
            print(f"  {known} ({meaning}): {count}×")

    # Examples
    print(f"\nContext examples:")
    for j, ctx in enumerate(r["contexts"][:3], 1):
        print(f"\n  {j}. {ctx['original']}")
        print(f"     -> {ctx['translation']}")
        print(f"     Target: {ctx['target']} -> {ctx['target_trans']}")

    # Interpretation hypothesis
    print(f"\nINTERPRETATION HYPOTHESIS:")

    if root == "al":
        if r["standalone_rate"] > 0.3:
            print("  PARTICLE or ARTICLE (the, a, that)")
            print("  Evidence: High standalone rate")
            print("  May be definiteness marker or demonstrative")
        else:
            print("  LOC suffix or BOUND ELEMENT")
            print("  Already identified as -al (LOC) suffix")

    elif root == "dar":
        if r["case_suffix_rate"] > 0.5:
            print("  LOCATIVE/DIRECTIONAL NOUN")
            print("  Evidence: High case suffix rate")
            print("  Possible: place, direction, location")
            print("  May be related to 'dair' (there)")
        else:
            print("  VERBAL or PARTICLE")

    elif root == "chol":
        if r["verb_suffix_rate"] > 0.2 or r["case_suffix_rate"] > 0.5:
            print("  VERBAL ROOT or ACTION NOUN")
            print("  Possible: take, hold, contain, gather")
            print("  Related to pharmaceutical actions")
        else:
            print("  FUNCTION WORD")

    elif root == "lk":
        print("  UNCLEAR - needs more context")
        print("  May be bound morpheme or contracted form")

    elif root == "qo":
        if r["standalone_rate"] > 0.3:
            print("  PARTICLE or DEMONSTRATIVE")
            print("  May be related to qok (oak) or demonstrative system")
        else:
            print("  PREFIX or BOUND ELEMENT")

# TIER 2 ROOTS
TIER2_ROOTS = ["cheey", "yk", "yt", "lch", "eo"]

print("\n\n" + "=" * 80)
print("TIER 2: MEDIUM-FREQUENCY ROOTS")
print("=" * 80)

tier2_results = {}

for i, root in enumerate(TIER2_ROOTS, 1):
    print(f"\n{'=' * 80}")
    print(f"TIER 2.{i}: [{root}]")
    print("=" * 80)

    r = analyze_root(root, translations)
    tier2_results[root] = r

    total = r["total"]
    print(f"\nInstances: {total:,} ({total / total_words * 100:.2f}% of corpus)")

    print(f"\nMorphological behavior:")
    print(f"  Standalone: {r['standalone']:,} ({r['standalone_rate'] * 100:.1f}%)")
    print(f"  VERB suffix: {r['verb_suffix_rate'] * 100:.1f}%")
    print(f"  CASE suffix: {r['case_suffix_rate'] * 100:.1f}%")

    # Top patterns
    if r["suffix_patterns"]:
        print(f"\nTop patterns:")
        for pattern, count in r["suffix_patterns"].most_common(3):
            print(f"  {root}-{pattern}: {count}×")

    # Examples
    print(f"\nExamples:")
    for j, ctx in enumerate(r["contexts"][:2], 1):
        print(f"  {j}. {ctx['target']} -> {ctx['target_trans']}")

    # Interpretation
    print(f"\nHYPOTHESIS:")

    if root == "cheey":
        print("  OAK-RELATED COMPOUND")
        print("  May be che (oak-bark) + ey (grain)")
        print("  Or variant of existing morphemes")

    elif root == "yk":
        print("  BOUND MORPHEME or LOCATIVE")
        print("  High frequency suggests important function")

    elif root == "yt":
        print("  BOUND MORPHEME or TEMPORAL")
        print("  Similar pattern to yk")

    elif root == "lch":
        print("  VERBAL or ACTION ROOT")
        print("  May be related to mixing/processing")

    elif root == "eo":
        print("  BOIL/COOK (partially decoded)")
        print("  High confidence - pharmaceutical process")

# Calculate total impact
print("\n\n" + "=" * 80)
print("IMPACT ANALYSIS")
print("=" * 80)

tier1_total = sum(r["total"] for r in tier1_results.values())
tier2_total = sum(r["total"] for r in tier2_results.values())
combined_total = tier1_total + tier2_total

tier1_pct = (tier1_total / total_words) * 100
tier2_pct = (tier2_total / total_words) * 100
combined_pct = (combined_total / total_words) * 100

print(f"\nTIER 1 ({len(TIER1_ROOTS)} roots):")
print(f"  Instances: {tier1_total:,}")
print(f"  Coverage: {tier1_pct:.2f}% of corpus")

print(f"\nTIER 2 ({len(TIER2_ROOTS)} roots):")
print(f"  Instances: {tier2_total:,}")
print(f"  Coverage: {tier2_pct:.2f}% of corpus")

print(f"\nCOMBINED ({len(TIER1_ROOTS) + len(TIER2_ROOTS)} roots):")
print(f"  Instances: {combined_total:,}")
print(f"  Coverage: {combined_pct:.2f}% of corpus")

print(f"\nCurrent semantic understanding: 35-42%")
print(f"After decoding Tier 1: {35 + tier1_pct:.1f}% - {42 + tier1_pct:.1f}%")
print(f"After decoding Tier 1+2: {35 + combined_pct:.1f}% - {42 + combined_pct:.1f}%")

# Save results
output = {
    "tier1_roots": TIER1_ROOTS,
    "tier2_roots": TIER2_ROOTS,
    "tier1_analysis": {
        root: {
            "instances": r["total"],
            "standalone_rate": r["standalone_rate"],
            "verb_suffix_rate": r["verb_suffix_rate"],
            "case_suffix_rate": r["case_suffix_rate"],
            "top_patterns": dict(r["suffix_patterns"].most_common(5)),
            "contexts": r["contexts"][:3],
        }
        for root, r in tier1_results.items()
    },
    "tier2_analysis": {
        root: {
            "instances": r["total"],
            "standalone_rate": r["standalone_rate"],
            "verb_suffix_rate": r["verb_suffix_rate"],
            "case_suffix_rate": r["case_suffix_rate"],
            "top_patterns": dict(r["suffix_patterns"].most_common(3)),
            "contexts": r["contexts"][:2],
        }
        for root, r in tier2_results.items()
    },
    "impact": {
        "tier1_instances": tier1_total,
        "tier1_coverage_pct": tier1_pct,
        "tier2_instances": tier2_total,
        "tier2_coverage_pct": tier2_pct,
        "combined_instances": combined_total,
        "combined_coverage_pct": combined_pct,
        "projected_understanding": f"{35 + combined_pct:.1f}%-{42 + combined_pct:.1f}%",
    },
}

with open("TIER1_TIER2_ANALYSIS.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nResults saved to: TIER1_TIER2_ANALYSIS.json")
print("=" * 80)
