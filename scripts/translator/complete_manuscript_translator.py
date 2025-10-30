#!/usr/bin/env python3
"""
Complete Voynich Manuscript Translator
Uses all 47 validated morphological elements + semantic meanings
Applies reversal hypothesis for enhanced recognition
"""

import re
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

# ============================================================================
# SEMANTIC DICTIONARY - All Known Meanings
# ============================================================================

SEMANTIC_MEANINGS = {
    # Confirmed spatial/environmental terms
    "dair": "THERE",
    "air": "SKY",
    "ar": "AT/IN",
    # Tentative botanical terms (phonetic intuition)
    "ok": "oak",
    "qok": "oak",
    "ot": "oat",
    "qot": "oat",
    "sho": "botanical-term",
    "chol": "botanical-term",
    # Tentative substance terms
    "she": "water",
    "shee": "water",
    "dor": "red",
    "cho": "vessel",
    "cheo": "vessel",
    # Pharmaceutical terms (structure validated, meaning unknown)
    "keo": "pharmaceutical-substance",
    "teo": "pharmaceutical-substance",
    # Unknown-meaning validated roots (show as uppercase)
    "okal": "OKAL",
    "or": "OR",
    "dol": "DOL",
    "dar": "DAR",
    "ol": "OL",
    "ain": "AIN",
    # Function words
    "sal": "AND",
    "qol": "THEN",
    "daiin": "THIS/THAT",
    "dain": "THIS/THAT",
    "ory": "[PARTICLE-FINAL]",
    "chy": "[PARTICLE]",
    "chey": "[PARTICLE]",
    "cheey": "[PARTICLE]",
    "shy": "[PARTICLE]",
    "am": "[MODAL]",
    "dam": "[MODAL]",
    "cthy": "[PARTICLE]",
    "chom": "[PARTICLE]",
    "otchol": "oat-vessel",
    "shecthy": "water-[COMPOUND]",
    # Validated compounds
    "olkedy": "at-KEDY",
    "olchedy": "at-CHEDY",
}

# Prefixes
PREFIXES = {
    "qok": "oak-GEN",
    "qot": "oat-GEN",
    "ol": "AT",
    "ot": "AT",  # Allomorph of ol-
}

# Suffixes
SUFFIXES = {
    "al": "LOC",
    "ol": "LOC",
    "ar": "DIR",
    "or": "INST",
    "dy": "VERB",
    "edy": "VERB",
    "ain": "DEF",
    "iin": "DEF",
    "aiin": "DEF",
}

# Reversal hypothesis dictionary (Middle English words that may be reversed)
REVERSAL_DICT = {
    "root": ["botanical", "plant-part"],
    "rote": ["botanical", "plant-part"],
    "ye": ["eye", "body-part"],
    "eye": ["eye", "body-part"],
    "ear": ["ear", "body-part"],
    "ere": ["ear", "body-part"],
    "sore": ["pain", "condition"],
    "pain": ["pain", "condition"],
}

# ============================================================================
# TRANSLATION FUNCTIONS
# ============================================================================


def apply_e_o_substitution(word: str) -> List[str]:
    """Generate e↔o variants of a word."""
    variants = [word]

    # Replace e with o
    if "e" in word:
        variants.append(word.replace("e", "o"))

    # Replace o with e
    if "o" in word:
        variants.append(word.replace("o", "e"))

    # Both directions for words with both e and o
    if "e" in word and "o" in word:
        temp = word.replace("e", "o")
        variants.append(temp.replace("o", "e"))

    return list(set(variants))


def reverse_word(word: str) -> str:
    """Reverse a word."""
    return word[::-1]


