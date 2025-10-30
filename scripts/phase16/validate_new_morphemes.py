#!/usr/bin/env python3
"""
Phase 16: Validate t- PREFIX and -d SUFFIX

Discovered in Phase 15B:
- t- prefix: tcho = t- + cho (~270 uses)
- -d suffix: chod = cho + -d (~360 uses)

Goal: Validate these work with OTHER roots, not just cho!
"""

import re
from collections import defaultdict, Counter
from pathlib import Path
from scipy import stats
import json

# Validated roots to test with
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
    "chy",
    "chey",
    "cheey",
    "shy",
    "am",
    "dam",
    "cthy",
    "chom",
}


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


def find_t_prefix_combinations(sentences):
    """Find all t- + ROOT combinations."""
    print("\n" + "=" * 80)
    print("ANALYZING t- PREFIX")
    print("=" * 80)

    t_data = {
        "total_instances": 0,
        "unique_forms": set(),
        "combinations": Counter(),
        "with_validated_roots": Counter(),
        "contexts": [],
    }

    for sent in sentences:
        for word in sent:
            word_lower = word.lower()

            # Check if word starts with 't' and has more letters
            if word_lower.startswith("t") and len(word_lower) > 1:
                # Check if remainder matches a validated root
                remainder = word_lower[1:]

                # Try to find validated root in remainder
                for root in sorted(VALIDATED_ROOTS, key=len, reverse=True):
                    if remainder.startswith(root) and len(root) >= 2:
                        t_data["total_instances"] += 1
                        t_data["unique_forms"].add(word_lower)
                        t_data["combinations"][f"t-{root}"] += 1
                        t_data["with_validated_roots"][root] += 1
                        t_data["contexts"].append(
                            {
                                "word": word_lower,
                                "root": root,
                                "context": " ".join(sent),
                            }
                        )
                        break

    print(f"\nTotal t- + ROOT instances found: {t_data['total_instances']}")
    print(f"Unique t- forms: {len(t_data['unique_forms'])}")
    print(f"\nTop 20 t- + ROOT combinations:")
    for combo, count in t_data["combinations"].most_common(20):
        print(f"  {combo}: {count}")

    print(f"\nValidated roots that combine with t-:")
    for root, count in t_data["with_validated_roots"].most_common(20):
        print(f"  {root}: {count} instances")

    # Calculate productivity
    unique_roots = len(t_data["with_validated_roots"])
    total_validated_roots = len(VALIDATED_ROOTS)
    productivity_pct = (
        (unique_roots / total_validated_roots * 100) if total_validated_roots > 0 else 0
    )

    print(
        f"\nProductivity: {unique_roots}/{total_validated_roots} roots ({productivity_pct:.1f}%)"
    )

    return t_data


def find_d_suffix_combinations(sentences):
    """Find all ROOT + -d combinations."""
    print("\n" + "=" * 80)
    print("ANALYZING -d SUFFIX")
    print("=" * 80)

    d_data = {
        "total_instances": 0,
        "unique_forms": set(),
        "combinations": Counter(),
        "with_validated_roots": Counter(),
        "contexts": [],
    }

    for sent in sentences:
        for word in sent:
            word_lower = word.lower()

            # Check if word ends with 'd' and has more letters
            if word_lower.endswith("d") and len(word_lower) > 1:
                # Check if beginning matches a validated root
                prefix_part = word_lower[:-1]

                # Try to find validated root in prefix
                for root in sorted(VALIDATED_ROOTS, key=len, reverse=True):
                    if prefix_part == root or (
                        prefix_part.endswith(root) and len(root) >= 2
                    ):
                        d_data["total_instances"] += 1
                        d_data["unique_forms"].add(word_lower)
                        d_data["combinations"][f"{root}-d"] += 1
                        d_data["with_validated_roots"][root] += 1
                        d_data["contexts"].append(
                            {
                                "word": word_lower,
                                "root": root,
                                "context": " ".join(sent),
                            }
                        )
                        break

    print(f"\nTotal ROOT + -d instances found: {d_data['total_instances']}")
    print(f"Unique -d forms: {len(d_data['unique_forms'])}")
    print(f"\nTop 20 ROOT + -d combinations:")
    for combo, count in d_data["combinations"].most_common(20):
        print(f"  {combo}: {count}")

    print(f"\nValidated roots that combine with -d:")
    for root, count in d_data["with_validated_roots"].most_common(20):
        print(f"  {root}: {count} instances")

    # Calculate productivity
    unique_roots = len(d_data["with_validated_roots"])
    total_validated_roots = len(VALIDATED_ROOTS)
    productivity_pct = (
        (unique_roots / total_validated_roots * 100) if total_validated_roots > 0 else 0
    )

    print(
        f"\nProductivity: {unique_roots}/{total_validated_roots} roots ({productivity_pct:.1f}%)"
    )

    return d_data


