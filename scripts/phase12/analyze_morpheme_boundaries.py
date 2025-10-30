#!/usr/bin/env python3
"""
Phase 12: Morpheme Boundary Analysis
Analyze prefix/suffix productivity and identify compound structures
"""

import re
from collections import Counter, defaultdict


def load_voynich_text(filepath):
    """Load EVA transcription"""
    words = []
    current_section = None

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            folio_match = re.match(r"<f(\d+[rv]?)>", line)
            if folio_match:
                folio_num = int(re.match(r"\d+", folio_match.group(1)).group())
                if folio_num <= 66:
                    current_section = "herbal"
                elif 67 <= folio_num <= 73:
                    current_section = "astronomical"
                elif 75 <= folio_num <= 84:
                    current_section = "biological"
                elif 85 <= folio_num <= 116:
                    current_section = "pharmaceutical"
                continue

            line_words = re.findall(r"\b[a-z]+\b", line.lower())
            for word in line_words:
                if len(word) >= 3:
                    words.append({"word": word, "section": current_section})

    return words


def get_validated_affixes():
    """Return known validated affixes from previous phases"""
    return {
        "prefixes": {
            "qok": {"type": "genitive", "validated": True, "phase": 8},
            "qot": {"type": "genitive", "validated": True, "phase": 8},
        },
        "suffixes": {
            "dy": {"type": "verbal", "validated": True, "phase": 8},
            "al": {"type": "locative", "validated": True, "phase": 8},
            "ol": {"type": "locative", "validated": True, "phase": 8},
            "ar": {"type": "directional", "validated": True, "phase": 8},
            "or": {"type": "instrumental", "validated": True, "phase": 8},
            "ain": {"type": "definiteness", "validated": True, "phase": 8},
            "iin": {"type": "definiteness", "validated": True, "phase": 8},
            "aiin": {"type": "definiteness", "validated": True, "phase": 8},
        },
    }


def analyze_prefix_productivity(words_list, prefix, min_stem_length=2):
    """Analyze how productively a prefix combines with different stems"""
    word_strings = [w["word"] for w in words_list]

    # Find words starting with this prefix
    prefix_words = [
        w
        for w in word_strings
        if w.startswith(prefix) and len(w) > len(prefix) + min_stem_length
    ]

    # Extract stems
    stems = Counter([w[len(prefix) :] for w in prefix_words])

    # Count total occurrences
    total_prefix_uses = len(prefix_words)
    unique_stems = len(stems)

    # Calculate productivity ratio
    productivity = unique_stems / total_prefix_uses if total_prefix_uses > 0 else 0

    # Find most common stems
    top_stems = stems.most_common(20)

    return {
        "prefix": prefix,
        "total_uses": total_prefix_uses,
        "unique_stems": unique_stems,
        "productivity": productivity,
        "top_stems": top_stems,
        "stem_frequencies": stems,
    }


def analyze_suffix_productivity(words_list, suffix, min_root_length=2):
    """Analyze how productively a suffix combines with different roots"""
    word_strings = [w["word"] for w in words_list]

    # Find words ending with this suffix
    suffix_words = [
        w
        for w in word_strings
        if w.endswith(suffix) and len(w) > len(suffix) + min_root_length
    ]

    # Extract roots
    roots = Counter([w[: -len(suffix)] for w in suffix_words])

    total_suffix_uses = len(suffix_words)
    unique_roots = len(roots)

    productivity = unique_roots / total_suffix_uses if total_suffix_uses > 0 else 0

    top_roots = roots.most_common(20)

    return {
        "suffix": suffix,
        "total_uses": total_suffix_uses,
        "unique_roots": unique_roots,
        "productivity": productivity,
        "top_roots": top_roots,
        "root_frequencies": roots,
    }


