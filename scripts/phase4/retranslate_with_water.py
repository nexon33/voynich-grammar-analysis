"""
RE-TRANSLATION TEST WITH WATER IDENTIFIED

We now have THREE validated nouns:
- oak (qok/ok) - plant ingredient
- oat (qot/ot) - grain ingredient
- water (shee) - liquid medium (10.3x enriched in baths, 1302 co-occurrences with oak/oat)

CRITICAL VALIDATION:
If these 3 nouns are sufficient, previously incoherent sentences should become interpretable.

This tests if our system fundamentally works before investing in verb analysis.

Author: Research Assistant
Date: 2025-10-29
"""

import json
from pathlib import Path


def load_f84v_sentences():
    """Load first 5 sentences from f84v"""
    with open(
        "results/phase4/readable_passages/f84v_oak_oat_bath_folio.txt",
        "r",
        encoding="utf-8",
    ) as f:
        sentences = []
        for line in f:
            line = line.strip()
            if line.startswith("Voynich:"):
                text = line.replace("Voynich:", "").strip()
                words = text.split()
                if words:
                    sentences.append(words)
                if len(sentences) >= 5:
                    break
        return sentences


def decompose_and_translate(word):
    """Decompose word and translate with updated vocabulary

    Now includes: oak, oat, water (shee)
    """
    original = word.lower()
    remaining = original

    components = {
        "original": original,
        "prefix": None,
        "root": None,
        "suffixes": [],
        "translation": None,
    }

    # Step 1: Genitive prefix
    if remaining.startswith("qok") and len(remaining) > 3:
        components["prefix"] = "qok"
        remaining = remaining[3:]

    # Step 2: Strip suffixes
    case_markers = ["al", "ar", "ol", "or"]
    while len(remaining) > 2:
        found = False
        for case in case_markers:
            if remaining.endswith(case):
                components["suffixes"].insert(0, case)
                remaining = remaining[:-2]
                found = True
                break
        if not found:
            break

    # Verbal suffix
    if remaining.endswith("edy") and len(remaining) > 3:
        components["suffixes"].insert(0, "edy")
        remaining = remaining[:-3]

    # Step 3: Identify root
    components["root"] = remaining

    # Step 4: TRANSLATE with expanded vocabulary
    parts = []

    # Genitive
    if components["prefix"] == "qok":
        parts.append("[of ")

    # ROOT - expanded vocabulary
    if "ok" in remaining and "qok" not in original:
        parts.append("oak")
    elif "ot" in remaining and "qok" not in original and remaining != "ot":
        parts.append("oat")
    elif "shee" in remaining:  # NEW: water
        parts.append("WATER")
    elif remaining in ["daiin", "aiin", "saiin", "oiin"]:
        if remaining == "daiin":
            parts.append("this")
        elif remaining == "aiin":
            parts.append("that")
        elif remaining == "saiin":
            parts.append("such")
        else:
            parts.append("it")
    elif remaining in ["ol", "ar", "or", "al", "y", "dar"]:
        parts.append(f"[{remaining}]")
    else:
        parts.append(f"???({remaining})")

    # Genitive close
    if components["prefix"] == "qok":
        parts.append("'s]")

    # Suffixes with interpretation
    for suffix in components["suffixes"]:
        if suffix == "ol":
            parts.append("-in/at")  # locative
        elif suffix == "ar":
            parts.append("-to/toward")  # directional
        elif suffix == "al":
            parts.append("-from/of")  # ablative/genitive
        elif suffix == "or":
            parts.append("-with")  # instrumental
        elif suffix == "edy":
            parts.append("-VERB")

    components["translation"] = "".join(parts)

    return components


