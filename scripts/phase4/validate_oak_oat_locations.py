#!/usr/bin/env python3
"""
Option 1: Validate Oak/Oat Discovery

Map oak and oat word instances to folio locations and check for
illustration correlation.
"""

import json
import re
from collections import defaultdict, Counter
from pathlib import Path


def load_voynich_with_folios():
    """Load Voynich transcription with folio markers."""

    # Try to find a transcription with folio markers
    transcription_files = [
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt",
        "data/voynich/transcription_with_folios.txt",
    ]

    for filepath in transcription_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if it has folio markers
            if "<f" in content or "f1r" in content or "#" in content:
                print(f"Using transcription: {filepath}")
                return parse_transcription_with_folios(content)
        except FileNotFoundError:
            continue

    # If no folio markers found, try to infer from word positions
    print("No folio markers found in transcription files.")
    print("Will attempt to map by word position...")

    with open(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt",
        "r",
        encoding="utf-8",
    ) as f:
        words = f.read().split()

    return estimate_folios_by_position(words)


def parse_transcription_with_folios(content):
    """Parse transcription text with folio markers."""

    folio_to_words = defaultdict(list)
    current_folio = None

    # Look for folio markers in various formats:
    # <f1r>, #f1r#, f1r:, etc.

    lines = content.split("\n")
    for line in lines:
        # Check for folio marker
        folio_match = re.search(r"[<#]?f(\d+[rv])[>#:]?", line, re.IGNORECASE)
        if folio_match:
            current_folio = "f" + folio_match.group(1).lower()
            continue

        # Extract words from line (skip markers)
        words = line.split()
        for word in words:
            # Skip markers and very short words
            if word.startswith("<") or word.startswith("#") or len(word) < 2:
                continue
            # Clean word
            word = re.sub(r"[<>#:;,\.]", "", word)
            if word and current_folio:
                folio_to_words[current_folio].append(word)

    return folio_to_words


