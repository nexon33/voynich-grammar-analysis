#!/usr/bin/env python3
"""
Option 3: Generate Readable Passages

Extract high-density sections and create partial translations
"""

import json
from collections import defaultdict
from pathlib import Path


def load_all_recognized_words():
    """Load all recognized words from Phase 4A."""

    # From exhaustive search
    with open("results/phase4/exhaustive_search_results.json", "r") as f:
        exhaustive = json.load(f)

    # From partial matches
    with open("results/phase4/compound_and_partial_matches.json", "r") as f:
        partial_data = json.load(f)

    # Create mapping: voynich_word -> meaning
    word_meanings = {}

    for result in exhaustive:
        word_meanings[result["voynich_word"]] = {
            "meaning": result["meaning"],
            "me_word": result["me_word"],
            "category": result["category"],
            "source": "exact",
        }

    for pm in partial_data["partial_matches"]:
        if pm["voynich_word"] not in word_meanings:  # Don't override exact matches
            # For partial matches, show the root
            word_meanings[pm["voynich_word"]] = {
                "meaning": pm["meaning"],
                "me_word": pm["me_word"],
                "category": pm["category"],
                "root": pm["me_variant"],
                "prefix": pm["prefix"],
                "suffix": pm["suffix"],
                "source": "partial",
            }

    return word_meanings


def load_folio_mappings():
    """Load Phase 3 folio mappings."""
    with open("results/phase3/proper_section_to_folio_mapping.json", "r") as f:
        return json.load(f)


def load_voynich_words():
    """Load Voynich text."""
    with open(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt",
        "r",
        encoding="utf-8",
    ) as f:
        return f.read().split()


def extract_folio_words(words, folio_mappings, target_folio):
    """Extract all words from a specific folio."""

    folio_words = []

    for section in folio_mappings:
        if section["primary_folio"] == target_folio:
            start, end = map(int, section["word_range"].split("-"))
            folio_words = words[start:end]
            break

    return folio_words


def calculate_recognition_density(words, word_meanings):
    """Calculate what % of words we recognize."""
    recognized = sum(1 for w in words if w.lower() in word_meanings)
    return (recognized / len(words) * 100) if words else 0


def find_high_density_folios(words, folio_mappings, word_meanings, min_density=15.0):
    """Find folios with high recognition density."""

    folio_densities = []

    for section in folio_mappings:
        folio = section["primary_folio"]
        start, end = map(int, section["word_range"].split("-"))
        folio_words = words[start:end]

        if len(folio_words) < 20:  # Skip very short sections
            continue

        density = calculate_recognition_density(folio_words, word_meanings)

        if density >= min_density:
            folio_densities.append(
                {
                    "folio": folio,
                    "density": density,
                    "word_count": len(folio_words),
                    "recognized_count": sum(
                        1 for w in folio_words if w.lower() in word_meanings
                    ),
                }
            )

    return sorted(folio_densities, key=lambda x: x["density"], reverse=True)


def translate_passage(words, word_meanings, show_unknown=True):
    """
    Translate a passage, showing recognized words.

    Format:
    - KNOWN words: show meaning
    - Unknown words: show [?] or actual Voynich word
    """

    translation = []

    for word in words:
        word_lower = word.lower()

        if word_lower in word_meanings:
            info = word_meanings[word_lower]

            if info["source"] == "exact":
                # Exact match - show meaning
                translation.append(info["meaning"])
            else:
                # Partial match - show root meaning + affixes
                root = info["meaning"]
                prefix = f"[{info['prefix']}-]" if info["prefix"] else ""
                suffix = f"[-{info['suffix']}]" if info["suffix"] else ""
                translation.append(f"{prefix}{root}{suffix}")
        else:
            if show_unknown:
                translation.append(f"[{word}]")
            else:
                translation.append("[?]")

    return translation


def format_translation_output(words, translation, words_per_line=10):
    """Format translation for readable output."""

    lines = []

    for i in range(0, len(words), words_per_line):
        chunk_words = words[i : i + words_per_line]
        chunk_trans = translation[i : i + words_per_line]

        # Original Voynich
        voynich_line = " ".join(chunk_words)
        # Translation
        trans_line = " ".join(chunk_trans)

        lines.append(f"Voynich: {voynich_line}")
        lines.append(f"Meaning: {trans_line}")
        lines.append("")

    return "\n".join(lines)


