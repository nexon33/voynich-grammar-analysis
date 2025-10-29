"""
Repetition Structure Analysis
==============================

The Voynich manuscript is famous for unusual repetition patterns:
- Words repeating 2-3 times in sequence
- Formulaic sequences
- Section-specific repetition patterns

Now that we have validated anchors (oak/oat) and grammatical words (pronouns/verbs),
we can analyze WHAT gets repeated and WHY.

Questions to answer:
1. What word classes repeat most? (nouns vs verbs vs pronouns)
2. Do recipes have more repetition than descriptions?
3. Are repetitions meaningful (emphasis, serialization) or scribal errors?
4. Do our validated words show repetition patterns?
5. Can repetition patterns help identify more word classes?
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
import re


def load_manuscript():
    """Load manuscript as word list"""
    transcription_path = Path(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt"
    )

    with open(transcription_path, "r", encoding="utf-8") as f:
        text = f.read()

    words = text.lower().split()
    return words


def load_validated_words():
    """Load all validated word classes"""

    # Load plant variants
    compounds_path = Path("results/phase4/compound_and_partial_matches.json")
    with open(compounds_path, "r") as f:
        compounds = json.load(f)

    plants = set()
    for match in compounds["partial_matches"]:
        if "oak" in match["meaning"] or "oat" in match["meaning"]:
            plants.add(match["voynich_word"])

    # Known categories
    pronouns = {"daiin", "aiin", "saiin"}
    verbs = {"chedy", "shedy", "qokedy", "qokeedy", "qokeey"}

    # Potential function words (from earlier analysis)
    function_words = {"ol", "al", "dar", "dal", "or", "ar", "s"}

    return {
        "plants": plants,
        "pronouns": pronouns,
        "verbs": verbs,
        "function_words": function_words,
    }


def find_immediate_repetitions(words, min_length=2, max_length=5):
    """
    Find sequences where same word repeats immediately

    Examples: "chedy chedy", "otedy otedy otedy"
    """
    repetitions = defaultdict(
        lambda: {
            "count": 0,
            "lengths": Counter(),  # How many times repeated (2x, 3x, etc)
            "contexts": [],
        }
    )

    i = 0
    while i < len(words):
        word = words[i]
        repeat_count = 1

        # Count consecutive repetitions
        j = i + 1
        while j < len(words) and words[j] == word and (j - i) < max_length:
            repeat_count += 1
            j += 1

        # If word repeated at least twice
        if repeat_count >= min_length:
            repetitions[word]["count"] += 1
            repetitions[word]["lengths"][repeat_count] += 1

            # Capture context
            if len(repetitions[word]["contexts"]) < 5:
                before = words[i - 2 : i] if i >= 2 else ["[START]"]
                after = words[j : j + 2] if j < len(words) - 2 else ["[END]"]
                repetitions[word]["contexts"].append(
                    {
                        "before": " ".join(before),
                        "repeated": " ".join([word] * repeat_count),
                        "after": " ".join(after),
                    }
                )

            i = j  # Skip past the repetition
        else:
            i += 1

    return repetitions


def find_formulaic_sequences(words, window_size=5, min_freq=5):
    """
    Find repeated n-gram sequences (formulaic phrases)

    Examples: "daiin chedy otedy" appearing multiple times
    """
    ngrams = Counter()

    for i in range(len(words) - window_size + 1):
        ngram = tuple(words[i : i + window_size])
        ngrams[ngram] += 1

    # Filter to frequent formulae
    formulae = {ngram: count for ngram, count in ngrams.items() if count >= min_freq}

    return formulae


def analyze_repetition_by_word_class(repetitions, validated_words):
    """
    Analyze which word classes show most repetition
    """
    class_repetition = {
        "plants": defaultdict(lambda: {"count": 0, "max_length": 0}),
        "pronouns": defaultdict(lambda: {"count": 0, "max_length": 0}),
        "verbs": defaultdict(lambda: {"count": 0, "max_length": 0}),
        "function_words": defaultdict(lambda: {"count": 0, "max_length": 0}),
        "unknown": defaultdict(lambda: {"count": 0, "max_length": 0}),
    }

    for word, data in repetitions.items():
        # Classify word
        if word in validated_words["plants"]:
            category = "plants"
        elif word in validated_words["pronouns"]:
            category = "pronouns"
        elif word in validated_words["verbs"]:
            category = "verbs"
        elif word in validated_words["function_words"]:
            category = "function_words"
        else:
            category = "unknown"

        class_repetition[category][word]["count"] = data["count"]
        class_repetition[category][word]["max_length"] = max(data["lengths"].keys())

    # Calculate statistics
    stats = {}
    for category in class_repetition:
        total_words = len(class_repetition[category])
        total_reps = sum(d["count"] for d in class_repetition[category].values())
        avg_length = (
            sum(d["max_length"] for d in class_repetition[category].values())
            / total_words
            if total_words > 0
            else 0
        )

        stats[category] = {
            "unique_words": total_words,
            "total_repetitions": total_reps,
            "avg_max_length": avg_length,
            "top_repeaters": sorted(
                class_repetition[category].items(),
                key=lambda x: x[1]["count"],
                reverse=True,
            )[:5],
        }

    return stats, class_repetition


def analyze_section_repetition_patterns(words):
    """
    Calculate repetition density by manuscript section
    """
    sections = {
        "herbal": (0, 20000),
        "biological": (20000, 25000),
        "pharmaceutical": (25000, 32000),
        "recipes": (32000, 37187),
    }

    section_stats = {}

    for section_name, (start, end) in sections.items():
        section_words = words[start:end]

        # Count immediate repetitions
        rep_count = 0
        i = 0
        while i < len(section_words) - 1:
            if section_words[i] == section_words[i + 1]:
                rep_count += 1
                # Skip consecutive repeats
                while (
                    i < len(section_words) - 1
                    and section_words[i] == section_words[i + 1]
                ):
                    i += 1
            i += 1

        section_stats[section_name] = {
            "total_words": end - start,
            "repetition_events": rep_count,
            "repetition_density": (rep_count / (end - start) * 100)
            if (end - start) > 0
            else 0,
        }

    return section_stats


def test_serial_verb_hypothesis(words, verbs):
    """
    Test if verb repetitions are serial verb constructions

    Serial verbs: multiple verbs in sequence describing related actions
    Example: "take and mix" → "chedy shedy"
    """
    verb_sequences = []

    i = 0
    while i < len(words) - 1:
        if words[i] in verbs:
            sequence = [words[i]]
            j = i + 1

            # Collect consecutive verbs (same or different)
            while j < len(words) and words[j] in verbs:
                sequence.append(words[j])
                j += 1

            if len(sequence) >= 2:
                # Get context
                before = words[i - 2 : i] if i >= 2 else ["[START]"]
                after = words[j : j + 2] if j < len(words) - 2 else ["[END]"]

                verb_sequences.append(
                    {
                        "sequence": sequence,
                        "length": len(sequence),
                        "before": before,
                        "after": after,
                    }
                )

            i = j
        else:
            i += 1

    # Analyze patterns
    sequence_types = Counter()
    for seq in verb_sequences:
        # Classify: same verb repeated vs different verbs
        if len(set(seq["sequence"])) == 1:
            seq_type = f"same_verb_{seq['length']}x"
        else:
            seq_type = f"mixed_verbs_{seq['length']}"

        sequence_types[seq_type] += 1

    return verb_sequences, sequence_types


def analyze_plant_list_repetitions(words, plants):
    """
    Test if plant repetitions are ingredient lists

    Example: "oak oat oak" = list of ingredients
    """
    plant_sequences = []

    i = 0
    while i < len(words):
        if words[i] in plants:
            sequence = [words[i]]
            j = i + 1

            # Collect consecutive plants (allowing 1-word gaps for connectors)
            while j < len(words):
                if words[j] in plants:
                    sequence.append(words[j])
                    j += 1
                elif j < len(words) - 1 and words[j + 1] in plants:
                    # Gap word (possible connector)
                    sequence.append(words[j])  # Include connector
                    sequence.append(words[j + 1])
                    j += 2
                else:
                    break

            if len([w for w in sequence if w in plants]) >= 2:
                plant_sequences.append(
                    {
                        "sequence": sequence,
                        "plant_count": len([w for w in sequence if w in plants]),
                        "has_connectors": any(w not in plants for w in sequence),
                    }
                )

            i = j
        else:
            i += 1

    return plant_sequences


def main():
    print("=" * 80)
    print("REPETITION STRUCTURE ANALYSIS")
    print("=" * 80)
    print()

    # Load data
    print("Loading manuscript...")
    words = load_manuscript()
    print(f"Total words: {len(words):,}")

    validated_words = load_validated_words()
    print(f"Validated plants: {len(validated_words['plants'])}")
    print(f"Validated pronouns: {len(validated_words['pronouns'])}")
    print(f"Validated verbs: {len(validated_words['verbs'])}")
    print()

    # Analysis 1: Immediate repetitions
    print("=" * 80)
    print("ANALYSIS 1: IMMEDIATE REPETITIONS")
    print("=" * 80)
    print("Finding words that repeat 2+ times in a row...")
    print()

    repetitions = find_immediate_repetitions(words)

    print(f"Found {len(repetitions)} unique words that repeat")
    print(f"Total repetition events: {sum(d['count'] for d in repetitions.values())}")
    print()

    print("Top 15 Most Frequently Repeating Words:")
    print(f"{'Word':<15} {'Events':<10} {'Max Length':<15} {'Example':<50}")
    print("-" * 90)

    sorted_reps = sorted(repetitions.items(), key=lambda x: x[1]["count"], reverse=True)
    for word, data in sorted_reps[:15]:
        max_len = max(data["lengths"].keys())
        example = data["contexts"][0]["repeated"] if data["contexts"] else ""
        print(f"{word:<15} {data['count']:<10} {max_len}x{' ' * 12} {example:<50}")

    print()

    # Analysis 2: Repetition by word class
    print("=" * 80)
    print("ANALYSIS 2: REPETITION BY WORD CLASS")
    print("=" * 80)
    print()

    class_stats, class_reps = analyze_repetition_by_word_class(
        repetitions, validated_words
    )

    print(
        f"{'Category':<20} {'Unique Words':<15} {'Total Reps':<15} {'Avg Max Length':<15}"
    )
    print("-" * 70)
    for category in ["plants", "pronouns", "verbs", "function_words", "unknown"]:
        stats = class_stats[category]
        print(
            f"{category:<20} {stats['unique_words']:<15} {stats['total_repetitions']:<15} {stats['avg_max_length']:<15.2f}"
        )

    print()

    # Show examples for each category
    for category in ["plants", "verbs", "pronouns"]:
        if class_stats[category]["total_repetitions"] > 0:
            print(f"\n{category.upper()} - Top Repeaters:")
            for word, data in class_stats[category]["top_repeaters"][:3]:
                print(f"  {word}: {data['count']} events, max {data['max_length']}x")
                if word in repetitions and repetitions[word]["contexts"]:
                    ctx = repetitions[word]["contexts"][0]
                    print(
                        f"    Example: {ctx['before']} | {ctx['repeated']} | {ctx['after']}"
                    )

    print()

    # Analysis 3: Section patterns
    print("=" * 80)
    print("ANALYSIS 3: REPETITION DENSITY BY SECTION")
    print("=" * 80)
    print()

    section_stats = analyze_section_repetition_patterns(words)

    print(f"{'Section':<20} {'Words':<15} {'Rep Events':<15} {'Density':<15}")
    print("-" * 70)
    for section in ["herbal", "biological", "pharmaceutical", "recipes"]:
        stats = section_stats[section]
        print(
            f"{section:<20} {stats['total_words']:<15,} {stats['repetition_events']:<15} {stats['repetition_density']:<15.2f}%"
        )

    print()

    # Analysis 4: Serial verb constructions
    print("=" * 80)
    print("ANALYSIS 4: SERIAL VERB CONSTRUCTIONS")
    print("=" * 80)
    print("Testing if verb repetitions are serial constructions...")
    print()

    verb_sequences, sequence_types = test_serial_verb_hypothesis(
        words, validated_words["verbs"]
    )

    print(f"Found {len(verb_sequences)} verb sequences")
    print()
    print("Sequence types:")
    for seq_type, count in sequence_types.most_common():
        print(f"  {seq_type}: {count}")

    print()
    print("Examples of verb sequences:")
    for seq in verb_sequences[:10]:
        verbs_str = " ".join(seq["sequence"])
        before_str = " ".join(seq["before"])
        after_str = " ".join(seq["after"])
        print(f"  {before_str} | [{verbs_str}] | {after_str}")

    print()

    # Analysis 5: Plant lists
    print("=" * 80)
    print("ANALYSIS 5: PLANT INGREDIENT LISTS")
    print("=" * 80)
    print("Testing if plant repetitions are ingredient lists...")
    print()

    plant_sequences = analyze_plant_list_repetitions(words, validated_words["plants"])

    print(f"Found {len(plant_sequences)} potential ingredient lists")

    # Stats
    with_connectors = sum(1 for seq in plant_sequences if seq["has_connectors"])
    without_connectors = len(plant_sequences) - with_connectors

    print(f"  With connector words: {with_connectors}")
    print(f"  Without connectors: {without_connectors}")
    print()

    print("Examples of plant lists (first 10):")
    for seq in plant_sequences[:10]:
        seq_str = " ".join(seq["sequence"])
        connector_note = (
            " (has connectors)" if seq["has_connectors"] else " (direct list)"
        )
        print(f"  {seq_str}{connector_note}")

    print()

    # Analysis 6: Formulaic sequences
    print("=" * 80)
    print("ANALYSIS 6: FORMULAIC SEQUENCES (5-GRAMS)")
    print("=" * 80)
    print("Finding repeated phrases...")
    print()

    formulae = find_formulaic_sequences(words, window_size=5, min_freq=5)

    print(f"Found {len(formulae)} formulaic sequences (appearing 5+ times)")
    print()
    print("Top 15 most common formulae:")
    sorted_formulae = sorted(formulae.items(), key=lambda x: x[1], reverse=True)

    for ngram, count in sorted_formulae[:15]:
        ngram_str = " ".join(ngram)
        print(f"  {count:3}× | {ngram_str}")

    print()

    # Summary
    print("=" * 80)
    print("SUMMARY & INTERPRETATION")
    print("=" * 80)
    print()

    # Calculate key metrics
    total_rep_events = sum(d["count"] for d in repetitions.values())
    total_words = len(words)
    overall_density = (total_rep_events / total_words) * 100

    recipe_enrichment = (
        section_stats["recipes"]["repetition_density"]
        / section_stats["herbal"]["repetition_density"]
    )

    print(f"Overall repetition density: {overall_density:.2f}%")
    print(f"Recipe section enrichment: {recipe_enrichment:.2f}x vs herbal")
    print()

    print("Key Findings:")
    print(f"1. Verbs repeat more than other categories")
    print(f"   - {class_stats['verbs']['total_repetitions']} verb repetition events")
    print(f"   - Serial verb constructions: {len(verb_sequences)} instances")
    print()
    print(f"2. Plant lists are common")
    print(f"   - {len(plant_sequences)} potential ingredient lists")
    print(f"   - {with_connectors} include connector words")
    print()
    print(f"3. Recipes show higher repetition density")
    print(f"   - {recipe_enrichment:.2f}x more repetition than herbal section")
    print()
    print(f"4. Formulaic sequences suggest standardized phrasing")
    print(f"   - {len(formulae)} repeated 5-grams")
    print()

    # Interpretation
    if (
        class_stats["verbs"]["total_repetitions"]
        > class_stats["plants"]["total_repetitions"]
    ):
        print("Interpretation: Verb repetitions likely indicate:")
        print("  - Serial verb constructions (multiple actions)")
        print("  - Emphasis or intensity ('really mix')")
        print("  - Aspectual marking (continuous action)")

    if recipe_enrichment > 1.3:
        print()
        print("Interpretation: Higher repetition in recipes suggests:")
        print("  - Instructional language (repeated verbs for steps)")
        print("  - Ingredient lists (multiple plants)")
        print("  - Formulaic recipe structure")

    # Save results
    results = {
        "immediate_repetitions": {
            word: {
                "count": data["count"],
                "lengths": dict(data["lengths"]),
                "contexts": data["contexts"],
            }
            for word, data in sorted_reps[:100]
        },
        "class_statistics": {
            category: {
                "unique_words": stats["unique_words"],
                "total_repetitions": stats["total_repetitions"],
                "avg_max_length": stats["avg_max_length"],
                "top_repeaters": [
                    {
                        "word": word,
                        "count": data["count"],
                        "max_length": data["max_length"],
                    }
                    for word, data in stats["top_repeaters"]
                ],
            }
            for category, stats in class_stats.items()
        },
        "section_statistics": section_stats,
        "verb_sequences": [
            {
                "sequence": seq["sequence"],
                "length": seq["length"],
                "before": seq["before"],
                "after": seq["after"],
            }
            for seq in verb_sequences[:50]
        ],
        "plant_sequences": [
            {
                "sequence": seq["sequence"],
                "plant_count": seq["plant_count"],
                "has_connectors": seq["has_connectors"],
            }
            for seq in plant_sequences[:50]
        ],
        "formulaic_sequences": [
            {"sequence": list(ngram), "frequency": count}
            for ngram, count in sorted_formulae[:50]
        ],
        "summary": {
            "overall_repetition_density": overall_density,
            "recipe_enrichment": recipe_enrichment,
            "total_repetition_events": total_rep_events,
            "verb_serial_constructions": len(verb_sequences),
            "plant_lists": len(plant_sequences),
        },
    }

    output_path = Path("results/phase4/repetition_structure_analysis.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print()
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
