#!/usr/bin/env python3
"""
Comprehensive Validated Vocabulary Extraction

Systematically extracts ALL validated and near-validated elements from ALL phase documents.
Creates a complete inventory of:
1. Validated elements (≥8/10)
2. Near-validated elements (6-7/10)
3. Elements mentioned but not validated
4. Missed opportunities for validation
"""

import re
import os
from collections import defaultdict


def extract_from_phase10(filepath):
    """Extract validated and near-validated from Phase 10."""
    results = {"validated": [], "near_validated": [], "phase": 10}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract validated elements table
        validated_pattern = r"\| \*\*(\w+)\*\* \| Root \| (\d+)/10 \| (\d+) \|"
        for match in re.finditer(validated_pattern, content):
            element, score, freq = match.groups()
            score_val = int(score)
            if score_val >= 8:
                results["validated"].append(
                    {
                        "element": element,
                        "score": f"{score}/10",
                        "frequency": int(freq),
                        "type": "root",
                        "phase": 10,
                    }
                )

        # Extract near-validated elements
        near_val_section = re.search(
            r"## Near-Validated Elements.*?\n(.*?)\n##", content, re.DOTALL
        )
        if near_val_section:
            near_val_text = near_val_section.group(1)
            near_pattern = r"\| \*\*(\w+)\*\* \| (\d+)/10 \| (\d+) \|"
            for match in re.finditer(near_pattern, near_val_text):
                element, score, freq = match.groups()
                if int(score) == 7:
                    results["near_validated"].append(
                        {
                            "element": element,
                            "score": f"{score}/10",
                            "frequency": int(freq),
                            "type": "root",
                            "phase": 10,
                            "reason": "Near-validated in Phase 10",
                        }
                    )

        print(
            f"Phase 10: Found {len(results['validated'])} validated, {len(results['near_validated'])} near-validated"
        )
        return results
    except FileNotFoundError:
        print(f"Phase 10 file not found: {filepath}")
        return results


def extract_from_phase11(filepath):
    """Extract validated and near-validated from Phase 11."""
    results = {"validated": [], "near_validated": [], "phase": 11}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract validated elements table
        validated_pattern = r"\| \*\*(\w+)\*\* \| (\w+) \| (\d+)/10 \| (\d+) \|"
        for match in re.finditer(validated_pattern, content):
            element, elem_type, score, freq = match.groups()
            score_val = int(score)
            if score_val >= 8:
                results["validated"].append(
                    {
                        "element": element,
                        "score": f"{score}/10",
                        "frequency": int(freq),
                        "type": elem_type.lower(),
                        "phase": 11,
                    }
                )

        # Extract near-validated
        near_val_section = re.search(
            r"## Near-Validated Elements.*?\n(.*?)\n##", content, re.DOTALL
        )
        if near_val_section:
            near_val_text = near_val_section.group(1)
            near_pattern = r"\| \*\*(\w+)\*\* \| (\d+)/10 \| (\d+) \|"
            for match in re.finditer(near_pattern, near_val_text):
                element, score, freq = match.groups()
                if int(score) == 7:
                    # Check if persistent from Phase 10
                    if (
                        "Persistent" in near_val_text
                        or "keol" in element
                        or "olkedy" in element
                        or "cthor" in element
                    ):
                        reason = "Persistent near-validated (Phase 10-11)"
                    else:
                        reason = "New near-validated in Phase 11"

                    results["near_validated"].append(
                        {
                            "element": element,
                            "score": f"{score}/10",
                            "frequency": int(freq),
                            "type": "root",
                            "phase": 11,
                            "reason": reason,
                        }
                    )

        print(
            f"Phase 11: Found {len(results['validated'])} validated, {len(results['near_validated'])} near-validated"
        )
        return results
    except FileNotFoundError:
        print(f"Phase 11 file not found: {filepath}")
        return results


