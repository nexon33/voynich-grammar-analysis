#!/usr/bin/env python3
"""
Phase 15A: Re-validate KEOL with Updated Vocabulary

Previously scored 7/10 in Phases 10-11 with 28-41 validated elements.
Now re-testing with 47 validated elements to see if co-occurrence improves.

Hypothesis: Increased vocabulary may push keol from 7/10 to 8/10.
"""

import re
from collections import defaultdict, Counter
from pathlib import Path
from scipy import stats
import json

# Updated validated vocabulary (47 elements)
VALIDATED_VOCABULARY = {
    # Prefixes (3)
    "qok",
    "qot",
    "ol",
    # Roots (30)
    "ok",
    "ot",
    "she",
    "shee",
    "dor",
    "cho",
    "cheo",
    "sho",
    "okal",
    "or",
    "dol",
    "dar",
    "chol",
    "keo",
    "teo",
    "ain",
    "air",
    "dair",
    "ar",
    "chy",
    "chey",
    "cheey",
    "shy",
    "am",
    "dam",
    "cthy",
    "chom",
    "otchol",
    "shecthy",
    "ke",
    "ol",  # Validated in Phase 14B
    # Function words (13 already included above)
    "sal",
    "qol",
    "daiin",
    "dain",
    "ory",
    # Compounds (2)
    "olkedy",
    "olchedy",
}

# Section labels
SECTION_LABELS = {
    "H": "Herbal",
    "A": "Astronomical",
    "B": "Biological",
    "P": "Pharmaceutical",
}


def load_sentences(filepath):
    """Load EVA file and extract sentences with section info."""
    sentences = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Match folio markers with section: <f1r.1,@H> or plain text
            match = re.match(r"<f\d+[rv]?[\.\d,@]*([HABP])?[^>]*>\s+(.+)$", line)
            if match:
                section = match.group(1) if match.group(1) else "H"  # Default to Herbal
                text = match.group(2).strip()
            else:
                section = "H"  # Default for plain text
                text = line

            # Remove EVA markup
            text = re.sub(r"[!%=\-\*\{\}]", "", text)
            words = text.split()

            if words:
                sentences.append({"words": words, "section": section})

    return sentences


def find_keol_instances(sentences):
    """Find all instances of keol and its morphological variants."""
    keol_data = {
        "standalone": 0,
        "in_compounds": 0,
        "total": 0,
        "with_prefix": [],
        "with_suffix": [],
        "sections": defaultdict(int),
        "contexts": [],
    }

    prefixes = ["qok", "qot", "ol", "ot"]
    suffixes = ["al", "ol", "ar", "or", "dy", "edy", "ain", "iin", "aiin", "y", "ey"]

    for sent in sentences:
        for word in sent["words"]:
            word_lower = word.lower()

            # Exact match
            if word_lower == "keol":
                keol_data["standalone"] += 1
                keol_data["total"] += 1
                keol_data["sections"][sent["section"]] += 1
                keol_data["contexts"].append(
                    {
                        "word": word,
                        "context": " ".join(sent["words"]),
                        "section": sent["section"],
                        "type": "standalone",
                    }
                )

            # Check for prefix + keol
            for prefix in prefixes:
                if word_lower.startswith(prefix + "keol"):
                    keol_data["with_prefix"].append(prefix)
                    keol_data["in_compounds"] += 1
                    keol_data["total"] += 1
                    keol_data["sections"][sent["section"]] += 1
                    keol_data["contexts"].append(
                        {
                            "word": word,
                            "context": " ".join(sent["words"]),
                            "section": sent["section"],
                            "type": f"{prefix}-keol",
                        }
                    )

            # Check for keol + suffix
            for suffix in suffixes:
                if word_lower == "keol" + suffix and word_lower != "keol":
                    keol_data["with_suffix"].append(suffix)
                    keol_data["in_compounds"] += 1
                    keol_data["total"] += 1
                    keol_data["sections"][sent["section"]] += 1
                    keol_data["contexts"].append(
                        {
                            "word": word,
                            "context": " ".join(sent["words"]),
                            "section": sent["section"],
                            "type": f"keol-{suffix}",
                        }
                    )

    return keol_data


def calculate_morphological_productivity(keol_data):
    """
    Calculate percentage of standalone vs compound usage.
    High productivity (>70% compound) suggests productive root.
    Low standalone (<30%) suggests it appears mostly in compounds.
    """
    total = keol_data["total"]
    standalone = keol_data["standalone"]
    compounds = keol_data["in_compounds"]

    standalone_pct = (standalone / total * 100) if total > 0 else 0
    compound_pct = (compounds / total * 100) if total > 0 else 0

    return {
        "total": total,
        "standalone": standalone,
        "standalone_pct": standalone_pct,
        "compounds": compounds,
        "compound_pct": compound_pct,
    }


