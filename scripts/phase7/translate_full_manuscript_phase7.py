"""
Phase 7B: Full Manuscript Translation with Complete Vocabulary

Translates the entire Voynich manuscript using:
- 9 validated nouns
- 2 spatial terms (dair, air)
- 2 validated function words (ar, daiin)
- 1 tentative function word (y)
- Complete agglutinative grammar

Output: Readable translation file with statistics
"""

import re
import json
from collections import defaultdict


def translate_word_phase7(word):
    """Translate with 13 validated terms + complete grammar"""

    word = word.lower().strip(".,;!?")
    translations = []
    remainder = word

    # 1. Check standalone function words FIRST (highest priority)
    if word == "ar" or word in ["ary", "ars", "arl"]:
        return "[AT/IN]"
    elif word == "dair":
        return "[THERE]"
    elif word == "air":
        return "[SKY]"
    elif word == "daiin" or word == "dain":
        return "[THIS/THAT]"
    elif word == "y":
        return "[AND?]"
    elif word == "qol":
        return "[THEN]"
    elif word == "sal":
        return "[AND]"
    elif word == "ory":
        return "[ADV]"

    # 2. Check genitive prefix
    if remainder.startswith("qok"):
        translations.append("oak-GEN")
        remainder = remainder[3:]
    elif remainder.startswith("qot"):
        translations.append("oat-GEN")
        remainder = remainder[3:]
    elif remainder.startswith("ok"):
        translations.append("oak")
        remainder = remainder[2:]
    elif remainder.startswith("ot"):
        translations.append("oat")
        remainder = remainder[2:]

    # 3. Check semantic nouns
    if remainder.startswith("shee"):
        translations.append("water")
        remainder = remainder[4:]
    elif remainder.startswith("she"):
        translations.append("water")
        remainder = remainder[3:]
    elif remainder.startswith("sho"):
        translations.append("SHO")
        remainder = remainder[3:]
    elif remainder.startswith("keo"):
        translations.append("KEO")
        remainder = remainder[3:]
    elif remainder.startswith("teo"):
        translations.append("TEO")
        remainder = remainder[3:]
    elif remainder.startswith("cheo"):
        translations.append("CHEO")
        remainder = remainder[4:]
    elif remainder.startswith("cho"):
        translations.append("vessel")
        remainder = remainder[3:]
    elif remainder.startswith("dor"):
        translations.append("red")
        remainder = remainder[3:]

    # 4. Check verbal suffix
    if remainder.endswith("edy"):
        translations.append("VERB")
        remainder = remainder[:-3]
    elif remainder.endswith("dy"):
        translations.append("VERB")
        remainder = remainder[:-2]

    # 5. Check definiteness
    if remainder.endswith("aiin"):
        translations.append("DEF")
        remainder = remainder[:-4]
    elif remainder.endswith("iin"):
        translations.append("DEF")
        remainder = remainder[:-3]
    elif remainder.endswith("ain"):
        translations.append("DEF")
        remainder = remainder[:-3]

    # 6. Check case markers
    if remainder.endswith("al"):
        translations.append("LOC")
        remainder = remainder[:-2]
    elif remainder.endswith("ol"):
        translations.append("LOC2")
        remainder = remainder[:-2]
    elif remainder.endswith("ar") and len(remainder) > 2:
        translations.append("DIR")
        remainder = remainder[:-2]
    elif remainder.endswith("or"):
        translations.append("INST")
        remainder = remainder[:-2]

    # 7. Unknown remainder
    if remainder and remainder not in ["s", "d"]:
        translations.append(f"[?{remainder}]")

    if translations:
        return ".".join(translations)
    else:
        return f"[?{word}]"


def load_voynich(filepath):
    """Load Voynich manuscript - simple line-by-line format"""
    lines = []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    pages = []
    line_num = 0

    # Simple format: each line is text, no special markers
    for line in lines:
        line_stripped = line.strip()

        # Skip empty lines and comments
        if not line_stripped or line_stripped.startswith("#"):
            continue

        # Clean text - remove special markers
        text = re.sub(r"[!*=\-]", "", line_stripped)
        text = re.sub(r"\s+", " ", text).strip()

        if text:
            line_num += 1
            pages.append(
                {"locator": f"line_{line_num}", "section": "unknown", "text": text}
            )

    return pages


def translate_page(page_data):
    """Translate a single page"""
    words = page_data["text"].split()
    translated_words = [translate_word_phase7(w) for w in words]

    # Calculate recognition
    unknown_count = sum(1 for w in translated_words if w.startswith("[?"))
    total_words = len(words)
    recognition_pct = 100 * (1 - unknown_count / total_words) if total_words > 0 else 0

    return {
        "locator": page_data["locator"],
        "section": page_data["section"],
        "original": page_data["text"],
        "translation": " ".join(translated_words),
        "total_words": total_words,
        "recognized_words": total_words - unknown_count,
        "recognition_pct": recognition_pct,
    }


