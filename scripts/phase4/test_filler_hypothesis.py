"""
Filler Word Hypothesis
======================

Test: Are many "words" actually filler/noise?

Patterns suggesting fillers:
1. Exact immediate repetitions (chekaiin chekaiin)
2. Very short words (y, dy, ky, or)
3. High frequency but no clear grammatical function
4. Break up otherwise sensible structure

Test approach:
1. Identify potential fillers by frequency + length + repetition
2. Re-analyze sentences with fillers removed
3. Check if structure becomes clearer
4. Compare before/after parsing quality
"""

import json
from pathlib import Path
from collections import Counter


def load_manuscript():
    """Load manuscript"""
    transcription_path = Path(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt"
    )

    with open(transcription_path, "r", encoding="utf-8") as f:
        text = f.read()

    words = text.lower().split()
    return words


def identify_potential_fillers(words):
    """
    Identify words that might be fillers based on:
    - Very short (1-2 chars)
    - Very high frequency
    - Often repeated immediately
    - No clear grammatical pattern
    """
    freq = Counter(words)

    # Immediate repetitions
    repetitions = Counter()
    for i in range(len(words) - 1):
        if words[i] == words[i + 1]:
            repetitions[words[i]] += 1

    potential_fillers = set()

    # Criterion 1: Very short + high frequency
    for word, count in freq.items():
        if len(word) <= 2 and count > 50:
            potential_fillers.add(word)

    # Criterion 2: High repetition rate
    for word, rep_count in repetitions.most_common(50):
        if rep_count >= 3:  # Repeats at least 3 times
            potential_fillers.add(word)

    # Criterion 3: Common "connector" words that might be fillers
    # (based on previous analysis showing these everywhere)
    suspect_fillers = {"y", "dy", "ky", "ly", "or", "ar", "al", "ol", "s", "d", "t"}

    # But keep validated grammatical elements
    validated_grammar = {"daiin", "aiin", "saiin"}  # Pronouns we know are real

    fillers = (potential_fillers | suspect_fillers) - validated_grammar

    return fillers, freq, repetitions


def remove_fillers_from_sentence(sentence, fillers):
    """Remove filler words from sentence"""
    return [w for w in sentence if w not in fillers]


def parse_sentence_simple(sentence):
    """
    Simple parsing with validated components only
    """
    parsed = []

    for word in sentence:
        # Pronouns
        if word in ["daiin", "aiin", "saiin"]:
            parsed.append("PRO")
        # Known verbs
        elif word in ["chedy", "shedy"] or word.endswith("edy"):
            parsed.append("VRB")
        # Oak/oat + case
        elif ("ok" in word or "ot" in word) and any(
            word.endswith(c) for c in ["al", "ar", "ol", "or"]
        ):
            parsed.append("NOUN+CASE")
        # Just case marker
        elif any(word.endswith(c) for c in ["al", "ar", "ol", "or"]):
            parsed.append("?+CASE")
        # Genitive prefix
        elif word.startswith("qok") or word.startswith("qot"):
            parsed.append("GEN+?")
        else:
            parsed.append("?")

    return parsed


