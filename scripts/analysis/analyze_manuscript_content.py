#!/usr/bin/env python3
"""
Analyze the semantic content of the Voynich manuscript.
Goal: Understand WHAT the manuscript discusses, not just HOW it's structured.
"""

import json
import re
from collections import Counter, defaultdict


def load_translation_data():
    """Load the Phase 16 translation data."""
    with open(
        "COMPLETE_MANUSCRIPT_TRANSLATION_PHASE16.json", "r", encoding="utf-8"
    ) as f:
        return json.load(f)


def categorize_by_confidence(data):
    """Categorize translations by confidence level."""
    categories = {
        "perfect": [],  # 100%
        "excellent": [],  # 90-99%
        "good": [],  # 80-89%
        "moderate": [],  # 70-79%
    }

    for trans in data["translations"]:
        rec_rate = trans["statistics"]["recognition_rate"]
        if rec_rate == 100:
            categories["perfect"].append(trans)
        elif rec_rate >= 90:
            categories["excellent"].append(trans)
        elif rec_rate >= 80:
            categories["good"].append(trans)
        elif rec_rate >= 70:
            categories["moderate"].append(trans)

    return categories


def extract_semantic_elements(translation_text):
    """Extract semantic elements from a translation."""
    elements = {
        "morphemes": [],
        "roots": [],
        "prefixes": [],
        "suffixes": [],
        "function_words": [],
        "particles": [],
    }

    # Known prefixes
    prefixes = ["oak-GEN", "oat-GEN", "AT", "T"]
    # Known suffixes
    suffixes = ["LOC", "DIR", "INST", "VERB", "DEF", "D"]
    # Known function words
    function_words = [
        "THIS/THAT",
        "THERE",
        "OR",
        "AND",
        "THEN",
        "SKY",
        "DAR",
        "DOL",
        "MODAL",
        "PARTICLE",
    ]
    # Botanical/vessel terms
    special_terms = [
        "botanical-term",
        "vessel",
        "water",
        "red",
        "pharmaceutical-substance",
    ]

    words = translation_text.split()

    for word in words:
        # Check for function words
        if word in function_words:
            elements["function_words"].append(word)
        # Check for special terms
        elif word in special_terms:
            elements["function_words"].append(word)
        # Check for morphological structures
        elif "-" in word:
            parts = word.split("-")
            for part in parts:
                if part in prefixes:
                    elements["prefixes"].append(part)
                elif part in suffixes:
                    elements["suffixes"].append(part)
                else:
                    # Root or unknown element
                    if part.startswith("[") and part.endswith("]"):
                        elements["roots"].append(part)
        else:
            # Standalone function word
            if word not in ["[", "]"]:
                elements["function_words"].append(word)

    return elements


def find_common_patterns(translations, min_length=2, top_n=50):
    """Find common phrase patterns in translations."""
    phrase_counter = Counter()
    bigram_counter = Counter()
    trigram_counter = Counter()

    for trans in translations:
        text = trans["final_translation"]
        words = text.split()

        # Extract bigrams
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i + 1]}"
            bigram_counter[bigram] += 1

        # Extract trigrams
        for i in range(len(words) - 2):
            trigram = f"{words[i]} {words[i + 1]} {words[i + 2]}"
            trigram_counter[trigram] += 1

        # Extract longer phrases (4-5 words)
        for i in range(len(words) - 3):
            phrase = " ".join(words[i : i + 4])
            phrase_counter[phrase] += 1

    return {
        "bigrams": bigram_counter.most_common(top_n),
        "trigrams": trigram_counter.most_common(top_n),
        "phrases": phrase_counter.most_common(top_n),
    }


def analyze_semantic_fields(translations):
    """Identify semantic fields (topics) in the translations."""

    # Initialize counters for different semantic categories
    semantic_fields = {
        "spatial": Counter(),  # Location, direction
        "botanical": Counter(),  # Plant-related
        "temporal": Counter(),  # Time, sequence
        "actions": Counter(),  # Verbs
        "substances": Counter(),  # Materials, elements
        "deixis": Counter(),  # Pointing words (this/that)
    }

    # Keywords for each field
    spatial_keywords = ["LOC", "DIR", "AT", "THERE", "SKY", "AT-OL", "AT-AT/IN"]
    botanical_keywords = [
        "botanical-term",
        "vessel",
        "water",
        "pharmaceutical-substance",
    ]
    temporal_keywords = ["THEN", "VERB"]
    action_keywords = ["VERB", "INST"]
    substance_keywords = ["oak", "oat", "water", "red", "DOL", "DAR"]
    deixis_keywords = ["THIS/THAT", "THERE", "DEF"]

    for trans in translations:
        text = trans["final_translation"]

        # Count spatial markers
        for keyword in spatial_keywords:
            count = text.count(keyword)
            if count > 0:
                semantic_fields["spatial"][keyword] += count

        # Count botanical markers
        for keyword in botanical_keywords:
            count = text.count(keyword)
            if count > 0:
                semantic_fields["botanical"][keyword] += count

        # Count temporal markers
        for keyword in temporal_keywords:
            count = text.count(keyword)
            if count > 0:
                semantic_fields["temporal"][keyword] += count

        # Count action markers
        for keyword in action_keywords:
            count = text.count(keyword)
            if count > 0:
                semantic_fields["actions"][keyword] += count

        # Count substance markers
        for keyword in substance_keywords:
            count = text.count(keyword)
            if count > 0:
                semantic_fields["substances"][keyword] += count

        # Count deixis markers
        for keyword in deixis_keywords:
            count = text.count(keyword)
            if count > 0:
                semantic_fields["deixis"][keyword] += count

    return semantic_fields


