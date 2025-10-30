#!/usr/bin/env python3
"""
Validate [?lch] = "mix/combine" Semantic Hypothesis

From Phase 20:
- [?lch]: 582 instances (1.6% of corpus)
- Classification: VERBAL (40.4% VERB suffix, 12.5% standalone)
- Co-occurs with [?ch]-VERB (45× before, 36× after)
- Co-occurs with [?sh]-VERB (37× before, 25× after)

Hypothesis: [?lch] = "mix", "combine", or "process" (distinct from [?ch] "prepare" and [?sh] "apply")

Tests:
1. Recipe sequence position (if mixing, should come between preparation and application)
2. Vessel/water co-occurrence (mixing happens in vessels with liquid)
3. Multiple ingredient contexts (mixing requires ≥2 ingredients)
4. Compare with [?ch] and [?sh] contexts (should be distinct)
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


def test_recipe_sequence_position(translations):
    """
    Test 1: Recipe sequence position

    If [?lch] = mix/combine:
    Should appear BETWEEN [?ch] (prepare) and [?sh] (apply)
    Pattern: [?ch]-VERB ... [?lch]-VERB ... [?sh]-VERB
    """
    sequences = []

    for trans in translations:
        sentence = trans["final_translation"]

        # Find sentences with all three verbs
        if (
            "[?ch]-VERB" in sentence
            and "[?lch]" in sentence
            and "[?sh]-VERB" in sentence
        ):
            words = sentence.split()

            # Find positions
            ch_pos = [i for i, w in enumerate(words) if "[?ch]-VERB" in w]
            lch_pos = [i for i, w in enumerate(words) if "[?lch]" in w]
            sh_pos = [i for i, w in enumerate(words) if "[?sh]-VERB" in w]

            if ch_pos and lch_pos and sh_pos:
                # Check if order is: ch < lch < sh
                for ch_i in ch_pos:
                    for lch_i in lch_pos:
                        for sh_i in sh_pos:
                            if ch_i < lch_i < sh_i:
                                sequences.append(
                                    {
                                        "line": trans.get("line", "unknown"),
                                        "sentence": sentence,
                                        "positions": (ch_i, lch_i, sh_i),
                                    }
                                )
                                break

    return sequences


def test_vessel_water_cooccurrence(translations):
    """
    Test 2: Vessel/water co-occurrence

    If [?lch] = mix/combine:
    Should appear with vessel and/or water (mixing requires container/liquid)
    """
    with_vessel = []
    with_water = []
    with_r_liquid = []

    for trans in translations:
        sentence = trans["final_translation"]

        if "[?lch]" in sentence:
            if "vessel" in sentence.lower():
                with_vessel.append(sentence)
            if "water" in sentence.lower():
                with_water.append(sentence)
            if "[?r]" in sentence:  # [?r] = liquid/contents
                with_r_liquid.append(sentence)

    return with_vessel, with_water, with_r_liquid


def test_multiple_ingredients(translations):
    """
    Test 3: Multiple ingredient contexts

    If [?lch] = mix/combine:
    Should appear with ≥2 ingredients (can't mix one thing)
    Look for: oak + oat, or botanical + oak, etc.
    """
    multiple_ingredients = []

    ingredients = ["oak", "oat", "botanical-term", "[?s]", "[?al]", "[?r]", "water"]

    for trans in translations:
        sentence = trans["final_translation"]

        if "[?lch]" in sentence:
            # Count different ingredients
            ingredient_count = sum(1 for ing in ingredients if ing in sentence.lower())

            if ingredient_count >= 2:
                multiple_ingredients.append(
                    {
                        "line": trans.get("line", "unknown"),
                        "sentence": sentence,
                        "ingredient_count": ingredient_count,
                    }
                )

    return multiple_ingredients


def compare_verb_contexts(translations):
    """
    Test 4: Compare [?lch] with [?ch] and [?sh] contexts

    If [?lch] is distinct:
    Should have different co-occurrence patterns
    """
    contexts = {
        "[?ch]": {"before": Counter(), "after": Counter()},
        "[?lch]": {"before": Counter(), "after": Counter()},
        "[?sh]": {"before": Counter(), "after": Counter()},
    }

    for trans in translations:
        sentence = trans["final_translation"]
        words = sentence.split()

        for verb_pattern in ["[?ch]-VERB", "[?lch]", "[?sh]-VERB"]:
            for i, word in enumerate(words):
                if verb_pattern in word:
                    before = words[max(0, i - 3) : i]
                    after = words[i + 1 : min(len(words), i + 3 + 1)]

                    # Determine which verb
                    if "[?ch]-VERB" in word:
                        contexts["[?ch]"]["before"].update(before)
                        contexts["[?ch]"]["after"].update(after)
                    elif "[?lch]" in word:
                        contexts["[?lch]"]["before"].update(before)
                        contexts["[?lch]"]["after"].update(after)
                    elif "[?sh]-VERB" in word:
                        contexts["[?sh]"]["before"].update(before)
                        contexts["[?sh]"]["after"].update(after)

    return contexts


def main():
    """Main validation"""
    print("=" * 70)
    print("VALIDATING [?lch] = 'mix/combine' HYPOTHESIS")
    print("=" * 70)
    print("\nFrom Phase 20:")
    print("- [?lch]: 582 instances (1.6% of corpus)")
    print("- VERBAL classification (40.4% VERB suffix)")
    print("- Co-occurs with [?ch]-VERB and [?sh]-VERB")
    print("\nHypothesis: [?lch] = 'mix', 'combine', 'process'")
    print("(Distinct from [?ch] 'prepare' and [?sh] 'apply')\n")

    print("Loading translations...")
    translations = load_translations()
    print(f"Loaded {len(translations)} translations\n")

    # TEST 1: Recipe sequence position
    print("=" * 70)
    print("TEST 1: RECIPE SEQUENCE POSITION")
    print("=" * 70)
    print("If [?lch] = mix/combine:")
    print("Should appear BETWEEN [?ch] (prepare) and [?sh] (apply)")
    print("Pattern: [?ch]-VERB ... [?lch]-VERB ... [?sh]-VERB\n")

    sequences = test_recipe_sequence_position(translations)

    print(f"Result: {len(sequences)} sequences with [?ch] < [?lch] < [?sh] order")

    if sequences:
        print("\nSample sequences (first 3):")
        for i, seq in enumerate(sequences[:3], 1):
            print(f"\n  {i}. {seq['line']}")
            print(f"     Order positions: {seq['positions']}")
            print(f"     {seq['sentence'][:100]}...")

    if len(sequences) > 20:
        print(f"\n✓ STRONG EVIDENCE: {len(sequences)} sequences")
        print("  [?lch] appears in middle position (mixing step)")
    elif len(sequences) > 10:
        print(f"\n⚠ MODERATE EVIDENCE: {len(sequences)} sequences")
    else:
        print(f"\n? WEAK EVIDENCE: Only {len(sequences)} sequences")

    # TEST 2: Vessel/water co-occurrence
    print("\n" + "=" * 70)
    print("TEST 2: VESSEL/WATER CO-OCCURRENCE")
    print("=" * 70)
    print("If [?lch] = mix/combine:")
    print("Should appear with vessel/water (mixing requires container/liquid)\n")

    with_vessel, with_water, with_r = test_vessel_water_cooccurrence(translations)

    print(f"Results:")
    print(f"  With vessel: {len(with_vessel)}")
    print(f"  With water: {len(with_water)}")
    print(f"  With [?r] (liquid): {len(with_r)}")

    total_lch = 582  # Known from Phase 20
    vessel_rate = len(with_vessel) / total_lch * 100
    water_rate = len(with_water) / total_lch * 100
    r_rate = len(with_r) / total_lch * 100

    print(f"\nRates:")
    print(f"  Vessel: {vessel_rate:.1f}%")
    print(f"  Water: {water_rate:.1f}%")
    print(f"  [?r] liquid: {r_rate:.1f}%")

    container_total = vessel_rate + water_rate + r_rate

    if container_total > 40:
        print(
            f"\n✓ STRONG EVIDENCE: {container_total:.1f}% with container/liquid contexts"
        )
    elif container_total > 20:
        print(f"\n⚠ MODERATE EVIDENCE: {container_total:.1f}% with container/liquid")
    else:
        print(f"\n? WEAK EVIDENCE: Only {container_total:.1f}%")

    # Show sample
    if with_vessel:
        print(f"\nSample with vessel:")
        print(f"  {with_vessel[0][:100]}...")

    # TEST 3: Multiple ingredients
    print("\n" + "=" * 70)
    print("TEST 3: MULTIPLE INGREDIENT CONTEXTS")
    print("=" * 70)
    print("If [?lch] = mix/combine:")
    print("Should appear with ≥2 ingredients (can't mix one thing)\n")

    multiple = test_multiple_ingredients(translations)

    print(f"Result: {len(multiple)} [?lch] instances with ≥2 ingredients")

    multi_rate = len(multiple) / total_lch * 100
    print(f"Rate: {multi_rate:.1f}%")

    if multiple:
        print("\nTop 3 examples by ingredient count:")
        sorted_multi = sorted(
            multiple, key=lambda x: x["ingredient_count"], reverse=True
        )
        for i, ex in enumerate(sorted_multi[:3], 1):
            print(f"\n  {i}. {ex['line']} ({ex['ingredient_count']} ingredients)")
            print(f"     {ex['sentence'][:100]}...")

    if multi_rate > 50:
        print(f"\n✓ STRONG EVIDENCE: {multi_rate:.1f}% with multiple ingredients")
        print("  [?lch] involves combining things")
    elif multi_rate > 30:
        print(f"\n⚠ MODERATE EVIDENCE: {multi_rate:.1f}% with multiple ingredients")
    else:
        print(f"\n? WEAK EVIDENCE: Only {multi_rate:.1f}%")

    # TEST 4: Compare verb contexts
    print("\n" + "=" * 70)
    print("TEST 4: COMPARE WITH [?ch] AND [?sh]")
    print("=" * 70)
    print("If [?lch] is distinct verb:")
    print("Should have different co-occurrence patterns\n")

    contexts = compare_verb_contexts(translations)

    print("Top 10 words BEFORE each verb:")
    for verb in ["[?ch]", "[?lch]", "[?sh]"]:
        print(f"\n  {verb}:")
        for word, count in contexts[verb]["before"].most_common(10):
            print(f"    {word}: {count}×")

    print("\nTop 10 words AFTER each verb:")
    for verb in ["[?ch]", "[?lch]", "[?sh]"]:
        print(f"\n  {verb}:")
        for word, count in contexts[verb]["after"].most_common(10):
            print(f"    {word}: {count}×")

    # Calculate distinctiveness
    ch_before = set(w for w, c in contexts["[?ch]"]["before"].most_common(20))
    lch_before = set(w for w, c in contexts["[?lch]"]["before"].most_common(20))
    sh_before = set(w for w, c in contexts["[?sh]"]["before"].most_common(20))

    lch_ch_overlap = len(lch_before & ch_before) / 20 * 100
    lch_sh_overlap = len(lch_before & sh_before) / 20 * 100

    print(f"\n[?lch] context overlap:")
    print(f"  With [?ch]: {lch_ch_overlap:.1f}%")
    print(f"  With [?sh]: {lch_sh_overlap:.1f}%")

    if lch_ch_overlap < 70 and lch_sh_overlap < 70:
        print(f"\n✓ DISTINCT: [?lch] has different contexts from [?ch] and [?sh]")
    else:
        print(f"\n? SIMILAR: [?lch] overlaps heavily with other verbs")

    # FINAL VERDICT
    print("\n" + "=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)

    evidence = 0

    if len(sequences) > 20:
        evidence += 1
        print("✓ Test 1 (Sequence position): PASSED")
    elif len(sequences) > 10:
        print("⚠ Test 1 (Sequence position): MARGINAL")
    else:
        print("✗ Test 1 (Sequence position): FAILED")

    if container_total > 40:
        evidence += 1
        print("✓ Test 2 (Container/liquid): PASSED")
    elif container_total > 20:
        print("⚠ Test 2 (Container/liquid): MARGINAL")
    else:
        print("✗ Test 2 (Container/liquid): FAILED")

    if multi_rate > 50:
        evidence += 1
        print("✓ Test 3 (Multiple ingredients): PASSED")
    elif multi_rate > 30:
        print("⚠ Test 3 (Multiple ingredients): MARGINAL")
    else:
        print("✗ Test 3 (Multiple ingredients): FAILED")

    if lch_ch_overlap < 70 and lch_sh_overlap < 70:
        evidence += 1
        print("✓ Test 4 (Distinctiveness): PASSED")
    else:
        print("? Test 4 (Distinctiveness): MARGINAL")

    print(f"\nEvidence: {evidence}/4 tests passed")

    if evidence >= 3:
        print("\n" + "=" * 70)
        print("✓ HYPOTHESIS CONFIRMED: [?lch] = 'mix/combine/process'")
        print("=" * 70)
        print("Confidence: MODERATE")
        print("\nMeaning:")
        print("  [?lch] = 'mix', 'combine', 'process'")
        print("  Distinct from [?ch] 'prepare' and [?sh] 'apply'")
        print("  Appears in middle of recipe sequences")
        print("\nRecipe pattern:")
        print("  [?ch]-VERB (prepare) → [?lch]-VERB (mix) → [?sh]-VERB (apply)")
        print("\nMedieval parallel:")
        print("  Latin 'miscere' (to mix), 'commiscere' (to mix together)")
        print("\nImpact:")
        print("  Semantic confidence: MODERATE (already counted in recognition)")
    elif evidence >= 2:
        print("\n? HYPOTHESIS POSSIBLE: [?lch] likely mixing/processing verb")
        print(f"Evidence: {evidence}/4 tests")
    else:
        print("\n✗ HYPOTHESIS UNCERTAIN")
        print(f"Only {evidence}/4 tests passed")

    # Save results
    results = {
        "hypothesis": "[?lch] = mix/combine/process",
        "evidence_count": evidence,
        "tests": {
            "sequence_position": len(sequences),
            "vessel_rate": vessel_rate,
            "water_rate": water_rate,
            "liquid_rate": r_rate,
            "container_total": container_total,
            "multiple_ingredients_rate": multi_rate,
            "ch_overlap": lch_ch_overlap,
            "sh_overlap": lch_sh_overlap,
        },
        "sample_sequences": [
            {"line": seq["line"], "sentence": seq["sentence"]} for seq in sequences[:10]
        ],
    }

    print("\nSaving results to LCH_MIXING_VALIDATION.json...")
    with open("LCH_MIXING_VALIDATION.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\nDONE!")


if __name__ == "__main__":
    main()
