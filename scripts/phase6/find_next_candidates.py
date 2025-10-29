"""
Find the next 1-3 best noun candidates to reach 10-12 total

Current: 9 validated nouns (ok, ot, shee/she, dor, cho, cheo, sho, keo, teo)

Strategy:
1. Extract unknown roots (excluding validated)
2. Score with 8/8 system
3. Focus on herbal-enriched (biggest section)
4. Target: 50-200 instance frequency (not too rare, not too common)
"""

import re
from collections import Counter, defaultdict


def load_voynich_by_section(filepath):
    """Load Voynich text by section"""

    sections = {
        "herbal": [],
        "astronomical": [],
        "biological": [],
        "pharmaceutical": [],
    }

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_section = "unknown"

    for line in lines:
        line_stripped = line.strip()

        if line_stripped.startswith("<f"):
            folio_match = re.search(r"<f(\d+)[rv]", line_stripped)
            if folio_match:
                num = int(folio_match.group(1))
                if 1 <= num <= 66:
                    current_section = "herbal"
                elif 67 <= num <= 73:
                    current_section = "astronomical"
                elif 75 <= num <= 84:
                    current_section = "biological"
                elif 85 <= num <= 116:
                    current_section = "pharmaceutical"

            match = re.search(r"<f\d+[rv]\d*\.[^>]+>\s+(.+)$", line_stripped)
            if match:
                text = match.group(1)
                text = re.sub(r"<[^>]+>", "", text)
                text = re.sub(r"\{[^}]+\}", "", text)
                text = re.sub(r"\[[^\]]+\]", "", text)
                text = re.sub(r"[@!]\d+;", "", text)
                words = re.findall(r"[a-z]+", text.lower())

                if current_section in sections:
                    sections[current_section].extend(words)

    return sections


def extract_unknown_roots(sections):
    """Extract unknown roots after removing validated vocabulary"""

    # All validated morphemes
    validated_nouns = [
        "ok",
        "qok",
        "ot",
        "qot",
        "shee",
        "she",
        "sho",
        "keo",
        "teo",
        "cho",
        "cheo",
        "dor",
    ]
    function_words = ["qol", "sal", "dain", "daiin", "ory"]
    suffixes = [
        "edy",
        "dy",
        "aiin",
        "iin",
        "ain",
        "al",
        "ol",
        "ar",
        "or",
        "s",
        "y",
        "d",
    ]

    known_morphemes = set(validated_nouns + function_words + suffixes)

    # Extract all words
    all_words = []
    for words in sections.values():
        all_words.extend(words)

    # Decompose to find roots
    potential_roots = Counter()

    for word in all_words:
        remainder = word

        # Remove validated nouns first
        skip = False
        for root in validated_nouns:
            if remainder.startswith(root):
                skip = True
                break

        if skip:
            continue

        # Remove suffixes
        for suffix in ["edy", "dy", "aiin", "iin", "ain", "al", "ol", "ar", "or"]:
            if remainder.endswith(suffix):
                remainder = remainder[: -len(suffix)]
                break

        # What's left
        if remainder and len(remainder) >= 2 and remainder not in known_morphemes:
            potential_roots[remainder] += 1

    return potential_roots


