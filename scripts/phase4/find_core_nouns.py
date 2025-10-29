"""
FIND CORE NOUNS FOR VERB DISAMBIGUATION

We need 15-20 validated nouns to distinguish verb meanings through co-occurrence.

Priority targets:
1. WATER/LIQUID - must be highly enriched in bath sections
2. VESSEL/CONTAINER - must be enriched in pharmaceutical sections
3. HEAT/FIRE - must co-occur with cooking contexts

Strategy: Use same validation methods that worked for oak/oat:
- Statistical enrichment in relevant sections
- Bound/free ratio (>95% take case marking)
- Co-occurrence with validated words
- Case distribution analysis

Author: Research Assistant
Date: 2025-10-29
"""

import json
from collections import Counter, defaultdict
from pathlib import Path


def load_f84v_words():
    """Load f84v (bath section) words"""
    with open(
        "results/phase4/readable_passages/f84v_oak_oat_bath_folio.txt",
        "r",
        encoding="utf-8",
    ) as f:
        words = []
        for line in f:
            line = line.strip()
            if line.startswith("Voynich:"):
                text = line.replace("Voynich:", "").strip()
                words.extend([w.lower() for w in text.split()])
        return words


def load_full_manuscript():
    """Load full manuscript words"""
    with open(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt",
        "r",
        encoding="utf-8",
    ) as f:
        words = [w.lower() for w in f.read().split() if w.isalpha()]
        return words


def test_bound_free_ratio(word_root, all_words):
    """Test if a word root appears mostly in bound forms (with affixes)

    Nouns typically are bound: oak → okal, okar, okol, okor (>95%)
    Returns: (bound_count, free_count, bound_ratio)
    """
    case_suffixes = ["al", "ar", "ol", "or"]

    bound_forms = 0
    free_forms = 0

    for word in all_words:
        # Check if word contains the root
        if word_root in word:
            # Is it bare root?
            if word == word_root:
                free_forms += 1
            # Or does it have affixes?
            else:
                # Check for case suffixes
                has_case = any(word.endswith(suffix) for suffix in case_suffixes)
                if has_case:
                    bound_forms += 1
                else:
                    # Other affixes
                    if len(word) > len(word_root):
                        bound_forms += 1

    total = bound_forms + free_forms
    bound_ratio = bound_forms / total if total > 0 else 0

    return (bound_forms, free_forms, bound_ratio)