def extract_from_phase12(filepath):
    """Extract prefix validation from Phase 12."""
    results = {"validated": [], "near_validated": [], "compounds": [], "phase": 12}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract validated prefix
        if "ol-" in content and "10/10" in content:
            ol_match = re.search(r"ol-.*?(\d+) uses", content, re.IGNORECASE)
            if ol_match:
                results["validated"].append(
                    {
                        "element": "ol",
                        "score": "10/10",
                        "frequency": int(ol_match.group(1)),
                        "type": "prefix",
                        "phase": 12,
                        "note": "Locative prefix",
                    }
                )

        # Extract near-validated prefix
        ot_match = re.search(
            r"\*\*ot-\*\*.*?7/10.*?(\d+) uses", content, re.IGNORECASE | re.DOTALL
        )
        if ot_match:
            results["near_validated"].append(
                {
                    "element": "ot",
                    "score": "7/10",
                    "frequency": int(ot_match.group(1)),
                    "type": "prefix",
                    "phase": 12,
                    "reason": "Low validated combination rate (4.1%), later discovered as allomorph in Phase 13",
                }
            )

        # Extract ct- (below threshold)
        ct_match = re.search(
            r"\*\*ct-\*\*.*?5/10.*?(\d+) uses", content, re.IGNORECASE | re.DOTALL
        )
        if ct_match:
            results["near_validated"].append(
                {
                    "element": "ct",
                    "score": "5/10",
                    "frequency": int(ct_match.group(1)),
                    "type": "prefix",
                    "phase": 12,
                    "reason": "Only 67 unique stems, 0% validated combinations",
                }
            )

        # Extract compound resolutions
        if "OLKEDY = OL- + KEDY" in content:
            results["compounds"].append(
                {
                    "compound": "olkedy",
                    "structure": "ol- + kedy",
                    "score": "9/10 (as compound)",
                    "phase": 12,
                    "note": "Previously scored 7/10 as single element",
                }
            )

        if "OLCHEDY = OL- + CHEDY" in content:
            results["compounds"].append(
                {
                    "compound": "olchedy",
                    "structure": "ol- + chedy",
                    "score": "9/10 (as compound)",
                    "phase": 12,
                    "note": "Previously scored 7/10 as single element",
                }
            )

        print(
            f"Phase 12: Found {len(results['validated'])} validated prefixes, {len(results['near_validated'])} near-validated, {len(results['compounds'])} compounds"
        )
        return results
    except FileNotFoundError:
        print(f"Phase 12 file not found: {filepath}")
        return results


def extract_from_phase14(filepath):
    """Extract vowel-initial roots from Phase 14."""
    results = {"validated": [], "insufficient_data": [], "phase": 14}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract validated elements
        validated_section = re.search(
            r"VALIDATED ELEMENTS:(.*?)(?:Results saved|Phase 14B complete)",
            content,
            re.DOTALL,
        )
        if validated_section:
            validated_text = validated_section.group(1)
            val_pattern = r"(\w+): (\d+)/10 - (\d+) uses"
            for match in re.finditer(val_pattern, validated_text):
                element, score, freq = match.groups()
                results["validated"].append(
                    {
                        "element": element,
                        "score": f"{score}/10",
                        "frequency": int(freq),
                        "type": "v-initial root",
                        "phase": 14,
                    }
                )

        # Extract insufficient data elements
        insufficient_pattern = r"(\w+).*?INSUFFICIENT DATA"
        for match in re.finditer(insufficient_pattern, content):
            element = match.group(1).lower()
            if element in ["edy", "eey", "eedy", "eeedy"]:
                results["insufficient_data"].append(
                    {
                        "element": element,
                        "reason": "n<20 (insufficient data for validation)",
                        "phase": 14,
                        "note": "High ot- compound frequency but low standalone usage",
                    }
                )

        print(
            f"Phase 14: Found {len(results['validated'])} validated, {len(results['insufficient_data'])} insufficient data"
        )
        return results
    except FileNotFoundError:
        print(f"Phase 14 file not found: {filepath}")
        return results


