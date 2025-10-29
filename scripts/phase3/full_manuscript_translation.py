"""
Full Manuscript Translation for LLM Analysis

Translate entire Voynich manuscript using selective obfuscation model.
Output in structured format suitable for LLM analysis.

Format:
- Original Voynich text
- Best translation attempt
- Confidence scores
- Medical term annotations
- Section markers
"""

from pathlib import Path
import json
import re
from itertools import product
from collections import Counter, defaultdict


def load_vocabularies():
    """Load all vocabulary resources."""
    # Medical vocabulary
    with open(
        "results/phase3/medical_vocabulary_database.json", "r", encoding="utf-8"
    ) as f:
        medical_vocab = json.load(f)

    medical_flat = {}
    for category, terms in medical_vocab.items():
        for term_info in terms:
            medical_flat[term_info["word"]] = {
                "category": category,
                "frequency": term_info["frequency"],
            }

    # Common ME words + recipe vocabulary
    common_words = {
        # Articles and determiners
        "the",
        "thorn",
        "a",
        "an",
        "this",
        "that",
        "these",
        "those",
        # Conjunctions
        "and",
        "or",
        "but",
        "if",
        "than",
        "then",
        "when",
        "where",
        # Prepositions
        "of",
        "to",
        "in",
        "on",
        "at",
        "by",
        "for",
        "from",
        "with",
        # Pronouns
        "he",
        "she",
        "it",
        "they",
        "them",
        "her",
        "his",
        "their",
        "you",
        "your",
        # Verbs
        "is",
        "was",
        "are",
        "were",
        "be",
        "been",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "can",
        "could",
        "may",
        "might",
        "will",
        "would",
        "shall",
        "should",
        # Common verbs
        "say",
        "said",
        "see",
        "saw",
        "seen",
        "go",
        "went",
        "gone",
        "come",
        "came",
        # MEDICAL INSTRUCTION WORDS (high priority!)
        "take",
        "tak",
        "taken",
        "takun",
        "taketh",
        "takith",
        "drink",
        "drynke",
        "drinke",
        "drinketh",
        "make",
        "maken",
        "made",
        "maketh",
        "boil",
        "boyle",
        "boylen",
        "boileth",
        "mix",
        "mixe",
        "mixen",
        "mixeth",
        "grind",
        "grynde",
        "grinden",
        "ground",
        "use",
        "usen",
        "used",
        "useth",
        "apply",
        "applye",
        "applien",
        "lay",
        "leye",
        "layen",
        "laid",
        "laide",
        "put",
        "putten",
        "putte",
        "give",
        "given",
        "yeve",
        "yeven",
        # Adjectives
        "good",
        "beste",
        "best",
        "wel",
        "well",
        "better",
        "much",
        "moche",
        "more",
        "most",
        "little",
        "litel",
        "less",
        "lest",
        "great",
        "grete",
        "greater",
        "hot",
        "hote",
        "cold",
        "colde",
        "warm",
        "warme",
        # Time/frequency
        "day",
        "daily",
        "night",
        "nightly",
        "time",
        "tyme",
        "times",
        "tymes",
        "hour",
        "houre",
        "hours",
        "houres",
        "ofte",
        "often",
        "always",
        "alway",
        "never",
        "once",
        "ones",
        "twice",
        "thrice",
        "thries",
        # Quantities
        "one",
        "two",
        "three",
        "four",
        "five",
        "many",
        "few",
        "all",
        "some",
        "none",
        # Substances
        "water",
        "watur",
        "wine",
        "wyn",
        "wyne",
        "oil",
        "oyle",
        "oile",
        "honey",
        "hony",
        "milk",
        "mylk",
        "milke",
        "vinegar",
        "vynegre",
        "salt",
        "salte",
        "sugar",
        "sugre",
        # Herbs/plants
        "herb",
        "herbe",
        "herbes",
        "root",
        "roote",
        "rote",
        "roots",
        "rootes",
        "leaf",
        "leef",
        "lef",
        "leaves",
        "leves",
        "flower",
        "flour",
        "floure",
        "flowers",
        "seed",
        "sede",
        "seeds",
        "sedes",
        # Body parts (common)
        "head",
        "hede",
        "hed",
        "body",
        "bodi",
        "bodye",
        "heart",
        "herte",
        "hand",
        "hond",
        "hands",
        "hondes",
        "foot",
        "fot",
        "feet",
        "fet",
        # Short common words
        "so",
        "as",
        "no",
        "not",
        "yes",
        "yea",
        "now",
        "here",
        "there",
        "up",
        "down",
        "out",
        "in",
    }

    return medical_flat, common_words