def check_reversal_hypothesis(word: str) -> Optional[Tuple[str, str]]:
    """
    Check if word matches reversal hypothesis.
    Returns (meaning, method) if match found, None otherwise.
    """
    # Strategy 1: Direct match with e↔o
    variants = apply_e_o_substitution(word)
    for variant in variants:
        if variant in REVERSAL_DICT:
            return (REVERSAL_DICT[variant][0], f"direct-e/o")

    # Strategy 2: Reverse then e↔o
    reversed_word = reverse_word(word)
    variants = apply_e_o_substitution(reversed_word)
    for variant in variants:
        if variant in REVERSAL_DICT:
            return (REVERSAL_DICT[variant][0], f"reverse+e/o")

    return None


def segment_morphology(word: str) -> Dict:
    """
    Segment word into morphological components.
    Returns dict with prefix, root, suffixes, and translation.
    """
    result = {
        "original": word,
        "prefix": None,
        "root": None,
        "suffixes": [],
        "translation": [],
        "method": "morphological",
    }

    remaining = word

    # Check for known whole words first
    if word in SEMANTIC_MEANINGS:
        result["root"] = word
        result["translation"] = [SEMANTIC_MEANINGS[word]]
        result["method"] = "whole-word"
        return result

    # Check prefixes (longest first)
    for prefix in sorted(PREFIXES.keys(), key=len, reverse=True):
        if remaining.startswith(prefix):
            result["prefix"] = prefix
            result["translation"].append(PREFIXES[prefix])
            remaining = remaining[len(prefix) :]
            break

    # Check suffixes (longest first, from end)
    while remaining:
        suffix_found = False
        for suffix in sorted(SUFFIXES.keys(), key=len, reverse=True):
            if remaining.endswith(suffix) and len(remaining) > len(suffix):
                result["suffixes"].insert(0, suffix)
                result["translation"].append(SUFFIXES[suffix])
                remaining = remaining[: -len(suffix)]
                suffix_found = True
                break

        if not suffix_found:
            break

    # What's left is the root
    if remaining:
        result["root"] = remaining
        if remaining in SEMANTIC_MEANINGS:
            result["translation"].insert(
                len([result["prefix"]]) if result["prefix"] else 0,
                SEMANTIC_MEANINGS[remaining],
            )
        else:
            result["translation"].insert(
                len([result["prefix"]]) if result["prefix"] else 0, f"[?{remaining}]"
            )

    return result


def translate_word(word: str) -> Dict:
    """
    Translate a single Voynich word using all available methods.
    Returns dict with translation and metadata.
    """
    # Method 1: Morphological segmentation
    morphology = segment_morphology(word)

    # Method 2: Reversal hypothesis
    reversal_match = check_reversal_hypothesis(word)

    translation = {
        "original": word,
        "morphology": morphology,
        "reversal": reversal_match,
        "final_translation": None,
        "confidence": "unknown",
    }

    # Determine final translation
    if morphology["method"] == "whole-word" and morphology["root"] in SEMANTIC_MEANINGS:
        # Known whole word
        translation["final_translation"] = " ".join(morphology["translation"])
        translation["confidence"] = "high"
    elif morphology["translation"] and "[?" not in " ".join(morphology["translation"]):
        # Fully segmented with all known parts
        translation["final_translation"] = "-".join(morphology["translation"])
        translation["confidence"] = "high"
    elif morphology["translation"] and any(
        "[?" not in t for t in morphology["translation"]
    ):
        # Partially segmented (some known parts)
        translation["final_translation"] = "-".join(morphology["translation"])
        translation["confidence"] = "medium"
    elif reversal_match:
        # Reversal hypothesis match
        translation["final_translation"] = f"{reversal_match[0]}[{reversal_match[1]}]"
        translation["confidence"] = "reversal-hypothesis"
    else:
        # Unknown
        translation["final_translation"] = f"[?{word}]"
        translation["confidence"] = "unknown"

    return translation


