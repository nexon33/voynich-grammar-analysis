#!/usr/bin/env python3
"""
Semantic Validation Test 2: Illustration Correlation Analysis (CORRECTED)

Uses proper folio mapping from word indices to compare botanical term frequency
across manuscript sections.
"""

import json
import re
from collections import defaultdict, Counter


def load_data():
    with open(
        "COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)
    return data["translations"]


def load_folio_mapping():
    with open(
        "results/phase3/proper_section_to_folio_mapping.json", "r", encoding="utf-8"
    ) as f:
        return json.load(f)


def get_word_index_from_line(line_id):
    """Extract word index from line ID (e.g., 'line1234' -> 1234)"""
    match = re.search(r"line(\d+)", str(line_id))
    if match:
        return int(match.group(1))
    return None


def get_folio_from_word_index(word_idx, folio_mapping):
    """Find which folio a given word index belongs to"""
    for section in folio_mapping:
        word_range = section["word_range"].split("-")
        start_word = int(word_range[0])
        end_word = int(word_range[1])

        if start_word <= word_idx < end_word:
            return section["primary_folio"], section["folios"]
    return None, []


def classify_folio_section(folio):
    """
    Classify folio into manuscript sections based on content.

    Known Voynich sections:
    - Herbal A: f1r-f66v (botanical drawings of plants)
    - Astronomical: f67r-f73v (circular astronomical diagrams)
    - Biological: f75r-f84v (biological/cosmological diagrams)
    - Pharmaceutical: f87r-f102v (jars and plants)
    - Stars: f103r-f116r (star diagrams and dense text)
    """
    if not folio:
        return "unknown"

    # Extract folio number
    match = re.search(r"f(\d+)", folio)
    if not match:
        return "unknown"

    num = int(match.group(1))

    if 1 <= num <= 66:
        return "herbal"
    elif 67 <= num <= 73:
        return "astronomical"
    elif 75 <= num <= 84:
        return "biological"
    elif 87 <= num <= 102:
        return "pharmaceutical"
    elif 103 <= num <= 116:
        return "stars"
    else:
        return "other"


def count_terms_by_section(translations, folio_mapping):
    """Count pharmaceutical terms by manuscript section using proper folio mapping"""

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
            "pharmaceutical_substance_count": 0,
        }
    )

    for idx, trans in enumerate(translations):
        folio_id = trans.get("folio", "unknown")

        # Get word index from folio_id
        word_idx = get_word_index_from_line(folio_id)
        if word_idx is None:
            word_idx = idx  # Fallback to sentence index

        # Map to actual folio
        primary_folio, _ = get_folio_from_word_index(word_idx, folio_mapping)

        # Classify section
        section = classify_folio_section(primary_folio)

        sentence = trans["final_translation"]
        words = sentence.split()

        sections[section]["sentence_count"] += 1
        sections[section]["word_count"] += len(words)

        # Count pharmaceutical terms
        if "[?al]" in sentence or "al-" in sentence or "-al " in sentence:
            sections[section]["al_count"] += 1

        if "botanical-term" in sentence:
            sections[section]["botanical_count"] += 1

        if "oak-GEN" in sentence:
            sections[section]["oak_gen_count"] += 1

        if "oat-GEN" in sentence:
            sections[section]["oat_gen_count"] += 1

        if "vessel" in sentence.lower():
            sections[section]["vessel_count"] += 1

        if "water" in sentence.lower():
            sections[section]["water_count"] += 1

        if "pharmaceutical-substance" in sentence:
            sections[section]["pharmaceutical_substance_count"] += 1

    return dict(sections)


def calculate_enrichment(sections):
    """Calculate enrichment comparing botanical sections vs non-botanical"""

    # Herbal + Pharmaceutical = botanical sections
    botanical_combined = {
        "sentence_count": sections["herbal"]["sentence_count"]
        + sections["pharmaceutical"]["sentence_count"],
        "al_count": sections["herbal"]["al_count"]
        + sections["pharmaceutical"]["al_count"],
        "botanical_count": sections["herbal"]["botanical_count"]
        + sections["pharmaceutical"]["botanical_count"],
        "oak_gen_count": sections["herbal"]["oak_gen_count"]
        + sections["pharmaceutical"]["oak_gen_count"],
        "oat_gen_count": sections["herbal"]["oat_gen_count"]
        + sections["pharmaceutical"]["oat_gen_count"],
        "vessel_count": sections["herbal"]["vessel_count"]
        + sections["pharmaceutical"]["vessel_count"],
        "water_count": sections["herbal"]["water_count"]
        + sections["pharmaceutical"]["water_count"],
    }

    # Astronomical + Biological + Stars = non-botanical
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
        bot_freq = (
            botanical_combined[term] / botanical_combined["sentence_count"]
            if botanical_combined["sentence_count"] > 0
            else 0
        )
        non_bot_freq = (
            non_botanical[term] / non_botanical["sentence_count"]
            if non_botanical["sentence_count"] > 0
            else 0
        )

        enrichment[term] = {
            "botanical_freq": bot_freq,
            "non_botanical_freq": non_bot_freq,
            "enrichment_ratio": bot_freq / non_bot_freq
            if non_bot_freq > 0
            else float("inf"),
        }

    return enrichment, botanical_combined, non_botanical