def main():
    print("=" * 80)
    print("FILLER WORD HYPOTHESIS TEST")
    print("=" * 80)
    print()

    # Load manuscript
    words = load_manuscript()
    print(f"Total words: {len(words):,}")
    print()

    # Identify fillers
    print("Identifying potential filler words...")
    fillers, freq, repetitions = identify_potential_fillers(words)

    print(f"Potential fillers identified: {len(fillers)}")
    print()

    print("Top potential fillers:")
    for word in sorted(fillers, key=lambda w: freq[w], reverse=True)[:20]:
        rep_count = repetitions.get(word, 0)
        print(f"  {word:<10} {freq[word]:>6}× (repeats immediately: {rep_count}×)")

    print()

    # Calculate filler density
    filler_instances = sum(1 for w in words if w in fillers)
    filler_density = filler_instances / len(words) * 100

    print(f"Filler density: {filler_density:.1f}% of manuscript")
    print()

    # Load previous parsing results
    prev_results_path = Path("results/phase4/sentence_level_parsing_f84v.json")
    with open(prev_results_path, "r") as f:
        prev_results = json.load(f)

    print("=" * 80)
    print("RE-ANALYSIS WITH FILLERS REMOVED")
    print("=" * 80)
    print()

    improvements = []

    for i, sent_data in enumerate(prev_results["sentences_analyzed"][:10], 1):
        original_sentence = sent_data["sentence"].split()
        filtered_sentence = remove_fillers_from_sentence(original_sentence, fillers)

        if len(filtered_sentence) == 0:
            continue

        print(f"SENTENCE {i}")
        print("-" * 80)
        print(f"Original ({len(original_sentence)} words):")
        print(f"  {' '.join(original_sentence)}")
        print()
        print(
            f"Filtered ({len(filtered_sentence)} words, removed {len(original_sentence) - len(filtered_sentence)}):"
        )
        print(f"  {' '.join(filtered_sentence)}")
        print()

        # Parse both versions
        original_structure = parse_sentence_simple(original_sentence)
        filtered_structure = parse_sentence_simple(filtered_sentence)

        # Calculate known ratio
        original_known = (
            sum(1 for s in original_structure if s != "?") / len(original_structure)
            if original_structure
            else 0
        )
        filtered_known = (
            sum(1 for s in filtered_structure if s != "?") / len(filtered_structure)
            if filtered_structure
            else 0
        )

        print(f"Original structure: {' '.join(original_structure)}")
        print(f"  Known: {original_known:.1%}")
        print()
        print(f"Filtered structure: {' '.join(filtered_structure)}")
        print(f"  Known: {filtered_known:.1%}")
        print()

        improvement = filtered_known - original_known
        improvements.append(
            {
                "sentence_num": i,
                "original_known": original_known,
                "filtered_known": filtered_known,
                "improvement": improvement,
                "words_removed": len(original_sentence) - len(filtered_sentence),
            }
        )

        if improvement > 0:
            print(f"✓ Improvement: +{improvement:.1%} known elements")
        else:
            print(f"  No improvement")
        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    avg_improvement = (
        sum(imp["improvement"] for imp in improvements) / len(improvements)
        if improvements
        else 0
    )
    avg_words_removed = (
        sum(imp["words_removed"] for imp in improvements) / len(improvements)
        if improvements
        else 0
    )

    sentences_improved = sum(1 for imp in improvements if imp["improvement"] > 0)

    print(f"Average improvement: {avg_improvement:.1%}")
    print(f"Average words removed: {avg_words_removed:.1f} per sentence")
    print(f"Sentences improved: {sentences_improved}/{len(improvements)}")
    print()

    if avg_improvement > 0.1:
        print("✓✓✓ FILLER HYPOTHESIS STRONGLY SUPPORTED")
        print()
        print(f"Removing {filler_density:.1f}% of words as fillers")
        print("significantly improves parsing quality.")
        print()
        print("Identified fillers:")
        for word in sorted(fillers, key=lambda w: freq[w], reverse=True)[:15]:
            print(f"  {word}")
        print()
        print("RECOMMENDATION: Re-run all analyses with filler filtering")
    elif avg_improvement > 0:
        print("~ FILLER HYPOTHESIS PARTIALLY SUPPORTED")
        print()
        print("Some improvement but not dramatic.")
        print("May need more refined filler identification.")
    else:
        print("✗ FILLER HYPOTHESIS NOT SUPPORTED")
        print()
        print("Removing suspected fillers doesn't improve parsing.")

    # Save results
    results = {
        "potential_fillers": list(fillers),
        "filler_density": filler_density,
        "improvements": improvements,
        "summary": {
            "avg_improvement": avg_improvement,
            "avg_words_removed": avg_words_removed,
            "sentences_improved": sentences_improved,
            "total_sentences": len(improvements),
        },
    }

    output_path = Path("results/phase4/filler_hypothesis_test.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print()
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
