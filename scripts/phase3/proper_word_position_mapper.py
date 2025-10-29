#!/usr/bin/env python3
"""
Create proper word position to folio mapping using ZL transcription.
This builds a definitive map of word positions to manuscript folios.
"""

import re
import json
from pathlib import Path


def build_word_to_folio_map():
    """
    Build a complete word-position-to-folio mapping from ZL transcription.
    Returns a dict mapping absolute word position to folio.
    """

    zl_path = (
        Path(__file__).parent.parent.parent
        / "data"
        / "voynich"
        / "eva_transcription"
        / "ZL3b-n.txt"
    )

    with open(zl_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    word_to_folio = {}
    current_folio = None
    absolute_word_position = 0

    folio_stats = {}  # Track words per folio

    for line in lines:
        line_stripped = line.strip()

        # Skip empty lines and comments
        if not line_stripped or line_stripped.startswith("#"):
            continue

        # Folio marker (e.g., <f1r>)
        if line_stripped.startswith("<f") and ">" in line_stripped:
            # Check if this is a folio header (not a text line)
            if "," not in line_stripped.split(">")[0]:
                folio_match = re.match(r"<(f\d+[rv])>", line_stripped)
                if folio_match:
                    current_folio = folio_match.group(1)
                    if current_folio not in folio_stats:
                        folio_stats[current_folio] = {
                            "start_word": absolute_word_position,
                            "word_count": 0,
                        }
                    continue

        # Text line (e.g., <f1r.1,@P0>)
        if "," in line_stripped and current_folio:
            # Extract text after the line marker
            parts = line_stripped.split(">")
            if len(parts) >= 2:
                text = parts[-1]

                # Normalize text: replace periods with spaces, remove special chars
                text = text.replace(".", " ")
                text = re.sub(r"[<>{}[\]()!?;:\-@$%*]", " ", text)

                # Split into words
                words = text.split()

                # Map each word position to this folio
                for word in words:
                    if word.strip():  # Only non-empty words
                        word_to_folio[absolute_word_position] = current_folio
                        absolute_word_position += 1
                        folio_stats[current_folio]["word_count"] += 1

    return word_to_folio, folio_stats, absolute_word_position


def map_sections_to_folios(word_to_folio, section_size=500):
    """
    Map sections (500-word chunks) to their corresponding folios.
    """

    max_word = max(word_to_folio.keys()) if word_to_folio else 0
    num_sections = (max_word // section_size) + 1

    section_mapping = []

    for section_id in range(num_sections):
        start_word = section_id * section_size
        end_word = min(start_word + section_size, max_word)

        # Find all folios in this range
        folios_in_section = {}
        for word_pos in range(start_word, end_word):
            if word_pos in word_to_folio:
                folio = word_to_folio[word_pos]
                folios_in_section[folio] = folios_in_section.get(folio, 0) + 1

        # Get primary folio (most words in this section)
        primary_folio = None
        if folios_in_section:
            primary_folio = max(folios_in_section.items(), key=lambda x: x[1])[0]

        section_mapping.append(
            {
                "section_id": section_id,
                "word_range": f"{start_word}-{end_word}",
                "primary_folio": primary_folio,
                "folios": list(folios_in_section.keys()),
                "folio_word_counts": folios_in_section,
            }
        )

    return section_mapping


def main():
    print("=" * 80)
    print("BUILDING PROPER WORD-TO-FOLIO MAPPING")
    print("=" * 80)
    print()

    print("Processing ZL transcription...")
    word_to_folio, folio_stats, total_words = build_word_to_folio_map()

    print(f"Total words in ZL transcription: {total_words:,}")
    print(f"Total folios: {len(folio_stats)}")
    print()

    # Show first few folios
    print("First 10 folios:")
    for i, (folio, stats) in enumerate(list(folio_stats.items())[:10]):
        print(
            f"  {folio}: words {stats['start_word']:5d}-{stats['start_word'] + stats['word_count']:5d} ({stats['word_count']:4d} words)"
        )
    print()

    # Map sections
    print("Mapping 500-word sections to folios...")
    section_mapping = map_sections_to_folios(word_to_folio)
    print(f"Created {len(section_mapping)} sections")
    print()

    # Save complete mapping
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"

    # Save section mapping
    output_path = results_dir / "proper_section_to_folio_mapping.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(section_mapping, f, indent=2)

    print(f"Section mapping saved to: {output_path}")

    # Save folio stats
    folio_stats_path = results_dir / "folio_statistics.json"
    with open(folio_stats_path, "w", encoding="utf-8") as f:
        json.dump(folio_stats, f, indent=2)

    print(f"Folio statistics saved to: {folio_stats_path}")
    print()

    # Load medical density data and map properly
    with open(results_dir / "section_medical_density.json", "r", encoding="utf-8") as f:
        medical_sections = json.load(f)

    print("=" * 80)
    print("HIGH MEDICAL DENSITY SECTIONS - PROPERLY MAPPED")
    print("=" * 80)
    print()

    high_density = [s for s in medical_sections if s["density_percent"] >= 1.0]
    high_density.sort(key=lambda x: x["density_percent"], reverse=True)

    critical_mappings = []

    for section in high_density[:10]:
        section_id = section["section_id"]
        density = section["density_percent"]
        med_count = section["medical_term_count"]

        # Get proper folio mapping
        if section_id < len(section_mapping):
            mapping = section_mapping[section_id]
            primary_folio = mapping["primary_folio"]
            folios = mapping["folios"]

            print(
                f"Section {section_id} (Density: {density:.1f}%, Medical terms: {med_count})"
            )
            print(f"  Word range: {mapping['word_range']}")
            print(f"  Primary folio: {primary_folio}")
            if len(folios) > 1:
                print(
                    f"  Also spans: {', '.join([f for f in folios if f != primary_folio])}"
                )
            print(
                f"  Medical terms: {', '.join([m['medical_term'] for m in section['medical_matches'][:5]])}"
            )
            print()

            critical_mappings.append(
                {
                    "section_id": section_id,
                    "density": density,
                    "medical_count": med_count,
                    "primary_folio": primary_folio,
                    "word_range": mapping["word_range"],
                }
            )

    # Save critical mappings
    critical_path = results_dir / "critical_section_mappings.json"
    with open(critical_path, "w", encoding="utf-8") as f:
        json.dump(critical_mappings, f, indent=2)

    print(f"Critical mappings saved to: {critical_path}")
    print()

    # CRITICAL CHECK: Section 4
    print("=" * 80)
    print("CRITICAL: Section 4 (Highest Medical Density) Verification")
    print("=" * 80)
    print()

    if 4 < len(section_mapping):
        section_4_map = section_mapping[4]
        print(f"Section 4 ACTUALLY maps to: {section_4_map['primary_folio']}")
        print(f"Word range: {section_4_map['word_range']}")
        print(f"Folios involved: {', '.join(section_4_map['folios'])}")
        print()
        print("Previous claim was f1v - verifying...")
        if section_4_map["primary_folio"] == "f1v":
            print("✓ CONFIRMED: Section 4 = f1v")
            print("  Belladonna finding is VALID")
        else:
            print(f"✗ ERROR: Section 4 = {section_4_map['primary_folio']}, NOT f1v")
            print("  Need to re-examine this folio")

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
