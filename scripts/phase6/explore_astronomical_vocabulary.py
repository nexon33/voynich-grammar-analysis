"""
Explore astronomical section vocabulary (f67r-f73v)

Goal: Identify astronomical-specific terms
Currently: 0 validated domain-specific terms (weakest section!)

Strategy:
1. Extract all words from astronomical section
2. Find words ENRICHED in astronomical (vs other sections)
3. Apply 8/8 evidence scoring to top candidates
"""

import re
from collections import Counter, defaultdict


def load_voynich_by_section(filepath):
    """Load Voynich text separated by section"""

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

        # Parse folio lines
        if line_stripped.startswith("<f"):
            # Extract folio number to determine section
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
                else:
                    current_section = "unknown"

            # Extract text
            match = re.search(r"<f\d+[rv]\d*\.[^>]+>\s+(.+)$", line_stripped)
            if match:
                text = match.group(1)
                # Clean
                text = re.sub(r"<[^>]+>", "", text)
                text = re.sub(r"\{[^}]+\}", "", text)
                text = re.sub(r"\[[^\]]+\]", "", text)
                text = re.sub(r"[@!]\d+;", "", text)
                words = re.findall(r"[a-z]+", text.lower())

                if current_section in sections:
                    sections[current_section].extend(words)

    return sections


def find_astronomical_enriched_terms(sections):
    """Find terms enriched in astronomical section"""

    # Count words per section
    section_counts = {name: Counter(words) for name, words in sections.items()}

    # Calculate enrichment for each word
    astronomical_words = section_counts["astronomical"]
    total_astronomical = sum(astronomical_words.values())

    # Get total occurrences across all sections
    all_words = Counter()
    for words in sections.values():
        all_words.update(words)

    total_all = sum(all_words.values())

    # Calculate enrichment scores
    enrichment_scores = {}

    for word, astro_count in astronomical_words.items():
        if astro_count < 5:  # Minimum 5 occurrences
            continue

        # Calculate expected vs observed
        total_count = all_words[word]
        expected_astro = total_count * (total_astronomical / total_all)
        observed_astro = astro_count

        if expected_astro > 0:
            enrichment = observed_astro / expected_astro
        else:
            enrichment = 0

        # Only include if enriched (>1.5x)
        if enrichment > 1.5:
            enrichment_scores[word] = {
                "astro_count": astro_count,
                "total_count": total_count,
                "astro_pct": 100 * astro_count / total_count,
                "enrichment": enrichment,
            }

    return enrichment_scores


def filter_known_morphemes(enrichment_scores):
    """Remove known grammatical morphemes and roots"""

    known_morphemes = [
        # Known roots
        "ok",
        "qok",
        "ot",
        "qot",
        "shee",
        "she",
        "sho",
        "keo",
        "cho",
        "cheo",
        "dor",
        # Function words
        "qol",
        "sal",
        "dain",
        "daiin",
        "ory",
        # Pure suffixes (will be caught by filtering, but list for clarity)
        "dy",
        "ol",
        "al",
        "or",
        "ar",
        "iin",
        "aiin",
        "ain",
        # Common particles
        "s",
        "y",
        "d",
    ]

    filtered = {}

    for word, stats in enrichment_scores.items():
        # Skip if word IS a known morpheme
        if word in known_morphemes:
            continue

        # Skip if word STARTS with a known root (it's a compound)
        skip = False
        for root in [
            "ok",
            "qok",
            "ot",
            "qot",
            "shee",
            "she",
            "sho",
            "keo",
            "cho",
            "cheo",
            "dor",
        ]:
            if word.startswith(root):
                skip = True
                break

        if not skip:
            filtered[word] = stats

    return filtered


def analyze_top_candidates(filtered_scores, sections, top_n=10):
    """Analyze top N astronomical-enriched candidates"""

    print("\n" + "=" * 70)
    print("TOP ASTRONOMICAL-ENRICHED CANDIDATES")
    print("=" * 70)

    # Sort by enrichment score
    sorted_candidates = sorted(
        filtered_scores.items(), key=lambda x: x[1]["enrichment"], reverse=True
    )

    print(f"\nTop {top_n} candidates (by enrichment):")
    print(f"{'Word':15} {'Astro%':>8} {'Total':>6} {'Enrichment':>12}")
    print("-" * 70)

    top_candidates = []

    for word, stats in sorted_candidates[:top_n]:
        print(
            f"{word:15} {stats['astro_pct']:7.1f}% {stats['total_count']:6} {stats['enrichment']:11.2f}x"
        )
        top_candidates.append(word)

    return top_candidates


def quick_morphological_check(word, sections):
    """Quick check of morphological patterns"""

    # Find all instances
    all_words = []
    for section_words in sections.values():
        all_words.extend(section_words)

    # Count forms with case/verbal markers
    case_markers = ["al", "ol", "ar", "or"]
    verbal_markers = ["dy", "edy"]

    total = all_words.count(word)

    # Count variants with markers
    case_count = 0
    verbal_count = 0

    for w in all_words:
        if word in w:
            if any(w.endswith(m) for m in case_markers):
                case_count += 1
            if any(w.endswith(m) for m in verbal_markers):
                verbal_count += 1

    case_pct = 100 * case_count / total if total > 0 else 0
    verbal_pct = 100 * verbal_count / total if total > 0 else 0

    return case_pct, verbal_pct


if __name__ == "__main__":
    filepath = (
        "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/ZL3b-n.txt"
    )

    print("Loading Voynich manuscript by section...")
    sections = load_voynich_by_section(filepath)

    # Show section sizes
    print("\nSection sizes:")
    for name, words in sections.items():
        print(f"  {name:20} {len(words):6} words")

    print("\nFinding astronomical-enriched terms...")
    enrichment_scores = find_astronomical_enriched_terms(sections)

    print(
        f"\nFound {len(enrichment_scores)} astronomical-enriched terms (>1.5x, >5 instances)"
    )

    print("\nFiltering out known morphemes...")
    filtered = filter_known_morphemes(enrichment_scores)

    print(f"After filtering: {len(filtered)} unknown astronomical candidates")

    # Analyze top candidates
    top_candidates = analyze_top_candidates(filtered, sections, top_n=15)

    # Quick morphological check on top 5
    print("\n" + "=" * 70)
    print("QUICK MORPHOLOGICAL CHECK (top 5)")
    print("=" * 70)

    for word in top_candidates[:5]:
        case_pct, verbal_pct = quick_morphological_check(word, sections)

        print(f"\n{word.upper()}:")
        print(f"  Case-marking: {case_pct:.1f}%")
        print(f"  Verbal rate: {verbal_pct:.1f}%")

        # Assessment
        if 30 <= case_pct <= 60 and verbal_pct < 15:
            print(f"  → LIKELY NOUN (investigate further!)")
        elif case_pct < 25 or verbal_pct > 25:
            print(f"  → Possibly function word or verb")
        else:
            print(f"  → Unclear pattern")

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("1. Investigate top candidate with full 8/8 scoring")
    print("2. Focus on candidates with nominal morphology (30-60% case, <15% verbal)")
    print("3. Look for astronomical context (celestial, time, position terms)")
