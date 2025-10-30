"""
CRITICAL TEST: Objective Validation Only (No Manual Scoring)

Re-validates all Phase 7 terms using ONLY the 5 objective criteria.
Removes "contextual coherence" manual scoring to eliminate bias.

10-point scoring system:
1. Morphology (0-2): <5% = 2, 5-15% = 1, >15% = 0
2. Standalone (0-2): >80% = 2, 60-80% = 1, <60% = 0
3. Position (0-2): medial >70% = 2, 50-70% = 1, other = 0
4. Distribution (0-2): 4 sections = 2, 3 sections = 1, <3 = 0
5. Co-occurrence (0-2): >15% = 2, 5-15% = 1, <5% = 0

Thresholds:
- ≥8/10 = VALIDATED
- 6-7/10 = LIKELY
- 4-5/10 = POSSIBLE
- <4/10 = REJECTED
"""

# Phase 7 terms with their OBJECTIVE scores (from Phase 7A investigations)

terms = {
    "ar": {
        "name": "ar (preposition: at/in)",
        "morphology_pct": 0.0,  # 0.0% case-marking, 0.0% verbal
        "standalone_pct": 94.0,  # 94.0% standalone
        "medial_position_pct": 86.6,  # 86.6% medial
        "sections": 4,  # All 4 sections (universal)
        "co_occurrence_pct": 14.4,  # 14.4% with validated terms
        "manual_coherence": 2,  # USER PROVIDED (we're removing this)
    },
    "daiin": {
        "name": "daiin (demonstrative: this/that)",
        "morphology_pct": 0.0,  # 0.0% in sample
        "standalone_pct": 100.0,  # Appears standalone
        "medial_position_pct": 64.3,  # 64.3% medial
        "sections": 4,  # All 4 sections
        "co_occurrence_pct": 8.1,  # 8.1% with validated terms
        "manual_coherence": 2,  # USER PROVIDED (we're removing this)
    },
    "y": {
        "name": "y (conjunction: and)",
        "morphology_pct": 1.4,  # 1.4% case-marking, 1.4% verbal
        "standalone_pct": 78.6,  # 78.6% standalone
        "medial_position_pct": 63.1,  # 63.1% medial
        "sections": 3,  # 3 sections (not universal)
        "co_occurrence_pct": 8.5,  # 8.5% with validated terms
        "manual_coherence": 2,  # USER PROVIDED (we're removing this)
    },
}


def score_morphology(morphology_pct):
    """Score morphology rate (function words should be <5%)"""
    if morphology_pct < 5.0:
        return 2
    elif morphology_pct < 15.0:
        return 1
    else:
        return 0


def score_standalone(standalone_pct):
    """Score standalone frequency (function words should be >60%)"""
    if standalone_pct > 80.0:
        return 2
    elif standalone_pct > 60.0:
        return 1
    else:
        return 0


def score_position(medial_pct):
    """Score position (function words should be medial >50%)"""
    if medial_pct > 70.0:
        return 2
    elif medial_pct > 50.0:
        return 1
    else:
        return 0


def score_distribution(sections):
    """Score section distribution (universal = 4 sections)"""
    if sections >= 4:
        return 2
    elif sections == 3:
        return 1
    else:
        return 0


def score_co_occurrence(co_occurrence_pct):
    """Score co-occurrence with validated terms"""
    if co_occurrence_pct > 15.0:
        return 2
    elif co_occurrence_pct > 5.0:
        return 1
    else:
        return 0


def validate_term(term_data):
    """Validate term using ONLY objective criteria (no manual scoring)"""

    # Calculate objective scores
    morphology_score = score_morphology(term_data["morphology_pct"])
    standalone_score = score_standalone(term_data["standalone_pct"])
    position_score = score_position(term_data["medial_position_pct"])
    distribution_score = score_distribution(term_data["sections"])
    co_occurrence_score = score_co_occurrence(term_data["co_occurrence_pct"])

    # Total objective score (out of 10)
    objective_total = (
        morphology_score
        + standalone_score
        + position_score
        + distribution_score
        + co_occurrence_score
    )

    # Original score (with manual coherence)
    original_total = objective_total + term_data["manual_coherence"]

    # Determine validation status
    if objective_total >= 8:
        objective_status = "VALIDATED"
        objective_symbol = "✓✓✓"
    elif objective_total >= 6:
        objective_status = "LIKELY"
        objective_symbol = "✓✓"
    elif objective_total >= 4:
        objective_status = "POSSIBLE"
        objective_symbol = "✓"
    else:
        objective_status = "REJECTED"
        objective_symbol = "✗"

    # Original status (for comparison)
    if original_total >= 10:
        original_status = "VALIDATED"
    elif original_total >= 8:
        original_status = "LIKELY"
    elif original_total >= 6:
        original_status = "POSSIBLE"
    else:
        original_status = "REJECTED"

    return {
        "morphology_score": morphology_score,
        "standalone_score": standalone_score,
        "position_score": position_score,
        "distribution_score": distribution_score,
        "co_occurrence_score": co_occurrence_score,
        "objective_total": objective_total,
        "objective_status": objective_status,
        "objective_symbol": objective_symbol,
        "original_total": original_total,
        "original_status": original_status,
        "status_changed": objective_status != original_status,
    }


