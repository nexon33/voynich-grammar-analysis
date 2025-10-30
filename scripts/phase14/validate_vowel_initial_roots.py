#!/usr/bin/env python3
"""
Phase 14B: Validate Vowel-Initial Roots

This script properly validates vowel-initial stems as independent morphological
elements, distinguishing them from bound morphemes (suffixes/prefixes).

Focus on candidates from Phase 13 ot- stem analysis:
- edy (162 ot- uses)
- eey (72 ot- uses)
- eedy (68 ot- uses)
- eeedy (98 ot- uses)
- ol (54 ot- uses as stem)
- ain (24 ot- uses as stem)
"""

import re
from collections import Counter
from scipy import stats

# Already validated elements
VALIDATED = {
    "aiin",
    "or",
    "ar",
    "okal",
    "am",
    "ory",
    "dam",
    "chey",
    "cheey",
    "chy",
    "shy",
    "qol",
    "cthy",
    "dar",
    "dol",
    "chol",
    "she",
    "sho",
    "cho",
    "dor",
    "kar",
    "kaiin",
    "kain",
    "kedy",
    "teey",
    "oiin",
    "olchedy",
    "kcho",
    "otchor",
    "chom",
    "shecthy",
}

# Known prefixes (for detecting compound usage)
PREFIXES = {"qok", "qot", "ol", "ot"}

# Known suffixes (for detecting compound usage)
SUFFIXES = {
    "dy",
    "y",
    "al",
    "ol",
    "ar",
    "or",
    "ain",
    "iin",
    "aiin",
    "edy",
    "eey",
    "chy",
    "shy",
    "shey",
}


def load_eva_with_position(filepath):
    """Load EVA transcription with position and section markup."""
    sentences = []
    current_section = None

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Detect folio markers and set section
            folio_match = re.match(r"<f(\d+)([rv]?)>", line)
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

            # Parse text lines: <f1r.1,@P0> text.text.text
            text_match = re.match(r"<f\d+[rv]?\.\d+[^>]*>\s+(.+)$", line)
            if not text_match:
                continue

            text_content = text_match.group(1)

            # Remove EVA markup: <$>, <%>, <!...>, etc.
            text_content = re.sub(r"<[^>]+>", "", text_content)
            text_content = re.sub(
                r"[,;.\[\]:?!]", " ", text_content
            )  # Replace punctuation

            # Extract words as sentence
            words = re.findall(r"[a-z]+", text_content.lower())
            if len(words) >= 2:
                sentence = []
                for i, word in enumerate(words):
                    if len(word) >= 2:
                        position = (
                            "initial"
                            if i == 0
                            else ("final" if i == len(words) - 1 else "medial")
                        )
                        sentence.append(
                            {
                                "word": word,
                                "position": position,
                                "section": current_section,
                            }
                        )
                if sentence:
                    sentences.append(sentence)

    return sentences


def extract_exact_matches(candidate_word, sentences):
    """Extract all exact word matches with context."""
    matches = []
    for sentence in sentences:
        for word_data in sentence:
            if word_data["word"] == candidate_word:
                matches.append(word_data)
    return matches


def find_morphological_variants(candidate_word, sentences):
    """Find morphological variants: prefix-STEM, STEM-suffix, prefix-STEM-suffix."""
    variants = {"with_prefix": [], "with_suffix": [], "with_both": [], "standalone": []}

    for sentence in sentences:
        for word_data in sentence:
            word = word_data["word"]

            # Exact match
            if word == candidate_word:
                variants["standalone"].append(word_data)
                continue

            # Check if candidate appears as stem in compound
            # Pattern: PREFIX-candidate or candidate-SUFFIX or PREFIX-candidate-SUFFIX

            has_prefix = False
            has_suffix = False
            is_stem = False

            # Check prefix patterns
            for prefix in PREFIXES:
                if word.startswith(prefix + candidate_word):
                    has_prefix = True
                    remainder = word[len(prefix + candidate_word) :]
                    if not remainder:  # Just prefix+candidate
                        is_stem = True
                    elif any(
                        remainder == suf or remainder.startswith(suf)
                        for suf in SUFFIXES
                    ):
                        is_stem = True
                        has_suffix = True
                    break

            # Check suffix patterns (if no prefix found)
            if not has_prefix and word.startswith(candidate_word):
                remainder = word[len(candidate_word) :]
                if remainder and any(
                    remainder == suf or remainder.startswith(suf) for suf in SUFFIXES
                ):
                    has_suffix = True
                    is_stem = True

            # Classify
            if is_stem:
                if has_prefix and has_suffix:
                    variants["with_both"].append(word_data)
                elif has_prefix:
                    variants["with_prefix"].append(word_data)
                elif has_suffix:
                    variants["with_suffix"].append(word_data)

    return variants