def main():
    print("=" * 80)
    print("OPTION 3: GENERATE READABLE PASSAGES")
    print("=" * 80)

    # Load data
    print("\nLoading recognized words...")
    word_meanings = load_all_recognized_words()
    print(f"Total recognized words: {len(word_meanings)}")

    folio_mappings = load_folio_mappings()
    words = load_voynich_words()

    # Find high-density folios
    print("\nFinding high-density folios (>15% recognition)...")
    high_density = find_high_density_folios(
        words, folio_mappings, word_meanings, min_density=15.0
    )

    print(f"\nFound {len(high_density)} folios with >15% recognition:")
    for fd in high_density[:20]:
        print(
            f"  {fd['folio']}: {fd['density']:.1f}% ({fd['recognized_count']}/{fd['word_count']} words)"
        )

    # Generate translations for top folios
    print("\n" + "=" * 80)
    print("READABLE PASSAGES")
    print("=" * 80)

    output_dir = Path("results/phase4/readable_passages")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Translate top 5 folios
    for i, fd in enumerate(high_density[:5]):
        folio = fd["folio"]
        density = fd["density"]

        print(f"\n" + "-" * 80)
        print(f"FOLIO {folio} ({density:.1f}% recognition)")
        print("-" * 80)

        # Extract words
        folio_words = extract_folio_words(words, folio_mappings, folio)

        # Translate
        translation = translate_passage(folio_words, word_meanings, show_unknown=False)

        # Show first 50 words
        print(f"\nFirst 50 words:")
        formatted = format_translation_output(
            folio_words[:50], translation[:50], words_per_line=8
        )
        print(formatted)

        # Save full translation
        full_formatted = format_translation_output(
            folio_words, translation, words_per_line=10
        )

        output_file = output_dir / f"{folio}_translation.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"FOLIO {folio} - PARTIAL TRANSLATION\n")
            f.write(f"Recognition rate: {density:.1f}%\n")
            f.write(f"Total words: {len(folio_words)}\n")
            f.write(f"Recognized: {fd['recognized_count']}\n")
            f.write("=" * 80 + "\n\n")
            f.write(full_formatted)

        print(f"\nFull translation saved to: {output_file}")

    # Special focus on f84v (the oak/oat bath folio)
    print("\n" + "=" * 80)
    print("SPECIAL FOCUS: FOLIO f84v (OAK/OAT BATH FOLIO)")
    print("=" * 80)

    f84v_words = extract_folio_words(words, folio_mappings, "f84v")

    if f84v_words:
        print(f"\nTotal words: {len(f84v_words)}")

        density = calculate_recognition_density(f84v_words, word_meanings)
        print(f"Recognition: {density:.1f}%")

        # Count oak/oat specifically
        oak_variants = {
            "okedy",
            "okeedy",
            "qokey",
            "qokol",
            "okol",
            "okeol",
            "okey",
            "okeody",
            "oko",
            "oke",
        }
        oat_variants = {
            "oteey",
            "oteedy",
            "qotedy",
            "otol",
            "qoteedy",
            "oteol",
            "oteody",
            "oto",
            "ote",
        }

        oak_count = sum(1 for w in f84v_words if w.lower() in oak_variants)
        oat_count = sum(1 for w in f84v_words if w.lower() in oat_variants)

        print(f"Oak instances: {oak_count}")
        print(f"Oat instances: {oat_count}")
        print(
            f"Combined: {oak_count + oat_count} ({100 * (oak_count + oat_count) / len(f84v_words):.1f}% of folio)"
        )

        # Translate
        translation = translate_passage(f84v_words, word_meanings, show_unknown=True)

        print(f"\nFirst 80 words (with Voynich text for unknown words):")
        formatted = format_translation_output(
            f84v_words[:80], translation[:80], words_per_line=8
        )
        print(formatted)

        # Save full translation
        output_file = output_dir / "f84v_oak_oat_bath_folio.txt"
        full_formatted = format_translation_output(
            f84v_words, translation, words_per_line=10
        )

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("FOLIO f84v - THE OAK/OAT BATH FOLIO\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Recognition rate: {density:.1f}%\n")
            f.write(f"Total words: {len(f84v_words)}\n")
            f.write(f"Oak instances: {oak_count}\n")
            f.write(f"Oat instances: {oat_count}\n")
            f.write(
                f"Other recognized: {int(len(f84v_words) * density / 100) - oak_count - oat_count}\n\n"
            )
            f.write(
                "CONTEXT: This folio shows circular pools with naked figures (bathing scenes).\n"
            )
            f.write(
                "HYPOTHESIS: Bath recipes using oak bark and oat as medicinal ingredients.\n"
            )
            f.write("=" * 80 + "\n\n")
            f.write(full_formatted)

        print(f"\nFull f84v translation saved to: {output_file}")
    else:
        print("\n(f84v not found in folio mappings)")

    print("\n" + "=" * 80)
    print("PASSAGE GENERATION COMPLETE")
    print("=" * 80)
    print(
        f"\nGenerated translations for {min(5, len(high_density))} high-density folios"
    )
    print(f"All translations saved to: {output_dir}/")


if __name__ == "__main__":
    main()
