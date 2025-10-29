"""
Build Middle English Medical Vocabulary Database

Extract medical terminology from ME corpus and create searchable database.
Focus on: herbs, body parts, conditions, treatments, women's health.
"""

from pathlib import Path
import re
import json
from collections import Counter, defaultdict


def load_me_corpus_words():
    """Load all words from ME corpus."""
    corpus_dir = Path("data/middle_english_corpus/cmepv/middle_english_text_cmepv/sgml")
    sgml_files = list(corpus_dir.glob("*.sgm"))

    all_words = []
    print(f"Reading {len(sgml_files)} ME texts...")

    for sgml_file in sgml_files:
        with open(sgml_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            # Remove SGML tags
            text = re.sub(r"<[^>]+>", " ", content)
            words = re.findall(r"[a-z]+", text.lower())
            all_words.extend(words)

    return Counter(all_words)


def extract_medical_vocabulary(word_freq):
    """Extract medical terms based on keywords and patterns."""

    medical_categories = {
        "herbs": [],
        "body_parts": [],
        "conditions": [],
        "treatments": [],
        "actions": [],
        "substances": [],
        "women_health": [],
        "general_medical": [],
    }

    # Known ME herb names and variants
    herb_keywords = [
        "betony",
        "betoyne",
        "betonie",
        "camomile",
        "camomyle",
        "kamomile",
        "comfrey",
        "cumfrey",
        "fennel",
        "fenel",
        "henbane",
        "hennebone",
        "lavender",
        "lavendel",
        "mint",
        "mynte",
        "pennyroyal",
        "penyroyal",
        "rue",
        "rwe",
        "sage",
        "sauge",
        "valerian",
        "valeriane",
        "vervain",
        "vervayne",
        "wormwood",
        "wermode",
        "yarrow",
        "yarwe",
        "herb",
        "herbe",
        "wort",
        "worte",
        "root",
        "roote",
        "rote",
        "leaf",
        "lef",
        "leef",
        "flower",
        "flour",
        "floure",
        "seed",
        "sede",
    ]

    # Body parts (especially women's health)
    body_keywords = [
        "womb",
        "wombe",
        "breast",
        "brest",
        "breste",
        "head",
        "hede",
        "hed",
        "belly",
        "bely",
        "blood",
        "blod",
        "blode",
        "bone",
        "bon",
        "child",
        "childe",
        "heart",
        "herte",
        "hand",
        "hond",
        "foot",
        "fot",
        "fet",
        "leg",
        "legge",
        "arm",
        "arme",
        "eye",
        "eyen",
        "ear",
        "ere",
        "mouth",
        "mouthe",
        "body",
        "bodi",
        "bodye",
    ]

    # Medical conditions
    condition_keywords = [
        "ache",
        "ake",
        "fever",
        "feuer",
        "fevere",
        "pain",
        "peyne",
        "payne",
        "sore",
        "sor",
        "sick",
        "seke",
        "sik",
        "ill",
        "ylle",
        "wound",
        "wounde",
        "swelling",
        "swellyng",
        "burn",
        "brenne",
        "cold",
        "colde",
        "heat",
        "hete",
        "disease",
        "disese",
    ]

    # Treatments and actions
    treatment_keywords = [
        "heal",
        "hele",
        "heale",
        "cure",
        "curen",
        "medicine",
        "medicyne",
        "salve",
        "salfe",
        "plaster",
        "plastre",
        "drink",
        "drynke",
        "bath",
        "bathe",
        "poultice",
        "pultis",
        "boil",
        "boyle",
        "mix",
        "mixe",
        "grind",
        "grynde",
        "take",
        "tak",
        "apply",
        "applye",
        "lay",
        "leye",
    ]

    # Women's health specific
    women_keywords = [
        "birth",
        "birthe",
        "bear",
        "bere",
        "beren",
        "mother",
        "moder",
        "modir",
        "maiden",
        "mayden",
        "woman",
        "womman",
        "wymman",
        "wife",
        "wyf",
        "midwife",
        "midwyf",
        "pregnancy",
        "pregnaunce",
        "labor",
        "labour",
        "nurse",
        "norice",
    ]

    # Substances
    substance_keywords = [
        "water",
        "watur",
        "wine",
        "wyn",
        "oil",
        "oyle",
        "honey",
        "hony",
        "milk",
        "mylk",
        "vinegar",
        "vynegre",
        "salt",
        "salte",
        "butter",
        "buttre",
    ]

    # Build dictionary of keyword → category
    keyword_map = {}
    for kw in herb_keywords:
        keyword_map[kw] = "herbs"
    for kw in body_keywords:
        keyword_map[kw] = "body_parts"
    for kw in condition_keywords:
        keyword_map[kw] = "conditions"
    for kw in treatment_keywords:
        keyword_map[kw] = "treatments"
    for kw in women_keywords:
        keyword_map[kw] = "women_health"
    for kw in substance_keywords:
        keyword_map[kw] = "substances"

    # Search for medical terms in corpus
    print("\nSearching for medical vocabulary...")

    for word, freq in word_freq.items():
        # Check direct matches
        if word in keyword_map:
            category = keyword_map[word]
            medical_categories[category].append(
                {"word": word, "frequency": freq, "type": "direct_match"}
            )

        # Check partial matches (contains medical keywords)
        else:
            for keyword, category in keyword_map.items():
                if keyword in word and len(word) > len(keyword):
                    # Likely a compound or inflected form
                    medical_categories[category].append(
                        {
                            "word": word,
                            "frequency": freq,
                            "type": "partial_match",
                            "keyword": keyword,
                        }
                    )
                    break  # Only add to one category

    # Also add words with medical suffixes
    medical_suffixes = ["ache", "sore", "wort", "roote", "herbe"]
    for word, freq in word_freq.items():
        for suffix in medical_suffixes:
            if word.endswith(suffix) and word not in [
                item["word"] for cat in medical_categories.values() for item in cat
            ]:
                if "wort" in suffix or "roote" in suffix or "herbe" in suffix:
                    category = "herbs"
                else:
                    category = "conditions"

                medical_categories[category].append(
                    {
                        "word": word,
                        "frequency": freq,
                        "type": "suffix_match",
                        "suffix": suffix,
                    }
                )

    return medical_categories


def find_medical_context_words(word_freq, medical_terms):
    """Find words that frequently appear near medical terms."""
    # This would require context analysis from original texts
    # For now, we'll mark high-frequency words that might be medical

    general_medical = []

    # Words likely to appear in medical contexts
    context_patterns = [
        "take",
        "tak",
        "make",
        "use",
        "good",
        "beste",
        "moche",
        "much",
        "litel",
        "little",
        "ofte",
        "often",
        "day",
        "night",
        "tyme",
        "time",
        "hour",
        "houre",
    ]

    for pattern in context_patterns:
        if pattern in word_freq:
            general_medical.append(
                {
                    "word": pattern,
                    "frequency": word_freq[pattern],
                    "type": "context_word",
                }
            )

    return general_medical


def main():
    print("=" * 70)
    print("BUILDING MIDDLE ENGLISH MEDICAL VOCABULARY DATABASE")
    print("=" * 70 + "\n")

    # Load ME corpus
    print("Loading Middle English corpus...")
    word_freq = load_me_corpus_words()
    print(f"✓ Loaded {len(word_freq):,} unique words")
    print(f"  Total word instances: {sum(word_freq.values()):,}\n")

    # Extract medical vocabulary
    medical_vocab = extract_medical_vocabulary(word_freq)

    # Add general medical context words
    medical_vocab["general_medical"] = find_medical_context_words(
        word_freq, medical_vocab
    )

    # Statistics
    print("=" * 70)
    print("MEDICAL VOCABULARY BY CATEGORY")
    print("=" * 70 + "\n")

    total_terms = 0
    for category, terms in medical_vocab.items():
        if terms:
            print(f"{category.upper().replace('_', ' ')}:")
            print(f"  Found: {len(terms)} terms")

            # Sort by frequency and show top 10
            sorted_terms = sorted(terms, key=lambda x: x["frequency"], reverse=True)
            print(f"  Top terms:")
            for term in sorted_terms[:10]:
                print(f"    {term['word']:20} ({term['frequency']:>7,} occurrences)")
            print()

            total_terms += len(terms)

    print(f"TOTAL MEDICAL TERMS: {total_terms}\n")

    # Save to JSON
    output_dir = Path("results/phase3")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "medical_vocabulary_database.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(medical_vocab, f, indent=2, ensure_ascii=False)

    print(f"✓ Medical vocabulary database saved to: {output_file}")

    # Create searchable text version
    text_file = output_dir / "medical_vocabulary_list.txt"

    with open(text_file, "w", encoding="utf-8") as f:
        f.write("MIDDLE ENGLISH MEDICAL VOCABULARY DATABASE\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total terms: {total_terms}\n\n")

        for category, terms in medical_vocab.items():
            if terms:
                f.write(f"\n{category.upper().replace('_', ' ')}:\n")
                f.write("-" * 70 + "\n")

                sorted_terms = sorted(terms, key=lambda x: x["frequency"], reverse=True)
                for term in sorted_terms:
                    f.write(f"{term['word']:25} {term['frequency']:>8,} occurrences")
                    if term["type"] != "direct_match":
                        f.write(f" ({term['type']})")
                    f.write("\n")

    print(f"✓ Text version saved to: {text_file}")

    # Summary for Phase 3
    print("\n" + "=" * 70)
    print("SUMMARY FOR PHASE 3 TRANSLATION")
    print("=" * 70 + "\n")

    print("Key medical vocabulary to look for in Voynich:")
    print()

    print("HERBS (top 10):")
    herb_terms = sorted(
        medical_vocab["herbs"], key=lambda x: x["frequency"], reverse=True
    )[:10]
    for term in herb_terms:
        print(f"  {term['word']}")

    print("\nBODY PARTS (top 10):")
    body_terms = sorted(
        medical_vocab["body_parts"], key=lambda x: x["frequency"], reverse=True
    )[:10]
    for term in body_terms:
        print(f"  {term['word']}")

    print("\nCONDITIONS (top 10):")
    condition_terms = sorted(
        medical_vocab["conditions"], key=lambda x: x["frequency"], reverse=True
    )[:10]
    for term in condition_terms:
        print(f"  {term['word']}")

    print("\nTREATMENTS (top 10):")
    treatment_terms = sorted(
        medical_vocab["treatments"], key=lambda x: x["frequency"], reverse=True
    )[:10]
    for term in treatment_terms:
        print(f"  {term['word']}")

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70 + "\n")
    print("1. Create selective translation tool")
    print("2. Search for these medical terms in Voynich (with e↔o variations)")
    print("3. Focus on sections where medical terms cluster")
    print("4. Validate findings against ME medical texts")
    print()


if __name__ == "__main__":
    main()
