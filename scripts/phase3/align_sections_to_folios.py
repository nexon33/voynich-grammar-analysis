#!/usr/bin/env python3
"""
Align Takahashi transcription to ZL EVA transcription with folio markers.
This maps our translated sections to exact manuscript folios.
"""

import re
from pathlib import Path
from difflib import SequenceMatcher


def normalize_text(text):
    """Normalize text for comparison (remove punctuation, lowercase)."""
    # Remove special characters but keep words
    text = re.sub(r"[<>{}[\](),.!?;:\-@$%]", " ", text)
    # Remove numbers
    text = re.sub(r"\d+", "", text)
    # Normalize spaces and lowercase
    text = " ".join(text.lower().split())
    return text


def load_takahashi():
    """Load our Takahashi transcription."""
    data_path = (
        Path(__file__).parent.parent.parent
        / "data"
        / "voynich"
        / "eva_transcription"
        / "voynich_eva_takahashi.txt"
    )

    with open(data_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Clean and split into words
    words = normalize_text(content).split()
    return words


def load_zl_with_folios():
    """Load ZL transcription with folio markers."""
    zl_path = (
        Path(__file__).parent.parent.parent
        / "data"
        / "voynich"
        / "eva_transcription"
        / "ZL3b-n.txt"
    )

    with open(zl_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Parse into folio sections
    folio_data = []
    current_folio = None
    current_words = []
    word_position = 0

    for line in lines:
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue

        # Folio marker
        if line.startswith("<f") and ">" in line and not "," in line.split(">")[0]:
            # Save previous folio if exists
            if current_folio and current_words:
                folio_data.append(
                    {
                        "folio": current_folio,
                        "start_word": word_position - len(current_words),
                        "end_word": word_position,
                        "word_count": len(current_words),
                        "words": current_words.copy(),
                        "text": " ".join(current_words),
                    }
                )

            # Start new folio
            folio_match = re.match(r"<(f\d+[rv])>", line)
            if folio_match:
                current_folio = folio_match.group(1)
                current_words = []

        # Text line (has folio.line marker)
        elif "," in line and current_folio:
            # Extract text after the marker
            parts = line.split(">")
            if len(parts) >= 2:
                text = parts[-1]
                words = normalize_text(text).split()
                current_words.extend(words)
                word_position += len(words)

    # Add last folio
    if current_folio and current_words:
        folio_data.append(
            {
                "folio": current_folio,
                "start_word": word_position - len(current_words),
                "end_word": word_position,
                "word_count": len(current_words),
                "words": current_words.copy(),
                "text": " ".join(current_words),
            }
        )

    return folio_data


def align_texts(takahashi_words, folio_data):
    """
    Align Takahashi and ZL transcriptions.
    Returns mapping of word positions to folios.
    """
    print(f"Takahashi words: {len(takahashi_words)}")
    print(f"ZL folios: {len(folio_data)}")
    print(f"ZL total words: {folio_data[-1]['end_word'] if folio_data else 0}")
    print()

    # Check first 100 words similarity
    takahashi_sample = " ".join(takahashi_words[:100])
    zl_sample = " ".join(folio_data[0]["words"][:100]) if folio_data else ""

    similarity = SequenceMatcher(None, takahashi_sample, zl_sample).ratio()
    print(f"First 100 words similarity: {similarity:.2%}")
    print()

    if similarity < 0.7:
        print("⚠ Warning: Transcriptions may differ significantly")
        print()

    # Simple alignment: assume word positions correspond roughly
    # (This works if both transcriptions follow same page order)
    word_to_folio = {}

    for folio in folio_data:
        for word_pos in range(folio["start_word"], folio["end_word"]):
            word_to_folio[word_pos] = folio["folio"]

    return word_to_folio


def map_sections_to_folios(word_to_folio, sections_data):
    """Map our translated sections to folios."""

    section_folio_map = []

    for section in sections_data:
        section_id = section["section_id"]
        word_start = section_id * 500
        word_end = word_start + 500

        # Find all folios in this range
        folios_in_section = set()
        for word_pos in range(word_start, word_end):
            if word_pos in word_to_folio:
                folios_in_section.add(word_to_folio[word_pos])

        section_folio_map.append(
            {
                "section_id": section_id,
                "word_range": f"{word_start}-{word_end}",
                "folios": sorted(list(folios_in_section)),
                "medical_density": section.get("density_percent", 0),
                "medical_term_count": section.get("medical_term_count", 0),
                "first_words": section.get("first_words", ""),
            }
        )

    return section_folio_map


def main():
    print("=" * 80)
    print("MAPPING SECTIONS TO FOLIOS")
    print("=" * 80)
    print()

    # Load transcriptions
    print("Loading Takahashi transcription...")
    takahashi_words = load_takahashi()

    print("Loading ZL transcription with folio markers...")
    folio_data = load_zl_with_folios()
    print()

    # Align
    print("Aligning transcriptions...")
    word_to_folio = align_texts(takahashi_words, folio_data)
    print()

    # Load our section data
    print("Loading medical density analysis...")
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"

    import json

    with open(results_dir / "section_medical_density.json", "r", encoding="utf-8") as f:
        sections_data = json.load(f)

    # Map sections to folios
    print("Mapping sections to folios...")
    section_folio_map = map_sections_to_folios(word_to_folio, sections_data)
    print()

    # Save results
    output_path = results_dir / "section_to_folio_mapping.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(section_folio_map, f, indent=2)

    print(f"Saved mapping to: {output_path}")
    print()

    # Display high-density sections
    print("=" * 80)
    print("HIGH MEDICAL DENSITY SECTIONS AND THEIR FOLIOS")
    print("=" * 80)
    print()

    high_density = [s for s in section_folio_map if s["medical_density"] >= 1.0]
    high_density.sort(key=lambda x: x["medical_density"], reverse=True)

    for i, section in enumerate(high_density[:10], 1):
        print(
            f"{i}. Section {section['section_id']} - Density: {section['medical_density']:.1f}%"
        )
        print(f"   Words: {section['word_range']}")
        print(f"   Folios: {', '.join(section['folios'])}")
        print(f"   Medical terms: {section['medical_term_count']}")
        print(f"   First words: {section['first_words'][:60]}...")
        print()

    print("=" * 80)
    print("CRITICAL TEST: Section 4 (Highest Density)")
    print("=" * 80)
    print()

    section_4 = next((s for s in section_folio_map if s["section_id"] == 4), None)
    if section_4:
        print(f"Section 4 maps to folios: {', '.join(section_4['folios'])}")
        print(f"Medical density: {section_4['medical_density']:.1f}%")
        print(f"Medical terms: {section_4['medical_term_count']}")
        print()
        print("NEXT STEP:")
        print("1. View these folios in Yale Beinecke scans:")
        print("   https://brbl-dl.library.yale.edu/vufind/Record/3519597")
        print()
        print("2. Look for wound-healing plants:")
        print("   - Plantain (Plantago)")
        print("   - Betony (Betonica)")
        print("   - Yarrow (Achillea)")
        print("   - Woundwort (Stachys)")
        print()
        print("3. Test the prediction:")
        print("   Does this folio show a wound-healing plant?")
        print("   YES → Strong validation of translation")
        print("   NO  → Need to reconsider approach")

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
