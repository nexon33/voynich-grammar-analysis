#!/usr/bin/env python3
"""
Phase 14A: Identify Vowel-Initial Candidate Morphemes

This script identifies high-frequency vowel-initial stems that warrant validation
as morphological elements, following the Phase 13 discovery that ot- (the /ot/
allomorph of {OL}) preferentially combines with vowel-initial stems.

Strategy:
1. Extract all words beginning with vowels (a, e, i, o, u, y)
2. Calculate frequency, standalone usage, morphological productivity
3. Filter by n >= 20 (sufficient statistical power)
4. Exclude already-validated elements
5. Rank by total frequency and ot- co-occurrence
6. Generate prioritized candidate list
"""

import re
from collections import Counter, defaultdict


def load_eva_transcription(filepath):
    """Load EVA transcription, returning list of words with section context."""
    words_with_context = []
    current_section = None

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Detect section markers (simplified)
            if "<f" in line and "r>" in line:
                folio_match = re.search(r"<f(\d+)([rv]?)>", line)
                if folio_match:
                    folio_num = int(folio_match.group(1))
                    if folio_num <= 66:
                        current_section = "herbal"
                    elif 67 <= folio_num <= 73:
                        current_section = "astronomical"
                    elif 75 <= folio_num <= 84:
                        current_section = "biological"
                    elif folio_num >= 85:
                        current_section = "pharmaceutical"
                continue

            # Extract words (remove markup)
            words = re.findall(r"[a-z]+", line.lower())
            for word in words:
                if len(word) >= 2:  # Minimum length
                    words_with_context.append(
                        {"word": word, "section": current_section}
                    )

    return words_with_context


def is_vowel_initial(word):
    """Check if word starts with vowel."""
    vowels = {"a", "e", "i", "o", "u", "y"}
    return word[0] in vowels if word else False


def calculate_morphological_productivity(target_word, all_words):
    """Calculate percentage of target appearances in compound forms."""
    total_count = 0
    compound_count = 0

    for word in all_words:
        if word == target_word:
            total_count += 1
        elif target_word in word and len(word) > len(target_word):
            total_count += 1
            compound_count += 1

    if total_count == 0:
        return 0.0, 0, 0

    productivity = (compound_count / total_count) * 100
    return productivity, total_count, compound_count


def get_ot_cooccurrence(stem, all_words):
    """Count how often stem appears with ot- prefix."""
    ot_stem_pattern = f"ot{stem}"
    count = sum(
        1
        for word in all_words
        if word == ot_stem_pattern or word.startswith(ot_stem_pattern)
    )
    return count


def analyze_vowel_initial_candidates(words_with_context):
    """Identify and analyze vowel-initial candidates."""

    # Extract word strings
    word_strings = [w["word"] for w in words_with_context]

    # Already validated elements to exclude
    validated = {
        "aiin",  # 9/10
        "or",  # 10/10
        "ar",  # function word
        "okal",  # 10/10 (starts with o)
        "am",  # 9/10 particle
        "ory",  # 8/10 particle
    }

    # Count vowel-initial words
    vowel_initial_words = [w for w in word_strings if is_vowel_initial(w)]
    word_freq = Counter(vowel_initial_words)

    candidates = []

    print(f"Total vowel-initial words: {len(vowel_initial_words)}")
    print(f"Unique vowel-initial words: {len(word_freq)}")
    print()

    # Analyze each high-frequency vowel-initial word
    for word, exact_count in word_freq.most_common(200):
        if word in validated:
            continue

        if exact_count < 20:  # Minimum threshold
            break

        # Calculate productivity
        productivity, total_count, compound_count = (
            calculate_morphological_productivity(word, word_strings)
        )

        standalone_count = exact_count
        standalone_pct = (
            (standalone_count / total_count * 100) if total_count > 0 else 0
        )

        # Get ot- co-occurrence
        ot_count = get_ot_cooccurrence(word, word_strings)

        # Calculate section distribution
        word_sections = [w["section"] for w in words_with_context if w["word"] == word]
        section_counts = Counter(word_sections)
        num_sections = len(section_counts)

        candidates.append(
            {
                "word": word,
                "exact_count": exact_count,
                "total_count": total_count,
                "compound_count": compound_count,
                "productivity": productivity,
                "standalone_pct": standalone_pct,
                "ot_cooccurrence": ot_count,
                "num_sections": num_sections,
                "section_dist": dict(section_counts),
                "initial_vowel": word[0],
            }
        )

    return candidates


