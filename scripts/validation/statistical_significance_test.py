"""
Statistical Significance Testing for Section Enrichment Claims

Tests the following enrichment claims using chi-square test:
1. sho - enriched in herbal section
2. keo - enriched in pharmaceutical section
3. teo - enriched in pharmaceutical section
4. ar - enriched in astronomical section

Null hypothesis: Term distribution across sections follows overall manuscript distribution
Alternative hypothesis: Term is significantly enriched in specific section

Target: p < 0.05 for statistical significance
"""

import re
from scipy.stats import chi2_contingency
import numpy as np


def load_voynich_data():
    """Load Voynich manuscript data with section labels"""
    filepath = "data/voynich/eva_transcription/ZL3b-n.txt"

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    words_with_context = []
    current_section = "unknown"

    for line_num, line in enumerate(lines, 1):
        line_stripped = line.strip()

        if not line_stripped or line_stripped.startswith("#"):
            continue

        # Extract folio/section info from line
        # Format: <f1r> or <f1r.1,@P0>
        folio_match = re.search(r"<f(\d+)[rv]", line_stripped)
        if folio_match:
            folio_num = int(folio_match.group(1))

            # Section ranges (based on Voynich manuscript structure)
            if 1 <= folio_num <= 66:
                current_section = "herbal"
            elif 67 <= folio_num <= 73:
                current_section = "astronomical"
            elif 75 <= folio_num <= 84:
                current_section = "biological"
            elif 85 <= folio_num <= 116:
                current_section = "pharmaceutical"
            else:
                current_section = "unknown"

        # Extract words from line (remove markup)
        # Remove everything in brackets, angle brackets, special chars
        text = re.sub(r"\[.*?\]", "", line_stripped)  # Remove [...]
        text = re.sub(r"\{.*?\}", "", text)  # Remove {...}
        text = re.sub(r"<.*?>", "", text)  # Remove <...>
        text = re.sub(r"[!*=\-@$%,.:;()']", " ", text)  # Replace punctuation with space
        words = re.findall(r"[a-z]{2,}", text.lower())  # Only words 2+ chars

        for i, word in enumerate(words):
            context_before = " ".join(words[max(0, i - 3) : i])
            context_after = " ".join(words[i + 1 : min(len(words), i + 4)])

            words_with_context.append(
                {
                    "word": word,
                    "line": line_num,
                    "section": current_section,
                    "context_before": context_before,
                    "context_after": context_after,
                    "full_sentence": " ".join(words),
                }
            )

    return words_with_context


def count_by_section(words_with_context):
    """Count total words in each section"""
    section_counts = {
        "herbal": 0,
        "biological": 0,
        "pharmaceutical": 0,
        "astronomical": 0,
    }

    for entry in words_with_context:
        section = entry.get("section", "unknown")
        if section in section_counts:
            section_counts[section] += 1

    total = sum(section_counts.values())
    return section_counts, total


def count_term_by_section(term, words_with_context):
    """Count term occurrences in each section"""
    term_counts = {"herbal": 0, "biological": 0, "pharmaceutical": 0, "astronomical": 0}

    for entry in words_with_context:
        word = entry["word"].lower()
        section = entry.get("section", "unknown")

        if word == term and section in term_counts:
            term_counts[section] += 1

    term_total = sum(term_counts.values())
    return term_counts, term_total


def chi_square_test(term, term_counts, section_counts, total_words):
    """
    Perform chi-square test for term enrichment in each section

    Returns: dictionary with p-values for each section
    """
    results = {}

    for section in ["herbal", "biological", "pharmaceutical", "astronomical"]:
        # Observed frequencies
        obs_term_in_section = term_counts[section]
        obs_term_not_in_section = sum(term_counts.values()) - obs_term_in_section
        obs_other_in_section = section_counts[section] - obs_term_in_section
        obs_other_not_in_section = (
            total_words - sum(term_counts.values()) - obs_other_in_section
        )

        # Create contingency table
        # Rows: [term, other words]
        # Cols: [in section, not in section]
        observed = np.array(
            [
                [obs_term_in_section, obs_term_not_in_section],
                [obs_other_in_section, obs_other_not_in_section],
            ]
        )

        # Expected frequency if term followed overall distribution
        expected_term_in_section = (
            sum(term_counts.values()) * section_counts[section]
        ) / total_words

        # Enrichment ratio (observed / expected)
        enrichment = (
            obs_term_in_section / expected_term_in_section
            if expected_term_in_section > 0
            else 0
        )

        # Chi-square test
        chi2, p_value, dof, expected = chi2_contingency(observed)

        results[section] = {
            "observed": obs_term_in_section,
            "expected": expected_term_in_section,
            "enrichment": enrichment,
            "chi2": chi2,
            "p_value": p_value,
            "significant": p_value < 0.05,
        }

    return results