def calculate_productivity(variants):
    """Calculate morphological productivity percentage."""
    standalone = len(variants["standalone"])
    compounds = (
        len(variants["with_prefix"])
        + len(variants["with_suffix"])
        + len(variants["with_both"])
    )
    total = standalone + compounds

    if total == 0:
        return 0.0, 0, 0

    productivity = (compounds / total) * 100
    return productivity, total, compounds


def validate_candidate(candidate_word, sentences):
    """Apply 10-point validation framework."""

    print(f"\n{'=' * 80}")
    print(f"VALIDATING: {candidate_word.upper()}")
    print(f"{'=' * 80}\n")

    # Extract exact matches
    exact_matches = extract_exact_matches(candidate_word, sentences)
    exact_count = len(exact_matches)

    print(f"Exact matches found: {exact_count}")

    if exact_count < 20:
        print(f"INSUFFICIENT DATA (n<20)")
        return None

    # Find morphological variants
    variants = find_morphological_variants(candidate_word, sentences)

    print(f"\nMorphological variants:")
    print(f"  Standalone: {len(variants['standalone'])}")
    print(f"  With prefix: {len(variants['with_prefix'])}")
    print(f"  With suffix: {len(variants['with_suffix'])}")
    print(f"  With both: {len(variants['with_both'])}")

    # Calculate productivity
    productivity, total_count, compound_count = calculate_productivity(variants)
    standalone_pct = (
        (len(variants["standalone"]) / total_count * 100) if total_count > 0 else 0
    )

    print(f"\nTotal occurrences (as stem): {total_count}")
    print(f"Compound uses: {compound_count}")
    print(f"Morphological productivity: {productivity:.1f}%")
    print(f"Standalone frequency: {standalone_pct:.1f}%")

    # CRITERION 1: Morphological Productivity (0-2 points, inverted for roots)
    if productivity > 30:
        prod_score = 2
        prod_note = "Highly productive root (>30% compounds)"
    elif productivity >= 15:
        prod_score = 1
        prod_note = "Moderate productivity (15-30%)"
    else:
        prod_score = 0
        prod_note = "Low productivity (<15%, likely not a root)"

    print(f"\n1. MORPHOLOGICAL PRODUCTIVITY: {prod_score}/2")
    print(f"   {prod_note}")

    # CRITERION 2: Standalone Frequency (0-2 points)
    # For roots, we expect some standalone but not overwhelming
    if 15 <= standalone_pct <= 85:
        stand_score = 2
        stand_note = "Balanced standalone/compound usage"
    elif standalone_pct > 85:
        stand_score = 1
        stand_note = "Very high standalone (may be function word)"
    else:
        stand_score = 1
        stand_note = "Mostly in compounds (expected for productive root)"

    print(f"\n2. STANDALONE FREQUENCY: {stand_score}/2")
    print(f"   {stand_note}")

    # CRITERION 3: Positional Distribution (0-2 points)
    # Collect positions from all variants
    all_instances = (
        variants["standalone"]
        + variants["with_prefix"]
        + variants["with_suffix"]
        + variants["with_both"]
    )
    positions = Counter([inst["position"] for inst in all_instances])
    total_pos = sum(positions.values())

    pos_pcts = {pos: (count / total_pos * 100) for pos, count in positions.items()}

    print(f"\n3. POSITIONAL DISTRIBUTION:")
    print(f"   Initial: {pos_pcts.get('initial', 0):.1f}%")
    print(f"   Medial: {pos_pcts.get('medial', 0):.1f}%")
    print(f"   Final: {pos_pcts.get('final', 0):.1f}%")

    # Roots should show flexibility (no single position >70%)
    max_pos_pct = max(pos_pcts.values()) if pos_pcts else 0

    if max_pos_pct < 60:
        pos_score = 2
        pos_note = "Flexible positioning (characteristic of roots)"
    elif max_pos_pct < 70:
        pos_score = 1
        pos_note = "Moderate positional preference"
    else:
        pos_score = 0
        pos_note = (
            f"Strong positional preference ({max_pos_pct:.1f}%, suggests function word)"
        )

    print(f"   SCORE: {pos_score}/2 - {pos_note}")

    # CRITERION 4: Section Distribution (0-2 points)
    sections = Counter([inst["section"] for inst in all_instances])
    num_sections = len(sections)

    print(f"\n4. SECTION DISTRIBUTION:")
    for section, count in sections.most_common():
        pct = count / len(all_instances) * 100
        print(f"   {section}: {count} ({pct:.1f}%)")

    # Calculate enrichment for top section
    if num_sections >= 2:
        top_section, top_count = sections.most_common(1)[0]
        expected_pct = 25.0  # 4 sections
        observed_pct = (top_count / len(all_instances)) * 100
        enrichment = observed_pct / expected_pct

        if enrichment > 1.5 and top_count >= 10:
            sect_score = 2
            sect_note = (
                f"{enrichment:.2f}× enrichment in {top_section} (domain-specific root)"
            )
        elif num_sections == 4:
            sect_score = 2
            sect_note = "Universal distribution (grammatical root)"
        elif num_sections >= 3:
            sect_score = 1
            sect_note = "Present in multiple sections"
        else:
            sect_score = 0
            sect_note = "Limited to 1-2 sections (insufficient data)"
    else:
        sect_score = 0
        sect_note = "Insufficient section coverage"

    print(f"   SCORE: {sect_score}/2 - {sect_note}")

    # CRITERION 5: Co-occurrence with Validated Elements (0-2 points)
    # Check 3-word windows
    cooccur_count = 0
    for sentence in sentences:
        for i, word_data in enumerate(sentence):
            if word_data["word"] == candidate_word or any(
                candidate_word in word_data["word"]
                and any(
                    word_data["word"].startswith(p + candidate_word) for p in PREFIXES
                )
                for _ in [None]
            ):
                # Check window
                window_start = max(0, i - 1)
                window_end = min(len(sentence), i + 2)
                window_words = [
                    sentence[j]["word"] for j in range(window_start, window_end)
                ]

                if any(w in VALIDATED for w in window_words if w != word_data["word"]):
                    cooccur_count += 1
                    break

    cooccur_pct = (cooccur_count / len(all_instances) * 100) if all_instances else 0

    print(f"\n5. CO-OCCURRENCE WITH VALIDATED ELEMENTS:")
    print(f"   {cooccur_pct:.1f}% of contexts contain validated elements")

    if cooccur_pct > 15:
        cooccur_score = 2
        cooccur_note = "Frequent co-occurrence (systematic integration)"
    elif cooccur_pct > 5:
        cooccur_score = 1
        cooccur_note = "Moderate co-occurrence"
    else:
        cooccur_score = 0
        cooccur_note = "Limited co-occurrence (isolated usage)"

    print(f"   SCORE: {cooccur_score}/2 - {cooccur_note}")

    # TOTAL SCORE
    total_score = prod_score + stand_score + pos_score + sect_score + cooccur_score

    print(f"\n{'=' * 80}")
    print(f"TOTAL SCORE: {total_score}/10")

    if total_score >= 8:
        result = "[VALIDATED]"
    elif total_score >= 6:
        result = "[NEAR-VALIDATED]"
    else:
        result = "[NOT VALIDATED]"

    print(f"RESULT: {result}")
    print(f"{'=' * 80}\n")

    return {
        "word": candidate_word,
        "score": total_score,
        "exact_count": exact_count,
        "total_count": total_count,
        "productivity": productivity,
        "standalone_pct": standalone_pct,
        "scores": {
            "productivity": prod_score,
            "standalone": stand_score,
            "position": pos_score,
            "section": sect_score,
            "cooccurrence": cooccur_score,
        },
        "sections": dict(sections),
        "num_sections": num_sections,
        "result": result,
    }


