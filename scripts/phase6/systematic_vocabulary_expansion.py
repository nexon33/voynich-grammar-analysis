"""
Phase 6: Systematic Vocabulary Expansion

NOW THAT GRAMMAR IS VALIDATED (92% structural coherence across 4 sections),
we can systematically decode semantic content.

STRATEGY:
1. Extract unknown roots from validated test sentences
2. Apply 8/8 evidence scoring to identify high-value targets
3. Use grammatical context to constrain semantic possibilities
4. Validate new terms and re-translate

GOAL: Expand from 6 validated nouns to 20-30 nouns for publication
"""

import re
from collections import defaultdict, Counter
import json


def load_voynich_text(filepath):
    """Load Voynich manuscript"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    all_words = []
    sections = defaultdict(list)
    current_section = "unknown"

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            # Check for section markers in comments
            if "# herbal" in line.lower():
                current_section = "herbal"
            elif "# pharmaceutical" in line.lower():
                current_section = "pharmaceutical"
            elif "# biological" in line.lower() or "# bath" in line.lower():
                current_section = "biological"
            elif "# astronomical" in line.lower() or "# cosmological" in line.lower():
                current_section = "astronomical"
            continue

        if line.startswith("<f"):
            # Extract text from ZL format
            match = re.search(r"<f\d+[rv]\d*\.[^>]+>\s+(.+)$", line)
            if match:
                text = match.group(1)
                # Remove markup
                text = re.sub(r"<[^>]+>", "", text)
                text = re.sub(r"\{[^}]+\}", "", text)
                text = re.sub(r"\[[^\]]+\]", "", text)
                text = re.sub(r"[@!]\d+;", "", text)
                # Extract words
                words = re.findall(r"[a-z!]+", text.lower())
                all_words.extend(words)
                sections[current_section].extend(words)

    return all_words, sections


def extract_unknown_roots_from_corpus(all_words, known_morphemes):
    """
    Extract potential roots by removing all known morphemes

    This identifies the SEMANTIC CONTENT we haven't decoded yet
    """

    # All known morphemes
    prefixes = ["qok", "qot", "ok", "ot"]  # Genitive + roots
    roots = ["shee", "she", "cho", "cheo", "dor"]  # Known semantic nouns
    function_words = ["qol", "sal", "dain", "ory"]
    suffixes = ["edy", "dy", "aiin", "iin", "ain", "al", "ar", "ol", "or"]

    unknown_roots = Counter()

    for word in all_words:
        remaining = word

        # Remove known prefixes
        for prefix in prefixes:
            if remaining.startswith(prefix):
                remaining = remaining[len(prefix) :]
                break

        # Remove known roots
        for root in roots:
            if root in remaining:
                remaining = remaining.replace(root, "", 1)

        # Remove function words
        for fw in function_words:
            if fw in remaining:
                remaining = remaining.replace(fw, "", 1)

        # Remove suffixes (iteratively, as they can stack)
        changed = True
        while changed:
            changed = False
            for suffix in sorted(suffixes, key=len, reverse=True):
                if suffix in remaining and len(remaining) > len(suffix):
                    remaining = remaining.replace(suffix, "", 1)
                    changed = True
                    break

        # What remains is likely a semantic root (or noise)
        if remaining and len(remaining) > 1:
            # Filter out single letters and common noise
            if remaining not in [
                "k",
                "ch",
                "p",
                "s",
                "l",
                "d",
                "y",
                "e",
                "t",
                "c",
                "h",
                "f",
            ]:
                unknown_roots[remaining] += 1

    return unknown_roots


def analyze_candidate_root(root, all_words, sections, validated_roots):
    """
    Apply 8/8 evidence scoring to candidate root

    Returns score and evidence dict
    """

    # Find all words containing this root
    instances = [w for w in all_words if root in w]

    if len(instances) < 20:
        return 0, {"note": "Insufficient frequency (<20 instances)"}

    evidence = {
        "root": root,
        "total_instances": len(instances),
        "frequency_pct": len(instances) / len(all_words) * 100,
    }

    score = 0

    # 1. Co-occurrence with validated roots (max 2 points)
    cooccur = defaultdict(int)
    for i, word in enumerate(all_words):
        if root in word:
            # Check window
            start = max(0, i - 3)
            end = min(len(all_words), i + 4)
            for j in range(start, end):
                if j != i:
                    for val_root in validated_roots:
                        if val_root in all_words[j]:
                            cooccur[val_root] += 1

    total_cooccur = sum(cooccur.values())
    evidence["cooccurrence"] = {"total": total_cooccur, "detail": dict(cooccur)}

    if total_cooccur > 200:
        score += 2
    elif total_cooccur > 100:
        score += 1

    # 2. Section enrichment (max 2 points)
    total_words = sum(len(words) for words in sections.values())
    total_root_count = sum(
        sum(1 for w in words if root in w) for words in sections.values()
    )
    global_rate = (total_root_count / total_words * 1000) if total_words > 0 else 0

    enrichments = {}
    for section, words in sections.items():
        if section == "unknown":
            continue
        section_count = sum(1 for w in words if root in w)
        section_rate = (section_count / len(words) * 1000) if len(words) > 0 else 0

        if global_rate > 0 and section_rate > global_rate * 1.5:
            enrichment = section_rate / global_rate
            enrichments[section] = enrichment

    max_enrichment = max(enrichments.values()) if enrichments else 1.0
    evidence["enrichment"] = {"max": max_enrichment, "by_section": enrichments}

    if max_enrichment > 10:
        score += 2
    elif max_enrichment > 5:
        score += 1

    # 3. Case-marking rate (max 2 points)
    case_suffixes = ["al", "ar", "ol", "or"]
    with_case = sum(
        1 for w in instances if any(w.endswith(case) for case in case_suffixes)
    )
    case_rate = (with_case / len(instances) * 100) if instances else 0

    evidence["case_rate"] = case_rate

    if 30 <= case_rate <= 60:
        score += 2
    elif (15 <= case_rate < 30) or (60 < case_rate <= 80):
        score += 1

    # 4. Verbal rate (max 2 points)
    with_verbal = sum(1 for w in instances if "dy" in w or "edy" in w)
    verbal_rate = (with_verbal / len(instances) * 100) if instances else 0

    evidence["verbal_rate"] = verbal_rate

    if verbal_rate < 15:
        score += 2
    elif verbal_rate < 25:
        score += 1

    evidence["score"] = score
    evidence["sample_instances"] = instances[:20]

    return score, evidence


def main():
    print("=" * 70)
    print("PHASE 6: SYSTEMATIC VOCABULARY EXPANSION")
    print("=" * 70)
    print("\nGOAL: Expand from 6 validated nouns to 20-30 nouns")
    print("\nSTRATEGY:")
    print("1. Extract unknown roots from corpus")
    print("2. Score candidates using 8/8 evidence system")
    print("3. Prioritize high-scoring targets (6-8/8)")
    print("4. Validate semantically using context")
    print("=" * 70)

    # Load data
    filepath = (
        "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/ZL3b-n.txt"
    )
    all_words, sections = load_voynich_text(filepath)

    print(f"\nLoaded {len(all_words)} words")
    print(f"Sections: {', '.join(s for s in sections.keys() if s != 'unknown')}")

    # Known morphemes
    known_morphemes = {
        "roots": ["ok", "qok", "ot", "qot", "shee", "she", "dor", "cho", "cheo"],
        "function_words": ["qol", "sal", "dain", "ory"],
        "suffixes": ["edy", "dy", "aiin", "iin", "ain", "al", "ar", "ol", "or"],
    }

    validated_roots = ["ok", "qok", "ot", "qot", "shee", "she", "dor", "cho", "cheo"]

    print("\nCurrently validated semantic nouns: 6")
    print("  - oak (ok/qok)")
    print("  - oat (ot/qot)")
    print("  - water (shee/she)")
    print("  - red (dor)")
    print("  - vessel (cho)")
    print("  - cheo")

    # Extract unknown roots
    print("\n" + "=" * 70)
    print("EXTRACTING UNKNOWN ROOTS FROM CORPUS")
    print("=" * 70)

    unknown_roots = extract_unknown_roots_from_corpus(all_words, known_morphemes)

    print(f"\nFound {len(unknown_roots)} potential semantic roots")
    print(f"\nTop 30 by frequency:")
    for i, (root, count) in enumerate(unknown_roots.most_common(30), 1):
        freq_pct = count / len(all_words) * 100
        print(f"{i:2}. {root:15} ({count:4} instances, {freq_pct:.2f}%)")

    # Score top candidates
    print("\n" + "=" * 70)
    print("SCORING TOP CANDIDATES (8/8 EVIDENCE SYSTEM)")
    print("=" * 70)

    candidates_to_test = [
        root for root, count in unknown_roots.most_common(50) if count >= 20
    ]

    scored_candidates = []

    for root in candidates_to_test[:20]:  # Test top 20
        score, evidence = analyze_candidate_root(
            root, all_words, sections, validated_roots
        )

        if score >= 4:  # Only show promising candidates
            scored_candidates.append((root, score, evidence))

            print(f"\n{root} - SCORE: {score}/8")
            print(
                f"  Instances: {evidence['total_instances']} ({evidence['frequency_pct']:.2f}%)"
            )
            print(f"  Co-occurrence: {evidence['cooccurrence']['total']}")
            print(f"  Max enrichment: {evidence['enrichment']['max']:.1f}x")
            if evidence["enrichment"]["by_section"]:
                enriched_sections = ", ".join(
                    f"{s}({e:.1f}x)"
                    for s, e in evidence["enrichment"]["by_section"].items()
                )
                print(f"    Enriched in: {enriched_sections}")
            print(f"  Case-marking: {evidence['case_rate']:.1f}%")
            print(f"  Verbal rate: {evidence['verbal_rate']:.1f}%")

    # Sort by score
    scored_candidates.sort(key=lambda x: x[1], reverse=True)

    # Summary
    print("\n" + "=" * 70)
    print("TOP CANDIDATES FOR VALIDATION")
    print("=" * 70)

    print(f"\nHigh priority (6-8/8 score):")
    high_priority = [c for c in scored_candidates if c[1] >= 6]
    for root, score, evidence in high_priority:
        print(f"  {root:15} {score}/8 - {evidence['total_instances']} instances")

    print(f"\nMedium priority (4-5/8 score):")
    medium_priority = [c for c in scored_candidates if 4 <= c[1] < 6]
    for root, score, evidence in medium_priority:
        print(f"  {root:15} {score}/8 - {evidence['total_instances']} instances")

    # Save results
    output = {
        "summary": {
            "total_unknown_roots": len(unknown_roots),
            "candidates_tested": len(candidates_to_test),
            "high_priority": len(high_priority),
            "medium_priority": len(medium_priority),
        },
        "high_priority_candidates": [
            {"root": root, "score": score, "evidence": evidence}
            for root, score, evidence in high_priority
        ],
        "medium_priority_candidates": [
            {"root": root, "score": score, "evidence": evidence}
            for root, score, evidence in medium_priority
        ],
    }

    output_path = (
        "C:/Users/adria/Documents/manuscript/phase6_vocabulary_candidates.json"
    )
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n\nResults saved to: {output_path}")

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("1. Manually inspect high-priority candidates (6-8/8 score)")
    print("2. Use grammatical context to constrain semantic possibilities")
    print("3. Look for visual correlations in illustrations")
    print("4. Test hypotheses and validate")
    print("5. Re-translate test sentences with expanded vocabulary")


if __name__ == "__main__":
    main()
