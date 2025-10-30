#!/usr/bin/env python3
"""
Phase 15B: Investigate chod, shee, tcho

All three scored 7/10 in Phase 11.
Following Phase 15A keol pattern, check if these are:
1. Compounds (like keol = ke + ol)
2. Allomorphs (like ot- ~ ol-)
3. Independent roots (genuine near-validated)
"""

import re
from collections import defaultdict, Counter
from pathlib import Path
import json

# Validated vocabulary for compound detection
VALIDATED_ROOTS = {
    "ok",
    "qok",
    "ot",
    "qot",
    "she",
    "shee",
    "cho",
    "cheo",
    "sho",
    "ke",
    "ol",
    "ain",
    "air",
    "dair",
    "ar",
    "okal",
    "or",
    "dol",
    "dar",
    "chol",
    "keo",
    "teo",
}

VALIDATED_SUFFIXES = [
    "al",
    "ol",
    "ar",
    "or",
    "dy",
    "edy",
    "ain",
    "iin",
    "aiin",
    "y",
    "ey",
    "d",
]
VALIDATED_PREFIXES = ["qok", "qot", "ol", "ot", "t", "ch", "sh"]


def load_sentences(filepath):
    """Load EVA file."""
    sentences = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Remove EVA markup
            text = re.sub(r"[!%=\-\*\{\}<>@,\.\d]", "", line)
            words = text.split()

            if words:
                sentences.append(words)

    return sentences


def analyze_element(element, sentences):
    """Analyze a single element for compound structure."""
    print(f"\n{'=' * 80}")
    print(f"ANALYZING: {element.upper()}")
    print(f"{'=' * 80}")

    # Find all instances
    instances = []
    contexts = []

    for sent in sentences:
        for word in sent:
            if element in word.lower():
                instances.append(word.lower())
                contexts.append(" ".join(sent))

    print(f"\nTotal instances: {len(instances)}")
    print(f"Unique forms: {len(set(instances))}")

    # Show frequency distribution
    freq = Counter(instances)
    print(f"\nTop 10 forms:")
    for form, count in freq.most_common(10):
        print(f"  {form}: {count}")

    # Check for compound patterns
    analysis = {
        "element": element,
        "total_instances": len(instances),
        "unique_forms": len(set(instances)),
        "frequency_distribution": dict(freq.most_common(20)),
        "compound_hypotheses": [],
    }

    # Hypothesis 1: PREFIX + element
    print(f"\n--- Hypothesis 1: PREFIX + {element} ---")
    for prefix in VALIDATED_PREFIXES:
        pattern = prefix + element
        matches = [w for w in instances if w.startswith(pattern)]
        if matches:
            print(f"  {prefix}-{element}: {len(matches)} instances")
            analysis["compound_hypotheses"].append(
                {
                    "type": "prefix_compound",
                    "structure": f"{prefix} + {element}",
                    "count": len(matches),
                    "examples": matches[:5],
                }
            )

    # Hypothesis 2: element + SUFFIX
    print(f"\n--- Hypothesis 2: {element} + SUFFIX ---")
    for suffix in VALIDATED_SUFFIXES:
        pattern = element + suffix
        exact_matches = [w for w in instances if w == pattern]
        if exact_matches:
            print(f"  {element}-{suffix}: {len(exact_matches)} instances")
            analysis["compound_hypotheses"].append(
                {
                    "type": "suffix_compound",
                    "structure": f"{element} + {suffix}",
                    "count": len(exact_matches),
                    "examples": exact_matches[:5],
                }
            )

    # Hypothesis 3: element = ROOT1 + ROOT2
    print(f"\n--- Hypothesis 3: {element} = ROOT + ROOT ---")
    for root in VALIDATED_ROOTS:
        if len(root) >= 2:  # Only check roots with 2+ letters
            if element.startswith(root) and len(element) > len(root):
                remainder = element[len(root) :]
                if remainder in VALIDATED_ROOTS or remainder in VALIDATED_SUFFIXES:
                    print(f"  {element} = {root} + {remainder}")
                    analysis["compound_hypotheses"].append(
                        {
                            "type": "root_compound",
                            "structure": f"{root} + {remainder}",
                            "count": len([w for w in instances if w == element]),
                            "validated": f"{root in VALIDATED_ROOTS}, {remainder in VALIDATED_ROOTS or remainder in VALIDATED_SUFFIXES}",
                        }
                    )

            if element.endswith(root) and len(element) > len(root):
                prefix_part = element[: -len(root)]
                if prefix_part in VALIDATED_ROOTS or prefix_part in VALIDATED_PREFIXES:
                    print(f"  {element} = {prefix_part} + {root}")
                    analysis["compound_hypotheses"].append(
                        {
                            "type": "root_compound",
                            "structure": f"{prefix_part} + {root}",
                            "count": len([w for w in instances if w == element]),
                            "validated": f"{prefix_part in VALIDATED_ROOTS or prefix_part in VALIDATED_PREFIXES}, {root in VALIDATED_ROOTS}",
                        }
                    )

    # Hypothesis 4: Allomorph of existing root
    print(f"\n--- Hypothesis 4: {element} as allomorph ---")
    for root in VALIDATED_ROOTS:
        if len(root) == len(element):
            # Check similarity (1-2 letter difference)
            diff_count = sum(1 for a, b in zip(element, root) if a != b)
            if 1 <= diff_count <= 2:
                print(f"  {element} ~ {root} ({diff_count} letter difference)")
                analysis["compound_hypotheses"].append(
                    {
                        "type": "allomorph",
                        "structure": f"{element} ~ {root}",
                        "similarity": f"{diff_count} letter difference",
                        "count": len([w for w in instances if w == element]),
                    }
                )

    # Co-occurrence analysis
    print(f"\n--- Co-occurrence with validated vocabulary ---")
    cooccurrence = Counter()

    for context in contexts:
        words = context.lower().split()
        for word in words:
            for validated in VALIDATED_ROOTS:
                if validated in word and element not in word:
                    cooccurrence[validated] += 1

    print(f"Top 10 co-occurring validated elements:")
    for validated, count in cooccurrence.most_common(10):
        print(f"  {validated}: {count}")

    analysis["cooccurrence"] = dict(cooccurrence.most_common(20))

    # Conclusion
    print(f"\n--- CONCLUSION for {element.upper()} ---")

    if analysis["compound_hypotheses"]:
        print(f"Found {len(analysis['compound_hypotheses'])} compound hypotheses:")
        for hyp in analysis["compound_hypotheses"]:
            print(f"  - {hyp['type']}: {hyp['structure']}")

        # Determine most likely hypothesis
        type_priority = {
            "root_compound": 1,
            "suffix_compound": 2,
            "prefix_compound": 3,
            "allomorph": 4,
        }
        best_hypothesis = min(
            analysis["compound_hypotheses"],
            key=lambda h: (type_priority.get(h["type"], 99), -h.get("count", 0)),
        )

        print(
            f"\nMost likely: {best_hypothesis['type']} → {best_hypothesis['structure']}"
        )
        analysis["recommendation"] = {
            "status": "COMPOUND or ALLOMORPH",
            "best_hypothesis": best_hypothesis,
        }
    else:
        print(f"No clear compound pattern found.")
        print(f"Recommendation: Investigate as potential independent root")
        analysis["recommendation"] = {
            "status": "INVESTIGATE AS INDEPENDENT ROOT",
            "note": "No compound structure detected",
        }

    return analysis


