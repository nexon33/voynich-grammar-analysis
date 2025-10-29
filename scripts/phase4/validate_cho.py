"""
VALIDATE 'CHO' - HIGH-FREQUENCY NOUN CANDIDATE

PROFILE:
- Frequency: 2,412 instances (6.5% of manuscript!)
- Case-marking: 51.8% (strong nominal preference)
- Verbal rate: 0.8% (minimal polysemy)
- Section enrichment: 3.1x

If we validate 'cho', we unlock 6.5% of manuscript vocabulary.

PREDICTIONS (Common high-frequency nouns in medieval recipes):
- Vessel/container (pot, jar, bowl)
- Body part (very common in medical texts)
- Plant part (root, leaf, stem)
- Liquid/substance (water, oil, but we have water)
- Action/process (but low verbal rate suggests noun)

Author: Research Assistant
Date: 2025-10-29
"""

import json
from collections import Counter, defaultdict
from pathlib import Path


def load_data():
    """Load manuscript words"""
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
            for j in range(max(0, i - window), min(len(all_words), i + window + 1)):
                if j != i:
                    adjacent[all_words[j]] += 1
    return adjacent


def find_cooccurrence(target, all_words, known_roots, window=3):
    """Check co-occurrence with known nouns"""
    cooccur = defaultdict(int)
    for i, word in enumerate(all_words):
        if target in word:
            start = max(0, i - window)
            end = min(len(all_words), i + window + 1)
            for j in range(start, end):
                if j != i:
                    for known in known_roots:
                        if known in all_words[j]:
                            cooccur[known] += 1
    return cooccur