def estimate_folios_by_position(words):
    """Estimate folio locations based on word position."""

    # Average ~50 words per folio based on typical Voynich density
    words_per_folio = 50

    folio_to_words = defaultdict(list)

    # Voynich has ~240 folios (f1r to f116v, with gaps)
    # For simplicity, distribute words evenly

    for i, word in enumerate(words):
        folio_num = (i // words_per_folio) + 1
        # Alternate r/v
        side = "r" if (folio_num % 2) == 1 else "v"
        actual_folio_num = (folio_num + 1) // 2
        folio = f"f{actual_folio_num}{side}"
        folio_to_words[folio].append(word)

    return folio_to_words


def find_oak_variants():
    """Return all oak-related words found in Phase 4A."""
    return {
        "okedy",
        "okeedy",
        "qokey",
        "qokol",
        "okol",
        "okeol",
        "okey",
        "okeody",
        "qokor",
        "okor",
        "qokeody",
        "okeeey",
        "qokeol",
        "okeey",
        "okeol",
        "okol",
        "oko",
        "oke",
    }


def find_oat_variants():
    """Return all oat-related words found in Phase 4A."""
    return {
        "oteey",
        "oteedy",
        "qotedy",
        "otol",
        "qoteedy",
        "oteol",
        "qoteey",
        "oteody",
        "otor",
        "otey",
        "qotol",
        "oto",
        "ote",
        "qotor",
        "otedy",
        "oteol",
        "qotey",
    }


def map_plant_to_folios(folio_to_words, plant_variants, plant_name):
    """Map plant word occurrences to folios."""

    folio_counts = Counter()
    folio_words = defaultdict(list)

    for folio, words in folio_to_words.items():
        for word in words:
            if word.lower() in plant_variants:
                folio_counts[folio] += 1
                folio_words[folio].append(word)

    return folio_counts, folio_words


def identify_botanical_sections():
    """
    Identify known botanical sections of the manuscript.

    Based on standard Voynich research:
    - f1r-f66v: "Herbal" section (plant illustrations)
    - f67r-f73v: "Astronomical" section
    - f75r-f84v: "Biological" section (naked figures, pools)
    - f85r-f86v: "Text-only" section
    - f87r-f102v: "Pharmaceutical" section (jars, roots)
    - f103r-f116v: "Recipes" section
    """

    sections = {
        "herbal": {
            "folios": set(),
            "description": "Plant illustrations with roots, leaves, flowers",
        },
        "pharmaceutical": {
            "folios": set(),
            "description": "Jars and plant parts (roots, etc.)",
        },
        "recipes": {"folios": set(), "description": "Text-heavy recipe section"},
        "other": {"folios": set(), "description": "Astronomical, biological, other"},
    }

    # Herbal section: f1r to f66v
    for i in range(1, 67):
        sections["herbal"]["folios"].add(f"f{i}r")
        sections["herbal"]["folios"].add(f"f{i}v")

    # Pharmaceutical section: f87r to f102v
    for i in range(87, 103):
        sections["pharmaceutical"]["folios"].add(f"f{i}r")
        sections["pharmaceutical"]["folios"].add(f"f{i}v")

    # Recipes section: f103r to f116v
    for i in range(103, 117):
        sections["recipes"]["folios"].add(f"f{i}r")
        sections["recipes"]["folios"].add(f"f{i}v")

    # Other sections
    for i in range(67, 87):
        sections["other"]["folios"].add(f"f{i}r")
        sections["other"]["folios"].add(f"f{i}v")

    return sections


def analyze_section_distribution(folio_counts, sections):
    """Analyze how plant words distribute across manuscript sections."""

    section_counts = {name: 0 for name in sections.keys()}

    for folio, count in folio_counts.items():
        for section_name, section_data in sections.items():
            if folio in section_data["folios"]:
                section_counts[section_name] += count
                break

    return section_counts


def calculate_enrichment(section_counts, sections, total_instances):
    """Calculate enrichment: observed vs expected distribution."""

    enrichment = {}

    # Calculate expected distribution (proportional to section size)
    total_folios = sum(len(s["folios"]) for s in sections.values())

    for section_name, section_data in sections.items():
        section_size = len(section_data["folios"])
        expected_proportion = section_size / total_folios
        expected_count = total_instances * expected_proportion

        observed_count = section_counts[section_name]

        if expected_count > 0:
            enrichment_ratio = observed_count / expected_count
        else:
            enrichment_ratio = 0

        enrichment[section_name] = {
            "observed": observed_count,
            "expected": expected_count,
            "enrichment": enrichment_ratio,
            "folios": section_size,
        }

    return enrichment


def statistical_test(enrichment_data, section_name="herbal"):
    """
    Perform binomial test for enrichment in botanical section.

    H0: Oak/oat words are randomly distributed across manuscript
    H1: Oak/oat words are enriched in botanical sections
    """

    from scipy import stats

    herbal_data = enrichment_data[section_name]

    observed = herbal_data["observed"]
    total_instances = sum(e["observed"] for e in enrichment_data.values())
    expected_prob = (
        herbal_data["expected"] / total_instances if total_instances > 0 else 0
    )

    # Binomial test
    p_value = stats.binom_test(
        observed, total_instances, expected_prob, alternative="greater"
    )

    return p_value


def main():
    print("=" * 80)
    print("OPTION 1: VALIDATE OAK/OAT DISCOVERY")
    print("=" * 80)
    print("\nMapping plant word instances to folio locations...")

    # Load transcription
    folio_to_words = load_voynich_with_folios()

    print(f"\nFound {len(folio_to_words)} folios with words")
    total_words = sum(len(words) for words in folio_to_words.values())
    print(f"Total words: {total_words:,}")

    # Get plant variants
    oak_variants = find_oak_variants()
    oat_variants = find_oat_variants()

    print(f"\nOak variants to search: {len(oak_variants)}")
    print(f"Oat variants to search: {len(oat_variants)}")

    # Map to folios
    print("\n" + "-" * 80)
    print("MAPPING OAK INSTANCES")
    print("-" * 80)

    oak_folio_counts, oak_folio_words = map_plant_to_folios(
        folio_to_words, oak_variants, "oak"
    )

    total_oak = sum(oak_folio_counts.values())
    print(f"\nTotal oak instances found: {total_oak:,}")
    print(f"Appears in {len(oak_folio_counts)} different folios")

    print(f"\nTop 20 folios with oak:")
    for folio, count in oak_folio_counts.most_common(20):
        print(f"  {folio}: {count} instances - {', '.join(oak_folio_words[folio][:5])}")

    print("\n" + "-" * 80)
    print("MAPPING OAT INSTANCES")
    print("-" * 80)

    oat_folio_counts, oat_folio_words = map_plant_to_folios(
        folio_to_words, oat_variants, "oat"
    )

    total_oat = sum(oat_folio_counts.values())
    print(f"\nTotal oat instances found: {total_oat:,}")
    print(f"Appears in {len(oat_folio_counts)} different folios")

    print(f"\nTop 20 folios with oat:")
    for folio, count in oat_folio_counts.most_common(20):
        print(f"  {folio}: {count} instances - {', '.join(oat_folio_words[folio][:5])}")

    # Identify sections
    print("\n" + "-" * 80)
    print("SECTION DISTRIBUTION ANALYSIS")
    print("-" * 80)

    sections = identify_botanical_sections()

    print("\nManuscript sections:")
    for section_name, section_data in sections.items():
        print(
            f"  {section_name:20} {len(section_data['folios']):3} folios - {section_data['description']}"
        )

    # Analyze oak distribution
    oak_section_counts = analyze_section_distribution(oak_folio_counts, sections)
    oak_enrichment = calculate_enrichment(oak_section_counts, sections, total_oak)

    print("\n" + "-" * 80)
    print("OAK DISTRIBUTION BY SECTION")
    print("-" * 80)
    print(
        f"\n{'Section':<20} {'Observed':<12} {'Expected':<12} {'Enrichment':<12} {'Status'}"
    )
    print("-" * 80)

    for section_name in ["herbal", "pharmaceutical", "recipes", "other"]:
        data = oak_enrichment[section_name]
        status = (
            "✓ ENRICHED"
            if data["enrichment"] > 1.5
            else ("✓ Expected" if data["enrichment"] > 0.8 else "- Depleted")
        )
        print(
            f"{section_name:<20} {data['observed']:<12} {data['expected']:<12.1f} {data['enrichment']:<12.2f}x {status}"
        )

    # Analyze oat distribution
    oat_section_counts = analyze_section_distribution(oat_folio_counts, sections)
    oat_enrichment = calculate_enrichment(oat_section_counts, sections, total_oat)

    print("\n" + "-" * 80)
    print("OAT DISTRIBUTION BY SECTION")
    print("-" * 80)
    print(
        f"\n{'Section':<20} {'Observed':<12} {'Expected':<12} {'Enrichment':<12} {'Status'}"
    )
    print("-" * 80)

    for section_name in ["herbal", "pharmaceutical", "recipes", "other"]:
        data = oat_enrichment[section_name]
        status = (
            "✓ ENRICHED"
            if data["enrichment"] > 1.5
            else ("✓ Expected" if data["enrichment"] > 0.8 else "- Depleted")
        )
        print(
            f"{section_name:<20} {data['observed']:<12} {data['expected']:<12.1f} {data['enrichment']:<12.2f}x {status}"
        )

    # Statistical validation
    print("\n" + "-" * 80)
    print("STATISTICAL VALIDATION")
    print("-" * 80)

    try:
        oak_p_value = statistical_test(oak_enrichment, "herbal")
        oat_p_value = statistical_test(oat_enrichment, "herbal")

        print(f"\nBinomial test (enrichment in HERBAL section):")
        print(f"  Oak p-value: {oak_p_value:.6f}")
        if oak_p_value < 0.001:
            print(f"  ✓✓ HIGHLY SIGNIFICANT (p < 0.001)")
        elif oak_p_value < 0.01:
            print(f"  ✓ SIGNIFICANT (p < 0.01)")
        elif oak_p_value < 0.05:
            print(f"  ✓ Significant (p < 0.05)")
        else:
            print(f"  - Not significant (p >= 0.05)")

        print(f"\n  Oat p-value: {oat_p_value:.6f}")
        if oat_p_value < 0.001:
            print(f"  ✓✓ HIGHLY SIGNIFICANT (p < 0.001)")
        elif oat_p_value < 0.01:
            print(f"  ✓ SIGNIFICANT (p < 0.01)")
        elif oat_p_value < 0.05:
            print(f"  ✓ Significant (p < 0.05)")
        else:
            print(f"  - Not significant (p >= 0.05)")

    except ImportError:
        print("\n(scipy not available - cannot calculate p-values)")
        print("Install scipy for statistical validation: pip install scipy")

    # Save results
    output = {
        "oak": {
            "total_instances": total_oak,
            "folio_distribution": dict(oak_folio_counts.most_common()),
            "section_distribution": oak_section_counts,
            "enrichment": oak_enrichment,
        },
        "oat": {
            "total_instances": total_oat,
            "folio_distribution": dict(oat_folio_counts.most_common()),
            "section_distribution": oat_section_counts,
            "enrichment": oat_enrichment,
        },
    }

    output_path = Path("results/phase4/oak_oat_validation.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    print("\nCONCLUSIONS:")

    oak_herbal_enrichment = oak_enrichment["herbal"]["enrichment"]
    oat_herbal_enrichment = oat_enrichment["herbal"]["enrichment"]

    if oak_herbal_enrichment > 1.5 or oat_herbal_enrichment > 1.5:
        print("\n✓ OAK/OAT words ARE enriched in botanical sections!")
        print("  This validates our decipherment - plants appear where expected.")
    else:
        print("\n- OAK/OAT words are evenly distributed across manuscript")
        print("  May indicate these words have different meanings than plants,")
        print("  or manuscript doesn't strictly separate content by section.")


if __name__ == "__main__":
    main()
