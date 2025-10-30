#!/usr/bin/env python3
"""
Extract Currier A/B classifications from the EVA transcription file.

This script parses ZL3b-n.txt to extract which folios are classified as
Currier Language A vs Language B (and which hand wrote them).
"""

import re
from collections import defaultdict


def extract_currier_classifications(filepath):
    """
    Parse the EVA transcription file and extract Currier classifications.

    Returns:
        dict: Mapping of folio -> {'language': 'A'|'B', 'hand': int, 'section': str}
    """
    classifications = {}
    current_folio = None
    current_section = None

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line_stripped = line.strip()

            # Extract folio number
            folio_match = re.match(r"<f(\d+[rv])>", line_stripped)
            if folio_match:
                current_folio = f"f{folio_match.group(1)}"

                # Determine section from folio number
                folio_num = int(re.search(r"\d+", folio_match.group(1)).group())
                if 1 <= folio_num <= 66:
                    current_section = "herbal"
                elif 67 <= folio_num <= 73:
                    current_section = "astronomical"
                elif 75 <= folio_num <= 84:
                    current_section = "biological"
                elif 85 <= folio_num <= 116:
                    current_section = "pharmaceutical"
                else:
                    current_section = "unknown"

                continue

            # Extract Currier language classification
            if current_folio and line_stripped.startswith("#"):
                # Look for "Currier's Language A" or "Currier's Language B" or "Currier's language A/B"
                lang_match = re.search(r"Currier'?s [Ll]anguage ([AB])", line_stripped)
                if lang_match:
                    language = lang_match.group(1)

                    # Extract hand number
                    hand_match = re.search(r"hand (\d+)", line_stripped)
                    hand = int(hand_match.group(1)) if hand_match else None

                    classifications[current_folio] = {
                        "language": language,
                        "hand": hand,
                        "section": current_section,
                    }

    return classifications


def main():
    filepath = "data/voynich/eva_transcription/ZL3b-n.txt"

    print("Extracting Currier A/B classifications from EVA transcription...")
    print()

    classifications = extract_currier_classifications(filepath)

    # Group by language
    language_a = [f for f, info in classifications.items() if info["language"] == "A"]
    language_b = [f for f, info in classifications.items() if info["language"] == "B"]

    print(f"Total folios with classification: {len(classifications)}")
    print(f"Language A folios: {len(language_a)}")
    print(f"Language B folios: {len(language_b)}")
    print()

    # Group by section
    section_counts = defaultdict(lambda: {"A": 0, "B": 0})
    for folio, info in classifications.items():
        section_counts[info["section"]][info["language"]] += 1

    print("Distribution by section:")
    print(f"{'Section':<20} {'Language A':<15} {'Language B':<15}")
    print("-" * 50)
    for section in ["herbal", "astronomical", "biological", "pharmaceutical"]:
        a_count = section_counts[section]["A"]
        b_count = section_counts[section]["B"]
        print(f"{section:<20} {a_count:<15} {b_count:<15}")
    print()

    # Show first few folios of each language
    print("First 10 Language A folios:")
    print(
        ", ".join(
            sorted(language_a, key=lambda x: int(re.search(r"\d+", x).group()))[:10]
        )
    )
    print()

    print("First 10 Language B folios:")
    print(
        ", ".join(
            sorted(language_b, key=lambda x: int(re.search(r"\d+", x).group()))[:10]
        )
    )
    print()

    # Save full classification to file
    output_file = "data/voynich/currier_classifications.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Currier A/B Classifications from EVA Transcription\n")
        f.write(f"# Total folios: {len(classifications)}\n")
        f.write(f"# Language A: {len(language_a)} folios\n")
        f.write(f"# Language B: {len(language_b)} folios\n")
        f.write("\n")
        f.write("Folio\tLanguage\tHand\tSection\n")

        # Sort by folio number
        sorted_folios = sorted(
            classifications.items(), key=lambda x: int(re.search(r"\d+", x[0]).group())
        )

        for folio, info in sorted_folios:
            hand = info["hand"] if info["hand"] is not None else "?"
            f.write(f"{folio}\t{info['language']}\t{hand}\t{info['section']}\n")

    print(f"Full classification saved to: {output_file}")


if __name__ == "__main__":
    main()