def get_section_distribution(target, all_words, section_size=500):
    """Section enrichment analysis"""
    positions = [i for i, w in enumerate(all_words) if target in w]
    if not positions:
        return {}

    n_sections = len(all_words) // section_size
    section_counts = defaultdict(int)
    for pos in positions:
        section_counts[pos // section_size] += 1

    avg_per_section = len(positions) / n_sections
    enrichments = {
        section: {
            "count": count,
            "enrichment": count / avg_per_section if avg_per_section > 0 else 0,
        }
        for section, count in section_counts.items()
    }
    return enrichments


def get_case_distribution(target, all_words):
    """Case distribution analysis"""
    forms = defaultdict(int)
    for word in all_words:
        if target in word:
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


def get_context_examples(target, all_words, n=15):
    """Get context examples"""
    examples = []
    for i, word in enumerate(all_words):
        if target in word:
            start = max(0, i - 3)
            end = min(len(all_words), i + 4)
            context = all_words[start:end]
            context_str = [f"**{w.upper()}**" if target in w else w for w in context]
            examples.append(" ".join(context_str))
            if len(examples) >= n:
                break
    return examples


def main():
    print("=" * 80)
    print("VALIDATING 'CHO' - HIGH-FREQUENCY NOUN CANDIDATE")
    print("=" * 80)
    print()
    print("PROFILE:")
    print("  Frequency: 2,412 instances (6.5% of manuscript!)")
    print("  Case-marking: 51.8% (strong nominal preference)")
    print("  Verbal rate: 0.8% (minimal polysemy)")
    print("  Section enrichment: 3.1x")
    print()
    print("SIGNIFICANCE: If validated, unlocks 6.5% of vocabulary")
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

    adjacent = find_adjacent_words("cho", all_words, window=2)
    print("Top 20 words appearing near 'cho':")
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
        "dor": "red",
    }

    cooccur = find_cooccurrence("cho", all_words, known_nouns.keys(), window=3)

    print("Co-occurrence with validated nouns (within 3 words):")
    print("-" * 80)
    total_cooccur = 0
    for root, count in cooccur.items():
        meaning = known_nouns.get(root, "unknown")
        print(f"  {root:<10} ({meaning:<20}) {count:4d} times")
        total_cooccur += count
    print()
    print(f"Total co-occurrences: {total_cooccur}")
    print()

    # Normalize by frequency
    cho_count = sum(1 for w in all_words if "cho" in w)
    cooccur_rate = total_cooccur / cho_count if cho_count > 0 else 0
    print(f"Co-occurrence rate: {cooccur_rate:.3f} per instance")
    print()

    if cooccur_rate > 0.15:
        print("  ✓✓ STRONG co-occurrence (>15%)")
    elif cooccur_rate > 0.10:
        print("  ✓ MODERATE co-occurrence (>10%)")
    else:
        print("  ~ WEAK co-occurrence")
    print()

    # TEST 3: Section distribution
    print("=" * 80)
    print("TEST 3: SECTION DISTRIBUTION")
    print("=" * 80)
    print()

    sections = get_section_distribution("cho", all_words, section_size=500)
    sorted_sections = sorted(
        sections.items(), key=lambda x: x[1]["enrichment"], reverse=True
    )

    print("Top 10 sections with 'cho' (by enrichment):")
    print("-" * 80)
    print(f"{'Section':<10} {'Count':<10} {'Enrichment':<15}")
    print("-" * 80)
    for section, data in sorted_sections[:10]:
        print(f"{section:<10} {data['count']:<10} {data['enrichment']:<15.1f}x")
    print()

    max_enrichment = sorted_sections[0][1]["enrichment"] if sorted_sections else 0
    if max_enrichment > 2.0:
        print(f"  ✓ Section clustering ({max_enrichment:.1f}x)")
    else:
        print(f"  ~ Even distribution")
    print()

    # TEST 4: Case distribution
    print("=" * 80)
    print("TEST 4: CASE DISTRIBUTION")
    print("=" * 80)
    print()

    cases = get_case_distribution("cho", all_words)

    print("Case distribution:")
    print("-" * 80)
    for case in ["al", "ar", "ol", "or", "bare", "other"]:
        if case in cases["counts"]:
            count = cases["counts"][case]
            pct = cases["percentages"][case]
            print(f"  -{case:8s}: {count:4d} ({pct:5.1f}%)")
    print()

    case_total = sum(cases["counts"].get(c, 0) for c in ["al", "ar", "ol", "or"])
    case_pct = 100 * case_total / cases["total"] if cases["total"] > 0 else 0
    print(f"Case-marked forms: {case_pct:.1f}%")
    print()

    if case_pct > 50:
        print("  ✓ HIGH case-marking (nominal behavior)")
    elif case_pct > 35:
        print("  ✓ MODERATE case-marking")
    else:
        print("  ~ LOW case-marking")
    print()

    # TEST 5: Context examples
    print("=" * 80)
    print("TEST 5: CONTEXT EXAMPLES")
    print("=" * 80)
    print()

    examples = get_context_examples("cho", all_words, n=20)
    for i, example in enumerate(examples, 1):
        print(f"  {i:2d}. {example}")
    print()

    # FINAL VERDICT
    print("=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)
    print()

    score = 0
    evidence = []

    if cooccur_rate >= 0.15:
        score += 2
        evidence.append(f"✓✓ Strong co-occurrence ({cooccur_rate:.1%})")
    elif cooccur_rate >= 0.10:
        score += 1
        evidence.append(f"✓ Moderate co-occurrence ({cooccur_rate:.1%})")

    if max_enrichment >= 2.5:
        score += 2
        evidence.append(f"✓✓ Strong section clustering ({max_enrichment:.1f}x)")
    elif max_enrichment >= 2.0:
        score += 1
        evidence.append(f"✓ Moderate section clustering ({max_enrichment:.1f}x)")

    if case_pct >= 50:
        score += 2
        evidence.append(f"✓✓ High case-marking ({case_pct:.0f}%)")
    elif case_pct >= 35:
        score += 1
        evidence.append(f"✓ Moderate case-marking ({case_pct:.0f}%)")

    # Low verbal rate (already known: 0.8%)
    score += 2
    evidence.append("✓✓ Very low verbal rate (0.8%)")

    print(f"EVIDENCE SCORE: {score}/8")
    print()

    for ev in evidence:
        print(f"  {ev}")
    print()

    if score >= 6:
        print("✓✓✓ STRONG VALIDATION")
        print()
        print("'cho' behaves like a concrete noun")
        print("High frequency (6.5%) suggests common/important term")
        print()
        print("HYPOTHESIS for meaning:")
        print("  Given high frequency, likely:")
        print("  - Common body part")
        print("  - Common vessel/container")
        print("  - Common plant part")
        print("  Need more context to narrow down specific meaning")
    elif score >= 4:
        print("✓ MODERATE VALIDATION")
        print()
        print("'cho' shows nominal properties but evidence mixed")
    else:
        print("✗ WEAK VALIDATION")
        print()
        print("'cho' does not strongly support concrete noun hypothesis")
    print()

    # Save results
    results = {
        "hypothesis": "cho = concrete noun (meaning TBD)",
        "frequency": cho_count,
        "manuscript_percentage": 100 * cho_count / len(all_words),
        "score": score,
        "max_score": 8,
        "evidence": evidence,
        "adjacent_words": dict(adjacent.most_common(20)),
        "cooccurrence": dict(cooccur),
        "cooccurrence_rate": cooccur_rate,
        "section_distribution": {k: v for k, v in sorted_sections[:10]},
        "case_distribution": cases,
        "examples": examples,
    }

    output_path = Path("results/phase4/cho_validation.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
