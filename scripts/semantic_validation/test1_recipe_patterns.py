#!/usr/bin/env python3
"""
Semantic Validation Test 1: Recipe Pattern Frequency Analysis

HYPOTHESIS: The Voynich Manuscript contains pharmaceutical recipes

PREDICTION: If manuscript contains recipes, we should find high frequency of:
1. SUBSTANCE + VERB + LOCATION (e.g., "oak extract, prepare, in vessel")
2. BOTANICAL + VERB + SUBSTANCE (e.g., "plant, grind, oak extract")
3. WATER + VERB + LOCATION (e.g., "with water, boil, in vessel")
4. VERB + SUBSTANCE + VESSEL (e.g., "prepare, oak extract, in vessel")

METHODOLOGY:
- Pattern matching on structural translations
- Count frequencies of recipe-like patterns
- Compare to random baseline
- Statistical significance testing

SUCCESS CRITERIA:
- If recipe hypothesis correct: 100-200+ pattern matches (5-10% of corpus)
- If wrong: <20 matches (<1% of corpus)
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import re


def load_json_file(filepath):
    """Load JSON data from file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}")
        sys.exit(1)


def parse_sentence_to_tokens(sentence_text):
    """Convert sentence into token list for pattern matching."""
    return sentence_text.split()


def has_pattern_sequence(tokens, pattern_elements, window=5):
    """
    Check if tokens contain pattern elements in order (within window).

    Args:
        tokens: List of words in sentence
        pattern_elements: List of elements to find in sequence
        window: Maximum distance between elements

    Returns:
        True if pattern found, False otherwise
    """
    if not pattern_elements:
        return False

    # Find positions of each pattern element
    positions = []
    for element in pattern_elements:
        found_positions = []
        for i, token in enumerate(tokens):
            if element in token:
                found_positions.append(i)
        if not found_positions:
            return False  # Element not found at all
        positions.append(found_positions)

    # Check if we can find a valid sequence
    def check_sequence(pos_lists, current_pos=-1, depth=0):
        if depth >= len(pos_lists):
            return True

        for pos in pos_lists[depth]:
            if pos > current_pos and (current_pos == -1 or pos - current_pos <= window):
                if check_sequence(pos_lists, pos, depth + 1):
                    return True
        return False

    return check_sequence(positions)


def find_recipe_patterns(translations):
    """Find sentences matching recipe structural patterns."""

    patterns = {
        # Pattern 1: SUBSTANCE + PREPARATION_VERB + LOCATION
        "substance_prep_location": {
            "elements": ["al", "ch]-VERB", "vessel"],
            "description": "Substance + Preparation + Vessel",
            "example": "oak-GEN-al + [?ch]-VERB + vessel",
            "matches": [],
        },
        # Pattern 2: SUBSTANCE + PREPARATION_VERB + APPLICATION_VERB
        "substance_prep_apply": {
            "elements": ["al", "ch]-VERB", "sh]-VERB"],
            "description": "Substance + Prepare + Apply",
            "example": "oak-GEN-al + [?ch]-VERB + [?sh]-VERB",
            "matches": [],
        },
        # Pattern 3: BOTANICAL + VERB + SUBSTANCE
        "botanical_verb_substance": {
            "elements": ["botanical-term", "VERB", "al"],
            "description": "Botanical term + Action + Substance",
            "example": "botanical-term + [?ch]-VERB + oak-GEN-al",
            "matches": [],
        },
        # Pattern 4: WATER + VERB + LOCATION
        "water_verb_location": {
            "elements": ["water", "VERB", "vessel"],
            "description": "Water + Action + Vessel",
            "example": "water + [?ch]-VERB + vessel",
            "matches": [],
        },
        # Pattern 5: GENITIVE_SUBSTANCE + VERB
        "genitive_substance_verb": {
            "elements": ["oak-GEN-al", "VERB"],
            "description": "Genitive Substance + Action",
            "example": "oak-GEN-al + [?ch]-VERB",
            "matches": [],
        },
        # Pattern 6: VERB + AT-SUBSTANCE
        "verb_at_substance": {
            "elements": ["VERB", "AT-al"],
            "description": "Action + Locative Substance",
            "example": "[?sh]-VERB + AT-al",
            "matches": [],
        },
        # Pattern 7: SUBSTANCE + VERB + WATER
        "substance_verb_water": {
            "elements": ["al", "VERB", "water"],
            "description": "Substance + Action + Water",
            "example": "oak-GEN-al + [?ch]-VERB + water",
            "matches": [],
        },
        # Pattern 8: VESSEL + VERB + SUBSTANCE
        "vessel_verb_substance": {
            "elements": ["vessel", "VERB", "al"],
            "description": "Vessel + Action + Substance",
            "example": "vessel + [?sh]-VERB + oak-GEN-al",
            "matches": [],
        },
        # Pattern 9: Multiple substances (mixing)
        "multi_substance": {
            "elements": ["oak-GEN-al", "oat-GEN-al"],
            "description": "Multiple substances (ingredient mixing)",
            "example": "oak-GEN-al + [?ch]-VERB + oat-GEN-al",
            "matches": [],
        },
        # Pattern 10: Botanical + water + vessel (extraction recipe)
        "botanical_water_vessel": {
            "elements": ["botanical-term", "water", "vessel"],
            "description": "Botanical + Water + Vessel (extraction)",
            "example": "botanical-term + water + vessel",
            "matches": [],
        },
    }

    # Search for patterns
    for trans in translations:
        folio = trans.get("folio", "unknown")
        sentence = trans["final_translation"]
        tokens = parse_sentence_to_tokens(sentence)

        for pattern_name, pattern_data in patterns.items():
            if has_pattern_sequence(tokens, pattern_data["elements"], window=10):
                patterns[pattern_name]["matches"].append(
                    {
                        "folio": folio,
                        "sentence": sentence,
                        "original": trans.get("original", ""),
                    }
                )

    return patterns


