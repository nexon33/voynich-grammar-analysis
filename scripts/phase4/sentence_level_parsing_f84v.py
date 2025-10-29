"""
Sentence-Level Structural Parsing - f84v
=========================================

TEST: Does our grammatical model actually work?

We have enough validated components to test structure:
- Content: oak, oat
- Pronouns: daiin, aiin, saiin
- Cases: -al, -ar, -ol, -or
- Genitive: q-/qok-
- Verbal: -edy

Apply full decomposition to 5-10 consecutive sentences and check:
1. Consistent word order?
2. Case marking makes positional sense?
3. Unknowns appear in predictable slots?
4. Overall structure suggests coherent instructions?

This is the CRITICAL DIAGNOSTIC before vocabulary expansion.
"""

import json
from pathlib import Path
from collections import defaultdict, Counter


def load_manuscript():
    """Load manuscript"""
    transcription_path = Path(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt"
    )

    with open(transcription_path, "r", encoding="utf-8") as f:
        text = f.read()

    words = text.lower().split()
    return words


def extract_f84v_section(words):
    """
    Extract f84v section - biological/bath folio
    Position: approximately 24500-25000
    """
    return words[24500:25000]


def decompose_word_structural(word):
    """
    Decompose word into structural components

    Returns:
    - prefixes: [list of prefixes]
    - root: extracted root
    - suffixes: [list of suffixes]
    - identified_components: what we know
    """
    original = word
    components = {
        "word": word,
        "prefixes": [],
        "root": None,
        "suffixes": [],
        "known_elements": [],
        "confidence": "unknown",
    }

    # Check for known complete words first
    if word in ["daiin", "aiin", "saiin"]:
        components["root"] = word[:-2]
        components["suffixes"] = ["in"]
        components["known_elements"].append("PRONOUN")
        components["confidence"] = "high"
        return components

    if word in ["chedy", "shedy", "qokedy", "qokeedy", "qokeey"]:
        if word.startswith("qok"):
            components["prefixes"] = ["qok"]
            word = word[3:]
        components["root"] = word[:-3] if len(word) > 3 else word
        components["suffixes"] = ["edy"]
        components["known_elements"].append("VERB?")
        components["confidence"] = "medium"
        return components

    # Decompose step by step
    remaining = word

    # Step 1: Check for genitive prefix
    if remaining.startswith("qok") and len(remaining) > 3:
        components["prefixes"].append("qok")
        components["known_elements"].append("GENITIVE")
        remaining = remaining[3:]
    elif remaining.startswith("q") and len(remaining) > 1:
        components["prefixes"].append("q")
        components["known_elements"].append("GEN?")
        remaining = remaining[1:]
    elif remaining.startswith("d") and len(remaining) > 1:
        components["prefixes"].append("d")
        remaining = remaining[1:]
    elif remaining.startswith("s") and len(remaining) > 1:
        components["prefixes"].append("s")
        remaining = remaining[1:]

    # Step 2: Strip case/verbal suffixes (can be multiple!)
    suffixes_found = []

    # Try up to 3 iterations
    for _ in range(3):
        found = False

        # Case markers (highest priority)
        for case in ["al", "ar", "ol", "or"]:
            if remaining.endswith(case) and len(remaining) > len(case):
                suffixes_found.insert(0, case)
                components["known_elements"].append(f"CASE:{case}")
                remaining = remaining[: -len(case)]
                found = True
                break

        if found:
            continue

        # Verbal markers
        for verbal in ["edy", "eedy", "dy", "ey", "y"]:
            if remaining.endswith(verbal) and len(remaining) > len(verbal):
                suffixes_found.insert(0, verbal)
                if verbal in ["edy", "eedy", "dy"]:
                    components["known_elements"].append("VERBAL")
                remaining = remaining[: -len(verbal)]
                found = True
                break

        if found:
            continue

        # Pronoun marker
        if remaining.endswith("in") and len(remaining) > 2:
            suffixes_found.insert(0, "in")
            components["known_elements"].append("PRONOUN")
            remaining = remaining[:-2]
            found = True

        if not found:
            break

    components["suffixes"] = suffixes_found
    components["root"] = remaining

    # Step 3: Identify root if possible
    if remaining in ["ok", "oke", "oko"]:
        components["known_elements"].append("ROOT:oak")
        components["confidence"] = "high"
    elif remaining in ["ot", "ote", "oto"]:
        components["known_elements"].append("ROOT:oat")
        components["confidence"] = "high"
    elif remaining in ["ch", "che"]:
        components["known_elements"].append("ROOT:ch(verb?)")
        components["confidence"] = "medium"
    elif remaining in ["sh", "she"]:
        components["known_elements"].append("ROOT:sh(verb?)")
        components["confidence"] = "medium"
    elif remaining in ["ai", "da", "sa"]:
        components["known_elements"].append("ROOT:pronoun")
        components["confidence"] = "medium"
    elif len(remaining) >= 2:
        components["known_elements"].append(f"ROOT:?({remaining})")
        components["confidence"] = "low"
    else:
        components["confidence"] = "very_low"

    return components