def find_water_candidate(f84v_words, all_words):
    """Find the most likely 'water' term

    Criteria:
    - Highly enriched in bath sections (3x+)
    - High frequency overall (top 50)
    - Takes case marking (bound form ratio >90%)
    - NOT oak/oat (already known)
    """
    print("=" * 80)
    print("SEARCH 1: FINDING 'WATER' TERM")
    print("=" * 80)
    print()
    print("HYPOTHESIS: Water term should be:")
    print("  - Highly enriched in bath sections (where water is depicted)")
    print("  - High frequency (water is common ingredient)")
    print("  - Takes case marking: water-LOC (in water), water-INSTR (with water)")
    print()

    f84v_freq = Counter(f84v_words)
    all_freq = Counter(all_words)

    # Get candidates: top words in f84v, excluding known ones
    candidates = []
    known_words = {
        "qok",
        "qot",
        "ok",
        "ot",
        "daiin",
        "aiin",
        "saiin",
        "oiin",
        "chedy",
        "shedy",
    }

    for word, f84v_count in f84v_freq.most_common(50):
        # Skip if too short or known
        if len(word) <= 2 or any(k in word for k in known_words):
            continue

        ms_count = all_freq[word]

        # Calculate enrichment
        f84v_rate = f84v_count / len(f84v_words)
        ms_rate = ms_count / len(all_words)
        enrichment = f84v_rate / ms_rate if ms_rate > 0 else 0

        # Must be enriched
        if enrichment < 2.0:
            continue

        # Test bound/free ratio
        # Extract likely root (remove common suffixes)
        root = word
        for suffix in ["al", "ar", "ol", "or", "edy", "ain", "iin"]:
            if word.endswith(suffix) and len(word) > len(suffix):
                root = word[: -len(suffix)]
                break

        bound, free, ratio = test_bound_free_ratio(root, all_words)

        # Must be mostly bound (noun-like)
        if ratio < 0.85:
            continue

        candidates.append(
            {
                "word": word,
                "root": root,
                "f84v_count": f84v_count,
                "ms_count": ms_count,
                "enrichment": enrichment,
                "bound_count": bound,
                "free_count": free,
                "bound_ratio": ratio,
            }
        )

    # Sort by enrichment
    candidates.sort(key=lambda x: x["enrichment"], reverse=True)

    print("TOP 10 WATER CANDIDATES:")
    print("-" * 80)
    print(
        f"{'Word':<15} {'Root':<10} {'Enrich':<8} {'F84v':<8} {'MS':<10} {'Bound%':<8}"
    )
    print("-" * 80)

    for cand in candidates[:10]:
        print(
            f"{cand['word']:<15} {cand['root']:<10} {cand['enrichment']:<8.1f}x "
            f"{cand['f84v_count']:<8} {cand['ms_count']:<10} {100 * cand['bound_ratio']:<8.0f}%"
        )

    print()

    if candidates:
        top = candidates[0]
        print(f"TOP CANDIDATE: '{top['word']}' (root: '{top['root']}')")
        print(f"  Enrichment: {top['enrichment']:.1f}x in bath sections")
        print(f"  Bound ratio: {100 * top['bound_ratio']:.0f}% (noun-like)")
        print(f"  Frequency: {top['ms_count']} instances in manuscript")
        print()

        # Test case distribution
        print(f"  Case distribution for '{top['root']}':")
        case_forms = defaultdict(int)
        for word in all_words:
            if top["root"] in word:
                for case in ["al", "ar", "ol", "or"]:
                    if word.endswith(case):
                        case_forms[case] += 1
                if word == top["root"]:
                    case_forms["bare"] += 1

        total_forms = sum(case_forms.values())
        for form, count in sorted(case_forms.items(), key=lambda x: x[1], reverse=True):
            pct = 100 * count / total_forms
            print(f"    {form:8s}: {count:4d} ({pct:5.1f}%)")
        print()

    return candidates


def find_cooccurrence_with_known(target_root, all_text, window=5):
    """Find what words co-occur with a target root near known words (oak/oat)"""

    known_roots = ["qok", "qot", "ok", "ot"]

    words = all_text.split()

    cooccurrences = Counter()

    for i, word in enumerate(words):
        # If word contains target root
        if target_root in word.lower():
            # Look at nearby words
            start = max(0, i - window)
            end = min(len(words), i + window + 1)

            for j in range(start, end):
                if j != i:
                    nearby_word = words[j].lower()
                    # Check if it's a known word
                    if any(root in nearby_word for root in known_roots):
                        cooccurrences[nearby_word] += 1

    return cooccurrences


def analyze_top_candidate(candidate, all_words, f84v_words):
    """Deep analysis of top candidate"""

    print("=" * 80)
    print(f"DEEP ANALYSIS: '{candidate['word']}' (root: '{candidate['root']}')")
    print("=" * 80)
    print()

    root = candidate["root"]

    # Co-occurrence with oak/oat
    print("CO-OCCURRENCE WITH OAK/OAT:")
    print("-" * 80)

    # Load full text
    with open(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt",
        "r",
        encoding="utf-8",
    ) as f:
        full_text = f.read()

    cooccur = find_cooccurrence_with_known(root, full_text, window=5)

    if cooccur:
        print("  Words containing this root appear near oak/oat:")
        for word, count in cooccur.most_common(10):
            print(f"    {word:<20} {count:4d} times")
        print()
        print(f"  ✓ Co-occurs with oak/oat {sum(cooccur.values())} times")
        print(f"    → Likely preparation ingredient/medium")
    else:
        print("  ✗ Does not co-occur with oak/oat")
    print()

    # Context examples
    print("EXAMPLE CONTEXTS IN F84V:")
    print("-" * 80)

    # Find sentences containing this root
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
                if root in text.lower():
                    lines.append(text)

    for i, line in enumerate(lines[:5], 1):
        # Highlight the root
        highlighted = line.lower()
        for word in line.split():
            if root in word.lower():
                highlighted = highlighted.replace(word.lower(), f"**{word.upper()}**")
        print(f"  {i}. {highlighted}")
    print()

    return cooccur


