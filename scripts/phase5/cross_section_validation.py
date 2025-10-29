"""
Phase 5A: Critical Cross-Section Validation Test

QUESTION: Does the grammatical system work across ALL manuscript sections?

TEST DESIGN:
- Phase 5A tested herbal section only (f2r, f3r, f2v)
- This test: astronomical, pharmaceutical, biological sections
- Same fixed grammar (NO modifications)
- Measure if grammar is universal or section-specific

HYPOTHESIS: Grammar is universal across manuscript

SUCCESS CRITERIA:
- Strong: All 3 sections show 80%+ structural coherence
- Partial: 2/3 sections show 80%+ structural coherence
- Failure: Only 1/3 or 0/3 sections show 80%+ coherence

If STRONG → grammar is universal → publishable breakthrough
If PARTIAL → mostly universal with variation → still publishable
If FAILURE → may be herbal-specific → need to reconsider

FIXED GRAMMATICAL SYSTEM (same as Phase 5A, no changes):
- 6 semantic nouns: oak, oat, water, red, vessel, cheo
- 4 function words: qol, sal, dain, ory
- 8 suffixes: -dy (VERB), -ol/-al (LOC), -ar (DIR), -or (INST), -iin/-aiin/-ain (DEF)
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

        # Check for folio marker (e.g., <f68r>, <f89r>, <f78r>)
        if f"<{folio_id}>" in line_stripped:
            in_folio = True
            continue
        elif line_stripped.startswith("<f") and ">" in line_stripped and in_folio:
            # Check if this is a different folio (not just a line marker)
            if re.match(r"^<f\d+[rv]>", line_stripped):
                # Reached next folio
                break

        # Process lines within the folio
        if in_folio:
            # Skip comments and section headers
            if line_stripped.startswith("#") or not line_stripped:
                continue

            # Extract text from ZL format
            if line_stripped.startswith("<f"):
                match = re.search(r"<f\d+[rv]\.[^>]+>\s+(.+)$", line_stripped)
                if match:
                    text = match.group(1)
                    # Remove markup
                    text = re.sub(r"<[^>]+>", "", text)
                    text = re.sub(r"\{[^}]+\}", "", text)
                    text = re.sub(r"\[[^\]]+\]", "", text)
                    text = re.sub(r"!@\d+;", "", text)
                    text = re.sub(r"@\d+;", "", text)
                    # Extract words
                    words = re.findall(r"[a-z!]+", text.lower())
                    if words:
                        folio_lines.append(" ".join(words))

    return folio_lines


def parse_word_fixed_grammar(word):
    """Parse word using FIXED grammatical system (no modifications allowed)"""
    components = {
        "roots": [],
        "function_words": [],
        "suffixes": [],
        "unknown": [],
    }

    remaining = word

    # 1. Semantic roots
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

    # 2. Function words
    if "qol" in remaining:
        components["function_words"].append("THEN")
        remaining = remaining.replace("qol", "", 1)

    if "sal" in remaining:
        components["function_words"].append("AND")
        remaining = remaining.replace("sal", "", 1)

    if "dain" in remaining or "dai!n" in remaining:
        components["function_words"].append("THAT")
        remaining = remaining.replace("dain", "", 1).replace("dai!n", "", 1)

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

    # 6. Unknown remainder
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
    """Assess if sentence shows clear grammatical structure"""
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
        "has_structure": structure_score >= 2,
        "score": structure_score,
        "has_roots": has_roots,
        "has_suffixes": has_suffixes,
        "has_case_or_verbal": has_case or has_verbal,
        "has_function_words": has_function,
    }


def test_folio(folio_id, lines, folio_name, section_type):
    """Test grammatical system on a single folio"""

    print(f"\n{'=' * 70}")
    print(f"TESTING: {folio_id} ({folio_name})")
    print(f"SECTION: {section_type}")
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
        "section_type": section_type,
        "avg_recognition": avg_recognition,
        "structure_pct": structure_pct,
        "lines_tested": len(test_lines),
        "results": results,
    }


def main():
    print("=" * 70)
    print("PHASE 5A: CRITICAL CROSS-SECTION VALIDATION")
    print("=" * 70)
    print("\nQUESTION: Does grammar work across ALL manuscript sections?")
    print("\nPREVIOUS TEST: Herbal section only (f2r, f3r, f2v)")
    print("  Result: 51% recognition, 97% structure")
    print("\nTHIS TEST: Astronomical, Pharmaceutical, Biological sections")
    print("\nFIXED SYSTEM (no modifications):")
    print("  • 6 semantic nouns: oak, oat, water, red, vessel, cheo")
    print("  • 4 function words: qol, sal, dain, ory")
    print("  • 8 suffixes: -dy, -ol/-al, -ar, -or, -iin/-aiin/-ain")
    print("\nSUCCESS CRITERIA:")
    print("  • Strong: All 3 sections show 80%+ structural coherence")
    print("  • Partial: 2/3 sections show 80%+ structural coherence")
    print("  • Failure: 0-1/3 sections show 80%+ structural coherence")
    print("=" * 70)

    filepath = (
        "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/ZL3b-n.txt"
    )

    # Test 3 sections: astronomical, pharmaceutical, biological
    test_folios = [
        ("f67r2", "Astronomical (circular diagram with sectors)", "Astronomical"),
        ("f88r", "Pharmaceutical (labeled roots)", "Pharmaceutical"),
        ("f78r", "Biological (bath scene, different from f84v)", "Biological"),
    ]

    all_results = []

    for folio_id, folio_name, section_type in test_folios:
        lines = load_folio(filepath, folio_id)

        if not lines:
            print(f"\nWARNING: No lines found for {folio_id}, trying without suffix...")
            # Try without the suffix (e.g., f68r instead of f68r3)
            base_folio = folio_id.rstrip("0123456789")
            lines = load_folio(filepath, base_folio)
            if lines:
                print(f"SUCCESS: Found {base_folio}")
                folio_id = base_folio

        if not lines:
            print(f"\nERROR: Could not load {folio_id}")
            continue

        result = test_folio(folio_id, lines, folio_name, section_type)
        all_results.append(result)

    # Overall summary
    print(f"\n\n{'=' * 70}")
    print("CROSS-SECTION VALIDATION RESULTS")
    print(f"{'=' * 70}")

    if not all_results:
        print("ERROR: No folios could be tested")
        return

    avg_recognition_all = sum(r["avg_recognition"] for r in all_results) / len(
        all_results
    )
    avg_structure_all = sum(r["structure_pct"] for r in all_results) / len(all_results)

    print(f"\nOverall Results Across All Sections:")
    print(f"  Average recognition: {avg_recognition_all:.1f}%")
    print(f"  Average structure: {avg_structure_all:.0f}%")

    print(f"\nBy Section:")
    for result in all_results:
        print(
            f"  {result['section_type']:20} ({result['folio_id']:6}): {result['avg_recognition']:5.1f}% recognition, {result['structure_pct']:3.0f}% structure"
        )

    # Count sections with 80%+ structure
    strong_sections = sum(1 for r in all_results if r["structure_pct"] >= 80)

    print(f"\n{'=' * 70}")
    print("VALIDATION VERDICT")
    print(f"{'=' * 70}")

    print(
        f"\nSections with 80%+ structural coherence: {strong_sections}/{len(all_results)}"
    )

    if strong_sections == len(all_results):
        print("\n✓✓✓ STRONG VALIDATION - GRAMMAR IS UNIVERSAL")
        print("All sections show consistent grammatical structure!")
        print("\nIMPLICATIONS:")
        print("  • Grammar works across entire manuscript")
        print("  • Not section-specific or domain-specific")
        print("  • This is a UNIVERSAL grammatical system")
        print("  • READY FOR PUBLICATION")
        print("\nRECOMMENDATION:")
        print("  → Proceed to write research paper")
        print("  → Expand to 100+ lines for statistical power")
        print("  → Submit for peer review")

    elif strong_sections >= 2:
        print("\n✓✓ PARTIAL VALIDATION - MOSTLY UNIVERSAL")
        print("Majority of sections show grammatical structure")
        print("\nIMPLICATIONS:")
        print("  • Grammar mostly universal with some variation")
        print("  • May be section-specific differences")
        print("  • Still publishable with caveats")
        print("\nRECOMMENDATION:")
        print("  → Document section differences")
        print("  → Test additional folios from weak section")
        print("  → Proceed to publication with noted limitations")

    else:
        print("\n✗ VALIDATION FAILED - NOT UNIVERSAL")
        print("Grammar does not generalize across sections")
        print("\nIMPLICATIONS:")
        print("  • May be herbal-section-specific")
        print("  • Different sections may have different grammar")
        print("  • Need to reconsider universality claim")
        print("\nRECOMMENDATION:")
        print("  → Document as herbal-section grammar")
        print("  → Investigate section-specific patterns")
        print("  → More limited publication scope")

    # Comparison to herbal baseline
    print(f"\n{'=' * 70}")
    print("COMPARISON TO HERBAL SECTION (BASELINE)")
    print(f"{'=' * 70}")
    print(f"Herbal (f2r/f3r/f2v):  51% recognition, 97% structure")
    print(
        f"Cross-section test:    {avg_recognition_all:.1f}% recognition, {avg_structure_all:.0f}% structure"
    )

    recog_diff = avg_recognition_all - 51
    struct_diff = avg_structure_all - 97

    if abs(recog_diff) <= 10:
        print(f"\n✓ Recognition is COMPARABLE ({recog_diff:+.1f}% difference)")
    else:
        print(f"\n⚠ Recognition differs significantly ({recog_diff:+.1f}% difference)")

    if abs(struct_diff) <= 10:
        print(f"✓ Structure is COMPARABLE ({struct_diff:+.0f}% difference)")
    else:
        print(f"⚠ Structure differs significantly ({struct_diff:+.0f}% difference)")


if __name__ == "__main__":
    main()
