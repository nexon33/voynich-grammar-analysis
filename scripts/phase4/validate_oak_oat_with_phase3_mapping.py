#!/usr/bin/env python3
"""
Validate Oak/Oat using Phase 3 folio mappings
"""

import json
from collections import Counter, defaultdict
from pathlib import Path


def load_folio_mappings():
    """Load Phase 3 folio-to-word-range mappings."""
    with open("results/phase3/proper_section_to_folio_mapping.json", "r") as f:
        return json.load(f)


def load_voynich_words():
    """Load Voynich word list."""
    with open(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt",
        "r",
        encoding="utf-8",
    ) as f:
        return f.read().split()


def find_oak_oat_variants():
    """Get oak and oat variants from Phase 4A results."""
    with open("results/phase4/compound_and_partial_matches.json", "r") as f:
        data = json.load(f)

    oak_variants = set()
    oat_variants = set()

    for pm in data["partial_matches"]:
        if pm["me_word"] == "oke":
            oak_variants.add(pm["voynich_word"])
        elif pm["me_word"] == "ote":
            oat_variants.add(pm["voynich_word"])

    return oak_variants, oat_variants


def map_words_to_folios(words, folio_mappings):
    """Map word positions to folios using Phase 3 mappings."""
    word_to_folio = {}

    for section in folio_mappings:
        # Parse word range
        start, end = map(int, section["word_range"].split("-"))
        primary_folio = section["primary_folio"]

        # Map words in this range to primary folio
        for i in range(start, min(end, len(words))):
            word_to_folio[i] = primary_folio

    return word_to_folio


def analyze_plant_distribution(words, word_to_folio, plant_variants, plant_name):
    """Analyze distribution of plant words across folios."""

    folio_counts = Counter()
    folio_words = defaultdict(list)
    total_found = 0

    for i, word in enumerate(words):
        if word.lower() in plant_variants:
            total_found += 1
            if i in word_to_folio:
                folio = word_to_folio[i]
                folio_counts[folio] += 1
                folio_words[folio].append(word)

    return folio_counts, folio_words, total_found


def classify_folios():
    """
    Classify folios into sections based on Voynich research.
    """
    classifications = {}

    # Herbal section (f1r-f66v): Plant illustrations
    for i in range(1, 67):
        classifications[f"f{i}r"] = "herbal"
        classifications[f"f{i}v"] = "herbal"

    # Astronomical/Astrological (f67r-f73v): Stars, zodiac
    for i in range(67, 74):
        classifications[f"f{i}r"] = "astronomical"
        classifications[f"f{i}v"] = "astronomical"

    # Biological (f75r-f84v): Naked figures in pools
    for i in range(75, 85):
        classifications[f"f{i}r"] = "biological"
        classifications[f"f{i}v"] = "biological"

    # Pharmaceutical (f87r-f102v): Jars and roots
    for i in range(87, 103):
        classifications[f"f{i}r"] = "pharmaceutical"
        classifications[f"f{i}v"] = "pharmaceutical"

    # Recipes (f103r-f116v): Dense text
    for i in range(103, 117):
        classifications[f"f{i}r"] = "recipes"
        classifications[f"f{i}v"] = "recipes"

    return classifications


def calculate_section_statistics(folio_counts, classifications):
    """Calculate statistics by section."""
    section_counts = Counter()

    for folio, count in folio_counts.items():
        section = classifications.get(folio, "unknown")
        section_counts[section] += count

    return section_counts


