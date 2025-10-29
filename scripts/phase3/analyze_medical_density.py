"""
Analyze Medical Term Density Across Voynich Sections

Find which sections have the highest concentration of medical vocabulary.
These are likely recipe/treatment sections.
"""

from pathlib import Path
import json
import re
from collections import defaultdict


def load_medical_vocabulary():
    """Load medical vocabulary database."""
    vocab_file = Path("results/phase3/medical_vocabulary_database.json")
    with open(vocab_file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_voynich_text():
    """Load Voynich text."""
    voynich_file = Path("data/voynich/eva_transcription/voynich_eva_takahashi.txt")
    with open(voynich_file, "r", encoding="utf-8") as f:
        return f.read().lower()


def generate_eo_variants(word):
    """Generate e↔o variants for a word."""
    from itertools import product

    # Find all positions with 'e' or 'o'
    eo_positions = []
    for i, char in enumerate(word):
        if char in ["e", "o"]:
            eo_positions.append(i)

    if not eo_positions:
        return [word]

    # Generate all combinations
    variants = []
    for combination in product(["e", "o"], repeat=len(eo_positions)):
        variant = list(word)
        for pos_idx, char_choice in enumerate(combination):
            variant[eo_positions[pos_idx]] = char_choice
        variants.append("".join(variant))

    return list(set(variants))


def split_into_sections(text, section_size=500):
    """
    Split Voynich text into sections of approximately section_size words.
    """
    words = re.findall(r"[a-z]+", text)

    sections = []
    current_section = []

    for word in words:
        current_section.append(word)
        if len(current_section) >= section_size:
            sections.append(current_section)
            current_section = []

    # Add remaining words
    if current_section:
        sections.append(current_section)

    return sections


def find_medical_terms_in_section(section_words, medical_vocab_flat):
    """
    Find medical terms in a section.
    Returns list of (voynich_word, medical_term, category, frequency).
    """
    matches = []

    for voyn_word in section_words:
        # Generate variants
        variants = generate_eo_variants(voyn_word)

        # Check if any variant is medical
        for variant in variants:
            if variant in medical_vocab_flat:
                matches.append(
                    {
                        "voynich": voyn_word,
                        "medical_term": variant,
                        "category": medical_vocab_flat[variant]["category"],
                        "me_frequency": medical_vocab_flat[variant]["me_frequency"],
                    }
                )
                break  # Only count once per word

    return matches


def main():
    print("\n" + "=" * 70)
    print("MEDICAL TERM DENSITY ANALYSIS")
    print("=" * 70 + "\n")

    # Load data
    print("Loading data...")
    medical_vocab = load_medical_vocabulary()
    voynich_text = load_voynich_text()

    # Flatten medical vocabulary for searching
    medical_vocab_flat = {}
    for category, terms in medical_vocab.items():
        for term_info in terms:
            medical_vocab_flat[term_info["word"]] = {
                "category": category,
                "me_frequency": term_info["frequency"],
            }

    print(f"✓ Loaded {len(medical_vocab_flat):,} medical terms")
    print(f"✓ Loaded Voynich text ({len(voynich_text):,} characters)\n")

    # Split into sections
    print("Splitting Voynich into sections...")
    sections = split_into_sections(voynich_text, section_size=500)
    print(f"✓ Created {len(sections)} sections (~500 words each)\n")

    # Analyze each section
    print("Analyzing medical term density in each section...")
    print("(This may take a minute...)\n")

    section_analysis = []

    for i, section_words in enumerate(sections):
        # Find medical terms
        medical_matches = find_medical_terms_in_section(
            section_words, medical_vocab_flat
        )

        # Calculate density
        density = len(medical_matches) / len(section_words) * 100

        # Count by category
        category_counts = defaultdict(int)
        for match in medical_matches:
            category_counts[match["category"]] += 1

        section_analysis.append(
            {
                "section_id": i,
                "word_count": len(section_words),
                "medical_term_count": len(medical_matches),
                "density_percent": density,
                "category_counts": dict(category_counts),
                "medical_matches": medical_matches,
                "first_words": " ".join(section_words[:10]),  # Preview
            }
        )

        if (i + 1) % 20 == 0:
            print(f"  Processed {i + 1}/{len(sections)} sections...")

    print(f"✓ Analysis complete!\n")

    # Sort by density (highest first)
    section_analysis.sort(key=lambda x: x["density_percent"], reverse=True)

    # Display results
    print("=" * 70)
    print("TOP 20 SECTIONS BY MEDICAL TERM DENSITY")
    print("=" * 70 + "\n")

    print(
        f"{'Rank':<6} {'Section':<10} {'Words':<8} {'Medical':<10} {'Density':<10} {'Top Categories'}"
    )
    print("-" * 70)

    for rank, section in enumerate(section_analysis[:20], 1):
        section_id = section["section_id"]
        word_count = section["word_count"]
        med_count = section["medical_term_count"]
        density = section["density_percent"]

        # Top 2 categories
        top_cats = sorted(
            section["category_counts"].items(), key=lambda x: x[1], reverse=True
        )[:2]
        cat_str = ", ".join([f"{cat}({count})" for cat, count in top_cats])

        print(
            f"{rank:<6} {section_id:<10} {word_count:<8} {med_count:<10} {density:>6.2f}%    {cat_str}"
        )

    # Show details for top 5 sections
    print("\n" + "=" * 70)
    print("DETAILED ANALYSIS: TOP 5 HIGHEST DENSITY SECTIONS")
    print("=" * 70)

    for rank, section in enumerate(section_analysis[:5], 1):
        print(f"\n{'=' * 70}")
        print(f"SECTION #{section['section_id']} (Rank {rank})")
        print(f"{'=' * 70}")
        print(f"Words: {section['word_count']}")
        print(f"Medical terms: {section['medical_term_count']}")
        print(f"Density: {section['density_percent']:.2f}%")
        print()

        print(f"Preview (first 10 words):")
        print(f"  {section['first_words']}")
        print()

        print(f"Medical term breakdown by category:")
        for category, count in sorted(
            section["category_counts"].items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  {category.replace('_', ' ').title()}: {count} terms")

        print()
        print(f"Medical terms found (top 15):")
        matches = section["medical_matches"][:15]
        for match in matches:
            print(
                f"  {match['voynich']:15} → {match['medical_term']:15} ({match['category']})"
            )

    # Statistics
    print("\n" + "=" * 70)
    print("OVERALL STATISTICS")
    print("=" * 70 + "\n")

    densities = [s["density_percent"] for s in section_analysis]
    avg_density = sum(densities) / len(densities)
    max_density = max(densities)
    min_density = min(densities)

    print(f"Average medical term density: {avg_density:.2f}%")
    print(f"Maximum density: {max_density:.2f}%")
    print(f"Minimum density: {min_density:.2f}%")
    print()

    # Sections with high density (> 2x average)
    high_density = [
        s for s in section_analysis if s["density_percent"] > avg_density * 2
    ]
    print(f"Sections with HIGH density (> 2x average): {len(high_density)}")
    print(f"  These are likely recipe/treatment sections!")
    print()

    # Category distribution across all sections
    all_categories = defaultdict(int)
    for section in section_analysis:
        for category, count in section["category_counts"].items():
            all_categories[category] += count

    print("Medical term distribution across entire manuscript:")
    for category, count in sorted(
        all_categories.items(), key=lambda x: x[1], reverse=True
    ):
        print(f"  {category.replace('_', ' ').title()}: {count} terms")

    # Save results
    output_dir = Path("results/phase3")

    # Save section analysis
    analysis_file = output_dir / "section_medical_density.json"
    with open(analysis_file, "w", encoding="utf-8") as f:
        json.dump(section_analysis, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Section analysis saved to: {analysis_file}")

    # Save high-density sections for translation
    high_density_file = output_dir / "high_density_sections.txt"
    with open(high_density_file, "w", encoding="utf-8") as f:
        f.write("HIGH MEDICAL TERM DENSITY SECTIONS\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"These sections likely contain medical recipes/treatments\n")
        f.write(f"Threshold: > {avg_density * 2:.2f}% (2x average)\n\n")

        for section in high_density:
            f.write(f"\nSection #{section['section_id']}:\n")
            f.write(f"  Density: {section['density_percent']:.2f}%\n")
            f.write(f"  Medical terms: {section['medical_term_count']}\n")
            f.write(f"  Preview: {section['first_words']}\n")
            f.write(f"  Categories: {section['category_counts']}\n")

    print(f"✓ High-density sections saved to: {high_density_file}")

    # Recommendations
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS FOR PHASE 3 TRANSLATION")
    print("=" * 70 + "\n")

    print(f"1. Focus on the top {len(high_density)} high-density sections")
    print(f"   These have >2x average medical term density")
    print()
    print(f"2. Start with Section #{section_analysis[0]['section_id']}")
    print(f"   Highest density: {section_analysis[0]['density_percent']:.2f}%")
    print(f"   Contains: {section_analysis[0]['medical_term_count']} medical terms")
    print()
    print(f"3. Look for instruction patterns:")
    print(f"   - 'take' variants (tak, take, takun)")
    print(f"   - 'drink' variants (drynke, drink)")
    print(f"   - Treatment verbs (boil, mix, grind, apply)")
    print()
    print(f"4. Expected structure: 'Take [herb], [action], drink'")
    print()


if __name__ == "__main__":
    main()