def print_term_analysis(term, term_counts, section_counts, total_words):
    """Print detailed analysis for a term"""
    term_total = sum(term_counts.values())

    print(f"\n{'=' * 70}")
    print(f"TERM: {term.upper()}")
    print(f"{'=' * 70}")
    print(f"Total instances: {term_total}")
    print(f"\nDistribution by section:")
    print(f"  {'Section':<15} {'Count':<10} {'% of term':<15} {'% of section':<15}")
    print(f"  {'-' * 60}")

    for section in ["herbal", "biological", "pharmaceutical", "astronomical"]:
        count = term_counts[section]
        pct_of_term = 100 * count / term_total if term_total > 0 else 0
        pct_of_section = (
            100 * count / section_counts[section] if section_counts[section] > 0 else 0
        )
        print(
            f"  {section:<15} {count:<10} {pct_of_term:<14.1f}% {pct_of_section:<14.2f}%"
        )

    print(f"\n{'=' * 70}")
    print(f"CHI-SQUARE TEST RESULTS")
    print(f"{'=' * 70}")

    results = chi_square_test(term, term_counts, section_counts, total_words)

    print(
        f"  {'Section':<15} {'Enrichment':<12} {'chi2':<10} {'p-value':<12} {'Significant?':<15}"
    )
    print(f"  {'-' * 70}")

    for section in ["herbal", "biological", "pharmaceutical", "astronomical"]:
        r = results[section]
        sig_marker = "✓✓✓ YES" if r["significant"] else "✗ NO"
        print(
            f"  {section:<15} {r['enrichment']:<11.2f}× {r['chi2']:<9.2f} {r['p_value']:<11.6f} {sig_marker:<15}"
        )

    # Find most enriched section
    max_section = max(results.items(), key=lambda x: x[1]["enrichment"])
    print(f"\n  Most enriched in: {max_section[0].upper()}")
    print(f"  Enrichment ratio: {max_section[1]['enrichment']:.2f}×")
    print(f"  P-value: {max_section[1]['p_value']:.6f}")

    if max_section[1]["significant"]:
        print(f"  Status: ✓✓✓ STATISTICALLY SIGNIFICANT (p < 0.05)")
    else:
        print(f"  Status: ✗ NOT SIGNIFICANT (p ≥ 0.05)")

    return results


