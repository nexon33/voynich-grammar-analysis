#!/usr/bin/env python3
"""
Validate [?r] = "liquid/contents/mixture" hypothesis

Evidence from Phase 20:
- [?r] co-occurs with "vessel" 13×
- 0.3% VERB suffix rate (extremely low - nominal)
- 21.5% standalone rate
- Appears with locative marking

Test: If [?r] means "liquid/contents", it should:
1. Appear AFTER vessel frequently
2. Take locative marking ([?r]-LOC = "in the liquid")
3. Co-occur with water
4. Appear in recipe/preparation contexts
"""

import json
import re
from collections import Counter


def load_translations():
    """Load translations"""
    with open(
        "COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)
        return data["translations"]


def test_vessel_r_pattern(translations):
    """
    Test 1: vessel ... [?r] pattern

    If [?r] means "liquid/contents":
    Should appear near vessel (within 5 words)
    """
    vessel_r = []

    for trans in translations:
        sentence = trans["final_translation"]
        words = sentence.split()

        # Find vessel and [?r] positions
        vessel_indices = [i for i, w in enumerate(words) if "vessel" in w.lower()]
        r_indices = [i for i, w in enumerate(words) if "[?r]" in w]

        # Check if they appear together (within 5 words)
        for v_idx in vessel_indices:
            for r_idx in r_indices:
                if abs(r_idx - v_idx) <= 5:
                    before = words[max(0, r_idx - 3) : r_idx]
                    after = words[r_idx + 1 : min(len(words), r_idx + 4)]

                    vessel_r.append(
                        {
                            "line": trans.get("line", "unknown"),
                            "word": words[r_idx],
                            "distance": abs(r_idx - v_idx),
                            "before": before,
                            "after": after,
                            "full_sentence": sentence,
                        }
                    )
                    break  # Only count once per sentence

    return vessel_r


def test_r_locative(translations):
    """
    Test 2: [?r] + locative marking

    If [?r] means "liquid/contents":
    Should take locative marking: [?r]-LOC = "in the liquid"
    """
    r_loc = []

    for trans in translations:
        sentence = trans["final_translation"]
        words = sentence.split()

        for i, word in enumerate(words):
            if "[?r]" in word and "-LOC" in word:
                before = words[max(0, i - 3) : i]
                after = words[i + 1 : min(len(words), i + 4)]

                r_loc.append(
                    {
                        "line": trans.get("line", "unknown"),
                        "word": word,
                        "before": before,
                        "after": after,
                        "full_sentence": sentence,
                    }
                )

    return r_loc


def test_water_r_cooccurrence(translations):
    """
    Test 3: water ... [?r] co-occurrence

    If [?r] means "liquid":
    Should co-occur with "water" (another liquid term)
    """
    water_r = []

    for trans in translations:
        sentence = trans["final_translation"]

        if "water" in sentence.lower() and "[?r]" in sentence:
            words = sentence.split()
            water_indices = [i for i, w in enumerate(words) if "water" in w.lower()]
            r_indices = [i for i, w in enumerate(words) if "[?r]" in w]

            # Find distance
            for w_idx in water_indices:
                for r_idx in r_indices:
                    distance = abs(r_idx - w_idx)
                    if distance <= 10:  # Within 10 words
                        water_r.append(
                            {
                                "line": trans.get("line", "unknown"),
                                "distance": distance,
                                "full_sentence": sentence,
                            }
                        )
                        break

    return water_r


def test_r_with_al(translations):
    """
    Test 4: [?r] with [?al] co-occurrence

    From Phase 20: [?r] co-occurs with [?al] (14× after)
    If [?r] = "liquid" and [?al] = "substance":
    Pattern might be: "[?r] [?al]" = "liquid substance" = "solution"
    """
    r_al = []

    for trans in translations:
        sentence = trans["final_translation"]

        # Pattern: [?r] ... [?al] (within 3 words)
        words = sentence.split()
        for i, word in enumerate(words):
            if "[?r]" in word:
                # Check next 3 words for [?al]
                next_words = words[i + 1 : min(len(words), i + 4)]
                if any("[?al]" in w for w in next_words):
                    r_al.append(
                        {
                            "line": trans.get("line", "unknown"),
                            "context": " ".join(
                                words[max(0, i - 2) : min(len(words), i + 5)]
                            ),
                            "full_sentence": sentence,
                        }
                    )

    return r_al


def analyze_r_contexts(translations):
    """
    General context analysis: What appears near [?r]?
    """
    before_r = Counter()
    after_r = Counter()

    for trans in translations:
        sentence = trans["final_translation"]
        words = sentence.split()

        for i, word in enumerate(words):
            if "[?r]" in word:
                # 3 words before and after
                before = words[max(0, i - 3) : i]
                after = words[i + 1 : min(len(words), i + 4)]

                before_r.update(before)
                after_r.update(after)

    return before_r, after_r


def main():
    """Main validation"""
    print("=" * 70)
    print("VALIDATING [?r] = 'liquid/contents/mixture' HYPOTHESIS")
    print("=" * 70)
    print("\nFrom Phase 20 findings:")
    print("- [?r]: 289 instances (0.8% of corpus)")
    print("- VERB suffix rate: 0.3% (EXTREMELY low - nominal)")
    print("- Co-occurs with vessel: 13×")
    print("- Standalone rate: 21.5%")
    print("\nHypothesis: [?r] means 'liquid', 'contents', or 'mixture'")
    print("(Medieval recipes constantly reference vessel contents/liquids)\n")

    print("Loading translations...")
    translations = load_translations()
    print(f"Loaded {len(translations)} translations\n")

    # TEST 1: vessel + [?r] pattern
    print("=" * 70)
    print("TEST 1: VESSEL + [?r] PATTERN")
    print("=" * 70)
    print("If [?r] = 'liquid/contents', should appear near 'vessel'\n")

    vessel_r = test_vessel_r_pattern(translations)
    print(f"Result: {len(vessel_r)} instances of vessel near [?r]")

    print("\nSample contexts (first 5):")
    for i, ctx in enumerate(vessel_r[:5], 1):
        print(f"\n  {i}. {ctx['line']} (distance: {ctx['distance']} words)")
        print(
            f"     ...{' '.join(ctx['before'])} **{ctx['word']}** {' '.join(ctx['after'])}..."
        )

    if len(vessel_r) > 8:
        print(f"\n✓ STRONG EVIDENCE: {len(vessel_r)} co-occurrences (expected >8)")
    else:
        print(f"\n? WEAK EVIDENCE: Only {len(vessel_r)} co-occurrences (expected >8)")

    # TEST 2: [?r]-LOC pattern
    print("\n" + "=" * 70)
    print("TEST 2: [?r] + LOCATIVE MARKING")
    print("=" * 70)
    print("If [?r] = 'liquid/contents', should take LOC: [?r]-LOC = 'in the liquid'\n")

    r_loc = test_r_locative(translations)
    print(f"Result: {len(r_loc)} instances of [?r]-LOC")

    print("\nSample contexts (first 5):")
    for i, ctx in enumerate(r_loc[:5], 1):
        print(f"\n  {i}. {ctx['line']}")
        print(
            f"     ...{' '.join(ctx['before'])} **{ctx['word']}** {' '.join(ctx['after'])}..."
        )

    if len(r_loc) > 30:
        print(
            f"\n✓ STRONG EVIDENCE: {len(r_loc)} instances with locative (expected >30)"
        )
    else:
        print(f"\n? WEAK EVIDENCE: Only {len(r_loc)} instances (expected >30)")

    # TEST 3: water + [?r] co-occurrence
    print("\n" + "=" * 70)
    print("TEST 3: WATER + [?r] CO-OCCURRENCE")
    print("=" * 70)
    print("If [?r] = 'liquid', should co-occur with 'water' (another liquid)\n")

    water_r = test_water_r_cooccurrence(translations)
    print(f"Result: {len(water_r)} instances of water near [?r]")

    if water_r:
        print("\nSample contexts (first 3):")
        for i, ctx in enumerate(water_r[:3], 1):
            print(f"\n  {i}. {ctx['line']} (distance: {ctx['distance']} words)")
            print(f"     {ctx['full_sentence'][:100]}...")

    if len(water_r) > 15:
        print(f"\n✓ STRONG EVIDENCE: {len(water_r)} co-occurrences (expected >15)")
    elif len(water_r) > 5:
        print(f"\n⚠ MODERATE EVIDENCE: {len(water_r)} co-occurrences")
    else:
        print(f"\n? WEAK EVIDENCE: Only {len(water_r)} co-occurrences")

    # TEST 4: [?r] + [?al] pattern
    print("\n" + "=" * 70)
    print("TEST 4: [?r] + [?al] PATTERN")
    print("=" * 70)
    print("If [?r] = 'liquid' and [?al] = 'substance':")
    print("Pattern '[?r] [?al]' might mean 'liquid substance' = 'solution'\n")

    r_al = test_r_with_al(translations)
    print(f"Result: {len(r_al)} instances of [?r] near [?al]")

    if r_al:
        print("\nSample contexts (first 3):")
        for i, ctx in enumerate(r_al[:3], 1):
            print(f"\n  {i}. {ctx['line']}")
            print(f"     {ctx['context']}")

    if len(r_al) > 10:
        print(f"\n✓ INTERESTING PATTERN: {len(r_al)} instances")
        print("  This suggests [?r] and [?al] form compounds/phrases")
    else:
        print(f"\n  {len(r_al)} instances noted")

    # GENERAL CONTEXT ANALYSIS
    print("\n" + "=" * 70)
    print("GENERAL CONTEXT ANALYSIS")
    print("=" * 70)

    before_r, after_r = analyze_r_contexts(translations)

    print("\nTop 10 words BEFORE [?r]:")
    for word, count in before_r.most_common(10):
        print(f"  {word}: {count}×")

    print("\nTop 10 words AFTER [?r]:")
    for word, count in after_r.most_common(10):
        print(f"  {word}: {count}×")

    # Count process verbs
    process_verbs_before = sum(
        count
        for word, count in before_r.items()
        if "VERB" in word and any(v in word for v in ["[?ch]", "[?sh]", "[?lch]"])
    )
    process_verbs_after = sum(
        count
        for word, count in after_r.items()
        if "VERB" in word and any(v in word for v in ["[?ch]", "[?sh]", "[?lch]"])
    )

    print(f"\nProcess verbs near [?r]:")
    print(f"  Before: {process_verbs_before}×")
    print(f"  After: {process_verbs_after}×")

    if process_verbs_before + process_verbs_after > 30:
        print("  ✓ [?r] appears in process/recipe contexts")

    # FINAL VERDICT
    print("\n" + "=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)

    evidence_count = 0

    if len(vessel_r) > 8:
        evidence_count += 1
        print("✓ Test 1 (vessel co-occurrence): PASSED")
    else:
        print("✗ Test 1 (vessel co-occurrence): FAILED")

    if len(r_loc) > 30:
        evidence_count += 1
        print("✓ Test 2 (locative marking): PASSED")
    else:
        print("✗ Test 2 (locative marking): FAILED")

    if len(water_r) > 15:
        evidence_count += 1
        print("✓ Test 3 (water co-occurrence): PASSED")
    elif len(water_r) > 5:
        print("⚠ Test 3 (water co-occurrence): MARGINAL")
    else:
        print("✗ Test 3 (water co-occurrence): FAILED")

    print(f"\nEvidence summary: {evidence_count}/3 tests passed")

    if evidence_count >= 2:
        print("\n" + "=" * 70)
        print("✓ HYPOTHESIS CONFIRMED: [?r] = 'liquid/contents/mixture'")
        print("=" * 70)
        print("Confidence: MODERATE to HIGH")
        print("\nMeaning:")
        print("  [?r] = 'liquid', 'contents', 'mixture'")
        print("  vessel [?r]-LOC = 'in vessel's liquid/contents'")
        print("  [?r] [?al] = 'liquid substance' = 'solution'")
        print("\nMedieval parallel:")
        print("  Latin 'aqua' (water/liquid), 'contentus' (contents)")
        print("  'in vase liquido' = 'in vessel's liquid'")
        print("\nImpact:")
        print("  Recognition gain: +0.8%")
        print("  Unlocks vessel-based recipe instructions")
    else:
        print("\n" + "=" * 70)
        print("? HYPOTHESIS UNCERTAIN")
        print("=" * 70)
        print(f"Only {evidence_count}/3 tests passed")
        print("More investigation needed")

    # Save results
    results = {
        "hypothesis": "[?r] = liquid/contents/mixture",
        "evidence_count": evidence_count,
        "vessel_r_count": len(vessel_r),
        "r_loc_count": len(r_loc),
        "water_r_count": len(water_r),
        "r_al_count": len(r_al),
        "top_before": dict(before_r.most_common(20)),
        "top_after": dict(after_r.most_common(20)),
        "sample_vessel_r": [
            {
                "line": ctx["line"],
                "word": ctx["word"],
                "distance": ctx["distance"],
                "context": " ".join(ctx["before"] + [ctx["word"]] + ctx["after"]),
            }
            for ctx in vessel_r[:10]
        ],
        "sample_r_loc": [
            {
                "line": ctx["line"],
                "word": ctx["word"],
                "context": " ".join(ctx["before"] + [ctx["word"]] + ctx["after"]),
            }
            for ctx in r_loc[:10]
        ],
    }

    print("\nSaving results to R_LIQUID_VALIDATION.json...")
    with open("R_LIQUID_VALIDATION.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\nDONE!")


if __name__ == "__main__":
    main()
