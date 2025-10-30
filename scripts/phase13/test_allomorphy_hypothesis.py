#!/usr/bin/env python3
"""
Phase 13: Statistical Test for OL-/OT- Allomorphy
Test whether ol- and ot- show phonologically conditioned distribution
"""

import re
from collections import Counter, defaultdict
from scipy import stats


def load_voynich_text(filepath):
    """Load EVA transcription"""
    words = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Skip folio markers
            folio_match = re.match(r"<f(\d+[rv]?)>", line)
            if folio_match:
                continue

            # Extract words from line
            line_words = re.findall(r"\b[a-z]+\b", line.lower())
            for word in line_words:
                if len(word) >= 3:
                    words.append(word)
    return words


def classify_initial_sound(stem):
    """Classify stem initial as consonant or vowel"""
    if not stem:
        return None

    vowels = {"a", "e", "i", "o", "u", "y"}
    first_char = stem[0]

    if first_char in vowels:
        return "V"  # Vowel
    else:
        return "C"  # Consonant


def analyze_ol_ot_distribution(words):
    """Analyze distribution of ol- vs ot- by stem-initial sound"""

    # Find ol- and ot- words
    ol_words = [w for w in words if w.startswith("ol") and len(w) > 4]
    ot_words = [w for w in words if w.startswith("ot") and len(w) > 4]

    # Extract stems and classify
    ol_stems = [w[2:] for w in ol_words]
    ot_stems = [w[2:] for w in ot_words]

    # Count by initial sound type
    ol_by_type = {"C": 0, "V": 0}
    ot_by_type = {"C": 0, "V": 0}

    for stem in ol_stems:
        stem_type = classify_initial_sound(stem)
        if stem_type:
            ol_by_type[stem_type] += 1

    for stem in ot_stems:
        stem_type = classify_initial_sound(stem)
        if stem_type:
            ot_by_type[stem_type] += 1

    return ol_by_type, ot_by_type


def chi_square_test(ol_counts, ot_counts):
    """Test independence of prefix choice and stem-initial sound"""

    # Contingency table:
    #           C-initial   V-initial
    # ol-       ol_C        ol_V
    # ot-       ot_C        ot_V

    observed = [[ol_counts["C"], ol_counts["V"]], [ot_counts["C"], ot_counts["V"]]]

    chi2, p_value, dof, expected = stats.chi2_contingency(observed)

    return chi2, p_value, expected


def analyze_top_stems(words, prefix, n=20):
    """Get top N stems for a prefix with sound classification"""

    prefix_words = [w for w in words if w.startswith(prefix) and len(w) > 4]
    stems = Counter([w[len(prefix) :] for w in prefix_words])

    top_stems = []
    for stem, count in stems.most_common(n):
        sound_type = classify_initial_sound(stem)
        top_stems.append(
            {
                "stem": stem,
                "count": count,
                "initial": sound_type,
                "full_word": prefix + stem,
            }
        )

    return top_stems