def identify_compound_structures(words_list):
    """Identify potential prefix-root-suffix compounds"""
    validated_affixes = get_validated_affixes()
    prefixes = list(validated_affixes["prefixes"].keys())
    suffixes = list(validated_affixes["suffixes"].keys())

    word_strings = [w["word"] for w in words_list]
    compounds = []

    for word in word_strings:
        # Check for prefix
        found_prefix = None
        for prefix in prefixes:
            if word.startswith(prefix) and len(word) > len(prefix) + 2:
                found_prefix = prefix
                break

        # Check for suffix
        found_suffix = None
        for suffix in suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                found_suffix = suffix
                break

        # If has both prefix and suffix
        if found_prefix and found_suffix:
            if len(word) > len(found_prefix) + len(found_suffix) + 1:
                root = word[len(found_prefix) : -len(found_suffix)]
                if len(root) >= 2:
                    compounds.append(
                        {
                            "word": word,
                            "prefix": found_prefix,
                            "root": root,
                            "suffix": found_suffix,
                            "structure": f"{found_prefix}-{root}-{found_suffix}",
                        }
                    )

    return compounds


def analyze_near_validated_compounds():
    """Analyze specific near-validated elements that may be compounds"""
    return [
        {"word": "olkedy", "hypothesis": "ol-kedy", "prefix": "ol", "root": "kedy"},
        {"word": "olchedy", "hypothesis": "ol-chedy", "prefix": "ol", "root": "chedy"},
        {"word": "cthor", "hypothesis": "ct-hor", "prefix": "ct", "root": "hor"},
        {"word": "otchol", "hypothesis": "ot-chol", "prefix": "ot", "root": "chol"},
        {"word": "otchor", "hypothesis": "ot-chor", "prefix": "ot", "root": "chor"},
    ]


def test_compound_hypothesis(words_list, word, prefix, root):
    """Test whether a compound hypothesis is supported by data"""
    word_strings = [w["word"] for w in words_list]

    # Count occurrences
    word_count = word_strings.count(word)

    # Count prefix usage
    prefix_words = [
        w for w in word_strings if w.startswith(prefix) and len(w) > len(prefix) + 1
    ]
    prefix_count = len(prefix_words)
    prefix_unique = len(set(prefix_words))

    # Count root as standalone or in compounds
    root_exact = word_strings.count(root)
    root_compound = sum(1 for w in word_strings if root in w and w != root)

    return {
        "word": word,
        "hypothesis": f"{prefix}-{root}",
        "word_count": word_count,
        "prefix_uses": prefix_count,
        "prefix_unique_stems": prefix_unique,
        "root_exact": root_exact,
        "root_in_compounds": root_compound,
        "prefix_productive": prefix_unique / prefix_count if prefix_count > 0 else 0,
        "root_productive": root_compound / (root_exact + root_compound)
        if (root_exact + root_compound) > 0
        else 0,
    }


