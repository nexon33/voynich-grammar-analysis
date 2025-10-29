"""
Decode Top 20 Most Productive Roots
====================================

From morphological analysis, we have 506 root families.
But we only know meanings for ~5 roots (oak, oat, ch=take?, sh=mix?, ai=this).

Strategy: Use the SAME distributional methods that successfully identified:
- Pronouns (appear sentence-initial, not between nouns)
- Verbs (appear before objects)

For each unknown root, test:
1. Positional distribution (where does it appear?)
2. Co-occurrence (what does it appear with?)
3. Affix preferences (what suffixes does it take?)
4. Section distribution (which sections is it enriched in?)

Target roots (from Phase 4):
1. ch (2,728×) - partially validated as verb root
2. ai (2,086×) - validated as pronoun root
3. ot (1,373×) - validated as oat
4. he (1,155×) - UNKNOWN
5. ok (883×) - validated as oak
6. ee (735×) - UNKNOWN
7. al (652×) - UNKNOWN (also a suffix!)
8. ar (641×) - UNKNOWN (also a suffix!)
9. ol (611×) - UNKNOWN (also a suffix!)
10. che (477×) - UNKNOWN
11. ho (452×) - UNKNOWN
12. ai! (434×) - variant of ai?
13. otch (344×) - UNKNOWN
14. ed (323×) - UNKNOWN
15. ke (317×) - UNKNOWN
16. cth (298×) - UNKNOWN
17. ote (276×) - variant of ot?
18. or (258×) - UNKNOWN (also a suffix!)
19. otai (250×) - compound?
20. oke (245×) - variant of ok?
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


def load_morphological_data():
    """Load root families from morphological analysis"""
    morph_path = Path("results/phase4/morphological_decomposition.json")

    with open(morph_path, "r") as f:
        data = json.load(f)

    return data["root_families"]


def load_validated_knowledge():
    """Load what we already know"""
    return {
        "plants": {"ot", "ote", "oto", "ok", "oke", "oko"},
        "pronouns": {"ai", "da", "sa"},
        "verbs": {"ch", "sh"},
        "particles": set(),  # To be determined
    }


def test_pronoun_hypothesis(words, root_variants):
    """
    Test if root behaves like pronoun:
    - Appears sentence-initially
    - Does NOT appear between nouns (plants)
    """
    plant_variants = {"ot", "ote", "oto", "ok", "oke", "oko", "otch", "okch"}

    sentence_initial = 0
    between_plants = 0
    total_occurrences = 0

    for i, word in enumerate(words):
        # Check if word contains this root
        if any(word.startswith(variant) for variant in root_variants):
            total_occurrences += 1

            # Sentence initial (previous word is pronoun or start)
            if i == 0 or words[i - 1] in {"daiin", "aiin", "saiin"}:
                sentence_initial += 1

            # Between plants
            if i > 0 and i < len(words) - 1:
                before_plant = any(words[i - 1].startswith(p) for p in plant_variants)
                after_plant = any(words[i + 1].startswith(p) for p in plant_variants)
                if before_plant and after_plant:
                    between_plants += 1

    if total_occurrences == 0:
        return None

    return {
        "sentence_initial_rate": sentence_initial / total_occurrences,
        "between_plants_rate": between_plants / total_occurrences,
        "total_occurrences": total_occurrences,
        "pronoun_score": (sentence_initial / total_occurrences)
        - (between_plants / total_occurrences),
    }


def test_verb_hypothesis(words, root_variants):
    """
    Test if root behaves like verb:
    - Appears before objects (plants)
    - Appears in serial constructions
    """
    plant_variants = {"ot", "ote", "oto", "ok", "oke", "oko", "otch", "okch"}

    before_plant = 0
    after_plant = 0
    total_occurrences = 0

    for i, word in enumerate(words):
        if any(word.startswith(variant) for variant in root_variants):
            total_occurrences += 1

            # Before plant
            if i < len(words) - 1:
                if any(words[i + 1].startswith(p) for p in plant_variants):
                    before_plant += 1

            # After plant
            if i > 0:
                if any(words[i - 1].startswith(p) for p in plant_variants):
                    after_plant += 1

    if total_occurrences == 0:
        return None

    return {
        "before_plant_rate": before_plant / total_occurrences,
        "after_plant_rate": after_plant / total_occurrences,
        "total_occurrences": total_occurrences,
        "verb_score": (before_plant / total_occurrences),  # Verbs appear before objects
    }


def test_noun_hypothesis(words, root_variants):
    """
    Test if root behaves like noun:
    - Takes case markers (-al, -ar, -ol, -or)
    - Appears after verbs
    - Appears after articles/prepositions
    """
    verb_variants = {"chedy", "shedy", "qokedy", "qokeedy", "qokeey"}
    prepositions = {"ol", "al", "dar", "dal", "or", "ar"}

    with_case_marker = 0
    after_verb = 0
    after_prep = 0
    total_occurrences = 0

    for i, word in enumerate(words):
        if any(word.startswith(variant) for variant in root_variants):
            total_occurrences += 1

            # Has case marker
            if word.endswith(("al", "ar", "ol", "or")) and len(word) > 3:
                with_case_marker += 1

            # After verb
            if i > 0 and words[i - 1] in verb_variants:
                after_verb += 1

            # After preposition
            if i > 0 and words[i - 1] in prepositions:
                after_prep += 1

    if total_occurrences == 0:
        return None

    return {
        "case_marker_rate": with_case_marker / total_occurrences,
        "after_verb_rate": after_verb / total_occurrences,
        "after_prep_rate": after_prep / total_occurrences,
        "total_occurrences": total_occurrences,
        "noun_score": (with_case_marker / total_occurrences)
        + (after_verb / total_occurrences),
    }


def test_particle_hypothesis(words, root_variants):
    """
    Test if root behaves like particle/function word:
    - Very high frequency
    - Short length (2-3 chars)
    - Appears in many contexts
    """
    contexts_before = Counter()
    contexts_after = Counter()
    total_occurrences = 0

    for i, word in enumerate(words):
        if word in root_variants:  # Exact match for particles
            total_occurrences += 1

            if i > 0:
                contexts_before[words[i - 1]] += 1
            if i < len(words) - 1:
                contexts_after[words[i + 1]] += 1

    if total_occurrences == 0:
        return None

    # High context diversity = function word
    context_diversity = (
        (len(contexts_before) + len(contexts_after)) / (2 * total_occurrences)
        if total_occurrences > 0
        else 0
    )

    return {
        "frequency": total_occurrences,
        "context_diversity": context_diversity,
        "total_occurrences": total_occurrences,
        "particle_score": context_diversity,
    }


def analyze_section_distribution(words, root_variants):
    """
    Calculate which sections root appears in
    """
    sections = {
        "herbal": (0, 20000),
        "biological": (20000, 25000),
        "pharmaceutical": (25000, 32000),
        "recipes": (32000, 37187),
    }

    section_counts = {s: 0 for s in sections}
    total = 0

    for i, word in enumerate(words):
        if any(word.startswith(variant) for variant in root_variants):
            total += 1

            for section_name, (start, end) in sections.items():
                if start <= i < end:
                    section_counts[section_name] += 1
                    break

    if total == 0:
        return None

    # Calculate proportions
    section_props = {s: count / total for s, count in section_counts.items()}

    # Find most enriched section
    max_section = max(section_props, key=section_props.get)

    return {
        "section_counts": section_counts,
        "section_proportions": section_props,
        "enriched_section": max_section,
        "enrichment_score": section_props[max_section],
    }


def decode_root(root, root_data, words):
    """
    Apply all tests to determine root function and possible meaning
    """
    # Get variants of this root
    variants = {root}

    # Test all hypotheses
    pronoun_test = test_pronoun_hypothesis(words, variants)
    verb_test = test_verb_hypothesis(words, variants)
    noun_test = test_noun_hypothesis(words, variants)
    particle_test = test_particle_hypothesis(words, variants)
    section_dist = analyze_section_distribution(words, variants)

    # Determine most likely category
    scores = {}

    if pronoun_test:
        scores["PRONOUN"] = pronoun_test["pronoun_score"]
    if verb_test:
        scores["VERB"] = verb_test["verb_score"]
    if noun_test:
        scores["NOUN"] = noun_test["noun_score"]
    if particle_test:
        scores["PARTICLE"] = particle_test["particle_score"]

    if not scores:
        likely_category = "UNKNOWN"
        confidence = 0.0
    else:
        likely_category = max(scores, key=scores.get)
        # Normalize confidence
        max_score = scores[likely_category]
        confidence = min(max_score, 1.0)

    return {
        "root": root,
        "frequency": root_data["total_frequency"],
        "num_variants": len(root_data["variants"]),
        "top_suffixes": list(root_data["suffix_patterns"].keys())[:3],
        "tests": {
            "pronoun": pronoun_test,
            "verb": verb_test,
            "noun": noun_test,
            "particle": particle_test,
        },
        "section_distribution": section_dist,
        "likely_category": likely_category,
        "confidence": confidence,
        "scores": scores,
    }


def main():
    print("=" * 80)
    print("DECODING TOP 20 PRODUCTIVE ROOTS")
    print("=" * 80)
    print()
    print("Using distributional methods that successfully identified pronouns/verbs")
    print()

    # Load data
    print("Loading manuscript and morphological data...")
    words = load_manuscript()
    root_families = load_morphological_data()

    print(f"Total words: {len(words):,}")
    print(f"Root families: {len(root_families)}")
    print()

    # Get top 20 roots by frequency
    sorted_roots = sorted(
        root_families.items(), key=lambda x: x[1]["total_frequency"], reverse=True
    )[:20]

    print("Analyzing top 20 most productive roots...")
    print()

    # Decode each root
    decoded_roots = []

    for root, data in sorted_roots:
        print(
            f"Analyzing: {root} ({data['total_frequency']}×, {len(data['variants'])} variants)"
        )

        analysis = decode_root(root, data, words)
        decoded_roots.append(analysis)

        print(
            f"  → {analysis['likely_category']} (confidence: {analysis['confidence']:.2f})"
        )
        print(
            f"     Scores: {', '.join(f'{k}={v:.2f}' for k, v in analysis['scores'].items())}"
        )

        if analysis["section_distribution"]:
            enriched = analysis["section_distribution"]["enriched_section"]
            enrichment = analysis["section_distribution"]["enrichment_score"]
            print(f"     Enriched in: {enriched} ({enrichment:.1%})")

        print()

    # Summary by category
    print("=" * 80)
    print("SUMMARY BY CATEGORY")
    print("=" * 80)
    print()

    by_category = defaultdict(list)
    for root in decoded_roots:
        by_category[root["likely_category"]].append(root)

    for category in ["PRONOUN", "VERB", "NOUN", "PARTICLE", "UNKNOWN"]:
        roots_in_cat = by_category[category]
        if roots_in_cat:
            print(f"\n{category} ({len(roots_in_cat)} roots):")
            for root in sorted(
                roots_in_cat, key=lambda x: x["confidence"], reverse=True
            ):
                print(
                    f"  {root['root']:<10} ({root['frequency']:>5}×) confidence: {root['confidence']:.2f}"
                )

    # Save results
    results = {
        "decoded_roots": [
            {
                "root": r["root"],
                "frequency": r["frequency"],
                "num_variants": r["num_variants"],
                "likely_category": r["likely_category"],
                "confidence": r["confidence"],
                "scores": r["scores"],
                "top_suffixes": r["top_suffixes"],
                "section_distribution": r["section_distribution"],
            }
            for r in decoded_roots
        ],
        "summary": {
            category: [r["root"] for r in roots]
            for category, roots in by_category.items()
        },
    }

    output_path = Path("results/phase4/top_20_roots_decoded.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print()
    print(f"\nResults saved to: {output_path}")
    print()
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("For roots categorized as NOUN:")
    print(
        "  → Try to identify specific meanings through co-occurrence with validated words"
    )
    print()
    print("For roots categorized as VERB:")
    print("  → Test serial verb constructions and object patterns")
    print()
    print("For roots categorized as PARTICLE:")
    print("  → Analyze syntactic position (sentence-initial, connective, etc.)")


if __name__ == "__main__":
    main()