def find_sentence_clusters(translations):
    """Group similar sentences together."""
    clusters = defaultdict(list)

    for trans in translations:
        text = trans["final_translation"]
        words = text.split()

        # Create a signature based on the structure
        # Replace unknown roots with placeholders
        signature_parts = []
        for word in words:
            if word.startswith("[?") and word.endswith("]"):
                signature_parts.append("[ROOT]")
            elif "-" in word:
                # Keep morphological structure
                parts = word.split("-")
                simplified = []
                for part in parts:
                    if part.startswith("[?") and part.endswith("]"):
                        simplified.append("[ROOT]")
                    else:
                        simplified.append(part)
                signature_parts.append("-".join(simplified))
            else:
                signature_parts.append(word)

        signature = " ".join(signature_parts)
        clusters[signature].append(
            {
                "folio": trans["folio"],
                "original": trans["original"],
                "translation": text,
            }
        )

    # Sort clusters by frequency
    sorted_clusters = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)

    return sorted_clusters


def main():
    import sys

    # Set UTF-8 encoding for output
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("VOYNICH MANUSCRIPT CONTENT ANALYSIS")
    print("=" * 80)
    print("Goal: Understand WHAT the manuscript discusses!\n")

    # Load data
    print("Loading translation data...")
    data = load_translation_data()

    # Categorize by confidence
    categories = categorize_by_confidence(data)

    print(f"Loaded {len(data['translations'])} total translations")
    print(f"  Perfect (100%): {len(categories['perfect'])}")
    print(f"  Excellent (90-99%): {len(categories['excellent'])}")
    print(f"  Good (80-89%): {len(categories['good'])}")
    print(f"  Moderate (70-79%): {len(categories['moderate'])}")
    print()

    # Focus on perfect + excellent translations (highest confidence)
    high_confidence = categories["perfect"] + categories["excellent"]
    print(f"Analyzing {len(high_confidence)} high-confidence translations...")
    print()

    # Find common patterns
    print("=" * 80)
    print("COMMON PHRASE PATTERNS")
    print("=" * 80)
    patterns = find_common_patterns(high_confidence)

    print("\nMost common BIGRAMS:")
    for i, (phrase, count) in enumerate(patterns["bigrams"][:20], 1):
        print(f"{i:2d}. {phrase:50s} ({count:3d}×)")

    print("\nMost common TRIGRAMS:")
    for i, (phrase, count) in enumerate(patterns["trigrams"][:20], 1):
        print(f"{i:2d}. {phrase:60s} ({count:3d}×)")

    print("\nMost common 4-WORD PHRASES:")
    for i, (phrase, count) in enumerate(patterns["phrases"][:20], 1):
        print(f"{i:2d}. {phrase:70s} ({count:2d}×)")

    # Analyze semantic fields
    print("\n" + "=" * 80)
    print("SEMANTIC FIELD ANALYSIS")
    print("=" * 80)
    fields = analyze_semantic_fields(high_confidence)

    for field_name, field_data in fields.items():
        print(f"\n{field_name.upper()} markers:")
        total = sum(field_data.values())
        print(f"  Total occurrences: {total}")
        for keyword, count in field_data.most_common(10):
            percentage = (count / total * 100) if total > 0 else 0
            print(f"    {keyword:20s}: {count:4d} ({percentage:5.1f}%)")

    # Find sentence clusters
    print("\n" + "=" * 80)
    print("SENTENCE STRUCTURE CLUSTERS")
    print("=" * 80)
    print("Grouping sentences with similar structures...\n")

    clusters = find_sentence_clusters(high_confidence)

    print(f"Found {len(clusters)} unique sentence structures")
    print("\nTop 10 most common sentence structures:\n")

    for i, (signature, examples) in enumerate(clusters[:10], 1):
        print(f"{i}. Structure (appears {len(examples)}× times):")
        print(f"   Pattern: {signature}")
        print(f"   Examples:")
        for j, ex in enumerate(examples[:3], 1):
            print(f"     {j}. [{ex['folio']}] {ex['original']}")
            print(f"        -> {ex['translation']}")
        print()

    # Extract most informative sentences
    print("=" * 80)
    print("MOST INFORMATIVE SENTENCES")
    print("=" * 80)
    print("Sentences with highest density of known vocabulary:\n")

    # Calculate information density
    scored_sentences = []
    for trans in high_confidence:
        text = trans["final_translation"]
        words = text.split()

        # Count known vs unknown elements
        known_count = 0
        for word in words:
            # Known = doesn't contain [?...]
            if "[?" not in word:
                known_count += 1

        density = (known_count / len(words) * 100) if len(words) > 0 else 0

        scored_sentences.append(
            {
                "folio": trans["folio"],
                "original": trans["original"],
                "translation": text,
                "density": density,
                "known_count": known_count,
                "total_words": len(words),
            }
        )

    # Sort by density
    scored_sentences.sort(key=lambda x: x["density"], reverse=True)

    print("Top 20 sentences with highest known vocabulary density:\n")
    for i, sent in enumerate(scored_sentences[:20], 1):
        print(
            f"{i:2d}. [{sent['folio']}] ({sent['density']:.1f}% known, {sent['known_count']}/{sent['total_words']} words)"
        )
        print(f"    Original:    {sent['original']}")
        print(f"    Translation: {sent['translation']}")
        print()

    print("=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)
    print("\nSummary written to: MANUSCRIPT_CONTENT_ANALYSIS.txt")


if __name__ == "__main__":
    main()