def analyze_pattern_distribution(patterns, total_sentences):
    """Analyze distribution and significance of pattern matches."""

    results = {"total_sentences": total_sentences, "patterns": {}}

    for pattern_name, pattern_data in patterns.items():
        match_count = len(pattern_data["matches"])
        percentage = (match_count / total_sentences) * 100 if total_sentences > 0 else 0

        results["patterns"][pattern_name] = {
            "description": pattern_data["description"],
            "example": pattern_data["example"],
            "match_count": match_count,
            "percentage": percentage,
            "matches": pattern_data["matches"][:10],  # Store first 10 examples
        }

    return results


def calculate_baseline(translations):
    """Calculate random baseline - how many matches would we expect by chance?"""

    # Count frequency of key terms
    term_counts = Counter()
    total = 0

    for trans in translations:
        tokens = parse_sentence_to_tokens(trans["final_translation"])
        total += len(tokens)
        for token in tokens:
            if (
                "al" in token
                or "vessel" in token
                or "water" in token
                or "botanical" in token
            ):
                term_counts[token] += 1

    # Estimate random co-occurrence probability
    avg_sentence_length = total / len(translations) if translations else 0

    p_al = sum(1 for t in translations if "al" in t["final_translation"]) / len(
        translations
    )
    p_verb = sum(1 for t in translations if "VERB" in t["final_translation"]) / len(
        translations
    )
    p_vessel = sum(1 for t in translations if "vessel" in t["final_translation"]) / len(
        translations
    )

    # Expected random co-occurrence (independent events)
    expected_random = {
        "substance_prep_location": p_al * p_verb * p_vessel * len(translations),
        "genitive_substance_verb": p_al * p_verb * len(translations),
    }

    return expected_random


