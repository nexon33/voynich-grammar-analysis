#!/usr/bin/env python3
"""
Re-translate Section 4 with specialized medical vocabulary.
Apply e↔o substitution to test recognition improvement.
"""

import json
import re
from pathlib import Path
from itertools import product


def load_specialized_vocab():
    """Load the specialized medical vocabulary."""
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"
    with open(
        results_dir / "specialized_medical_vocabulary.json", "r", encoding="utf-8"
    ) as f:
        return json.load(f)


def load_common_words():
    """Common ME function words."""
    return {
        "the",
        "and",
        "or",
        "an",
        "in",
        "of",
        "to",
        "for",
        "a",
        "is",
        "be",
        "she",
        "he",
        "it",
        "this",
        "that",
        "with",
        "from",
        "at",
        "by",
        "on",
        "as",
        "so",
        "do",
        "if",
        "when",
        "than",
        "then",
        "all",
        "but",
        "not",
    }


def generate_eo_variants(word, max_variants=16):
    """Generate e↔o variants."""
    eo_positions = [(i, c) for i, c in enumerate(word.lower()) if c in ["e", "o"]]

    if not eo_positions:
        return [word.lower()]

    if len(eo_positions) > 4:
        # Too many positions, just try simple swaps
        return [
            word.lower(),
            word.lower().replace("e", "o"),
            word.lower().replace("o", "e"),
            word.lower().replace("e", "X").replace("o", "e").replace("X", "o"),
        ]

    variants = set()
    for combination in product(["e", "o"], repeat=len(eo_positions)):
        variant = list(word.lower())
        for (pos, _), new_char in zip(eo_positions, combination):
            variant[pos] = new_char
        variants.add("".join(variant))
        if len(variants) >= max_variants:
            break

    return list(variants)


def translate_word_with_vocab(word, specialized_vocab, common_words):
    """Translate a word using specialized vocabulary and e↔o variants."""
    word_clean = word.lower().strip(".,;:!?[]")

    # Check exact match first
    if word_clean in common_words:
        return word_clean, "COMMON", 1.0, word_clean

    if word_clean in specialized_vocab:
        entry = specialized_vocab[word_clean]
        return entry["meaning"], entry["category"].upper(), 1.0, word_clean

    # Try e↔o variants
    for variant in generate_eo_variants(word_clean):
        if variant in common_words:
            return variant, "COMMON_VAR", 0.8, variant

        if variant in specialized_vocab:
            entry = specialized_vocab[variant]
            return entry["meaning"], entry["category"].upper() + "_VAR", 0.7, variant

    return None, None, 0.0, None


