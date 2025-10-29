"""
CRITICAL TEST: Are "shee" and "she" the same word?

DANGER: I'm about to assume "she" is a variant of "shee" (water),
        but I already validated "shedy" as a VERB root.

If "shedy" = "she" + "-edy" (verb root + verbal marker),
then "she" is a VERB, not water!

This test will prevent corrupting the entire analysis.

STRATEGY: Compare distributional behavior
- If they're the same word → should have identical patterns
- If different words → should have different patterns

Author: Research Assistant
Date: 2025-10-29
"""

import json
from collections import Counter, defaultdict
from pathlib import Path


def load_data():
    """Load f84v and full manuscript"""
    # F84v
    with open(
        "results/phase4/readable_passages/f84v_oak_oat_bath_folio.txt",
        "r",
        encoding="utf-8",
    ) as f:
        f84v_words = []
        for line in f:
            if line.startswith("Voynich:"):
                words = [w.lower() for w in line.replace("Voynich:", "").split()]
                f84v_words.extend(words)

    # Full manuscript
    with open(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt",
        "r",
        encoding="utf-8",
    ) as f:
        all_words = [w.lower() for w in f.read().split() if w.isalpha()]

    return f84v_words, all_words


def test_section_enrichment(root, f84v_words, all_words):
    """Calculate how enriched a root is in bath sections"""
    f84v_count = sum(1 for w in f84v_words if root in w)
    all_count = sum(1 for w in all_words if root in w)

    if all_count == 0:
        return 0

    f84v_rate = f84v_count / len(f84v_words)
    all_rate = all_count / len(all_words)

    enrichment = f84v_rate / all_rate if all_rate > 0 else 0

    return {"f84v_count": f84v_count, "all_count": all_count, "enrichment": enrichment}


def test_cooccurrence_with_oak_oat(root, all_words, window=5):
    """Count co-occurrences with oak/oat"""
    oak_oat_roots = ["qok", "qot", "ok", "ot"]

    cooccurrences = 0

    for i, word in enumerate(all_words):
        if root in word:
            # Check window
            start = max(0, i - window)
            end = min(len(all_words), i + window + 1)

            for j in range(start, end):
                if j != i:
                    if any(r in all_words[j] for r in oak_oat_roots):
                        cooccurrences += 1
                        break

    return cooccurrences


def test_case_distribution(root, all_words):
    """Get case suffix distribution"""
    cases = defaultdict(int)

    for word in all_words:
        if root in word:
            # Check for case suffixes
            if word.endswith("ol"):
                cases["ol"] += 1
            elif word.endswith("or"):
                cases["or"] += 1
            elif word.endswith("al"):
                cases["al"] += 1
            elif word.endswith("ar"):
                cases["ar"] += 1
            elif word == root:
                cases["bare"] += 1
            else:
                cases["other"] += 1

    total = sum(cases.values())

    # Calculate percentages
    case_pct = {}
    for case, count in cases.items():
        case_pct[case] = {
            "count": count,
            "percentage": 100 * count / total if total > 0 else 0,
        }

    return case_pct


def test_verbal_forms(root, all_words):
    """Check if root takes -edy (verbal marker)"""
    verbal_forms = []
    verbal_count = 0

    for word in all_words:
        if root in word and "edy" in word:
            verbal_forms.append(word)
            verbal_count += 1

    # Get unique forms
    unique_forms = list(set(verbal_forms))

    return {
        "has_verbal": verbal_count > 0,
        "verbal_count": verbal_count,
        "verbal_forms": unique_forms[:10],  # Top 10
    }


