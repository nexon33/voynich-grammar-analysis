"""
Test Verbal Hypothesis for chedy/shedy/qokedy
==============================================

These words appear 10-18% BEFORE and AFTER plants, but only 2-3% BETWEEN.
This suggests they may be VERBS (action words) rather than conjunctions.

Verbal hypothesis:
- Verbs should appear immediately BEFORE object nouns (plants)
- Verbs should appear AFTER subject nouns/pronouns
- Verbs should NOT connect two nouns (that's conjunction behavior)
- Verbs may appear with pronoun subjects (daiin/aiin + VERB + plant)

Test patterns:
1. [pronoun] + VERB + [plant] → "it takes oak"
2. VERB + [plant] → imperative "take oak"
3. [plant] + VERB → passive or intransitive "oak grows"
4. Frequency analysis: verbs should cluster in recipe/pharmaceutical sections
"""

import json
from pathlib import Path
from collections import Counter, defaultdict


def load_manuscript():
    """Load the Voynich manuscript transcription"""
    transcription_path = Path(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt"
    )

    with open(transcription_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Simple word tokenization
    words = text.lower().split()
    return words


def load_plant_variants():
    """Load all plant variants (oak, oat + affixed forms)"""
    results_path = Path("results/phase4/manuscript_wide_hypothesis_tests.json")

    with open(results_path, "r") as f:
        data = json.load(f)

    # Extract all plant variants from previous analysis
    # We'll build from the compound matches which have our plant list
    compounds_path = Path("results/phase4/compound_and_partial_matches.json")

    with open(compounds_path, "r") as f:
        compounds = json.load(f)

    plant_variants = set()

    # Collect all Voynich words that match oak/oat
    for match in compounds["partial_matches"]:
        if "oak" in match["meaning"] or "oat" in match["meaning"]:
            plant_variants.add(match["voynich_word"])

    # Also add base forms
    plant_variants.update(["oke", "ote", "oko", "oto", "okcho", "otcho"])

    return plant_variants


def load_pronouns():
    """Load validated pronouns from hypothesis testing"""
    return {"daiin", "aiin", "saiin"}


def test_verb_pronoun_plant_pattern(words, verb_candidates, pronouns, plants):
    """
    Test pattern: [pronoun] + VERB + [plant]
    Example: "it takes oak", "this uses oat"
    """
    pattern_counts = defaultdict(lambda: {"total": 0, "examples": []})

    for i in range(1, len(words) - 1):
        word = words[i]

        if word in verb_candidates:
            word_before = words[i - 1]
            word_after = words[i + 1]

            # Check if pronoun before and plant after
            if word_before in pronouns and word_after in plants:
                pattern_counts[word]["total"] += 1

                if len(pattern_counts[word]["examples"]) < 10:
                    pattern_counts[word]["examples"].append(
                        f"{word_before} {word} {word_after}"
                    )

    return pattern_counts


def test_verb_plant_imperative_pattern(words, verb_candidates, plants):
    """
    Test pattern: VERB + [plant]
    Example: "take oak", "boil oat"

    This is imperative/command form common in recipes
    """
    pattern_counts = defaultdict(
        lambda: {
            "total": 0,
            "examples": [],
            "after_period_like": 0,  # Start of instruction
        }
    )

    # Words that might indicate sentence boundaries
    period_like = {".", "daiin", "aiin"}  # Pronouns often start new thoughts

    for i in range(len(words) - 1):
        word = words[i]

        if word in verb_candidates:
            word_after = words[i + 1]

            # Check if plant after
            if word_after in plants:
                pattern_counts[word]["total"] += 1

                # Check if this appears to be start of instruction
                if i == 0 or words[i - 1] in period_like:
                    pattern_counts[word]["after_period_like"] += 1

                if len(pattern_counts[word]["examples"]) < 10:
                    # Get context
                    before = words[i - 1] if i > 0 else "[START]"
                    pattern_counts[word]["examples"].append(
                        f"{before} | {word} {word_after}"
                    )

    return pattern_counts


def test_plant_verb_pattern(words, verb_candidates, plants):
    """
    Test pattern: [plant] + VERB
    Example: "oak grows", "oat boils"

    Less common in recipes but possible for process descriptions
    """
    pattern_counts = defaultdict(lambda: {"total": 0, "examples": []})

    for i in range(1, len(words)):
        word = words[i]

        if word in verb_candidates:
            word_before = words[i - 1]

            # Check if plant before
            if word_before in plants:
                pattern_counts[word]["total"] += 1

                if len(pattern_counts[word]["examples"]) < 10:
                    word_after = words[i + 1] if i < len(words) - 1 else "[END]"
                    pattern_counts[word]["examples"].append(
                        f"{word_before} {word} | {word_after}"
                    )

    return pattern_counts


def calculate_section_distribution(words, verb_candidates):
    """
    Calculate which sections have highest density of verb candidates

    Recipes should have high verb density (instructions)
    Herbal might have lower (descriptions)
    """
    # Rough section boundaries (based on ~37k words)
    sections = {
        "herbal": (0, 20000),  # f1r-f66v (herbal illustrations)
        "biological": (20000, 25000),  # f75r-f84v (baths/biological)
        "pharmaceutical": (25000, 32000),  # f87r-f102v (pharmaceutical jars)
        "recipes": (32000, 37187),  # f103r-f116v (text-heavy recipes)
    }

    section_counts = defaultdict(lambda: {"total_words": 0, "verb_words": 0})

    for i, word in enumerate(words):
        for section_name, (start, end) in sections.items():
            if start <= i < end:
                section_counts[section_name]["total_words"] += 1

                if word in verb_candidates:
                    section_counts[section_name]["verb_words"] += 1

                break

    # Calculate densities
    for section_name in section_counts:
        total = section_counts[section_name]["total_words"]
        verb = section_counts[section_name]["verb_words"]
        section_counts[section_name]["density"] = (
            (verb / total * 100) if total > 0 else 0
        )

    return section_counts


def analyze_verb_object_contexts(words, verb_candidates, plants):
    """
    Analyze what words appear AFTER verb candidates

    If these are verbs, we should see:
    - Plants (objects: "take oak")
    - Pronouns (objects: "take it")
    - Other object-like words
    """
    after_contexts = defaultdict(Counter)

    for i in range(len(words) - 1):
        word = words[i]

        if word in verb_candidates:
            word_after = words[i + 1]
            after_contexts[word][word_after] += 1

    # Analyze: what percentage are plants vs other
    analysis = {}

    for verb in verb_candidates:
        total = sum(after_contexts[verb].values())
        plant_count = sum(
            count for word, count in after_contexts[verb].items() if word in plants
        )

        top_5 = after_contexts[verb].most_common(5)

        analysis[verb] = {
            "total_contexts": total,
            "plant_objects": plant_count,
            "plant_rate": (plant_count / total * 100) if total > 0 else 0,
            "top_following_words": [{"word": w, "count": c} for w, c in top_5],
        }

    return analysis


def main():
    print("=" * 80)
    print("TESTING VERBAL HYPOTHESIS FOR CHEDY/SHEDY/QOKEDY")
    print("=" * 80)
    print()

    # Load data
    print("Loading manuscript...")
    words = load_manuscript()
    plants = load_plant_variants()
    pronouns = load_pronouns()

    verb_candidates = {"chedy", "shedy", "qokedy", "qokeedy", "qokeey"}

    print(f"Total words: {len(words):,}")
    print(f"Plant variants: {len(plants)}")
    print(f"Pronouns: {len(pronouns)}")
    print(f"Verb candidates: {len(verb_candidates)}")
    print()

    # Test 1: Pronoun + Verb + Plant
    print("=" * 80)
    print("TEST 1: [PRONOUN] + VERB + [PLANT] PATTERN")
    print("=" * 80)
    print("Expected: If these are verbs, should see 'it VERB oak' patterns")
    print()

    pronoun_verb_plant = test_verb_pronoun_plant_pattern(
        words, verb_candidates, pronouns, plants
    )

    for verb in verb_candidates:
        data = pronoun_verb_plant[verb]
        print(f"{verb:15} {data['total']:4} instances")
        if data["examples"]:
            print(f"  Examples: {', '.join(data['examples'][:3])}")
    print()

    # Test 2: Verb + Plant (imperative)
    print("=" * 80)
    print("TEST 2: VERB + [PLANT] PATTERN (Imperative)")
    print("=" * 80)
    print("Expected: Recipe instructions like 'take oak', 'boil oat'")
    print()

    verb_plant = test_verb_plant_imperative_pattern(words, verb_candidates, plants)

    for verb in sorted(
        verb_candidates, key=lambda v: verb_plant[v]["total"], reverse=True
    ):
        data = verb_plant[verb]
        imperative_rate = (
            (data["after_period_like"] / data["total"] * 100)
            if data["total"] > 0
            else 0
        )

        print(
            f"{verb:15} {data['total']:4} instances ({imperative_rate:.1f}% at instruction start)"
        )
        if data["examples"]:
            print(f"  Examples:")
            for ex in data["examples"][:3]:
                print(f"    {ex}")
    print()

    # Test 3: Plant + Verb
    print("=" * 80)
    print("TEST 3: [PLANT] + VERB PATTERN")
    print("=" * 80)
    print("Expected: Less common, but possible for process descriptions")
    print()

    plant_verb = test_plant_verb_pattern(words, verb_candidates, plants)

    for verb in sorted(
        verb_candidates, key=lambda v: plant_verb[v]["total"], reverse=True
    ):
        data = plant_verb[verb]
        print(f"{verb:15} {data['total']:4} instances")
        if data["examples"]:
            print(f"  Examples:")
            for ex in data["examples"][:3]:
                print(f"    {ex}")
    print()

    # Test 4: Section distribution
    print("=" * 80)
    print("TEST 4: SECTION DISTRIBUTION")
    print("=" * 80)
    print("Expected: High density in recipes (instruction-heavy)")
    print()

    section_dist = calculate_section_distribution(words, verb_candidates)

    print(f"{'Section':<20} {'Words':<10} {'Verbs':<10} {'Density':<10}")
    print("-" * 60)
    for section in ["herbal", "biological", "pharmaceutical", "recipes"]:
        data = section_dist[section]
        print(
            f"{section:<20} {data['total_words']:<10,} {data['verb_words']:<10} {data['density']:.2f}%"
        )
    print()

    # Test 5: Object analysis
    print("=" * 80)
    print("TEST 5: VERB OBJECT ANALYSIS")
    print("=" * 80)
    print("Expected: Verbs should be followed by objects (plants, pronouns, etc)")
    print()

    object_analysis = analyze_verb_object_contexts(words, verb_candidates, plants)

    for verb in sorted(
        verb_candidates, key=lambda v: object_analysis[v]["plant_rate"], reverse=True
    ):
        data = object_analysis[verb]
        print(f"\n{verb}:")
        print(f"  Total contexts: {data['total_contexts']}")
        print(f"  Plant objects: {data['plant_objects']} ({data['plant_rate']:.1f}%)")
        print(f"  Top following words:")
        for item in data["top_following_words"]:
            is_plant = " [PLANT]" if item["word"] in plants else ""
            print(f"    {item['word']:15} {item['count']:4}×{is_plant}")

    print()
    print("=" * 80)
    print("HYPOTHESIS EVALUATION")
    print("=" * 80)
    print()

    # Calculate overall statistics
    total_pronoun_verb_plant = sum(
        pronoun_verb_plant[v]["total"] for v in verb_candidates
    )
    total_verb_plant = sum(verb_plant[v]["total"] for v in verb_candidates)
    total_plant_verb = sum(plant_verb[v]["total"] for v in verb_candidates)

    avg_plant_obj_rate = sum(
        object_analysis[v]["plant_rate"] for v in verb_candidates
    ) / len(verb_candidates)

    recipe_density = section_dist["recipes"]["density"]
    herbal_density = section_dist["herbal"]["density"]
    enrichment = recipe_density / herbal_density if herbal_density > 0 else 0

    print(f"Pattern Evidence:")
    print(f"  [pronoun] VERB [plant]: {total_pronoun_verb_plant} instances")
    print(f"  VERB [plant]:          {total_verb_plant} instances")
    print(f"  [plant] VERB:          {total_plant_verb} instances")
    print(f"  Avg plant object rate:  {avg_plant_obj_rate:.1f}%")
    print()
    print(f"Section Distribution:")
    print(f"  Recipe section density: {recipe_density:.2f}%")
    print(f"  Herbal section density: {herbal_density:.2f}%")
    print(f"  Enrichment ratio:       {enrichment:.2f}x")
    print()

    # Verdict
    if total_verb_plant > 50 and recipe_density > herbal_density * 1.5:
        verdict = "STRONGLY SUPPORTED"
        interpretation = "These words show strong verb-like behavior"
    elif total_verb_plant > 20 and recipe_density > herbal_density:
        verdict = "SUPPORTED"
        interpretation = "These words likely function as verbs"
    else:
        verdict = "INCONCLUSIVE"
        interpretation = "Mixed evidence, needs further analysis"

    print(f"Verbal Hypothesis: {verdict}")
    print(f"Interpretation: {interpretation}")
    print()

    # Save results
    results = {
        "verb_candidates": list(verb_candidates),
        "patterns": {
            "pronoun_verb_plant": {k: v for k, v in pronoun_verb_plant.items()},
            "verb_plant_imperative": {k: v for k, v in verb_plant.items()},
            "plant_verb": {k: v for k, v in plant_verb.items()},
        },
        "section_distribution": {k: dict(v) for k, v in section_dist.items()},
        "object_analysis": object_analysis,
        "verdict": verdict,
        "interpretation": interpretation,
        "statistics": {
            "total_pronoun_verb_plant": total_pronoun_verb_plant,
            "total_verb_plant": total_verb_plant,
            "total_plant_verb": total_plant_verb,
            "avg_plant_object_rate": avg_plant_obj_rate,
            "recipe_enrichment": enrichment,
        },
    }

    output_path = Path("results/phase4/verbal_hypothesis_test.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
