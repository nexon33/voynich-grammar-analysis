#!/usr/bin/env python3
"""
Deep vocabulary analysis of top unknown Voynich words.

Strategy:
1. Apply ALL known transforms to see possible ME words
2. Test against expanded vocabulary sources:
   - Regional dialects (Northern, Southern, Kentish, West Midlands)
   - Latin medical terms
   - French pharmacological terms
   - Abbreviations and contractions
3. Look for phonetic patterns
4. Check compound word possibilities
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from itertools import product
import re


def load_manuscript():
    """Load manuscript and get word frequencies."""
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"

    with open(
        results_dir / "full_manuscript_translation.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)

    all_words = []
    for section in data["sections"]:
        words = section["original"].split()
        all_words.extend(words)

    # Count frequencies
    word_freq = Counter()
    for word in all_words:
        word_clean = word.lower().strip(".,;:!?")
        if len(word_clean) >= 2:
            word_freq[word_clean] += 1

    return word_freq


def reverse_all_transforms(voynich_word):
    """
    Apply ALL reverse transforms systematically.
    Returns dict of possibilities by transform type.
    """
    results = {
        "direct_eo": set(),
        "direct_consonants": set(),
        "reversed_eo": set(),
        "reversed_consonants": set(),
        "multi": set(),
    }

    # Helper: reverse e↔o
    def reverse_eo(w):
        variants = {w}
        eo_positions = [(i, c) for i, c in enumerate(w) if c in ["e", "o"]]
        if len(eo_positions) <= 5:
            for combo in product(["e", "o"], repeat=len(eo_positions)):
                variant = list(w)
                for (pos, _), new_char in zip(eo_positions, combo):
                    variant[pos] = new_char
                variants.add("".join(variant))
                if len(variants) >= 30:
                    break
        else:
            variants.add(w.replace("o", "e"))
            variants.add(w.replace("e", "o"))
        return list(variants)

    # Helper: reverse consonants
    def reverse_consonants(w):
        variants = {w}
        # ch↔sh
        variants.add(w.replace("ch", "sh"))
        variants.add(w.replace("sh", "ch"))
        # t↔d
        variants.add(w.replace("t", "d"))
        variants.add(w.replace("d", "t"))
        # c↔k
        variants.add(w.replace("c", "k"))
        variants.add(w.replace("k", "c"))
        # Additional: th↔dh (voicing)
        variants.add(w.replace("th", "dh"))
        variants.add(w.replace("dh", "th"))
        # gh↔h (ME spelling)
        variants.add(w.replace("gh", "h"))
        variants.add(w.replace("h", "gh"))
        return list(variants)

    # Path 1: Direct (no reversal), e↔o only
    for eo_var in reverse_eo(voynich_word):
        results["direct_eo"].add(eo_var)

    # Path 2: Direct (no reversal), consonants only
    for cons_var in reverse_consonants(voynich_word):
        results["direct_consonants"].add(cons_var)

    # Path 3: Direct, consonants + e↔o
    for cons_var in reverse_consonants(voynich_word):
        for eo_var in reverse_eo(cons_var):
            results["multi"].add(eo_var)

    # Path 4: Reversed word, e↔o
    reversed_word = voynich_word[::-1]
    for eo_var in reverse_eo(reversed_word):
        results["reversed_eo"].add(eo_var)

    # Path 5: Reversed word, consonants
    for cons_var in reverse_consonants(reversed_word):
        results["reversed_consonants"].add(cons_var)

    # Path 6: Reversed word, consonants + e↔o
    for cons_var in reverse_consonants(reversed_word):
        for eo_var in reverse_eo(cons_var):
            results["multi"].add(eo_var)

    return results


def build_expanded_vocabulary():
    """
    Build comprehensive ME vocabulary from multiple sources.
    """
    vocab = {
        # Standard ME medical terms (already tested)
        "standard_medical": {
            "take",
            "tak",
            "make",
            "mak",
            "root",
            "rote",
            "leaf",
            "lef",
            "seed",
            "sed",
            "sede",
            "herb",
            "herbe",
            "blood",
            "blod",
            "pain",
            "peyn",
            "sore",
            "sor",
            "heal",
            "hele",
        },
        # Regional dialectal variations
        "northern_dialect": {
            # Northern ME often uses 'a' where southern uses 'o'
            "tak",
            "mak",
            "stan",
            "banes",  # take, make, stone, bones
            "hame",
            "mare",
            "gude",
            "kirk",  # home, more, good, church
            "til",
            "fra",
            "qwhat",
            "qwen",  # to, from, what, when
        },
        "southern_dialect": {
            # Southern ME preserves older forms
            "ychon",
            "yclept",
            "ywis",
            "iwis",  # each, called, certainly
            "vor",
            "vrom",  # for, from (f→v)
        },
        # Latin medical terms (common in medieval medicine)
        "latin_medical": {
            "radix",
            "folia",
            "flores",
            "semen",  # root, leaves, flowers, seed
            "sanguis",
            "dolor",
            "morbus",
            "cura",  # blood, pain, disease, cure
            "medicina",
            "potio",
            "unguentum",
            "emplastrum",  # medicine, potion, ointment, plaster
            "infusio",
            "decoctio",
            "pulvis",  # infusion, decoction, powder
            "aqua",
            "oleum",
            "mel",
            "vinum",  # water, oil, honey, wine
            "calida",
            "frigida",
            "sicca",
            "humida",  # hot, cold, dry, wet
        },
        # French medical/pharmaceutical terms
        "french_medical": {
            "racine",
            "feuille",
            "fleur",
            "graine",  # root, leaf, flower, seed
            "herbe",
            "poudre",
            "jus",
            "suc",  # herb, powder, juice, sap
            "douleur",
            "maladie",
            "remede",
            "guerir",  # pain, disease, remedy, heal
        },
        # Common abbreviations in medieval texts
        "abbreviations": {
            # Medieval scribes abbreviated frequently
            "q",
            "qd",
            "qt",
            "qm",  # que, quod, quot, quam
            "p",
            "pp",
            "ppt",
            "pr",  # per, propter, praeparatio, pro
            "m",
            "md",
            "mn",  # medicine, medicamentum, manus
            "r",
            "rx",  # recipe (take thou)
            "aa",
            "ana",  # of each (pharmaceutical notation)
            "qs",
            "ss",  # quantum sufficit, semis (half)
        },
        # Compound word elements
        "prefixes": {
            "a-",
            "be-",
            "for-",
            "mis-",
            "un-",
            "y-",
            "i-",
            "with-",
            "over-",
            "under-",
            "out-",
        },
        "suffixes": {
            "-ly",
            "-lich",
            "-ness",
            "-ship",
            "-dom",
            "-hood",
            "-en",
            "-ed",
            "-ing",
            "-er",
            "-est",
        },
        # Body parts - expanded
        "body_parts": {
            "hed",
            "heved",
            "hevid",  # head
            "ere",
            "eare",  # ear
            "ye",
            "eye",
            "eyen",  # eye(s)
            "nase",
            "nose",  # nose
            "mouth",
            "muthe",  # mouth
            "tunge",
            "tonge",  # tongue
            "throte",
            "throte",  # throat
            "nek",
            "necke",  # neck
            "brest",
            "breste",  # breast
            "herte",
            "hert",  # heart
            "liver",
            "lyver",  # liver
            "milt",
            "splene",  # spleen
            "wombe",
            "wome",  # womb
            "bely",
            "belee",  # belly
            "guttis",
            "bowels",  # guts, bowels
        },
        # Verbs - action/process words
        "process_verbs": {
            "grind",
            "grynde",
            "stamp",
            "stampe",
            "pound",
            "poune",
            "boil",
            "boile",
            "seth",
            "sethe",  # seethe
            "bren",
            "burn",
            "brenne",  # burn
            "wasch",
            "wash",
            "clense",  # wash, cleanse
            "meng",
            "mingle",
            "medel",  # mix, meddle
            "strayn",
            "streyne",  # strain
            "tempere",
            "tempre",  # temper, moderate
        },
        # Common function words - dialect variants
        "function_words": {
            "and",
            "ant",
            "ond",  # and
            "the",
            "þe",
            "that",
            "þat",  # the, that
            "with",
            "wiþ",
            "mid",  # with
            "of",
            "off",  # of
            "to",
            "til",  # to
            "for",
            "vor",  # for
            "in",
            "inn",  # in
            "it",
            "hit",  # it
            "is",
            "ys",
            "es",  # is
            "be",
            "ben",
            "beon",  # be
            "have",
            "haven",
            "habben",  # have
        },
    }

    # Flatten into single set
    all_vocab = set()
    for category, words in vocab.items():
        if isinstance(words, set):
            all_vocab.update(words)

    return vocab, all_vocab


def analyze_word_deeply(voynich_word, freq, all_vocab, vocab_by_category):
    """Deep analysis of a single word."""

    print(f"\n{'=' * 80}")
    print(f"ANALYZING: '{voynich_word}' (frequency: {freq})")
    print(f"{'=' * 80}\n")

    # Get all possible transforms
    transforms = reverse_all_transforms(voynich_word)

    # Check each transform type for matches
    findings = defaultdict(list)

    for transform_type, possibilities in transforms.items():
        for possibility in possibilities:
            if possibility in all_vocab:
                # Find which category
                for cat, words in vocab_by_category.items():
                    if isinstance(words, set) and possibility in words:
                        findings[transform_type].append(
                            {"word": possibility, "category": cat}
                        )
                        break

    # Report findings
    if findings:
        print(f"✓ MATCHES FOUND!")
        for transform_type, matches in findings.items():
            print(f"\n  {transform_type}:")
            for match in matches[:5]:  # Limit to top 5
                print(f"    → {match['word']:20s} ({match['category']})")
        return True
    else:
        print(f"✗ No direct vocabulary matches")

        # Show most plausible candidates
        print(f"\n  Most plausible forms (if word exists in ME):")
        if transforms["reversed_eo"]:
            print(f"    Reversed + e↔o: {list(transforms['reversed_eo'])[:5]}")
        if transforms["direct_eo"]:
            print(f"    Direct e↔o: {list(transforms['direct_eo'])[:3]}")

        return False


def main():
    print("=" * 80)
    print("DEEP VOCABULARY ANALYSIS OF TOP UNKNOWN VOYNICH WORDS")
    print("=" * 80)
    print()
    print("Strategy:")
    print("  1. Expand vocabulary: Regional dialects, Latin, French, abbreviations")
    print("  2. Apply ALL transforms to top unknown words")
    print("  3. Identify patterns in successful vs. unsuccessful matches")
    print()

    # Load data
    word_freq = load_manuscript()
    vocab_by_category, all_vocab = build_expanded_vocabulary()

    print(f"Manuscript: {len(word_freq)} unique words")
    print(f"Expanded vocabulary: {len(all_vocab)} ME terms")
    print()

    # Get top unknown words (excluding the 3 we already know)
    known_decoded = {"or", "dol", "tol"}

    top_unknown = []
    for word, freq in word_freq.most_common(30):
        if word not in known_decoded:
            top_unknown.append((word, freq))

    print(
        f"Analyzing top 30 unknown words (covering ~{sum(f for w, f in top_unknown) / sum(word_freq.values()) * 100:.1f}% of manuscript)"
    )
    print()

    # Analyze each
    decoded_count = 0
    decoded_instances = 0

    for word, freq in top_unknown:
        if analyze_word_deeply(word, freq, all_vocab, vocab_by_category):
            decoded_count += 1
            decoded_instances += freq

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    print(f"Top 30 unknown words analyzed")
    print(f"Decoded: {decoded_count} words")
    print(f"Still unknown: {30 - decoded_count} words")
    print(f"Coverage: {decoded_instances} instances")
    print()

    if decoded_count > 5:
        print("✓✓✓ EXCELLENT PROGRESS!")
        print(f"    Found {decoded_count} new words through expanded vocabulary")
    elif decoded_count > 2:
        print("✓✓ GOOD PROGRESS")
        print(f"    Found {decoded_count} new words")
    elif decoded_count > 0:
        print("✓ SOME PROGRESS")
        print(f"    Found {decoded_count} word(s)")
    else:
        print("⚠️  LIMITED MATCHES")
        print("    Expanded vocabulary didn't match top unknown words")
        print("    → Suggests specialized jargon or different approach needed")

    print()


if __name__ == "__main__":
    main()
