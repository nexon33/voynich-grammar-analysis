"""
FIND UNAMBIGUOUS CONCRETE NOUNS

KEY INSIGHT: The language has derivational morphology.
- Same root can be nominal (+ case) or verbal (+ -edy)
- "shee/she" is polysemous: nominal "water" OR verbal "to wet/soak"

NEW STRATEGY: Find roots with STRONG NOMINAL PREFERENCE
- High case-marking rate (>30%) = primarily used as nouns
- Low verbal rate (<15%) = not polysemous verbs
- These are unambiguous noun anchors

PRIORITY TARGETS:
1. Vessel/container (pharmaceutical sections)
2. Body parts (bath/biological sections)
3. Plant parts (herbal sections)
4. Tools/instruments

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


def extract_root_from_word(word):
    """Extract likely root from word by stripping known affixes

    This is heuristic - we strip suffixes iteratively
    """
    root = word

    # Strip case markers
    for case in ["al", "ar", "ol", "or"]:
        if root.endswith(case) and len(root) > len(case) + 1:
            root = root[:-2]
            break

    # Strip verbal marker
    if root.endswith("edy") and len(root) > 4:
        root = root[:-3]

    # Strip genitive prefix
    if root.startswith("qok") and len(root) > 4:
        root = root[3:]

    # Additional common suffixes
    for suffix in ["ain", "iin", "aiin", "chy", "thy", "khy"]:
        if root.endswith(suffix) and len(root) > len(suffix) + 1:
            root = root[: -len(suffix)]
            break

    return root


def analyze_root_morphology(root, all_words):
    """Analyze how a root is used morphologically

    Returns:
    - case_rate: % of instances with case marking
    - verbal_rate: % of instances with -edy
    - bare_rate: % of instances without affixes
    - total_instances: total count
    """

    instances = [w for w in all_words if root in w]

    if not instances:
        return None

    total = len(instances)

    # Count different forms
    with_case = 0
    with_verbal = 0
    bare = 0

    for word in instances:
        # Check for case
        if any(word.endswith(case) for case in ["al", "ar", "ol", "or"]):
            with_case += 1
        # Check for verbal
        elif "edy" in word:
            with_verbal += 1
        # Bare root
        elif word == root:
            bare += 1

    return {
        "root": root,
        "total_instances": total,
        "with_case": with_case,
        "with_verbal": with_verbal,
        "bare": bare,
        "case_rate": with_case / total,
        "verbal_rate": with_verbal / total,
        "bare_rate": bare / total,
        "other_rate": (total - with_case - with_verbal - bare) / total,
    }


def calculate_section_enrichment(root, all_words, section_size=500):
    """Calculate enrichment in different sections

    We'll approximate sections by position in manuscript
    """
    # Find positions where root appears
    positions = []
    for i, word in enumerate(all_words):
        if root in word:
            positions.append(i)

    if not positions:
        return {}

    # Divide manuscript into sections
    total_words = len(all_words)
    n_sections = total_words // section_size

    # Count instances per section
    section_counts = defaultdict(int)
    for pos in positions:
        section = pos // section_size
        section_counts[section] += 1

    # Find max enrichment
    if section_counts:
        max_section = max(section_counts.items(), key=lambda x: x[1])
        avg_per_section = len(positions) / n_sections
        max_enrichment = max_section[1] / avg_per_section if avg_per_section > 0 else 0

        return {
            "max_enrichment": max_enrichment,
            "max_section": max_section[0],
            "max_count": max_section[1],
        }

    return {}


def find_nominal_candidates(all_words, min_frequency=50):
    """Find roots with strong nominal preference

    Criteria:
    - High case rate (>30%)
    - Low verbal rate (<15%)
    - Sufficient frequency (>50 instances)
    """

    print("=" * 80)
    print("FINDING UNAMBIGUOUS NOMINAL ROOTS")
    print("=" * 80)
    print()
    print("CRITERIA:")
    print("  - Case-marking rate > 30% (primarily nominal)")
    print("  - Verbal rate < 15% (not polysemous verb)")
    print("  - Frequency > 50 instances (statistically reliable)")
    print()

    # Extract unique roots
    print("Extracting roots from manuscript...")
    root_counter = Counter()
    for word in all_words:
        root = extract_root_from_word(word)
        if len(root) >= 2:  # Minimum length
            root_counter[root] += 1

    print(f"Found {len(root_counter)} unique roots")
    print()

    # Analyze each frequent root
    print("Analyzing morphological patterns...")
    candidates = []

    for root, freq in root_counter.most_common(200):  # Top 200 roots
        if freq < min_frequency:
            continue

        analysis = analyze_root_morphology(root, all_words)

        if analysis is None:
            continue

        # Apply criteria
        if analysis["case_rate"] > 0.30 and analysis["verbal_rate"] < 0.15:
            # Calculate section enrichment
            enrichment = calculate_section_enrichment(root, all_words)

            candidates.append({**analysis, **enrichment})

    print(f"Found {len(candidates)} nominal candidates")
    print()

    return candidates


def main():
    print("=" * 80)
    print("SEARCH FOR UNAMBIGUOUS CONCRETE NOUNS")
    print("=" * 80)
    print()
    print("GOAL: Find 5-10 unambiguous nouns to use as translation anchors")
    print()
    print("KEY INSIGHT: Language has derivational morphology")
    print("  - 'shee/she' is polysemous: nominal (water) AND verbal (to wet)")
    print("  - Need roots with STRONG nominal preference")
    print("  - High case-marking rate = reliable noun")
    print()

    # Load data
    all_words = load_data()
    print(f"Loaded {len(all_words)} words from manuscript")
    print()

    # Find candidates
    candidates = find_nominal_candidates(all_words)

    # Sort by case rate (most nominal first)
    candidates.sort(key=lambda x: x["case_rate"], reverse=True)

    # Display results
    print("=" * 80)
    print("TOP 20 UNAMBIGUOUS NOMINAL CANDIDATES")
    print("=" * 80)
    print()
    print(
        f"{'Root':<12} {'Freq':<8} {'Case%':<8} {'Verb%':<8} {'Bare%':<8} {'Enrich':<8} {'Section':<8}"
    )
    print("-" * 80)

    for i, cand in enumerate(candidates[:20], 1):
        enrich = cand.get("max_enrichment", 0)
        section = cand.get("max_section", 0)

        print(
            f"{cand['root']:<12} {cand['total_instances']:<8} "
            f"{100 * cand['case_rate']:<8.1f} {100 * cand['verbal_rate']:<8.1f} "
            f"{100 * cand['bare_rate']:<8.1f} {enrich:<8.1f}x {section:<8}"
        )

    print()

    # Analyze top candidates in detail
    print("=" * 80)
    print("DETAILED ANALYSIS: TOP 5 CANDIDATES")
    print("=" * 80)
    print()

    for i, cand in enumerate(candidates[:5], 1):
        print(f"CANDIDATE {i}: '{cand['root']}'")
        print("-" * 80)
        print(f"  Total instances: {cand['total_instances']}")
        print(f"  Case-marked: {cand['with_case']} ({100 * cand['case_rate']:.1f}%)")
        print(
            f"  Verbal forms: {cand['with_verbal']} ({100 * cand['verbal_rate']:.1f}%)"
        )
        print(f"  Bare forms: {cand['bare']} ({100 * cand['bare_rate']:.1f}%)")
        print(f"  Other forms: {100 * cand['other_rate']:.1f}%")

        if "max_enrichment" in cand:
            print(
                f"  Max enrichment: {cand['max_enrichment']:.1f}x in section {cand['max_section']}"
            )

        print()

        # Interpretation
        print(f"  INTERPRETATION:")
        if cand["case_rate"] > 0.50:
            print(f"    ✓✓ VERY STRONG nominal preference")
        elif cand["case_rate"] > 0.35:
            print(f"    ✓ Strong nominal preference")
        else:
            print(f"    ~ Moderate nominal preference")

        if cand["verbal_rate"] < 0.05:
            print(f"    ✓✓ NO verbal use (unambiguous noun)")
        elif cand["verbal_rate"] < 0.10:
            print(f"    ✓ Minimal verbal use")
        else:
            print(f"    ~ Some verbal use ({100 * cand['verbal_rate']:.0f}%)")

        if "max_enrichment" in cand and cand["max_enrichment"] > 2.0:
            print(f"    ✓ Section-specific ({cand['max_enrichment']:.1f}x enriched)")

        # Compare to known words
        if cand["root"] in ["ok", "ot", "shee", "she"]:
            print(f"    ⚠ Already validated")

        print()
        print(f"  HYPOTHESIS:")

        # Try to guess semantic category
        if "max_enrichment" in cand and cand["max_enrichment"] > 3.0:
            if cand["case_rate"] > 0.40:
                print(f"    → Likely concrete noun (vessel, body part, or plant part)")
                print(f"    → High case-marking suggests locational use")
            else:
                print(f"    → Section-specific term")
        else:
            print(f"    → Common noun (used across manuscript)")

        print()

    # Summary recommendation
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()

    # Filter top candidates by novelty (not already known)
    known_roots = ["ok", "ot", "shee", "she", "daiin", "aiin", "saiin", "oiin"]
    novel_candidates = [c for c in candidates[:20] if c["root"] not in known_roots]

    print(f"Novel unambiguous noun candidates: {len(novel_candidates)}")
    print()

    if len(novel_candidates) >= 5:
        print("✓✓ SUFFICIENT CANDIDATES for validation")
        print()
        print("NEXT STEPS:")
        print("  1. Validate top 3-5 candidates using oak/oat methods:")
        print("     - Co-occurrence analysis")
        print("     - Context examination")
        print("     - Illustration correlation (if applicable)")
        print()
        print("  2. Once validated, re-attempt translation with expanded vocabulary")
        print()
        print("  3. Target: 8-10 unambiguous concrete nouns for reliable translation")
    else:
        print("⚠ LIMITED CANDIDATES")
        print()
        print("May need to:")
        print("  - Relax criteria slightly")
        print("  - Look for compound words")
        print("  - Consider roots with moderate nominal preference")
    print()

    # Save results
    output_path = Path("results/phase4/unambiguous_noun_candidates.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(candidates[:20], f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
