"""
POSITIONAL TESTS FOR CAPTION HYPOTHESIS

Testing three predictions:
1. Enriched words (ory, oly, sheey) cluster at LINE-INITIAL positions (caption/deictic)
2. Ubiquitous words (oak, oat) distributed evenly (content)
3. Lines show vocabulary stratification: caption words early, content words later

Author: Research Assistant
Date: 2025-10-29
"""

import json
from collections import Counter, defaultdict
from pathlib import Path


def load_f84v_lines():
    """Load f84v text as lines (preserving line structure)"""
    with open(
        "results/phase4/readable_passages/f84v_oak_oat_bath_folio.txt",
        "r",
        encoding="utf-8",
    ) as f:
        lines = []
        for line in f:
            line = line.strip()
            if line.startswith("Voynich:"):
                text = line.replace("Voynich:", "").strip()
                words = [w.lower() for w in text.split()]
                if words:
                    lines.append(words)
        return lines


def test_positional_distribution(lines, target_word, word_display_name):
    """Test where a word appears within lines

    If caption/deictic: should cluster at positions 1-2 (line-initial)
    If content: should be evenly distributed
    """
    print(f"\nPOSITIONAL ANALYSIS: {word_display_name.upper()}")
    print("-" * 80)

    position_counts = defaultdict(int)
    total_instances = 0

    for line in lines:
        for pos, word in enumerate(line, 1):  # 1-indexed positions
            if target_word in word:
                position_counts[pos] += 1
                total_instances += 1

    if total_instances == 0:
        print(f"  No instances of '{target_word}' found")
        return None

    # Show distribution
    print(f"  Total instances: {total_instances}")
    print()
    print(f"  Position distribution:")

    # Group into position bands
    early_positions = sum(position_counts[p] for p in [1, 2])
    middle_positions = sum(position_counts[p] for p in [3, 4, 5, 6, 7, 8])
    late_positions = sum(position_counts[p] for p in [9, 10])

    early_pct = 100 * early_positions / total_instances
    middle_pct = 100 * middle_positions / total_instances
    late_pct = 100 * late_positions / total_instances

    print(f"    Positions 1-2 (LINE-INITIAL): {early_positions:3d} ({early_pct:5.1f}%)")
    print(
        f"    Positions 3-8 (MIDDLE):       {middle_positions:3d} ({middle_pct:5.1f}%)"
    )
    print(f"    Positions 9-10 (LINE-FINAL):  {late_positions:3d} ({late_pct:5.1f}%)")
    print()

    # Detailed position breakdown
    print(f"  Detailed breakdown:")
    for pos in sorted(position_counts.keys()):
        count = position_counts[pos]
        pct = 100 * count / total_instances
        bar = "█" * int(pct / 2)  # Visual bar
        print(f"    Position {pos:2d}: {count:3d} ({pct:5.1f}%) {bar}")
    print()

    # VERDICT
    print(f"  INTERPRETATION:")
    if early_pct >= 60:
        print(f"    ✓✓✓ STRONG CAPTION/DEICTIC pattern")
        print(f"        → {early_pct:.1f}% line-initial (caption position)")
        print(f"        → Likely pointing word: 'this', 'shown', 'here'")
        verdict = "DEICTIC"
    elif early_pct >= 40:
        print(f"    ✓✓ MODERATE CAPTION pattern")
        print(f"        → {early_pct:.1f}% line-initial")
        print(f"        → Possible caption/structural word")
        verdict = "POSSIBLE_DEICTIC"
    elif abs(early_pct - 20) < 10:  # Expected for random is 20% (2/10 positions)
        print(f"    ~ EVEN DISTRIBUTION")
        print(f"        → {early_pct:.1f}% line-initial (near 20% baseline)")
        print(f"        → Content word, not positionally constrained")
        verdict = "CONTENT"
    else:
        print(f"    ? UNCLEAR PATTERN")
        print(f"        → {early_pct:.1f}% line-initial")
        verdict = "UNCLEAR"
    print()

    return {
        "word": target_word,
        "display_name": word_display_name,
        "total_instances": total_instances,
        "early_pct": early_pct,
        "middle_pct": middle_pct,
        "late_pct": late_pct,
        "verdict": verdict,
        "position_distribution": dict(position_counts),
    }