def generate_variants_smart(word, max_variants=32):
    """Generate e↔o variants intelligently."""
    eo_positions = [(i, c) for i, c in enumerate(word) if c in ["e", "o"]]

    if not eo_positions:
        return [word]

    # Limit combinations for long words
    if len(eo_positions) > 5:
        return [
            word,
            word.replace("o", "e"),
            word.replace("e", "o"),
        ]

    variants = []
    for combination in product(["e", "o"], repeat=len(eo_positions)):
        variant = list(word)
        for (pos, _), new_char in zip(eo_positions, combination):
            variant[pos] = new_char
        variants.append("".join(variant))

    return list(set(variants))[:max_variants]


def score_variant(variant, original, medical_vocab, common_words):
    """Score a single variant."""
    score = 0
    tags = []
    category = None

    # Medical term (HIGHEST PRIORITY)
    if variant in medical_vocab:
        score += 2000
        category = medical_vocab[variant]["category"]
        tags.append(f"MED:{category}")
        freq = medical_vocab[variant]["frequency"]
        score += min(freq // 50, 1000)

        # Extra boost for key terms
        if category == "treatments" and variant in ["take", "tak", "drynke", "hele"]:
            score += 1000
            tags.append("KEY_INSTRUCTION")

    # Common ME word (HIGH PRIORITY)
    elif variant in common_words:
        score += 1000
        tags.append("COMMON")

        # Extra boost for instruction words
        if variant in [
            "take",
            "tak",
            "takun",
            "drynke",
            "make",
            "boil",
            "mix",
            "grind",
        ]:
            score += 500
            tags.append("INSTRUCTION")

    # Unchanged from original (bonus for short/common words)
    if variant == original:
        if len(variant) <= 3:
            score += 200
            tags.append("unchanged")
        elif len(variant) <= 5:
            score += 100
            tags.append("unchanged")

    # Length bonuses
    if len(variant) <= 2:
        score += 100
    elif len(variant) <= 4:
        score += 50

    # ME patterns
    if "ch" in variant:
        score += 40
        tags.append("ch")
    if "sh" in variant:
        score += 40
        tags.append("sh")
    if variant.endswith("ly"):
        score += 30
        tags.append("adverb")
    if variant.endswith("er") or variant.endswith("or"):
        score += 25
        tags.append("agent")
    if variant.endswith("ed") or variant.endswith("od"):
        score += 20
        tags.append("past")
    if variant.endswith("es") or variant.endswith("os"):
        score += 20
        tags.append("plural")
    if variant.startswith("y") and len(variant) > 2:
        score += 15
        tags.append("y-prefix")

    return {
        "word": variant,
        "score": score,
        "tags": tags,
        "category": category,
        "original": original,
    }


def translate_word(word, medical_vocab, common_words):
    """Translate a single word with all variants and scores."""
    variants = generate_variants_smart(word)

    scored = [score_variant(v, word, medical_vocab, common_words) for v in variants]
    scored.sort(key=lambda x: x["score"], reverse=True)

    return {
        "original": word,
        "best": scored[0] if scored else None,
        "alternatives": scored[1:6] if len(scored) > 1 else [],
    }


def translate_full_manuscript(voynich_text, medical_vocab, common_words):
    """Translate entire manuscript."""
    print("Translating full manuscript...")
    print("(This will take a few minutes...)\n")

    # Split into words
    all_words = re.findall(r"[a-z]+", voynich_text.lower())

    print(f"Total words to translate: {len(all_words):,}")

    # Translate each word
    translations = []

    for i, word in enumerate(all_words):
        translation = translate_word(word, medical_vocab, common_words)
        translations.append(translation)

        if (i + 1) % 5000 == 0:
            print(f"  Processed {i + 1:,} words...")

    print(f"✓ Translation complete!\n")

    return translations


def format_for_llm(translations, words_per_section=100):
    """
    Format translation for LLM analysis.

    Structure:
    - Sections of ~100 words
    - Original + translation side by side
    - Confidence annotations
    - Medical term highlights
    """
    sections = []

    for i in range(0, len(translations), words_per_section):
        chunk = translations[i : i + words_per_section]

        # Build section
        original_words = [t["original"] for t in chunk]
        translated_words = []
        annotations = []

        for t in chunk:
            if t["best"] and t["best"]["score"] >= 500:  # High confidence
                translated_words.append(t["best"]["word"])

                # Add annotation if medical/important
                if t["best"]["score"] >= 1500:
                    annotations.append(
                        {
                            "original": t["original"],
                            "translation": t["best"]["word"],
                            "tags": t["best"]["tags"],
                            "category": t["best"]["category"],
                            "confidence": "HIGH",
                        }
                    )
            elif t["best"] and t["best"]["score"] >= 100:  # Medium confidence
                translated_words.append(f"[{t['best']['word']}]")
            else:
                translated_words.append(f"[{t['original']}?]")

        section = {
            "section_id": i // words_per_section,
            "word_range": f"{i}-{min(i + words_per_section, len(translations))}",
            "original": " ".join(original_words),
            "translation": " ".join(translated_words),
            "annotations": annotations,
            "medical_term_count": len([a for a in annotations if a["category"]]),
            "high_confidence_count": len(
                [t for t in chunk if t["best"] and t["best"]["score"] >= 1000]
            ),
        }

        sections.append(section)

    return sections


def create_llm_prompt_file(sections):
    """Create a file formatted for LLM analysis."""
    output = []

    output.append("# Voynich Manuscript - Partial Translation")
    output.append("# Using Selective Obfuscation Model (e↔o substitution)")
    output.append("# Date: 2025-10-29")
    output.append("#")
    output.append("# Format:")
    output.append("# - Words in [brackets] = medium confidence")
    output.append("# - Words in [brackets?] = low confidence")
    output.append("# - Plain words = high confidence")
    output.append("# - Medical terms are annotated")
    output.append("#")
    output.append("# Instructions for LLM:")
    output.append("# This is a 15th century Middle English medical manuscript.")
    output.append("# Focus on:")
    output.append("# 1. Medical recipes/instructions")
    output.append("# 2. Herb names and preparations")
    output.append("# 3. Body parts and conditions")
    output.append("# 4. Treatment procedures")
    output.append("# 5. Women's health content")
    output.append("#")
    output.append("# Known vocabulary:")
    output.append("# - 'sor' = sore (condition)")
    output.append("# - 'hele' = heal (treatment)")
    output.append("# - 'drynke' = drink (instruction)")
    output.append("# - 'tak/take/takun' = take/taken (instruction)")
    output.append("# - 'she' = she (pronoun, women's context)")
    output.append("#")
    output.append("=" * 70)
    output.append("")

    for section in sections:
        output.append(f"\n## Section {section['section_id']}")
        output.append(f"Words: {section['word_range']}")
        output.append(f"Medical terms: {section['medical_term_count']}")
        output.append(f"High confidence: {section['high_confidence_count']}")
        output.append("")

        output.append("### Original Voynich:")
        output.append(section["original"])
        output.append("")

        output.append("### Translation:")
        output.append(section["translation"])
        output.append("")

        if section["annotations"]:
            output.append("### Medical/Key Terms:")
            for ann in section["annotations"]:
                tags_str = ", ".join(ann["tags"])
                cat = ann["category"] if ann["category"] else "common"
                output.append(
                    f"- {ann['original']} → {ann['translation']} ({cat}: {tags_str})"
                )
            output.append("")

        output.append("-" * 70)

    return "\n".join(output)


def generate_statistics(translations):
    """Generate translation statistics."""
    stats = {
        "total_words": len(translations),
        "high_confidence": 0,
        "medium_confidence": 0,
        "low_confidence": 0,
        "medical_terms": 0,
        "common_words": 0,
        "instruction_words": 0,
        "categories": defaultdict(int),
    }

    for t in translations:
        if t["best"]:
            score = t["best"]["score"]

            if score >= 1000:
                stats["high_confidence"] += 1
            elif score >= 500:
                stats["medium_confidence"] += 1
            elif score >= 100:
                stats["low_confidence"] += 1

            if "MED:" in str(t["best"]["tags"]):
                stats["medical_terms"] += 1
                if t["best"]["category"]:
                    stats["categories"][t["best"]["category"]] += 1

            if "COMMON" in t["best"]["tags"]:
                stats["common_words"] += 1

            if (
                "INSTRUCTION" in t["best"]["tags"]
                or "KEY_INSTRUCTION" in t["best"]["tags"]
            ):
                stats["instruction_words"] += 1

    return stats


def main():
    print("\n" + "=" * 70)
    print("FULL MANUSCRIPT TRANSLATION FOR LLM ANALYSIS")
    print("=" * 70 + "\n")

    # Load vocabularies
    print("Loading vocabularies...")
    medical_vocab, common_words = load_vocabularies()
    print(f"✓ Medical terms: {len(medical_vocab):,}")
    print(f"✓ Common words: {len(common_words)}\n")

    # Load Voynich
    voynich_file = Path("data/voynich/eva_transcription/voynich_eva_takahashi.txt")
    with open(voynich_file, "r", encoding="utf-8") as f:
        voynich_text = f.read().lower()

    print(f"✓ Voynich text loaded: {len(voynich_text):,} characters\n")

    # Translate
    translations = translate_full_manuscript(voynich_text, medical_vocab, common_words)

    # Statistics
    print("=" * 70)
    print("TRANSLATION STATISTICS")
    print("=" * 70 + "\n")

    stats = generate_statistics(translations)

    print(f"Total words: {stats['total_words']:,}")
    print(
        f"High confidence (score >= 1000): {stats['high_confidence']:,} ({stats['high_confidence'] / stats['total_words'] * 100:.1f}%)"
    )
    print(
        f"Medium confidence (score >= 500): {stats['medium_confidence']:,} ({stats['medium_confidence'] / stats['total_words'] * 100:.1f}%)"
    )
    print(
        f"Low confidence (score >= 100): {stats['low_confidence']:,} ({stats['low_confidence'] / stats['total_words'] * 100:.1f}%)"
    )
    print()
    print(
        f"Medical terms found: {stats['medical_terms']:,} ({stats['medical_terms'] / stats['total_words'] * 100:.1f}%)"
    )
    print(
        f"Common words found: {stats['common_words']:,} ({stats['common_words'] / stats['total_words'] * 100:.1f}%)"
    )
    print(f"Instruction words: {stats['instruction_words']:,}")
    print()

    if stats["categories"]:
        print("Medical categories:")
        for cat, count in sorted(
            stats["categories"].items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  {cat.replace('_', ' ').title()}: {count}")
    print()

    # Format for LLM
    print("Formatting for LLM analysis...")
    sections = format_for_llm(translations, words_per_section=100)
    print(f"✓ Created {len(sections)} sections\n")

    # Create LLM prompt file
    llm_content = create_llm_prompt_file(sections)

    # Save files
    output_dir = Path("results/phase3")

    # Save full translation data (JSON)
    trans_file = output_dir / "full_manuscript_translation.json"
    with open(trans_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "statistics": stats,
                "sections": sections,
                "metadata": {
                    "source": "Voynich EVA Takahashi transcription",
                    "method": "Selective obfuscation model (e↔o)",
                    "date": "2025-10-29",
                    "total_words": len(translations),
                },
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"✓ Full translation data: {trans_file}")

    # Save LLM-ready file (text)
    llm_file = output_dir / "voynich_for_llm_analysis.txt"
    with open(llm_file, "w", encoding="utf-8") as f:
        f.write(llm_content)

    print(f"✓ LLM-ready file: {llm_file}")

    # Save compact version (just translations)
    compact_file = output_dir / "voynich_translated_compact.txt"
    with open(compact_file, "w", encoding="utf-8") as f:
        f.write("VOYNICH MANUSCRIPT - TRANSLATED VERSION\n")
        f.write("=" * 70 + "\n\n")

        for section in sections:
            f.write(f"\n[Section {section['section_id']}]\n")
            f.write(section["translation"])
            f.write("\n")

    print(f"✓ Compact translation: {compact_file}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70 + "\n")

    print(f"✓ Translated {stats['total_words']:,} words")
    print(
        f"✓ Recognition rate: {(stats['high_confidence'] + stats['medium_confidence']) / stats['total_words'] * 100:.1f}%"
    )
    print(f"✓ Medical vocabulary: {stats['medical_terms']} terms")
    print(f"✓ Instruction words: {stats['instruction_words']}")
    print()
    print("FILES READY FOR LLM:")
    print(f"  1. {llm_file.name} - Full annotated version")
    print(f"  2. {compact_file.name} - Clean translated text")
    print(f"  3. {trans_file.name} - Complete data (JSON)")
    print()
    print("READY TO FEED INTO LLM FOR:")
    print("  - Pattern recognition")
    print("  - Recipe structure identification")
    print("  - Medical term interpretation")
    print("  - Context analysis")
    print("  - Coherent passage extraction")
    print()


if __name__ == "__main__":
    main()