def main():
    print("=" * 80)
    print("SEMANTIC VALIDATION TEST 2: ILLUSTRATION CORRELATION (CORRECTED)")
    print("=" * 80)
    print()

    # Load data
    print("Loading translation data...")
    translations = load_data()
    print(f"Loaded {len(translations)} sentences")

    print("Loading folio mapping...")
    folio_mapping = load_folio_mapping()
    print(f"Loaded {len(folio_mapping)} folio sections")
    print()

    # Count terms by section
    print("=" * 80)
    print("ANALYZING TERM DISTRIBUTION BY MANUSCRIPT SECTION...")
    print("=" * 80)
    print()

    sections = count_terms_by_section(translations, folio_mapping)

    # Display results
    print("TERM FREQUENCIES BY SECTION:")
    print()

    for section_name in [
        "herbal",
        "astronomical",
        "biological",
        "pharmaceutical",
        "stars",
        "other",
    ]:
        if section_name in sections and sections[section_name]["sentence_count"] > 0:
            data = sections[section_name]
            print(f"SECTION: {section_name.upper()}")
            print(f"  Sentences: {data['sentence_count']}")
            print(
                f"  [?al]: {data['al_count']} ({data['al_count'] / data['sentence_count']:.3f} per sentence)"
            )
            print(
                f"  botanical-term: {data['botanical_count']} ({data['botanical_count'] / data['sentence_count']:.3f} per sentence)"
            )
            print(
                f"  oak-GEN: {data['oak_gen_count']} ({data['oak_gen_count'] / data['sentence_count']:.3f} per sentence)"
            )
            print(
                f"  oat-GEN: {data['oat_gen_count']} ({data['oat_gen_count'] / data['sentence_count']:.3f} per sentence)"
            )
            print(
                f"  vessel: {data['vessel_count']} ({data['vessel_count'] / data['sentence_count']:.3f} per sentence)"
            )
            print(
                f"  water: {data['water_count']} ({data['water_count'] / data['sentence_count']:.3f} per sentence)"
            )
            print()

    # Calculate enrichment
    print("=" * 80)
    print("ENRICHMENT ANALYSIS")
    print("=" * 80)
    print()

    enrichment, botanical, non_botanical = calculate_enrichment(sections)

    print(
        f"BOTANICAL SECTIONS (Herbal + Pharmaceutical): {botanical['sentence_count']} sentences"
    )
    print(
        f"NON-BOTANICAL SECTIONS (Astronomical + Biological + Stars): {non_botanical['sentence_count']} sentences"
    )
    print()

    print("ENRICHMENT RATIOS (Botanical vs Non-Botanical):")
    print()

    for term, data in enrichment.items():
        term_name = term.replace("_count", "").replace("_", "-")
        print(f"{term_name}:")
        print(f"  Botanical frequency: {data['botanical_freq']:.3f} per sentence")
        print(
            f"  Non-botanical frequency: {data['non_botanical_freq']:.3f} per sentence"
        )

        if data["enrichment_ratio"] == float("inf"):
            print(f"  Enrichment ratio: ∞× (term absent in non-botanical)")
        else:
            print(f"  Enrichment ratio: {data['enrichment_ratio']:.2f}×")
        print()

    # Interpretation
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print()

    # Calculate average enrichment (excluding infinite values)
    valid_enrichments = [
        data["enrichment_ratio"]
        for data in enrichment.values()
        if data["enrichment_ratio"] != float("inf") and data["enrichment_ratio"] > 0
    ]
    avg_enrichment = (
        sum(valid_enrichments) / len(valid_enrichments) if valid_enrichments else 0
    )

    if avg_enrichment >= 2.0:
        print("✓ STRONG SUPPORT for illustration correlation hypothesis")
        print(f"  - Average enrichment: {avg_enrichment:.2f}×")
        print(
            "  - Botanical terms ARE significantly enriched in herbal/pharmaceutical sections"
        )
        print("  - Manuscript content MATCHES illustrations")
    elif avg_enrichment >= 1.5:
        print("? MODERATE SUPPORT for illustration correlation hypothesis")
        print(f"  - Average enrichment: {avg_enrichment:.2f}×")
        print("  - Some enrichment observed")
    else:
        print("✗ WEAK SUPPORT for illustration correlation hypothesis")
        print(f"  - Average enrichment: {avg_enrichment:.2f}×")
        print("  - Enrichment below prediction threshold")

    print()

    # Save results
    output = {
        "sections": sections,
        "enrichment": {
            k: {
                kk: (float(vv) if vv != float("inf") else "infinite")
                for kk, vv in v.items()
            }
            for k, v in enrichment.items()
        },
        "summary": {
            "botanical_sentences": botanical["sentence_count"],
            "non_botanical_sentences": non_botanical["sentence_count"],
            "avg_enrichment": float(avg_enrichment),
        },
    }

    with open("SEMANTIC_TEST2_CORRECTED.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: SEMANTIC_TEST2_CORRECTED.json")
    print()


if __name__ == "__main__":
    main()