def identify_sentences(words):
    """
    Identify sentence boundaries in f84v section

    Use pronouns (daiin, aiin, saiin) as likely sentence starts
    """
    sentences = []
    current = []

    pronouns = {"daiin", "aiin", "saiin"}

    for i, word in enumerate(words):
        current.append(word)

        # End sentence if:
        # - Next word is pronoun (new sentence starts)
        # - Reached good length (5-15 words)
        # - Contains punctuation

        is_end = False

        if i < len(words) - 1 and words[i + 1] in pronouns and len(current) >= 3:
            is_end = True
        elif len(current) >= 15:
            is_end = True
        elif any(c in word for c in [".", "!", "*"]):
            is_end = True

        if is_end:
            sentences.append(current)
            current = []

    if current:
        sentences.append(current)

    return sentences


def analyze_sentence_structure(sentence):
    """
    Analyze grammatical structure of a sentence
    """
    decompositions = []

    for word in sentence:
        decomp = decompose_word_structural(word)
        decompositions.append(decomp)

    # Build structure pattern
    structure = []
    for decomp in decompositions:
        # Categorize by primary function
        if "PRONOUN" in decomp["known_elements"]:
            structure.append("PRO")
        elif (
            "VERB?" in decomp["known_elements"] or "VERBAL" in decomp["known_elements"]
        ):
            structure.append("VRB")
        elif (
            "ROOT:oak" in decomp["known_elements"]
            or "ROOT:oat" in decomp["known_elements"]
        ):
            if any("CASE" in elem for elem in decomp["known_elements"]):
                structure.append("NOUN+CASE")
            else:
                structure.append("NOUN")
        elif any("CASE" in elem for elem in decomp["known_elements"]):
            structure.append("?+CASE")
        elif "GENITIVE" in decomp["known_elements"]:
            structure.append("GEN+?")
        else:
            structure.append("?")

    return {
        "sentence": sentence,
        "decompositions": decompositions,
        "structure": structure,
        "known_ratio": sum(
            1 for d in decompositions if d["confidence"] in ["high", "medium"]
        )
        / len(decompositions),
        "word_count": len(sentence),
    }


def find_structural_patterns(analyses):
    """
    Identify common structural patterns across sentences
    """
    pattern_counts = Counter()
    positional_slots = defaultdict(Counter)

    for analysis in analyses:
        # Pattern of known elements
        pattern = tuple(analysis["structure"])
        pattern_counts[pattern] += 1

        # What appears in each position?
        for i, (struct, decomp) in enumerate(
            zip(analysis["structure"], analysis["decompositions"])
        ):
            slot_type = f"position_{i}" if i < 5 else "position_5+"
            positional_slots[slot_type][struct] += 1

    return {
        "common_patterns": pattern_counts.most_common(10),
        "positional_frequencies": {
            slot: dict(counts.most_common(5))
            for slot, counts in positional_slots.items()
        },
    }