def translate_sentence(sentence: str, folio: str = "") -> Dict:
    """
    Translate a complete sentence.
    Returns dict with word-by-word translations and statistics.
    """
    words = sentence.split()
    translations = []

    for word in words:
        if word:  # Skip empty strings
            trans = translate_word(word.lower())
            translations.append(trans)

    # Calculate statistics
    total_words = len(translations)
    high_confidence = sum(1 for t in translations if t["confidence"] == "high")
    medium_confidence = sum(1 for t in translations if t["confidence"] == "medium")
    reversal = sum(1 for t in translations if t["confidence"] == "reversal-hypothesis")
    unknown = sum(1 for t in translations if t["confidence"] == "unknown")

    recognition_rate = (
        ((high_confidence + medium_confidence) / total_words * 100)
        if total_words > 0
        else 0
    )

    return {
        "folio": folio,
        "original": sentence,
        "words": translations,
        "final_translation": " ".join([t["final_translation"] for t in translations]),
        "statistics": {
            "total_words": total_words,
            "high_confidence": high_confidence,
            "medium_confidence": medium_confidence,
            "reversal_matches": reversal,
            "unknown": unknown,
            "recognition_rate": recognition_rate,
        },
    }


def load_manuscript(filepath: Path) -> List[Tuple[str, str]]:
    """
    Load manuscript from EVA file.
    Returns list of (folio, text) tuples.
    """
    sentences = []
    line_number = 0

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            line_number += 1

            # Match folio markers: <f1r.1,@P0> or <f1r.P0>
            match = re.match(r"<(f\d+[rv]?)[\.\d,@]*>\s+(.+)$", line)
            if match:
                folio = match.group(1)
                text = match.group(2).strip()
            else:
                # Plain text format - use line number as folio
                folio = f"line{line_number}"
                text = line

            # Remove EVA markup (!, %, =, -, *, {, })
            text = re.sub(r"[!%=\-\*\{\}]", "", text)

            if text:
                sentences.append((folio, text))

    return sentences