def score_candidate(root, sections):
    """Apply 8/8 evidence scoring"""

    # Get all instances of this root
    all_words = []
    section_words = {name: [] for name in sections.keys()}

    for section_name, words in sections.items():
        all_words.extend(words)
        section_words[section_name] = words

    # Find instances
    instances = [w for w in all_words if root in w]
    total = len(instances)

    if total < 20:  # Minimum threshold
        return None

    # 1. Co-occurrence with validated nouns
    validated = [
        "ok",
        "qok",
        "ot",
        "qot",
        "shee",
        "she",
        "sho",
        "keo",
        "teo",
        "cho",
        "cheo",
        "dor",
    ]

    # Simple co-occurrence: look at surrounding context
    # (This is simplified - full version would need context extraction)
    cooccur_score = 1  # Assume moderate (we'd need full context analysis)

    # 2. Section enrichment
    section_counts = {}
    for section_name, words in section_words.items():
        section_counts[section_name] = sum(1 for w in words if root in w)

    total_in_sections = sum(section_counts.values())
    if total_in_sections == 0:
        return None

    max_enrichment = 0
    for section, count in section_counts.items():
        pct = 100 * count / total_in_sections
        enrichment = pct / 25.0  # 25% baseline
        if enrichment > max_enrichment:
            max_enrichment = enrichment
            top_section = section

    if max_enrichment > 1.6:
        enrichment_score = 2
    elif max_enrichment > 1.2:
        enrichment_score = 1
    else:
        enrichment_score = 0

    # 3. Case-marking rate
    case_markers = ["al", "ol", "ar", "or"]
    case_count = sum(1 for w in instances if any(w.endswith(m) for m in case_markers))
    case_pct = 100 * case_count / total

    if 30 <= case_pct <= 60:
        case_score = 2
    elif 20 <= case_pct <= 70:
        case_score = 1
    else:
        case_score = 0

    # 4. Verbal rate
    verbal_markers = ["dy", "edy"]
    verbal_count = sum(
        1 for w in instances if any(w.endswith(m) for m in verbal_markers)
    )
    verbal_pct = 100 * verbal_count / total

    if verbal_pct < 10:
        verbal_score = 2
    elif verbal_pct < 15:
        verbal_score = 1
    else:
        verbal_score = 0

    total_score = cooccur_score + enrichment_score + case_score + verbal_score

    return {
        "root": root,
        "total_instances": total,
        "top_section": top_section,
        "enrichment": max_enrichment,
        "case_pct": case_pct,
        "verbal_pct": verbal_pct,
        "score": total_score,
        "section_dist": section_counts,
    }


if __name__ == "__main__":
    filepath = (
        "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/ZL3b-n.txt"
    )

    print("Loading Voynich manuscript by section...")
    sections = load_voynich_by_section(filepath)

    print(f"\\nSection sizes:")
    for name, words in sections.items():
        print(f"  {name:20} {len(words):6} words")

    print("\\nExtracting unknown roots (excluding 9 validated nouns)...")
    potential_roots = extract_unknown_roots(sections)

    print(f"Found {len(potential_roots)} potential unknown roots")

    # Filter by frequency (50-200 instances - sweet spot)
    medium_freq = {
        root: count for root, count in potential_roots.items() if 50 <= count <= 200
    }

    print(
        f"Filtered to {len(medium_freq)} medium-frequency candidates (50-200 instances)"
    )

    # Score top candidates
    print("\\nScoring candidates...")
    scored_candidates = []

    for root in list(medium_freq.keys())[:30]:  # Score top 30 by frequency
        result = score_candidate(root, sections)
        if result and result["score"] >= 4:  # Minimum 4/8 score
            scored_candidates.append(result)

    # Sort by score
    scored_candidates.sort(key=lambda x: x["score"], reverse=True)

    print("\\n" + "=" * 70)
    print("TOP CANDIDATES FOR INVESTIGATION (4+/8 score)")
    print("=" * 70)

    print(
        f"\\n{'Root':10} {'Instances':>10} {'Section':>15} {'Enrich':>8} {'Case%':>7} {'Verb%':>7} {'Score':>6}"
    )
    print("-" * 70)

    for cand in scored_candidates[:15]:
        print(
            f"{cand['root']:10} {cand['total_instances']:10} "
            f"{cand['top_section']:>15} {cand['enrichment']:7.2f}x "
            f"{cand['case_pct']:6.1f}% {cand['verbal_pct']:6.1f}% "
            f"{cand['score']:5}/8"
        )

    print("\\n" + "=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)

    if scored_candidates:
        top_3 = scored_candidates[:3]
        print(f"\\nInvestigate these {len(top_3)} candidates:")
        for i, cand in enumerate(top_3, 1):
            print(
                f"  {i}. {cand['root']:10} ({cand['score']}/8 score, "
                f"{cand['total_instances']} instances, "
                f"{cand['top_section']}-enriched)"
            )
    else:
        print("\\n? No candidates scored 4+/8")
        print("? May need to lower thresholds or investigate lower-frequency terms")