def main():
    print("=" * 80)
    print("CRITICAL TEST: OBJECTIVE VALIDATION ONLY (NO MANUAL SCORING)")
    print("=" * 80)
    print("\nRemoving subjective 'contextual coherence' component")
    print("Re-validating all Phase 7 terms with 5 objective criteria only\n")
    print("10-point scoring system:")
    print("  1. Morphology (0-2)")
    print("  2. Standalone (0-2)")
    print("  3. Position (0-2)")
    print("  4. Distribution (0-2)")
    print("  5. Co-occurrence (0-2)")
    print("\nThresholds:")
    print("  ≥8/10 = VALIDATED ✓✓✓")
    print("  6-7/10 = LIKELY ✓✓")
    print("  4-5/10 = POSSIBLE ✓")
    print("  <4/10 = REJECTED ✗")
    print("\n" + "=" * 80)

    results = {}

    for term_key, term_data in terms.items():
        print(f"\n{'=' * 80}")
        print(f"TERM: {term_data['name']}")
        print("=" * 80)

        result = validate_term(term_data)
        results[term_key] = result

        print(f"\nOBJECTIVE CRITERIA SCORES:")
        print(
            f"  1. Morphology:     {result['morphology_score']}/2  ({term_data['morphology_pct']:.1f}% morphology)"
        )
        print(
            f"  2. Standalone:     {result['standalone_score']}/2  ({term_data['standalone_pct']:.1f}% standalone)"
        )
        print(
            f"  3. Position:       {result['position_score']}/2  ({term_data['medial_position_pct']:.1f}% medial)"
        )
        print(
            f"  4. Distribution:   {result['distribution_score']}/2  ({term_data['sections']} sections)"
        )
        print(
            f"  5. Co-occurrence:  {result['co_occurrence_score']}/2  ({term_data['co_occurrence_pct']:.1f}% with validated)"
        )

        print(f"\n{'─' * 80}")
        print(f"OBJECTIVE TOTAL:   {result['objective_total']}/10")
        print(
            f"OBJECTIVE STATUS:  {result['objective_status']} {result['objective_symbol']}"
        )

        print(f"\n{'─' * 80}")
        print("COMPARISON TO ORIGINAL (WITH MANUAL SCORING):")
        print(
            f"  Original total:  {result['original_total']}/12  (included +{term_data['manual_coherence']} manual coherence)"
        )
        print(f"  Original status: {result['original_status']}")

        if result["status_changed"]:
            print(
                f"\n⚠️  STATUS CHANGED: {result['original_status']} → {result['objective_status']}"
            )
            print("    Manual scoring was influencing validation decision!")
        else:
            print(f"\n✓  Status unchanged: {result['objective_status']}")

    print(f"\n\n{'=' * 80}")
    print("SUMMARY: IMPACT OF REMOVING MANUAL SCORING")
    print("=" * 80)

    for term_key, result in results.items():
        term_name = terms[term_key]["name"]
        print(f"\n{term_name}")
        print(
            f"  Original: {result['original_total']}/12 → {result['original_status']}"
        )
        print(
            f"  Objective: {result['objective_total']}/10 → {result['objective_status']} {result['objective_symbol']}"
        )
        if result["status_changed"]:
            print(
                f"  ⚠️  CHANGED: Dropped from {result['original_status']} to {result['objective_status']}"
            )

    # Count status changes
    status_changes = sum(1 for r in results.values() if r["status_changed"])

    print(f"\n{'=' * 80}")
    print("CRITICAL FINDINGS")
    print("=" * 80)

    print(f"\nTerms with status changes: {status_changes}/{len(terms)}")

    if status_changes > 0:
        print("\n⚠️  WARNING: Manual scoring was biasing validation decisions!")
        print("    Subjective coherence judgments influenced which terms validated.")
        print("    This is similar to Bax's subjective illustration matching.")
    else:
        print("\n✓  Good: Manual scoring did not change validation outcomes.")
        print("    Our terms validate on objective criteria alone.")

    print(f"\n{'=' * 80}")
    print("RECOMMENDATIONS")
    print("=" * 80)

    validated_count = sum(
        1 for r in results.values() if r["objective_status"] == "VALIDATED"
    )
    likely_count = sum(1 for r in results.values() if r["objective_status"] == "LIKELY")
    possible_count = sum(
        1 for r in results.values() if r["objective_status"] == "POSSIBLE"
    )
    rejected_count = sum(
        1 for r in results.values() if r["objective_status"] == "REJECTED"
    )

    print(f"\nObjective validation results:")
    print(f"  VALIDATED: {validated_count} terms")
    print(f"  LIKELY:    {likely_count} terms")
    print(f"  POSSIBLE:  {possible_count} terms")
    print(f"  REJECTED:  {rejected_count} terms")

    if validated_count > 0:
        print(
            f"\n✓ We have {validated_count} term(s) that validate on objective criteria alone."
        )
        print("  These are defensible without subjective scoring.")

    if status_changes > 0:
        print("\n⚠️  ACTION REQUIRED:")
        print("  1. Remove manual coherence from validation framework")
        print("  2. Use 10-point objective scoring system going forward")
        print("  3. Re-evaluate claims about terms that changed status")
        print("  4. Be transparent about subjective bias in previous phases")

    print("\n" + "=" * 80)
    print("TEST 1 COMPLETE: OBJECTIVE VALIDATION ONLY")
    print("=" * 80)
    print("\nNext: Run null hypothesis test (Test 2)")
    print("  → Can random words score 6-8/10 on objective criteria?")


if __name__ == "__main__":
    main()
