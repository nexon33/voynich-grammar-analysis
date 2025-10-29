#!/usr/bin/env python3
"""
Analyze positional distribution of reversed terms.

Tests Hypothesis C: Reversal applied by location in manuscript
- Do reversed terms cluster in specific sections?
- Are they near illustrations?
- Do they appear at specific positions (titles, labels)?
"""

import json
from pathlib import Path
from collections import defaultdict, Counter


def load_results():
    """Load reversal search results."""
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"

    with open(
        results_dir / "reversed_terms_search_results.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)

    with open(
        results_dir / "full_manuscript_translation.json", "r", encoding="utf-8"
    ) as f:
        manuscript = json.load(f)

    return data, manuscript


def position_to_section(position, manuscript):
    """Convert word position to section number."""
    cumulative = 0
    for section in manuscript["sections"]:
        word_count = len(section["original"].split())
        if position < cumulative + word_count:
            return section["section_id"]
        cumulative += word_count
    return None


def main():
    print("=" * 80)
    print("REVERSAL DISTRIBUTION ANALYSIS")
    print("=" * 80)
    print()

    data, manuscript = load_results()

    # Extract reversed terms and their positions
    reversed_terms = {}
    for term, info in data["results"].items():
        if info["reversed_matches"] > 0:
            reversed_terms[term] = {
                "positions": info["sample_positions"],
                "count": info["reversed_matches"],
                "category": info["category"],
            }

    print(f"Found {len(reversed_terms)} terms with reversal:")
    for term, info in reversed_terms.items():
        print(f"  {term:10s} ({info['category']:15s}): {info['count']:3d} instances")
    print()

    # Analyze sectional distribution
    print("=" * 80)
    print("SECTIONAL DISTRIBUTION")
    print("=" * 80)
    print()

    section_counts = defaultdict(lambda: defaultdict(int))

    for term, info in reversed_terms.items():
        for pos in info["positions"]:
            section = position_to_section(pos, manuscript)
            if section is not None:
                section_counts[section][term] += 1
                section_counts[section]["TOTAL"] += 1

    # Find sections with high reversal density
    high_density_sections = sorted(
        [(sec, counts) for sec, counts in section_counts.items()],
        key=lambda x: x[1]["TOTAL"],
        reverse=True,
    )[:20]

    print("Top 20 sections by reversed term density:")
    print()
    for section, counts in high_density_sections:
        total = counts.pop("TOTAL", 0)
        terms = ", ".join([f"{term}({count})" for term, count in counts.items()])
        print(f"  Section {section:3d}: {total:2d} reversed terms - {terms}")
    print()

    # Analyze by category
    print("=" * 80)
    print("CATEGORY DISTRIBUTION")
    print("=" * 80)
    print()

    category_positions = defaultdict(list)
    for term, info in reversed_terms.items():
        category_positions[info["category"]].extend(info["positions"])

    for category, positions in category_positions.items():
        # Calculate density across manuscript
        total_words = data["total_words"]
        density = len(positions) / total_words * 100

        # Find clustering
        sections = [position_to_section(pos, manuscript) for pos in positions]
        section_counter = Counter(sections)
        most_common_section = (
            section_counter.most_common(1)[0] if section_counter else (None, 0)
        )

        print(f"{category:20s}:")
        print(f"  Total instances: {len(positions)}")
        print(f"  Density: {density:.4f}%")
        print(
            f"  Most common section: {most_common_section[0]} ({most_common_section[1]} instances)"
        )
        print(f"  Spread: {len(section_counter)} unique sections")
        print()

    # Test clustering hypothesis
    print("=" * 80)
    print("CLUSTERING ANALYSIS")
    print("=" * 80)
    print()

    # Check if reversal terms cluster together
    all_reversed_positions = []
    for info in reversed_terms.values():
        all_reversed_positions.extend(info["positions"])

    all_reversed_positions.sort()

    # Calculate gaps between consecutive reversed terms
    gaps = []
    for i in range(1, len(all_reversed_positions)):
        gap = all_reversed_positions[i] - all_reversed_positions[i - 1]
        gaps.append(gap)

    if gaps:
        avg_gap = sum(gaps) / len(gaps)
        median_gap = sorted(gaps)[len(gaps) // 2]

        print(f"Total reversed term instances: {len(all_reversed_positions)}")
        print(f"Average gap between instances: {avg_gap:.1f} words")
        print(f"Median gap: {median_gap} words")
        print()

        # Check for tight clusters (gap < 100 words)
        tight_clusters = [g for g in gaps if g < 100]
        print(
            f"Tight clusters (< 100 words apart): {len(tight_clusters)} ({len(tight_clusters) / len(gaps) * 100:.1f}%)"
        )
        print()

    # Positional patterns
    print("=" * 80)
    print("POSITIONAL PATTERNS")
    print("=" * 80)
    print()

    # Check if reversed terms appear at specific relative positions within sections
    section_relative_positions = []

    for term, info in reversed_terms.items():
        for pos in info["positions"]:
            section = position_to_section(pos, manuscript)
            if section is not None:
                # Calculate relative position within section (0.0 = start, 1.0 = end)
                section_data = manuscript["sections"][section]
                section_words = section_data["original"].split()

                # Find cumulative position up to this section
                cumulative = sum(
                    len(s["original"].split()) for s in manuscript["sections"][:section]
                )
                relative_pos = (
                    (pos - cumulative) / len(section_words)
                    if len(section_words) > 0
                    else 0
                )

                section_relative_positions.append(relative_pos)

    if section_relative_positions:
        # Bin into quintiles
        bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
        bin_counts = defaultdict(int)

        for rel_pos in section_relative_positions:
            for i in range(len(bins) - 1):
                if bins[i] <= rel_pos < bins[i + 1]:
                    bin_counts[f"{int(bins[i] * 100)}-{int(bins[i + 1] * 100)}%"] += 1
                    break

        print("Distribution within sections:")
        for bin_range in ["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"]:
            count = bin_counts[bin_range]
            pct = count / len(section_relative_positions) * 100
            bar = "█" * int(pct / 2)
            print(f"  {bin_range:10s}: {count:3d} ({pct:5.1f}%) {bar}")
        print()

    # Summary
    print("=" * 80)
    print("HYPOTHESIS C ASSESSMENT: Positional Patterns")
    print("=" * 80)
    print()

    # Check for even distribution
    if section_relative_positions:
        import statistics

        stdev = statistics.stdev(bin_counts.values()) if len(bin_counts) > 1 else 0
        mean = statistics.mean(bin_counts.values())
        coefficient_of_variation = stdev / mean if mean > 0 else 0

        if coefficient_of_variation < 0.3:
            print("✓ EVEN DISTRIBUTION")
            print("Reversed terms appear uniformly throughout sections.")
            print("No evidence for positional rules (titles, labels, etc.)")
        elif coefficient_of_variation < 0.6:
            print("~ MODERATE CLUSTERING")
            print("Some positional preference, but not strongly clustered.")
        else:
            print("✓ STRONG CLUSTERING")
            print("Reversed terms cluster at specific positions within sections.")
            print("May indicate titles, labels, or structural markers.")

        print(f"  Coefficient of variation: {coefficient_of_variation:.3f}")

    # Save analysis
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase3"
    output = {
        "reversed_terms": {
            term: {
                "count": info["count"],
                "category": info["category"],
                "positions": info["positions"],
            }
            for term, info in reversed_terms.items()
        },
        "section_distribution": {
            int(sec): dict(counts) for sec, counts in section_counts.items()
        },
        "high_density_sections": [
            (int(sec), dict(counts)) for sec, counts in high_density_sections
        ],
        "category_stats": {
            cat: {
                "count": len(positions),
                "density": len(positions) / data["total_words"] * 100,
            }
            for cat, positions in category_positions.items()
        },
        "clustering_stats": {
            "total_instances": len(all_reversed_positions),
            "avg_gap": sum(gaps) / len(gaps) if gaps else 0,
            "median_gap": sorted(gaps)[len(gaps) // 2] if gaps else 0,
            "tight_clusters": len([g for g in gaps if g < 100]) if gaps else 0,
        }
        if gaps
        else {},
    }

    output_path = results_dir / "reversal_distribution_analysis.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print()
    print(f"Results saved to: {output_path}")
    print()


if __name__ == "__main__":
    main()