def extract_section_4_text():
    """Extract actual text from Section 4 (words 2000-2500)."""
    zl_path = (
        Path(__file__).parent.parent.parent
        / "data"
        / "voynich"
        / "eva_transcription"
        / "ZL3b-n.txt"
    )

    with open(zl_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    section_words = []
    current_word = 0
    current_folio = None

    for line in lines:
        line_stripped = line.strip()

        if line_stripped.startswith("<f") and "," not in line_stripped.split(">")[0]:
            folio_match = re.match(r"<(f\d+[rv])>", line_stripped)
            if folio_match:
                current_folio = folio_match.group(1)

        if "," in line_stripped and ">" in line_stripped:
            parts = line_stripped.split(">")
            if len(parts) >= 2:
                text = parts[-1]
                text = text.replace(".", " ")
                text = re.sub(r"[<>{}[\]()!?;:\-@$%*]", " ", text)
                words = text.split()

                for word in words:
                    if 2000 <= current_word < 2500:
                        section_words.append((current_folio, word, current_word))
                    current_word += 1

                    if current_word >= 2500:
                        break

        if current_word >= 2500:
            break

    return section_words


def retranslate_section_4():
    """Re-translate Section 4 with specialized vocabulary."""
    print("=" * 80)
    print("RE-TRANSLATING SECTION 4 WITH SPECIALIZED VOCABULARY")
    print("=" * 80)
    print()

    specialized_vocab = load_specialized_vocab()
    common_words = load_common_words()

    print(f"Specialized vocabulary: {len(specialized_vocab)} terms")
    print(f"Common words: {len(common_words)} terms")
    print()

    section_text = extract_section_4_text()
    print(f"Section 4: {len(section_text)} words (2000-2500)")
    print()

    # Group by folio for readability
    by_folio = {}
    for folio, word, pos in section_text:
        if folio not in by_folio:
            by_folio[folio] = []
        by_folio[folio].append((word, pos))

    print("=" * 80)
    print()

    total_recognized = 0
    total_words = len(section_text)

    all_translations = []

    for folio in sorted(by_folio.keys()):
        words = by_folio[folio]

        print(f"## Folio {folio} ({len(words)} words)")
        print()

        # Original
        original = " ".join([w for w, _ in words])
        print(f"**Original:**")
        print(original)
        print()

        # Translate
        translations = []
        recognized_here = 0
        annotations = []

        for word, pos in words:
            meaning, category, confidence, variant = translate_word_with_vocab(
                word, specialized_vocab, common_words
            )

            if meaning and confidence > 0.5:
                translations.append(meaning)
                recognized_here += 1
                all_translations.append(
                    {
                        "original": word,
                        "variant": variant,
                        "meaning": meaning,
                        "category": category,
                        "confidence": confidence,
                        "folio": folio,
                        "position": pos,
                    }
                )

                if category and (
                    "INSTRUCTION" in category
                    or "WOMENS_HEALTH" in category
                    or "CONDITION" in category
                    or "HERB" in category
                ):
                    annotations.append(f"{word} → {meaning} ({category})")
            else:
                translations.append(f"[{word}?]")

        print(
            f"**Translation** ({recognized_here}/{len(words)} = {100 * recognized_here / len(words):.1f}%):"
        )
        print(" ".join(translations))
        print()

        if annotations:
            print(f"**Key terms:**")
            for ann in annotations:
                print(f"  • {ann}")
            print()

        total_recognized += recognized_here

        print("-" * 80)
        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    recognition_rate = 100 * total_recognized / total_words
    print(
        f"Overall recognition: {total_recognized}/{total_words} = {recognition_rate:.1f}%"
    )
    print()

    # Breakdown by category
    by_category = {}
    for t in all_translations:
        cat = t["category"].replace("_VAR", "")
        by_category[cat] = by_category.get(cat, 0) + 1

    print("Breakdown by category:")
    for cat, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat:20s}: {count:3d} words")
    print()

    # Find readable phrases (3+ words in a row recognized)
    print("=" * 80)
    print("READABLE PHRASES (3+ consecutive words)")
    print("=" * 80)
    print()

    phrases_found = False
    for folio in sorted(by_folio.keys()):
        words = by_folio[folio]

        consecutive = []
        current_phrase = []

        for word, pos in words:
            meaning, category, confidence, variant = translate_word_with_vocab(
                word, specialized_vocab, common_words
            )

            if meaning and confidence > 0.5:
                current_phrase.append((word, meaning, category))
            else:
                if len(current_phrase) >= 3:
                    consecutive.append(current_phrase)
                current_phrase = []

        if len(current_phrase) >= 3:
            consecutive.append(current_phrase)

        if consecutive:
            phrases_found = True
            print(f"**{folio}:**")
            for phrase in consecutive:
                orig = " ".join([w for w, _, _ in phrase])
                trans = " ".join([m for _, m, _ in phrase])
                print(f"  Original:    {orig}")
                print(f"  Translation: {trans}")
                print()

    if not phrases_found:
        print("No phrases with 3+ consecutive recognized words found.")
        print("(This is expected - need more vocabulary expansion)")

    print()

    # Save results
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"
    output_path = results_dir / "section_4_retranslation.json"

    output = {
        "section_id": 4,
        "total_words": total_words,
        "recognized": total_recognized,
        "recognition_rate": recognition_rate,
        "translations": all_translations,
        "vocabulary_size": len(specialized_vocab) + len(common_words),
        "method": "e_o_substitution_with_specialized_vocab",
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to: {output_path}")
    print()


if __name__ == "__main__":
    retranslate_section_4()
