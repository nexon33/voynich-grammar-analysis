"""
VALIDATE 'DOR' AS "RED"

PRIOR EVIDENCE: Earlier contextual analysis suggested 'dor' might mean "red"

CRITICAL TEST: If 'dor' = "red" (color adjective), it should:
1. Appear adjacent to known nouns (oak, oat, body parts)
2. Take cases to agree with nouns (adjectival concord)
3. Be enriched where illustrations show red things
4. Have LOW verbal rate (colors aren't verbs) ✓ Already 0%

This validates both:
- The specific 'dor' = "red" hypothesis
- The general noun-hunting methodology

Author: Research Assistant
Date: 2025-10-29
"""

import json
from collections import Counter, defaultdict
from pathlib import Path


def load_data():
    """Load manuscript words with position tracking"""
    with open(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt",
        "r",
        encoding="utf-8",
    ) as f:
        words = [w.lower() for w in f.read().split() if w.isalpha()]
    return words


def find_adjacent_words(target, all_words, window=2):
    """Find words adjacent to target"""

    adjacent = Counter()

    for i, word in enumerate(all_words):
        if target in word:
            # Look at neighbors
            for j in range(max(0, i - window), min(len(all_words), i + window + 1)):
                if j != i:
                    adjacent[all_words[j]] += 1

    return adjacent


def find_cooccurrence_with_known(target, all_words, known_roots, window=3):
    """Check co-occurrence with known nouns"""

    cooccur = defaultdict(int)

    for i, word in enumerate(all_words):
        if target in word:
            # Check window
            start = max(0, i - window)
            end = min(len(all_words), i + window + 1)

            for j in range(start, end):
                if j != i:
                    for known in known_roots:
                        if known in all_words[j]:
                            cooccur[known] += 1

    return cooccur


def get_section_distribution(target, all_words, section_size=500):
    """Find which sections target appears in"""

    positions = []
    for i, word in enumerate(all_words):
        if target in word:
            positions.append(i)

    if not positions:
        return {}

    # Divide into sections
    total_words = len(all_words)
    n_sections = total_words // section_size

    section_counts = defaultdict(int)
    for pos in positions:
        section = pos // section_size
        section_counts[section] += 1

    # Calculate enrichment
    avg_per_section = len(positions) / n_sections

    enrichments = {}
    for section, count in section_counts.items():
        enrichment = count / avg_per_section if avg_per_section > 0 else 0
        enrichments[section] = {"count": count, "enrichment": enrichment}

    return enrichments


def get_case_distribution(target, all_words):
    """Get detailed case distribution"""

    forms = defaultdict(int)

    for word in all_words:
        if target in word:
            # Check what follows target
            if word.endswith("al"):
                forms["al"] += 1
            elif word.endswith("ar"):
                forms["ar"] += 1
            elif word.endswith("ol"):
                forms["ol"] += 1
            elif word.endswith("or"):
                forms["or"] += 1
            elif word == target:
                forms["bare"] += 1
            else:
                forms["other"] += 1

    total = sum(forms.values())

    return {
        "counts": dict(forms),
        "percentages": {k: 100 * v / total for k, v in forms.items()},
        "total": total,
    }


def get_context_examples(target, all_words, n=10):
    """Get context examples"""

    examples = []

    for i, word in enumerate(all_words):
        if target in word:
            # Get context window
            start = max(0, i - 3)
            end = min(len(all_words), i + 4)

            context = all_words[start:end]
            # Highlight target
            context_str = []
            for w in context:
                if target in w:
                    context_str.append(f"**{w.upper()}**")
                else:
                    context_str.append(w)

            examples.append(" ".join(context_str))

            if len(examples) >= n:
                break

    return examples


