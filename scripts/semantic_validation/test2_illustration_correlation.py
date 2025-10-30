#!/usr/bin/env python3
"""
Semantic Validation Test 2: Illustration Correlation Analysis

HYPOTHESIS: If manuscript contains pharmaceutical recipes, botanical terms
should cluster in sections with plant illustrations (herbal section)

PREDICTION:
- Botanical folios (with plant drawings): HIGH frequency of [?al], botanical-term, oak-GEN, oat-GEN
- Astronomical folios (with star diagrams): LOW frequency of botanical terms
- Expected enrichment: 2-5× in botanical sections

METHODOLOGY:
- Define folio ranges for different sections
- Calculate term frequencies per section
- Compare enrichment ratios
- Statistical significance testing

SUCCESS CRITERIA:
- If hypothesis correct: 2-5× enrichment in botanical sections
- If wrong: No enrichment (<1.5×) or random distribution
"""

import json
import sys
from collections import defaultdict, Counter
import re


def load_data():
    with open(
        "COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)
    return data["translations"]


def extract_folio_section(folio_id):
    """
    Extract section number from folio ID.

    Voynich sections (approximate):
    - Herbal A: f1r-f66v (folios 1-66)
    - Herbal B: f87r-f102v (folios 87-102)
    - Astronomical: f67r-f73v (folios 67-73)
    - Biological: f75r-f84v (folios 75-84)
    - Pharmaceutical: f88r-f100v (mixed with Herbal B)
    - Stars: f103r-f116r (folios 103-116)
    - Text only: f103r onwards (varies)
    """

    # Extract folio number
    match = re.search(r"(\d+)", str(folio_id))
    if not match:
        return "unknown"

    folio_num = int(match.group(1))

    # Classify by section (simplified)
    if 1 <= folio_num <= 66:
        return "herbal_a"  # Main herbal section with plant illustrations
    elif 67 <= folio_num <= 73:
        return "astronomical"  # Circular astronomical diagrams
    elif 75 <= folio_num <= 84:
        return "biological"  # Biological/cosmological diagrams
    elif 87 <= folio_num <= 102:
        return "herbal_b"  # Pharmaceutical jars and plant illustrations
    elif 103 <= folio_num <= 116:
        return "stars"  # Star diagrams
    else:
        return "text_only"  # Mainly text


def count_terms_by_section(translations):
    """Count occurrence of key pharmaceutical terms by manuscript section."""

    sections = defaultdict(
        lambda: {
            "sentence_count": 0,
            "word_count": 0,
            "al_count": 0,
            "botanical_count": 0,
            "oak_gen_count": 0,
            "oat_gen_count": 0,
            "vessel_count": 0,
            "water_count": 0,
            "ch_verb_count": 0,
            "sh_verb_count": 0,
            "pharmaceutical_substance_count": 0,
        }
    )

    for trans in translations:
        folio = trans.get("folio", "unknown")
        section = extract_folio_section(folio)
        sentence = trans["final_translation"]
        words = sentence.split()

        sections[section]["sentence_count"] += 1
        sections[section]["word_count"] += len(words)

        # Count pharmaceutical terms
        if "[?al]" in sentence or "-al" in sentence:
            sections[section]["al_count"] += sentence.count("al")

        if "botanical-term" in sentence:
            sections[section]["botanical_count"] += sentence.count("botanical-term")

        if "oak-GEN" in sentence:
            sections[section]["oak_gen_count"] += 1

        if "oat-GEN" in sentence:
            sections[section]["oat_gen_count"] += 1

        if "vessel" in sentence.lower():
            sections[section]["vessel_count"] += 1

        if "water" in sentence.lower():
            sections[section]["water_count"] += 1

        if "[?ch]" in sentence and "VERB" in sentence:
            sections[section]["ch_verb_count"] += 1

        if "[?sh]" in sentence and "VERB" in sentence:
            sections[section]["sh_verb_count"] += 1

        if "pharmaceutical-substance" in sentence:
            sections[section]["pharmaceutical_substance_count"] += 1

    return dict(sections)


def calculate_enrichment(sections):
    """Calculate enrichment ratios comparing botanical vs non-botanical sections."""

    # Combine herbal sections
    herbal_combined = {
        "sentence_count": sections["herbal_a"]["sentence_count"]
        + sections["herbal_b"]["sentence_count"],
        "al_count": sections["herbal_a"]["al_count"] + sections["herbal_b"]["al_count"],
        "botanical_count": sections["herbal_a"]["botanical_count"]
        + sections["herbal_b"]["botanical_count"],
        "oak_gen_count": sections["herbal_a"]["oak_gen_count"]
        + sections["herbal_b"]["oak_gen_count"],
        "oat_gen_count": sections["herbal_a"]["oat_gen_count"]
        + sections["herbal_b"]["oat_gen_count"],
        "vessel_count": sections["herbal_a"]["vessel_count"]
        + sections["herbal_b"]["vessel_count"],
        "water_count": sections["herbal_a"]["water_count"]
        + sections["herbal_b"]["water_count"],
    }

    # Combine non-botanical sections
    non_botanical = {
        "sentence_count": sections["astronomical"]["sentence_count"]
        + sections["biological"]["sentence_count"]
        + sections["stars"]["sentence_count"],
        "al_count": sections["astronomical"]["al_count"]
        + sections["biological"]["al_count"]
        + sections["stars"]["al_count"],
        "botanical_count": sections["astronomical"]["botanical_count"]
        + sections["biological"]["botanical_count"]
        + sections["stars"]["botanical_count"],
        "oak_gen_count": sections["astronomical"]["oak_gen_count"]
        + sections["biological"]["oak_gen_count"]
        + sections["stars"]["oak_gen_count"],
        "oat_gen_count": sections["astronomical"]["oat_gen_count"]
        + sections["biological"]["oat_gen_count"]
        + sections["stars"]["oat_gen_count"],
        "vessel_count": sections["astronomical"]["vessel_count"]
        + sections["biological"]["vessel_count"]
        + sections["stars"]["vessel_count"],
        "water_count": sections["astronomical"]["water_count"]
        + sections["biological"]["water_count"]
        + sections["stars"]["water_count"],
    }

    enrichment = {}

    for term in [
        "al_count",
        "botanical_count",
        "oak_gen_count",
        "oat_gen_count",
        "vessel_count",
        "water_count",
    ]:
        herbal_freq = (
            herbal_combined[term] / herbal_combined["sentence_count"]
            if herbal_combined["sentence_count"] > 0
            else 0
        )
        non_botanical_freq = (
            non_botanical[term] / non_botanical["sentence_count"]
            if non_botanical["sentence_count"] > 0
            else 0
        )

        enrichment[term] = {
            "herbal_freq": herbal_freq,
            "non_botanical_freq": non_botanical_freq,
            "enrichment_ratio": herbal_freq / non_botanical_freq
            if non_botanical_freq > 0
            else 0,
        }

    return enrichment, herbal_combined, non_botanical


def main():
    print("=" * 80)
    print("SEMANTIC VALIDATION TEST 2: ILLUSTRATION CORRELATION")
    print("=" * 80)
    print()
    print("HYPOTHESIS: Botanical terms cluster in illustrated herbal sections")
    print()
    print("PREDICTION:")
    print("  - Herbal sections (plant illustrations): HIGH botanical term frequency")
    print("  - Astronomical sections (star diagrams): LOW botanical term frequency")
    print("  - Expected enrichment: 2-5× in herbal sections")
    print()

    # Load data
    print("Loading translation data...")
    translations = load_data()
    print(f"Loaded {len(translations)} sentences")
    print()

    # Count terms by section
    print("=" * 80)
    print("ANALYZING TERM DISTRIBUTION BY MANUSCRIPT SECTION...")
    print("=" * 80)
    print()

    sections = count_terms_by_section(translations)

    # Display results by section
    print("TERM FREQUENCIES BY SECTION:")
    print()

    for section_name in [
        "herbal_a",
        "herbal_b",
        "astronomical",
        "biological",
        "stars",
        "text_only",
    ]:
        if section_name in sections and sections[section_name]["sentence_count"] > 0:
            data = sections[section_name]
            print(f"SECTION: {section_name.upper()}")
            print(f"  Sentences: {data['sentence_count']}")
            print(
                f"  [?al] occurrences: {data['al_count']} ({data['al_count'] / data['sentence_count']:.2f} per sentence)"
            )
            print(
                f"  botanical-term: {data['botanical_count']} ({data['botanical_count'] / data['sentence_count']:.2f} per sentence)"
            )
            print(
                f"  oak-GEN: {data['oak_gen_count']} ({data['oak_gen_count'] / data['sentence_count']:.2f} per sentence)"
            )
            print(
                f"  oat-GEN: {data['oat_gen_count']} ({data['oat_gen_count'] / data['sentence_count']:.2f} per sentence)"
            )
            print(
                f"  vessel: {data['vessel_count']} ({data['vessel_count'] / data['sentence_count']:.2f} per sentence)"
            )
            print(
                f"  water: {data['water_count']} ({data['water_count'] / data['sentence_count']:.2f} per sentence)"
            )
            print()

    # Calculate enrichment
    print("=" * 80)
    print("ENRICHMENT ANALYSIS")
    print("=" * 80)
    print()

    enrichment, herbal, non_botanical = calculate_enrichment(sections)

    print(f"HERBAL SECTIONS (combined): {herbal['sentence_count']} sentences")
    print(
        f"NON-BOTANICAL SECTIONS (combined): {non_botanical['sentence_count']} sentences"
    )
    print()

    print("ENRICHMENT RATIOS (Herbal vs Non-Botanical):")
    print()

    for term, data in enrichment.items():
        term_name = term.replace("_count", "").replace("_", "-")
        print(f"{term_name}:")
        print(f"  Herbal frequency: {data['herbal_freq']:.3f} per sentence")
        print(
            f"  Non-botanical frequency: {data['non_botanical_freq']:.3f} per sentence"
        )
        print(f"  Enrichment ratio: {data['enrichment_ratio']:.2f}×")
        print()

    # Interpretation
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print()

    # Check if enrichment meets predictions
    al_enrichment = enrichment["al_count"]["enrichment_ratio"]
    botanical_enrichment = enrichment["botanical_count"]["enrichment_ratio"]
    oak_enrichment = enrichment["oak_gen_count"]["enrichment_ratio"]

    avg_enrichment = (al_enrichment + botanical_enrichment + oak_enrichment) / 3

    if avg_enrichment >= 2.0:
        print("✓ STRONG SUPPORT for illustration correlation hypothesis")
        print(f"  - Average enrichment: {avg_enrichment:.2f}×")
        print("  - Botanical terms ARE significantly enriched in herbal sections")
        print("  - Manuscript content MATCHES illustrations")
    elif avg_enrichment >= 1.5:
        print("? MODERATE SUPPORT for illustration correlation hypothesis")
        print(f"  - Average enrichment: {avg_enrichment:.2f}×")
        print("  - Some enrichment observed")
        print("  - Further analysis needed")
    else:
        print("✗ NO SUPPORT for illustration correlation hypothesis")
        print(f"  - Average enrichment: {avg_enrichment:.2f}×")
        print("  - No significant clustering in herbal sections")
        print("  - Content may not match illustrations")

    print()

    # Most enriched section
    print("MOST ENRICHED TERMS IN HERBAL SECTIONS:")
    print()

    sorted_enrichment = sorted(
        enrichment.items(), key=lambda x: x[1]["enrichment_ratio"], reverse=True
    )
    for term, data in sorted_enrichment[:5]:
        if data["enrichment_ratio"] > 1:
            term_name = term.replace("_count", "").replace("_", "-")
            print(f"  {term_name}: {data['enrichment_ratio']:.2f}× enrichment")

    print()

    # Save results
    output = {
        "sections": sections,
        "enrichment": {
            k: {
                kk: float(vv) if isinstance(vv, (int, float)) else vv
                for kk, vv in v.items()
            }
            for k, v in enrichment.items()
        },
        "summary": {
            "herbal_sentences": herbal["sentence_count"],
            "non_botanical_sentences": non_botanical["sentence_count"],
            "avg_enrichment": float(avg_enrichment),
        },
    }

    output_file = "SEMANTIC_TEST2_ILLUSTRATION_CORRELATION.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {output_file}")
    print()

    # Next steps
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()

    if avg_enrichment >= 1.5:
        print("RECOMMENDATION: Hypothesis SUPPORTED - proceed to Test 3")
        print()
        print("Test 3: Medieval recipe structural comparison")
        print("  - Compare Voynich patterns with known pharmaceutical texts")
        print("  - Validate recipe structure hypothesis")
    else:
        print("RECOMMENDATION: Reconsider content interpretation")
        print()
        print("If botanical terms don't cluster in herbal sections:")
        print("  - Content may be abstract/symbolic rather than literal")
        print("  - Illustrations may be decorative rather than informative")
        print("  - Alternative text genres should be explored")

    print()


if __name__ == "__main__":
    main()
