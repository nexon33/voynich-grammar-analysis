#!/usr/bin/env python3
"""
Phase 12: Validate Productive Prefixes
Test ol-, ot-, ct- as systematic morphological prefixes
"""

import re
from collections import Counter, defaultdict
from scipy import stats


def load_voynich_text(filepath):
    """Load EVA transcription with section markup"""
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
                if len(word) >= 2:
                    words.append({"word": word, "section": current_section})

    return words


def validate_prefix(prefix, words_list, min_stem_length=2):
    """
    Validate a prefix as a systematic morphological element
    Different scoring criteria than roots/function words
    """
    word_strings = [w["word"] for w in words_list]

    # Find all words with this prefix
    prefix_words = [
        w
        for w in word_strings
        if w.startswith(prefix) and len(w) > len(prefix) + min_stem_length
    ]

    if len(prefix_words) == 0:
        return None

    # Extract stems
    stems = Counter([w[len(prefix) :] for w in prefix_words])

    # Scoring criteria for prefixes:
    # 1. PRODUCTIVITY: How many unique stems? (0-2 points)
    #    2 points: >100 unique stems (highly productive)
    #    1 point: 30-100 unique stems
    #    0 points: <30 unique stems

    unique_stems = len(stems)
    if unique_stems > 100:
        productivity_score = 2
    elif unique_stems >= 30:
        productivity_score = 1
    else:
        productivity_score = 0

    # 2. FREQUENCY: Total usage (0-2 points)
    #    2 points: >500 uses
    #    1 point: 100-500 uses
    #    0 points: <100 uses

    total_uses = len(prefix_words)
    if total_uses > 500:
        frequency_score = 2
    elif total_uses >= 100:
        frequency_score = 1
    else:
        frequency_score = 0

    # 3. PRODUCTIVITY RATIO: unique/total (0-2 points)
    #    Higher ratio = more productive (Turkish prefixes: 0.15-0.35)
    #    2 points: >0.25
    #    1 point: 0.15-0.25
    #    0 points: <0.15

    productivity_ratio = unique_stems / total_uses
    if productivity_ratio > 0.25:
        ratio_score = 2
    elif productivity_ratio >= 0.15:
        ratio_score = 1
    else:
        ratio_score = 0

    # 4. VALIDATED STEM COMBINATION: Does it combine with validated roots? (0-2 points)
    validated_roots = {
        "okal",
        "or",
        "dar",
        "dol",
        "chol",
        "keo",
        "teo",
        "she",
        "sho",
        "cho",
        "dor",
        "air",
        "dain",
        "oteey",
        "otchol",
        "kchy",
        "kaiin",
        "kar",
        "kain",
        "kedy",
        "teey",
        "oiin",
        "olchedy",
        "chom",
        "kcho",
        "otchor",
    }

    validated_combinations = 0
    for stem in stems:
        if stem in validated_roots:
            validated_combinations += stems[stem]

    validated_rate = validated_combinations / total_uses if total_uses > 0 else 0

    if validated_rate > 0.15:
        validated_score = 2
    elif validated_rate >= 0.05:
        validated_score = 1
    else:
        validated_score = 0

    # 5. SECTION DISTRIBUTION: Does it appear across sections? (0-2 points)
    section_counts = defaultdict(int)
    for entry in words_list:
        if (
            entry["word"].startswith(prefix)
            and len(entry["word"]) > len(prefix) + min_stem_length
        ):
            if entry["section"]:
                section_counts[entry["section"]] += 1

    sections_present = len([s for s in section_counts if section_counts[s] > 0])

    if sections_present >= 4:
        section_score = 2
    elif sections_present >= 2:
        section_score = 1
    else:
        section_score = 0

    # Total score
    total_score = (
        productivity_score
        + frequency_score
        + ratio_score
        + validated_score
        + section_score
    )

    # Get top stems for reporting
    top_stems = stems.most_common(15)

    return {
        "prefix": prefix,
        "score": total_score,
        "total_uses": total_uses,
        "unique_stems": unique_stems,
        "productivity_ratio": productivity_ratio,
        "validated_combinations": validated_combinations,
        "validated_rate": validated_rate,
        "sections": sections_present,
        "top_stems": top_stems,
        "section_counts": dict(section_counts),
        "scores": {
            "productivity": productivity_score,
            "frequency": frequency_score,
            "ratio": ratio_score,
            "validated": validated_score,
            "section": section_score,
        },
    }