def test_all_enriched_words(lines):
    """Test all highly enriched words from previous analysis"""
    print("=" * 80)
    print("TEST 1: POSITIONAL DISTRIBUTION OF ENRICHED VOCABULARY")
    print("=" * 80)
    print()
    print(
        "HYPOTHESIS: Enriched words cluster at line-initial positions (caption/deictic)"
    )
    print("BASELINE: Random distribution = 20% in positions 1-2")
    print()

    # Top enriched words from previous analysis
    enriched_words = [
        ("ory", "ory", 15.8),
        ("oly", "oly", 8.4),
        ("qoteedy", "qoteedy", 4.5),
        ("sheey", "sheey", 4.3),
        ("opchedy", "opchedy", 4.2),
        ("sheedy", "sheedy", 4.0),
        ("qol", "qol", 3.6),
        ("oteedy", "oteedy", 3.5),
        ("sheol", "sheol", 3.0),
        ("ol", "ol", 3.0),
    ]

    results = []
    for word, display, enrichment in enriched_words:
        result = test_positional_distribution(
            lines, word, f"{display} ({enrichment:.1f}x enriched)"
        )
        if result:
            results.append(result)

    # Summary
    print("=" * 80)
    print("SUMMARY: ENRICHED WORD POSITIONING")
    print("=" * 80)
    print()
    print(f"{'Word':<15} {'Enrichment':<12} {'Line-Initial %':<16} {'Verdict':<20}")
    print("-" * 80)

    for (word, display, enrichment), result in zip(enriched_words, results):
        if result:
            print(
                f"{display:<15} {enrichment:<12.1f}x {result['early_pct']:<16.1f} {result['verdict']:<20}"
            )

    print()

    # Count deictic words
    deictic_count = sum(
        1 for r in results if r and r["verdict"] in ["DEICTIC", "POSSIBLE_DEICTIC"]
    )
    print(f"Words with caption/deictic positioning: {deictic_count}/{len(results)}")
    print()

    if deictic_count >= 5:
        print("✓✓✓ STRONG SUPPORT for caption hypothesis")
        print("    → Multiple enriched words cluster line-initially")
        print("    → Suggests caption/deictic vocabulary stratum")
    elif deictic_count >= 3:
        print("✓✓ MODERATE SUPPORT for caption hypothesis")
        print("    → Some enriched words show caption positioning")
    else:
        print("✗ WEAK SUPPORT for caption hypothesis")
        print("    → Enriched words not positionally constrained")
    print()

    return results


def test_content_word_distribution(lines):
    """Test ubiquitous words (oak/oat) for comparison

    Should be evenly distributed if content words
    """
    print("=" * 80)
    print("TEST 2: POSITIONAL DISTRIBUTION OF CONTENT VOCABULARY")
    print("=" * 80)
    print()
    print("HYPOTHESIS: Content words (oak/oat) evenly distributed")
    print("BASELINE: Should be ~20% line-initial (random)")
    print()

    content_words = [
        ("qok", "oak (qok)", 1.02),
        ("qot", "oat (qot)", 0.96),
        ("chedy", "chedy (verb)", 1.36),
        ("shedy", "shedy (verb)", 1.11),
    ]

    results = []
    for word, display, enrichment in content_words:
        result = test_positional_distribution(
            lines, word, f"{display} ({enrichment:.2f}x)"
        )
        if result:
            results.append(result)

    # Summary
    print("=" * 80)
    print("SUMMARY: CONTENT WORD POSITIONING")
    print("=" * 80)
    print()
    print(f"{'Word':<20} {'Enrichment':<12} {'Line-Initial %':<16} {'Verdict':<20}")
    print("-" * 80)

    for (word, display, enrichment), result in zip(content_words, results):
        if result:
            print(
                f"{display:<20} {enrichment:<12.2f}x {result['early_pct']:<16.1f} {result['verdict']:<20}"
            )

    print()

    return results


