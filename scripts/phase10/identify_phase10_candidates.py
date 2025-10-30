#!/usr/bin/env python3
"""
Phase 10: Identify New Candidate Words
Systematically identify promising candidates for vocabulary expansion
"""

import re
from collections import Counter, defaultdict


def load_voynich_text(filepath):
    """Load EVA transcription with section markup"""
    words = []
    current_section = None
    current_folio = None

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Extract folio number
            folio_match = re.match(r"<f(\d+[rv]?)>", line)
            if folio_match:
                current_folio = folio_match.group(1)
                # Determine section from folio
                folio_num = int(re.match(r"\d+", current_folio).group())
                if folio_num <= 66:
                    current_section = "herbal"
                elif 67 <= folio_num <= 73:
                    current_section = "astronomical"
                elif 75 <= folio_num <= 84:
                    current_section = "biological"
                elif 85 <= folio_num <= 116:
                    current_section = "pharmaceutical"
                continue

            # Extract words from line
            line_words = re.findall(r"\b[a-z]+\b", line.lower())
            for word in line_words:
                if len(word) >= 2:  # Skip single characters
                    words.append(
                        {
                            "word": word,
                            "section": current_section,
                            "folio": current_folio,
                        }
                    )

    return words


def get_validated_elements():
    """Return our 28 validated elements from Phases 8-9"""
    return {
        # Roots (14)
        "okal",
        "or",
        "dar",
        "dol",
        "chol",
        "keo",
        "teo",
        "she",
        "sho",
        "cho",
        "dor",
        "air",
        "dain",
        "oteey",
        # Function words (12)
        "chey",
        "cheey",
        "chy",
        "shy",
        "qol",
        "cthy",
        "shey",
        # Particles (2)
        "am",
        "dam",
        "ory",
        # Spatial demonstratives (2)
        "dair",  # air and dain already in roots
    }


def analyze_morphological_productivity(words_list):
    """Find words that appear frequently in modified forms"""
    word_strings = [w["word"] for w in words_list]

    candidates = []
    word_freq = Counter(word_strings)

    # Look for words with 20-100 occurrences (medium frequency)
    for word, count in word_freq.most_common(200):
        if 20 <= count <= 100:
            # Count how often this word appears as substring in longer words
            exact_count = count
            substring_count = sum(1 for w in word_strings if word in w and w != word)
            total = exact_count + substring_count

            if total >= 30:  # At least 30 total instances
                productivity = (substring_count / total) * 100

                # Roots should show >20% productivity
                # Function words should show <10% productivity
                if productivity > 20 or productivity < 10:
                    candidates.append(
                        {
                            "word": word,
                            "type": "root" if productivity > 20 else "function",
                            "exact": exact_count,
                            "compounds": substring_count,
                            "total": total,
                            "productivity": productivity,
                        }
                    )

    return candidates


def analyze_positional_distribution(words_list):
    """Find words with strong positional preferences"""
    # Create sentence-like structures from lines
    sentences = []
    current_sentence = []

    for i, entry in enumerate(words_list):
        current_sentence.append(entry["word"])
        # Simple sentence boundary: every 5-8 words or section change
        if len(current_sentence) >= 8 or (
            i > 0 and entry["section"] != words_list[i - 1]["section"]
        ):
            if len(current_sentence) >= 3:
                sentences.append(current_sentence)
            current_sentence = []

    # Analyze position for each word
    position_stats = defaultdict(
        lambda: {"initial": 0, "medial": 0, "final": 0, "total": 0}
    )

    for sentence in sentences:
        for i, word in enumerate(sentence):
            if i == 0:
                position_stats[word]["initial"] += 1
            elif i == len(sentence) - 1:
                position_stats[word]["final"] += 1
            else:
                position_stats[word]["medial"] += 1
            position_stats[word]["total"] += 1

    candidates = []
    for word, stats in position_stats.items():
        if stats["total"] >= 20:  # At least 20 occurrences
            initial_pct = (stats["initial"] / stats["total"]) * 100
            medial_pct = (stats["medial"] / stats["total"]) * 100
            final_pct = (stats["final"] / stats["total"]) * 100

            # Look for strong preferences (>60% in one position)
            if medial_pct > 60 or final_pct > 60 or initial_pct > 60:
                dominant = max(
                    [
                        ("initial", initial_pct),
                        ("medial", medial_pct),
                        ("final", final_pct),
                    ],
                    key=lambda x: x[1],
                )
                candidates.append(
                    {
                        "word": word,
                        "position": dominant[0],
                        "percentage": dominant[1],
                        "initial": initial_pct,
                        "medial": medial_pct,
                        "final": final_pct,
                        "n": stats["total"],
                    }
                )

    return candidates


