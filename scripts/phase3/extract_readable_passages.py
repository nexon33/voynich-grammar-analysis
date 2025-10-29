#!/usr/bin/env python3
"""
Extract the most readable passages from the Voynich manuscript.
Focus on Section 4 and other high-density sections.
Build actual readable text that people can verify.
"""

import re
from pathlib import Path
from collections import Counter

# Common Middle English words that should be preserved
COMMON_ME_WORDS = {
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
    "take",
    "tak",
    "make",
    "use",
    "put",
    "set",
    "get",
    "let",
}

# Medical recipe instruction words
RECIPE_WORDS = {
    "take": "take",
    "tak": "take",
    "takyn": "taken",
    "takun": "taken",
    "boil": "boil",
    "boyle": "boil",
    "boylyn": "boiling",
    "drink": "drink",
    "drynke": "drink",
    "drynk": "drink",
    "hele": "heal",
    "helyn": "healing",
    "heele": "heal",
    "mix": "mix",
    "myx": "mix",
    "mixyn": "mixing",
    "grind": "grind",
    "grynde": "grind",
    "grynd": "grind",
    "pound": "pound",
    "pounde": "pound",
    "pownde": "pound",
    "steep": "steep",
    "stepe": "steep",
    "stepyn": "steeping",
    "apply": "apply",
    "applye": "apply",
    "applyyn": "applying",
    "use": "use",
    "usen": "use",
    "usyn": "using",
}

# Medical terms we've identified
MEDICAL_TERMS = {
    "sor": "sore/pain",
    "sory": "sore/painful",
    "soar": "sore",
    "ched": "body_part",
    "chod": "body_part",
    "shed": "shed/body",
    "ear": "ear",
    "ere": "ear",
    "oar": "ear",
    "hele": "heal",
    "chele": "heal",
    "hel": "heal",
    "womb": "womb",
    "womman": "woman",
    "women": "women",
    "child": "child",
    "childe": "child",
    "blod": "blood",
    "blood": "blood",
    "hed": "head",
    "head": "head",
    "heued": "head",
}


def apply_eo_substitution(word):
    """Generate e↔o variants of a word."""
    variants = [word]

    # Try e→o
    if "e" in word:
        variants.append(word.replace("e", "o"))

    # Try o→e
    if "o" in word:
        variants.append(word.replace("o", "e"))

    # Try both
    if "e" in word and "o" in word:
        temp = word.replace("e", "X").replace("o", "e").replace("X", "o")
        variants.append(temp)

    return list(set(variants))


def translate_word(word):
    """Attempt to translate a single word."""
    word_lower = word.lower().strip(".,;:!?")

    # Check if it's a known common word
    if word_lower in COMMON_ME_WORDS:
        return word_lower, "COMMON", 1.0

    # Check recipe words
    if word_lower in RECIPE_WORDS:
        return RECIPE_WORDS[word_lower], "RECIPE", 1.0

    # Check medical terms
    if word_lower in MEDICAL_TERMS:
        return MEDICAL_TERMS[word_lower], "MEDICAL", 0.9

    # Try e↔o variants
    for variant in apply_eo_substitution(word_lower):
        if variant in COMMON_ME_WORDS:
            return variant, "COMMON_VAR", 0.8
        if variant in RECIPE_WORDS:
            return RECIPE_WORDS[variant], "RECIPE_VAR", 0.8
        if variant in MEDICAL_TERMS:
            return MEDICAL_TERMS[variant], "MEDICAL_VAR", 0.7

    return None, None, 0.0