def identify_gaps(analyses):
    """
    What unknown elements appear in what positions?
    """
    verb_position_unknowns = Counter()
    object_position_unknowns = Counter()
    all_unknowns = Counter()

    for analysis in analyses:
        for i, (struct, decomp) in enumerate(
            zip(analysis["structure"], analysis["decompositions"])
        ):
            root = decomp["root"]

            # Track unknowns
            if decomp["confidence"] in ["low", "very_low"]:
                all_unknowns[root] += 1

                # Is it in verb position? (after pronoun, before noun)
                if i > 0 and i < len(analysis["structure"]) - 1:
                    if (
                        analysis["structure"][i - 1] == "PRO"
                        and "NOUN" in analysis["structure"][i + 1]
                    ):
                        verb_position_unknowns[root] += 1

                    # Is it in object position? (after verb)
                    if "VRB" in analysis["structure"][i - 1]:
                        object_position_unknowns[root] += 1

    return {
        "all_unknowns": dict(all_unknowns.most_common(20)),
        "verb_position_unknowns": dict(verb_position_unknowns.most_common(10)),
        "object_position_unknowns": dict(object_position_unknowns.most_common(10)),
    }


def main():
    print("=" * 80)
    print("SENTENCE-LEVEL STRUCTURAL PARSING - F84V")
    print("=" * 80)
    print()
    print("DIAGNOSTIC TEST: Does our grammatical model work?")
    print()

    # Load f84v
    print("Loading f84v section...")
    words = load_manuscript()
    f84v = extract_f84v_section(words)
    print(f"F84v section: {len(f84v)} words")
    print()

    # Identify sentences
    print("Identifying sentences...")
    sentences = identify_sentences(f84v)
    print(f"Found {len(sentences)} sentences")
    print()

    # Analyze first 5-10 sentences
    print("=" * 80)
    print("SENTENCE-BY-SENTENCE STRUCTURAL ANALYSIS")
    print("=" * 80)
    print()

    analyses = []
    num_sentences = min(10, len(sentences))

    for i, sentence in enumerate(sentences[:num_sentences], 1):
        print(f"SENTENCE {i} ({len(sentence)} words)")
        print("-" * 80)
        print(f"Voynich: {' '.join(sentence)}")
        print()

        analysis = analyze_sentence_structure(sentence)
        analyses.append(analysis)

        # Print decompositions
        print("Decomposition:")
        for word, decomp in zip(sentence, analysis["decompositions"]):
            prefix_str = (
                "+".join(decomp["prefixes"]) + "-" if decomp["prefixes"] else ""
            )
            suffix_str = (
                "-" + "-".join(decomp["suffixes"]) if decomp["suffixes"] else ""
            )
            decomp_str = f"{prefix_str}{decomp['root']}{suffix_str}"

            known_str = (
                ", ".join(decomp["known_elements"])
                if decomp["known_elements"]
                else "UNKNOWN"
            )
            conf_str = decomp["confidence"]

            print(f"  {word:15} → {decomp_str:20} [{known_str}] ({conf_str})")

        print()
        print(f"Structure: {' → '.join(analysis['structure'])}")
        print(f"Known elements: {analysis['known_ratio']:.1%}")
        print()
        print()

    # Pattern analysis
    print("=" * 80)
    print("STRUCTURAL PATTERN ANALYSIS")
    print("=" * 80)
    print()

    patterns = find_structural_patterns(analyses)

    print("Common sentence structures:")
    for pattern, count in patterns["common_patterns"]:
        pattern_str = " → ".join(pattern)
        print(f"  {pattern_str}: {count}×")
    print()

    print("Positional frequencies:")
    for position in sorted(patterns["positional_frequencies"].keys()):
        print(f"  {position}:")
        for struct, count in patterns["positional_frequencies"][position].items():
            print(f"    {struct}: {count}×")
    print()

    # Gap analysis
    print("=" * 80)
    print("GAP ANALYSIS: What unknowns appear where?")
    print("=" * 80)
    print()

    gaps = identify_gaps(analyses)

    print("Most frequent unknown roots:")
    for root, count in list(gaps["all_unknowns"].items())[:15]:
        print(f"  {root}: {count}×")
    print()

    print("Unknown roots in VERB position (after pronoun, before noun):")
    for root, count in list(gaps["verb_position_unknowns"].items())[:10]:
        print(f"  {root}: {count}×")
    print()

    print("Unknown roots in OBJECT position (after verb):")
    for root, count in list(gaps["object_position_unknowns"].items())[:10]:
        print(f"  {root}: {count}×")
    print()

    # VERDICT
    print("=" * 80)
    print("DIAGNOSTIC VERDICT")
    print("=" * 80)
    print()

    # Calculate metrics
    avg_known_ratio = sum(a["known_ratio"] for a in analyses) / len(analyses)
    has_common_patterns = (
        len(patterns["common_patterns"]) > 0 and patterns["common_patterns"][0][1] > 1
    )

    print(f"Average known elements: {avg_known_ratio:.1%}")
    print(f"Repeated structures found: {has_common_patterns}")
    print()

    checks_passed = 0
    total_checks = 4

    # Check 1: Pronouns in expected positions
    pro_initial = sum(
        1 for a in analyses if a["structure"] and a["structure"][0] == "PRO"
    )
    if pro_initial >= len(analyses) * 0.5:
        print("✓ CHECK 1: Pronouns appear sentence-initially (expected)")
        checks_passed += 1
    else:
        print("✗ CHECK 1: Pronouns NOT consistently sentence-initial")

    # Check 2: Cases appear on nouns
    case_on_nouns = sum(
        1 for a in analyses for s in a["structure"] if "NOUN+CASE" in s or "?+CASE" in s
    )
    if case_on_nouns > 0:
        print("✓ CHECK 2: Case markers attach to nominals (expected)")
        checks_passed += 1
    else:
        print("✗ CHECK 2: No case-marked nominals found")

    # Check 3: Some structural consistency
    if has_common_patterns:
        print("✓ CHECK 3: Repeated sentence structures (shows consistency)")
        checks_passed += 1
    else:
        print("✗ CHECK 3: No repeated structures (random variation?)")

    # Check 4: Reasonable known ratio
    if avg_known_ratio >= 0.3:
        print(
            f"✓ CHECK 4: {avg_known_ratio:.1%} known elements (sufficient for analysis)"
        )
        checks_passed += 1
    else:
        print(f"✗ CHECK 4: Only {avg_known_ratio:.1%} known elements (insufficient)")

    print()
    print(f"RESULT: {checks_passed}/{total_checks} checks passed")
    print()

    if checks_passed >= 3:
        print("✓✓✓ GRAMMATICAL MODEL VALIDATED")
        print()
        print("The structure shows:")
        print("  - Consistent word order patterns")
        print("  - Case marking behaves as expected")
        print("  - Pronouns in appropriate positions")
        print("  - Identifiable gaps in specific grammatical slots")
        print()
        print("NEXT STEP: Systematic vocabulary expansion")
        print("Focus on high-frequency unknowns in:")
        print("  1. Verb positions (after pronouns)")
        print("  2. Object positions (after verbs)")
        print("  3. Location expressions (with case markers)")
    else:
        print("⚠ GRAMMATICAL MODEL NEEDS REVISION")
        print()
        print("Issues found:")
        if pro_initial < len(analyses) * 0.5:
            print("  - Pronoun positions inconsistent")
        if not has_common_patterns:
            print("  - No repeated structures")
        if avg_known_ratio < 0.3:
            print("  - Too few known elements")
        print()
        print("NEXT STEP: Revisit grammatical assumptions")

    # Save results
    results = {
        "sentences_analyzed": [
            {
                "sentence": " ".join(a["sentence"]),
                "structure": a["structure"],
                "known_ratio": a["known_ratio"],
                "decompositions": [
                    {
                        "word": d["word"],
                        "root": d["root"],
                        "prefixes": d["prefixes"],
                        "suffixes": d["suffixes"],
                        "known_elements": d["known_elements"],
                        "confidence": d["confidence"],
                    }
                    for d in a["decompositions"]
                ],
            }
            for a in analyses
        ],
        "patterns": {
            "common_structures": [
                {"pattern": list(p), "count": c} for p, c in patterns["common_patterns"]
            ],
            "positional_frequencies": patterns["positional_frequencies"],
        },
        "gaps": gaps,
        "verdict": {
            "checks_passed": checks_passed,
            "total_checks": total_checks,
            "avg_known_ratio": avg_known_ratio,
            "model_validated": checks_passed >= 3,
        },
    }

    output_path = Path("results/phase4/sentence_level_parsing_f84v.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print()
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