def analyze_section_distribution(words_list):
    """Find words with section-specific enrichment"""
    section_totals = Counter([w["section"] for w in words_list if w["section"]])
    word_by_section = defaultdict(lambda: defaultdict(int))
    word_totals = Counter([w["word"] for w in words_list])

    for entry in words_list:
        if entry["section"]:
            word_by_section[entry["word"]][entry["section"]] += 1

    candidates = []
    total_words = sum(section_totals.values())

    for word, count in word_totals.most_common(300):
        if 20 <= count <= 150:  # Medium frequency
            # Calculate enrichment for each section
            for section in ["herbal", "astronomical", "biological", "pharmaceutical"]:
                observed = word_by_section[word][section]
                expected = (count / total_words) * section_totals[section]

                if expected > 5:  # Enough expected frequency
                    enrichment = observed / expected

                    if enrichment >= 1.5:  # At least 1.5x enrichment
                        candidates.append(
                            {
                                "word": word,
                                "section": section,
                                "enrichment": enrichment,
                                "observed": observed,
                                "expected": expected,
                                "total": count,
                                "section_percentage": (observed / count) * 100,
                            }
                        )

    return candidates


def analyze_cooccurrence(words_list):
    """Find words frequently appearing with validated elements"""
    validated = get_validated_elements()

    # Create 3-word windows
    cooccurrence = defaultdict(int)
    word_counts = Counter([w["word"] for w in words_list])

    for i in range(1, len(words_list) - 1):
        current = words_list[i]["word"]
        prev_word = words_list[i - 1]["word"]
        next_word = words_list[i + 1]["word"]

        # Check if any validated element in window
        if prev_word in validated or next_word in validated:
            cooccurrence[current] += 1

    candidates = []
    for word, cooccur_count in cooccurrence.items():
        total = word_counts[word]
        if 20 <= total <= 150:  # Medium frequency
            cooccur_rate = (cooccur_count / total) * 100
            if cooccur_rate >= 15:  # At least 15% co-occurrence
                candidates.append(
                    {
                        "word": word,
                        "cooccurrence_rate": cooccur_rate,
                        "cooccur_count": cooccur_count,
                        "total": total,
                    }
                )

    return candidates