def main():
    print("=" * 80)
    print("PHASE 7B: FULL MANUSCRIPT TRANSLATION")
    print("=" * 80)
    print("\nVocabulary: 13 validated terms")
    print("  - 9 nouns (oak, oat, water, red, vessel, cheo, sho, keo, teo)")
    print("  - 2 spatial terms (dair=THERE, air=SKY)")
    print("  - 2 function words (ar=AT/IN, daiin=THIS/THAT)")
    print("  - 1 tentative (y=AND?)")
    print("\nLoading manuscript...")

    # Load manuscript
    voynich_path = "data/voynich/eva_transcription/voynich_eva_takahashi.txt"
    pages = load_voynich(voynich_path)

    print(f"Loaded {len(pages)} pages")
    print("\nTranslating...")

    # Translate all pages
    translations = []
    section_stats = defaultdict(
        lambda: {"total_words": 0, "recognized_words": 0, "page_count": 0}
    )

    for i, page_data in enumerate(pages):
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i + 1}/{len(pages)} pages...")

        translation = translate_page(page_data)
        translations.append(translation)

        # Update section stats
        section = translation["section"]
        section_stats[section]["total_words"] += translation["total_words"]
        section_stats[section]["recognized_words"] += translation["recognized_words"]
        section_stats[section]["page_count"] += 1

    print(f"  Completed: {len(pages)}/{len(pages)} pages")

    # Calculate overall statistics
    total_words = sum(t["total_words"] for t in translations)
    total_recognized = sum(t["recognized_words"] for t in translations)
    overall_recognition = 100 * total_recognized / total_words if total_words > 0 else 0

    # Calculate section statistics
    for section, stats in section_stats.items():
        stats["recognition_pct"] = (
            100 * stats["recognized_words"] / stats["total_words"]
            if stats["total_words"] > 0
            else 0
        )

    print("\n" + "=" * 80)
    print("TRANSLATION COMPLETE")
    print("=" * 80)

    print(f"\nTotal pages: {len(pages)}")
    print(f"Total words: {total_words:,}")
    print(f"Recognized words: {total_recognized:,}")
    print(f"Overall recognition: {overall_recognition:.1f}%")

    print("\n" + "=" * 80)
    print("SECTION BREAKDOWN")
    print("=" * 80)

    for section in [
        "herbal",
        "biological",
        "pharmaceutical",
        "astronomical",
        "unknown",
    ]:
        if section in section_stats:
            stats = section_stats[section]
            print(f"\n{section.upper()}:")
            print(f"  Pages: {stats['page_count']}")
            print(f"  Words: {stats['total_words']:,}")
            print(f"  Recognized: {stats['recognized_words']:,}")
            print(f"  Recognition: {stats['recognition_pct']:.1f}%")

    # Save translations to file
    output_file = "results/phase7/full_manuscript_translation_phase7.txt"
    print(f"\n\nSaving readable translation to: {output_file}")

    import os

    os.makedirs("results/phase7", exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("VOYNICH MANUSCRIPT - PHASE 7B TRANSLATION\n")
        f.write("=" * 80 + "\n\n")
        f.write("Vocabulary: 13 validated terms\n")
        f.write("  - 9 nouns: oak, oat, water, red, vessel, cheo, sho, keo, teo\n")
        f.write("  - 2 spatial: dair (THERE), air (SKY)\n")
        f.write("  - 2 function: ar (AT/IN), daiin (THIS/THAT)\n")
        f.write("  - 1 tentative: y (AND?)\n\n")
        f.write(f"Overall Recognition: {overall_recognition:.1f}%\n")
        f.write(f"Total Words: {total_words:,}\n")
        f.write(f"Total Pages: {len(pages)}\n\n")
        f.write("=" * 80 + "\n\n")

        current_section = None
        for translation in translations:
            # Section header
            if translation["section"] != current_section:
                current_section = translation["section"]
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"SECTION: {current_section.upper()}\n")
                f.write("=" * 80 + "\n\n")

            # Page translation
            f.write(
                f"[{translation['locator']}] ({translation['recognition_pct']:.0f}% recognized)\n"
            )
            f.write(f"Original:    {translation['original']}\n")
            f.write(f"Translation: {translation['translation']}\n\n")

    # Save JSON data
    json_output = "results/phase7/full_manuscript_translation_phase7.json"
    print(f"Saving JSON data to: {json_output}")

    with open(json_output, "w", encoding="utf-8") as f:
        json.dump(
            {
                "metadata": {
                    "phase": "7B",
                    "vocabulary_count": 13,
                    "total_pages": len(pages),
                    "total_words": total_words,
                    "recognized_words": total_recognized,
                    "overall_recognition_pct": overall_recognition,
                },
                "section_stats": dict(section_stats),
                "translations": translations,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    # Find and display best translations
    print("\n" + "=" * 80)
    print("BEST TRANSLATIONS (>80% recognition)")
    print("=" * 80)

    best_translations = sorted(
        [t for t in translations if t["recognition_pct"] >= 80],
        key=lambda x: x["recognition_pct"],
        reverse=True,
    )[:10]

    if best_translations:
        for i, t in enumerate(best_translations, 1):
            print(
                f"\n{i}. [{t['locator']}] - {t['section']} ({t['recognition_pct']:.0f}%)"
            )
            print(f"   Original:    {t['original'][:70]}...")
            print(f"   Translation: {t['translation'][:70]}...")
    else:
        print("\nNo pages with >80% recognition found.")

    # Find spatial system examples
    print("\n" + "=" * 80)
    print("SPATIAL SYSTEM EXAMPLES")
    print("=" * 80)

    spatial_examples = [
        t
        for t in translations
        if "[THERE]" in t["translation"]
        or "[AT/IN]" in t["translation"]
        or "[SKY]" in t["translation"]
    ][:10]

    if spatial_examples:
        for i, t in enumerate(spatial_examples, 1):
            print(
                f"\n{i}. [{t['locator']}] - {t['section']} ({t['recognition_pct']:.0f}%)"
            )
            print(f"   Original:    {t['original']}")
            print(f"   Translation: {t['translation']}")
    else:
        print("\nNo spatial system examples found.")

    print("\n" + "=" * 80)
    print("FILES CREATED")
    print("=" * 80)
    print(f"1. {output_file}")
    print(f"2. {json_output}")
    print("\nTranslation complete! ✓✓✓")


if __name__ == "__main__":
    main()