def main():
    print("Phase 12: Prefix Validation")
    print("=" * 80)

    # Load data
    eva_file = (
        "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/ZL3b-n.txt"
    )
    words = load_voynich_text(eva_file)
    print(f"\nLoaded {len(words)} words from EVA transcription\n")

    # Test prefixes
    candidates = ["ol", "ot", "ct"]

    print(f"Testing {len(candidates)} prefix candidates: {', '.join(candidates)}\n")

    print("=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)

    results = []
    for prefix in candidates:
        result = validate_prefix(prefix, words)
        if result:
            results.append(result)

    # Sort by score
    results.sort(key=lambda x: x["score"], reverse=True)

    print("\nSummary Table:\n")
    print(
        f"{'Prefix':<10} {'Score':<8} {'Uses':<8} {'Stems':<8} {'Ratio':<8} {'Val%':<8} {'Sections':<10}"
    )
    print("-" * 70)

    for r in results:
        print(
            f"{r['prefix']:<10} {r['score']}/10  {r['total_uses']:<8} {r['unique_stems']:<8} {r['productivity_ratio']:<8.3f} {r['validated_rate'] * 100:<8.1f} {r['sections']:<10}"
        )

    # Detailed breakdown
    print("\n" + "=" * 80)
    print("DETAILED VALIDATION BREAKDOWN")
    print("=" * 80)

    for r in results:
        print(f"\n{r['prefix'].upper()}- PREFIX - SCORE: {r['score']}/10")
        print("-" * 60)
        print(f"  Total uses: {r['total_uses']}")
        print(f"  Unique stems: {r['unique_stems']} [{r['scores']['productivity']}/2]")
        print(
            f"  Productivity ratio: {r['productivity_ratio']:.3f} [{r['scores']['ratio']}/2]"
        )
        print(f"  Frequency: {r['total_uses']} uses [{r['scores']['frequency']}/2]")
        print(
            f"  Validated combinations: {r['validated_combinations']}/{r['total_uses']} ({r['validated_rate'] * 100:.1f}%) [{r['scores']['validated']}/2]"
        )
        print(f"  Sections: {r['sections']} [{r['scores']['section']}/2]")

        if r["section_counts"]:
            print(f"  Section distribution:")
            for section, count in r["section_counts"].items():
                pct = (count / r["total_uses"]) * 100
                print(f"    {section}: {count} ({pct:.1f}%)")

        print(f"\n  Top 15 stems:")
        for stem, count in r["top_stems"]:
            print(f"    {r['prefix']}-{stem}: {count}")

    print("\n" + "=" * 80)
    print("PHASE 12 PREFIX SUMMARY")
    print("=" * 80)

    validated_count = len([r for r in results if r["score"] >= 8])

    print(f"\nValidated (>=8/10): {validated_count}/{len(candidates)}")

    if validated_count > 0:
        print(f"\nVALIDATED PREFIXES ({validated_count}):")
        for r in results:
            if r["score"] >= 8:
                print(
                    f"  - {r['prefix']}- ({r['score']}/10, {r['total_uses']} uses, {r['unique_stems']} stems)"
                )

    near_validated = [r for r in results if 6 <= r["score"] < 8]
    if near_validated:
        print(f"\nNEAR-VALIDATED PREFIXES ({len(near_validated)}):")
        for r in near_validated:
            print(
                f"  - {r['prefix']}- ({r['score']}/10, {r['total_uses']} uses, {r['unique_stems']} stems)"
            )

    print(
        f"\nTotal validated affixes: {2 + validated_count} prefixes (qok-, qot-, + {validated_count} new)"
    )


if __name__ == "__main__":
    main()