def extract_from_complete_vocab(filepath):
    """Extract complete 47-element list from COMPLETE_VALIDATED_VOCABULARY.md."""
    results = {
        "prefixes": [],
        "roots": [],
        "function_words": [],
        "particles": [],
        "compounds": [],
    }

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # This file has our authoritative 47-element list
        # We can use this as the baseline

        # Extract from sections
        sections = {
            "Prefixes": "prefixes",
            "Consonant-Initial Roots": "roots",
            "Vowel-Initial Roots": "roots",
            "Function Words": "function_words",
            "Particles": "particles",
            "Validated Compounds": "compounds",
        }

        # Count elements in each section
        for section_name, result_key in sections.items():
            section_match = re.search(
                f"## {section_name}.*?(?=##|$)", content, re.DOTALL
            )
            if section_match:
                section_text = section_match.group(0)
                # Count ### subsections (each element has ### heading)
                element_count = len(
                    re.findall(r"^### \d+\.", section_text, re.MULTILINE)
                )
                results[result_key].append(
                    {"count": element_count, "section": section_name}
                )

        print(
            f"Complete vocab: {sum(r[0]['count'] if r else 0 for r in results.values())} elements documented"
        )
        return results
    except FileNotFoundError:
        print(f"Complete vocab file not found: {filepath}")
        return results


def find_phase_documents():
    """Find all phase validation documents."""
    base_dir = "."
    phase_files = {
        "phase10": "PHASE10_VALIDATION_RESULTS.md",
        "phase11": "PHASE11_VALIDATION_RESULTS.md",
        "phase12": "PHASE12_PREFIX_VALIDATION.md",
        "phase14": "PHASE14B_VALIDATION_RESULTS.md",
        "complete": "COMPLETE_VALIDATED_VOCABULARY.md",
    }

    found_files = {}
    for phase, filename in phase_files.items():
        filepath = os.path.join(base_dir, filename)
        if os.path.exists(filepath):
            found_files[phase] = filepath
        else:
            print(f"Warning: {filename} not found")

    return found_files


def compile_missed_vocabulary(all_results):
    """Compile complete list of missed/near-validated vocabulary."""
    missed = {
        "near_validated_persistent": [],  # Scored 7/10 multiple times
        "near_validated_single": [],  # Scored 7/10 once
        "below_threshold": [],  # Scored 5-6/10
        "insufficient_data": [],  # n<20
    }

    # Track which elements appear multiple times at 7/10
    near_val_counts = defaultdict(int)
    near_val_details = defaultdict(list)

    for phase_name, results in all_results.items():
        if "near_validated" in results:
            for item in results["near_validated"]:
                element = item["element"]
                near_val_counts[element] += 1
                near_val_details[element].append(
                    {
                        "phase": item["phase"],
                        "score": item["score"],
                        "frequency": item.get("frequency"),
                        "reason": item.get("reason", "Unknown"),
                    }
                )

        if "insufficient_data" in results:
            missed["insufficient_data"].extend(results["insufficient_data"])

    # Categorize near-validated elements
    for element, count in near_val_counts.items():
        details = near_val_details[element]
        if count >= 2:
            missed["near_validated_persistent"].append(
                {
                    "element": element,
                    "appearances": count,
                    "phases": [d["phase"] for d in details],
                    "details": details,
                }
            )
        else:
            missed["near_validated_single"].append(
                {
                    "element": element,
                    "phase": details[0]["phase"],
                    "details": details[0],
                }
            )

    return missed


