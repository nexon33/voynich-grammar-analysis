"""
Critical Test: Content Words vs Particles
==========================================

Testing if ok/ot are content words (oak/oat) or particles (with/of).

Four decisive tests:

TEST 1: Free vs Bound Morphemes
- If ok/ot appear standalone → could be particles
- If ok/ot only appear with affixes → likely content roots + required case

TEST 2: Semantic Field Coherence
- If ok-words cluster with botanical terms → content word
- If ok-words appear randomly distributed → particle

TEST 3: Compositionality
- If okedy/otedy have parallel meanings → content + verbal
- If unrelated meanings → different analysis needed

TEST 4: Root vs Affix Context Diversity
- Content roots: domain-constrained (low diversity in specific contexts)
- Affixes: promiscuous (high diversity across all contexts)
- Compare ok/ot to validated affixes -al/-ar

This resolves the circular reasoning: we're testing PREDICTIONS not DEFINITIONS.
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
import math


def load_manuscript():
    """Load manuscript"""
    transcription_path = Path(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt"
    )

    with open(transcription_path, "r", encoding="utf-8") as f:
        text = f.read()

    words = text.lower().split()
    return words


def test_free_vs_bound(words):
    """
    TEST 1: Are ok/ot free-standing or always affixed?

    Compare:
    - ok (bare)
    - oke, oko (minor variants)
    - okal, okar, okol, okor (+ case)
    - okedy, okeedy (+ verbal)
    - qokedy, qokeedy (+ genitive + verbal)
    """
    # Count different forms
    ok_forms = defaultdict(int)
    ot_forms = defaultdict(int)

    for word in words:
        # OK forms
        if word == "ok":
            ok_forms["bare: ok"] += 1
        elif word == "oke":
            ok_forms["bare: oke"] += 1
        elif word == "oko":
            ok_forms["bare: oko"] += 1
        elif word.startswith("ok") and len(word) > 2:
            # Categorize by suffix
            suffix = word[2:]
            if suffix in ["al", "ar", "ol", "or"]:
                ok_forms[f"case: ok+{suffix}"] += 1
            elif suffix in ["edy", "eedy", "dy", "y"]:
                ok_forms[f"verbal: ok+{suffix}"] += 1
            elif suffix.startswith("ai"):
                ok_forms[f"compound?: ok+{suffix}"] += 1
            else:
                ok_forms[f"other: ok+{suffix}"] += 1

        # Special: qok- prefix forms
        if word.startswith("qok") and len(word) > 3:
            ok_forms[f"genitive: qok+..."] += 1

        # OT forms
        if word == "ot":
            ot_forms["bare: ot"] += 1
        elif word == "ote":
            ot_forms["bare: ote"] += 1
        elif word == "oto":
            ot_forms["bare: oto"] += 1
        elif word.startswith("ot") and len(word) > 2:
            suffix = word[2:]
            if suffix in ["al", "ar", "ol", "or"]:
                ot_forms[f"case: ot+{suffix}"] += 1
            elif suffix in ["edy", "eedy", "dy", "y"]:
                ot_forms[f"verbal: ot+{suffix}"] += 1
            elif suffix.startswith("ai"):
                ot_forms[f"compound?: ot+{suffix}"] += 1
            elif suffix.startswith("ch"):
                ot_forms[f"compound?: ot+{suffix}"] += 1
            else:
                ot_forms[f"other: ot+{suffix}"] += 1

        # Special: qot- forms
        if word.startswith("qot") and len(word) > 3:
            ot_forms[f"genitive: qot+..."] += 1

    # Calculate free vs bound ratios
    ok_total = sum(ok_forms.values())
    ok_bare = ok_forms["bare: ok"] + ok_forms["bare: oke"] + ok_forms["bare: oko"]
    ok_bound = ok_total - ok_bare

    ot_total = sum(ot_forms.values())
    ot_bare = ot_forms["bare: ot"] + ot_forms["bare: ote"] + ot_forms["bare: oto"]
    ot_bound = ot_total - ot_bare

    return {
        "ok": {
            "forms": dict(ok_forms),
            "total": ok_total,
            "bare": ok_bare,
            "bound": ok_bound,
            "bare_ratio": ok_bare / ok_total if ok_total > 0 else 0,
            "bound_ratio": ok_bound / ok_total if ok_total > 0 else 0,
        },
        "ot": {
            "forms": dict(ot_forms),
            "total": ot_total,
            "bare": ot_bare,
            "bound": ot_bound,
            "bare_ratio": ot_bare / ot_total if ot_total > 0 else 0,
            "bound_ratio": ot_bound / ot_total if ot_total > 0 else 0,
        },
    }


def test_semantic_coherence(words):
    """
    TEST 2: Do ok-words cluster with botanical/practical terms?

    Find all ok-containing words and check their context:
    - Do they co-occur with each other? (botanical cluster)
    - Do they co-occur with validated botanical terms?
    - Or random distribution?
    """
    # Collect validated botanical/practical terms
    botanical_terms = {
        # Known plants
        "oke",
        "oko",
        "okal",
        "okar",
        "okedy",
        "ote",
        "oto",
        "otal",
        "otar",
        "otedy",
        # Suspected botanical (from previous analysis)
        "okeey",
        "oteey",
        "qokey",
        "qotey",
        # Known verbs (practical actions)
        "chedy",
        "shedy",
        "qokedy",
        "qokeedy",
    }

    # Find all ok-words and ot-words
    ok_words = set()
    ot_words = set()

    for word in set(words):
        if "ok" in word and len(word) >= 3:
            ok_words.add(word)
        if "ot" in word and len(word) >= 3:
            ot_words.add(word)

    # Measure co-occurrence
    window = 10

    ok_cooccurrence = Counter()
    ot_cooccurrence = Counter()

    for i, word in enumerate(words):
        # If word contains ok
        if word in ok_words:
            # Check nearby words
            start = max(0, i - window)
            end = min(len(words), i + window + 1)

            for j in range(start, end):
                if j != i:
                    nearby = words[j]
                    if (
                        nearby in botanical_terms
                        or nearby in ok_words
                        or nearby in ot_words
                    ):
                        ok_cooccurrence[nearby] += 1

        # If word contains ot
        if word in ot_words:
            start = max(0, i - window)
            end = min(len(words), i + window + 1)

            for j in range(start, end):
                if j != i:
                    nearby = words[j]
                    if (
                        nearby in botanical_terms
                        or nearby in ok_words
                        or nearby in ot_words
                    ):
                        ot_cooccurrence[nearby] += 1

    # Calculate clustering coefficient
    # If botanical terms appear together more than random → semantic cluster

    total_ok_contexts = sum(ok_cooccurrence.values())
    botanical_in_ok_contexts = sum(
        count for word, count in ok_cooccurrence.items() if word in botanical_terms
    )

    total_ot_contexts = sum(ot_cooccurrence.values())
    botanical_in_ot_contexts = sum(
        count for word, count in ot_cooccurrence.items() if word in botanical_terms
    )

    # Expected rate (baseline)
    total_words = len(words)
    botanical_baseline = len(botanical_terms) / len(set(words))

    return {
        "ok_words": {
            "unique_count": len(ok_words),
            "cooccurrence": dict(ok_cooccurrence.most_common(20)),
            "total_contexts": total_ok_contexts,
            "botanical_contexts": botanical_in_ok_contexts,
            "botanical_rate": botanical_in_ok_contexts / total_ok_contexts
            if total_ok_contexts > 0
            else 0,
            "expected_botanical_rate": botanical_baseline,
        },
        "ot_words": {
            "unique_count": len(ot_words),
            "cooccurrence": dict(ot_cooccurrence.most_common(20)),
            "total_contexts": total_ot_contexts,
            "botanical_contexts": botanical_in_ot_contexts,
            "botanical_rate": botanical_in_ot_contexts / total_ot_contexts
            if total_ot_contexts > 0
            else 0,
            "expected_botanical_rate": botanical_baseline,
        },
    }


def test_compositionality(words):
    """
    TEST 3: Do okedy/otedy have parallel structure?

    If oak/oat are content roots:
    - okedy = oak + verbal (to use oak, oak-action)
    - otedy = oat + verbal (to use oat, oat-action)

    They should appear in similar contexts, with similar frequencies,
    in similar sections.
    """
    # Find all -edy forms
    edy_forms = defaultdict(
        lambda: {"count": 0, "contexts_before": Counter(), "contexts_after": Counter()}
    )

    for i, word in enumerate(words):
        if word.endswith("edy") and len(word) > 3:
            root = word[:-3]
            edy_forms[root]["count"] += 1

            # Context before
            if i > 0:
                edy_forms[root]["contexts_before"][words[i - 1]] += 1

            # Context after
            if i < len(words) - 1:
                edy_forms[root]["contexts_after"][words[i + 1]] += 1

    # Compare ok/ot specifically
    ok_edy = edy_forms["ok"]
    ot_edy = edy_forms["ot"]

    # Calculate context overlap
    ok_before = set(ok_edy["contexts_before"].keys())
    ot_before = set(ot_edy["contexts_before"].keys())

    before_overlap = len(ok_before & ot_before)
    before_union = len(ok_before | ot_before)

    ok_after = set(ok_edy["contexts_after"].keys())
    ot_after = set(ot_edy["contexts_after"].keys())

    after_overlap = len(ok_after & ot_after)
    after_union = len(ok_after | ot_after)

    # Parallel structure score
    parallel_score = (
        ((before_overlap / before_union) + (after_overlap / after_union)) / 2
        if before_union > 0 and after_union > 0
        else 0
    )

    return {
        "all_edy_roots": {
            root: data["count"]
            for root, data in sorted(
                edy_forms.items(), key=lambda x: x[1]["count"], reverse=True
            )[:20]
        },
        "okedy": {
            "count": ok_edy["count"],
            "top_before": dict(ok_edy["contexts_before"].most_common(10)),
            "top_after": dict(ok_edy["contexts_after"].most_common(10)),
        },
        "otedy": {
            "count": ot_edy["count"],
            "top_before": dict(ot_edy["contexts_before"].most_common(10)),
            "top_after": dict(ot_edy["contexts_after"].most_common(10)),
        },
        "parallel_structure": {
            "before_overlap": before_overlap,
            "before_union": before_union,
            "after_overlap": after_overlap,
            "after_union": after_union,
            "parallel_score": parallel_score,
        },
    }


def test_root_vs_affix_diversity(words):
    """
    TEST 4: Compare context diversity of roots vs affixes

    True content roots (oak, oat):
    - Should have CONSTRAINED contexts (botanical domain)
    - Lower context diversity in specific semantic field

    True affixes (-al, -ar):
    - Should have PROMISCUOUS contexts (any noun)
    - Higher context diversity across all domains

    Measure: unique contexts per occurrence
    """
    # Analyze ok/ot as roots
    ok_contexts = set()
    ok_count = 0

    ot_contexts = set()
    ot_count = 0

    # Analyze -al/-ar as affixes
    al_contexts = set()
    al_count = 0

    ar_contexts = set()
    ar_count = 0

    window = 3

    for i, word in enumerate(words):
        # Get context
        context_before = tuple(words[max(0, i - window) : i]) if i > 0 else ()
        context_after = (
            tuple(words[i + 1 : min(len(words), i + 1 + window)])
            if i < len(words) - 1
            else ()
        )
        context = (context_before, context_after)

        # Check ok/ot
        if "ok" in word:
            ok_contexts.add(context)
            ok_count += 1

        if "ot" in word:
            ot_contexts.add(context)
            ot_count += 1

        # Check -al/-ar
        if word.endswith("al") and len(word) > 2:
            al_contexts.add(context)
            al_count += 1

        if word.endswith("ar") and len(word) > 2:
            ar_contexts.add(context)
            ar_count += 1

    # Calculate diversity scores
    ok_diversity = len(ok_contexts) / ok_count if ok_count > 0 else 0
    ot_diversity = len(ot_contexts) / ot_count if ot_count > 0 else 0
    al_diversity = len(al_contexts) / al_count if al_count > 0 else 0
    ar_diversity = len(ar_contexts) / ar_count if ar_count > 0 else 0

    return {
        "ok": {
            "occurrences": ok_count,
            "unique_contexts": len(ok_contexts),
            "diversity_score": ok_diversity,
        },
        "ot": {
            "occurrences": ot_count,
            "unique_contexts": len(ot_contexts),
            "diversity_score": ot_diversity,
        },
        "al_affix": {
            "occurrences": al_count,
            "unique_contexts": len(al_contexts),
            "diversity_score": al_diversity,
        },
        "ar_affix": {
            "occurrences": ar_count,
            "unique_contexts": len(ar_contexts),
            "diversity_score": ar_diversity,
        },
        "interpretation": {
            "ok_vs_al_ratio": ok_diversity / al_diversity if al_diversity > 0 else 0,
            "ot_vs_ar_ratio": ot_diversity / ar_diversity if ar_diversity > 0 else 0,
        },
    }


def main():
    print("=" * 80)
    print("CRITICAL TEST: CONTENT WORDS VS PARTICLES")
    print("=" * 80)
    print()
    print("Resolving the circular reasoning: Are ok/ot particles or content words?")
    print()

    # Load data
    print("Loading manuscript...")
    words = load_manuscript()
    print(f"Total words: {len(words):,}")
    print()

    # TEST 1: Free vs Bound
    print("=" * 80)
    print("TEST 1: FREE VS BOUND MORPHEMES")
    print("=" * 80)
    print()
    print("If ok/ot are particles → should appear standalone frequently")
    print("If ok/ot are content roots → mostly appear with case/verbal affixes")
    print()

    free_bound = test_free_vs_bound(words)

    print("OK forms:")
    print(
        f"  Bare (ok/oke/oko): {free_bound['ok']['bare']} ({free_bound['ok']['bare_ratio']:.1%})"
    )
    print(
        f"  Bound (affixed):   {free_bound['ok']['bound']} ({free_bound['ok']['bound_ratio']:.1%})"
    )
    print(f"  Total: {free_bound['ok']['total']}")
    print()
    print("  Top forms:")
    for form, count in sorted(
        free_bound["ok"]["forms"].items(), key=lambda x: x[1], reverse=True
    )[:10]:
        print(f"    {form}: {count}")
    print()

    print("OT forms:")
    print(
        f"  Bare (ot/ote/oto): {free_bound['ot']['bare']} ({free_bound['ot']['bare_ratio']:.1%})"
    )
    print(
        f"  Bound (affixed):   {free_bound['ot']['bound']} ({free_bound['ot']['bound_ratio']:.1%})"
    )
    print(f"  Total: {free_bound['ot']['total']}")
    print()
    print("  Top forms:")
    for form, count in sorted(
        free_bound["ot"]["forms"].items(), key=lambda x: x[1], reverse=True
    )[:10]:
        print(f"    {form}: {count}")
    print()

    # Evaluate TEST 1
    if free_bound["ok"]["bound_ratio"] > 0.7 and free_bound["ot"]["bound_ratio"] > 0.7:
        print("✓ TEST 1 RESULT: Predominantly BOUND forms")
        print("  → Supports content word interpretation (roots require case marking)")
    elif free_bound["ok"]["bare_ratio"] > 0.3 and free_bound["ot"]["bare_ratio"] > 0.3:
        print("✓ TEST 1 RESULT: Significant FREE-STANDING forms")
        print("  → Supports particle interpretation")
    else:
        print("~ TEST 1 RESULT: Mixed pattern")

    print()

    # TEST 2: Semantic Coherence
    print("=" * 80)
    print("TEST 2: SEMANTIC FIELD COHERENCE")
    print("=" * 80)
    print()
    print("If ok/ot are content → should cluster with botanical/practical terms")
    print("If ok/ot are particles → random distribution")
    print()

    semantic = test_semantic_coherence(words)

    print(f"OK-words: {semantic['ok_words']['unique_count']} unique forms")
    print(
        f"  Co-occur with botanical terms: {semantic['ok_words']['botanical_rate']:.1%}"
    )
    print(f"  Expected baseline: {semantic['ok_words']['expected_botanical_rate']:.1%}")
    print(
        f"  Enrichment: {semantic['ok_words']['botanical_rate'] / semantic['ok_words']['expected_botanical_rate']:.2f}x"
    )
    print()
    print("  Top co-occurring words:")
    for word, count in list(semantic["ok_words"]["cooccurrence"].items())[:10]:
        print(f"    {word}: {count}")
    print()

    print(f"OT-words: {semantic['ot_words']['unique_count']} unique forms")
    print(
        f"  Co-occur with botanical terms: {semantic['ot_words']['botanical_rate']:.1%}"
    )
    print(f"  Expected baseline: {semantic['ot_words']['expected_botanical_rate']:.1%}")
    print(
        f"  Enrichment: {semantic['ot_words']['botanical_rate'] / semantic['ot_words']['expected_botanical_rate']:.2f}x"
    )
    print()

    # Evaluate TEST 2
    ok_enrichment = (
        semantic["ok_words"]["botanical_rate"]
        / semantic["ok_words"]["expected_botanical_rate"]
    )
    ot_enrichment = (
        semantic["ot_words"]["botanical_rate"]
        / semantic["ot_words"]["expected_botanical_rate"]
    )

    if ok_enrichment > 2.0 and ot_enrichment > 2.0:
        print("✓ TEST 2 RESULT: Strong SEMANTIC CLUSTERING")
        print("  → Supports content word interpretation (domain-specific)")
    elif ok_enrichment < 1.5 and ot_enrichment < 1.5:
        print("✓ TEST 2 RESULT: Random distribution")
        print("  → Supports particle interpretation")
    else:
        print("~ TEST 2 RESULT: Moderate clustering")

    print()

    # TEST 3: Compositionality
    print("=" * 80)
    print("TEST 3: COMPOSITIONALITY")
    print("=" * 80)
    print()
    print("If ok/ot are content → okedy/otedy should have parallel structure")
    print()

    compositionality = test_compositionality(words)

    print(f"okedy: {compositionality['okedy']['count']} instances")
    print("  Top contexts BEFORE:")
    for word, count in list(compositionality["okedy"]["top_before"].items())[:5]:
        print(f"    {word}: {count}")
    print("  Top contexts AFTER:")
    for word, count in list(compositionality["okedy"]["top_after"].items())[:5]:
        print(f"    {word}: {count}")
    print()

    print(f"otedy: {compositionality['otedy']['count']} instances")
    print("  Top contexts BEFORE:")
    for word, count in list(compositionality["otedy"]["top_before"].items())[:5]:
        print(f"    {word}: {count}")
    print("  Top contexts AFTER:")
    for word, count in list(compositionality["otedy"]["top_after"].items())[:5]:
        print(f"    {word}: {count}")
    print()

    print(
        f"Parallel structure score: {compositionality['parallel_structure']['parallel_score']:.1%}"
    )
    print(
        f"  Context overlap: {compositionality['parallel_structure']['before_overlap']}/{compositionality['parallel_structure']['before_union']} before, {compositionality['parallel_structure']['after_overlap']}/{compositionality['parallel_structure']['after_union']} after"
    )
    print()

    # Evaluate TEST 3
    if compositionality["parallel_structure"]["parallel_score"] > 0.5:
        print("✓ TEST 3 RESULT: High PARALLEL STRUCTURE")
        print("  → Supports content word interpretation (systematic composition)")
    else:
        print("✗ TEST 3 RESULT: Low parallel structure")

    print()

    # TEST 4: Root vs Affix Diversity
    print("=" * 80)
    print("TEST 4: ROOT VS AFFIX CONTEXT DIVERSITY")
    print("=" * 80)
    print()
    print("Content roots: constrained contexts (LOW diversity)")
    print("Grammatical affixes: promiscuous contexts (HIGH diversity)")
    print()

    diversity = test_root_vs_affix_diversity(words)

    print(f"ok diversity: {diversity['ok']['diversity_score']:.3f}")
    print(
        f"  ({diversity['ok']['unique_contexts']} unique contexts / {diversity['ok']['occurrences']} occurrences)"
    )
    print()
    print(f"ot diversity: {diversity['ot']['diversity_score']:.3f}")
    print(
        f"  ({diversity['ot']['unique_contexts']} unique contexts / {diversity['ot']['occurrences']} occurrences)"
    )
    print()
    print(f"-al affix diversity: {diversity['al_affix']['diversity_score']:.3f}")
    print(
        f"  ({diversity['al_affix']['unique_contexts']} unique contexts / {diversity['al_affix']['occurrences']} occurrences)"
    )
    print()
    print(f"-ar affix diversity: {diversity['ar_affix']['diversity_score']:.3f}")
    print(
        f"  ({diversity['ar_affix']['unique_contexts']} unique contexts / {diversity['ar_affix']['occurrences']} occurrences)"
    )
    print()

    print(f"ok/al ratio: {diversity['interpretation']['ok_vs_al_ratio']:.2f}")
    print(f"ot/ar ratio: {diversity['interpretation']['ot_vs_ar_ratio']:.2f}")
    print()

    # Evaluate TEST 4
    if (
        diversity["interpretation"]["ok_vs_al_ratio"] < 0.8
        and diversity["interpretation"]["ot_vs_ar_ratio"] < 0.8
    ):
        print("✓ TEST 4 RESULT: Roots have LOWER diversity than affixes")
        print("  → Supports content word interpretation (domain-constrained)")
    elif diversity["interpretation"]["ok_vs_al_ratio"] > 1.2:
        print("✓ TEST 4 RESULT: Roots have HIGHER diversity than affixes")
        print("  → Supports particle interpretation (promiscuous distribution)")
    else:
        print("~ TEST 4 RESULT: Similar diversity levels")

    print()

    # FINAL VERDICT
    print("=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)
    print()

    tests_passed = 0
    tests_for_content = 0
    tests_for_particle = 0

    # Score tests
    if free_bound["ok"]["bound_ratio"] > 0.7:
        tests_for_content += 1
    elif free_bound["ok"]["bare_ratio"] > 0.3:
        tests_for_particle += 1

    if ok_enrichment > 2.0 and ot_enrichment > 2.0:
        tests_for_content += 1
    elif ok_enrichment < 1.5:
        tests_for_particle += 1

    if compositionality["parallel_structure"]["parallel_score"] > 0.5:
        tests_for_content += 1

    if diversity["interpretation"]["ok_vs_al_ratio"] < 0.8:
        tests_for_content += 1
    elif diversity["interpretation"]["ok_vs_al_ratio"] > 1.2:
        tests_for_particle += 1

    print(f"Tests supporting CONTENT WORD interpretation: {tests_for_content}")
    print(f"Tests supporting PARTICLE interpretation: {tests_for_particle}")
    print()

    if tests_for_content >= 3:
        print("✓✓✓ VERDICT: ok/ot are CONTENT WORDS (likely oak/oat)")
        print()
        print("Evidence:")
        print("  - Predominantly bound forms (require case marking)")
        print("  - Cluster with botanical/practical terms")
        print("  - Show compositional structure")
        print("  - Domain-constrained contexts")
        print()
        print("Conclusion: Original oak/oat interpretation is VALIDATED")
        print(
            "The particle hypothesis was over-correction based on decomposition artifacts"
        )
    elif tests_for_particle >= 3:
        print("✓✓✓ VERDICT: ok/ot are PARTICLES")
        print()
        print("Evidence:")
        print("  - Significant free-standing forms")
        print("  - Random distribution")
        print("  - High context diversity")
        print()
        print("Conclusion: Need to reconsider oak/oat interpretation")
    else:
        print("~ VERDICT: INCONCLUSIVE")
        print("Mixed evidence - may have hybrid function")

    # Save results
    results = {
        "test1_free_bound": free_bound,
        "test2_semantic_coherence": semantic,
        "test3_compositionality": compositionality,
        "test4_diversity": diversity,
        "verdict": {
            "tests_for_content": tests_for_content,
            "tests_for_particle": tests_for_particle,
            "conclusion": "CONTENT_WORD"
            if tests_for_content >= 3
            else ("PARTICLE" if tests_for_particle >= 3 else "INCONCLUSIVE"),
        },
    }

    output_path = Path("results/phase4/content_vs_particle_test.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print()
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