def extract_section_text(section_id=4):
    """Extract text from a specific section."""
    # Read the ZL transcription to get actual text
    zl_path = (
        Path(__file__).parent.parent.parent
        / "data"
        / "voynich"
        / "eva_transcription"
        / "ZL3b-n.txt"
    )

    with open(zl_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find words 2000-2500 for Section 4
    word_start = section_id * 500
    word_end = word_start + 500

    current_word = 0
    section_lines = []
    current_folio = None

    for line in lines:
        line_stripped = line.strip()

        # Track folio
        if line_stripped.startswith("<f") and "," not in line_stripped.split(">")[0]:
            folio_match = re.match(r"<(f\d+[rv])>", line_stripped)
            if folio_match:
                current_folio = folio_match.group(1)

        # Extract text
        if "," in line_stripped and ">" in line_stripped:
            parts = line_stripped.split(">")
            if len(parts) >= 2:
                text = parts[-1]
                # Clean text
                text = text.replace(".", " ")
                text = re.sub(r"[<>{}[\]()!?;:\-@$%*]", " ", text)
                words = text.split()

                for word in words:
                    if word_start <= current_word < word_end:
                        section_lines.append((current_folio, word))
                    current_word += 1

                    if current_word >= word_end:
                        break

        if current_word >= word_end:
            break

    return section_lines


def translate_section(section_id=4):
    """Translate a section with annotations."""
    print(f"=" * 80)
    print(f"TRANSLATING SECTION {section_id}")
    print(f"=" * 80)
    print()

    section_text = extract_section_text(section_id)

    if not section_text:
        print("No text found for this section")
        return

    print(f"Extracted {len(section_text)} words")
    print()

    # Group by folio
    by_folio = {}
    for folio, word in section_text:
        if folio not in by_folio:
            by_folio[folio] = []
        by_folio[folio].append(word)

    print(f"Spans {len(by_folio)} folios: {', '.join(sorted(by_folio.keys()))}")
    print()
    print("=" * 80)
    print()

    # Translate each folio's portion
    for folio in sorted(by_folio.keys()):
        words = by_folio[folio]

        print(f"## Folio {folio} ({len(words)} words)")
        print()

        # Original text
        original_line = " ".join(words)
        print(f"**Original:**")
        print(original_line)
        print()

        # Translation with annotations
        translations = []
        annotations = []
        recognized_count = 0

        for word in words:
            translation, category, confidence = translate_word(word)

            if translation:
                translations.append(translation)
                recognized_count += 1
                if category in ["MEDICAL", "MEDICAL_VAR"]:
                    annotations.append(f"{word}→{translation}")
            else:
                translations.append(f"[{word}?]")

        print(
            f"**Translation** ({recognized_count}/{len(words)} = {100 * recognized_count / len(words):.1f}% recognized):"
        )
        print(" ".join(translations))
        print()

        if annotations:
            print(f"**Medical terms:**")
            for ann in annotations:
                print(f"  - {ann}")
            print()

        print("-" * 80)
        print()


def find_best_passages():
    """Find the most readable passages across the entire manuscript."""
    print("=" * 80)
    print("SEARCHING FOR MOST READABLE PASSAGES")
    print("=" * 80)
    print()

    # We'll search in chunks of 20 words
    chunk_size = 20
    best_passages = []

    # Get all text
    zl_path = (
        Path(__file__).parent.parent.parent
        / "data"
        / "voynich"
        / "eva_transcription"
        / "ZL3b-n.txt"
    )

    with open(zl_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    all_words = []
    current_folio = None

    for line in lines:
        line_stripped = line.strip()

        # Track folio
        if line_stripped.startswith("<f") and "," not in line_stripped.split(">")[0]:
            folio_match = re.match(r"<(f\d+[rv])>", line_stripped)
            if folio_match:
                current_folio = folio_match.group(1)

        # Extract text
        if "," in line_stripped and ">" in line_stripped:
            parts = line_stripped.split(">")
            if len(parts) >= 2:
                text = parts[-1]
                text = text.replace(".", " ")
                text = re.sub(r"[<>{}[\]()!?;:\-@$%*]", " ", text)
                words = text.split()

                for word in words:
                    all_words.append((current_folio, word))

    # Scan in chunks
    for i in range(0, len(all_words) - chunk_size, 5):  # Step by 5 for overlap
        chunk = all_words[i : i + chunk_size]
        folio = chunk[0][0]
        words = [w for _, w in chunk]

        # Count recognized words
        recognized = 0
        medical_count = 0

        for word in words:
            translation, category, confidence = translate_word(word)
            if translation and confidence > 0.5:
                recognized += 1
                if category and "MEDICAL" in category:
                    medical_count += 1

        recognition_rate = recognized / len(words)

        if recognition_rate > 0.3:  # At least 30% recognized
            best_passages.append(
                {
                    "folio": folio,
                    "start_index": i,
                    "words": words,
                    "recognition_rate": recognition_rate,
                    "medical_count": medical_count,
                }
            )

    # Sort by recognition rate
    best_passages.sort(key=lambda x: x["recognition_rate"], reverse=True)

    print(f"Found {len(best_passages)} passages with >30% recognition")
    print()
    print("TOP 10 MOST READABLE PASSAGES:")
    print()

    for idx, passage in enumerate(best_passages[:10], 1):
        print(
            f"{idx}. Folio {passage['folio']} - {passage['recognition_rate'] * 100:.1f}% recognized"
        )
        print(f"   Medical terms: {passage['medical_count']}")

        # Show translation
        original = " ".join(passage["words"])
        translations = []

        for word in passage["words"]:
            translation, _, confidence = translate_word(word)
            if translation and confidence > 0.5:
                translations.append(translation)
            else:
                translations.append(f"[{word}?]")

        print(f"   Original: {original[:60]}...")
        print(f"   Translation: {' '.join(translations[:15])}...")
        print()


def main():
    # Translate Section 4 (highest medical density)
    translate_section(4)

    print()
    print()

    # Find best readable passages
    find_best_passages()


if __name__ == "__main__":
    main()