def calculate_position_distribution(keol_data):
    """
    Calculate positional distribution (initial, medial, final).
    Productive roots tend to be medial (>70%).
    """
    positions = {"initial": 0, "medial": 0, "final": 0}

    for context in keol_data["contexts"]:
        words = context["context"].split()
        word_pos = None

        # Find position of word containing 'keol'
        for i, w in enumerate(words):
            if "keol" in w.lower():
                if i == 0:
                    positions["initial"] += 1
                elif i == len(words) - 1:
                    positions["final"] += 1
                else:
                    positions["medial"] += 1
                break

    total = sum(positions.values())
    position_pct = {
        k: (v / total * 100) if total > 0 else 0 for k, v in positions.items()
    }

    return position_pct


def calculate_section_distribution(keol_data, total_sentences_per_section):
    """
    Calculate section enrichment.
    Check if keol appears more in certain sections than expected.
    """
    observed = keol_data["sections"]
    total_keol = sum(observed.values())

    # Expected distribution based on section sizes
    expected = {}
    total_sentences = sum(total_sentences_per_section.values())
    for section, count in total_sentences_per_section.items():
        expected[section] = (count / total_sentences) * total_keol

    # Chi-square test for enrichment
    sections = ["H", "A", "B", "P"]
    obs = [observed.get(s, 0) for s in sections]
    exp = [expected.get(s, 0) for s in sections]

    # Only test if we have enough data
    if total_keol >= 20 and all(e >= 1 for e in exp):
        chi2, p_value = stats.chisquare(obs, exp)

        # Calculate enrichment ratios
        enrichment = {}
        for section in sections:
            if expected.get(section, 0) > 0:
                ratio = observed.get(section, 0) / expected.get(section, 1)
                enrichment[section] = ratio

        return {
            "chi2": chi2,
            "p_value": p_value,
            "enrichment": enrichment,
            "observed": dict(observed),
            "expected": expected,
        }
    else:
        return {
            "chi2": None,
            "p_value": None,
            "enrichment": None,
            "observed": dict(observed),
            "expected": expected,
            "note": "Insufficient data for chi-square test",
        }


def calculate_cooccurrence_with_validated(sentences, keol_data):
    """
    Calculate co-occurrence with validated vocabulary.
    This is the KEY metric that may have improved with 47 elements vs 28-41.
    """
    keol_sentences = set()

    # Find all sentences containing keol
    for context in keol_data["contexts"]:
        keol_sentences.add(context["context"])

    # Count co-occurrences
    cooccurrence = {
        "total_keol_sentences": len(keol_sentences),
        "sentences_with_validated": 0,
        "cooccurrence_pct": 0,
        "validated_words_found": Counter(),
    }

    for sent_text in keol_sentences:
        words = sent_text.lower().split()
        found_validated = False

        for word in words:
            # Skip keol itself
            if "keol" in word:
                continue

            # Check for exact match or as substring (for compounds)
            for validated in VALIDATED_VOCABULARY:
                if validated in word:
                    found_validated = True
                    cooccurrence["validated_words_found"][validated] += 1

        if found_validated:
            cooccurrence["sentences_with_validated"] += 1

    if cooccurrence["total_keol_sentences"] > 0:
        cooccurrence["cooccurrence_pct"] = (
            cooccurrence["sentences_with_validated"]
            / cooccurrence["total_keol_sentences"]
            * 100
        )

    return cooccurrence


