"""
Translate High-Density Medical Sections

Focus on sections with highest medical term concentration.
Look for recipe patterns: "Take [herb], [action], drink"
"""

from pathlib import Path
import json
import re
from itertools import product


def load_medical_vocabulary():
    """Load medical vocabulary database."""
    vocab_file = Path("results/phase3/medical_vocabulary_database.json")
    with open(vocab_file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_section_analysis():
    """Load section analysis."""
    analysis_file = Path("results/phase3/section_medical_density.json")
    with open(analysis_file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_voynich_text():
    """Load Voynich text."""
    voynich_file = Path("data/voynich/eva_transcription/voynich_eva_takahashi.txt")
    with open(voynich_file, "r", encoding="utf-8") as f:
        return f.read().lower()


def generate_eo_variants(word):
    """Generate all e↔o variants."""
    eo_positions = []
    for i, char in enumerate(word):
        if char in ["e", "o"]:
            eo_positions.append(i)

    if not eo_positions:
        return [word]

    variants = []
    for combination in product(["e", "o"], repeat=len(eo_positions)):
        variant = list(word)
        for pos_idx, char_choice in enumerate(combination):
            variant[eo_positions[pos_idx]] = char_choice
        variants.append("".join(variant))

    return list(set(variants))


def load_me_common_words():
    """Load common ME words for context."""
    # Common ME function words and frequent vocabulary
    common = {
        "the",
        "thorn",
        "and",
        "of",
        "to",
        "in",
        "a",
        "is",
        "was",
        "that",
        "he",
        "she",
        "it",
        "be",
        "with",
        "for",
        "on",
        "at",
        "by",
        "from",
        "or",
        "an",
        "as",
        "are",
        "not",
        "but",
        "this",
        "take",
        "tak",
        "taken",
        "takun",
        "make",
        "drink",
        "drynke",
        "boil",
        "boyle",
        "mix",
        "mixe",
        "grind",
        "grynde",
        "use",
        "good",
        "beste",
        "water",
        "wine",
        "wyn",
        "oil",
        "oyle",
        "herb",
        "herbe",
        "root",
        "roote",
        "leaf",
        "leef",
        "seed",
        "sede",
        "day",
        "night",
        "time",
        "tyme",
        "hour",
        "houre",
        "ofte",
        "often",
        "much",
        "moche",
        "little",
        "litel",
        "well",
        "wel",
    }
    return common


def translate_word_comprehensive(word, medical_vocab_flat, common_words):
    """
    Try all e↔o variants and rank by likelihood.
    """
    variants = generate_eo_variants(word)

    scored = []
    for variant in variants:
        score = 0
        tags = []

        # Medical term (highest priority)
        if variant in medical_vocab_flat:
            score += 500
            tags.append(f"MEDICAL:{medical_vocab_flat[variant]['category']}")

        # Common ME word
        if variant in common_words:
            score += 200
            tags.append("common")

        # Short word bonus
        if len(variant) < 4:
            score += 50

        # ME patterns
        if "ch" in variant:
            score += 20
            tags.append("ch")
        if "sh" in variant:
            score += 20
            tags.append("sh")
        if variant.endswith("ly"):
            score += 15
        if variant.endswith("er") or variant.endswith("or"):
            score += 10

        scored.append({"variant": variant, "score": score, "tags": tags})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def extract_section_text(voynich_text, section_id, words_per_section=500):
    """Extract text for a specific section."""
    all_words = re.findall(r"[a-z]+", voynich_text)

    start_idx = section_id * words_per_section
    end_idx = start_idx + words_per_section

    section_words = all_words[start_idx:end_idx]
    return section_words


def translate_section(section_words, medical_vocab_flat, common_words):
    """Translate a section word by word."""
    translations = []

    for word in section_words:
        variants = translate_word_comprehensive(word, medical_vocab_flat, common_words)

        # Take top 3
        top_variants = variants[:3]

        translations.append({"original": word, "variants": top_variants})

    return translations


def format_translation_readable(translations, words_per_line=10):
    """Format translation in readable form."""
    lines = []

    for i in range(0, len(translations), words_per_line):
        chunk = translations[i : i + words_per_line]

        # Original line
        original_line = " ".join([t["original"] for t in chunk])

        # Best translation line
        best_line = " ".join(
            [
                t["variants"][0]["variant"]
                if t["variants"] and t["variants"][0]["score"] > 0
                else "???"
                for t in chunk
            ]
        )

        # Annotations
        medical_terms = []
        for t in chunk:
            if t["variants"] and t["variants"][0]["score"] >= 500:
                medical_terms.append(f"{t['original']}→{t['variants'][0]['variant']}")

        lines.append(
            {
                "original": original_line,
                "translation": best_line,
                "medical_terms": medical_terms,
            }
        )

    return lines


def main():
    print("\n" + "=" * 70)
    print("TRANSLATING HIGH-DENSITY MEDICAL SECTIONS")
    print("=" * 70 + "\n")

    # Load data
    print("Loading data...")
    medical_vocab = load_medical_vocabulary()
    section_analysis = load_section_analysis()
    voynich_text = load_voynich_text()
    common_words = load_me_common_words()

    # Flatten medical vocab
    medical_vocab_flat = {}
    for category, terms in medical_vocab.items():
        for term_info in terms:
            medical_vocab_flat[term_info["word"]] = {
                "category": category,
                "frequency": term_info["frequency"],
            }

    print(f"✓ Loaded {len(medical_vocab_flat):,} medical terms")
    print(f"✓ Loaded {len(common_words)} common ME words\n")

    # Get top 3 sections
    top_sections = sorted(
        section_analysis, key=lambda x: x["density_percent"], reverse=True
    )[:3]

    print(f"Translating top 3 highest-density sections...\n")

    all_translations = []

    for rank, section in enumerate(top_sections, 1):
        section_id = section["section_id"]
        density = section["density_percent"]

        print("=" * 70)
        print(f"SECTION #{section_id} (Rank {rank}, Density: {density:.2f}%)")
        print("=" * 70 + "\n")

        # Extract section text
        section_words = extract_section_text(voynich_text, section_id)

        print(f"Section contains {len(section_words)} words")
        print(f"Medical terms found: {section['medical_term_count']}")
        print()

        # Translate
        translations = translate_section(
            section_words, medical_vocab_flat, common_words
        )

        # Format for display
        formatted = format_translation_readable(translations, words_per_line=10)

        print("TRANSLATION (first 10 lines):")
        print("-" * 70)

        for i, line in enumerate(formatted[:10]):
            print(f"\nLine {i + 1}:")
            print(f"  Voynich:     {line['original']}")
            print(f"  Translation: {line['translation']}")
            if line["medical_terms"]:
                print(f"  Medical:     {', '.join(line['medical_terms'])}")

        print("\n...")

        # Save full translation
        all_translations.append(
            {
                "section_id": section_id,
                "rank": rank,
                "density": density,
                "word_count": len(section_words),
                "medical_count": section["medical_term_count"],
                "translations": translations,
                "formatted": formatted,
            }
        )

    # Look for recipe patterns
    print("\n" + "=" * 70)
    print("SEARCHING FOR RECIPE PATTERNS")
    print("=" * 70 + "\n")

    recipe_keywords = {
        "take": ["take", "tak", "taken", "takun"],
        "drink": ["drink", "drynke"],
        "boil": ["boil", "boyle"],
        "mix": ["mix", "mixe"],
        "grind": ["grind", "grynde"],
        "make": ["make"],
        "use": ["use"],
        "apply": ["apply", "lay", "leye"],
    }

    print("Looking for instruction words:\n")

    for section_trans in all_translations:
        section_id = section_trans["section_id"]
        translations = section_trans["translations"]

        found_instructions = []

        for trans in translations:
            best_variant = trans["variants"][0] if trans["variants"] else None
            if best_variant:
                for instr_type, keywords in recipe_keywords.items():
                    if best_variant["variant"] in keywords:
                        found_instructions.append(
                            {
                                "voynich": trans["original"],
                                "translation": best_variant["variant"],
                                "type": instr_type,
                                "score": best_variant["score"],
                            }
                        )

        if found_instructions:
            print(
                f"Section #{section_id} - Found {len(found_instructions)} instruction words:"
            )
            for instr in found_instructions[:5]:  # Show first 5
                print(
                    f"  {instr['voynich']:15} → {instr['translation']:15} ({instr['type']})"
                )
            print()

    # Save results
    output_dir = Path("results/phase3")

    # Save translations
    trans_file = output_dir / "high_density_translations.json"
    with open(trans_file, "w", encoding="utf-8") as f:
        json.dump(all_translations, f, indent=2, ensure_ascii=False)

    print(f"✓ Translations saved to: {trans_file}")

    # Create readable version
    readable_file = output_dir / "translations_readable.txt"
    with open(readable_file, "w", encoding="utf-8") as f:
        f.write("HIGH-DENSITY SECTION TRANSLATIONS\n")
        f.write("=" * 70 + "\n\n")

        for section_trans in all_translations:
            section_id = section_trans["section_id"]
            rank = section_trans["rank"]
            density = section_trans["density"]

            f.write(f"\n{'=' * 70}\n")
            f.write(f"SECTION #{section_id} (Rank {rank}, Density: {density:.2f}%)\n")
            f.write(f"{'=' * 70}\n\n")

            formatted = section_trans["formatted"]

            for i, line in enumerate(formatted, 1):
                f.write(f"Line {i}:\n")
                f.write(f"  V: {line['original']}\n")
                f.write(f"  T: {line['translation']}\n")
                if line["medical_terms"]:
                    f.write(f"  M: {', '.join(line['medical_terms'])}\n")
                f.write("\n")

    print(f"✓ Readable version saved to: {readable_file}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70 + "\n")

    print("✓ Translated 3 highest-density medical sections")
    print("✓ Sections contain:")
    for section_trans in all_translations:
        print(
            f"    Section #{section_trans['section_id']}: {section_trans['medical_count']} medical terms"
        )
    print()
    print("Next steps:")
    print("  1. Review translations for coherent phrases")
    print("  2. Look for repeated patterns across sections")
    print("  3. Compare with known ME medical recipes")
    print("  4. Validate with ME linguistics experts")
    print()


if __name__ == "__main__":
    main()