def test_line_stratification(lines):
    """Test if lines have vocabulary stratification: caption early, content later

    Prediction: enriched words cluster in first half, ubiquitous words in second half
    """
    print("=" * 80)
    print("TEST 3: WITHIN-LINE VOCABULARY STRATIFICATION")
    print("=" * 80)
    print()
    print("HYPOTHESIS: Lines have caption+content structure")
    print("  First half (words 1-5): enriched vocabulary (caption)")
    print("  Second half (words 6-10): ubiquitous vocabulary (content)")
    print()

    enriched_words = [
        "ory",
        "oly",
        "qoteedy",
        "sheey",
        "opchedy",
        "sheedy",
        "qol",
        "oteedy",
        "sheol",
    ]
    content_words = ["qok", "qot", "ok", "ot"]

    first_half_enriched = 0
    first_half_content = 0
    second_half_enriched = 0
    second_half_content = 0

    for line in lines:
        first_half = line[:5] if len(line) >= 5 else line
        second_half = line[5:] if len(line) > 5 else []

        # Count enriched words
        for word in first_half:
            if any(e in word for e in enriched_words):
                first_half_enriched += 1
            if any(c in word for c in content_words):
                first_half_content += 1

        for word in second_half:
            if any(e in word for e in enriched_words):
                second_half_enriched += 1
            if any(c in word for c in content_words):
                second_half_content += 1

    # Calculate ratios
    total_enriched = first_half_enriched + second_half_enriched
    total_content = first_half_content + second_half_content

    if total_enriched > 0:
        enriched_first_pct = 100 * first_half_enriched / total_enriched
        enriched_second_pct = 100 * second_half_enriched / total_enriched
    else:
        enriched_first_pct = enriched_second_pct = 0

    if total_content > 0:
        content_first_pct = 100 * first_half_content / total_content
        content_second_pct = 100 * second_half_content / total_content
    else:
        content_first_pct = content_second_pct = 0

    print(f"ENRICHED VOCABULARY DISTRIBUTION:")
    print(
        f"  First half (words 1-5):  {first_half_enriched:3d} ({enriched_first_pct:5.1f}%)"
    )
    print(
        f"  Second half (words 6-10): {second_half_enriched:3d} ({enriched_second_pct:5.1f}%)"
    )
    print()

    print(f"CONTENT VOCABULARY DISTRIBUTION:")
    print(
        f"  First half (words 1-5):  {first_half_content:3d} ({content_first_pct:5.1f}%)"
    )
    print(
        f"  Second half (words 6-10): {second_half_content:3d} ({content_second_pct:5.1f}%)"
    )
    print()

    # VERDICT
    print(f"INTERPRETATION:")
    print()

    # Check if stratification exists
    stratification_score = (enriched_first_pct - 50) - (content_first_pct - 50)

    print(f"  Stratification score: {stratification_score:.1f}")
    print(f"    (positive = enriched words front-loaded, content words back-loaded)")
    print()

    if stratification_score > 10:
        print("  ✓✓ MODERATE STRATIFICATION detected")
        print("      → Enriched words cluster in first half")
        print("      → Content words cluster in second half")
        print("      → Supports caption+content hybrid structure")
        verdict = "STRATIFIED"
    elif stratification_score < -10:
        print("  ✗ REVERSE STRATIFICATION")
        print("      → Pattern opposite to prediction")
        verdict = "REVERSE"
    else:
        print("  ~ NO CLEAR STRATIFICATION")
        print("      → Both vocabulary types evenly distributed")
        print("      → Does not support hybrid structure")
        verdict = "MIXED"
    print()

    return {
        "enriched_first_pct": enriched_first_pct,
        "enriched_second_pct": enriched_second_pct,
        "content_first_pct": content_first_pct,
        "content_second_pct": content_second_pct,
        "stratification_score": stratification_score,
        "verdict": verdict,
    }


def main():
    print("=" * 80)
    print("POSITIONAL TESTS FOR CAPTION HYPOTHESIS")
    print("=" * 80)
    print()

    # Load f84v lines
    lines = load_f84v_lines()
    print(f"Loaded {len(lines)} lines from f84v (bath section)")
    print(f"Average words per line: {sum(len(l) for l in lines) / len(lines):.1f}")
    print()

    # Test 1: Enriched words positioning
    enriched_results = test_all_enriched_words(lines)

    # Test 2: Content words positioning
    content_results = test_content_word_distribution(lines)

    # Test 3: Line stratification
    stratification_results = test_line_stratification(lines)

    # Final synthesis
    print()
    print("=" * 80)
    print("FINAL SYNTHESIS: CAPTION HYPOTHESIS")
    print("=" * 80)
    print()

    # Count evidence
    deictic_words = sum(
        1 for r in enriched_results if r["verdict"] in ["DEICTIC", "POSSIBLE_DEICTIC"]
    )
    content_words_distributed = sum(
        1 for r in content_results if r["verdict"] == "CONTENT"
    )
    stratified = stratification_results["verdict"] == "STRATIFIED"

    print(f"Evidence summary:")
    print(
        f"  Enriched words with caption positioning: {deictic_words}/{len(enriched_results)}"
    )
    print(
        f"  Content words evenly distributed: {content_words_distributed}/{len(content_results)}"
    )
    print(f"  Within-line stratification: {stratification_results['verdict']}")
    print()

    # Calculate overall support
    if deictic_words >= 5 and content_words_distributed >= 2:
        print("✓✓✓ VERY STRONG SUPPORT for hybrid caption+content hypothesis")
        print()
        print("CONCLUSION:")
        print("  Lines have two vocabulary strata:")
        print("  1. CAPTION STRATUM: enriched, positionally-constrained, deictic")
        print("  2. CONTENT STRATUM: ubiquitous, evenly-distributed, substantive")
        print()
        print("  This matches medieval herbal structure:")
        print("  - Brief caption identifying illustration")
        print("  - Continuous prose explaining properties/uses")
    elif deictic_words >= 3:
        print("✓✓ MODERATE SUPPORT for hybrid hypothesis")
        print()
        print("Evidence suggests some caption-like vocabulary")
    else:
        print("✗ WEAK SUPPORT for caption hypothesis")
        print()
        print("Vocabulary appears uniformly distributed")
    print()

    # Save results
    results = {
        "enriched_words": enriched_results,
        "content_words": content_results,
        "stratification": stratification_results,
        "summary": {
            "deictic_count": deictic_words,
            "content_distributed": content_words_distributed,
            "stratified": stratified,
        },
    }

    output_path = Path("results/phase4/positional_analysis.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
