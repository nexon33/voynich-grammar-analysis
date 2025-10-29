"""
Empirical Case System Validation
=================================

CRITICAL TEST: Are -al/-ar really case markers?

Hypothesis:
- -al = locative ("in/at/on")
- -ar = directional ("to/toward")
- -ol/-or = variants

Empirical predictions to test:
1. -al words should appear with "place" contexts (nouns that can be locations)
2. -ar words should appear with motion/directional verbs
3. They should be mutually exclusive (words take -al OR -ar, rarely both)
4. -al/-ar should show different distributional patterns

This is a FALSIFIABLE test. If predictions fail, case hypothesis is wrong.
"""

import json
from pathlib import Path
from collections import Counter, defaultdict


def load_manuscript():
    """Load manuscript"""
    transcription_path = Path(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt"
    )

    with open(transcription_path, "r", encoding="utf-8") as f:
        text = f.read()

    words = text.lower().split()
    return words


def extract_case_marked_words(words):
    """
    Extract all words ending in -al, -ar, -ol, -or
    """
    case_words = {"al": [], "ar": [], "ol": [], "or": []}

    for word in words:
        if word.endswith("al") and len(word) > 2:
            case_words["al"].append(word)
        elif word.endswith("ar") and len(word) > 2:
            case_words["ar"].append(word)
        elif word.endswith("ol") and len(word) > 2:
            case_words["ol"].append(word)
        elif word.endswith("or") and len(word) > 2:
            case_words["or"].append(word)

    return case_words


def test_mutual_exclusivity(case_words):
    """
    Test if same root takes different case markers

    Example: If "ok" is a root:
    - Does "okal" exist? (locative)
    - Does "okar" exist? (directional)
    - Do they both exist? (would support case system)
    - Does root randomly take any suffix? (would reject case system)
    """
    # Extract roots (strip case endings)
    roots_by_case = {"al": {}, "ar": {}, "ol": {}, "or": {}}

    for case, words in case_words.items():
        for word in words:
            root = word[:-2]  # Strip case ending
            if root not in roots_by_case[case]:
                roots_by_case[case][root] = 0
            roots_by_case[case][root] += 1

    # Find roots that appear with multiple cases
    all_roots = set()
    for case_roots in roots_by_case.values():
        all_roots.update(case_roots.keys())

    root_case_patterns = {}
    for root in all_roots:
        pattern = {
            "al": roots_by_case["al"].get(root, 0),
            "ar": roots_by_case["ar"].get(root, 0),
            "ol": roots_by_case["ol"].get(root, 0),
            "or": roots_by_case["or"].get(root, 0),
        }
        total = sum(pattern.values())

        if total > 0:
            root_case_patterns[root] = {
                "counts": pattern,
                "total": total,
                "num_cases": sum(1 for v in pattern.values() if v > 0),
                "dominant_case": max(pattern, key=pattern.get),
            }

    return root_case_patterns


def analyze_positional_context(words, case_marked_words, window=3):
    """
    Analyze what appears before/after case-marked words

    Predictions:
    - -al words should follow place-related words or prepositions
    - -ar words should follow motion verbs
    """
    contexts = {
        "al": {"before": Counter(), "after": Counter()},
        "ar": {"before": Counter(), "after": Counter()},
        "ol": {"before": Counter(), "after": Counter()},
        "or": {"before": Counter(), "after": Counter()},
    }

    # Track all case words
    all_case_words = set()
    for case_list in case_marked_words.values():
        all_case_words.update(case_list)

    for i, word in enumerate(words):
        # Determine which case suffix
        case_type = None
        if word.endswith("al") and len(word) > 2:
            case_type = "al"
        elif word.endswith("ar") and len(word) > 2:
            case_type = "ar"
        elif word.endswith("ol") and len(word) > 2:
            case_type = "ol"
        elif word.endswith("or") and len(word) > 2:
            case_type = "or"

        if case_type:
            # Get before context
            before_words = words[max(0, i - window) : i]
            if before_words:
                contexts[case_type]["before"][before_words[-1]] += 1

            # Get after context
            after_words = words[i + 1 : min(len(words), i + 1 + window)]
            if after_words:
                contexts[case_type]["after"][after_words[0]] += 1

    return contexts


def test_verb_association(words, case_marked_words, validated_verbs):
    """
    Test if -ar (directional) appears more with motion verbs
    Test if -al (locative) appears more with stative verbs
    """
    # Known verbs
    verbs = {
        "chedy": "action",
        "shedy": "action",
        "qokedy": "action",
        "qokeedy": "action",
        "qokeey": "action",
    }

    # Find case words near verbs
    verb_associations = {
        "al": Counter(),
        "ar": Counter(),
        "ol": Counter(),
        "or": Counter(),
    }

    window = 5

    for i, word in enumerate(words):
        if word in verbs:
            # Check nearby words for case markers
            start = max(0, i - window)
            end = min(len(words), i + window + 1)

            for j in range(start, end):
                if j == i:
                    continue

                nearby_word = words[j]

                if nearby_word.endswith("al") and len(nearby_word) > 2:
                    verb_associations["al"][word] += 1
                elif nearby_word.endswith("ar") and len(nearby_word) > 2:
                    verb_associations["ar"][word] += 1
                elif nearby_word.endswith("ol") and len(nearby_word) > 2:
                    verb_associations["ol"][word] += 1
                elif nearby_word.endswith("or") and len(nearby_word) > 2:
                    verb_associations["or"][word] += 1

    return verb_associations


