#!/usr/bin/env python3
"""
Extract the most readable sentences from the translation.
Focus on high-confidence translations to see what the manuscript actually says!
"""

import json
from pathlib import Path
from collections import defaultdict


def analyze_translation_quality(translation_file):
    """
    Analyze translation and extract best sentences.
    """
    print("=" * 80)
    print("EXTRACTING READABLE CONTENT FROM VOYNICH MANUSCRIPT")
    print("=" * 80)

    with open(translation_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Group sentences by recognition rate
    recognition_tiers = {
        "perfect": [],  # 100% recognition
        "excellent": [],  # 90-99%
        "good": [],  # 80-89%
        "moderate": [],  # 70-79%
        "fair": [],  # 60-69%
        "poor": [],  # <60%
    }

    for trans in data["translations"]:
        rec_rate = trans["statistics"]["recognition_rate"]

        if rec_rate == 100:
            recognition_tiers["perfect"].append(trans)
        elif rec_rate >= 90:
            recognition_tiers["excellent"].append(trans)
        elif rec_rate >= 80:
            recognition_tiers["good"].append(trans)
        elif rec_rate >= 70:
            recognition_tiers["moderate"].append(trans)
        elif rec_rate >= 60:
            recognition_tiers["fair"].append(trans)
        else:
            recognition_tiers["poor"].append(trans)

    # Print statistics
    print(f"\nTotal sentences: {data['metadata']['total_sentences']}")
    print(
        f"Overall recognition: {data['statistics'].get('overall_recognition_rate', 0):.1f}%"
    )
    print("\nRecognition tier breakdown:")
    print(f"  Perfect (100%):    {len(recognition_tiers['perfect'])} sentences")
    print(f"  Excellent (90-99%): {len(recognition_tiers['excellent'])} sentences")
    print(f"  Good (80-89%):      {len(recognition_tiers['good'])} sentences")
    print(f"  Moderate (70-79%):  {len(recognition_tiers['moderate'])} sentences")
    print(f"  Fair (60-69%):      {len(recognition_tiers['fair'])} sentences")
    print(f"  Poor (<60%):        {len(recognition_tiers['poor'])} sentences")

    return recognition_tiers, data


def extract_readable_sentences(recognition_tiers, output_file, limit_per_tier=50):
    """
    Extract most readable sentences and write to file.
    """
    print(f"\nExtracting top sentences to {output_file}...")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("VOYNICH MANUSCRIPT - READABLE CONTENT\n")
        f.write("=" * 80 + "\n")
        f.write("Extracted: Highest-confidence translations\n")
        f.write("Purpose: To see what the manuscript actually says!\n")
        f.write("=" * 80 + "\n\n")

        # Perfect translations
        if recognition_tiers["perfect"]:
            f.write("\n" + "=" * 80 + "\n")
            f.write(
                f"PERFECT TRANSLATIONS (100% recognized) - {len(recognition_tiers['perfect'])} sentences\n"
            )
            f.write("=" * 80 + "\n\n")

            for i, trans in enumerate(recognition_tiers["perfect"][:limit_per_tier], 1):
                f.write(f"{i}. [{trans['folio']}]\n")
                f.write(f"   Original:    {trans['original']}\n")
                f.write(f"   Translation: {trans['final_translation']}\n\n")

        # Excellent translations
        if recognition_tiers["excellent"]:
            f.write("\n" + "=" * 80 + "\n")
            f.write(
                f"EXCELLENT TRANSLATIONS (90-99% recognized) - {len(recognition_tiers['excellent'])} sentences\n"
            )
            f.write("=" * 80 + "\n\n")

            # Sort by recognition rate descending
            excellent_sorted = sorted(
                recognition_tiers["excellent"],
                key=lambda x: x["statistics"]["recognition_rate"],
                reverse=True,
            )

            for i, trans in enumerate(excellent_sorted[:limit_per_tier], 1):
                f.write(
                    f"{i}. [{trans['folio']}] ({trans['statistics']['recognition_rate']:.0f}%)\n"
                )
                f.write(f"   Original:    {trans['original']}\n")
                f.write(f"   Translation: {trans['final_translation']}\n\n")

        # Good translations
        if recognition_tiers["good"]:
            f.write("\n" + "=" * 80 + "\n")
            f.write(
                f"GOOD TRANSLATIONS (80-89% recognized) - {len(recognition_tiers['good'])} sentences\n"
            )
            f.write("=" * 80 + "\n\n")

            good_sorted = sorted(
                recognition_tiers["good"],
                key=lambda x: x["statistics"]["recognition_rate"],
                reverse=True,
            )

            for i, trans in enumerate(good_sorted[:limit_per_tier], 1):
                f.write(
                    f"{i}. [{trans['folio']}] ({trans['statistics']['recognition_rate']:.0f}%)\n"
                )
                f.write(f"   Original:    {trans['original']}\n")
                f.write(f"   Translation: {trans['final_translation']}\n\n")

        # Moderate translations (sample)
        if recognition_tiers["moderate"]:
            f.write("\n" + "=" * 80 + "\n")
            f.write(
                f"MODERATE TRANSLATIONS (70-79% recognized) - Sample of {min(20, len(recognition_tiers['moderate']))}\n"
            )
            f.write("=" * 80 + "\n\n")

            moderate_sorted = sorted(
                recognition_tiers["moderate"],
                key=lambda x: x["statistics"]["recognition_rate"],
                reverse=True,
            )

            for i, trans in enumerate(moderate_sorted[:20], 1):
                f.write(
                    f"{i}. [{trans['folio']}] ({trans['statistics']['recognition_rate']:.0f}%)\n"
                )
                f.write(f"   Original:    {trans['original']}\n")
                f.write(f"   Translation: {trans['final_translation']}\n\n")

    print(f"Readable content extracted to: {output_file}")


def find_patterns(recognition_tiers, data):
    """
    Look for patterns in readable sentences.
    """
    print("\n" + "=" * 80)
    print("PATTERN ANALYSIS")
    print("=" * 80)

    # Combine perfect and excellent for analysis
    high_quality = recognition_tiers["perfect"] + recognition_tiers["excellent"]

    # Count word usage in high-quality translations
    word_usage = defaultdict(int)
    for trans in high_quality:
        words = trans["final_translation"].split()
        for word in words:
            word_usage[word] += 1

    print(f"\nMost common words in high-quality translations:")
    for word, count in sorted(word_usage.items(), key=lambda x: x[1], reverse=True)[
        :30
    ]:
        print(f"  {word}: {count}")

    # Look for repeated phrases
    print("\nLooking for repeated phrases...")
    phrase_usage = defaultdict(int)
    for trans in high_quality:
        words = trans["final_translation"].split()
        # Check 2-word phrases
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i + 1]}"
            phrase_usage[phrase] += 1

    print(f"\nMost common 2-word phrases:")
    for phrase, count in sorted(phrase_usage.items(), key=lambda x: x[1], reverse=True)[
        :20
    ]:
        if count >= 3:  # Only show if appears 3+ times
            print(f'  "{phrase}": {count} times')


def main():
    # Paths
    script_dir = Path(__file__).parent
    manuscript_dir = script_dir.parent.parent

    # Check for Phase 16 translation first, fall back to original
    phase16_file = manuscript_dir / "COMPLETE_MANUSCRIPT_TRANSLATION_PHASE16.json"
    original_file = manuscript_dir / "COMPLETE_MANUSCRIPT_TRANSLATION.json"

    if phase16_file.exists():
        translation_file = phase16_file
        output_file = manuscript_dir / "READABLE_CONTENT_PHASE16.txt"
        print("Using Phase 16 translation (with t- and -d morphemes)")
    elif original_file.exists():
        translation_file = original_file
        output_file = manuscript_dir / "READABLE_CONTENT.txt"
        print("Using original translation")
    else:
        print("Error: No translation file found!")
        return

    print(f"Loading translation from: {translation_file}\n")

    # Analyze
    recognition_tiers, data = analyze_translation_quality(translation_file)

    # Extract readable sentences
    extract_readable_sentences(recognition_tiers, output_file)

    # Find patterns
    find_patterns(recognition_tiers, data)

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)
    print(f"\nReadable content saved to: {output_file}")
    print("\nNow you can read the best translations and see what the manuscript says!")


if __name__ == "__main__":
    main()