def main():
    transcription_file = "data/voynich/eva_transcription/ZL3b-n.txt"

    print("Loading EVA transcription with position/section markup...")
    sentences = load_eva_with_position(transcription_file)
    print(f"Loaded {len(sentences)} sentences\n")

    # Candidates from Phase 13 ot- analysis
    candidates = [
        "edy",  # 162 ot- uses
        "eey",  # 72 ot- uses
        "eedy",  # 68 ot- uses
        "eeedy",  # 98 ot- uses
        "ol",  # 54 ot- uses as stem (also prefix!)
        "ain",  # 24 ot- uses as stem (also suffix!)
        "air",  # 30 ot- uses (already validated? check)
    ]

    results = []

    for candidate in candidates:
        result = validate_candidate(candidate, sentences)
        if result:
            results.append(result)

    # Summary
    print("\n" + "=" * 80)
    print("PHASE 14B VALIDATION SUMMARY")
    print("=" * 80 + "\n")

    validated = [r for r in results if r["score"] >= 8]
    near_validated = [r for r in results if 6 <= r["score"] < 8]
    not_validated = [r for r in results if r["score"] < 6]

    print(f"Total candidates tested: {len(results)}")
    print(f"Validated (≥8/10): {len(validated)}")
    print(f"Near-validated (6-7/10): {len(near_validated)}")
    print(f"Not validated (<6/10): {len(not_validated)}\n")

    if validated:
        print("VALIDATED ELEMENTS:")
        for r in validated:
            print(
                f"  {r['word']}: {r['score']}/10 - {r['total_count']} uses, {r['productivity']:.1f}% productive"
            )

    if near_validated:
        print("\nNEAR-VALIDATED ELEMENTS:")
        for r in near_validated:
            print(
                f"  {r['word']}: {r['score']}/10 - {r['total_count']} uses, {r['productivity']:.1f}% productive"
            )

    if not_validated:
        print("\nNOT VALIDATED:")
        for r in not_validated:
            print(
                f"  {r['word']}: {r['score']}/10 - {r['total_count']} uses, {r['productivity']:.1f}% productive"
            )

    # Save results
    output_file = "PHASE14B_VALIDATION_RESULTS.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Phase 14B: Vowel-Initial Root Validation Results\n\n")
        f.write(f"**Total tested**: {len(results)}\n")
        f.write(f"**Validated (≥8/10)**: {len(validated)}\n")
        f.write(f"**Near-validated (6-7/10)**: {len(near_validated)}\n\n")

        for r in results:
            f.write(f"## {r['word'].upper()}: {r['score']}/10 {r['result']}\n\n")
            f.write(f"- **Total occurrences**: {r['total_count']}\n")
            f.write(f"- **Exact matches**: {r['exact_count']}\n")
            f.write(f"- **Productivity**: {r['productivity']:.1f}%\n")
            f.write(f"- **Standalone**: {r['standalone_pct']:.1f}%\n")
            f.write(f"- **Sections**: {r['num_sections']}/4 - {r['sections']}\n")
            f.write(
                f"- **Scores**: Prod={r['scores']['productivity']}/2, Stand={r['scores']['standalone']}/2, "
            )
            f.write(
                f"Pos={r['scores']['position']}/2, Sect={r['scores']['section']}/2, Cooccur={r['scores']['cooccurrence']}/2\n\n"
            )

    print(f"\nResults saved to {output_file}")
    print("\nPhase 14B complete!")


if __name__ == "__main__":
    main()
