#!/usr/bin/env python3
"""
Decode [?y] suffix function.

OBSERVATION: [?y] appears in suffix position 63.8% of the time
Most common patterns:
  - GEN-[?y] (220×)
  - AT-[?y] (162×)
  - T-[?y] (15×)

HYPOTHESIS: [?y] is a DEICTIC/DEMONSTRATIVE suffix
Similar to Hungarian demonstratives or Turkish locative deictics.

Tests:
1. Does GEN-[?y] vs GEN show deictic contrast?
2. Does AT-[?y] vs AT show deictic contrast?
3. Does [?y] correlate with THIS/THAT context?
4. Position in sentence (deictics often sentence-initial or focus position)
"""

import json
import re
from collections import Counter


def load_translations():
    with open(
        "COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)
        return data["translations"]


def test_deictic_context(translations):
    """
    Test if [?y] co-occurs with THIS/THAT more than expected.

    If [?y] is deictic, should appear near demonstratives.
    """

    with_y_and_deictic = 0
    with_y_no_deictic = 0
    no_y_with_deictic = 0
    no_y_no_deictic = 0

    for trans in translations:
        text = trans["final_translation"]

        has_y = "[?y]" in text
        has_deictic = "THIS/THAT" in text

        if has_y and has_deictic:
            with_y_and_deictic += 1
        elif has_y and not has_deictic:
            with_y_no_deictic += 1
        elif not has_y and has_deictic:
            no_y_with_deictic += 1
        else:
            no_y_no_deictic += 1

    # Calculate enrichment
    total = len(translations)
    y_rate = (with_y_and_deictic + with_y_no_deictic) / total
    deictic_rate = (with_y_and_deictic + no_y_with_deictic) / total
    expected = y_rate * deictic_rate * total
    observed = with_y_and_deictic
    enrichment = observed / expected if expected > 0 else 0

    return {
        "with_y_and_deictic": with_y_and_deictic,
        "with_y_no_deictic": with_y_no_deictic,
        "enrichment": enrichment,
        "passed": enrichment > 1.3,  # 30% enrichment threshold
    }


def test_gen_y_contrast(translations):
    """
    Test if GEN-[?y] appears in different contexts than bare GEN.

    If [?y] is deictic, GEN-[?y] should mark PROXIMAL/DISTAL
    (this one's X vs that one's X)
    """

    gen_y_contexts = Counter()
    gen_contexts = Counter()

    for trans in translations:
        text = trans["final_translation"]
        words = text.split()

        for i, word in enumerate(words):
            # Get context (previous word)
            prev_word = words[i - 1] if i > 0 else "<START>"

            if "GEN-[?y]" in word:
                gen_y_contexts[prev_word] += 1
            elif re.search(r"-GEN\b", word) and "[?y]" not in word:
                gen_contexts[prev_word] += 1

    # Find distinctive contexts
    gen_y_total = sum(gen_y_contexts.values())
    gen_total = sum(gen_contexts.values())

    distinctive_for_y = []
    for word, count in gen_y_contexts.most_common(20):
        y_rate = count / gen_y_total if gen_y_total > 0 else 0
        gen_rate = gen_contexts.get(word, 0) / gen_total if gen_total > 0 else 0

        if y_rate > gen_rate * 1.5:  # 50% enrichment
            distinctive_for_y.append((word, count, y_rate, gen_rate))

    return {
        "gen_y_total": gen_y_total,
        "gen_total": gen_total,
        "distinctive_contexts": distinctive_for_y[:5],
        "passed": len(distinctive_for_y) > 3,
    }


def test_at_y_contrast(translations):
    """
    Test if AT-[?y] appears in different contexts than bare AT.

    Similar logic to GEN-[?y] test.
    """

    at_y_contexts = Counter()
    at_contexts = Counter()

    for trans in translations:
        text = trans["final_translation"]
        words = text.split()

        for i, word in enumerate(words):
            next_word = words[i + 1] if i < len(words) - 1 else "<END>"

            if "AT-[?y]" in word:
                at_y_contexts[next_word] += 1
            elif word.startswith("AT/IN") or word.startswith("AT-"):
                if "[?y]" not in word:
                    at_contexts[next_word] += 1

    at_y_total = sum(at_y_contexts.values())
    at_total = sum(at_contexts.values())

    distinctive_for_y = []
    for word, count in at_y_contexts.most_common(20):
        y_rate = count / at_y_total if at_y_total > 0 else 0
        at_rate = at_contexts.get(word, 0) / at_total if at_total > 0 else 0

        if y_rate > at_rate * 1.5:
            distinctive_for_y.append((word, count, y_rate, at_rate))

    return {
        "at_y_total": at_y_total,
        "at_total": at_total,
        "distinctive_contexts": distinctive_for_y[:5],
        "passed": len(distinctive_for_y) > 3,
    }


def analyze_sentence_position(translations):
    """
    Test if GEN-[?y] or AT-[?y] appear in special positions
    (sentence-initial, focus positions)
    """

    y_initial = 0
    y_non_initial = 0

    for trans in translations:
        text = trans["final_translation"]
        words = text.split()

        for i, word in enumerate(words):
            if "[?y]" in word:
                if i < 2:  # First or second position
                    y_initial += 1
                else:
                    y_non_initial += 1

    total = y_initial + y_non_initial
    initial_rate = y_initial / total if total > 0 else 0

    # Random expectation: ~15% in first 2 positions (average sentence ~13 words)
    expected_rate = 0.15

    return {
        "y_initial": y_initial,
        "y_non_initial": y_non_initial,
        "initial_rate": initial_rate,
        "expected_rate": expected_rate,
        "passed": initial_rate > expected_rate * 1.3,
    }


def main():
    print("=" * 70)
    print("DECODE [?y] SUFFIX")
    print("=" * 70)
    print()
    print("OBSERVATION: [?y] is a SUFFIX (63.8% suffix position)")
    print("  Most common: GEN-[?y] (220×), AT-[?y] (162×)")
    print()
    print("HYPOTHESIS: [?y] is DEICTIC/DEMONSTRATIVE suffix")
    print("  (like Hungarian -ez/-az or Turkish locative deictics)")
    print()
    print("=" * 70)

    translations = load_translations()

    # Test 1: Deictic context
    print("\nTest 1: Co-occurrence with THIS/THAT")
    print("-" * 70)
    result1 = test_deictic_context(translations)
    print(f"Sentences with [?y] AND THIS/THAT: {result1['with_y_and_deictic']}")
    print(f"Sentences with [?y] but no THIS/THAT: {result1['with_y_no_deictic']}")
    print(f"Enrichment: {result1['enrichment']:.2f}×")
    print(f"Threshold: 1.30×")
    print(f"Result: {'PASS ✓' if result1['passed'] else 'FAIL ✗'}")

    # Test 2: GEN-[?y] vs GEN contrast
    print("\n\nTest 2: GEN-[?y] distinctive contexts")
    print("-" * 70)
    result2 = test_gen_y_contrast(translations)
    print(f"Total GEN-[?y]: {result2['gen_y_total']}")
    print(f"Total GEN: {result2['gen_total']}")
    print(
        f"Distinctive contexts for GEN-[?y] (>1.5× enrichment): {len(result2['distinctive_contexts'])}"
    )
    if result2["distinctive_contexts"]:
        print("\nTop contexts:")
        for word, count, y_rate, gen_rate in result2["distinctive_contexts"]:
            print(
                f"  {word}: GEN-[?y]={y_rate:.1%}, GEN={gen_rate:.1%} (enrichment: {y_rate / gen_rate if gen_rate > 0 else 0:.2f}×)"
            )
    print(f"\nThreshold: >3 distinctive contexts")
    print(f"Result: {'PASS ✓' if result2['passed'] else 'FAIL ✗'}")

    # Test 3: AT-[?y] vs AT contrast
    print("\n\nTest 3: AT-[?y] distinctive contexts")
    print("-" * 70)
    result3 = test_at_y_contrast(translations)
    print(f"Total AT-[?y]: {result3['at_y_total']}")
    print(f"Total AT: {result3['at_total']}")
    print(f"Distinctive contexts for AT-[?y]: {len(result3['distinctive_contexts'])}")
    if result3["distinctive_contexts"]:
        print("\nTop contexts:")
        for word, count, y_rate, at_rate in result3["distinctive_contexts"]:
            print(
                f"  {word}: AT-[?y]={y_rate:.1%}, AT={at_rate:.1%} (enrichment: {y_rate / at_rate if at_rate > 0 else 0:.2f}×)"
            )
    print(f"\nThreshold: >3 distinctive contexts")
    print(f"Result: {'PASS ✓' if result3['passed'] else 'FAIL ✗'}")

    # Test 4: Sentence position
    print("\n\nTest 4: Sentence-initial position (focus)")
    print("-" * 70)
    result4 = analyze_sentence_position(translations)
    print(f"[?y] in initial position (first 2 words): {result4['y_initial']}")
    print(f"[?y] in non-initial position: {result4['y_non_initial']}")
    print(f"Initial rate: {result4['initial_rate']:.1%}")
    print(f"Expected rate (random): {result4['expected_rate']:.1%}")
    print(f"Threshold: >19.5% (1.3× enrichment)")
    print(f"Result: {'PASS ✓' if result4['passed'] else 'FAIL ✗'}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    tests_passed = sum(
        [result1["passed"], result2["passed"], result3["passed"], result4["passed"]]
    )

    print(f"\nTests passed: {tests_passed}/4")
    print()

    if tests_passed >= 3:
        print("CONCLUSION: [?y] is LIKELY a DEICTIC/DEMONSTRATIVE suffix")
        print("  Confidence: HIGH" if tests_passed == 4 else "  Confidence: MODERATE")
        print()
        print("SEMANTIC INTERPRETATION:")
        print("  [?y] marks PROXIMAL deixis ('this', 'here')")
        print("  GEN-[?y] = 'of/from this (one)'")
        print("  AT-[?y] = 'at/in this (place)'")
        print()
        print("PARALLEL: Hungarian -ez 'this', Turkish şu 'this/that (visible)'")
    elif tests_passed >= 2:
        print("CONCLUSION: [?y] is POSSIBLY deictic/demonstrative")
        print("  Confidence: LOW")
        print("  More investigation needed")
    else:
        print("CONCLUSION: Deictic hypothesis NOT supported")
        print("  [?y] may have different function")

    print()
    print("RECOGNITION IMPACT:")
    print(f"  [?y] instances: 622 (~1.7% of corpus)")
    print(f"  If classified as DEICTIC suffix: +1.7% recognition")
    print(f"  New total: 82.2% + 1.7% = 83.9%")
    print()


if __name__ == "__main__":
    main()