def main():
    print("=" * 70)
    print("STATISTICAL SIGNIFICANCE TESTING")
    print("Section Enrichment Claims")
    print("=" * 70)

    # Load data
    print("\nLoading Voynich manuscript data...")
    words_with_context = load_voynich_data()
    section_counts, total_words = count_by_section(words_with_context)

    print(f"\nManuscript statistics:")
    print(f"  Total words: {total_words:,}")
    print(f"\nSection distribution:")
    for section, count in section_counts.items():
        pct = 100 * count / total_words
        print(f"  {section:<15}: {count:>6,} words ({pct:>5.1f}%)")

    # Test enrichment claims
    terms_to_test = {
        "sho": "herbal",
        "keo": "pharmaceutical",
        "teo": "pharmaceutical",
        "ar": "astronomical",
    }

    all_results = {}

    for term, expected_section in terms_to_test.items():
        term_counts, term_total = count_term_by_section(term, words_with_context)
        results = print_term_analysis(term, term_counts, section_counts, total_words)
        all_results[term] = results

    # Summary
    print(f"\n\n{'=' * 70}")
    print("SUMMARY OF ENRICHMENT CLAIMS")
    print("=" * 70)

    print(
        f"\n{'Term':<8} {'Expected Section':<20} {'Enrichment':<12} {'p-value':<12} {'Result':<15}"
    )
    print(f"{'-' * 70}")

    for term, expected_section in terms_to_test.items():
        r = all_results[term][expected_section]
        sig_marker = "✓ CONFIRMED" if r["significant"] else "✗ REJECTED"
        print(
            f"{term:<8} {expected_section:<20} {r['enrichment']:<11.2f}× {r['p_value']:<11.6f} {sig_marker:<15}"
        )

    # Count confirmed claims
    confirmed = sum(
        1
        for term, exp_sec in terms_to_test.items()
        if all_results[term][exp_sec]["significant"]
    )
    total_claims = len(terms_to_test)

    print(f"\n{'=' * 70}")
    print(
        f"CONFIRMATION RATE: {confirmed}/{total_claims} ({100 * confirmed / total_claims:.0f}%)"
    )
    print(f"{'=' * 70}")

    if confirmed == total_claims:
        print("\n✓✓✓ ALL ENRICHMENT CLAIMS CONFIRMED")
        print("All terms show statistically significant enrichment (p < 0.05)")
    elif confirmed >= total_claims * 0.75:
        print(f"\n✓✓ MOST ENRICHMENT CLAIMS CONFIRMED ({confirmed}/{total_claims})")
        print("Majority of terms show statistically significant enrichment")
    elif confirmed >= total_claims * 0.5:
        print(f"\n✓ SOME ENRICHMENT CLAIMS CONFIRMED ({confirmed}/{total_claims})")
        print("Some terms show statistically significant enrichment")
    else:
        print(f"\n✗ ENRICHMENT CLAIMS NOT SUPPORTED ({confirmed}/{total_claims})")
        print("Most terms do not show statistically significant enrichment")

    # Additional analysis: test all Phase 6-8 terms
    print(f"\n\n{'=' * 70}")
    print("ADDITIONAL ANALYSIS: ALL VALIDATED TERMS")
    print("=" * 70)

    all_terms = [
        "ok",
        "ot",
        "she",
        "dor",
        "cho",
        "cheo",
        "sho",
        "keo",
        "teo",
        "okal",
        "or",
        "dol",
        "dar",
        "chol",
    ]

    enrichment_summary = {}

    for term in all_terms:
        term_counts, term_total = count_term_by_section(term, words_with_context)
        if term_total == 0:
            continue
        results = chi_square_test(term, term_counts, section_counts, total_words)

        # Find most enriched section
        max_section = max(results.items(), key=lambda x: x[1]["enrichment"])
        enrichment_summary[term] = {
            "section": max_section[0],
            "enrichment": max_section[1]["enrichment"],
            "p_value": max_section[1]["p_value"],
            "significant": max_section[1]["significant"],
            "total_instances": term_total,
        }

    print(
        f"\n{'Term':<8} {'Instances':<12} {'Most Enriched In':<20} {'Enrichment':<12} {'p-value':<12} {'Significant?':<15}"
    )
    print(f"{'-' * 90}")

    for term in all_terms:
        if term not in enrichment_summary:
            continue
        e = enrichment_summary[term]
        sig_marker = "✓ YES" if e["significant"] else "✗ NO"
        print(
            f"{term:<8} {e['total_instances']:<12} {e['section']:<20} {e['enrichment']:<11.2f}× {e['p_value']:<11.6f} {sig_marker:<15}"
        )

    # Count how many terms show significant enrichment
    sig_enriched = sum(1 for e in enrichment_summary.values() if e["significant"])
    total_tested = len(enrichment_summary)

    print(f"\n{'=' * 70}")
    print(
        f"Terms with significant section enrichment: {sig_enriched}/{total_tested} ({100 * sig_enriched / total_tested:.0f}%)"
    )
    print(f"{'=' * 70}")

    print("\nInterpretation:")
    if sig_enriched >= total_tested * 0.7:
        print("✓✓✓ Most validated terms show section-specific usage")
        print("    This supports domain-specific vocabulary hypothesis")
    elif sig_enriched >= total_tested * 0.3:
        print("✓ Mix of universal and domain-specific terms")
        print("  This is expected - some terms (water, oak) are universal,")
        print("  while others (botanical, pharmaceutical) are domain-specific")
    else:
        print("✗ Most terms show universal distribution")
        print("  This may indicate terms are grammatical rather than semantic")

    print("\n" + "=" * 70)
    print("STATISTICAL SIGNIFICANCE TESTING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