def compare_roots(root1, root2, f84v_words, all_words):
    """Compare two roots across all tests"""

    print(f"=" * 80)
    print(f"COMPARING: '{root1}' vs '{root2}'")
    print(f"=" * 80)
    print()

    # Test 1: Section enrichment
    print("TEST 1: BATH SECTION ENRICHMENT")
    print("-" * 80)

    enrich1 = test_section_enrichment(root1, f84v_words, all_words)
    enrich2 = test_section_enrichment(root2, f84v_words, all_words)

    print(f"  {root1}:")
    print(f"    F84v count: {enrich1['f84v_count']}")
    print(f"    Manuscript count: {enrich1['all_count']}")
    print(f"    Enrichment: {enrich1['enrichment']:.2f}x")
    print()
    print(f"  {root2}:")
    print(f"    F84v count: {enrich2['f84v_count']}")
    print(f"    Manuscript count: {enrich2['all_count']}")
    print(f"    Enrichment: {enrich2['enrichment']:.2f}x")
    print()

    # Check similarity
    ratio = (
        enrich1["enrichment"] / enrich2["enrichment"]
        if enrich2["enrichment"] > 0
        else 0
    )
    if 0.5 < ratio < 2.0:
        print(f"  → Similar enrichment (ratio: {ratio:.2f})")
        enrich_similar = True
    else:
        print(f"  → DIFFERENT enrichment (ratio: {ratio:.2f})")
        enrich_similar = False
    print()

    # Test 2: Co-occurrence with oak/oat
    print("TEST 2: CO-OCCURRENCE WITH OAK/OAT")
    print("-" * 80)

    cooccur1 = test_cooccurrence_with_oak_oat(root1, all_words)
    cooccur2 = test_cooccurrence_with_oak_oat(root2, all_words)

    print(f"  {root1}: {cooccur1} co-occurrences")
    print(f"  {root2}: {cooccur2} co-occurrences")
    print()

    # Normalize by frequency
    cooccur1_rate = cooccur1 / enrich1["all_count"] if enrich1["all_count"] > 0 else 0
    cooccur2_rate = cooccur2 / enrich2["all_count"] if enrich2["all_count"] > 0 else 0

    print(f"  {root1}: {cooccur1_rate:.2f} co-occur per instance")
    print(f"  {root2}: {cooccur2_rate:.2f} co-occur per instance")
    print()

    ratio = cooccur1_rate / cooccur2_rate if cooccur2_rate > 0 else 0
    if 0.5 < ratio < 2.0:
        print(f"  → Similar co-occurrence (ratio: {ratio:.2f})")
        cooccur_similar = True
    else:
        print(f"  → DIFFERENT co-occurrence (ratio: {ratio:.2f})")
        cooccur_similar = False
    print()

    # Test 3: Case distribution
    print("TEST 3: CASE DISTRIBUTION")
    print("-" * 80)

    cases1 = test_case_distribution(root1, all_words)
    cases2 = test_case_distribution(root2, all_words)

    print(f"  {root1}:")
    for case, data in sorted(cases1.items(), key=lambda x: x[1]["count"], reverse=True)[
        :5
    ]:
        print(f"    -{case:8s}: {data['count']:4d} ({data['percentage']:5.1f}%)")
    print()

    print(f"  {root2}:")
    for case, data in sorted(cases2.items(), key=lambda x: x[1]["count"], reverse=True)[
        :5
    ]:
        print(f"    -{case:8s}: {data['count']:4d} ({data['percentage']:5.1f}%)")
    print()

    # Compare top case
    top_case1 = max(cases1.items(), key=lambda x: x[1]["count"])[0]
    top_case2 = max(cases2.items(), key=lambda x: x[1]["count"])[0]

    if top_case1 == top_case2:
        print(f"  → Similar case preference ({top_case1})")
        case_similar = True
    else:
        print(f"  → DIFFERENT case preference ({top_case1} vs {top_case2})")
        case_similar = False
    print()

    # Test 4: Verbal forms
    print("TEST 4: VERBAL FORMS (-edy)")
    print("-" * 80)

    verbal1 = test_verbal_forms(root1, all_words)
    verbal2 = test_verbal_forms(root2, all_words)

    print(f"  {root1}:")
    print(f"    Takes -edy: {verbal1['has_verbal']}")
    print(f"    Count: {verbal1['verbal_count']}")
    if verbal1["verbal_forms"]:
        print(f"    Forms: {', '.join(verbal1['verbal_forms'][:5])}")
    print()

    print(f"  {root2}:")
    print(f"    Takes -edy: {verbal2['has_verbal']}")
    print(f"    Count: {verbal2['verbal_count']}")
    if verbal2["verbal_forms"]:
        print(f"    Forms: {', '.join(verbal2['verbal_forms'][:5])}")
    print()

    verbal_similar = verbal1["has_verbal"] == verbal2["has_verbal"]

    if verbal_similar:
        print(
            f"  → Both {'take' if verbal1['has_verbal'] else 'do not take'} verbal suffix"
        )
    else:
        print(f"  → DIFFERENT: one takes -edy, other doesn't")
    print()

    # OVERALL VERDICT
    print("=" * 80)
    print("VERDICT")
    print("=" * 80)
    print()

    similarity_score = sum(
        [enrich_similar, cooccur_similar, case_similar, verbal_similar]
    )

    print(f"Similarity score: {similarity_score}/4")
    print()
    print(f"  Enrichment: {'✓ Similar' if enrich_similar else '✗ Different'}")
    print(f"  Co-occurrence: {'✓ Similar' if cooccur_similar else '✗ Different'}")
    print(f"  Case distribution: {'✓ Similar' if case_similar else '✗ Different'}")
    print(f"  Verbal forms: {'✓ Similar' if verbal_similar else '✗ Different'}")
    print()

    if similarity_score >= 3:
        print(f"✓✓ '{root1}' and '{root2}' are LIKELY THE SAME WORD")
        print(f"   → Orthographic variants (spelling variation)")
        print(f"   → Safe to treat as synonyms")
        verdict = "SAME"
    elif similarity_score == 2:
        print(f"~ '{root1}' and '{root2}' show MIXED EVIDENCE")
        print(f"   → Could be related but not identical")
        print(f"   → Need more investigation")
        verdict = "UNCLEAR"
    else:
        print(f"✗✗ '{root1}' and '{root2}' are DIFFERENT WORDS")
        print(f"   → Happen to look similar but distinct meanings")
        print(f"   → DO NOT treat as synonyms")
        verdict = "DIFFERENT"
    print()

    return {
        "root1": root1,
        "root2": root2,
        "enrichment": {"root1": enrich1, "root2": enrich2, "similar": enrich_similar},
        "cooccurrence": {
            "root1": cooccur1,
            "root2": cooccur2,
            "similar": cooccur_similar,
        },
        "cases": {"root1": cases1, "root2": cases2, "similar": case_similar},
        "verbal": {"root1": verbal1, "root2": verbal2, "similar": verbal_similar},
        "similarity_score": similarity_score,
        "verdict": verdict,
    }


