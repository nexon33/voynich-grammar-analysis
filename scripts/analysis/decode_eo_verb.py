#!/usr/bin/env python3
"""
Decode [?eo] - The Strong Verbal Candidate

OBSERVATION: 63.9% VERB suffix rate (HIGHEST of all remaining unknowns)

HYPOTHESIS: [?eo] is a core pharmaceutical action verb
  Candidates: grind/pound, boil/cook, strain/filter

Medieval recipe verbs (from previous phases):
  - [?ch]: prepare/make ✓
  - [?sh]: apply/heat ✓
  - [?lch]: [unknown action] ✓
  - [?eo]: ??? ← THIS ONE

Tests:
1. Vessel co-occurrence (boil/cook needs vessel)
2. Water co-occurrence (boil/strain uses water)
3. Instrumental marking (grind/pound uses tool)
4. Position in recipe sequence
5. Compare with known verbs
"""

import json
import re
from collections import Counter


def load_translations():
    with open(
        "COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)
        return data["translations"]


def test_vessel_context(translations):
    """Test if [?eo] appears with vessel"""

    eo_with_vessel = 0
    eo_total = 0

    for trans in translations:
        text = trans["final_translation"]

        has_eo = "[?eo]" in text
        has_vessel = "vessel" in text.lower()

        if has_eo:
            eo_total += 1
            if has_vessel:
                eo_with_vessel += 1

    rate = eo_with_vessel / eo_total if eo_total > 0 else 0

    # Compare with [?sh] (apply/heat) which uses vessel
    sh_with_vessel = 0
    sh_total = 0
    for trans in translations:
        text = trans["final_translation"]
        if "[?sh]" in text:
            sh_total += 1
            if "vessel" in text.lower():
                sh_with_vessel += 1

    sh_rate = sh_with_vessel / sh_total if sh_total > 0 else 0
    enrichment = rate / sh_rate if sh_rate > 0 else 0

    return {
        "eo_with_vessel": eo_with_vessel,
        "eo_total": eo_total,
        "rate": rate,
        "sh_rate": sh_rate,
        "enrichment": enrichment,
        "interpretation": "boil/cook" if rate > 0.15 else "not vessel-based",
    }


def test_water_context(translations):
    """Test if [?eo] appears with water"""

    eo_with_water = 0
    eo_total = 0

    for trans in translations:
        text = trans["final_translation"]

        has_eo = "[?eo]" in text
        has_water = "water" in text.lower()

        if has_eo:
            eo_total += 1
            if has_water:
                eo_with_water += 1

    rate = eo_with_water / eo_total if eo_total > 0 else 0

    # Baseline water rate
    total = len(translations)
    water_baseline = (
        sum(1 for t in translations if "water" in t["final_translation"].lower())
        / total
    )
    enrichment = rate / water_baseline if water_baseline > 0 else 0

    return {
        "eo_with_water": eo_with_water,
        "eo_total": eo_total,
        "rate": rate,
        "baseline": water_baseline,
        "enrichment": enrichment,
        "interpretation": "boil/strain" if enrichment > 1.5 else "not water-specific",
    }


def test_instrumental_marking(translations):
    """Test if [?eo] takes INST suffix (tool-using action)"""

    eo_inst = 0
    eo_total = 0

    for trans in translations:
        text = trans["final_translation"]
        words = text.split()

        for word in words:
            if "[?eo]" in word:
                eo_total += 1
                if "-INST" in word or "-or" in word:
                    eo_inst += 1

    rate = eo_inst / eo_total if eo_total > 0 else 0

    # Compare with [?ch] (prepare) - should use instruments
    ch_inst = 0
    ch_total = 0
    for trans in translations:
        text = trans["final_translation"]
        words = text.split()
        for word in words:
            if "[?ch]" in word and "botanical-term" not in word:
                ch_total += 1
                if "-INST" in word or "-or" in word:
                    ch_inst += 1

    ch_rate = ch_inst / ch_total if ch_total > 0 else 0

    return {
        "eo_inst": eo_inst,
        "eo_total": eo_total,
        "rate": rate,
        "ch_rate": ch_rate,
        "interpretation": "grind/pound" if rate > 0.25 else "not tool-based",
    }


def test_sequence_position(translations):
    """Test where [?eo] appears in recipe sequences"""

    after_ch = 0  # [?ch]-VERB ... [?eo]-VERB
    after_sh = 0  # [?sh]-VERB ... [?eo]-VERB
    after_lch = 0  # [?lch]-VERB ... [?eo]-VERB

    for trans in translations:
        text = trans["final_translation"]

        # Simple sequential search
        words = text.split()

        for i, word in enumerate(words):
            if "[?eo]" in word and "-VERB" in word:
                # Look back up to 5 words
                for j in range(max(0, i - 5), i):
                    prev_word = words[j]
                    if "[?ch]" in prev_word and "-VERB" in prev_word:
                        after_ch += 1
                        break
                    elif "[?sh]" in prev_word and "-VERB" in prev_word:
                        after_sh += 1
                        break
                    elif "[?lch]" in prev_word and "-VERB" in prev_word:
                        after_lch += 1
                        break

    total = after_ch + after_sh + after_lch

    return {
        "after_ch": after_ch,
        "after_sh": after_sh,
        "after_lch": after_lch,
        "total": total,
        "interpretation": "Recipe sequences found"
        if total > 10
        else "Limited sequence data",
    }


def compare_with_known_verbs(translations):
    """Compare [?eo] distribution with [?ch], [?sh], [?lch]"""

    verb_contexts = {
        "?ch": Counter(),
        "?sh": Counter(),
        "?lch": Counter(),
        "?eo": Counter(),
    }

    context_words = ["vessel", "water", "botanical-term", "oak", "oat", "THIS/THAT"]

    for trans in translations:
        text = trans["final_translation"]

        for verb in verb_contexts.keys():
            if f"[{verb}]" in text:
                for ctx in context_words:
                    if ctx in text:
                        verb_contexts[verb][ctx] += 1

    return verb_contexts


def main():
    print("=" * 70)
    print("DECODE [?eo] - VERBAL ROOT ANALYSIS")
    print("=" * 70)
    print()
    print("OBSERVATION: 63.9% VERB suffix rate (STRONGEST verbal candidate)")
    print()
    print("HYPOTHESIS: [?eo] is a core pharmaceutical action verb")
    print("  Candidates: grind/pound, boil/cook, strain/filter")
    print()
    print("=" * 70)

    translations = load_translations()

    # Test 1: Vessel context
    print("\nTest 1: Vessel co-occurrence (boil/cook indicator)")
    print("-" * 70)
    result1 = test_vessel_context(translations)
    print(f"[?eo] with vessel: {result1['eo_with_vessel']}/{result1['eo_total']}")
    print(f"[?eo] vessel rate: {result1['rate']:.1%}")
    print(f"[?sh] vessel rate (comparison): {result1['sh_rate']:.1%}")
    print(f"Enrichment: {result1['enrichment']:.2f}×")
    print(f"Interpretation: {result1['interpretation']}")

    # Test 2: Water context
    print("\n\nTest 2: Water co-occurrence (boil/strain indicator)")
    print("-" * 70)
    result2 = test_water_context(translations)
    print(f"[?eo] with water: {result2['eo_with_water']}/{result2['eo_total']}")
    print(f"[?eo] water rate: {result2['rate']:.1%}")
    print(f"Baseline water rate: {result2['baseline']:.1%}")
    print(f"Enrichment: {result2['enrichment']:.2f}×")
    print(f"Interpretation: {result2['interpretation']}")

    # Test 3: Instrumental marking
    print("\n\nTest 3: Instrumental suffix (grind/pound indicator)")
    print("-" * 70)
    result3 = test_instrumental_marking(translations)
    print(f"[?eo]-INST: {result3['eo_inst']}/{result3['eo_total']}")
    print(f"[?eo] INST rate: {result3['rate']:.1%}")
    print(f"[?ch] INST rate (comparison): {result3['ch_rate']:.1%}")
    print(f"Interpretation: {result3['interpretation']}")

    # Test 4: Sequence position
    print("\n\nTest 4: Position in recipe sequences")
    print("-" * 70)
    result4 = test_sequence_position(translations)
    print(f"[?eo] after [?ch] (prepare): {result4['after_ch']}×")
    print(f"[?eo] after [?sh] (apply/heat): {result4['after_sh']}×")
    print(f"[?eo] after [?lch]: {result4['after_lch']}×")
    print(f"Total sequences: {result4['total']}")

    if result4["after_ch"] > result4["after_sh"]:
        print("\nInterpretation: [?eo] comes AFTER prepare")
        print("  → Likely a processing action (grind, crush, pound)")
    elif result4["after_sh"] > result4["after_ch"]:
        print("\nInterpretation: [?eo] comes AFTER apply/heat")
        print("  → Likely a finalizing action (strain, filter, pour)")

    # Test 5: Context comparison
    print("\n\nTest 5: Context comparison with known verbs")
    print("-" * 70)
    verb_contexts = compare_with_known_verbs(translations)

    print("\nContext co-occurrences:")
    print(f"{'Context':<15} {'[?ch]':>8} {'[?sh]':>8} {'[?lch]':>8} {'[?eo]':>8}")
    print("-" * 60)

    contexts = ["vessel", "water", "botanical-term", "oak", "oat"]
    for ctx in contexts:
        print(
            f"{ctx:<15} {verb_contexts['?ch'].get(ctx, 0):>8} "
            f"{verb_contexts['?sh'].get(ctx, 0):>8} "
            f"{verb_contexts['?lch'].get(ctx, 0):>8} "
            f"{verb_contexts['?eo'].get(ctx, 0):>8}"
        )

    # Final classification
    print("\n" + "=" * 70)
    print("FINAL CLASSIFICATION")
    print("=" * 70)
    print()

    # Decision logic
    vessel_score = 1 if result1["rate"] > 0.15 else 0
    water_score = 1 if result2["enrichment"] > 1.5 else 0
    inst_score = 1 if result3["rate"] > 0.25 else 0

    total_score = vessel_score + water_score + inst_score

    if water_score and vessel_score:
        classification = "BOIL/COOK"
        confidence = "HIGH" if total_score >= 2 else "MODERATE"
        print(f"[?eo] = {classification}")
        print(f"Confidence: {confidence}")
        print()
        print("Evidence:")
        print("  - High vessel co-occurrence (heating requires vessel)")
        print("  - High water enrichment (boiling uses water)")
        print()
        print("PARALLEL: Latin coquere 'to cook/boil'")
        print("         Medieval recipes: 'coque in aqua' (boil in water)")

    elif inst_score:
        classification = "GRIND/POUND"
        confidence = "MODERATE"
        print(f"[?eo] = {classification}")
        print(f"Confidence: {confidence}")
        print()
        print("Evidence:")
        print("  - Takes instrumental marking (tool-using action)")
        print()
        print("PARALLEL: Latin terere 'to grind'")
        print("         Medieval recipes: 'tere in mortario' (grind in mortar)")

    else:
        classification = "PROCESS/ACT (unspecified)"
        confidence = "LOW"
        print(f"[?eo] = {classification}")
        print(f"Confidence: {confidence}")
        print()
        print("More investigation needed")

    print()
    print("RECOGNITION IMPACT:")
    print(f"  [?eo] instances: 170 (~0.46% of corpus)")
    print(f"  Current recognition: 88.2%")
    print(f"  With [?eo]: 88.2% + 0.5% = 88.7%")
    print()

    # Save results
    results = {
        "classification": classification,
        "confidence": confidence,
        "tests": {
            "vessel": result1,
            "water": result2,
            "instrumental": result3,
            "sequence": result4,
        },
    }

    with open("EO_VERB_ANALYSIS.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("Results saved to EO_VERB_ANALYSIS.json")
    print()


if __name__ == "__main__":
    main()