def validate_morpheme(morpheme_data, morpheme_name, morpheme_type):
    """
    Validate prefix or suffix using 10-point framework.
    """
    print(f"\n{'=' * 80}")
    print(f"VALIDATING {morpheme_name} ({morpheme_type})")
    print(f"{'=' * 80}")

    validation = {"morpheme": morpheme_name, "type": morpheme_type, "criteria": {}}

    total_instances = morpheme_data["total_instances"]
    unique_forms = len(morpheme_data["unique_forms"])
    unique_roots = len(morpheme_data["with_validated_roots"])

    # Criterion 1: Productivity (unique stems) - 2 points
    print(f"\n1. Productivity (unique roots combined)")
    print(f"   Unique roots: {unique_roots}")

    if unique_roots >= 10:
        prod_score = 2
        prod_note = f"High productivity: {unique_roots} different roots"
    elif unique_roots >= 5:
        prod_score = 1
        prod_note = f"Moderate productivity: {unique_roots} different roots"
    else:
        prod_score = 0
        prod_note = f"Low productivity: {unique_roots} different roots (needs 5+)"

    validation["criteria"]["productivity"] = {
        "score": prod_score,
        "data": {"unique_roots": unique_roots, "total_roots": len(VALIDATED_ROOTS)},
        "note": prod_note,
    }
    print(f"   → Score: {prod_score}/2 - {prod_note}")

    # Criterion 2: Frequency - 2 points
    print(f"\n2. Frequency")
    print(f"   Total instances: {total_instances}")

    if total_instances >= 50:
        freq_score = 2
        freq_note = f"High frequency: {total_instances} instances"
    elif total_instances >= 20:
        freq_score = 1
        freq_note = f"Moderate frequency: {total_instances} instances"
    else:
        freq_score = 0
        freq_note = f"Low frequency: {total_instances} instances (needs 20+)"

    validation["criteria"]["frequency"] = {
        "score": freq_score,
        "data": {"total_instances": total_instances},
        "note": freq_note,
    }
    print(f"   → Score: {freq_score}/2 - {freq_note}")

    # Criterion 3: Diversity (unique forms) - 2 points
    print(f"\n3. Form diversity")
    print(f"   Unique forms: {unique_forms}")

    if unique_forms >= 30:
        div_score = 2
        div_note = f"High diversity: {unique_forms} unique forms"
    elif unique_forms >= 15:
        div_score = 1
        div_note = f"Moderate diversity: {unique_forms} unique forms"
    else:
        div_score = 0
        div_note = f"Low diversity: {unique_forms} unique forms (needs 15+)"

    validation["criteria"]["diversity"] = {
        "score": div_score,
        "data": {"unique_forms": unique_forms},
        "note": div_note,
    }
    print(f"   → Score: {div_score}/2 - {div_note}")

    # Criterion 4: Productivity ratio - 2 points
    print(f"\n4. Productivity ratio")
    if total_instances > 0:
        ratio = unique_forms / total_instances
        print(
            f"   Ratio: {ratio:.3f} ({unique_forms} forms / {total_instances} instances)"
        )

        if ratio >= 0.20:
            ratio_score = 2
            ratio_note = f"High ratio: {ratio:.3f} (productive affix)"
        elif ratio >= 0.10:
            ratio_score = 1
            ratio_note = f"Moderate ratio: {ratio:.3f}"
        else:
            ratio_score = 0
            ratio_note = f"Low ratio: {ratio:.3f} (needs 0.10+)"
    else:
        ratio_score = 0
        ratio_note = "No instances found"

    validation["criteria"]["productivity_ratio"] = {
        "score": ratio_score,
        "data": {"ratio": ratio if total_instances > 0 else 0},
        "note": ratio_note,
    }
    print(f"   → Score: {ratio_score}/2 - {ratio_note}")

    # Criterion 5: Combines with diverse roots - 2 points
    print(f"\n5. Root diversity")
    roots_list = list(morpheme_data["with_validated_roots"].keys())
    print(f"   Combines with: {', '.join(roots_list[:10])}")
    if len(roots_list) > 10:
        print(f"   ... and {len(roots_list) - 10} more")

    # Check if combines with different root types
    has_c_initial = any(r[0] in "bcdfghjklmnpqrstvwxyz" for r in roots_list)
    has_v_initial = any(r[0] in "aeiou" for r in roots_list)
    has_function = any(
        r in ["qol", "sal", "daiin", "ory", "chy", "shy", "am", "dam"]
        for r in roots_list
    )

    diversity_count = sum([has_c_initial, has_v_initial, has_function])

    if diversity_count >= 2 and unique_roots >= 5:
        root_div_score = 2
        root_div_note = f"Combines with diverse root types ({diversity_count}/3)"
    elif diversity_count >= 1 and unique_roots >= 3:
        root_div_score = 1
        root_div_note = f"Limited root diversity"
    else:
        root_div_score = 0
        root_div_note = f"Insufficient root diversity"

    validation["criteria"]["root_diversity"] = {
        "score": root_div_score,
        "data": {
            "c_initial": has_c_initial,
            "v_initial": has_v_initial,
            "function_words": has_function,
            "diversity_count": diversity_count,
        },
        "note": root_div_note,
    }
    print(f"   → Score: {root_div_score}/2 - {root_div_note}")

    # Calculate total
    total_score = sum(c["score"] for c in validation["criteria"].values())
    validation["total_score"] = total_score
    validation["max_score"] = 10

    # Status
    if total_score >= 8:
        validation["status"] = "VALIDATED"
        validation["result"] = f"✓ VALIDATED: {morpheme_name} scores {total_score}/10"
    elif total_score >= 7:
        validation["status"] = "NEAR-VALIDATED"
        validation["result"] = (
            f"⚠ NEAR-VALIDATED: {morpheme_name} scores {total_score}/10"
        )
    else:
        validation["status"] = "NOT VALIDATED"
        validation["result"] = (
            f"✗ NOT VALIDATED: {morpheme_name} scores {total_score}/10"
        )

    # Print results
    print(f"\n{'=' * 80}")
    print(f"VALIDATION RESULT: {morpheme_name}")
    print(f"{'=' * 80}")
    print(f"\nTotal Score: {total_score}/10")
    print(f"Status: {validation['status']}")
    print(f"\n{validation['result']}")

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
    output_file = manuscript_dir / "PHASE16_NEW_MORPHEME_VALIDATION.json"

    if not eva_file.exists():
        print(f"Error: EVA file not found: {eva_file}")
        return

    print("=" * 80)
    print("PHASE 16: NEW MORPHEME VALIDATION")
    print("=" * 80)
    print("\nValidating t- prefix and -d suffix discovered in Phase 15B")
    print(f"Testing against {len(VALIDATED_ROOTS)} validated roots\n")

    print("Loading manuscript...")
    sentences = load_sentences(eva_file)
    print(f"Loaded {len(sentences)} sentences\n")

    # Analyze t- prefix
    t_data = find_t_prefix_combinations(sentences)

    # Analyze -d suffix
    d_data = find_d_suffix_combinations(sentences)

    # Validate both
    t_validation = validate_morpheme(t_data, "t-", "prefix")
    d_validation = validate_morpheme(d_data, "-d", "suffix")

    # Summary
    print("\n" + "=" * 80)
    print("PHASE 16 SUMMARY")
    print("=" * 80)

    results = {
        "t_prefix": {
            "validation": t_validation,
            "data": {
                "total_instances": t_data["total_instances"],
                "unique_forms": len(t_data["unique_forms"]),
                "top_combinations": dict(t_data["combinations"].most_common(10)),
            },
        },
        "d_suffix": {
            "validation": d_validation,
            "data": {
                "total_instances": d_data["total_instances"],
                "unique_forms": len(d_data["unique_forms"]),
                "top_combinations": dict(d_data["combinations"].most_common(10)),
            },
        },
    }

    print(f"\nt- PREFIX: {t_validation['result']}")
    print(f"-d SUFFIX: {d_validation['result']}")

    # Count new validated morphemes
    new_validated = 0
    if t_validation["status"] == "VALIDATED":
        new_validated += 1
    if d_validation["status"] == "VALIDATED":
        new_validated += 1

    print(f"\n{'=' * 80}")
    if new_validated == 2:
        print("🎉 SUCCESS: Both morphemes VALIDATED!")
        print(f"New morpheme count: 47 + 2 = 49 morphemes")
    elif new_validated == 1:
        print("⚠ PARTIAL SUCCESS: 1 morpheme validated")
    else:
        print("✗ No new morphemes validated")
    print(f"{'=' * 80}")

    # Save results
    print(f"\nSaving results to {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nPhase 16 validation complete!")
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()