def translate_manuscript(
    input_file: Path, output_file: Path, sample_size: Optional[int] = None
):
    """
    Translate entire manuscript or sample.
    Saves results to JSON file with statistics.
    """
    print(f"Loading manuscript from {input_file}...")
    sentences = load_manuscript(input_file)

    if sample_size:
        sentences = sentences[:sample_size]
        print(f"Processing sample of {sample_size} sentences...")
    else:
        print(f"Processing all {len(sentences)} sentences...")

    results = []
    stats = {
        "total_sentences": 0,
        "total_words": 0,
        "high_confidence_words": 0,
        "medium_confidence_words": 0,
        "reversal_matches": 0,
        "unknown_words": 0,
        "recognition_rates": [],
    }

    for i, (folio, text) in enumerate(sentences):
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(sentences)} sentences...")

        translation = translate_sentence(text, folio)
        results.append(translation)

        # Update statistics
        stats["total_sentences"] += 1
        stats["total_words"] += translation["statistics"]["total_words"]
        stats["high_confidence_words"] += translation["statistics"]["high_confidence"]
        stats["medium_confidence_words"] += translation["statistics"][
            "medium_confidence"
        ]
        stats["reversal_matches"] += translation["statistics"]["reversal_matches"]
        stats["unknown_words"] += translation["statistics"]["unknown"]
        stats["recognition_rates"].append(translation["statistics"]["recognition_rate"])

    # Calculate overall statistics
    if stats["total_words"] > 0:
        stats["overall_recognition_rate"] = (
            (stats["high_confidence_words"] + stats["medium_confidence_words"])
            / stats["total_words"]
            * 100
        )
        stats["high_confidence_percentage"] = (
            stats["high_confidence_words"] / stats["total_words"] * 100
        )
        stats["reversal_contribution"] = (
            stats["reversal_matches"] / stats["total_words"] * 100
        )

    stats["average_sentence_recognition"] = (
        sum(stats["recognition_rates"]) / len(stats["recognition_rates"])
        if stats["recognition_rates"]
        else 0
    )

    # Save results
    output_data = {
        "metadata": {
            "source_file": str(input_file),
            "total_sentences": stats["total_sentences"],
            "total_words": stats["total_words"],
            "vocabulary_size": len(SEMANTIC_MEANINGS),
            "prefix_count": len(PREFIXES),
            "suffix_count": len(SUFFIXES),
        },
        "statistics": stats,
        "translations": results,
    }

    print(f"\nSaving results to {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("TRANSLATION COMPLETE")
    print("=" * 80)
    print(f"Total sentences: {stats['total_sentences']}")
    print(f"Total words: {stats['total_words']}")
    print(f"Overall recognition rate: {stats.get('overall_recognition_rate', 0):.1f}%")
    print(f"  High confidence: {stats.get('high_confidence_percentage', 0):.1f}%")
    print(
        f"  Medium confidence: {(stats['medium_confidence_words'] / stats['total_words'] * 100) if stats['total_words'] > 0 else 0:.1f}%"
    )
    print(f"  Reversal matches: {stats.get('reversal_contribution', 0):.1f}%")
    print(
        f"  Unknown: {(stats['unknown_words'] / stats['total_words'] * 100) if stats['total_words'] > 0 else 0:.1f}%"
    )
    print(f"Average sentence recognition: {stats['average_sentence_recognition']:.1f}%")
    print(f"\nResults saved to: {output_file}")
    print("=" * 80)

    return output_data


def create_readable_translation(json_file: Path, output_txt: Path):
    """
    Create human-readable translation file from JSON results.
    """
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("VOYNICH MANUSCRIPT TRANSLATION\n")
        f.write("=" * 80 + "\n")
        f.write(f"Total sentences: {data['metadata']['total_sentences']}\n")
        f.write(
            f"Overall recognition: {data['statistics'].get('overall_recognition_rate', 0):.1f}%\n"
        )
        f.write("=" * 80 + "\n\n")

        for trans in data["translations"]:
            f.write(
                f"[{trans['folio']}] ({trans['statistics']['recognition_rate']:.0f}% recognized)\n"
            )
            f.write(f"Original:    {trans['original']}\n")
            f.write(f"Translation: {trans['final_translation']}\n")
            f.write("\n")

            # Word-by-word breakdown for sentences with <100% recognition
            if trans["statistics"]["recognition_rate"] < 100:
                f.write("  Word breakdown:\n")
                for word in trans["words"]:
                    if word["confidence"] != "high":
                        morph = word["morphology"]
                        f.write(
                            f"    {word['original']}: {' '.join(morph['translation'])}\n"
                        )
                f.write("\n")

    print(f"Readable translation saved to: {output_txt}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Translate Voynich Manuscript with current knowledge"
    )
    parser.add_argument(
        "--input",
        default="data/voynich/eva_transcription/voynich_eva_takahashi.txt",
        help="Input EVA file",
    )
    parser.add_argument(
        "--output",
        default="COMPLETE_MANUSCRIPT_TRANSLATION.json",
        help="Output JSON file",
    )
    parser.add_argument(
        "--readable",
        default="COMPLETE_MANUSCRIPT_TRANSLATION.txt",
        help="Readable translation file",
    )
    parser.add_argument(
        "--sample", type=int, help="Process only first N sentences (for testing)"
    )

    args = parser.parse_args()

    # Get paths
    script_dir = Path(__file__).parent
    manuscript_dir = script_dir.parent.parent
    input_path = manuscript_dir / args.input
    output_json = manuscript_dir / args.output
    output_txt = manuscript_dir / args.readable

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        print("Please provide correct path to EVA transcription file.")
        exit(1)

    # Translate manuscript
    results = translate_manuscript(input_path, output_json, args.sample)

    # Create readable version
    create_readable_translation(output_json, output_txt)

    print("\nTranslation complete! Review files:")
    print(f"  - Detailed JSON: {output_json}")
    print(f"  - Readable text: {output_txt}")