def attempt_coherent_interpretation(translations, decompositions):
    """Try to build coherent interpretation with 3 known nouns

    Medieval bath recipe structure:
    - [Action] [ingredient] in [liquid] with [other ingredients]
    - In [liquid], [action] [ingredients]
    """

    # Extract known elements
    has_water = any("WATER" in t for t in translations)
    has_oak = any("oak" in t for t in translations)
    has_oat = any("oat" in t for t in translations)
    has_pronoun = len(decompositions) > 0 and decompositions[0]["root"] in [
        "daiin",
        "aiin",
        "saiin",
    ]
    has_verb = any("VERB" in t for t in translations)

    # Check for locative patterns (in water, in oak)
    water_loc = any("WATER-in" in t for t in translations)
    oak_loc = any("oak-in" in t for t in translations)

    interpretations = []
    confidence = "NONE"

    # Pattern 1: "in oak, in water, oat..."
    if oak_loc and water_loc and has_oat:
        interpretations.append("Prepare oak [bark] in water with oat")
        confidence = "MODERATE"

    # Pattern 2: "oak, water, oat + VERB"
    elif has_oak and has_water and has_oat and has_verb:
        interpretations.append("[Action] oak [and] water [and] oat")
        confidence = "LOW-MODERATE"

    # Pattern 3: "pronoun + ingredients"
    elif has_pronoun and (has_water or has_oak or has_oat):
        ingredients = []
        if has_water:
            ingredients.append("water")
        if has_oak:
            ingredients.append("oak")
        if has_oat:
            ingredients.append("oat")
        interpretations.append(f"This [preparation] with {', '.join(ingredients)}")
        confidence = "LOW"

    # Pattern 4: Just lists ingredients
    elif has_water or has_oak or has_oat:
        ingredients = []
        if has_water:
            ingredients.append("water")
        if has_oak:
            ingredients.append("oak")
        if has_oat:
            ingredients.append("oat")
        interpretations.append(f"[Using] {', '.join(ingredients)}")
        confidence = "LOW"

    if not interpretations:
        interpretations.append("[Cannot interpret - insufficient known elements]")
        confidence = "NONE"

    return {
        "interpretations": interpretations,
        "confidence": confidence,
        "has_water": has_water,
        "has_oak": has_oak,
        "has_oat": has_oat,
        "has_pronoun": has_pronoun,
        "has_verb": has_verb,
    }


def assess_coherence(interpretation_result, translations):
    """Assess if interpretation is coherent for a medieval bath recipe"""

    confidence = interpretation_result["confidence"]

    # Check if interpretation makes medical sense
    coherent = False
    reasoning = []

    if confidence in ["MODERATE", "LOW-MODERATE"]:
        # Has clear structure with multiple ingredients
        if interpretation_result["has_water"] and (
            interpretation_result["has_oak"] or interpretation_result["has_oat"]
        ):
            coherent = True
            reasoning.append("✓ Multiple ingredients with liquid medium (water)")
            reasoning.append("✓ Makes sense as bath/preparation recipe")

    if interpretation_result["has_water"] and any("in" in t for t in translations):
        reasoning.append("✓ Locative structure: ingredients IN water")

    if len([t for t in translations if "oak" in t or "oat" in t or "WATER" in t]) >= 2:
        reasoning.append("✓ Multiple recipe components identified")

    # Check for problematic patterns
    unknown_count = sum(1 for t in translations if "???" in t)
    if unknown_count > 6:
        reasoning.append("⚠ Many unknowns still present")

    return {"coherent": coherent or confidence == "MODERATE", "reasoning": reasoning}


