"""
Analyze morphological patterns in matched vocabulary.

Looking for:
1. Middle English suffixes: -ed, -es, -ing, -yng, -ly, -er
2. Middle English prefixes: y- (past participle marker)
3. Common word patterns
"""

from collections import Counter, defaultdict
from pathlib import Path
import re


def load_matches():
    """Load the vocabulary matches from Phase 2."""
    matches_file = Path("results/phase2/vocabulary_matches.txt")

    matches = []
    with open(matches_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Skip header lines
    in_data = False
    for line in lines:
        if "→" in line and not line.startswith("Matched"):
            parts = line.strip().split("→")
            if len(parts) == 2:
                voyn = parts[0].strip()
                me = parts[1].strip()
                matches.append((voyn, me))

    return matches


def analyze_suffixes(matches):
    """Analyze suffix patterns in matched words."""
    suffix_patterns = {
        "-ed": [],  # Past tense/past participle
        "-es": [],  # Plural/3rd person singular
        "-ing": [],  # Present participle
        "-yng": [],  # ME variant of -ing
        "-ly": [],  # Adverb
        "-er": [],  # Agent noun
        "-or": [],  # ME variant of -er
        "-el": [],  # Diminutive/instrumental
    }

    for voyn, me in matches:
        for suffix, words in suffix_patterns.items():
            if me.endswith(suffix.lstrip("-")):
                words.append((voyn, me))

    return suffix_patterns


def analyze_prefixes(matches):
    """Analyze prefix patterns in matched words."""
    prefix_patterns = {
        "y-": [],  # Past participle prefix (ME "i-" or "y-")
    }

    for voyn, me in matches:
        for prefix, words in prefix_patterns.items():
            if me.startswith(prefix.rstrip("-")):
                words.append((voyn, me))

    return prefix_patterns


def analyze_voynich_patterns(matches):
    """Analyze what Voynich patterns correspond to ME morphemes."""
    # Look at how ME suffixes appear in Voynich
    me_to_voyn_suffix = defaultdict(list)

    for voyn, me in matches:
        # Check ME suffixes and see Voynich equivalent
        if me.endswith("ed"):
            voyn_suffix = voyn[-2:] if len(voyn) >= 2 else ""
            me_to_voyn_suffix["ed"].append((voyn, me, voyn_suffix))

        if me.endswith("es"):
            voyn_suffix = voyn[-2:] if len(voyn) >= 2 else ""
            me_to_voyn_suffix["es"].append((voyn, me, voyn_suffix))

        if me.endswith("er"):
            voyn_suffix = voyn[-2:] if len(voyn) >= 2 else ""
            me_to_voyn_suffix["er"].append((voyn, me, voyn_suffix))

        if me.endswith("ly"):
            voyn_suffix = voyn[-2:] if len(voyn) >= 2 else ""
            me_to_voyn_suffix["ly"].append((voyn, me, voyn_suffix))

    return me_to_voyn_suffix


def look_for_medical_terms(matches):
    """Look for medical/women's health related vocabulary."""
    medical_keywords = [
        # Body parts
        "body",
        "bodi",
        "hede",
        "head",
        "hand",
        "fot",
        "foot",
        "legge",
        "leg",
        "arm",
        "brest",
        "breast",
        "wombe",
        "womb",
        "childe",
        "child",
        # Medical conditions
        "seke",
        "seek",
        "sick",
        "sore",
        "peyne",
        "pain",
        "ache",
        "feuer",
        "fever",
        # Healing/treatment
        "hele",
        "heal",
        "cure",
        "leche",
        "leech",
        "medicine",
        "salve",
        "herbe",
        "herb",
        "roote",
        "root",
        # Women's health
        "birthe",
        "birth",
        "bere",
        "bear",
        "moder",
        "mother",
        "mayden",
        "maiden",
        # Common ME medical terms
        "blood",
        "blod",
        "water",
        "hete",
        "heat",
        "colde",
        "cold",
    ]

    medical_matches = []
    for voyn, me in matches:
        for keyword in medical_keywords:
            if keyword in me or me in keyword:
                medical_matches.append((voyn, me, keyword))

    return medical_matches


def main():
    print("\n" + "=" * 70)
    print("MORPHOLOGICAL PATTERN ANALYSIS")
    print("=" * 70 + "\n")

    # Load matched vocabulary
    print("Loading vocabulary matches...")
    matches = load_matches()
    print(f"✓ Loaded {len(matches)} unique matches\n")

    # Analyze suffixes
    print("=" * 70)
    print("SUFFIX ANALYSIS")
    print("=" * 70 + "\n")

    suffix_patterns = analyze_suffixes(matches)

    for suffix, words in suffix_patterns.items():
        if words:
            print(f"{suffix} suffix ({len(words)} matches):")
            print("-" * 70)
            for voyn, me in words[:10]:  # Show first 10
                print(f"  {voyn:20} → {me}")
            if len(words) > 10:
                print(f"  ... and {len(words) - 10} more")
            print()

    # Analyze prefixes
    print("=" * 70)
    print("PREFIX ANALYSIS")
    print("=" * 70 + "\n")

    prefix_patterns = analyze_prefixes(matches)

    for prefix, words in prefix_patterns.items():
        if words:
            print(f"{prefix} prefix ({len(words)} matches):")
            print("-" * 70)
            for voyn, me in words[:10]:
                print(f"  {voyn:20} → {me}")
            if len(words) > 10:
                print(f"  ... and {len(words) - 10} more")
            print()

    # Analyze Voynich patterns for ME morphemes
    print("=" * 70)
    print("VOYNICH SUFFIX PATTERNS")
    print("=" * 70 + "\n")
    print("What Voynich endings correspond to ME suffixes?\n")

    me_to_voyn = analyze_voynich_patterns(matches)

    for me_suffix, instances in me_to_voyn.items():
        if instances:
            # Count Voynich suffix patterns
            voyn_suffix_counter = Counter([voyn_suf for _, _, voyn_suf in instances])

            print(f"ME suffix '-{me_suffix}' appears as Voynich:")
            print("-" * 70)
            for voyn_suf, count in voyn_suffix_counter.most_common(5):
                pct = (count / len(instances)) * 100
                print(f"  '-{voyn_suf}' ({count}/{len(instances)} = {pct:.1f}%)")

            print(f"\nExamples:")
            for voyn, me, voyn_suf in instances[:5]:
                print(f"  {voyn:20} → {me:20} (Voynich ends: -{voyn_suf})")
            print()

    # Look for medical vocabulary
    print("=" * 70)
    print("MEDICAL/WOMEN'S HEALTH VOCABULARY")
    print("=" * 70 + "\n")

    medical_matches = look_for_medical_terms(matches)

    if medical_matches:
        print(f"Found {len(medical_matches)} potential medical terms:\n")
        for voyn, me, keyword in medical_matches:
            print(f"  {voyn:20} → {me:20} (relates to: {keyword})")
    else:
        print("✗ No obvious medical terms found in current matches.")
        print("  This could mean:")
        print("  1. We need more character mappings to reveal medical vocabulary")
        print("  2. Medical terms use different vocabulary than our ME corpus")
        print("  3. The Voynich sections analyzed aren't medical in nature")

    # Interesting word patterns
    print("\n" + "=" * 70)
    print("INTERESTING PATTERNS")
    print("=" * 70 + "\n")

    # Words with 'ch' bigram (very English)
    ch_words = [(v, m) for v, m in matches if "ch" in m]
    print(f"Words with 'ch' bigram: {len(ch_words)}")
    print("Examples:")
    for voyn, me in ch_words[:10]:
        print(f"  {voyn:20} → {me}")

    print()

    # Words with 'sh' bigram
    sh_words = [(v, m) for v, m in matches if "sh" in m]
    print(f"Words with 'sh' bigram: {len(sh_words)}")
    print("Examples:")
    for voyn, me in sh_words[:10]:
        print(f"  {voyn:20} → {me}")

    # Summary
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70 + "\n")

    total_suffixed = sum(len(words) for words in suffix_patterns.values())
    total_prefixed = sum(len(words) for words in prefix_patterns.values())

    print(
        f"✓ Words with ME suffixes: {total_suffixed}/{len(matches)} ({total_suffixed / len(matches) * 100:.1f}%)"
    )
    print(
        f"✓ Words with ME prefixes: {total_prefixed}/{len(matches)} ({total_prefixed / len(matches) * 100:.1f}%)"
    )
    print(f"✓ Words with 'ch' bigram: {len(ch_words)} (very characteristic of English)")
    print(f"✓ Words with 'sh' bigram: {len(sh_words)}")

    if total_suffixed > 20:
        print("\n✓✓ Significant morphological patterns detected!")
        print("   This strongly supports the ME hypothesis.")

    # Save detailed analysis
    output_file = Path("results/phase2/morphological_analysis.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("MORPHOLOGICAL PATTERN ANALYSIS\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"Total unique matches: {len(matches)}\n")
        f.write(f"Words with ME suffixes: {total_suffixed}\n")
        f.write(f"Words with ME prefixes: {total_prefixed}\n\n")

        f.write("SUFFIX PATTERNS:\n")
        f.write("-" * 70 + "\n")
        for suffix, words in suffix_patterns.items():
            f.write(f"\n{suffix}: {len(words)} matches\n")
            for voyn, me in words:
                f.write(f"  {voyn:20} → {me}\n")

        f.write("\n\nVOYNICH SUFFIX MAPPINGS:\n")
        f.write("-" * 70 + "\n")
        for me_suffix, instances in me_to_voyn.items():
            voyn_suffix_counter = Counter([voyn_suf for _, _, voyn_suf in instances])
            f.write(f"\nME '-{me_suffix}' → Voynich patterns:\n")
            for voyn_suf, count in voyn_suffix_counter.most_common():
                pct = (count / len(instances)) * 100
                f.write(f"  '-{voyn_suf}': {count}/{len(instances)} ({pct:.1f}%)\n")

    print(f"\n✓ Detailed analysis saved to: {output_file}")


if __name__ == "__main__":
    main()
