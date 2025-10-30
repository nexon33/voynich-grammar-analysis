#!/usr/bin/env python3
"""
Semantic Validation Test 2: Illustration Correlation (Proper Implementation)

Uses ZL3b-n.txt file to map lines to folios, then compares botanical term
frequency in herbal vs non-herbal sections.
"""

import json
import re
from collections import defaultdict


def load_translations():
    """Load translation data"""
    with open(
        "COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)
    return data["translations"]


def build_folio_mapping():
    """
    Build mapping from line numbers to folios using ZL3b-n.txt

    Format in file: <f1r.1,@P0> text...
    This tells us line 1 is on folio f1r
    """
    line_to_folio = {}

    with open(
        "data/voynich/eva_transcription/ZL3b-n.txt",
        "r",
        encoding="utf-8",
        errors="ignore",
    ) as f:
        line_num = 0
        for file_line in f:
            # Skip comments and blank lines
            if file_line.startswith("#") or not file_line.strip():
                continue

            # Look for folio markers like <f1r.1,@P0> or <f1r>
            folio_match = re.search(r"<(f\d+[rv])\.?\d*[^>]*>", file_line)
            if folio_match:
                folio = folio_match.group(1)
                line_num += 1
                line_to_folio[line_num] = folio

    return line_to_folio


def classify_folio(folio):
    """
    Classify folio into manuscript sections.

    Known Voynich sections:
    - Herbal: f1r-f66v (botanical drawings)
    - Astronomical: f67r-f73v (circular diagrams)
    - Biological: f75r-f84v (cosmological diagrams)
    - Pharmaceutical: f87r-f102v (jars and plants)
    - Stars: f103r-f116r (star diagrams)
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


def count_terms_by_section(translations, line_to_folio):
    """Count pharmaceutical terms by manuscript section"""

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
        }
    )

    unmapped_count = 0

    for idx, trans in enumerate(translations):
        # Extract line number from folio_id
        folio_id = trans.get("folio", "unknown")
        line_match = re.search(r"line(\d+)", folio_id)

        if line_match:
            line_num = int(line_match.group(1))
        else:
            line_num = idx + 1  # Fallback to index

        # Get folio from mapping
        folio = line_to_folio.get(line_num)

        if not folio:
            unmapped_count += 1
            section = "unknown"
        else:
            section = classify_folio(folio)

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

        if "[?ch]" in sentence and "VERB" in sentence:
            sections[section]["ch_verb_count"] += 1

        if "[?sh]" in sentence and "VERB" in sentence:
            sections[section]["sh_verb_count"] += 1

    return dict(sections), unmapped_count


def calculate_enrichment(sections):
    """Calculate enrichment: botanical sections vs non-botanical"""

    # Combine botanical sections (herbal + pharmaceutical)
    botanical = {
        "sentence_count": sections.get("herbal", {}).get("sentence_count", 0)
        + sections.get("pharmaceutical", {}).get("sentence_count", 0),
        "al_count": sections.get("herbal", {}).get("al_count", 0)
        + sections.get("pharmaceutical", {}).get("al_count", 0),
        "botanical_count": sections.get("herbal", {}).get("botanical_count", 0)
        + sections.get("pharmaceutical", {}).get("botanical_count", 0),
        "oak_gen_count": sections.get("herbal", {}).get("oak_gen_count", 0)
        + sections.get("pharmaceutical", {}).get("oak_gen_count", 0),
        "oat_gen_count": sections.get("herbal", {}).get("oat_gen_count", 0)
        + sections.get("pharmaceutical", {}).get("oat_gen_count", 0),
        "vessel_count": sections.get("herbal", {}).get("vessel_count", 0)
        + sections.get("pharmaceutical", {}).get("vessel_count", 0),
        "water_count": sections.get("herbal", {}).get("water_count", 0)
        + sections.get("pharmaceutical", {}).get("water_count", 0),
    }

    # Combine non-botanical sections
    non_botanical = {
        "sentence_count": sections.get("astronomical", {}).get("sentence_count", 0)
        + sections.get("biological", {}).get("sentence_count", 0)
        + sections.get("stars", {}).get("sentence_count", 0),
        "al_count": sections.get("astronomical", {}).get("al_count", 0)
        + sections.get("biological", {}).get("al_count", 0)
        + sections.get("stars", {}).get("al_count", 0),
        "botanical_count": sections.get("astronomical", {}).get("botanical_count", 0)
        + sections.get("biological", {}).get("botanical_count", 0)
        + sections.get("stars", {}).get("botanical_count", 0),
        "oak_gen_count": sections.get("astronomical", {}).get("oak_gen_count", 0)
        + sections.get("biological", {}).get("oak_gen_count", 0)
        + sections.get("stars", {}).get("oak_gen_count", 0),
        "oat_gen_count": sections.get("astronomical", {}).get("oat_gen_count", 0)
        + sections.get("biological", {}).get("oat_gen_count", 0)
        + sections.get("stars", {}).get("oat_gen_count", 0),
        "vessel_count": sections.get("astronomical", {}).get("vessel_count", 0)
        + sections.get("biological", {}).get("vessel_count", 0)
        + sections.get("stars", {}).get("vessel_count", 0),
        "water_count": sections.get("astronomical", {}).get("water_count", 0)
        + sections.get("biological", {}).get("water_count", 0)
        + sections.get("stars", {}).get("water_count", 0),
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
            botanical[term] / botanical["sentence_count"]
            if botanical["sentence_count"] > 0
            else 0
        )
        non_bot_freq = (
            non_botanical[term] / non_botanical["sentence_count"]
            if non_botanical["sentence_count"] > 0
            else 0
        )

        if non_bot_freq > 0:
            ratio = bot_freq / non_bot_freq
        elif bot_freq > 0:
            ratio = float("inf")
        else:
            ratio = 1.0

        enrichment[term] = {
            "botanical_freq": bot_freq,
            "non_botanical_freq": non_bot_freq,
            "enrichment_ratio": ratio,
        }

    return enrichment, botanical, non_botanical


def main():
    print("=" * 80)
    print("SEMANTIC VALIDATION TEST 2: ILLUSTRATION CORRELATION")
    print("=" * 80)
    print()
    print("HYPOTHESIS: Botanical terms cluster in illustrated herbal sections")
    print()
    print("PREDICTION:")
    print("  - Herbal sections (f1r-f66v, f87r-f102v): HIGH botanical frequency")
    print("  - Non-herbal sections (f67r-f73v, f75r-f84v, f103r-f116r): LOW frequency")
    print("  - Expected enrichment: 2-5× in botanical sections")
    print()

    # Load data
    print("Loading translation data...")
    translations = load_translations()
    print(f"Loaded {len(translations)} sentences")

    print("Building folio mapping from ZL3b-n.txt...")
    line_to_folio = build_folio_mapping()
    print(f"Mapped {len(line_to_folio)} lines to folios")
    print()

    # Count terms
    print("=" * 80)
    print("ANALYZING TERM DISTRIBUTION BY MANUSCRIPT SECTION...")
    print("=" * 80)
    print()

    sections, unmapped = count_terms_by_section(translations, line_to_folio)

    if unmapped > 0:
        print(f"WARNING: {unmapped} sentences could not be mapped to folios")
        print()

    # Display results
    print("TERM FREQUENCIES BY SECTION:")
    print()

    section_order = [
        "herbal",
        "astronomical",
        "biological",
        "pharmaceutical",
        "stars",
        "other",
        "unknown",
    ]

    for section_name in section_order:
        if section_name in sections and sections[section_name]["sentence_count"] > 0:
            data = sections[section_name]
            print(f"SECTION: {section_name.upper()}")
            print(f"  Sentences: {data['sentence_count']}")

            if data["sentence_count"] > 0:
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

    if botanical["sentence_count"] == 0 or non_botanical["sentence_count"] == 0:
        print("ERROR: Cannot calculate enrichment - one section has no sentences")
        print("This suggests the folio mapping didn't work correctly.")
        return

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
            print(f"  Enrichment ratio: ∞× (term absent in non-botanical sections)")
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

    if valid_enrichments:
        avg_enrichment = sum(valid_enrichments) / len(valid_enrichments)
    else:
        avg_enrichment = 0

    print(f"Average enrichment: {avg_enrichment:.2f}×")
    print()

    if avg_enrichment >= 2.0:
        print("✓ STRONG SUPPORT for illustration correlation hypothesis")
        print(
            f"  - Botanical terms ARE significantly enriched in herbal/pharmaceutical sections"
        )
        print(
            f"  - Enrichment {avg_enrichment:.2f}× exceeds prediction threshold (2.0×)"
        )
        print("  - Manuscript content MATCHES illustrations")
    elif avg_enrichment >= 1.5:
        print("? MODERATE SUPPORT for illustration correlation hypothesis")
        print(f"  - Some enrichment observed ({avg_enrichment:.2f}×)")
        print("  - Below strong threshold but above random baseline")
    elif avg_enrichment >= 1.0:
        print("~ WEAK SUPPORT for illustration correlation hypothesis")
        print(f"  - Minimal enrichment ({avg_enrichment:.2f}×)")
        print("  - Near random distribution")
    else:
        print("✗ NO SUPPORT for illustration correlation hypothesis")
        print(f"  - No enrichment or depletion ({avg_enrichment:.2f}×)")
        print("  - Content may not correlate with illustrations")

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
            "unmapped_sentences": unmapped,
        },
    }

    with open("SEMANTIC_TEST2_FINAL.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: SEMANTIC_TEST2_FINAL.json")
    print()

    print("=" * 80)
    print("TEST 2 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