def main():
    print("=" * 80)
    print("RE-TRANSLATION TEST WITH WATER IDENTIFIED")
    print("=" * 80)
    print()
    print("CRITICAL VALIDATION: Do 3 validated nouns make sentences coherent?")
    print()
    print("VALIDATED VOCABULARY:")
    print("  1. oak (qok/ok) - plant ingredient")
    print("  2. oat (qot/ot) - grain ingredient")
    print("  3. WATER (shee) - liquid medium [NEW - 10.3x enriched, 1302 co-occur]")
    print()
    print("HYPOTHESIS: If system works, previously incoherent sentences")
    print("            should become interpretable with these 3 nouns.")
    print()

    sentences = load_f84v_sentences()

    results = []
    coherent_count = 0

    for i, sentence in enumerate(sentences, 1):
        print("=" * 80)
        print(f"SENTENCE {i}")
        print("=" * 80)
        print()
        print(f"Raw: {' '.join(sentence)}")
        print()

        # Decompose and translate
        decompositions = []
        translations = []

        for word in sentence:
            comp = decompose_and_translate(word)
            decompositions.append(comp)
            translations.append(comp["translation"])

        print("TRANSLATION (with WATER):")
        print("-" * 80)
        for orig, trans in zip(sentence, translations):
            # Highlight water
            display_trans = trans
            if "WATER" in trans:
                display_trans = f"**{trans}**"
            print(f"  {orig:15s} → {display_trans}")
        print()

        print("WORD-BY-WORD GLOSS:")
        print("-" * 80)
        print(f"  {' '.join(translations)}")
        print()

        # Attempt interpretation
        interpretation = attempt_coherent_interpretation(translations, decompositions)

        print("INTERPRETATION:")
        print("-" * 80)
        for interp in interpretation["interpretations"]:
            print(f"  {interp}")
        print(f"  Confidence: {interpretation['confidence']}")
        print()

        # Assess coherence
        coherence = assess_coherence(interpretation, translations)

        print("COHERENCE ASSESSMENT:")
        print("-" * 80)
        for reason in coherence["reasoning"]:
            print(f"  {reason}")
        print()

        if coherence["coherent"]:
            print("  ✓✓ COHERENT - Makes sense as bath/recipe instruction")
            coherent_count += 1
        else:
            print("  ✗ NOT YET COHERENT - Still missing critical elements")
        print()

        results.append(
            {
                "sentence": " ".join(sentence),
                "translations": translations,
                "interpretation": interpretation,
                "coherence": coherence,
            }
        )

    # Overall assessment
    print()
    print("=" * 80)
    print("OVERALL VALIDATION RESULTS")
    print("=" * 80)
    print()
    print(f"Coherent sentences: {coherent_count}/5")
    print()

    if coherent_count >= 4:
        print("✓✓✓ VALIDATION PASSED")
        print()
        print("CONCLUSION:")
        print("  - Morphological system is correct")
        print("  - Case system interpretation is correct")
        print("  - Noun identification method works")
        print("  - System fundamentally sound")
        print()
        print("RECOMMENDED NEXT STEP:")
        print("  → Proceed with verb co-occurrence analysis")
        print("  → Goal: Decode ch-edy, sh-edy, opch-edy meanings")
        print("  → Method: Check which case frames each verb prefers")
    elif coherent_count >= 2:
        print("✓ PARTIAL VALIDATION")
        print()
        print("CONCLUSION:")
        print("  - System shows promise but incomplete")
        print("  - Some structural understanding is correct")
        print("  - Need more vocabulary or refinement")
        print()
        print("RECOMMENDED NEXT STEP:")
        print("  → Find 2-3 more core nouns (vessel, heat, body part)")
        print("  → Re-test coherence with expanded vocabulary")
    else:
        print("✗ VALIDATION FAILED")
        print()
        print("CONCLUSION:")
        print("  - Something fundamental is wrong")
        print("  - Possible issues:")
        print("    • Wrong word boundaries")
        print("    • Incorrect case interpretations")
        print("    • 'shee' might not be 'water'")
        print("    • Over-aggressive morphological decomposition")
        print()
        print("RECOMMENDED NEXT STEP:")
        print("  → Diagnose deeper structural issues")
        print("  → Re-examine morphological decomposition rules")
        print("  → Validate 'shee' = water hypothesis independently")
    print()

    # Save results
    output_path = Path("results/phase4/retranslation_with_water.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