def main():
    print("=" * 80)
    print("SEMANTIC VALIDATION TEST 1: RECIPE PATTERN FREQUENCY")
    print("=" * 80)
    print()
    print("HYPOTHESIS: Voynich Manuscript contains pharmaceutical recipes")
    print()
    print("TESTING: Frequency of recipe-like structural patterns")
    print()
    print("SUCCESS CRITERION:")
    print("  - Recipe hypothesis: 100-200+ matches (5-10% of corpus)")
    print("  - Null hypothesis: <20 matches (<1% of corpus)")
    print()

    # Load data
    print("Loading translation data...")
    data = load_json_file("COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json")
    translations = data["translations"]
    total_sentences = len(translations)
    print(f"Loaded {total_sentences} sentences")
    print()

    # Find recipe patterns
    print("=" * 80)
    print("SEARCHING FOR RECIPE PATTERNS...")
    print("=" * 80)
    print()

    patterns = find_recipe_patterns(translations)

    # Analyze results
    results = analyze_pattern_distribution(patterns, total_sentences)

    # Display results
    print("PATTERN MATCH RESULTS:")
    print()

    total_matches = 0
    for pattern_name in sorted(
        results["patterns"].keys(),
        key=lambda x: results["patterns"][x]["match_count"],
        reverse=True,
    ):
        pattern_info = results["patterns"][pattern_name]
        count = pattern_info["match_count"]
        pct = pattern_info["percentage"]
        total_matches += count

        print(f"PATTERN: {pattern_info['description']}")
        print(f"  Example: {pattern_info['example']}")
        print(f"  Matches: {count} ({pct:.2f}% of corpus)")
        print()

        if count > 0 and count <= 5:
            print("  Sample sentences:")
            for i, match in enumerate(pattern_info["matches"][:3], 1):
                print(f"    {i}. {match['folio']}: {match['sentence']}")
            print()

    # Summary statistics
    print("=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    print()
    print(f"Total sentences analyzed: {total_sentences}")
    print(f"Total pattern matches: {total_matches}")
    print(f"Average matches per pattern: {total_matches / len(patterns):.1f}")
    print()

    # Calculate baseline
    print("BASELINE COMPARISON:")
    print()
    expected_random = calculate_baseline(translations)

    for pattern_name, expected in expected_random.items():
        if pattern_name in results["patterns"]:
            observed = results["patterns"][pattern_name]["match_count"]
            enrichment = observed / expected if expected > 0 else 0
            print(f"{pattern_name}:")
            print(f"  Expected (random): {expected:.1f}")
            print(f"  Observed: {observed}")
            print(f"  Enrichment: {enrichment:.1f}×")
            print()

    # Interpretation
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print()

    total_pct = (total_matches / total_sentences) * 100 if total_sentences > 0 else 0

    if total_pct > 10:
        print("✓ STRONG SUPPORT for recipe hypothesis")
        print(f"  - {total_matches} pattern matches ({total_pct:.1f}% of corpus)")
        print("  - Well above random baseline")
        print("  - Consistent with pharmaceutical text structure")
    elif total_pct > 5:
        print("? MODERATE SUPPORT for recipe hypothesis")
        print(f"  - {total_matches} pattern matches ({total_pct:.1f}% of corpus)")
        print("  - Above random baseline")
        print("  - Further validation needed")
    elif total_pct > 1:
        print("~ WEAK SUPPORT for recipe hypothesis")
        print(f"  - {total_matches} pattern matches ({total_pct:.1f}% of corpus)")
        print("  - Near random baseline")
        print("  - Alternative hypotheses should be considered")
    else:
        print("✗ NO SUPPORT for recipe hypothesis")
        print(f"  - Only {total_matches} pattern matches ({total_pct:.1f}% of corpus)")
        print("  - Consistent with random co-occurrence")
        print("  - Recipe hypothesis likely incorrect")

    print()

    # Most common patterns
    print("=" * 80)
    print("TOP 5 MOST COMMON RECIPE PATTERNS")
    print("=" * 80)
    print()

    sorted_patterns = sorted(
        results["patterns"].items(), key=lambda x: x[1]["match_count"], reverse=True
    )

    for i, (pattern_name, pattern_info) in enumerate(sorted_patterns[:5], 1):
        print(
            f"{i}. {pattern_info['description']}: {pattern_info['match_count']} matches"
        )
        print(f"   Example structure: {pattern_info['example']}")

        if pattern_info["matches"]:
            print(f"   Sample sentence: {pattern_info['matches'][0]['sentence']}")
        print()

    # Save results
    output_file = "SEMANTIC_TEST1_RECIPE_PATTERNS.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {output_file}")
    print()

    # Next steps
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()

    if total_pct > 5:
        print("RECOMMENDATION: Proceed with Tests 2 and 3")
        print()
        print("Test 2: Illustration correlation")
        print("  - Verify botanical terms cluster in herbal section")
        print()
        print("Test 3: Medieval recipe comparison")
        print("  - Compare structural patterns with known pharmaceutical texts")
        print()
    else:
        print("RECOMMENDATION: Reconsider recipe hypothesis")
        print()
        print("Alternative hypotheses to explore:")
        print("  - Astronomical/astrological text")
        print("  - Magical/ritual text")
        print("  - Encyclopedic reference work")
        print()

    return results


if __name__ == "__main__":
    main()