def generate_report(all_results, missed_vocab):
    """Generate comprehensive report."""
    report = []

    report.append("=" * 80)
    report.append("COMPREHENSIVE VALIDATED VOCABULARY EXTRACTION")
    report.append("=" * 80)
    report.append("")

    # Summary statistics
    report.append("## SUMMARY STATISTICS")
    report.append("")

    total_validated = 0
    for phase_name, results in all_results.items():
        if "validated" in results:
            count = len(results["validated"])
            total_validated += count
            report.append(
                f"Phase {results.get('phase', phase_name)}: {count} validated elements"
            )

    report.append(f"\n**Total validated elements found**: {total_validated}")
    report.append("")

    # Missed vocabulary
    report.append("=" * 80)
    report.append("## MISSED VOCABULARY OPPORTUNITIES")
    report.append("=" * 80)
    report.append("")

    # Persistent near-validated (highest priority)
    report.append(
        "### HIGH PRIORITY: Persistent Near-Validated Elements (7/10 multiple phases)"
    )
    report.append("")
    if missed_vocab["near_validated_persistent"]:
        for item in missed_vocab["near_validated_persistent"]:
            report.append(f"**{item['element'].upper()}**")
            report.append(
                f"  - Appearances: {item['appearances']} phases {item['phases']}"
            )
            for detail in item["details"]:
                report.append(
                    f"  - Phase {detail['phase']}: {detail['score']}, n={detail.get('frequency', 'unknown')}, Reason: {detail['reason']}"
                )
            report.append("")
    else:
        report.append("  None found")
        report.append("")

    # Single near-validated
    report.append("### MEDIUM PRIORITY: Single Near-Validated Elements (7/10 once)")
    report.append("")
    if missed_vocab["near_validated_single"]:
        for item in missed_vocab["near_validated_single"]:
            report.append(f"**{item['element']}** (Phase {item['phase']})")
            report.append(f"  - Score: {item['details']['score']}")
            report.append(
                f"  - Frequency: {item['details'].get('frequency', 'unknown')}"
            )
            report.append(f"  - Reason: {item['details']['reason']}")
            report.append("")
    else:
        report.append("  None found")
        report.append("")

    # Insufficient data
    report.append("### LOW PRIORITY: Insufficient Data (n<20)")
    report.append("")
    if missed_vocab["insufficient_data"]:
        for item in missed_vocab["insufficient_data"]:
            report.append(f"**{item['element']}** (Phase {item['phase']})")
            report.append(f"  - Reason: {item['reason']}")
            report.append(f"  - Note: {item.get('note', 'N/A')}")
            report.append("")
    else:
        report.append("  None found")
        report.append("")

    return "\n".join(report)


def main():
    print("Starting comprehensive vocabulary extraction...\n")

    # Find all phase documents
    phase_files = find_phase_documents()
    print(f"Found {len(phase_files)} phase documents\n")

    # Extract from each phase
    all_results = {}

    if "phase10" in phase_files:
        all_results["phase10"] = extract_from_phase10(phase_files["phase10"])

    if "phase11" in phase_files:
        all_results["phase11"] = extract_from_phase11(phase_files["phase11"])

    if "phase12" in phase_files:
        all_results["phase12"] = extract_from_phase12(phase_files["phase12"])

    if "phase14" in phase_files:
        all_results["phase14"] = extract_from_phase14(phase_files["phase14"])

    if "complete" in phase_files:
        all_results["complete"] = extract_from_complete_vocab(phase_files["complete"])

    print("\n" + "=" * 80)

    # Compile missed vocabulary
    missed_vocab = compile_missed_vocabulary(all_results)

    # Generate report
    report = generate_report(all_results, missed_vocab)

    # Print report
    print(report)

    # Save to file
    output_file = "MISSED_VOCABULARY_ANALYSIS.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n\nReport saved to: {output_file}")

    # Summary of findings
    total_persistent = len(missed_vocab["near_validated_persistent"])
    total_single = len(missed_vocab["near_validated_single"])
    total_insufficient = len(missed_vocab["insufficient_data"])

    print(f"\n{'=' * 80}")
    print("FINAL SUMMARY")
    print(f"{'=' * 80}")
    print(f"Persistent near-validated (7/10 multiple phases): {total_persistent}")
    print(f"Single near-validated (7/10 once): {total_single}")
    print(f"Insufficient data (n<20): {total_insufficient}")
    print(
        f"\n**Total missed opportunities**: {total_persistent + total_single + total_insufficient}"
    )


if __name__ == "__main__":
    main()
