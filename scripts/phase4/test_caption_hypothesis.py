"""
TEST: CAPTION HYPOTHESIS

If the Voynich MS is an illustrated reference work with captions (not continuous text),
then vocabulary should be SECTION-SPECIFIC:

- Herbal section: plant names, botanical terms
- Astronomical section: celestial terms
- Biological section: body parts, bath terms (oak/oat)
- Pharmaceutical section: vessel/preparation terms

PREDICTION: 30-50% of vocabulary in each section should be unique to that section

If vocabulary is the SAME across sections → continuous text, not captions
If vocabulary is DIFFERENT by section → caption/label structure

Author: Research Assistant
Date: 2025-10-29
"""

import json
from collections import Counter, defaultdict
from pathlib import Path


def load_voynich_by_sections():
    """Load Voynich text organized by manuscript sections

    Standard Voynich sections:
    - Herbal: f1r-f66v (plant illustrations, one per page)
    - Astronomical: f67r1-f73v (circular diagrams, stars)
    - Biological: f75r-f84v (bathing scenes, human figures)
    - Pharmaceutical: f88r-f100v (jars, vessels)
    - Text-only: f103r-f116v (dense text, no major illustrations)
    """

    # Read the EVA transcription file
    with open(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt",
        "r",
        encoding="utf-8",
    ) as f:
        content = f.read()

    # Extract all words
    words_raw = content.split()

    # Simple approach: split into sections based on document structure
    # We'll use folio ranges as proxy (since we don't have folio markers in this file)

    # Instead, let's use the known bath folio data and extrapolate
    # For now, analyze what we can determine from the full text

    # Get word frequencies for full manuscript
    all_words = [w.lower() for w in words_raw if w.isalpha()]

    return {
        "all_words": all_words,
        "total_words": len(all_words),
        "unique_words": len(set(all_words)),
    }


def analyze_f84v_section_vocabulary():
    """Analyze f84v (bath section) vocabulary in detail

    We have detailed f84v data - use this as test case
    """
    print("=" * 80)
    print("SECTION-SPECIFIC VOCABULARY TEST")
    print("=" * 80)
    print()
    print("Testing if vocabulary is section-specific (caption-like)")
    print("vs. uniform across sections (continuous prose)")
    print()

    # Load f84v text (bath section)
    with open(
        "results/phase4/readable_passages/f84v_oak_oat_bath_folio.txt",
        "r",
        encoding="utf-8",
    ) as f:
        f84v_lines = []
        for line in f:
            line = line.strip()
            if line.startswith("Voynich:"):
                text = line.replace("Voynich:", "").strip()
                words = [w.lower() for w in text.split()]
                f84v_lines.extend(words)

    # Load full manuscript
    with open(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt",
        "r",
        encoding="utf-8",
    ) as f:
        all_words = [w.lower() for w in f.read().split() if w.isalpha()]

    # Get frequencies
    f84v_freq = Counter(f84v_lines)
    all_freq = Counter(all_words)

    # Calculate section-specific enrichment
    f84v_unique = set(f84v_lines)
    all_unique = set(all_words)

    print(f"F84V (BATH SECTION) VOCABULARY:")
    print(f"  Total words in f84v: {len(f84v_lines)}")
    print(f"  Unique words in f84v: {len(f84v_unique)}")
    print(f"  Total words in manuscript: {len(all_words)}")
    print(f"  Unique words in manuscript: {len(all_unique)}")
    print()

    # Calculate enrichment for top f84v words
    print("TOP 30 WORDS IN F84V (with manuscript-wide frequency):")
    print("-" * 80)
    print(
        f"{'Word':<15} {'F84v Count':<12} {'MS Count':<12} {'F84v %':<10} {'MS %':<10} {'Enrichment':<12}"
    )
    print("-" * 80)

    enrichment_scores = []

    for word, f84v_count in f84v_freq.most_common(30):
        ms_count = all_freq[word]

        f84v_pct = 100 * f84v_count / len(f84v_lines)
        ms_pct = 100 * ms_count / len(all_words)

        # Enrichment = how much more common in f84v vs manuscript average
        enrichment = f84v_pct / ms_pct if ms_pct > 0 else 0

        enrichment_scores.append((word, enrichment, f84v_count, ms_count))

        marker = "✓✓" if enrichment > 3 else "✓" if enrichment > 2 else ""
        print(
            f"{word:<15} {f84v_count:<12} {ms_count:<12} {f84v_pct:<10.2f} {ms_pct:<10.2f} {enrichment:<12.2f}x {marker}"
        )

    print()

    # Identify highly enriched words (section-specific)
    highly_enriched = [(w, e) for w, e, _, _ in enrichment_scores if e > 2.0]

    print(f"HIGHLY ENRICHED WORDS (2x+ more common in f84v than MS average):")
    print(f"  Count: {len(highly_enriched)}/{len(enrichment_scores)}")
    print(f"  Percentage: {100 * len(highly_enriched) / len(enrichment_scores):.1f}%")
    print()

    if highly_enriched:
        print("  These words suggest SECTION-SPECIFIC vocabulary:")
        for word, enrichment in highly_enriched[:15]:
            print(f"    {word:<15} {enrichment:.1f}x enriched")
    print()

    # Look for words that appear ONLY in f84v (extremely section-specific)
    f84v_only = []
    for word in f84v_unique:
        if f84v_freq[word] >= 2:  # Must appear at least twice
            ms_elsewhere = all_freq[word] - f84v_freq[word]
            if ms_elsewhere == 0:
                f84v_only.append((word, f84v_freq[word]))

    f84v_only.sort(key=lambda x: x[1], reverse=True)

    print(f"WORDS APPEARING ONLY IN F84V (and nowhere else in MS):")
    print(f"  Count: {len(f84v_only)}")
    print()

    if f84v_only:
        print("  Top words exclusive to bath section:")
        for word, count in f84v_only[:20]:
            print(f"    {word:<15} ({count} times in f84v, 0 elsewhere)")
    print()

    # VERDICT
    print("=" * 80)
    print("VERDICT ON CAPTION HYPOTHESIS:")
    print("=" * 80)
    print()

    enriched_pct = 100 * len(highly_enriched) / len(enrichment_scores)

    print(f"  Highly enriched words: {enriched_pct:.1f}%")
    print(f"  Section-exclusive words: {len(f84v_only)}")
    print()

    if enriched_pct >= 30:
        print("  ✓✓ STRONG SUPPORT for caption hypothesis")
        print("     → Bath section has specialized vocabulary")
        print("     → Text is likely section-specific labels/captions")
    elif enriched_pct >= 20:
        print("  ✓ MODERATE SUPPORT for caption hypothesis")
        print("     → Some vocabulary specialization")
        print("     → Possible mixed structure (captions + prose)")
    else:
        print("  ✗ WEAK SUPPORT for caption hypothesis")
        print("     → Vocabulary is similar across sections")
        print("     → More likely continuous prose")
    print()

    return {
        "f84v_total": len(f84v_lines),
        "f84v_unique": len(f84v_unique),
        "enriched_words": highly_enriched,
        "exclusive_words": f84v_only,
        "enrichment_percentage": enriched_pct,
    }


