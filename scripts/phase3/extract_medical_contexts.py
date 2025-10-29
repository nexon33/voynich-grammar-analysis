#!/usr/bin/env python3
"""
Extract medical terms with surrounding context from the translated Voynich manuscript.
This creates a focused reference file showing medical vocabulary in actual usage.
"""

import json
from pathlib import Path


def load_translation():
    """Load the full translation JSON."""
    json_path = (
        Path(__file__).parent.parent.parent
        / "results"
        / "phase3"
        / "full_manuscript_translation.json"
    )
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_contexts(translation_data, context_words=5):
    """Extract medical terms with surrounding context."""

    medical_contexts = {}

    for section in translation_data["sections"]:
        # Parse the original and translation strings
        original_words = section["original"].split()
        translated_words = section["translation"].split()

        # Get the section number from word_range
        section_num = section["section_id"]
        start_word = int(section["word_range"].split("-")[0])

        # Process each annotation
        for annotation in section["annotations"]:
            medical_tags = [
                tag for tag in annotation.get("tags", []) if tag.startswith("MED:")
            ]

            if medical_tags:
                # Find the position of this word in the section
                orig_word = annotation["original"]

                # Find all positions where this word appears
                for i, word in enumerate(original_words):
                    if word == orig_word:
                        # Extract context window
                        start_idx = max(0, i - context_words)
                        end_idx = min(len(translated_words), i + context_words + 1)

                        context_original = " ".join(original_words[start_idx:end_idx])
                        context_translated = " ".join(
                            translated_words[start_idx:end_idx]
                        )

                        # Mark the target word in context
                        trans_word = annotation["translation"]
                        context_translated_marked = " ".join(
                            translated_words[start_idx:i]
                            + [f"**{trans_word}**"]
                            + translated_words[i + 1 : end_idx]
                        )

                        # Store by medical term
                        term_key = trans_word.strip("[]?")
                        if term_key not in medical_contexts:
                            medical_contexts[term_key] = {
                                "category": medical_tags[0].split(":")[1],
                                "count": 0,
                                "contexts": [],
                            }

                        medical_contexts[term_key]["count"] += 1
                        medical_contexts[term_key]["contexts"].append(
                            {
                                "section": section_num,
                                "position": i + start_word,
                                "original_context": context_original,
                                "translated_context": context_translated_marked,
                                "confidence": annotation["confidence"],
                            }
                        )

    return medical_contexts


def write_context_file(medical_contexts, output_path):
    """Write medical terms with contexts to a readable file."""

    # Sort by frequency
    sorted_terms = sorted(
        medical_contexts.items(), key=lambda x: x[1]["count"], reverse=True
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Voynich Medical Terms in Context\n\n")
        f.write(
            "This file shows all identified medical terms with their surrounding context.\n"
        )
        f.write("Terms are sorted by frequency of occurrence.\n\n")
        f.write(f"Total unique medical terms: {len(medical_contexts)}\n")
        f.write(
            f"Total medical term occurrences: {sum(t['count'] for t in medical_contexts.values())}\n\n"
        )
        f.write("=" * 80 + "\n\n")

        for term, data in sorted_terms:
            f.write(f"## {term}\n")
            f.write(f"Category: {data['category']}\n")
            f.write(f"Occurrences: {data['count']}\n\n")

            # Show up to 10 contexts
            contexts_to_show = data["contexts"][:10]

            for ctx in contexts_to_show:
                f.write(
                    f"### Context {ctx['position']} (Section {ctx['section']}, Confidence: {ctx['confidence']})\n"
                )
                f.write(f"**Original:** {ctx['original_context']}\n")
                f.write(f"**Translated:** {ctx['translated_context']}\n\n")

            if len(data["contexts"]) > 10:
                f.write(f"... and {len(data['contexts']) - 10} more occurrences\n\n")

            f.write("-" * 80 + "\n\n")


def main():
    print("Loading translation data...")
    translation_data = load_translation()

    print("Extracting medical term contexts...")
    medical_contexts = extract_contexts(translation_data, context_words=5)

    print(f"Found {len(medical_contexts)} unique medical terms")
    print(f"Total occurrences: {sum(t['count'] for t in medical_contexts.values())}")

    output_path = (
        Path(__file__).parent.parent.parent
        / "results"
        / "phase3"
        / "medical_terms_in_context.txt"
    )
    print(f"Writing context file to {output_path}...")
    write_context_file(medical_contexts, output_path)

    print("Done!")

    # Show top 10 terms
    sorted_terms = sorted(
        medical_contexts.items(), key=lambda x: x[1]["count"], reverse=True
    )
    print("\nTop 10 most frequent medical terms:")
    for i, (term, data) in enumerate(sorted_terms[:10], 1):
        print(
            f"{i:2d}. {term:15s} ({data['category']:15s}) - {data['count']:3d} occurrences"
        )


if __name__ == "__main__":
    main()