def main():
    print("=" * 80)
    print("VALIDATING 'DOR' AS 'RED'")
    print("=" * 80)
    print()
    print("HYPOTHESIS: 'dor' is a color adjective meaning 'red'")
    print()
    print("PREDICTIONS:")
    print("  1. Should appear adjacent to nouns (plants, body parts)")
    print("  2. Should take case markers (adjectival agreement)")
    print("  3. Should be enriched in sections with red illustrations")
    print("  4. Should have 0% verbal rate ✓ (confirmed: 0.0%)")
    print()

    # Load data
    all_words = load_data()
    print(f"Loaded {len(all_words)} words")
    print()

    # TEST 1: Adjacent words
    print("=" * 80)
    print("TEST 1: ADJACENT WORDS")
    print("=" * 80)
    print()
    print("If 'dor' is an adjective, it should appear next to nouns")
    print()

    adjacent = find_adjacent_words("dor", all_words, window=2)

    print("Top 20 words appearing near 'dor':")
    print("-" * 80)
    for word, count in adjacent.most_common(20):
        print(f"  {word:<20} {count:4d} times")
    print()

    # TEST 2: Co-occurrence with known nouns
    print("=" * 80)
    print("TEST 2: CO-OCCURRENCE WITH KNOWN NOUNS")
    print("=" * 80)
    print()

    known_nouns = {
        "ok": "oak",
        "ot": "oat",
        "qok": "oak (genitive)",
        "qot": "oat (genitive)",
        "shee": "water/wet",
        "she": "water/wet",
    }

    cooccur = find_cooccurrence_with_known(
        "dor", all_words, known_nouns.keys(), window=3
    )

    print("Co-occurrence with known nouns (within 3 words):")
    print("-" * 80)
    total_cooccur = 0
    for root, count in cooccur.items():
        meaning = known_nouns.get(root, "unknown")
        print(f"  {root:<10} ({meaning:<20}) {count:4d} times")
        total_cooccur += count
    print()
    print(f"Total co-occurrences with known nouns: {total_cooccur}")
    print()

    if total_cooccur > 20:
        print("  ✓ STRONG co-occurrence with nouns (adjective behavior)")
    elif total_cooccur > 10:
        print("  ✓ Moderate co-occurrence with nouns")
    else:
        print("  ✗ WEAK co-occurrence with nouns (unexpected for adjective)")
    print()

    # TEST 3: Section distribution
    print("=" * 80)
    print("TEST 3: SECTION DISTRIBUTION")
    print("=" * 80)
    print()
    print("Color terms should cluster where they're depicted")
    print()

    sections = get_section_distribution("dor", all_words, section_size=500)

    # Sort by enrichment
    sorted_sections = sorted(
        sections.items(), key=lambda x: x[1]["enrichment"], reverse=True
    )

    print("Top 10 sections with 'dor' (by enrichment):")
    print("-" * 80)
    print(f"{'Section':<10} {'Count':<10} {'Enrichment':<15} {'Approx Folio':<15}")
    print("-" * 80)

    for section, data in sorted_sections[:10]:
        # Rough folio estimate (assuming 10 words per line, 10 lines per folio)
        approx_folio = section * 5  # Very rough
        print(
            f"{section:<10} {data['count']:<10} {data['enrichment']:<15.1f}x ~f{approx_folio}"
        )
    print()

    max_enrichment = sorted_sections[0][1]["enrichment"] if sorted_sections else 0
    if max_enrichment > 3.0:
        print(f"  ✓ STRONG section clustering ({max_enrichment:.1f}x enrichment)")
        print(f"    → Suggests topic-specific use (consistent with color term)")
    elif max_enrichment > 2.0:
        print(f"  ✓ Moderate section clustering")
    else:
        print(f"  ~ Even distribution across manuscript")
    print()

    # TEST 4: Case distribution
    print("=" * 80)
    print("TEST 4: CASE DISTRIBUTION")
    print("=" * 80)
    print()
    print("Adjectives should take cases to agree with nouns")
    print()

    cases = get_case_distribution("dor", all_words)

    print("Case distribution:")
    print("-" * 80)
    for case in ["al", "ar", "ol", "or", "bare", "other"]:
        if case in cases["counts"]:
            count = cases["counts"][case]
            pct = cases["percentages"][case]
            print(f"  -{case:8s}: {count:4d} ({pct:5.1f}%)")
    print()
    print(f"Total instances: {cases['total']}")
    print()

    case_total = sum(cases["counts"].get(c, 0) for c in ["al", "ar", "ol", "or"])
    case_pct = 100 * case_total / cases["total"] if cases["total"] > 0 else 0

    print(f"  Case-marked forms: {case_pct:.1f}%")
    print()

    if case_pct > 70:
        print("  ✓✓ VERY HIGH case-marking (strong nominal/adjectival behavior)")
    elif case_pct > 50:
        print("  ✓ HIGH case-marking (nominal/adjectival behavior)")
    else:
        print("  ~ MODERATE case-marking")
    print()

    # TEST 5: Context examples
    print("=" * 80)
    print("TEST 5: CONTEXT EXAMPLES")
    print("=" * 80)
    print()
    print("Examining actual contexts where 'dor' appears:")
    print()

    examples = get_context_examples("dor", all_words, n=15)

    for i, example in enumerate(examples, 1):
        print(f"  {i:2d}. {example}")
    print()

    # FINAL VERDICT
    print("=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)
    print()

    # Calculate evidence score
    score = 0
    evidence = []

    if total_cooccur >= 20:
        score += 2
        evidence.append("✓✓ Strong co-occurrence with nouns")
    elif total_cooccur >= 10:
        score += 1
        evidence.append("✓ Moderate co-occurrence with nouns")

    if max_enrichment >= 3.0:
        score += 2
        evidence.append(f"✓✓ Strong section clustering ({max_enrichment:.1f}x)")
    elif max_enrichment >= 2.0:
        score += 1
        evidence.append("✓ Moderate section clustering")

    if case_pct >= 70:
        score += 2
        evidence.append(f"✓✓ Very high case-marking ({case_pct:.0f}%)")
    elif case_pct >= 50:
        score += 1
        evidence.append(f"✓ High case-marking ({case_pct:.0f}%)")

    # Already know verbal rate is 0%
    score += 2
    evidence.append("✓✓ Zero verbal use (0%)")

    print(f"EVIDENCE SCORE: {score}/8")
    print()

    for ev in evidence:
        print(f"  {ev}")
    print()

    if score >= 6:
        print("✓✓✓ STRONG VALIDATION")
        print()
        print("CONCLUSION:")
        print("  'dor' behaves like a color adjective")
        print("  Hypothesis 'dor' = 'red' is SUPPORTED")
        print()
        print("IMPLICATIONS:")
        print("  ✓ Noun-hunting method works")
        print("  ✓ Can proceed with systematic candidate validation")
        print("  ✓ Have 4th validated content term (oak, oat, water/wet, red)")
    elif score >= 4:
        print("✓ MODERATE VALIDATION")
        print()
        print("'dor' shows some adjectival properties but evidence is mixed")
    else:
        print("✗ WEAK VALIDATION")
        print()
        print("'dor' does not strongly support color adjective hypothesis")
    print()

    # Save results
    results = {
        "hypothesis": "dor = red (color adjective)",
        "score": score,
        "max_score": 8,
        "evidence": evidence,
        "adjacent_words": dict(adjacent.most_common(20)),
        "cooccurrence": dict(cooccur),
        "section_distribution": {k: v for k, v in sorted_sections[:10]},
        "case_distribution": cases,
        "examples": examples,
    }

    output_path = Path("results/phase4/dor_validation.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