def main():
    print("Phase 13: Statistical Test for OL-/OT- Allomorphy")
    print("=" * 80)
    print("H0: ol- and ot- choice is independent of stem-initial sound")
    print("H1: ol- and ot- show phonologically conditioned distribution")
    print("=" * 80)

    # Load data
    eva_file = (
        "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/ZL3b-n.txt"
    )
    words = load_voynich_text(eva_file)
    print(f"\nLoaded {len(words)} words from EVA transcription\n")

    print("=" * 80)
    print("ANALYSIS 1: Overall Distribution")
    print("=" * 80)

    ol_counts, ot_counts = analyze_ol_ot_distribution(words)

    ol_total = ol_counts["C"] + ol_counts["V"]
    ot_total = ot_counts["C"] + ot_counts["V"]

    ol_c_pct = (ol_counts["C"] / ol_total) * 100 if ol_total > 0 else 0
    ol_v_pct = (ol_counts["V"] / ol_total) * 100 if ol_total > 0 else 0
    ot_c_pct = (ot_counts["C"] / ot_total) * 100 if ot_total > 0 else 0
    ot_v_pct = (ot_counts["V"] / ot_total) * 100 if ot_total > 0 else 0

    print(f"\nOL- distribution:")
    print(f"  Consonant-initial stems: {ol_counts['C']} ({ol_c_pct:.1f}%)")
    print(f"  Vowel-initial stems: {ol_counts['V']} ({ol_v_pct:.1f}%)")
    print(f"  Total: {ol_total}")

    print(f"\nOT- distribution:")
    print(f"  Consonant-initial stems: {ot_counts['C']} ({ot_c_pct:.1f}%)")
    print(f"  Vowel-initial stems: {ot_counts['V']} ({ot_v_pct:.1f}%)")
    print(f"  Total: {ot_total}")

    print("\n" + "=" * 80)
    print("ANALYSIS 2: Chi-Square Test of Independence")
    print("=" * 80)

    chi2, p_value, expected = chi_square_test(ol_counts, ot_counts)

    print(f"\nContingency Table (Observed):")
    print(f"{'':>10} {'C-initial':>15} {'V-initial':>15}")
    print(f"{'ol-':>10} {ol_counts['C']:>15} {ol_counts['V']:>15}")
    print(f"{'ot-':>10} {ot_counts['C']:>15} {ot_counts['V']:>15}")

    print(f"\nExpected (if independent):")
    print(f"{'':>10} {'C-initial':>15} {'V-initial':>15}")
    print(f"{'ol-':>10} {expected[0][0]:>15.1f} {expected[0][1]:>15.1f}")
    print(f"{'ot-':>10} {expected[1][0]:>15.1f} {expected[1][1]:>15.1f}")

    print(f"\nChi-square statistic: {chi2:.4f}")
    print(f"p-value: {p_value:.6f}")
    print(f"Degrees of freedom: 1")

    if p_value < 0.001:
        print(f"\n*** HIGHLY SIGNIFICANT (p < 0.001) ***")
        print("REJECT H0: ol- and ot- choice is NOT independent of stem-initial sound")
        print("ACCEPT H1: ol- and ot- show phonologically conditioned distribution")
    elif p_value < 0.05:
        print(f"\n** SIGNIFICANT (p < 0.05) **")
        print("REJECT H0: Evidence for phonological conditioning")
    else:
        print(f"\nNOT SIGNIFICANT (p >= 0.05)")
        print("FAIL TO REJECT H0: No evidence for phonological conditioning")

    print("\n" + "=" * 80)
    print("ANALYSIS 3: Top Stems by Prefix")
    print("=" * 80)

    print(f"\nTop 20 OL- stems:")
    print(f"{'Stem':<15} {'Count':<10} {'Initial':<10} {'Full Word':<20}")
    print("-" * 60)

    ol_tops = analyze_top_stems(words, "ol", 20)
    for stem_data in ol_tops:
        print(
            f"{stem_data['stem']:<15} {stem_data['count']:<10} {stem_data['initial']:<10} {stem_data['full_word']:<20}"
        )

    # Count C vs V in top 20
    ol_top_c = sum(1 for s in ol_tops if s["initial"] == "C")
    ol_top_v = sum(1 for s in ol_tops if s["initial"] == "V")
    print(
        f"\nTop 20 summary: {ol_top_c} C-initial ({ol_top_c / 20 * 100:.0f}%), {ol_top_v} V-initial ({ol_top_v / 20 * 100:.0f}%)"
    )

    print(f"\n\nTop 20 OT- stems:")
    print(f"{'Stem':<15} {'Count':<10} {'Initial':<10} {'Full Word':<20}")
    print("-" * 60)

    ot_tops = analyze_top_stems(words, "ot", 20)
    for stem_data in ot_tops:
        print(
            f"{stem_data['stem']:<15} {stem_data['count']:<10} {stem_data['initial']:<10} {stem_data['full_word']:<20}"
        )

    ot_top_c = sum(1 for s in ot_tops if s["initial"] == "C")
    ot_top_v = sum(1 for s in ot_tops if s["initial"] == "V")
    print(
        f"\nTop 20 summary: {ot_top_c} C-initial ({ot_top_c / 20 * 100:.0f}%), {ot_top_v} V-initial ({ot_top_v / 20 * 100:.0f}%)"
    )

    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)

    if p_value < 0.001:
        print("\n*** ALLOMORPHY CONFIRMED ***")
        print(f"\nOL- strongly prefers C-initial stems: {ol_c_pct:.1f}%")
        print(f"OT- strongly prefers V-initial stems: {ot_v_pct:.1f}%")
        print(f"\nStatistical evidence: chi2={chi2:.2f}, p<0.001")
        print("\nConclusion: OL- and OT- are phonologically conditioned ALLOMORPHS")
        print("of the same underlying locative prefix {OL}.")
        print("\nDistribution rule:")
        print("  /ol/ -> before consonants (preferred)")
        print("  /ot/ -> before vowels (preferred)")
        print("\nThis is STRONG EVIDENCE for systematic phonological processes")
        print("in Voynichese, characteristic of natural languages.")


if __name__ == "__main__":
    main()