def main():
    print("Phase 12: Morpheme Boundary Analysis")
    print("=" * 80)

    # Load data
    eva_file = (
        "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/ZL3b-n.txt"
    )
    words = load_voynich_text(eva_file)
    print(f"\nLoaded {len(words)} words from EVA transcription\n")

    validated_affixes = get_validated_affixes()

    print("=" * 80)
    print("ANALYSIS 1: Validated Prefix Productivity")
    print("=" * 80)

    print("\nAnalyzing validated prefixes:\n")

    for prefix_name, prefix_data in validated_affixes["prefixes"].items():
        result = analyze_prefix_productivity(words, prefix_name)
        print(f"{prefix_name.upper()} ({prefix_data['type']}):")
        print(f"  Total uses: {result['total_uses']}")
        print(f"  Unique stems: {result['unique_stems']}")
        print(f"  Productivity: {result['productivity']:.3f}")
        print(f"  Top 10 stems:")
        for stem, count in result["top_stems"][:10]:
            print(f"    {prefix_name}-{stem}: {count} occurrences")
        print()

    print("=" * 80)
    print("ANALYSIS 2: Validated Suffix Productivity")
    print("=" * 80)

    print("\nAnalyzing validated suffixes:\n")

    for suffix_name, suffix_data in validated_affixes["suffixes"].items():
        result = analyze_suffix_productivity(words, suffix_name)
        print(f"{suffix_name.upper()} ({suffix_data['type']}):")
        print(f"  Total uses: {result['total_uses']}")
        print(f"  Unique roots: {result['unique_roots']}")
        print(f"  Productivity: {result['productivity']:.3f}")
        print(f"  Top 10 roots:")
        for root, count in result["top_roots"][:10]:
            print(f"    {root}-{suffix_name}: {count} occurrences")
        print()

    print("=" * 80)
    print("ANALYSIS 3: Additional Prefix Candidates")
    print("=" * 80)

    # Test additional potential prefixes
    candidate_prefixes = ["ol", "ot", "ct", "ok", "ch", "sh", "da"]

    print("\nTesting potential productive prefixes:\n")
    print(
        f"{'Prefix':<10} {'Total Uses':<12} {'Unique Stems':<15} {'Productivity':<12}"
    )
    print("-" * 55)

    for prefix in candidate_prefixes:
        result = analyze_prefix_productivity(words, prefix)
        if result["total_uses"] >= 50:
            print(
                f"{prefix:<10} {result['total_uses']:<12} {result['unique_stems']:<15} {result['productivity']:<12.3f}"
            )

    print("\n" + "=" * 80)
    print("ANALYSIS 4: Near-Validated Compound Hypothesis Testing")
    print("=" * 80)

    near_validated_compounds = analyze_near_validated_compounds()

    print("\nTesting compound hypotheses for near-validated elements:\n")

    for compound in near_validated_compounds:
        result = test_compound_hypothesis(
            words, compound["word"], compound["prefix"], compound["root"]
        )
        print(f"{result['word'].upper()} -> {result['hypothesis']}")
        print(f"  Word frequency: {result['word_count']}")
        print(
            f"  Prefix '{compound['prefix']}' productivity: {result['prefix_uses']} uses, "
            f"{result['prefix_unique_stems']} unique stems ({result['prefix_productive']:.3f})"
        )
        print(
            f"  Root '{compound['root']}': {result['root_exact']} exact, "
            f"{result['root_in_compounds']} in compounds ({result['root_productive']:.1%} productivity)"
        )
        print()

    print("=" * 80)
    print("ANALYSIS 5: Full Compound Structure Detection")
    print("=" * 80)

    compounds = identify_compound_structures(words)

    print(f"\nFound {len(compounds)} prefix-root-suffix compounds")
    print("\nTop 20 most frequent compound structures:\n")

    compound_freqs = Counter([c["structure"] for c in compounds])
    print(f"{'Structure':<30} {'Count':<10}")
    print("-" * 45)

    for structure, count in compound_freqs.most_common(20):
        print(f"{structure:<30} {count:<10}")

    print("\n" + "=" * 80)
    print("RECOMMENDATIONS FOR PHASE 12")
    print("=" * 80)

    print("\n1. VALIDATE PRODUCTIVE PREFIXES:")
    print("   - ol- (locative prefix, appears in olkedy, olchedy)")
    print("   - ot- (potential prefix, appears in otchol, otchor)")
    print("   - ct- (potential prefix, appears in cthor)")

    print("\n2. RE-TEST NEAR-VALIDATED AS COMPOUNDS:")
    print("   - olkedy (ol-kedy) - Test as locative + root compound")
    print("   - cthor (ct-hor) - Test as prefix + instrumental compound")

    print("\n3. IDENTIFY NEW COMPOUND CANDIDATES:")
    print("   - Search for high-frequency prefix-root-suffix combinations")
    print("   - Test compounds with n>=10")

    print("\n4. VALIDATE ADDITIONAL AFFIXES:")
    print("   - Test suffixes with >100 unique roots")
    print("   - Test prefixes with >50 unique stems")


if __name__ == "__main__":
    main()
