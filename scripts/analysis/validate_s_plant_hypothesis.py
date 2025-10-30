#!/usr/bin/env python3
"""
Validate [?s] = "plant/herb" hypothesis

Evidence from Phase 20:
- [?s]: 694 instances (1.9% of corpus)
- VERB suffix rate: 0.7% (extremely low - nominal)
- Co-occurs with botanical-term: 27×
- Appears with definiteness markers
- Standalone rate: 22.6%

Test: If [?s] means "plant/herb", it should:
1. Cluster in Herbal section (botanical context)
2. Co-occur with botanical-term frequently
3. Appear with THIS/THAT (pointing to illustrations)
4. Take definiteness markers ([?s]-DEF = "the plant")
5. Appear in preparation contexts (botanical processing)
"""

import json
import re
from collections import Counter, defaultdict


def load_translations():
    """Load translations"""
    with open(
        "COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)
        return data["translations"]


def build_folio_mapping():
    """Build mapping from line numbers to folios"""
    line_to_folio = {}

    with open(
        "data/voynich/eva_transcription/ZL3b-n.txt",
        "r",
        encoding="utf-8",
        errors="ignore",
    ) as f:
        line_num = 0
        for file_line in f:
            if file_line.startswith("#") or not file_line.strip():
                continue

            folio_match = re.search(r"<(f\d+[rv])\.?\d*[^>]*>", file_line)
            if folio_match:
                folio = folio_match.group(1)
                line_num += 1
                line_to_folio[line_num] = folio

    return line_to_folio


def classify_folio(folio):
    """Classify folio into manuscript sections"""
    match = re.search(r"f(\d+)", folio)
    if not match:
        return "unknown"
    num = int(match.group(1))

    if 1 <= num <= 66:
        return "herbal"
    elif 67 <= num <= 73:
        return "astronomical"
    elif 75 <= num <= 84:
        return "biological"
    elif 87 <= num <= 102:
        return "pharmaceutical"
    elif 103 <= num <= 116:
        return "stars"
    else:
        return "unknown"


def test_herbal_enrichment(translations, line_to_folio):
    """
    Test 1: Herbal section enrichment

    If [?s] = "plant/herb", should be ENRICHED in Herbal section
    (where botanical illustrations are)
    """
    section_counts = defaultdict(int)
    section_totals = defaultdict(int)
    s_in_sections = defaultdict(list)

    for trans in translations:
        line_id = trans.get("line", "unknown")

        # Extract line number
        line_match = re.search(r"line(\d+)", line_id)
        if not line_match:
            continue

        line_num = int(line_match.group(1))
        folio = line_to_folio.get(line_num, None)

        if not folio:
            continue

        section = classify_folio(folio)
        section_totals[section] += 1

        sentence = trans["final_translation"]
        if "[?s]" in sentence:
            section_counts[section] += 1
            s_in_sections[section].append(
                {"line": line_id, "folio": folio, "sentence": sentence}
            )

    # Calculate enrichment
    enrichment = {}
    for section in section_totals:
        if section_totals[section] > 0:
            observed = section_counts[section] / section_totals[section]

            # Baseline: overall [?s] frequency
            total_s = sum(section_counts.values())
            total_lines = sum(section_totals.values())
            baseline = total_s / total_lines if total_lines > 0 else 0

            enrichment[section] = (observed / baseline) if baseline > 0 else 0

    return section_counts, section_totals, enrichment, s_in_sections


def test_botanical_cooccurrence(translations):
    """
    Test 2: botanical-term co-occurrence

    If [?s] = "plant/herb", should co-occur with botanical-term
    Pattern: "botanical-term [?s]" = "[named plant] herb"
    """
    botanical_s = []

    for trans in translations:
        sentence = trans["final_translation"]

        if "botanical-term" in sentence and "[?s]" in sentence:
            words = sentence.split()
            bot_indices = [i for i, w in enumerate(words) if "botanical-term" in w]
            s_indices = [i for i, w in enumerate(words) if "[?s]" in w]

            # Check if they're close (within 5 words)
            for b_idx in bot_indices:
                for s_idx in s_indices:
                    if abs(s_idx - b_idx) <= 5:
                        botanical_s.append(
                            {
                                "line": trans.get("line", "unknown"),
                                "distance": abs(s_idx - b_idx),
                                "full_sentence": sentence,
                            }
                        )
                        break

    return botanical_s


def test_deictic_cooccurrence(translations):
    """
    Test 3: THIS/THAT co-occurrence

    If [?s] = "plant/herb", should appear with THIS/THAT
    (pointing to illustrated plants)
    Pattern: "THIS [?s]" = "this plant/herb"
    """
    deictic_s = []

    for trans in translations:
        sentence = trans["final_translation"]

        if "THIS/THAT" in sentence and "[?s]" in sentence:
            words = sentence.split()
            this_indices = [i for i, w in enumerate(words) if "THIS/THAT" in w]
            s_indices = [i for i, w in enumerate(words) if "[?s]" in w]

            for t_idx in this_indices:
                for s_idx in s_indices:
                    if abs(s_idx - t_idx) <= 3:
                        before = words[max(0, s_idx - 2) : s_idx]
                        after = words[s_idx + 1 : min(len(words), s_idx + 3)]

                        deictic_s.append(
                            {
                                "line": trans.get("line", "unknown"),
                                "word": words[s_idx],
                                "distance": abs(s_idx - t_idx),
                                "before": before,
                                "after": after,
                                "full_sentence": sentence,
                            }
                        )
                        break

    return deictic_s


def test_definiteness(translations):
    """
    Test 4: Definiteness markers

    If [?s] = "plant/herb", should take DEF: [?s]-DEF = "the plant/herb"
    """
    s_def = []

    for trans in translations:
        sentence = trans["final_translation"]
        words = sentence.split()

        for i, word in enumerate(words):
            if "[?s]" in word and "-DEF" in word:
                before = words[max(0, i - 3) : i]
                after = words[i + 1 : min(len(words), i + 4)]

                s_def.append(
                    {
                        "line": trans.get("line", "unknown"),
                        "word": word,
                        "before": before,
                        "after": after,
                        "full_sentence": sentence,
                    }
                )

    return s_def


def test_preparation_context(translations):
    """
    Test 5: Preparation/process context

    If [?s] = "plant/herb", should appear with preparation verbs
    Pattern: "[?s] [?ch]-VERB" = "herb prepare"
    """
    s_with_verbs = []

    for trans in translations:
        sentence = trans["final_translation"]

        if "[?s]" in sentence:
            # Check for process verbs
            has_process = any(
                v in sentence for v in ["[?ch]-VERB", "[?sh]-VERB", "[?lch]-VERB"]
            )

            if has_process:
                s_with_verbs.append(
                    {"line": trans.get("line", "unknown"), "sentence": sentence}
                )

    return s_with_verbs


def analyze_s_contexts(translations):
    """General context analysis"""
    before_s = Counter()
    after_s = Counter()

    for trans in translations:
        sentence = trans["final_translation"]
        words = sentence.split()

        for i, word in enumerate(words):
            if "[?s]" in word:
                before = words[max(0, i - 3) : i]
                after = words[i + 1 : min(len(words), i + 4)]

                before_s.update(before)
                after_s.update(after)

    return before_s, after_s


def main():
    """Main validation"""
    print("=" * 70)
    print("VALIDATING [?s] = 'plant/herb' HYPOTHESIS")
    print("=" * 70)
    print("\nFrom Phase 20 findings:")
    print("- [?s]: 694 instances (1.9% of corpus)")
    print("- VERB suffix rate: 0.7% (extremely low - nominal)")
    print("- Co-occurs with botanical-term: 27×")
    print("- Standalone rate: 22.6%")
    print("\nHypothesis: [?s] means 'plant' or 'herb' (generic botanical term)")
    print("Compare to [?al] = 'substance' (generic), [?s] = botanical-specific\n")

    print("Loading translations...")
    translations = load_translations()
    print(f"Loaded {len(translations)} translations")

    print("Building folio mapping...")
    line_to_folio = build_folio_mapping()
    print(f"Mapped {len(line_to_folio)} lines to folios\n")

    # TEST 1: Herbal section enrichment
    print("=" * 70)
    print("TEST 1: HERBAL SECTION ENRICHMENT")
    print("=" * 70)
    print("If [?s] = 'plant/herb', should be enriched in Herbal section")
    print("(where botanical illustrations are)\n")

    section_counts, section_totals, enrichment, s_in_sections = test_herbal_enrichment(
        translations, line_to_folio
    )

    print("Section distribution:")
    for section in sorted(section_counts.keys()):
        count = section_counts[section]
        total = section_totals[section]
        pct = count / total * 100 if total > 0 else 0
        enrich = enrichment[section]

        print(
            f"  {section:15s}: {count:3d}/{total:4d} ({pct:5.2f}%) - enrichment: {enrich:.2f}×"
        )

    # Check Herbal enrichment
    herbal_enrichment = enrichment.get("herbal", 0)

    if herbal_enrichment > 1.5:
        print(
            f"\n✓ STRONG EVIDENCE: {herbal_enrichment:.2f}× enrichment in Herbal section"
        )
        print("  [?s] clusters in botanical contexts!")
    elif herbal_enrichment > 1.0:
        print(f"\n⚠ MODERATE EVIDENCE: {herbal_enrichment:.2f}× enrichment in Herbal")
    else:
        print(f"\n✗ WEAK EVIDENCE: Only {herbal_enrichment:.2f}× enrichment")

    # Show some Herbal examples
    if s_in_sections.get("herbal"):
        print("\nSample [?s] in Herbal section (first 3):")
        for i, ctx in enumerate(s_in_sections["herbal"][:3], 1):
            print(f"\n  {i}. {ctx['line']} ({ctx['folio']})")
            print(f"     {ctx['sentence'][:100]}...")

    # TEST 2: botanical-term co-occurrence
    print("\n" + "=" * 70)
    print("TEST 2: BOTANICAL-TERM CO-OCCURRENCE")
    print("=" * 70)
    print("If [?s] = 'plant/herb', should co-occur with botanical-term")
    print("Pattern: 'botanical-term [?s]' = '[named plant] herb'\n")

    botanical_s = test_botanical_cooccurrence(translations)
    print(f"Result: {len(botanical_s)} instances of botanical-term near [?s]")

    if botanical_s:
        print("\nSample contexts (first 3):")
        for i, ctx in enumerate(botanical_s[:3], 1):
            print(f"\n  {i}. {ctx['line']} (distance: {ctx['distance']} words)")
            print(f"     {ctx['full_sentence'][:100]}...")

    if len(botanical_s) > 20:
        print(f"\n✓ STRONG EVIDENCE: {len(botanical_s)} co-occurrences")
    elif len(botanical_s) > 10:
        print(f"\n⚠ MODERATE EVIDENCE: {len(botanical_s)} co-occurrences")
    else:
        print(f"\n✗ WEAK EVIDENCE: Only {len(botanical_s)} co-occurrences")

    # TEST 3: THIS/THAT deictic
    print("\n" + "=" * 70)
    print("TEST 3: THIS/THAT DEICTIC CO-OCCURRENCE")
    print("=" * 70)
    print("If [?s] = 'plant/herb', should appear with THIS/THAT")
    print("(pointing to illustrated plants)\n")

    deictic_s = test_deictic_cooccurrence(translations)
    print(f"Result: {len(deictic_s)} instances of THIS/THAT near [?s]")

    if deictic_s:
        print("\nSample contexts (first 3):")
        for i, ctx in enumerate(deictic_s[:3], 1):
            print(f"\n  {i}. {ctx['line']} (distance: {ctx['distance']} words)")
            print(
                f"     ...{' '.join(ctx['before'])} **{ctx['word']}** {' '.join(ctx['after'])}..."
            )

    if len(deictic_s) > 30:
        print(f"\n✓ STRONG EVIDENCE: {len(deictic_s)} co-occurrences")
        print("  THIS/THAT likely points to plant illustrations")
    elif len(deictic_s) > 15:
        print(f"\n⚠ MODERATE EVIDENCE: {len(deictic_s)} co-occurrences")
    else:
        print(f"\n? WEAK EVIDENCE: Only {len(deictic_s)} co-occurrences")

    # TEST 4: Definiteness
    print("\n" + "=" * 70)
    print("TEST 4: DEFINITENESS MARKERS")
    print("=" * 70)
    print("If [?s] = 'plant/herb', should take DEF: [?s]-DEF = 'the plant/herb'\n")

    s_def = test_definiteness(translations)
    print(f"Result: {len(s_def)} instances of [?s]-DEF")

    if s_def:
        print("\nSample contexts (first 3):")
        for i, ctx in enumerate(s_def[:3], 1):
            print(f"\n  {i}. {ctx['line']}")
            print(
                f"     ...{' '.join(ctx['before'])} **{ctx['word']}** {' '.join(ctx['after'])}..."
            )

    total_s = 694  # From Phase 20
    def_pct = len(s_def) / total_s * 100 if total_s > 0 else 0
    print(f"\nDefiniteness rate: {len(s_def)}/{total_s} ({def_pct:.1f}%)")

    # TEST 5: Preparation context
    print("\n" + "=" * 70)
    print("TEST 5: PREPARATION/PROCESS CONTEXT")
    print("=" * 70)
    print("If [?s] = 'plant/herb', should appear with preparation verbs\n")

    s_with_verbs = test_preparation_context(translations)
    print(f"Result: {len(s_with_verbs)} instances of [?s] with process verbs")

    verb_pct = len(s_with_verbs) / total_s * 100 if total_s > 0 else 0
    print(f"Process context rate: {len(s_with_verbs)}/{total_s} ({verb_pct:.1f}%)")

    if verb_pct > 50:
        print("\n✓ [?s] frequently appears in preparation contexts")

    # GENERAL CONTEXT
    print("\n" + "=" * 70)
    print("GENERAL CONTEXT ANALYSIS")
    print("=" * 70)

    before_s, after_s = analyze_s_contexts(translations)

    print("\nTop 10 words BEFORE [?s]:")
    for word, count in before_s.most_common(10):
        print(f"  {word}: {count}×")

    print("\nTop 10 words AFTER [?s]:")
    for word, count in after_s.most_common(10):
        print(f"  {word}: {count}×")

    # FINAL VERDICT
    print("\n" + "=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)

    evidence_count = 0

    if herbal_enrichment > 1.5:
        evidence_count += 1
        print("✓ Test 1 (Herbal enrichment): PASSED")
    elif herbal_enrichment > 1.0:
        print("⚠ Test 1 (Herbal enrichment): MARGINAL")
    else:
        print("✗ Test 1 (Herbal enrichment): FAILED")

    if len(botanical_s) > 20:
        evidence_count += 1
        print("✓ Test 2 (botanical-term): PASSED")
    elif len(botanical_s) > 10:
        print("⚠ Test 2 (botanical-term): MARGINAL")
    else:
        print("✗ Test 2 (botanical-term): FAILED")

    if len(deictic_s) > 30:
        evidence_count += 1
        print("✓ Test 3 (THIS/THAT): PASSED")
    elif len(deictic_s) > 15:
        print("⚠ Test 3 (THIS/THAT): MARGINAL")
    else:
        print("✗ Test 3 (THIS/THAT): FAILED")

    if def_pct > 10:
        evidence_count += 1
        print("✓ Test 4 (Definiteness): PASSED")
    else:
        print("✗ Test 4 (Definiteness): FAILED")

    if verb_pct > 50:
        evidence_count += 1
        print("✓ Test 5 (Process context): PASSED")
    else:
        print("✗ Test 5 (Process context): FAILED")

    print(f"\nEvidence summary: {evidence_count}/5 tests passed")

    if evidence_count >= 3:
        print("\n" + "=" * 70)
        print("✓ HYPOTHESIS CONFIRMED: [?s] = 'plant/herb'")
        print("=" * 70)
        print("Confidence: MODERATE")
        print("\nMeaning:")
        print("  [?s] = 'plant', 'herb' (generic botanical term)")
        print("  botanical-term [?s]-DEF = '[named plant] the herb'")
        print("  THIS [?s] = 'this plant/herb' (pointing to illustration)")
        print("\nCompare to:")
        print("  [?al] = 'substance' (generic)")
        print("  [?s] = 'plant/herb' (botanical-specific)")
        print("  [?r] = 'liquid' (liquid-specific)")
        print("\nMedieval parallel:")
        print("  Latin 'herba' (herb), 'planta' (plant)")
        print("  'herba rosae' = 'herb of rose' = 'rose plant'")
        print("\nImpact:")
        print("  Recognition gain: +1.9%")
        print("  Unlocks botanical terminology")
    else:
        print("\n" + "=" * 70)
        print("? HYPOTHESIS UNCERTAIN")
        print("=" * 70)
        print(f"Only {evidence_count}/5 tests passed")
        print("Alternative: [?s] might be more general term")

    # Save results
    results = {
        "hypothesis": "[?s] = plant/herb",
        "evidence_count": evidence_count,
        "herbal_enrichment": herbal_enrichment,
        "botanical_cooccurrence": len(botanical_s),
        "deictic_cooccurrence": len(deictic_s),
        "definiteness_count": len(s_def),
        "definiteness_pct": def_pct,
        "process_context_count": len(s_with_verbs),
        "process_context_pct": verb_pct,
        "section_distribution": dict(section_counts),
        "enrichment": enrichment,
        "top_before": dict(before_s.most_common(20)),
        "top_after": dict(after_s.most_common(20)),
    }

    print("\nSaving results to S_PLANT_VALIDATION.json...")
    with open("S_PLANT_VALIDATION.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\nDONE!")


if __name__ == "__main__":
    main()