def analyze_known_terms_distribution():
    """Check if our KNOWN terms (oak, oat, ear, cheek) are section-specific

    If caption hypothesis is correct:
    - oak/oat should concentrate in BATH sections (where they're depicted)
    - NOT evenly distributed across manuscript
    """
    print("=" * 80)
    print("KNOWN TERMS DISTRIBUTION TEST")
    print("=" * 80)
    print()
    print("Testing if validated terms (oak/oat/ear/cheek) concentrate in")
    print("bath sections (where they would be depicted)")
    print()

    # Load f84v (bath section)
    with open(
        "results/phase4/readable_passages/f84v_oak_oat_bath_folio.txt",
        "r",
        encoding="utf-8",
    ) as f:
        f84v_text = f.read().lower()

    # Load full manuscript
    with open(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt",
        "r",
        encoding="utf-8",
    ) as f:
        full_text = f.read().lower()

    # Count known terms
    known_terms = {
        "oak": ["qok", "ok"],  # oak-related roots
        "oat": ["qot", "ot"],  # oat-related roots
        "ear": ["chear", "shear"],  # ear
        "cheek": ["cheek"],  # cheek
    }

    print("KNOWN TERM CONCENTRATIONS:")
    print("-" * 80)
    print(
        f"{'Term':<15} {'F84v':<10} {'Full MS':<10} {'F84v %':<12} {'MS %':<12} {'Enrichment':<12}"
    )
    print("-" * 80)

    f84v_words = f84v_text.split()
    full_words = full_text.split()

    for term_name, patterns in known_terms.items():
        f84v_count = sum(1 for word in f84v_words if any(p in word for p in patterns))
        full_count = sum(1 for word in full_words if any(p in word for p in patterns))

        f84v_pct = 100 * f84v_count / len(f84v_words)
        full_pct = 100 * full_count / len(full_words)

        enrichment = f84v_pct / full_pct if full_pct > 0 else 0

        marker = (
            "✓✓✓"
            if enrichment > 5
            else "✓✓"
            if enrichment > 3
            else "✓"
            if enrichment > 2
            else ""
        )
        print(
            f"{term_name:<15} {f84v_count:<10} {full_count:<10} {f84v_pct:<12.2f} {full_pct:<12.2f} {enrichment:<12.2f}x {marker}"
        )

    print()
    print("INTERPRETATION:")
    print()
    print("If caption hypothesis correct:")
    print("  → Oak/oat should be 3-10x enriched in bath sections (where depicted)")
    print("  → Body parts (ear/cheek) should also concentrate in bath sections")
    print()
    print("If continuous text:")
    print("  → Terms should be evenly distributed (enrichment ~1x)")
    print()

    # Calculate average enrichment
    enrichments = []
    for term_name, patterns in known_terms.items():
        f84v_count = sum(1 for word in f84v_words if any(p in word for p in patterns))
        full_count = sum(1 for word in full_words if any(p in word for p in patterns))

        f84v_pct = 100 * f84v_count / len(f84v_words)
        full_pct = 100 * full_count / len(full_words)

        enrichment = f84v_pct / full_pct if full_pct > 0 else 0
        enrichments.append(enrichment)

    avg_enrichment = sum(enrichments) / len(enrichments) if enrichments else 0

    print(f"Average enrichment: {avg_enrichment:.1f}x")
    print()

    if avg_enrichment > 3:
        print("  ✓✓ STRONG SUPPORT for caption hypothesis")
        print("     → Validated terms concentrate where they'd be depicted")
    elif avg_enrichment > 1.5:
        print("  ✓ MODERATE SUPPORT for caption hypothesis")
        print("     → Some concentration in relevant sections")
    else:
        print("  ✗ WEAK SUPPORT for caption hypothesis")
        print("     → Terms distributed evenly (continuous text pattern)")
    print()

    return {
        "average_enrichment": avg_enrichment,
        "enrichments": dict(zip(known_terms.keys(), enrichments)),
    }


