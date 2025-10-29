#!/usr/bin/env python3
"""
Map our translated sections to actual Voynich manuscript folios.
This helps us correlate medical term density with specific illustrations.
"""

import json
from pathlib import Path


def create_folio_mapping_guide():
    """
    Create a guide for manually mapping sections to folios.
    Since our Takahashi transcription doesn't have folio markers,
    we need to use external resources to map word positions to pages.
    """

    # Load our section data
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"

    with open(results_dir / "section_medical_density.json", "r", encoding="utf-8") as f:
        sections = json.load(f)

    # Get high-density sections
    high_density = [s for s in sections if s["density_percent"] >= 1.0]
    high_density.sort(key=lambda x: x["density_percent"], reverse=True)

    output_path = results_dir / "FOLIO_MAPPING_GUIDE.md"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Folio Mapping Guide: High Medical Density Sections\n\n")
        f.write("## Purpose\n\n")
        f.write(
            "This guide helps map our translated sections to actual Voynich manuscript folios,\n"
        )
        f.write(
            "allowing us to test whether medical term density correlates with specific illustration types.\n\n"
        )

        f.write("## How to Use This Guide\n\n")
        f.write("1. **Access the Voynich manuscript**:\n")
        f.write(
            "   - Yale Beinecke Library: https://brbl-dl.library.yale.edu/vufind/Record/3519597\n"
        )
        f.write("   - Voynich.nu (with transcription): http://www.voynich.nu/\n\n")

        f.write("2. **Find the first words** of each section below in the manuscript\n")
        f.write("3. **Note the folio number** (e.g., f1r, f3v, f78r)\n")
        f.write("4. **Record the illustration type** on that folio\n")
        f.write("5. **Test the correlation**:\n")
        f.write("   - Do high 'sor' sections show wound-healing plants?\n")
        f.write(
            "   - Do body-part sections correspond to anatomical illustrations?\n\n"
        )

        f.write("## High-Density Sections to Map\n\n")
        f.write("### Section Priority: Top 10 Highest Medical Density\n\n")

        for i, section in enumerate(high_density[:10], 1):
            f.write(
                f"#### {i}. Section #{section['section_id']} - Density: {section['density_percent']:.1f}%\n\n"
            )

            # Word range
            word_start = section["section_id"] * 500
            word_end = word_start + section["word_count"]
            f.write(f"**Word Range:** {word_start}-{word_end}\n\n")

            # First words to search for
            f.write(f"**Search for these words in manuscript:**\n")
            f.write(f"```\n{section['first_words']}\n```\n\n")

            # Medical terms found
            f.write(f"**Medical Terms Found ({section['medical_term_count']}):**\n")
            for match in section["medical_matches"][:5]:  # Show first 5
                f.write(
                    f"- `{match['voynich']}` → {match['medical_term']} ({match['category']})\n"
                )
            if len(section["medical_matches"]) > 5:
                f.write(f"- ... and {len(section['medical_matches']) - 5} more\n")
            f.write("\n")

            # Categories
            f.write(f"**Category Breakdown:**\n")
            for cat, count in section["category_counts"].items():
                f.write(f"- {cat}: {count}\n")
            f.write("\n")

            # Expected illustration
            f.write(f"**Expected Illustration Type:**\n")
            if "sor" in [m["medical_term"] for m in section["medical_matches"]]:
                f.write(
                    "- Likely: Wound-healing plant (plantain, betony, yarrow, woundwort)\n"
                )
            if section["category_counts"].get("body_parts", 0) > 3:
                f.write("- Possibly: Anatomical diagram or bathing/therapeutic scene\n")
            if section["category_counts"].get("treatments", 0) > 0:
                f.write(
                    "- Possibly: Pharmaceutical jars, vessels, or preparation tools\n"
                )
            f.write("\n")

            # Mapping template
            f.write("**YOUR MAPPING:**\n")
            f.write("```\n")
            f.write("Folio number: ________________\n")
            f.write("Illustration type: ________________\n")
            f.write("Plant/subject (if identifiable): ________________\n")
            f.write("Notes: ________________\n")
            f.write("```\n\n")

            f.write("-" * 80 + "\n\n")

        # Add resources section
        f.write("## Resources for Mapping\n\n")
        f.write("### Online Transcriptions with Folio Markers:\n\n")
        f.write("1. **Voynich.nu Interlinear**\n")
        f.write("   - http://www.voynich.nu/transcr.html\n")
        f.write("   - Has folio markers alongside EVA transcription\n\n")

        f.write("2. **René Zandbergen's Reference**\n")
        f.write("   - http://www.voynich.nu/folios.html\n")
        f.write("   - Detailed folio descriptions with illustrations\n\n")

        f.write("3. **Jason Davies Interactive**\n")
        f.write("   - https://www.jasondavies.com/voynich/\n")
        f.write("   - Searchable transcription with images\n\n")

        f.write("### How to Map Word Positions:\n\n")
        f.write(
            "Our sections are based on sequential word count from the Takahashi transcription.\n"
        )
        f.write("To find which folio corresponds to Section N:\n\n")
        f.write("1. Calculate word position: Section N × 500 words\n")
        f.write(
            "2. Search for the 'first_words' string in a folio-marked transcription\n"
        )
        f.write("3. Note which folio (f1r, f2v, etc.) contains that text\n")
        f.write("4. View that folio's illustration in the Yale scans\n\n")

        f.write("### Plant Identification Resources:\n\n")
        f.write("Once you have the folios, compare plants against:\n\n")
        f.write("1. **Medieval Herbal References:**\n")
        f.write("   - British Library MS Sloane 1975 (online)\n")
        f.write("   - Bodleian MS Ashmole 1431\n\n")

        f.write("2. **Modern Plant Guides:**\n")
        f.write("   - Medieval Plants Database: http://medieval-plants.org/\n")
        f.write("   - Botanical illustrations from 1400-1500\n\n")

        f.write("## Validation Criteria\n\n")
        f.write("**Strong confirmation if:**\n")
        f.write("- Section 4 (highest 'sor') → folio shows wound-healing plant\n")
        f.write("- Section 24 (sor + body parts) → folio shows medicinal plant\n")
        f.write("- Section 51 (conditions) → folio shows therapeutic scene\n\n")

        f.write("**Weak/no confirmation if:**\n")
        f.write("- High medical density sections → random plant types\n")
        f.write("- No correlation between terms and illustration content\n")
        f.write(
            "- Contradictory evidence (e.g., astronomical diagrams in herbal sections)\n\n"
        )

        f.write("## Next Steps After Mapping\n\n")
        f.write("Once you've identified the folios:\n\n")
        f.write("1. **Document the correlations** in this file\n")
        f.write("2. **Photograph/screenshot** the relevant folios\n")
        f.write("3. **Create a correlation table** showing:\n")
        f.write("   - Section → Folio → Illustration → Medical terms → Match?\n")
        f.write("4. **Calculate correlation coefficient**:\n")
        f.write("   - How often do medical terms match illustration content?\n")
        f.write("   - Statistical significance of the correlation\n\n")

        f.write("---\n\n")
        f.write("*Generated: 2025-10-29*\n")
        f.write("*Purpose: Enable visual-textual correlation testing*\n")
        f.write("*Critical step: Independent validation of translation hypothesis*\n")

    return output_path


def main():
    print("Creating folio mapping guide...")
    output_path = create_folio_mapping_guide()
    print(f"Guide created: {output_path}")
    print()
    print("Next steps:")
    print("1. Use the guide to map sections to folios")
    print("2. Examine the illustrations on those folios")
    print("3. Test whether medical terms correlate with illustration content")
    print()
    print("This is the critical validation step!")


if __name__ == "__main__":
    main()