def validate_keol(sentences, total_sentences_per_section):
    """
    Complete 10-point validation of keol.
    Compare to original Phase 10-11 score of 7/10.
    """
    print("\n" + "=" * 80)
    print("PHASE 15A: KEOL RE-VALIDATION WITH 47-ELEMENT VOCABULARY")
    print("=" * 80)

    # Find all keol instances
    print("\n1. Extracting keol instances...")
    keol_data = find_keol_instances(sentences)

    print(f"   Found {keol_data['total']} total instances of keol")
    print(f"   - Standalone: {keol_data['standalone']}")
    print(f"   - In compounds: {keol_data['in_compounds']}")
    print(
        f"   - With prefixes: {len(keol_data['with_prefix'])} ({Counter(keol_data['with_prefix'])})"
    )
    print(
        f"   - With suffixes: {len(keol_data['with_suffix'])} ({Counter(keol_data['with_suffix'])})"
    )

    # Validation criteria
    validation = {"total_instances": keol_data["total"], "criteria": {}}

    # Criterion 1: Morphological Productivity (2 points)
    print("\n2. Calculating morphological productivity...")
    productivity = calculate_morphological_productivity(keol_data)
    print(f"   Standalone: {productivity['standalone_pct']:.1f}%")
    print(f"   Compounds: {productivity['compound_pct']:.1f}%")

    # Score: 2 pts if standalone >70%, 1 pt if >50%, 0 pts if <50%
    if productivity["standalone_pct"] >= 70:
        productivity_score = 2
        productivity_note = "High standalone usage (>70%)"
    elif productivity["standalone_pct"] >= 50:
        productivity_score = 1
        productivity_note = "Moderate standalone usage (50-70%)"
    else:
        productivity_score = 0
        productivity_note = (
            f"Low standalone usage (<50%): {productivity['standalone_pct']:.1f}%"
        )

    validation["criteria"]["productivity"] = {
        "score": productivity_score,
        "data": productivity,
        "note": productivity_note,
    }
    print(f"   → Score: {productivity_score}/2 - {productivity_note}")

    # Criterion 2: Frequency (2 points)
    print("\n3. Checking frequency threshold...")
    # For low-frequency elements (n<25), threshold is n>=20
    freq_threshold = 20

    if keol_data["total"] >= freq_threshold:
        frequency_score = 2
        frequency_note = f"n={keol_data['total']} >= {freq_threshold}"
    else:
        frequency_score = 0
        frequency_note = (
            f"n={keol_data['total']} < {freq_threshold} (insufficient data)"
        )

    validation["criteria"]["frequency"] = {
        "score": frequency_score,
        "data": {"total": keol_data["total"], "threshold": freq_threshold},
        "note": frequency_note,
    }
    print(f"   → Score: {frequency_score}/2 - {frequency_note}")

    # Criterion 3: Position Distribution (2 points)
    print("\n4. Analyzing position distribution...")
    positions = calculate_position_distribution(keol_data)
    print(f"   Initial: {positions['initial']:.1f}%")
    print(f"   Medial: {positions['medial']:.1f}%")
    print(f"   Final: {positions['final']:.1f}%")

    # Score: 2 pts if medial >70%, 1 pt if >65% (adjusted for low-frequency), 0 pts if <65%
    medial_threshold = 65  # Adjusted threshold for n<25

    if positions["medial"] >= 70:
        position_score = 2
        position_note = "Strong medial preference (>70%)"
    elif positions["medial"] >= medial_threshold:
        position_score = 1
        position_note = f"Moderate medial preference ({medial_threshold}-70%)"
    else:
        position_score = 0
        position_note = (
            f"Weak medial preference (<{medial_threshold}%): {positions['medial']:.1f}%"
        )

    validation["criteria"]["position"] = {
        "score": position_score,
        "data": positions,
        "note": position_note,
    }
    print(f"   → Score: {position_score}/2 - {position_note}")

    # Criterion 4: Section Distribution (2 points)
    print("\n5. Testing section enrichment...")
    section_analysis = calculate_section_distribution(
        keol_data, total_sentences_per_section
    )

    if section_analysis["chi2"] is not None:
        print(f"   Chi-square: {section_analysis['chi2']:.2f}")
        print(f"   P-value: {section_analysis['p_value']:.4f}")
        print(f"   Enrichment ratios:")
        for section, ratio in section_analysis["enrichment"].items():
            print(f"      {SECTION_LABELS[section]}: {ratio:.2f}×")

        # Score: 2 pts if p<0.05 with clear enrichment, 1 pt if p<0.10, 0 pts otherwise
        if section_analysis["p_value"] < 0.05:
            section_score = 2
            section_note = (
                f"Significant enrichment (p={section_analysis['p_value']:.4f})"
            )
        elif section_analysis["p_value"] < 0.10:
            section_score = 1
            section_note = f"Marginal enrichment (p={section_analysis['p_value']:.4f})"
        else:
            section_score = 0
            section_note = (
                f"No significant enrichment (p={section_analysis['p_value']:.4f})"
            )
    else:
        section_score = 0
        section_note = section_analysis.get("note", "Insufficient data")
        print(f"   {section_note}")

    validation["criteria"]["section_distribution"] = {
        "score": section_score,
        "data": section_analysis,
        "note": section_note,
    }
    print(f"   → Score: {section_score}/2 - {section_note}")

    # Criterion 5: Co-occurrence with Validated Vocabulary (2 points) *** KEY TEST ***
    print("\n6. *** CRITICAL TEST: Co-occurrence with 47 validated elements ***")
    cooccurrence = calculate_cooccurrence_with_validated(sentences, keol_data)
    print(f"   Sentences with keol: {cooccurrence['total_keol_sentences']}")
    print(
        f"   Sentences with validated vocabulary: {cooccurrence['sentences_with_validated']}"
    )
    print(f"   Co-occurrence rate: {cooccurrence['cooccurrence_pct']:.1f}%")

    print(f"\n   Top validated words co-occurring with keol:")
    for word, count in cooccurrence["validated_words_found"].most_common(10):
        print(f"      {word}: {count}")

    # Score: 2 pts if >30%, 1 pt if >20%, 0 pts if <20%
    if cooccurrence["cooccurrence_pct"] >= 30:
        cooccurrence_score = 2
        cooccurrence_note = (
            f"Strong co-occurrence (>30%): {cooccurrence['cooccurrence_pct']:.1f}%"
        )
    elif cooccurrence["cooccurrence_pct"] >= 20:
        cooccurrence_score = 1
        cooccurrence_note = (
            f"Moderate co-occurrence (20-30%): {cooccurrence['cooccurrence_pct']:.1f}%"
        )
    else:
        cooccurrence_score = 0
        cooccurrence_note = (
            f"Weak co-occurrence (<20%): {cooccurrence['cooccurrence_pct']:.1f}%"
        )

    validation["criteria"]["cooccurrence"] = {
        "score": cooccurrence_score,
        "data": cooccurrence,
        "note": cooccurrence_note,
    }
    print(f"   → Score: {cooccurrence_score}/2 - {cooccurrence_note}")

    # Calculate total score
    total_score = sum(
        criterion["score"] for criterion in validation["criteria"].values()
    )
    validation["total_score"] = total_score
    validation["max_score"] = 10

    # Determine validation status
    if total_score >= 8:
        validation["status"] = "VALIDATED"
        validation["result"] = f"✓ VALIDATED: keol scores {total_score}/10"
    elif total_score >= 7:
        validation["status"] = "NEAR-VALIDATED"
        validation["result"] = (
            f"⚠ NEAR-VALIDATED: keol scores {total_score}/10 (needs 8+)"
        )
    else:
        validation["status"] = "NOT VALIDATED"
        validation["result"] = (
            f"✗ NOT VALIDATED: keol scores {total_score}/10 (needs 8+)"
        )

    # Print results
    print("\n" + "=" * 80)
    print("FINAL VALIDATION RESULTS")
    print("=" * 80)
    print(f"\nCandidate: keol")
    print(f"Frequency: n={keol_data['total']}")
    print(f"\nScores by criterion:")
    for criterion, data in validation["criteria"].items():
        print(f"  {criterion.upper()}: {data['score']}/2 - {data['note']}")

    print(f"\n{'=' * 80}")
    print(f"TOTAL SCORE: {total_score}/10")
    print(f"STATUS: {validation['status']}")
    print(f"{'=' * 80}")
    print(f"\n{validation['result']}")

    # Comparison to Phase 10-11
    print(f"\n" + "=" * 80)
    print("COMPARISON TO PHASE 10-11")
    print("=" * 80)
    print(f"Phase 10-11 score: 7/10 (with 28-41 validated elements)")
    print(f"Phase 15A score: {total_score}/10 (with 47 validated elements)")
    print(f"Improvement: {total_score - 7:+d} points")

    if total_score >= 8:
        print(f"\n✓✓✓ SUCCESS: keol now VALIDATED with expanded vocabulary context!")
    elif total_score == 7:
        print(f"\n⚠ No improvement: keol remains at 7/10 despite expanded vocabulary")
    else:
        print(f"\n✗ Score decreased: Investigate why keol performed worse")

    return validation


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
    output_file = manuscript_dir / "PHASE15A_KEOL_REVALIDATION.json"

    if not eva_file.exists():
        print(f"Error: EVA file not found: {eva_file}")
        return

    print("Loading manuscript...")
    sentences = load_sentences(eva_file)
    print(f"Loaded {len(sentences)} sentences")

    # Count sentences per section
    total_sentences_per_section = defaultdict(int)
    for sent in sentences:
        total_sentences_per_section[sent["section"]] += 1

    print("\nSentences per section:")
    for section, count in sorted(total_sentences_per_section.items()):
        print(f"  {SECTION_LABELS.get(section, section)}: {count}")

    # Validate keol
    validation = validate_keol(sentences, total_sentences_per_section)

    # Save results
    print(f"\nSaving results to {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(validation, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nPhase 15A complete! Results saved to:")
    print(f"  {output_file}")


if __name__ == "__main__":
    main()