def main():
    print("=" * 80)
    print("OAK/OAT VALIDATION (Using Phase 3 Folio Mappings)")
    print("=" * 80)

    # Load data
    print("\nLoading data...")
    folio_mappings = load_folio_mappings()
    words = load_voynich_words()
    oak_variants, oat_variants = find_oak_oat_variants()

    print(f"Voynich words: {len(words):,}")
    print(f"Folio mapping sections: {len(folio_mappings)}")
    print(f"Oak variants: {len(oak_variants)}")
    print(f"Oat variants: {len(oat_variants)}")

    # Map words to folios
    print("\nMapping words to folios...")
    word_to_folio = map_words_to_folios(words, folio_mappings)
    print(f"Mapped {len(word_to_folio):,} word positions to folios")

    # Analyze oak
    print("\n" + "-" * 80)
    print("OAK ANALYSIS")
    print("-" * 80)

    oak_folio_counts, oak_folio_words, oak_total = analyze_plant_distribution(
        words, word_to_folio, oak_variants, "oak"
    )

    print(f"\nTotal oak instances: {oak_total:,}")
    print(f"Appears in {len(oak_folio_counts)} folios")

    print(f"\nTop 15 folios with oak:")
    for folio, count in oak_folio_counts.most_common(15):
        words_sample = ", ".join(oak_folio_words[folio][:4])
        print(f"  {folio}: {count:3} instances - {words_sample}")

    # Analyze oat
    print("\n" + "-" * 80)
    print("OAT ANALYSIS")
    print("-" * 80)

    oat_folio_counts, oat_folio_words, oat_total = analyze_plant_distribution(
        words, word_to_folio, oat_variants, "oat"
    )

    print(f"\nTotal oat instances: {oat_total:,}")
    print(f"Appears in {len(oat_folio_counts)} folios")

    print(f"\nTop 15 folios with oat:")
    for folio, count in oat_folio_counts.most_common(15):
        words_sample = ", ".join(oat_folio_words[folio][:4])
        print(f"  {folio}: {count:3} instances - {words_sample}")

    # Section analysis
    print("\n" + "-" * 80)
    print("SECTION DISTRIBUTION")
    print("-" * 80)

    classifications = classify_folios()

    oak_sections = calculate_section_statistics(oak_folio_counts, classifications)
    oat_sections = calculate_section_statistics(oat_folio_counts, classifications)

    # Calculate section sizes
    section_sizes = Counter()
    for folio, section in classifications.items():
        section_sizes[section] += 1

    print(f"\n{'Section':<20} {'Folios':<10} {'Oak':<10} {'Oat':<10} {'Combined'}")
    print("-" * 80)

    for section in [
        "herbal",
        "pharmaceutical",
        "recipes",
        "astronomical",
        "biological",
    ]:
        folios = section_sizes[section]
        oak_count = oak_sections[section]
        oat_count = oat_sections[section]
        combined = oak_count + oat_count
        print(f"{section:<20} {folios:<10} {oak_count:<10} {oat_count:<10} {combined}")

    # Calculate enrichment
    print("\n" + "-" * 80)
    print("ENRICHMENT ANALYSIS")
    print("-" * 80)

    total_folios = sum(section_sizes.values())

    print(
        f"\n{'Section':<20} {'Expected %':<12} {'Oak %':<12} {'Oat %':<12} {'Enrichment'}"
    )
    print("-" * 80)

    for section in [
        "herbal",
        "pharmaceutical",
        "recipes",
        "astronomical",
        "biological",
    ]:
        folios = section_sizes[section]
        expected_pct = (folios / total_folios) * 100

        oak_pct = (oak_sections[section] / oak_total) * 100 if oak_total > 0 else 0
        oat_pct = (oat_sections[section] / oat_total) * 100 if oat_total > 0 else 0

        oak_enrichment = oak_pct / expected_pct if expected_pct > 0 else 0
        oat_enrichment = oat_pct / expected_pct if expected_pct > 0 else 0
        avg_enrichment = (oak_enrichment + oat_enrichment) / 2

        status = ""
        if avg_enrichment > 1.3:
            status = " ✓ ENRICHED"
        elif avg_enrichment > 0.8:
            status = " ~ Expected"
        else:
            status = " - Depleted"

        print(
            f"{section:<20} {expected_pct:<12.1f} {oak_pct:<12.1f} {oat_pct:<12.1f} {avg_enrichment:<10.2f}x{status}"
        )

    # Save results
    output = {
        "oak": {
            "total": oak_total,
            "folio_counts": dict(oak_folio_counts.most_common()),
            "section_counts": dict(oak_sections),
        },
        "oat": {
            "total": oat_total,
            "folio_counts": dict(oat_folio_counts.most_common()),
            "section_counts": dict(oat_sections),
        },
        "sections": dict(section_sizes),
    }

    output_path = Path("results/phase4/oak_oat_folio_validation.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    # Conclusions
    print("\n" + "=" * 80)
    print("CONCLUSIONS")
    print("=" * 80)

    herbal_oak = oak_sections["herbal"]
    herbal_oat = oat_sections["herbal"]
    herbal_pct = ((herbal_oak + herbal_oat) / (oak_total + oat_total)) * 100

    print(f"\nHerbal section contains:")
    print(
        f"  {herbal_oak}/{oak_total} oak instances ({100 * herbal_oak / oak_total:.1f}%)"
    )
    print(
        f"  {herbal_oat}/{oat_total} oat instances ({100 * herbal_oat / oat_total:.1f}%)"
    )
    print(f"  Combined: {herbal_pct:.1f}% of all oak/oat words")

    if herbal_pct > 60:
        print("\n✓✓ STRONG VALIDATION - Majority of oak/oat in herbal section!")
    elif herbal_pct > 40:
        print("\n✓ MODERATE VALIDATION - Significant oak/oat in herbal section")
    else:
        print("\n~ WEAK VALIDATION - Oak/oat distributed across sections")
        print("  (May indicate these words have multiple meanings or")
        print("   sections aren't strictly separated by content)")


if __name__ == "__main__":
    main()