def main():
    print("=" * 80)
    print("CRITICAL TEST: 'shee' vs 'she'")
    print("=" * 80)
    print()
    print("HYPOTHESIS TO TEST:")
    print("  Are 'shee' and 'she' orthographic variants of the same word?")
    print("  OR are they different words that happen to look similar?")
    print()
    print("CRITICAL ISSUE:")
    print("  'shee' was validated as WATER (10.3x bath enrichment)")
    print("  'shedy' was validated as VERB (423 instances)")
    print()
    print("  If 'shedy' = 'she' + 'edy', then 'she' is a VERB ROOT, NOT water!")
    print()
    print("METHOD:")
    print("  Compare distributional behavior across 4 tests")
    print("  If same word → should behave identically")
    print("  If different → should have different patterns")
    print()

    # Load data
    f84v_words, all_words = load_data()

    # Compare shee vs she
    result = compare_roots("shee", "she", f84v_words, all_words)

    # Final recommendation
    print()
    print("=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    print()

    if result["verdict"] == "SAME":
        print("PROCEED WITH VARIANT EXPANSION:")
        print("  → Treat shee/she as same word (water)")
        print("  → Re-run translation with expanded matching")
        print("  → Should improve coherence")
    elif result["verdict"] == "UNCLEAR":
        print("INVESTIGATE FURTHER:")
        print("  → Mixed evidence requires deeper analysis")
        print("  → Check if they appear in complementary distribution")
        print("  → May be allomorphs (context-dependent variants)")
    else:
        print("DO NOT EXPAND VARIANTS:")
        print("  → 'shee' and 'she' are DIFFERENT words")
        print("  → Treating them as same would corrupt analysis")
        print("  → Continue searching for more core nouns instead")
        print()
        print("NEXT STEP:")
        print("  → Find vessel/pot term (pharmaceutical section)")
        print("  → Find heat/fire term (cooking contexts)")
        print("  → Need 5-7 core nouns before reliable translation")
    print()

    # Save results
    output_path = Path("results/phase4/shee_vs_she_comparison.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert defaultdicts to regular dicts for JSON
    json_result = {
        "root1": result["root1"],
        "root2": result["root2"],
        "enrichment": {
            "root1": result["enrichment"]["root1"],
            "root2": result["enrichment"]["root2"],
            "similar": result["enrichment"]["similar"],
        },
        "cooccurrence": result["cooccurrence"],
        "verbal": result["verbal"],
        "similarity_score": result["similarity_score"],
        "verdict": result["verdict"],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_result, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
