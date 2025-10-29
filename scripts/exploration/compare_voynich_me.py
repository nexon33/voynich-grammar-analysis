"""
Compare Voynich and Middle English character frequency distributions
with statistical significance testing.
"""

from collections import Counter
from pathlib import Path
import re
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt


def read_voynich_text():
    """Read Voynich EVA transcription."""
    voynich_file = Path("data/voynich/eva_transcription/voynich_eva_takahashi.txt")
    with open(voynich_file, "r", encoding="utf-8") as f:
        text = f.read()

    # Extract only alphabetic characters
    chars = [c for c in text.lower() if c.isalpha()]
    return Counter(chars)


def read_me_corpus():
    """Read Middle English corpus from CMEPV."""
    corpus_dir = Path("data/middle_english_corpus/cmepv/middle_english_text_cmepv/sgml")
    sgml_files = list(corpus_dir.glob("*.sgm"))

    all_text = []
    for sgml_file in sgml_files:
        with open(sgml_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            # Remove SGML tags
            text = re.sub(r"<[^>]+>", " ", content)
            all_text.append(text)

    combined_text = " ".join(all_text)
    chars = [c for c in combined_text.lower() if c.isalpha()]
    return Counter(chars)


def normalize_frequencies(counter):
    """Convert counts to percentages."""
    total = sum(counter.values())
    return {char: (count / total) * 100 for char, count in counter.items()}


def calculate_chi_square(voynich_freq, me_freq):
    """
    Calculate chi-square test for independence.
    Tests if Voynich and ME distributions are from same underlying distribution.
    """
    # Get all unique characters from both
    all_chars = sorted(set(voynich_freq.keys()) | set(me_freq.keys()))

    voynich_percentages = [voynich_freq.get(char, 0) for char in all_chars]
    me_percentages = [me_freq.get(char, 0) for char in all_chars]

    # Chi-square test
    chi2, p_value = stats.chisquare(voynich_percentages, me_percentages)

    return chi2, p_value, all_chars, voynich_percentages, me_percentages


def calculate_correlation(voynich_freq, me_freq):
    """Calculate Pearson and Spearman correlation coefficients."""
    # Get common characters
    common_chars = sorted(set(voynich_freq.keys()) & set(me_freq.keys()))

    voynich_vals = [voynich_freq[char] for char in common_chars]
    me_vals = [me_freq[char] for char in common_chars]

    # Pearson correlation (linear relationship)
    pearson_r, pearson_p = stats.pearsonr(voynich_vals, me_vals)

    # Spearman correlation (rank-based, non-parametric)
    spearman_r, spearman_p = stats.spearmanr(voynich_vals, me_vals)

    return (
        pearson_r,
        pearson_p,
        spearman_r,
        spearman_p,
        common_chars,
        voynich_vals,
        me_vals,
    )


def create_comparison_visualization(voynich_freq, me_freq, output_path):
    """Create side-by-side bar chart comparing distributions."""
    # Get top 15 characters from each
    voynich_top = sorted(voynich_freq.items(), key=lambda x: x[1], reverse=True)[:15]
    me_top = sorted(me_freq.items(), key=lambda x: x[1], reverse=True)[:15]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Voynich
    chars1, freqs1 = zip(*voynich_top)
    ax1.bar(chars1, freqs1, color="#2E86AB")
    ax1.set_title("Voynich Character Frequencies", fontsize=14, fontweight="bold")
    ax1.set_xlabel("Character")
    ax1.set_ylabel("Frequency (%)")
    ax1.grid(axis="y", alpha=0.3)

    # Middle English
    chars2, freqs2 = zip(*me_top)
    ax2.bar(chars2, freqs2, color="#A23B72")
    ax2.set_title(
        "Middle English Character Frequencies", fontsize=14, fontweight="bold"
    )
    ax2.set_xlabel("Character")
    ax2.set_ylabel("Frequency (%)")
    ax2.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✓ Visualization saved to: {output_path}")


def create_scatter_plot(voynich_vals, me_vals, common_chars, pearson_r, output_path):
    """Create scatter plot showing correlation."""
    plt.figure(figsize=(10, 8))
    plt.scatter(me_vals, voynich_vals, s=100, alpha=0.6, color="#F18F01")

    # Add labels for notable points
    for i, char in enumerate(common_chars):
        if me_vals[i] > 5 or voynich_vals[i] > 5:  # Label high-frequency chars
            plt.annotate(
                char,
                (me_vals[i], voynich_vals[i]),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=12,
                fontweight="bold",
            )

    # Add trend line
    z = np.polyfit(me_vals, voynich_vals, 1)
    p = np.poly1d(z)
    plt.plot(me_vals, p(me_vals), "r--", alpha=0.8, linewidth=2)

    plt.xlabel("Middle English Frequency (%)", fontsize=12)
    plt.ylabel("Voynich Frequency (%)", fontsize=12)
    plt.title(
        f"Voynich vs Middle English Character Frequencies\nPearson r = {pearson_r:.4f}",
        fontsize=14,
        fontweight="bold",
    )
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✓ Scatter plot saved to: {output_path}")


def main():
    print("\n" + "=" * 70)
    print("STATISTICAL COMPARISON: VOYNICH vs MIDDLE ENGLISH")
    print("=" * 70 + "\n")

    # Read data
    print("Reading data...")
    voynich_counts = read_voynich_text()
    me_counts = read_me_corpus()

    # Normalize to percentages
    voynich_freq = normalize_frequencies(voynich_counts)
    me_freq = normalize_frequencies(me_counts)

    print(f"✓ Voynich: {sum(voynich_counts.values()):,} characters")
    print(f"✓ Middle English: {sum(me_counts.values()):,} characters\n")

    # Create output directory
    output_dir = Path("results/phase1")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Statistical tests
    print("=" * 70)
    print("STATISTICAL TESTS")
    print("=" * 70 + "\n")

    # 1. Chi-square test
    print("1. CHI-SQUARE TEST")
    print("-" * 70)
    chi2, chi_p, all_chars, voyn_pct, me_pct = calculate_chi_square(
        voynich_freq, me_freq
    )
    print(f"   Chi-square statistic: {chi2:.4f}")
    print(f"   P-value: {chi_p:.6f}")

    if chi_p < 0.001:
        print(f"   ✗ Distributions are SIGNIFICANTLY DIFFERENT (p < 0.001)")
        print(f"      This is expected - we're not claiming identical distributions,")
        print(f"      but rather that Voynich may be a CIPHER of ME.")
    else:
        print(f"   ✓ Distributions are similar (p >= 0.001)")
    print()

    # 2. Correlation tests
    print("2. CORRELATION TESTS")
    print("-" * 70)
    pearson_r, pearson_p, spearman_r, spearman_p, common_chars, voyn_vals, me_vals = (
        calculate_correlation(voynich_freq, me_freq)
    )

    print(f"   Pearson correlation:")
    print(f"      r = {pearson_r:.4f}")
    print(f"      p-value = {pearson_p:.6f}")
    if pearson_p < 0.05:
        print(f"      ✓ SIGNIFICANT linear correlation (p < 0.05)")
    else:
        print(f"      ✗ No significant linear correlation")
    print()

    print(f"   Spearman correlation:")
    print(f"      ρ = {spearman_r:.4f}")
    print(f"      p-value = {spearman_p:.6f}")
    if spearman_p < 0.05:
        print(f"      ✓ SIGNIFICANT rank correlation (p < 0.05)")
    else:
        print(f"      ✗ No significant rank correlation")
    print()

    # 3. Specific hypothesis: o = e
    print("3. TESTING 'o' = 'e' HYPOTHESIS")
    print("-" * 70)
    voyn_o = voynich_freq.get("o", 0)
    me_e = me_freq.get("e", 0)
    diff = abs(voyn_o - me_e)

    print(f"   Voynich 'o': {voyn_o:.2f}%")
    print(f"   ME 'e':      {me_e:.2f}%")
    print(f"   Difference:  {diff:.2f}%")

    if diff < 1.0:
        print(f"   ✓✓✓ EXCELLENT MATCH! (< 1% difference)")
    elif diff < 2.0:
        print(f"   ✓✓ VERY GOOD MATCH (< 2% difference)")
    elif diff < 5.0:
        print(f"   ✓ REASONABLE MATCH (< 5% difference)")
    else:
        print(f"   ✗ POOR MATCH (>= 5% difference)")
    print()

    # Create visualizations
    print("=" * 70)
    print("CREATING VISUALIZATIONS")
    print("=" * 70 + "\n")

    comparison_path = output_dir / "voynich_me_comparison.png"
    scatter_path = output_dir / "voynich_me_scatter.png"

    create_comparison_visualization(voynich_freq, me_freq, comparison_path)
    create_scatter_plot(voyn_vals, me_vals, common_chars, pearson_r, scatter_path)

    # Summary
    print("\n" + "=" * 70)
    print("PHASE 1 DECISION POINT")
    print("=" * 70 + "\n")

    print("Based on our statistical analysis:\n")

    evidence_count = 0

    if diff < 2.0:
        print("✓ The 'o' = 'e' hypothesis is strongly supported")
        evidence_count += 1
    else:
        print("✗ The 'o' = 'e' hypothesis is NOT supported")

    if abs(pearson_r) > 0.3 or abs(spearman_r) > 0.3:
        print("✓ There is measurable correlation between distributions")
        evidence_count += 1
    else:
        print("✗ Correlation is too weak")

    # Check if Voynich 'o' is the most frequent (should be if it's 'e')
    voyn_top_char = max(voynich_freq.items(), key=lambda x: x[1])[0]
    if voyn_top_char == "o":
        print("✓ Voynich 'o' is the most frequent character (as expected if it = 'e')")
        evidence_count += 1

    print(f"\nEvidence score: {evidence_count}/3\n")

    if evidence_count >= 2:
        print("=" * 70)
        print("RECOMMENDATION: PROCEED TO PHASE 2")
        print("=" * 70)
        print("\nThere is sufficient statistical evidence to support the hypothesis")
        print("that Voynich text may be obfuscated Middle English.")
        print("\nNext steps:")
        print("1. Begin vocabulary mapping using Margery Kempe's Book")
        print("2. Test additional character substitutions")
        print("3. Look for morphological patterns (suffixes, prefixes)")
    else:
        print("=" * 70)
        print("RECOMMENDATION: HYPOTHESIS NOT SUPPORTED")
        print("=" * 70)
        print("\nInsufficient evidence to proceed. Consider:")
        print("1. Different cipher hypothesis")
        print("2. Different base language")
        print("3. More complex obfuscation method")

    print()


if __name__ == "__main__":
    main()
