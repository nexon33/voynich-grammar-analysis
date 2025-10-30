#!/usr/bin/env python3
"""
Phase 11: Validate Low-Frequency Candidates + Re-evaluate Near-Validated
Apply 10-point framework with adjusted thresholds for low-frequency elements
"""

import re
from collections import Counter, defaultdict
from scipy import stats


def load_voynich_text(filepath):
    """Load EVA transcription with section markup"""
    words = []
    current_section = None
    current_folio = None

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            folio_match = re.match(r"<f(\d+[rv]?)>", line)
            if folio_match:
                current_folio = folio_match.group(1)
                folio_num = int(re.match(r"\d+", current_folio).group())
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
                    words.append(
                        {
                            "word": word,
                            "section": current_section,
                            "folio": current_folio,
                        }
                    )

    return words


def get_validated_elements():
    """Return all 37 validated elements"""
    return {
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
        "chey",
        "cheey",
        "chy",
        "shy",
        "qol",
        "cthy",
        "shey",
        "am",
        "dam",
        "ory",
        "dair",
        "otchol",
        "kchy",
        "kaiin",
        "kar",
        "kain",
        "kedy",
        "teey",
        "oiin",
        "olchedy",
    }


def validate_candidate(
    candidate_word, words_list, validated_elements, adjusted_threshold=False
):
    """
    Apply 10-point validation framework
    adjusted_threshold: Use relaxed thresholds for low-frequency elements (n<25)
    """

    word_strings = [w["word"] for w in words_list]

    # Count exact and compound occurrences
    exact_count = sum(1 for w in word_strings if w == candidate_word)
    compound_count = sum(
        1 for w in word_strings if candidate_word in w and w != candidate_word
    )
    total_count = exact_count + compound_count

    if total_count == 0:
        return None

    # Determine if adjusting thresholds
    use_adjusted = adjusted_threshold and exact_count < 25

    # Criterion 1: Morphological Productivity (0-2 points)
    productivity = (compound_count / total_count) * 100
    standalone_pct = (exact_count / total_count) * 100

    is_root = productivity > 20

    if is_root:
        if productivity > 30:
            prod_score = 2
        elif productivity >= 15:
            prod_score = 1
        else:
            prod_score = 0
    else:
        if productivity < 5:
            prod_score = 2
        elif productivity <= 15:
            prod_score = 1
        else:
            prod_score = 0

    # Criterion 2: Standalone Frequency (0-2 points)
    if standalone_pct > 80:
        standalone_score = 2
    elif standalone_pct >= 50:
        standalone_score = 1
    else:
        standalone_score = 0

    # Criterion 3: Positional Distribution (0-2 points)
    sentences = []
    current_sentence = []
    for i, entry in enumerate(words_list):
        current_sentence.append(entry["word"])
        if len(current_sentence) >= 8 or (
            i > 0 and entry["section"] != words_list[i - 1]["section"]
        ):
            if len(current_sentence) >= 3:
                sentences.append(current_sentence)
            current_sentence = []

    position_counts = {"initial": 0, "medial": 0, "final": 0}
    for sentence in sentences:
        for i, word in enumerate(sentence):
            if word == candidate_word:
                if i == 0:
                    position_counts["initial"] += 1
                elif i == len(sentence) - 1:
                    position_counts["final"] += 1
                else:
                    position_counts["medial"] += 1

    total_pos = sum(position_counts.values())
    if total_pos > 0:
        initial_pct = (position_counts["initial"] / total_pos) * 100
        medial_pct = (position_counts["medial"] / total_pos) * 100
        final_pct = (position_counts["final"] / total_pos) * 100

        max_position = max(initial_pct, medial_pct, final_pct)

        # Adjusted threshold: 65% for low-frequency vs. 70% standard
        position_threshold = 65 if use_adjusted else 70

        if max_position > position_threshold:
            position_score = 2
        elif max_position >= 50:
            position_score = 1
        else:
            position_score = 0

        dominant_position = (
            "medial"
            if medial_pct == max_position
            else ("final" if final_pct == max_position else "initial")
        )
    else:
        position_score = 0
        initial_pct = medial_pct = final_pct = 0
        dominant_position = "unknown"

    # Criterion 4: Section Distribution (0-2 points)
    section_counts = defaultdict(int)
    for entry in words_list:
        if entry["word"] == candidate_word and entry["section"]:
            section_counts[entry["section"]] += 1

    sections_present = len([s for s in section_counts if section_counts[s] > 0])

    # Calculate enrichment
    section_totals = Counter([w["section"] for w in words_list if w["section"]])
    total_words = sum(section_totals.values())

    max_enrichment = 0
    enriched_section = None
    for section in ["herbal", "astronomical", "biological", "pharmaceutical"]:
        observed = section_counts[section]
        expected = (exact_count / total_words) * section_totals[section]
        if expected > 3:  # Lower threshold for low-frequency
            enrichment = observed / expected
            if enrichment > max_enrichment:
                max_enrichment = enrichment
                enriched_section = section

    # Adjusted threshold: 1.5× enrichment with n≥8 for low-frequency
    enrichment_threshold = 8 if use_adjusted else 10

    if sections_present >= 4 or (
        max_enrichment >= 1.5 and exact_count >= enrichment_threshold
    ):
        section_score = 2
    elif sections_present >= 2:
        section_score = 1
    else:
        section_score = 0

    # Criterion 5: Co-occurrence (0-2 points)
    cooccur_count = 0
    for i in range(1, len(words_list) - 1):
        if words_list[i]["word"] == candidate_word:
            prev_word = words_list[i - 1]["word"]
            next_word = words_list[i + 1]["word"]
            if prev_word in validated_elements or next_word in validated_elements:
                cooccur_count += 1

    cooccur_rate = (cooccur_count / exact_count) * 100 if exact_count > 0 else 0

    if cooccur_rate > 15:
        cooccur_score = 2
    elif cooccur_rate >= 5:
        cooccur_score = 1
    else:
        cooccur_score = 0

    # Total score
    total_score = (
        prod_score + standalone_score + position_score + section_score + cooccur_score
    )

    return {
        "word": candidate_word,
        "type": "root" if is_root else "function",
        "score": total_score,
        "n": exact_count,
        "productivity": productivity,
        "standalone": standalone_pct,
        "position_dominant": dominant_position,
        "position_pct": max(initial_pct, medial_pct, final_pct),
        "initial_pct": initial_pct,
        "medial_pct": medial_pct,
        "final_pct": final_pct,
        "sections": sections_present,
        "enrichment": max_enrichment,
        "enriched_section": enriched_section,
        "cooccur_rate": cooccur_rate,
        "adjusted": use_adjusted,
        "scores": {
            "productivity": prod_score,
            "standalone": standalone_score,
            "position": position_score,
            "section": section_score,
            "cooccur": cooccur_score,
        },
    }