def main():
    print("=" * 80)
    print("FINDING CORE NOUNS FOR VERB DISAMBIGUATION")
    print("=" * 80)
    print()
    print("GOAL: Find 'water', 'vessel', 'heat' terms to enable verb meaning analysis")
    print()
    print("STRATEGY: Use oak/oat validation methods:")
    print("  1. Statistical enrichment in relevant sections")
    print("  2. Bound/free ratio (>85% take case marking)")
    print("  3. Co-occurrence with validated words")
    print("  4. Case distribution analysis")
    print()

    # Load data
    print("Loading data...")
    f84v_words = load_f84v_words()
    all_words = load_full_manuscript()
    print(f"  F84v words: {len(f84v_words)}")
    print(f"  Manuscript words: {len(all_words)}")
    print()

    # Find water candidate
    water_candidates = find_water_candidate(f84v_words, all_words)

    if water_candidates:
        print()
        print("=" * 80)
        print("VALIDATION TEST: TOP CANDIDATE")
        print("=" * 80)
        print()

        top_candidate = water_candidates[0]
        cooccur = analyze_top_candidate(top_candidate, all_words, f84v_words)

        # VERDICT
        print("=" * 80)
        print("VERDICT ON TOP CANDIDATE")
        print("=" * 80)
        print()

        root = top_candidate["root"]
        enrichment = top_candidate["enrichment"]
        bound_ratio = top_candidate["bound_ratio"]
        cooccur_count = sum(cooccur.values()) if cooccur else 0

        print(f"Candidate: '{root}'")
        print()
        print(f"  Evidence:")
        print(f"    - {enrichment:.1f}x enriched in bath sections")
        print(f"    - {100 * bound_ratio:.0f}% bound forms (noun-like)")
        print(f"    - {cooccur_count} co-occurrences with oak/oat")
        print(f"    - {top_candidate['ms_count']} total instances")
        print()

        score = 0
        if enrichment >= 3.0:
            score += 2
            print("    ✓✓ Strong enrichment (3x+)")
        elif enrichment >= 2.0:
            score += 1
            print("    ✓ Moderate enrichment (2x+)")

        if bound_ratio >= 0.90:
            score += 2
            print("    ✓✓ Very high bound ratio (90%+)")
        elif bound_ratio >= 0.85:
            score += 1
            print("    ✓ High bound ratio (85%+)")

        if cooccur_count >= 20:
            score += 2
            print("    ✓✓ Frequent co-occurrence with oak/oat")
        elif cooccur_count >= 10:
            score += 1
            print("    ✓ Some co-occurrence with oak/oat")

        print()
        print(f"  VALIDATION SCORE: {score}/6")
        print()

        if score >= 5:
            print("  ✓✓✓ VERY STRONG CANDIDATE")
            print(f"      → '{root}' is very likely a core noun (possibly 'water')")
        elif score >= 4:
            print("  ✓✓ STRONG CANDIDATE")
            print(f"      → '{root}' is likely a core noun")
        elif score >= 3:
            print("  ✓ MODERATE CANDIDATE")
            print(f"      → '{root}' shows noun-like properties")
        else:
            print("  ✗ WEAK CANDIDATE")
            print(f"      → Need to examine other candidates")
        print()

    # Save results
    results = {
        "water_candidates": water_candidates[:10],
        "top_candidate": water_candidates[0] if water_candidates else None,
    }

    output_path = Path("results/phase4/core_noun_search.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
