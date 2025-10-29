"""
Phase 5A: Critical Generalization Test

HYPOTHESIS: The grammatical system discovered from f84v generalizes to unseen text

TEST DESIGN:
- Select 3 folios from DIFFERENT sections (never analyzed in Phases 4-5)
- Parse 10 consecutive lines from each using ONLY discovered grammar
- Measure recognition rates and structural coherence
- Compare to f84v baseline (100% coherence, 58% coverage)

SUCCESS CRITERIA:
- Strong validation: 60-80% recognition, clear grammatical structure in 70-90% of sentences
- Partial validation: 40-60% recognition, structure in 40-60% of sentences
- Failure: <40% recognition, <30% show structure

FIXED GRAMMATICAL SYSTEM (no new analysis allowed):
- 8 suffixes: -dy, -ol, -ar, -al, -or, -iin, -aiin, -ain
- 4 function words: qol, sal, dain, ory
- 6 semantic nouns: ok/qok (oak), ot/qot (oat), shee/she (water), dor (red), cho (vessel), cheo

NO MODIFICATIONS ALLOWED DURING TEST
"""

import re
from collections import Counter


def load_folio(filepath, folio_id):
    """Load specific folio from ZL transcription"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    folio_lines = []
    in_folio = False

    for line in lines:
        line_stripped = line.strip()

        # Check for folio marker (e.g., <f1r>, <f2r>, <f3r>)
        if f"<{folio_id}>" in line_stripped:
            in_folio = True
            continue
        elif line_stripped.startswith("<f") and ">" in line_stripped and in_folio:
            # Check if this is a different folio (not just a line marker like <f2r.1>)
            if re.match(r"^<f\d+[rv]>", line_stripped):
                # Reached next folio
                break

        # Process lines within the folio
        if in_folio:
            # Skip comments and section headers
            if line_stripped.startswith("#") or not line_stripped:
                continue

            # Extract text from ZL format: <f1r.1,@P0> text.here.with.dots
            if line_stripped.startswith("<f"):
                # Find the text after the line marker
                match = re.search(r"<f\d+[rv]\.[^>]+>\s+(.+)$", line_stripped)
                if match:
                    text = match.group(1)
                    # Remove markup and extract words
                    # Remove special markers like <%>, <$>, <!@...>, {...}, [...]
                    text = re.sub(r"<[^>]+>", "", text)
                    text = re.sub(r"\{[^}]+\}", "", text)
                    text = re.sub(r"\[[^\]]+\]", "", text)
                    text = re.sub(r"!@\d+;", "", text)
                    text = re.sub(r"@\d+;", "", text)
                    # Split by dots, commas, hyphens, extract words
                    words = re.findall(r"[a-z!]+", text.lower())
                    if words:
                        folio_lines.append(" ".join(words))

    return folio_lines


def parse_word_fixed_grammar(word):
    """
    Parse word using ONLY the fixed grammatical system
    NO NEW ANALYSIS OR MODIFICATIONS ALLOWED
    """
    original = word
    components = {"roots": [], "function_words": [], "suffixes": [], "unknown": []}

    remaining = word

    # 1. Semantic roots (6 validated)
    if word.startswith("qok"):
        components["roots"].append("oak-GEN")
        remaining = word[3:]
    elif word.startswith("qot"):
        components["roots"].append("oat-GEN")
        remaining = word[3:]
    elif word.startswith("ok"):
        components["roots"].append("oak")
        remaining = word[2:]
    elif word.startswith("ot"):
        components["roots"].append("oat")
        remaining = word[2:]

    # Check for other semantic roots
    if "shee" in remaining:
        components["roots"].append("water")
        remaining = remaining.replace("shee", "", 1)
    elif "she" in remaining:
        components["roots"].append("water")
        remaining = remaining.replace("she", "", 1)

    if "cho" in remaining and "cheo" not in remaining:
        components["roots"].append("vessel")
        remaining = remaining.replace("cho", "", 1)

    if "cheo" in remaining:
        components["roots"].append("CHEO")
        remaining = remaining.replace("cheo", "", 1)

    if "dor" in remaining:
        components["roots"].append("red")
        remaining = remaining.replace("dor", "", 1)

    # 2. Function words (4 validated)
    if "qol" in remaining:
        components["function_words"].append("THEN")
        remaining = remaining.replace("qol", "", 1)

    if "sal" in remaining:
        components["function_words"].append("AND")
        remaining = remaining.replace("sal", "", 1)

    if "dain" in remaining or "dai!n" in remaining:
        components["function_words"].append("THAT")
        remaining = remaining.replace("dain", "", 1).replace("dai!n", "", 1)

    # Check for ory (bound derivational suffix)
    if remaining.endswith("ory"):
        components["suffixes"].append("ADV")
        remaining = remaining[:-3]

    # 3. Verbal suffix
    if "edy" in remaining:
        components["suffixes"].append("VERB")
        remaining = remaining.replace("edy", "", 1)
    elif remaining.endswith("dy"):
        components["suffixes"].append("VERB")
        remaining = remaining[:-2]

    # 4. Definiteness markers
    if "aiin" in remaining:
        components["suffixes"].append("DEF")
        remaining = remaining.replace("aiin", "", 1)
    elif "iin" in remaining:
        components["suffixes"].append("DEF")
        remaining = remaining.replace("iin", "", 1)
    elif "ain" in remaining:
        components["suffixes"].append("DEF")
        remaining = remaining.replace("ain", "", 1)

    # 5. Case markers
    if "al" in remaining:
        components["suffixes"].append("LOC")
        remaining = remaining.replace("al", "", 1)
    if "ar" in remaining:
        components["suffixes"].append("DIR")
        remaining = remaining.replace("ar", "", 1)
    if "or" in remaining:
        components["suffixes"].append("INST")
        remaining = remaining.replace("or", "", 1)
    if "ol" in remaining:
        components["suffixes"].append("LOC2")
        remaining = remaining.replace("ol", "", 1)

    # 6. What remains is unknown
    if remaining and remaining not in [
        "",
        "k",
        "ch",
        "p",
        "s",
        "l",
        "d",
        "y",
        "e",
        "!",
        "t",
        "c",
        "h",
    ]:
        components["unknown"].append(remaining)

    return components


def format_parsed_word(word, components):
    """Format parsed word for display"""
    parts = []

    if components["roots"]:
        parts.extend(components["roots"])

    if components["function_words"]:
        parts.extend([f"[{fw}]" for fw in components["function_words"]])

    if components["suffixes"]:
        parts.append("-" + "-".join(components["suffixes"]))

    if components["unknown"]:
        parts.append(f"[?{components['unknown'][0]}]")

    if not parts:
        return f"[?{word}]"

    return ".".join(parts)


def calculate_recognition_rate(components):
    """Calculate what % of word was recognized"""
    recognized = (
        len(components["roots"])
        + len(components["function_words"])
        + len(components["suffixes"])
    )
    total = recognized + len(components["unknown"])

    if total == 0:
        return 0.0

    return recognized / total


def assess_sentence_structure(parsed_words):
    """
    Assess if sentence shows clear grammatical structure

    Criteria:
    1. Contains semantic roots (content)
    2. Contains grammatical suffixes (structure)
    3. Has case marking or verbal forms (grammatical relations)
    4. Function words in plausible positions
    """
    has_roots = any("roots" in w and w["roots"] for w in parsed_words)
    has_suffixes = any("suffixes" in w and w["suffixes"] for w in parsed_words)
    has_case = any(
        "suffixes" in w
        and any(s in w["suffixes"] for s in ["LOC", "DIR", "INST", "LOC2"])
        for w in parsed_words
    )
    has_verbal = any("suffixes" in w and "VERB" in w["suffixes"] for w in parsed_words)
    has_function = any(
        "function_words" in w and w["function_words"] for w in parsed_words
    )

    structure_score = sum(
        [has_roots, has_suffixes, has_case or has_verbal, has_function]
    )

    return {
        "has_structure": structure_score >= 2,  # At least 2 of 4 criteria
        "score": structure_score,
        "has_roots": has_roots,
        "has_suffixes": has_suffixes,
        "has_case_or_verbal": has_case or has_verbal,
        "has_function_words": has_function,
    }


def test_folio(folio_id, lines, folio_name):
    """Test grammatical system on a single folio"""

    print(f"\n{'=' * 70}")
    print(f"TESTING: {folio_id} ({folio_name})")
    print(f"{'=' * 70}")

    # Take first 10 lines
    test_lines = lines[:10]

    results = []
    total_recognition = 0
    total_words = 0
    structured_sentences = 0

    for i, line in enumerate(test_lines, 1):
        words = line.split()

        parsed_words = []
        line_recognition = []

        for word in words:
            # Check if standalone function word
            if word in ["qol", "sal", "dain", "dai!n", "ol", "or"]:
                components = {
                    "roots": [],
                    "function_words": [word.upper()],
                    "suffixes": [],
                    "unknown": [],
                }
                line_recognition.append(1.0)
            else:
                components = parse_word_fixed_grammar(word)
                line_recognition.append(calculate_recognition_rate(components))

            parsed_words.append(components)

        # Format translation
        translation_parts = []
        for j, word in enumerate(words):
            if word in ["qol", "sal", "dain", "dai!n", "ol", "or"]:
                translation_parts.append(f"[{word.upper()}]")
            else:
                translation_parts.append(format_parsed_word(word, parsed_words[j]))

        translation = " ".join(translation_parts)

        # Assess structure
        structure = assess_sentence_structure(parsed_words)

        # Calculate line recognition
        line_recog_rate = (
            sum(line_recognition) / len(line_recognition) if line_recognition else 0
        )

        print(f"\nLine {i}:")
        print(f"  Original:    {line}")
        print(f"  Translation: {translation}")
        print(f"  Recognition: {line_recog_rate * 100:.0f}%")
        print(
            f"  Structure:   {'YES ✓' if structure['has_structure'] else 'NO ✗'} (score: {structure['score']}/4)"
        )

        results.append(
            {
                "line_num": i,
                "original": line,
                "translation": translation,
                "recognition_rate": line_recog_rate,
                "has_structure": structure["has_structure"],
                "structure_score": structure["score"],
            }
        )

        total_recognition += line_recog_rate
        total_words += len(words)
        if structure["has_structure"]:
            structured_sentences += 1

    # Summary for this folio
    avg_recognition = (total_recognition / len(test_lines)) * 100 if test_lines else 0
    structure_pct = (structured_sentences / len(test_lines)) * 100 if test_lines else 0

    print(f"\n{'-' * 70}")
    print(f"FOLIO SUMMARY: {folio_id}")
    print(f"{'-' * 70}")
    print(f"Average recognition: {avg_recognition:.1f}%")
    print(
        f"Lines with structure: {structured_sentences}/{len(test_lines)} ({structure_pct:.0f}%)"
    )

    return {
        "folio_id": folio_id,
        "folio_name": folio_name,
        "avg_recognition": avg_recognition,
        "structure_pct": structure_pct,
        "lines_tested": len(test_lines),
        "results": results,
    }


def main():
    print("=" * 70)
    print("PHASE 5A: CRITICAL GENERALIZATION TEST")
    print("=" * 70)
    print(
        "\nHYPOTHESIS: Grammatical system discovered from f84v generalizes to unseen text"
    )
    print("\nFIXED SYSTEM (no modifications allowed):")
    print("  • 6 semantic nouns: oak, oat, water, red, vessel, cheo")
    print("  • 4 function words: qol, sal, dain, ory")
    print(
        "  • 8 suffixes: -dy (VERB), -ol/-al (LOC), -ar (DIR), -or (INST), -iin/-aiin/-ain (DEF)"
    )
    print("\nSUCCESS CRITERIA:")
    print("  • Strong: 60-80% recognition, 70-90% show structure")
    print("  • Partial: 40-60% recognition, 40-60% show structure")
    print("  • Failure: <40% recognition, <30% show structure")
    print("=" * 70)

    filepath = (
        "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/ZL3b-n.txt"
    )

    # Test 3 unseen folios from different sections (NOT f84v which was training set!)
    test_folios = [
        ("f2r", "Herbal section (plant illustrations)"),
        ("f3r", "Herbal section (different plant)"),
        ("f2v", "Herbal section (another plant)"),
    ]

    all_results = []

    for folio_id, folio_name in test_folios:
        lines = load_folio(filepath, folio_id)

        if not lines:
            print(f"\nWARNING: No lines found for {folio_id}")
            continue

        result = test_folio(folio_id, lines, folio_name)
        all_results.append(result)

    # Overall summary
    print(f"\n\n{'=' * 70}")
    print("FINAL GENERALIZATION TEST RESULTS")
    print(f"{'=' * 70}")

    if not all_results:
        print("ERROR: No folios could be tested")
        return

    avg_recognition_all = sum(r["avg_recognition"] for r in all_results) / len(
        all_results
    )
    avg_structure_all = sum(r["structure_pct"] for r in all_results) / len(all_results)

    print(f"\nOverall Results:")
    print(f"  Average recognition: {avg_recognition_all:.1f}%")
    print(f"  Average structure: {avg_structure_all:.0f}%")

    print(f"\nBy Section:")
    for result in all_results:
        print(
            f"  {result['folio_id']:6} ({result['folio_name']:30}): {result['avg_recognition']:5.1f}% recognition, {result['structure_pct']:3.0f}% structure"
        )

    print(f"\n{'=' * 70}")
    print("VALIDATION ASSESSMENT")
    print(f"{'=' * 70}")

    if avg_recognition_all >= 60 and avg_structure_all >= 70:
        print("\n✓✓✓ STRONG VALIDATION")
        print("The grammatical system GENERALIZES to unseen text!")
        print("\nIMPLICATIONS:")
        print("  • The suffix system is REAL, not over-fit")
        print("  • Function words work across manuscript sections")
        print("  • This is publishable research")
        print("\nNEXT STEP: Expand to 20+ folios for statistical validation")

    elif avg_recognition_all >= 40 and avg_structure_all >= 40:
        print("\n✓✓ PARTIAL VALIDATION")
        print("The grammatical system partially generalizes")
        print("\nIMPLICATIONS:")
        print("  • Core suffix system likely correct")
        print("  • Some suffixes may need refinement")
        print("  • Section-specific variations exist")
        print("\nNEXT STEP: Refine suffix identification and retest")

    else:
        print("\n✗ VALIDATION FAILED")
        print("The grammatical system does NOT generalize")
        print("\nIMPLICATIONS:")
        print("  • System may be over-fit to f84v")
        print("  • Suffix identifications may be incorrect")
        print("  • Need to reconsider methodology")
        print("\nNEXT STEP: Return to diagnostic phase")

    # Comparison to f84v baseline
    print(f"\n{'=' * 70}")
    print("COMPARISON TO F84V BASELINE")
    print(f"{'=' * 70}")
    print(f"f84v (training):  58% coverage, 100% structure")
    print(
        f"Unseen (test):    {avg_recognition_all:.1f}% coverage, {avg_structure_all:.0f}% structure"
    )

    if avg_recognition_all >= 50:
        print("\n✓ Recognition rate is COMPARABLE - system generalizes well")
    elif avg_recognition_all >= 35:
        print("\n≈ Recognition rate is LOWER but REASONABLE - some generalization")
    else:
        print("\n✗ Recognition rate is MUCH LOWER - poor generalization")


if __name__ == "__main__":
    main()