def chi_square_test(candidate_word, words_list, enriched_section):
    """Test statistical significance of section enrichment"""
    if not enriched_section:
        return None, None

    word_in_section = 0
    word_in_other = 0
    total_in_section = 0
    total_in_other = 0

    for entry in words_list:
        if entry["section"]:
            if entry["section"] == enriched_section:
                total_in_section += 1
                if entry["word"] == candidate_word:
                    word_in_section += 1
            else:
                total_in_other += 1
                if entry["word"] == candidate_word:
                    word_in_other += 1

    observed = [
        [word_in_section, word_in_other],
        [total_in_section - word_in_section, total_in_other - word_in_other],
    ]

    try:
        chi2, p_value, dof, expected = stats.chi2_contingency(observed)
        return chi2, p_value
    except:
        return None, None


def main():
    print("Phase 11: Validating Low-Frequency + Re-evaluating Near-Validated")
    print("=" * 80)

    # Load data
    eva_file = (
        "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/ZL3b-n.txt"
    )
    words = load_voynich_text(eva_file)
    print(f"\nLoaded {len(words)} words from EVA transcription")

    validated = get_validated_elements()
    print(f"Previously validated: {len(validated)} elements\n")

    # Phase 11 candidates
    # Re-evaluation (3)
    near_validated = ["keol", "olkedy", "cthor"]
    # New low-frequency (8)
    new_lowfreq = ["shed", "chod", "shee", "tcho", "kcho", "chom", "shecthy", "otchor"]

    candidates = near_validated + new_lowfreq

    print(f"Phase 11 candidates: {len(candidates)}")
    print(f"  Re-evaluation: {len(near_validated)} - {', '.join(near_validated)}")
    print(f"  New low-freq: {len(new_lowfreq)} - {', '.join(new_lowfreq)}\n")

    print("=" * 80)
    print("VALIDATION RESULTS (with adjusted thresholds for n<25)")
    print("=" * 80)

    results = []
    for candidate in candidates:
        result = validate_candidate(
            candidate, words, validated, adjusted_threshold=True
        )
        if result:
            results.append(result)

            # Chi-square test if section enriched
            if result["enriched_section"] and result["n"] >= 8:
                chi2, p_value = chi_square_test(
                    candidate, words, result["enriched_section"]
                )
                result["chi2"] = chi2
                result["p_value"] = p_value
            else:
                result["chi2"] = None
                result["p_value"] = None

    # Sort by score
    results.sort(key=lambda x: x["score"], reverse=True)

    print("\nSummary Table:\n")
    print(
        f"{'Word':<12} {'Type':<10} {'Score':<7} {'n':<6} {'Prod%':<8} {'Pos%':<7} {'Position':<10} {'Enrich':<8} {'CoOcc%':<8} {'Adj?':<5}"
    )
    print("-" * 100)

    for r in results:
        adj_marker = "Yes" if r["adjusted"] else "No"
        print(
            f"{r['word']:<12} {r['type']:<10} {r['score']}/10  {r['n']:<6} {r['productivity']:<8.1f} {r['position_pct']:<7.1f} {r['position_dominant']:<10} {r['enrichment']:<8.2f} {r['cooccur_rate']:<8.1f} {adj_marker:<5}"
        )

    # Detailed breakdown
    print("\n" + "=" * 80)
    print("DETAILED VALIDATION BREAKDOWN")
    print("=" * 80)

    for r in results:
        adj_note = " (ADJUSTED THRESHOLDS)" if r["adjusted"] else ""
        print(
            f"\n{r['word'].upper()} - {r['type'].upper()} - SCORE: {r['score']}/10{adj_note}"
        )
        print("-" * 60)
        print(f"  n = {r['n']} (exact matches)")
        print(
            f"  Morphological Productivity: {r['productivity']:.1f}% [{r['scores']['productivity']}/2]"
        )
        print(
            f"  Standalone Frequency: {r['standalone']:.1f}% [{r['scores']['standalone']}/2]"
        )
        print(
            f"  Position: {r['position_dominant']} {r['position_pct']:.1f}% [{r['scores']['position']}/2]"
        )
        print(
            f"    (Initial: {r['initial_pct']:.1f}%, Medial: {r['medial_pct']:.1f}%, Final: {r['final_pct']:.1f}%)"
        )
        print(f"  Sections: {r['sections']} sections [{r['scores']['section']}/2]")
        if r["enriched_section"]:
            print(
                f"    Enriched in {r['enriched_section']}: {r['enrichment']:.2f}x",
                end="",
            )
            if r["p_value"] is not None:
                if r["p_value"] < 0.001:
                    print(f" (p<0.001) ***")
                elif r["p_value"] < 0.01:
                    print(f" (p={r['p_value']:.3f}) **")
                elif r["p_value"] < 0.05:
                    print(f" (p={r['p_value']:.3f}) *")
                else:
                    print(f" (p={r['p_value']:.3f}) ns")
            else:
                print()
        print(f"  Co-occurrence: {r['cooccur_rate']:.1f}% [{r['scores']['cooccur']}/2]")

    print("\n" + "=" * 80)
    print("PHASE 11 SUMMARY")
    print("=" * 80)

    validated_count = len([r for r in results if r["score"] >= 8])
    near_validated_count = len([r for r in results if 6 <= r["score"] < 8])
    promoted = len(
        [r for r in results if r["score"] >= 8 and r["word"] in near_validated]
    )

    print(f"\nValidated (>=8/10): {validated_count}/{len(candidates)}")
    print(f"  - Promoted from near-validated: {promoted}/3")
    print(
        f"  - New low-frequency validated: {validated_count - promoted}/{len(new_lowfreq)}"
    )
    print(f"Near-validated (6-7/10): {near_validated_count}/{len(candidates)}")
    print(
        f"Below threshold (<6/10): {len(candidates) - validated_count - near_validated_count}/{len(candidates)}"
    )

    if validated_count > 0:
        print(f"\nNEW VALIDATED ELEMENTS ({validated_count}):")
        for r in results:
            if r["score"] >= 8:
                promoted_marker = " (PROMOTED)" if r["word"] in near_validated else ""
                print(
                    f"  - {r['word']} ({r['type']}, {r['score']}/10, n={r['n']}){promoted_marker}"
                )

    if near_validated_count > 0:
        print(f"\nNEAR-VALIDATED ELEMENTS ({near_validated_count}):")
        for r in results:
            if 6 <= r["score"] < 8:
                print(f"  - {r['word']} ({r['type']}, {r['score']}/10, n={r['n']})")

    print(f"\nTotal validated vocabulary: {len(validated) + validated_count} elements")


if __name__ == "__main__":
    main()