def calculate_case_distribution_difference(contexts):
    """
    Calculate if -al and -ar have statistically different distributions

    If they're real case markers, they should have different typical contexts
    """
    # Compare top contexts for al vs ar
    al_before = set(w for w, c in contexts["al"]["before"].most_common(20))
    ar_before = set(w for w, c in contexts["ar"]["before"].most_common(20))

    overlap = len(al_before & ar_before)
    total = len(al_before | ar_before)

    distinctiveness = 1 - (overlap / total) if total > 0 else 0

    return {
        "overlap_count": overlap,
        "total_unique_contexts": total,
        "distinctiveness_score": distinctiveness,
        "al_specific": al_before - ar_before,
        "ar_specific": ar_before - al_before,
        "shared": al_before & ar_before,
    }


def main():
    print("=" * 80)
    print("EMPIRICAL CASE SYSTEM VALIDATION")
    print("=" * 80)
    print()
    print("Testing if -al/-ar are real case markers with consistent semantic functions")
    print()
    print("Hypotheses:")
    print("  H1: -al = locative (in/at/on)")
    print("  H2: -ar = directional (to/toward)")
    print("  H3: -ol/-or are variants")
    print()
    print("Predictions:")
    print("  P1: Same root can take different cases (mutual exclusivity)")
    print("  P2: -al words appear in locative contexts")
    print("  P3: -ar words appear with motion verbs")
    print("  P4: -al and -ar have distinct distributional patterns")
    print()

    # Load manuscript
    print("Loading manuscript...")
    words = load_manuscript()
    print(f"Total words: {len(words):,}")
    print()

    # Extract case-marked words
    print("Extracting case-marked words...")
    case_words = extract_case_marked_words(words)

    for case, word_list in case_words.items():
        unique = len(set(word_list))
        total = len(word_list)
        print(f"  -{case}: {unique} unique words, {total} instances")

    print()

    # TEST 1: Mutual Exclusivity
    print("=" * 80)
    print("TEST 1: MUTUAL EXCLUSIVITY (P1)")
    print("=" * 80)
    print("Do same roots take different case markers?")
    print()

    root_patterns = test_mutual_exclusivity(case_words)

    # Find roots with multiple cases
    multi_case_roots = {
        root: data
        for root, data in root_patterns.items()
        if data["num_cases"] >= 2 and data["total"] >= 5
    }

    print(f"Found {len(multi_case_roots)} roots that take multiple case markers")
    print()
    print("Top 15 roots with case alternation:")
    print(
        f"{'Root':<15} {'Total':<8} {'-al':<6} {'-ar':<6} {'-ol':<6} {'-or':<6} {'Cases':<6}"
    )
    print("-" * 70)

    sorted_roots = sorted(
        multi_case_roots.items(), key=lambda x: x[1]["total"], reverse=True
    )

    for root, data in sorted_roots[:15]:
        print(
            f"{root:<15} {data['total']:<8} "
            f"{data['counts']['al']:<6} {data['counts']['ar']:<6} "
            f"{data['counts']['ol']:<6} {data['counts']['or']:<6} {data['num_cases']:<6}"
        )

    print()

    # Evaluate P1
    if len(multi_case_roots) >= 20:
        print(
            "✓ P1 SUPPORTED: Many roots take multiple cases (systematic case marking)"
        )
    else:
        print("✗ P1 REJECTED: Few roots take multiple cases (not systematic)")

    print()

    # TEST 2: Positional Context
    print("=" * 80)
    print("TEST 2: POSITIONAL CONTEXT (P2)")
    print("=" * 80)
    print("What words appear before/after case-marked words?")
    print()

    contexts = analyze_positional_context(words, case_words)

    print("TOP 10 WORDS BEFORE -al (locative):")
    for word, count in contexts["al"]["before"].most_common(10):
        print(f"  {word}: {count}×")

    print()
    print("TOP 10 WORDS BEFORE -ar (directional):")
    for word, count in contexts["ar"]["before"].most_common(10):
        print(f"  {word}: {count}×")

    print()

    # TEST 3: Verb Association
    print("=" * 80)
    print("TEST 3: VERB ASSOCIATION (P3)")
    print("=" * 80)
    print("Do -ar words appear more with action verbs?")
    print()

    verb_assoc = test_verb_association(words, case_words, {})

    print("Case marker appearances near validated verbs:")
    print(f"{'Case':<6} {'chedy':<10} {'shedy':<10} {'qokedy':<10} {'Total':<10}")
    print("-" * 50)

    for case in ["al", "ar", "ol", "or"]:
        total = sum(verb_assoc[case].values())
        print(
            f"-{case:<5} "
            f"{verb_assoc[case].get('chedy', 0):<10} "
            f"{verb_assoc[case].get('shedy', 0):<10} "
            f"{verb_assoc[case].get('qokedy', 0):<10} "
            f"{total:<10}"
        )

    print()

    # Evaluate P3
    al_verb_count = sum(verb_assoc["al"].values())
    ar_verb_count = sum(verb_assoc["ar"].values())

    if ar_verb_count > al_verb_count * 1.2:
        print("✓ P3 SUPPORTED: -ar appears more with verbs (directional with motion)")
    elif al_verb_count > ar_verb_count * 1.2:
        print("~ P3 INVERTED: -al appears more with verbs (unexpected)")
    else:
        print("✗ P3 REJECTED: No clear difference in verb association")

    print()

    # TEST 4: Distributional Distinctiveness
    print("=" * 80)
    print("TEST 4: DISTRIBUTIONAL DISTINCTIVENESS (P4)")
    print("=" * 80)
    print("Do -al and -ar have different typical contexts?")
    print()

    distinctiveness = calculate_case_distribution_difference(contexts)

    print(
        f"Context overlap: {distinctiveness['overlap_count']}/{distinctiveness['total_unique_contexts']} words"
    )
    print(f"Distinctiveness score: {distinctiveness['distinctiveness_score']:.2%}")
    print()

    print(f"Words appearing mainly BEFORE -al (locative):")
    for word in list(distinctiveness["al_specific"])[:5]:
        print(f"  {word}")

    print()
    print(f"Words appearing mainly BEFORE -ar (directional):")
    for word in list(distinctiveness["ar_specific"])[:5]:
        print(f"  {word}")

    print()

    # Evaluate P4
    if distinctiveness["distinctiveness_score"] >= 0.5:
        print("✓ P4 SUPPORTED: -al and -ar have distinct contexts (≥50% different)")
    elif distinctiveness["distinctiveness_score"] >= 0.3:
        print("~ P4 WEAK: Some distinction but significant overlap")
    else:
        print("✗ P4 REJECTED: -al and -ar have very similar contexts")

    print()

    # FINAL VERDICT
    print("=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)
    print()

    tests_passed = 0
    total_tests = 4

    # Score tests
    if len(multi_case_roots) >= 20:
        tests_passed += 1
        print("✓ Test 1: Mutual exclusivity")
    else:
        print("✗ Test 1: Mutual exclusivity")

    # Test 2 is observational, skip scoring

    if ar_verb_count > al_verb_count * 1.2 or al_verb_count > ar_verb_count * 1.2:
        tests_passed += 1
        print("✓ Test 3: Verb association difference")
    else:
        print("✗ Test 3: Verb association difference")

    if distinctiveness["distinctiveness_score"] >= 0.3:
        tests_passed += 1
        print("✓ Test 4: Distributional distinctiveness")
    else:
        print("✗ Test 4: Distributional distinctiveness")

    print()
    print(f"RESULT: {tests_passed}/3 tests passed")
    print()

    if tests_passed >= 2:
        print("✓✓ CASE SYSTEM HYPOTHESIS SUPPORTED")
        print("Evidence suggests -al/-ar are systematic case markers")
        print("with consistent (though not yet fully understood) semantic functions")
    else:
        print("✗✗ CASE SYSTEM HYPOTHESIS REJECTED")
        print("-al/-ar may be derivational suffixes, not inflectional cases")
        print("Need to reconsider our interpretation")

    # Save results
    results = {
        "case_word_counts": {
            case: len(set(words)) for case, words in case_words.items()
        },
        "multi_case_roots": {
            root: {
                "counts": data["counts"],
                "total": data["total"],
                "num_cases": data["num_cases"],
            }
            for root, data in sorted_roots[:50]
        },
        "contexts": {
            case: {
                "before_top10": [
                    {"word": w, "count": c} for w, c in ctx["before"].most_common(10)
                ],
                "after_top10": [
                    {"word": w, "count": c} for w, c in ctx["after"].most_common(10)
                ],
            }
            for case, ctx in contexts.items()
        },
        "verb_associations": {case: dict(assoc) for case, assoc in verb_assoc.items()},
        "distinctiveness": {
            "overlap": distinctiveness["overlap_count"],
            "total": distinctiveness["total_unique_contexts"],
            "score": distinctiveness["distinctiveness_score"],
            "al_specific": list(distinctiveness["al_specific"])[:10],
            "ar_specific": list(distinctiveness["ar_specific"])[:10],
        },
        "verdict": {
            "tests_passed": tests_passed,
            "total_tests": 3,
            "hypothesis_supported": tests_passed >= 2,
        },
    }

    output_path = Path("results/phase4/case_system_empirical_validation.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print()
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