def main():
    print("=" * 80)
    print("CAPTION HYPOTHESIS TEST")
    print("=" * 80)
    print()
    print("HYPOTHESIS: Voynich MS is illustrated reference work with captions")
    print("            (not continuous medical text)")
    print()
    print("PREDICTION: Vocabulary should be section-specific:")
    print("  - Bath sections: oak/oat, body terms")
    print("  - Herbal sections: plant names")
    print("  - Astronomical sections: celestial terms")
    print()
    print("BASELINE: If continuous prose, vocabulary should be uniform")
    print()

    # Test 1: Section-specific vocabulary
    results_vocab = analyze_f84v_section_vocabulary()

    # Test 2: Known terms distribution
    results_terms = analyze_known_terms_distribution()

    # Final synthesis
    print()
    print("=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)
    print()

    vocab_score = results_vocab["enrichment_percentage"]
    term_score = results_terms["average_enrichment"]

    print(f"Evidence for caption hypothesis:")
    print(f"  Section vocabulary specialization: {vocab_score:.1f}%")
    print(f"  Known term concentration: {term_score:.1f}x enrichment")
    print()

    # Combined verdict
    if vocab_score >= 30 and term_score >= 3:
        print("✓✓✓ VERY STRONG SUPPORT for caption hypothesis")
        print()
        print("The Voynich MS appears to be an ILLUSTRATED REFERENCE WORK")
        print("with text serving as IMAGE CAPTIONS/LABELS, not continuous prose.")
        print()
        print("This explains:")
        print("  - Structural template repetition (formulaic captions)")
        print("  - Section-specific vocabulary (different image types)")
        print("  - Oak/oat concentration in bath folios (depicted elements)")
        print("  - Zero exact sentence repetition (different captions per image)")
    elif vocab_score >= 20 or term_score >= 2:
        print("✓ MODERATE SUPPORT for caption hypothesis")
        print()
        print("Evidence suggests mixed structure or partial caption use")
    else:
        print("✗ WEAK SUPPORT for caption hypothesis")
        print()
        print("Text appears more like continuous prose than captions")
    print()

    # Save results
    results = {
        "vocabulary_analysis": {
            "f84v_total": results_vocab["f84v_total"],
            "f84v_unique": results_vocab["f84v_unique"],
            "enrichment_percentage": results_vocab["enrichment_percentage"],
            "top_enriched": results_vocab["enriched_words"][:20],
            "exclusive_words": results_vocab["exclusive_words"][:20],
        },
        "term_distribution": {
            "average_enrichment": results_terms["average_enrichment"],
            "individual_enrichments": results_terms["enrichments"],
        },
        "verdict": {
            "vocab_score": vocab_score,
            "term_score": term_score,
            "caption_hypothesis_supported": vocab_score >= 30 and term_score >= 3,
        },
    }

    output_path = Path("results/phase4/caption_hypothesis_test.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
