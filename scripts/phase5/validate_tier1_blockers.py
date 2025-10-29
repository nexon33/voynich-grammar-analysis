"""
Phase 5A: Validate Tier 1 Blocking Words

Tests the 4 critical blocking words from failed translation sentences:
- qol (sentences 2, 4)
- ory (sentence 2, 15.8x enriched)
- sal (sentence 2)
- dai!n (sentence 4, possible pronoun)

Uses 8/8 evidence scoring system:
1. Co-occurrence with validated nouns (>100 = +1, >200 = +2)
2. Section enrichment (>5x = +1, >10x = +2)
3. Case-marking rate (30-60% = +2, 15-30% or 60-80% = +1)
4. Verbal rate (<15% = +2, 15-25% = +1)

6-8/8 = VALIDATED NOUN → add to vocabulary
3-5/8 = AMBIGUOUS → needs more investigation
0-2/8 = FUNCTION WORD → confirms bottleneck hypothesis
"""

import re
from collections import defaultdict, Counter
import json


def load_voynich_text(filepath):
    """Load and parse Voynich manuscript"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    all_words = []
    sections = defaultdict(list)
    current_section = None

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Section headers
        if line.startswith("<"):
            match = re.search(r"<([^>]+)>", line)
            if match:
                current_section = match.group(1).split(".")[0]
            continue

        # Extract words
        words = re.findall(r"[a-z!]+", line.lower())
        all_words.extend(words)
        if current_section:
            sections[current_section].extend(words)

    return all_words, sections


def find_root_instances(root, words):
    """Find all instances containing root"""
    instances = []
    for word in words:
        if root in word:
            instances.append(word)
    return instances


def analyze_morphology(root, all_words):
    """Analyze case-marking and verbal rates"""
    instances = find_root_instances(root, all_words)

    if not instances:
        return 0, 0, 0, 0

    case_suffixes = ["al", "ar", "ol", "or"]
    with_case = 0
    with_verbal = 0
    bare = 0

    for word in instances:
        if any(word.endswith(case) for case in case_suffixes):
            with_case += 1
        elif "edy" in word or "dy" == word[-2:]:
            with_verbal += 1
        elif word == root:
            bare += 1

    total = len(instances)
    case_rate = (with_case / total * 100) if total > 0 else 0
    verbal_rate = (with_verbal / total * 100) if total > 0 else 0

    return case_rate, verbal_rate, total, instances


def calculate_cooccurrence(root, all_words, validated_roots, window=3):
    """Calculate co-occurrence with validated nouns"""
    cooccur = defaultdict(int)
    root_positions = []

    # Find all positions of root
    for i, word in enumerate(all_words):
        if root in word:
            root_positions.append(i)

    # Check window around each instance
    for pos in root_positions:
        start = max(0, pos - window)
        end = min(len(all_words), pos + window + 1)

        for j in range(start, end):
            if j != pos:
                for validated in validated_roots:
                    if validated in all_words[j]:
                        cooccur[validated] += 1

    total_cooccur = sum(cooccur.values())
    return total_cooccur, dict(cooccur)


def calculate_section_enrichment(root, sections):
    """Calculate section-specific enrichment"""
    # Calculate global frequency
    total_words = sum(len(words) for words in sections.values())
    total_root_count = sum(
        sum(1 for w in words if root in w) for words in sections.values()
    )
    global_rate = (total_root_count / total_words * 1000) if total_words > 0 else 0

    # Calculate per-section enrichment
    enrichments = {}
    for section, words in sections.items():
        section_count = sum(1 for w in words if root in w)
        section_rate = (section_count / len(words) * 1000) if len(words) > 0 else 0

        if global_rate > 0:
            enrichment = section_rate / global_rate
            if enrichment > 1.5:  # Only track notable enrichments
                enrichments[section] = enrichment

    max_enrichment = max(enrichments.values()) if enrichments else 1.0
    return max_enrichment, enrichments


def score_evidence(root, all_words, sections, validated_roots):
    """Score using 8/8 evidence system"""

    print(f"\n{'=' * 60}")
    print(f"VALIDATING: {root}")
    print(f"{'=' * 60}")

    score = 0
    evidence = {}

    # 1. Co-occurrence test (max 2 points)
    total_cooccur, cooccur_detail = calculate_cooccurrence(
        root, all_words, validated_roots
    )
    evidence["cooccurrence"] = {"total": total_cooccur, "detail": cooccur_detail}

    if total_cooccur > 200:
        score += 2
        print(f"✓✓ Co-occurrence: {total_cooccur} (>200) [+2 points]")
    elif total_cooccur > 100:
        score += 1
        print(f"✓ Co-occurrence: {total_cooccur} (>100) [+1 point]")
    else:
        print(f"✗ Co-occurrence: {total_cooccur} (<100) [+0 points]")

    # 2. Section enrichment test (max 2 points)
    max_enrichment, enrichment_detail = calculate_section_enrichment(root, sections)
    evidence["enrichment"] = {"max": max_enrichment, "by_section": enrichment_detail}

    if max_enrichment > 10:
        score += 2
        print(f"✓✓ Section enrichment: {max_enrichment:.1f}x (>10x) [+2 points]")
    elif max_enrichment > 5:
        score += 1
        print(f"✓ Section enrichment: {max_enrichment:.1f}x (>5x) [+1 point]")
    else:
        print(f"✗ Section enrichment: {max_enrichment:.1f}x (<5x) [+0 points]")

    # 3. Case-marking test (max 2 points)
    case_rate, verbal_rate, total_instances, instances = analyze_morphology(
        root, all_words
    )
    evidence["morphology"] = {
        "case_rate": case_rate,
        "verbal_rate": verbal_rate,
        "total_instances": total_instances,
        "sample_instances": instances[:20],
    }

    if 30 <= case_rate <= 60:
        score += 2
        print(f"✓✓ Case-marking: {case_rate:.1f}% (30-60% sweet spot) [+2 points]")
    elif (15 <= case_rate < 30) or (60 < case_rate <= 80):
        score += 1
        print(f"✓ Case-marking: {case_rate:.1f}% (moderate) [+1 point]")
    else:
        print(f"✗ Case-marking: {case_rate:.1f}% (outside nominal range) [+0 points]")

    # 4. Verbal rate test (max 2 points)
    if verbal_rate < 15:
        score += 2
        print(f"✓✓ Verbal rate: {verbal_rate:.1f}% (<15%, strong nominal) [+2 points]")
    elif verbal_rate < 25:
        score += 1
        print(f"✓ Verbal rate: {verbal_rate:.1f}% (<25%, nominal-leaning) [+1 point]")
    else:
        print(f"✗ Verbal rate: {verbal_rate:.1f}% (>25%, verb-like) [+0 points]")

    # Final assessment
    print(f"\n{'=' * 60}")
    print(f"TOTAL SCORE: {score}/8")

    if score >= 6:
        assessment = "VALIDATED NOUN ✓✓✓"
        print(f"ASSESSMENT: {assessment}")
        print(f"→ Add '{root}' to validated vocabulary")
    elif score >= 3:
        assessment = "AMBIGUOUS"
        print(f"ASSESSMENT: {assessment}")
        print(f"→ Needs more investigation")
    else:
        assessment = "FUNCTION WORD (NOT SEMANTIC NOUN)"
        print(f"ASSESSMENT: {assessment}")
        print(f"→ Confirms function word bottleneck hypothesis")

    print(f"{'=' * 60}\n")

    evidence["score"] = score
    evidence["assessment"] = assessment

    return score, evidence


def main():
    print("Phase 5A: Tier 1 Blocking Word Validation")
    print("=" * 60)

    # Load data
    filepath = "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/voynich_eva_takahashi.txt"
    all_words, sections = load_voynich_text(filepath)

    print(f"Loaded {len(all_words)} words from manuscript")
    print(f"Sections: {list(sections.keys())}\n")

    # Validated roots for co-occurrence testing
    validated_roots = ["ok", "qok", "ot", "qot", "shee", "she", "dor", "cho", "cheo"]

    # Tier 1 blocking words
    tier1_targets = {
        "qol": "High frequency, appears in sentences 2 & 4",
        "ory": "Sentence 2 blocker, previously 15.8x enriched",
        "sal": "Sentence 2 blocker",
        "dain": "Sentence 4 blocker, possible pronoun (dai!n without punctuation)",
    }

    results = {}

    for root, description in tier1_targets.items():
        print(f"\nTARGET: {root}")
        print(f"CONTEXT: {description}")

        score, evidence = score_evidence(root, all_words, sections, validated_roots)
        results[root] = {
            "description": description,
            "score": score,
            "evidence": evidence,
        }

    # Summary
    print("\n" + "=" * 60)
    print("TIER 1 VALIDATION SUMMARY")
    print("=" * 60)

    validated_nouns = []
    ambiguous = []
    function_words = []

    for root, data in results.items():
        score = data["score"]
        assessment = data["evidence"]["assessment"]

        print(f"\n{root:10} {score}/8  {assessment}")

        if score >= 6:
            validated_nouns.append(root)
        elif score >= 3:
            ambiguous.append(root)
        else:
            function_words.append(root)

    print(f"\n{'=' * 60}")
    print(
        f"VALIDATED NOUNS: {len(validated_nouns)} → {', '.join(validated_nouns) if validated_nouns else 'NONE'}"
    )
    print(
        f"AMBIGUOUS: {len(ambiguous)} → {', '.join(ambiguous) if ambiguous else 'NONE'}"
    )
    print(
        f"FUNCTION WORDS: {len(function_words)} → {', '.join(function_words) if function_words else 'NONE'}"
    )
    print(f"{'=' * 60}")

    # Key finding
    if len(function_words) >= 3:
        print("\n⚠️  CRITICAL FINDING:")
        print("Majority of blocking words are FUNCTION WORDS (not nouns)")
        print("→ This CONFIRMS the function word bottleneck hypothesis")
        print("→ Cannot solve translation problem by adding more nouns")
    elif len(validated_nouns) >= 3:
        print("\n✓ ENCOURAGING FINDING:")
        print("Majority of blocking words are NOUNS")
        print("→ Adding these to vocabulary should improve translation")
        print("→ Proceed with re-translation test")

    # Save results
    output_path = "C:/Users/adria/Documents/manuscript/tier1_validation_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