def main():
    # Paths
    script_dir = Path(__file__).parent
    manuscript_dir = script_dir.parent.parent
    eva_file = (
        manuscript_dir
        / "data"
        / "voynich"
        / "eva_transcription"
        / "voynich_eva_takahashi.txt"
    )
    output_file = manuscript_dir / "PHASE15B_MEDIUM_PRIORITY_ANALYSIS.json"

    if not eva_file.exists():
        print(f"Error: EVA file not found: {eva_file}")
        return

    print("Loading manuscript...")
    sentences = load_sentences(eva_file)
    print(f"Loaded {len(sentences)} sentences")

    # Elements to investigate
    elements = ["chod", "shee", "tcho"]

    results = {}

    for element in elements:
        analysis = analyze_element(element, sentences)
        results[element] = analysis

    # Summary
    print(f"\n{'=' * 80}")
    print("PHASE 15B SUMMARY")
    print(f"{'=' * 80}")

    for element, analysis in results.items():
        print(f"\n{element.upper()}:")
        print(f"  Total instances: {analysis['total_instances']}")
        print(f"  Compound hypotheses: {len(analysis['compound_hypotheses'])}")
        print(f"  Recommendation: {analysis['recommendation']['status']}")
        if "best_hypothesis" in analysis["recommendation"]:
            print(
                f"  Best hypothesis: {analysis['recommendation']['best_hypothesis']['structure']}"
            )

    # Save results
    print(f"\nSaving results to {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nPhase 15B complete! Results saved to:")
    print(f"  {output_file}")


if __name__ == "__main__":
    main()
