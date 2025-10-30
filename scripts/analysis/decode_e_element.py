#!/usr/bin/env python3
"""
Decode [?e] - The Big One (1,165+ instances, 3.1% of corpus)

Determine if [?e] is:
1. ASPECTUAL MARKER (grammatical - continuous/ongoing/iterative)
2. LEXICAL ROOT (semantic - high-frequency verb like "make/do")

This is the HIGHEST PRIORITY unknown - decoding it could jump recognition by 3%
"""

import json
import re
from collections import Counter, defaultdict


def load_translations():
    """Load the complete manuscript translation"""
    with open(
        "COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)
        return data["translations"]


def find_standalone_e(translations):
    """
    Test 1: Standalone usage

    If [?e] is ASPECTUAL: Should rarely appear standalone (grammatical marker)
    If [?e] is LEXICAL: Should appear standalone frequently (actual word)
    """
    standalone = []

    for trans in translations:
        sentence = trans["final_translation"]
        words = sentence.split()

        for i, word in enumerate(words):
            # Check for standalone [?e] (not part of compound)
            if word == "[?e]":
                before = words[max(0, i - 3) : i]
                after = words[i + 1 : min(len(words), i + 3 + 1)]

                standalone.append(
                    {
                        "line": trans.get("line", "unknown"),
                        "before": before,
                        "after": after,
                        "full_sentence": sentence,
                    }
                )

    return standalone


def find_unique_roots_before_e(translations):
    """
    Test 2: Root diversity

    If [?e] is ASPECTUAL: Should combine with MANY different roots (grammatical)
    If [?e] is LEXICAL: Should combine with FEW roots (it IS a root)
    """
    roots_before_e = Counter()

    # Pattern: anything + [?e] + something
    # e.g., "oak-GEN-[?e]-VERB" → root is "oak-GEN"

    for trans in translations:
        sentence = trans["final_translation"]

        # Find all instances of [?e] in compounds
        # Pattern: WORD-[?e]-SUFFIX or WORD-[?e]
        pattern = r"(\S+)-\[\?e\](?:-|$)"
        matches = re.finditer(pattern, sentence)

        for match in matches:
            root_before = match.group(1)
            # Clean up the root (remove any leading stuff)
            if root_before:
                roots_before_e[root_before] += 1

    return roots_before_e


def analyze_positions(translations):
    """
    Test 3: Position analysis

    If [?e] is ASPECTUAL: Should appear MEDIALLY (between root and suffix)
    If [?e] is LEXICAL: Should appear INITIALLY (start of compound)
    """
    positions = {
        "initial": 0,  # [?e]-X
        "medial": 0,  # X-[?e]-Y
        "final": 0,  # X-[?e]
        "standalone": 0,  # [?e]
    }

    for trans in translations:
        sentence = trans["final_translation"]
        words = sentence.split()

        for word in words:
            if "[?e]" in word:
                # Standalone
                if word == "[?e]":
                    positions["standalone"] += 1
                # Initial: [?e]-X
                elif word.startswith("[?e]-"):
                    positions["initial"] += 1
                # Final: X-[?e]
                elif word.endswith("-[?e]"):
                    positions["final"] += 1
                # Medial: X-[?e]-Y
                elif "-[?e]-" in word:
                    positions["medial"] += 1

    total = sum(positions.values())
    if total > 0:
        # Create percentage keys separately to avoid modifying dict during iteration
        pct_dict = {}
        for pos in ["initial", "medial", "final", "standalone"]:
            pct_dict[f"{pos}_pct"] = positions[pos] / total
        positions.update(pct_dict)

    return positions


def find_elements_after_e(translations):
    """
    Test 4: What follows [?e]?

    If [?e] is ASPECTUAL: Should be followed by VERBS (marks verbal aspect)
    If [?e] is LEXICAL: Could be followed by anything
    """
    after_e = Counter()

    for trans in translations:
        sentence = trans["final_translation"]

        # Pattern: [?e]-X where X is the next element
        pattern = r"\[\?e\]-(\w+)"
        matches = re.finditer(pattern, sentence)

        for match in matches:
            element_after = match.group(1)
            after_e[element_after] += 1

    return after_e


def analyze_e_with_oak_oat(translations):
    """
    Special test: oak-GEN-[?e]-VERB pattern

    This is the most common pattern in the manuscript
    Understanding this could unlock major semantic content
    """
    oak_e_pattern = []
    oat_e_pattern = []

    for trans in translations:
        sentence = trans["final_translation"]

        # Find oak-GEN-[?e]-VERB
        if "oak-GEN-[?e]" in sentence:
            oak_e_pattern.append(
                {"line": trans.get("line", "unknown"), "sentence": sentence}
            )

        # Find oat-GEN-[?e]-VERB
        if "oat-GEN-[?e]" in sentence:
            oat_e_pattern.append(
                {"line": trans.get("line", "unknown"), "sentence": sentence}
            )

    return oak_e_pattern, oat_e_pattern


def main():
    """Main analysis"""
    print("=" * 70)
    print("DECODING [?e] - THE BIG ONE")
    print("=" * 70)
    print("\n[?e] is the highest-frequency unknown: 1,165+ instances (3.1% of corpus)")
    print("Decoding this could jump recognition rate by 2.5-3.0%\n")

    print("Loading translations...")
    translations = load_translations()
    print(f"Loaded {len(translations)} translations\n")

    # TEST 1: Standalone usage
    print("=" * 70)
    print("TEST 1: STANDALONE USAGE")
    print("=" * 70)
    print("If [?e] is ASPECTUAL: Should be rare (grammatical marker)")
    print("If [?e] is LEXICAL: Should be common (actual word)\n")

    standalone = find_standalone_e(translations)
    print(f"Result: {len(standalone)} standalone instances of [?e]")

    if standalone:
        print("\nSample contexts (first 5):")
        for i, ctx in enumerate(standalone[:5], 1):
            print(f"\n  {i}. {ctx['line']}")
            print(
                f"     ...{' '.join(ctx['before'])} **[?e]** {' '.join(ctx['after'])}..."
            )

    # Interpretation
    if len(standalone) < 20:
        print(
            f"\n→ EVIDENCE FOR ASPECTUAL: Only {len(standalone)} standalone instances (rare)"
        )
    else:
        print(
            f"\n→ EVIDENCE FOR LEXICAL: {len(standalone)} standalone instances (common)"
        )

    # TEST 2: Root diversity
    print("\n" + "=" * 70)
    print("TEST 2: ROOT DIVERSITY")
    print("=" * 70)
    print("If [?e] is ASPECTUAL: Should combine with MANY roots (>15)")
    print("If [?e] is LEXICAL: Should combine with FEW roots (<10)\n")

    roots_before_e = find_unique_roots_before_e(translations)
    print(f"Result: {len(roots_before_e)} unique roots combine with [?e]")

    print(f"\nTop 20 roots before [?e]:")
    for root, count in roots_before_e.most_common(20):
        print(f"  {root}-[?e]: {count}×")

    # Interpretation
    if len(roots_before_e) > 15:
        print(
            f"\n→ EVIDENCE FOR ASPECTUAL: Combines with {len(roots_before_e)} different roots (highly productive)"
        )
    else:
        print(
            f"\n→ EVIDENCE FOR LEXICAL: Only {len(roots_before_e)} roots (limited productivity)"
        )

    # TEST 3: Position analysis
    print("\n" + "=" * 70)
    print("TEST 3: POSITION ANALYSIS")
    print("=" * 70)
    print("If [?e] is ASPECTUAL: Should be MEDIAL (between root and suffix) >70%")
    print("If [?e] is LEXICAL: Should be INITIAL or STANDALONE\n")

    positions = analyze_positions(translations)

    print(f"Position distribution:")
    print(
        f"  Standalone: {positions['standalone']} ({positions.get('standalone_pct', 0):.1%})"
    )
    print(
        f"  Initial ([?e]-X): {positions['initial']} ({positions.get('initial_pct', 0):.1%})"
    )
    print(
        f"  Medial (X-[?e]-Y): {positions['medial']} ({positions.get('medial_pct', 0):.1%})"
    )
    print(
        f"  Final (X-[?e]): {positions['final']} ({positions.get('final_pct', 0):.1%})"
    )

    # Interpretation
    medial_pct = positions.get("medial_pct", 0)
    if medial_pct > 0.7:
        print(
            f"\n→ EVIDENCE FOR ASPECTUAL: {medial_pct:.1%} medial position (grammatical marker)"
        )
    else:
        print(
            f"\n→ EVIDENCE FOR LEXICAL: Only {medial_pct:.1%} medial (not primarily grammatical)"
        )

    # TEST 4: Elements after [?e]
    print("\n" + "=" * 70)
    print("TEST 4: WHAT FOLLOWS [?e]?")
    print("=" * 70)
    print("If [?e] is ASPECTUAL: Should be followed by VERBS (marks aspect)")
    print("If [?e] is LEXICAL: Could be followed by anything\n")

    after_e = find_elements_after_e(translations)

    print(f"Top 15 elements after [?e]:")
    for element, count in after_e.most_common(15):
        print(f"  [?e]-{element}: {count}×")

    # Count VERBs
    verb_after = sum(count for elem, count in after_e.items() if "VERB" in elem)
    total_after = sum(after_e.values())
    verb_pct = verb_after / total_after if total_after > 0 else 0

    print(f"\nVERB suffixes after [?e]: {verb_after}/{total_after} ({verb_pct:.1%})")

    # Interpretation
    if verb_pct > 0.5:
        print(
            f"\n→ EVIDENCE FOR ASPECTUAL: {verb_pct:.1%} followed by VERB (marks verbal aspect)"
        )
    else:
        print(f"\n→ EVIDENCE FOR LEXICAL: Only {verb_pct:.1%} followed by VERB")

    # SPECIAL TEST: oak-GEN-[?e]-VERB pattern
    print("\n" + "=" * 70)
    print("SPECIAL TEST: oak-GEN-[?e]-VERB PATTERN")
    print("=" * 70)
    print("This is the most common [?e] pattern in the manuscript\n")

    oak_e, oat_e = analyze_e_with_oak_oat(translations)

    print(f"oak-GEN-[?e]: {len(oak_e)} instances")
    print(f"oat-GEN-[?e]: {len(oat_e)} instances")
    print(f"Total: {len(oak_e) + len(oat_e)} instances")

    print("\nSample oak-GEN-[?e] contexts (first 5):")
    for i, ctx in enumerate(oak_e[:5], 1):
        print(f"  {i}. {ctx['line']}: {ctx['sentence'][:100]}...")

    # FINAL CLASSIFICATION
    print("\n" + "=" * 70)
    print("FINAL CLASSIFICATION")
    print("=" * 70)

    # Count evidence
    aspectual_evidence = 0
    lexical_evidence = 0

    # Test 1: Standalone
    if len(standalone) < 20:
        aspectual_evidence += 1
        print("✓ Test 1 (Standalone): ASPECTUAL")
    else:
        lexical_evidence += 1
        print("✓ Test 1 (Standalone): LEXICAL")

    # Test 2: Root diversity
    if len(roots_before_e) > 15:
        aspectual_evidence += 1
        print("✓ Test 2 (Root diversity): ASPECTUAL")
    else:
        lexical_evidence += 1
        print("✓ Test 2 (Root diversity): LEXICAL")

    # Test 3: Position
    if medial_pct > 0.7:
        aspectual_evidence += 1
        print("✓ Test 3 (Position): ASPECTUAL")
    else:
        lexical_evidence += 1
        print("✓ Test 3 (Position): LEXICAL")

    # Test 4: After elements
    if verb_pct > 0.5:
        aspectual_evidence += 1
        print("✓ Test 4 (After [?e]): ASPECTUAL")
    else:
        lexical_evidence += 1
        print("✓ Test 4 (After [?e]): LEXICAL")

    print(f"\nEvidence summary:")
    print(f"  ASPECTUAL: {aspectual_evidence}/4 tests")
    print(f"  LEXICAL: {lexical_evidence}/4 tests")

    if aspectual_evidence >= 3:
        classification = "ASPECTUAL MARKER"
        confidence = "HIGH" if aspectual_evidence == 4 else "MODERATE"
        function = "Continuous/ongoing/iterative aspect"
        translation = "-ing, continuously, repeatedly"

        print(f"\n{'=' * 70}")
        print(f"CONCLUSION: [?e] is an ASPECTUAL MARKER ({confidence} confidence)")
        print(f"{'=' * 70}")
        print(f"Function: {function}")
        print(f"Translation: {translation}")
        print(f"\nMeaning:")
        print(f"  oak-GEN-[?e]-VERB = 'oak-related CONTINUOUS processing'")
        print(f"  = 'Continue processing with oak'")
        print(f"  = 'Ongoing oak preparation'")

        print(f"\nMedieval parallel:")
        print(f"  Latin gerund/gerundive: -ndum, -ndus (ongoing action)")
        print(f"  English -ing (continuous aspect)")

        print(f"\nImpact:")
        print(f"  Recognition gain: +2.5-3.0%")
        print(f"  This explains repetition in recipes (continuous/repeated actions)")

    else:
        classification = "LEXICAL ROOT"
        confidence = "HIGH" if lexical_evidence == 4 else "MODERATE"
        function = "High-frequency verb"
        translation = "make, do, take, use"

        print(f"\n{'=' * 70}")
        print(f"CONCLUSION: [?e] is a LEXICAL ROOT ({confidence} confidence)")
        print(f"{'=' * 70}")
        print(f"Function: {function}")
        print(f"Translation: {translation}")
        print(f"\nMeaning:")
        print(f"  oak-GEN-[?e]-VERB = 'oak-related making/doing'")
        print(f"  = 'Make with oak'")
        print(f"  = 'Do [action] with oak'")

        print(f"\nMedieval parallel:")
        print(f"  Latin 'facere' (make/do) - most common verb in recipes")
        print(f"  English 'make', 'take' - extremely frequent in herbals")

        print(f"\nImpact:")
        print(f"  Recognition gain: +2.5-3.0%")
        print(f"  This is likely THE most common action verb")

    # Save results
    results = {
        "classification": classification,
        "confidence": confidence,
        "standalone_count": len(standalone),
        "unique_roots": len(roots_before_e),
        "position_distribution": positions,
        "verb_following_pct": verb_pct,
        "aspectual_evidence": aspectual_evidence,
        "lexical_evidence": lexical_evidence,
        "top_roots": dict(roots_before_e.most_common(30)),
        "top_after": dict(after_e.most_common(30)),
        "oak_e_count": len(oak_e),
        "oat_e_count": len(oat_e),
        "sample_standalone": [
            {"line": ctx["line"], "before": ctx["before"], "after": ctx["after"]}
            for ctx in standalone[:10]
        ],
    }

    print(f"\nSaving results to E_ELEMENT_ANALYSIS.json...")
    with open("E_ELEMENT_ANALYSIS.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

    return results


if __name__ == "__main__":
    main()
