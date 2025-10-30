#!/usr/bin/env python3
"""
Phase 11: Identify Lower-Frequency Candidates + Re-evaluate Near-Validated
Focus on 10-20 occurrence range and Phase 10 near-validated elements
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

            folio_match = re.match(r"<f(\d+[rv]?)>", line)
            if folio_match:
                current_folio = folio_match.group(1)
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

            line_words = re.findall(r"\b[a-z]+\b", line.lower())
            for word in line_words:
                if len(word) >= 2:
                    words.append(
                        {
                            "word": word,
                            "section": current_section,
                            "folio": current_folio,
                        }
                    )

    return words


def get_all_validated_elements():
    """Return all 37 validated elements from Phases 8-10"""
    return {
        # Phase 8-9 (28)
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
        "chey",
        "cheey",
        "chy",
        "shy",
        "qol",
        "cthy",
        "shey",
        "am",
        "dam",
        "ory",
        "dair",
        # Phase 10 (9)
        "otchol",
        "kchy",
        "kaiin",
        "kar",
        "kain",
        "kedy",
        "teey",
        "oiin",
        "olchedy",
    }


def get_near_validated():
    """Return Phase 10 near-validated elements (7/10)"""
    return ["keol", "olkedy", "cthor"]


def analyze_low_frequency_candidates(words_list, min_freq=10, max_freq=20):
    """Find candidates in low-frequency range with strong patterns"""
    word_strings = [w["word"] for w in words_list]
    word_freq = Counter(word_strings)

    candidates = []

    for word, count in word_freq.items():
        if min_freq <= count <= max_freq:
            # Count compound occurrences
            substring_count = sum(1 for w in word_strings if word in w and w != word)
            total = count + substring_count

            if total >= 15:  # At least 15 total occurrences for pattern reliability
                productivity = (substring_count / total) * 100

                # Look for high productivity (roots) or low productivity (function words)
                if productivity > 25 or productivity < 8:
                    candidates.append(
                        {
                            "word": word,
                            "type": "root" if productivity > 25 else "function",
                            "exact": count,
                            "compounds": substring_count,
                            "total": total,
                            "productivity": productivity,
                        }
                    )

    return candidates


def analyze_suffix_patterns(words_list):
    """Identify potential productive suffixes"""
    word_strings = [w["word"] for w in words_list]

    # Common 2-3 character endings
    suffix_counts = defaultdict(lambda: {"total": 0, "unique_roots": set()})

    for word in word_strings:
        if len(word) >= 4:  # Need minimum length for root+suffix
            # Test 2-char suffixes
            suffix2 = word[-2:]
            suffix_counts[suffix2]["total"] += 1
            suffix_counts[suffix2]["unique_roots"].add(word[:-2])

            # Test 3-char suffixes
            if len(word) >= 5:
                suffix3 = word[-3:]
                suffix_counts[suffix3]["total"] += 1
                suffix_counts[suffix3]["unique_roots"].add(word[:-3])

    # Find productive suffixes (many unique roots)
    candidates = []
    for suffix, data in suffix_counts.items():
        if data["total"] >= 50 and len(data["unique_roots"]) >= 15:
            productivity = len(data["unique_roots"]) / data["total"]
            candidates.append(
                {
                    "suffix": suffix,
                    "total": data["total"],
                    "unique_roots": len(data["unique_roots"]),
                    "productivity": productivity,
                }
            )

    return candidates


def analyze_prefix_patterns(words_list):
    """Identify potential productive prefixes"""
    word_strings = [w["word"] for w in words_list]

    prefix_counts = defaultdict(lambda: {"total": 0, "unique_stems": set()})

    for word in word_strings:
        if len(word) >= 4:
            # Test 2-char prefixes
            prefix2 = word[:2]
            prefix_counts[prefix2]["total"] += 1
            prefix_counts[prefix2]["unique_stems"].add(word[2:])

            # Test 3-char prefixes
            if len(word) >= 5:
                prefix3 = word[:3]
                prefix_counts[prefix3]["total"] += 1
                prefix_counts[prefix3]["unique_stems"].add(word[3:])

    candidates = []
    for prefix, data in prefix_counts.items():
        if data["total"] >= 50 and len(data["unique_stems"]) >= 15:
            productivity = len(data["unique_stems"]) / data["total"]
            candidates.append(
                {
                    "prefix": prefix,
                    "total": data["total"],
                    "unique_stems": len(data["unique_stems"]),
                    "productivity": productivity,
                }
            )

    return candidates


def analyze_section_enrichment_lowfreq(words_list, min_freq=10, max_freq=20):
    """Find low-frequency words with strong section enrichment"""
    word_freq = Counter([w["word"] for w in words_list])
    section_totals = Counter([w["section"] for w in words_list if w["section"]])
    total_words = sum(section_totals.values())

    word_by_section = defaultdict(lambda: defaultdict(int))
    for entry in words_list:
        if entry["section"]:
            word_by_section[entry["word"]][entry["section"]] += 1

    candidates = []

    for word, count in word_freq.items():
        if min_freq <= count <= max_freq:
            for section in ["herbal", "astronomical", "biological", "pharmaceutical"]:
                observed = word_by_section[word][section]
                expected = (count / total_words) * section_totals[section]

                if expected > 3:  # Minimum expected frequency
                    enrichment = observed / expected

                    if enrichment >= 2.0:  # Strong enrichment
                        candidates.append(
                            {
                                "word": word,
                                "section": section,
                                "enrichment": enrichment,
                                "observed": observed,
                                "expected": expected,
                                "total": count,
                                "section_pct": (observed / count) * 100,
                            }
                        )

    return candidates


def main():
    print("Phase 11: Low-Frequency Candidates + Near-Validated Re-evaluation")
    print("=" * 80)

    # Load data
    eva_file = (
        "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/ZL3b-n.txt"
    )
    words = load_voynich_text(eva_file)
    print(f"\nLoaded {len(words)} words from EVA transcription")

    validated = get_all_validated_elements()
    near_validated = get_near_validated()
    print(f"Currently validated: {len(validated)} elements")
    print(
        f"Near-validated (Phase 10): {len(near_validated)} elements - {', '.join(near_validated)}\n"
    )

    print("=" * 80)
    print("ANALYSIS 1: Low-Frequency Candidates (10-20 occurrences)")
    print("=" * 80)

    lowfreq = analyze_low_frequency_candidates(words, 10, 20)
    lowfreq.sort(key=lambda x: x["productivity"], reverse=True)

    print(f"\nFound {len(lowfreq)} candidates in 10-20 frequency range")
    print("\nTop 20 by productivity:\n")
    print(
        f"{'Word':<12} {'Type':<10} {'Exact':<8} {'Compound':<10} {'Total':<8} {'Prod%':<8}"
    )
    print("-" * 70)

    for i, c in enumerate(lowfreq[:20]):
        if c["word"] not in validated and c["word"] not in near_validated:
            print(
                f"{c['word']:<12} {c['type']:<10} {c['exact']:<8} {c['compounds']:<10} {c['total']:<8} {c['productivity']:<8.1f}"
            )

    print("\n" + "=" * 80)
    print("ANALYSIS 2: Section-Specific Enrichment (Low-Frequency)")
    print("=" * 80)

    section_lowfreq = analyze_section_enrichment_lowfreq(words, 10, 20)
    section_lowfreq.sort(key=lambda x: x["enrichment"], reverse=True)

    print(f"\nFound {len(section_lowfreq)} candidates with strong enrichment")
    print("\nTop 20 by enrichment:\n")
    print(
        f"{'Word':<12} {'Section':<15} {'Enrich':<8} {'Observed':<10} {'Expected':<10} {'Total':<8} {'Sect%':<8}"
    )
    print("-" * 85)

    for i, c in enumerate(section_lowfreq[:20]):
        if c["word"] not in validated and c["word"] not in near_validated:
            print(
                f"{c['word']:<12} {c['section']:<15} {c['enrichment']:<8.2f} {c['observed']:<10} {c['expected']:<10.1f} {c['total']:<8} {c['section_pct']:<8.1f}"
            )

    print("\n" + "=" * 80)
    print("ANALYSIS 3: Productive Suffixes")
    print("=" * 80)

    suffixes = analyze_suffix_patterns(words)
    suffixes.sort(key=lambda x: x["unique_roots"], reverse=True)

    print(f"\nFound {len(suffixes)} potential productive suffixes")
    print("\nTop 20 by unique root count:\n")
    print(
        f"{'Suffix':<10} {'Total Uses':<12} {'Unique Roots':<15} {'Productivity':<12}"
    )
    print("-" * 55)

    for s in suffixes[:20]:
        print(
            f"{s['suffix']:<10} {s['total']:<12} {s['unique_roots']:<15} {s['productivity']:<12.3f}"
        )

    print("\n" + "=" * 80)
    print("ANALYSIS 4: Productive Prefixes")
    print("=" * 80)

    prefixes = analyze_prefix_patterns(words)
    prefixes.sort(key=lambda x: x["unique_stems"], reverse=True)

    print(f"\nFound {len(prefixes)} potential productive prefixes")
    print("\nTop 20 by unique stem count:\n")
    print(
        f"{'Prefix':<10} {'Total Uses':<12} {'Unique Stems':<15} {'Productivity':<12}"
    )
    print("-" * 55)

    for p in prefixes[:20]:
        print(
            f"{p['prefix']:<10} {p['total']:<12} {p['unique_stems']:<15} {p['productivity']:<12.3f}"
        )

    print("\n" + "=" * 80)
    print("PHASE 11 CANDIDATE SELECTION")
    print("=" * 80)

    # Combine analyses
    all_lowfreq_candidates = set()
    for c in lowfreq[:30]:
        if c["word"] not in validated and c["word"] not in near_validated:
            all_lowfreq_candidates.add(c["word"])

    for c in section_lowfreq[:30]:
        if c["word"] not in validated and c["word"] not in near_validated:
            all_lowfreq_candidates.add(c["word"])

    print(f"\nLow-frequency candidates identified: {len(all_lowfreq_candidates)}")

    # Count multi-analysis appearances
    candidate_scores = defaultdict(int)
    for c in lowfreq[:30]:
        if c["word"] not in validated and c["word"] not in near_validated:
            candidate_scores[c["word"]] += 1
    for c in section_lowfreq[:30]:
        if c["word"] not in validated and c["word"] not in near_validated:
            candidate_scores[c["word"]] += 1

    print("\nTop candidates (appearing in multiple analyses):")
    print(f"{'Word':<12} {'Appears in N analyses':<25}")
    print("-" * 40)

    top_candidates = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
    for word, score in top_candidates[:15]:
        print(f"{word:<12} {score:<25}")

    print("\n" + "=" * 80)
    print("RECOMMENDATIONS FOR PHASE 11")
    print("=" * 80)

    print("\nPRIMARY CANDIDATES (new low-frequency):")
    print("  Select 8-10 from multi-analysis low-frequency candidates")

    print("\nSECONDARY CANDIDATES (re-evaluation):")
    print("  Include 3 near-validated from Phase 10:")
    print("  - keol (7/10)")
    print("  - olkedy (7/10)")
    print("  - cthor (7/10)")

    print("\nTERTIARY (suffix/prefix analysis):")
    print("  Identify 2-3 productive affixes for separate affix validation")

    print("\nTarget: 10-12 candidates total")


if __name__ == "__main__":
    main()