def prioritize_candidates(candidates):
    """Prioritize candidates by frequency and ot- co-occurrence."""

    # Calculate priority score: total_count + 2*ot_cooccurrence
    for c in candidates:
        c["priority_score"] = c["total_count"] + (2 * c["ot_cooccurrence"])

    # Sort by priority score
    candidates.sort(key=lambda x: x["priority_score"], reverse=True)

    return candidates


def print_candidate_report(candidates):
    """Print formatted candidate report."""

    print("=" * 100)
    print("PHASE 14A: VOWEL-INITIAL CANDIDATE IDENTIFICATION")
    print("=" * 100)
    print()

    print(f"Total candidates identified (n>=20): {len(candidates)}")
    print()

    # Summary by initial vowel
    vowel_counts = Counter(c["initial_vowel"] for c in candidates)
    print("Distribution by initial vowel:")
    for vowel in sorted(vowel_counts.keys()):
        print(f"  {vowel}-initial: {vowel_counts[vowel]} candidates")
    print()

    # High priority candidates (top 15)
    print("=" * 100)
    print("TOP 15 PRIORITY CANDIDATES")
    print("=" * 100)
    print()
    print(
        f"{'Rank':<5} {'Word':<10} {'Total':<7} {'Exact':<7} {'Prod%':<8} {'Stand%':<8} {'ot-':<6} {'Sects':<6} {'Priority':<9} {'Type Hint'}"
    )
    print("-" * 100)

    for i, c in enumerate(candidates[:15], 1):
        # Determine likely type
        if c["productivity"] > 30:
            type_hint = "ROOT"
        elif c["standalone_pct"] > 80:
            type_hint = "FUNCTION?"
        elif c["productivity"] < 15:
            type_hint = "FUNCTION?"
        else:
            type_hint = "MIXED"

        print(
            f"{i:<5} {c['word']:<10} {c['total_count']:<7} {c['exact_count']:<7} "
            f"{c['productivity']:<8.1f} {c['standalone_pct']:<8.1f} "
            f"{c['ot_cooccurrence']:<6} {c['num_sections']:<6} "
            f"{c['priority_score']:<9} {type_hint}"
        )

    print()
    print("=" * 100)
    print("DETAILED ANALYSIS: TOP 10 CANDIDATES")
    print("=" * 100)
    print()

    for i, c in enumerate(candidates[:10], 1):
        print(f"{i}. {c['word'].upper()}")
        print(f"   Total occurrences: {c['total_count']}")
        print(f"   Exact matches: {c['exact_count']}")
        print(f"   Compound uses: {c['compound_count']}")
        print(f"   Morphological productivity: {c['productivity']:.1f}%")
        print(f"   Standalone frequency: {c['standalone_pct']:.1f}%")
        print(f"   ot- co-occurrence: {c['ot_cooccurrence']}")
        print(f"   Sections present: {c['num_sections']}/4")
        print(f"   Section distribution: {c['section_dist']}")
        print(f"   Priority score: {c['priority_score']}")

        # Initial assessment
        if c["productivity"] > 50:
            assessment = "HIGHLY PRODUCTIVE ROOT (>50% compounds)"
        elif c["productivity"] > 30:
            assessment = "PRODUCTIVE ROOT (30-50% compounds)"
        elif c["standalone_pct"] > 80 and c["productivity"] < 15:
            assessment = "LIKELY FUNCTION WORD (<15% variants, >80% standalone)"
        elif c["productivity"] < 15:
            assessment = "POSSIBLE FUNCTION WORD (low productivity)"
        else:
            assessment = "MIXED USAGE (15-30% productivity)"

        print(f"   Initial assessment: {assessment}")
        print()

    print("=" * 100)
    print("CANDIDATE CATEGORIES")
    print("=" * 100)
    print()

    # Categorize by productivity
    high_prod = [c for c in candidates if c["productivity"] > 30]
    med_prod = [c for c in candidates if 15 <= c["productivity"] <= 30]
    low_prod = [c for c in candidates if c["productivity"] < 15]

    print(f"HIGH PRODUCTIVITY ROOTS (>30%): {len(high_prod)} candidates")
    print(f"  Top 5: {', '.join(c['word'] for c in high_prod[:5])}")
    print()

    print(f"MEDIUM PRODUCTIVITY (15-30%): {len(med_prod)} candidates")
    print(f"  Top 5: {', '.join(c['word'] for c in med_prod[:5])}")
    print()

    print(f"LOW PRODUCTIVITY FUNCTION WORDS? (<15%): {len(low_prod)} candidates")
    print(f"  Top 5: {', '.join(c['word'] for c in low_prod[:5])}")
    print()

    # High ot- co-occurrence
    high_ot = sorted(candidates, key=lambda x: x["ot_cooccurrence"], reverse=True)[:10]
    print("HIGHEST OT- CO-OCCURRENCE (validates allomorphy hypothesis):")
    for c in high_ot:
        print(
            f"  {c['word']:<10} ot- count: {c['ot_cooccurrence']:<4} (total: {c['total_count']})"
        )
    print()