def main():
    print("Phase 10: Identifying New Candidate Words")
    print("=" * 60)

    # Load data
    eva_file = (
        "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/ZL3b-n.txt"
    )
    words = load_voynich_text(eva_file)
    print(f"\nLoaded {len(words)} words from EVA transcription")

    validated = get_validated_elements()
    print(f"Validated vocabulary: {len(validated)} elements")

    print("\n" + "=" * 60)
    print("ANALYSIS 1: Morphological Productivity")
    print("=" * 60)

    prod_candidates = analyze_morphological_productivity(words)
    prod_candidates.sort(key=lambda x: x["productivity"], reverse=True)

    print(
        f"\nFound {len(prod_candidates)} candidates with interesting productivity patterns"
    )
    print("\nTop 20 by productivity:\n")
    print(
        f"{'Word':<12} {'Type':<10} {'Exact':<8} {'Compound':<10} {'Total':<8} {'Prod%':<8}"
    )
    print("-" * 70)

    for i, c in enumerate(prod_candidates[:20]):
        if c["word"] not in validated:
            print(
                f"{c['word']:<12} {c['type']:<10} {c['exact']:<8} {c['compounds']:<10} {c['total']:<8} {c['productivity']:<8.1f}"
            )

    print("\n" + "=" * 60)
    print("ANALYSIS 2: Positional Distribution")
    print("=" * 60)

    pos_candidates = analyze_positional_distribution(words)
    pos_candidates.sort(key=lambda x: x["percentage"], reverse=True)

    print(
        f"\nFound {len(pos_candidates)} candidates with strong positional preferences"
    )
    print("\nTop 20 by position strength:\n")
    print(
        f"{'Word':<12} {'Position':<10} {'%':<8} {'Initial':<8} {'Medial':<8} {'Final':<8} {'n':<6}"
    )
    print("-" * 75)

    for i, c in enumerate(pos_candidates[:20]):
        if c["word"] not in validated:
            print(
                f"{c['word']:<12} {c['position']:<10} {c['percentage']:<8.1f} {c['initial']:<8.1f} {c['medial']:<8.1f} {c['final']:<8.1f} {c['n']:<6}"
            )

    print("\n" + "=" * 60)
    print("ANALYSIS 3: Section-Specific Enrichment")
    print("=" * 60)

    section_candidates = analyze_section_distribution(words)
    section_candidates.sort(key=lambda x: x["enrichment"], reverse=True)

    print(f"\nFound {len(section_candidates)} candidates with section enrichment")
    print("\nTop 20 by enrichment:\n")
    print(
        f"{'Word':<12} {'Section':<15} {'Enrich':<8} {'Observed':<10} {'Expected':<10} {'Total':<8} {'Sect%':<8}"
    )
    print("-" * 85)

    for i, c in enumerate(section_candidates[:20]):
        if c["word"] not in validated:
            print(
                f"{c['word']:<12} {c['section']:<15} {c['enrichment']:<8.2f} {c['observed']:<10} {c['expected']:<10.1f} {c['total']:<8} {c['section_percentage']:<8.1f}"
            )

    print("\n" + "=" * 60)
    print("ANALYSIS 4: Co-occurrence with Validated Elements")
    print("=" * 60)

    cooccur_candidates = analyze_cooccurrence(words)
    cooccur_candidates.sort(key=lambda x: x["cooccurrence_rate"], reverse=True)

    print(f"\nFound {len(cooccur_candidates)} candidates with high co-occurrence")
    print("\nTop 20 by co-occurrence rate:\n")
    print(f"{'Word':<12} {'CoOccur%':<12} {'CoOccur_n':<12} {'Total':<8}")
    print("-" * 50)

    for i, c in enumerate(cooccur_candidates[:20]):
        if c["word"] not in validated:
            print(
                f"{c['word']:<12} {c['cooccurrence_rate']:<12.1f} {c['cooccur_count']:<12} {c['total']:<8}"
            )

    print("\n" + "=" * 60)
    print("CANDIDATE SUMMARY")
    print("=" * 60)

    # Find words appearing in multiple analyses
    all_candidates = set()
    for c in prod_candidates:
        if c["word"] not in validated:
            all_candidates.add(c["word"])
    for c in pos_candidates:
        if c["word"] not in validated:
            all_candidates.add(c["word"])
    for c in section_candidates:
        if c["word"] not in validated:
            all_candidates.add(c["word"])
    for c in cooccur_candidates:
        if c["word"] not in validated:
            all_candidates.add(c["word"])

    print(f"\nTotal unique candidates identified: {len(all_candidates)}")

    # Find candidates in multiple categories
    candidate_scores = defaultdict(int)
    for c in prod_candidates[:30]:
        if c["word"] not in validated:
            candidate_scores[c["word"]] += 1
    for c in pos_candidates[:30]:
        if c["word"] not in validated:
            candidate_scores[c["word"]] += 1
    for c in section_candidates[:30]:
        if c["word"] not in validated:
            candidate_scores[c["word"]] += 1
    for c in cooccur_candidates[:30]:
        if c["word"] not in validated:
            candidate_scores[c["word"]] += 1

    print("\nTop candidates (appearing in multiple analyses):")
    print(f"{'Word':<12} {'Appears in N analyses':<25}")
    print("-" * 40)

    top_candidates = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
    for word, score in top_candidates[:25]:
        print(f"{word:<12} {score:<25}")

    print("\n" + "=" * 60)
    print("RECOMMENDATIONS FOR PHASE 10")
    print("=" * 60)
    print("\nSelect 10-15 candidates from the top multi-analysis candidates")
    print("Prioritize words appearing in 2+ analyses")
    print(
        "Mix of potential roots (high productivity) and function words (strong position)"
    )


if __name__ == "__main__":
    main()
