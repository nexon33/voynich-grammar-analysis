#!/usr/bin/env python3
"""
Manual search in ZL transcription to find exact folios for high-density sections.
This verifies the automatic alignment by directly searching for section text.
"""

import re
import json
from pathlib import Path


def normalize_for_search(text):
    """Normalize text for searching (less aggressive than alignment normalization)."""
    # Replace periods with spaces (ZL uses periods as separators)
    text = text.replace(".", " ")
    # Remove special chars but keep letters
    text = re.sub(r"[<>{}[\]()!?;:\-@$%*]", " ", text)
    # Lowercase and remove extra spaces
    return " ".join(text.lower().split())


def search_zl_for_text(search_string, context_words=10):
    """Search ZL transcription for a specific text string."""
    zl_path = (
        Path(__file__).parent.parent.parent
        / "data"
        / "voynich"
        / "eva_transcription"
        / "ZL3b-n.txt"
    )

    with open(zl_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    search_normalized = normalize_for_search(search_string)
    current_folio = "Unknown"
    results = []

    for i, line in enumerate(lines):
        line_stripped = line.strip()

        # Track current folio
        if (
            line_stripped.startswith("<f")
            and ">" in line_stripped
            and "," not in line_stripped.split(">")[0]
        ):
            folio_match = re.match(r"<(f\d+[rv])>", line_stripped)
            if folio_match:
                current_folio = folio_match.group(1)

        # Extract text from line
        if "," in line_stripped and ">" in line_stripped:
            parts = line_stripped.split(">")
            if len(parts) >= 2:
                text = parts[-1]
                text_normalized = normalize_for_search(text)

                # Check if search string is in this line
                if search_normalized in text_normalized:
                    # Get context (previous and next lines)
                    context_before = []
                    context_after = []

                    for j in range(max(0, i - context_words), i):
                        if "," in lines[j] and ">" in lines[j]:
                            context_before.append(lines[j].split(">")[-1].strip())

                    for j in range(i + 1, min(len(lines), i + context_words + 1)):
                        if "," in lines[j] and ">" in lines[j]:
                            context_after.append(lines[j].split(">")[-1].strip())

                    results.append(
                        {
                            "folio": current_folio,
                            "line_number": i,
                            "line": line_stripped,
                            "text": text,
                            "context_before": context_before,
                            "context_after": context_after,
                        }
                    )

    return results


def main():
    print("=" * 80)
    print("MANUAL FOLIO SEARCH - Verifying Alignment")
    print("=" * 80)
    print()

    # Load section data
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"

    with open(results_dir / "section_medical_density.json", "r", encoding="utf-8") as f:
        sections = json.load(f)

    # Get high-density sections
    high_density = sorted(
        [s for s in sections if s["density_percent"] >= 1.0],
        key=lambda x: x["density_percent"],
        reverse=True,
    )[:5]  # Top 5

    print("Searching for top 5 highest medical density sections...")
    print()

    search_results = {}

    for section in high_density:
        section_id = section["section_id"]
        first_words = section["first_words"]

        print(f"Section {section_id} (Density: {section['density_percent']:.1f}%)")
        print(f"Searching for: '{first_words[:60]}...'")

        # Try searching for first 20-30 characters
        search_strings = [
            " ".join(first_words.split()[:3]),  # First 3 words
            " ".join(first_words.split()[:4]),  # First 4 words
            " ".join(first_words.split()[:5]),  # First 5 words
        ]

        found = False
        for search_str in search_strings:
            results = search_zl_for_text(search_str)
            if results:
                result = results[0]  # Take first match
                print(f"  ✓ Found in folio: {result['folio']}")
                print(f"    Line: {result['text'][:70]}...")
                search_results[section_id] = result
                found = True
                break

        if not found:
            print(f"  ✗ Not found - trying partial match...")
            # Try just first 2 words
            partial = " ".join(first_words.split()[:2])
            results = search_zl_for_text(partial)
            if results:
                print(f"  ⚠ Partial match in folio: {results[0]['folio']}")
                search_results[section_id] = results[0]
            else:
                print(f"  ✗ No match found")
                search_results[section_id] = None

        print()

    # Compare with automatic alignment
    print("=" * 80)
    print("COMPARISON: Manual Search vs Automatic Alignment")
    print("=" * 80)
    print()

    try:
        with open(
            results_dir / "section_to_folio_mapping.json", "r", encoding="utf-8"
        ) as f:
            auto_mapping = json.load(f)
    except:
        auto_mapping = []

    for section_id, manual_result in search_results.items():
        auto_result = next(
            (s for s in auto_mapping if s["section_id"] == section_id), None
        )

        print(f"Section {section_id}:")

        if manual_result:
            print(f"  Manual search:     {manual_result['folio']}")
        else:
            print(f"  Manual search:     NOT FOUND")

        if auto_result:
            auto_folios = (
                ", ".join(auto_result["folios"]) if auto_result["folios"] else "NONE"
            )
            print(f"  Auto alignment:    {auto_folios}")
        else:
            print(f"  Auto alignment:    NOT FOUND")

        # Check if they match
        if manual_result and auto_result:
            manual_folio = manual_result["folio"]
            if manual_folio in auto_result["folios"]:
                print(f"  ✓ MATCH")
            else:
                print(f"  ✗ MISMATCH")
        print()

    # Save manual search results
    output = {
        "search_date": "2025-10-29",
        "method": "manual_text_search",
        "results": search_results,
    }

    output_path = results_dir / "manual_folio_search_results.json"

    # Convert for JSON serialization
    json_output = {
        "search_date": output["search_date"],
        "method": output["method"],
        "results": {},
    }

    for section_id, result in search_results.items():
        if result:
            json_output["results"][str(section_id)] = {
                "folio": result["folio"],
                "line_number": result["line_number"],
                "text_found": result["text"][:100],
            }
        else:
            json_output["results"][str(section_id)] = None

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_output, f, indent=2)

    print("=" * 80)
    print(f"Results saved to: {output_path}")
    print("=" * 80)
    print()

    # Print critical finding for Section 4
    if 4 in search_results and search_results[4]:
        print("=" * 80)
        print("CRITICAL FINDING: Section 4 (Highest Medical Density)")
        print("=" * 80)
        print()
        print(f"Manual search found Section 4 in: {search_results[4]['folio']}")
        print()
        print("NEXT STEP:")
        print(f"1. View folio {search_results[4]['folio']} in Yale Beinecke scans")
        print("2. Look for wound-healing plants (plantain, betony, yarrow)")
        print("3. Document what illustration is actually there")
        print()
        print("This is the critical validation test!")


if __name__ == "__main__":
    main()