def save_candidate_list(candidates, output_file):
    """Save detailed candidate list to file."""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Phase 14A: Vowel-Initial Candidate List\n\n")
        f.write("## Summary\n\n")
        f.write(f"Total candidates identified (n>=20): {len(candidates)}\n\n")

        f.write("## Top 15 Priority Candidates\n\n")
        f.write(
            "| Rank | Word | Total | Exact | Prod% | Stand% | ot- | Sects | Priority | Assessment |\n"
        )
        f.write(
            "|------|------|-------|-------|-------|--------|-----|-------|----------|------------|\n"
        )

        for i, c in enumerate(candidates[:15], 1):
            if c["productivity"] > 30:
                assessment = "ROOT"
            elif c["standalone_pct"] > 80 and c["productivity"] < 15:
                assessment = "FUNCTION?"
            else:
                assessment = "MIXED"

            f.write(
                f"| {i} | {c['word']} | {c['total_count']} | {c['exact_count']} | "
                f"{c['productivity']:.1f} | {c['standalone_pct']:.1f} | "
                f"{c['ot_cooccurrence']} | {c['num_sections']} | "
                f"{c['priority_score']} | {assessment} |\n"
            )

        f.write("\n## Complete Candidate List\n\n")
        for i, c in enumerate(candidates, 1):
            f.write(f"### {i}. {c['word'].upper()}\n\n")
            f.write(f"- **Total occurrences**: {c['total_count']}\n")
            f.write(f"- **Exact matches**: {c['exact_count']}\n")
            f.write(f"- **Morphological productivity**: {c['productivity']:.1f}%\n")
            f.write(f"- **Standalone frequency**: {c['standalone_pct']:.1f}%\n")
            f.write(f"- **ot- co-occurrence**: {c['ot_cooccurrence']}\n")
            f.write(f"- **Sections**: {c['num_sections']}/4 - {c['section_dist']}\n")
            f.write(f"- **Priority score**: {c['priority_score']}\n\n")


def main():
    transcription_file = "data/voynich/eva_transcription/ZL3b-n.txt"
    output_file = "PHASE14A_CANDIDATE_LIST.md"

    print("Loading EVA transcription...")
    words_with_context = load_eva_transcription(transcription_file)
    print(f"Loaded {len(words_with_context)} words\n")

    print("Analyzing vowel-initial candidates...")
    candidates = analyze_vowel_initial_candidates(words_with_context)

    print("Prioritizing candidates...")
    candidates = prioritize_candidates(candidates)

    print_candidate_report(candidates)

    print(f"Saving candidate list to {output_file}...")
    save_candidate_list(candidates, output_file)

    print("\nPhase 14A complete!")
    print(f"Identified {len(candidates)} vowel-initial candidates with n>=20")
    print(f"Top candidates: {', '.join(c['word'] for c in candidates[:5])}")


if __name__ == "__main__":
    main()
