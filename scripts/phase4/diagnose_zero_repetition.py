"""
DIAGNOSTIC TEST: Why Zero Repeated Sentence Structures?

Testing three hypotheses:
A. Wrong sentence boundaries (should use line breaks, not paragraphs)
B. Over-aggressive decomposition hiding surface-level repetition
C. Looking for exact matches instead of structural templates

Author: Research Assistant
Date: 2025-10-29
"""

import json
from collections import Counter, defaultdict
from pathlib import Path


def load_voynich_text():
    """Load f84v text from transcription"""
    with open(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt",
        "r",
        encoding="utf-8",
    ) as f:
        lines = []
        current_folio = None
        in_f84v = False

        for line in f:
            line = line.strip()
            if not line:
                continue

            # Check for folio marker
            if line.startswith("<") and line.endswith(">"):
                folio = line.strip("<>")
                if folio == "f84v":
                    in_f84v = True
                    current_folio = folio
                elif in_f84v:
                    break
                continue

            # Collect f84v lines
            if in_f84v:
                # Remove line-initial markers like 'P' or 'C'
                if line and line[0] in ["P", "C", "R", "S"]:
                    line = line[1:].strip()

                # Split into words, preserve line structure
                words = line.split()
                if words:
                    lines.append(words)

        return lines


def test_hypothesis_a_line_boundaries(lines):
    """HYPOTHESIS A: Are we using wrong boundaries?

    Real recipe texts have:
    - 5-8 words per line (instruction length)
    - Lines start with repeated patterns
    - Paragraphs = complete recipes
    """
    print("=" * 80)
    print("HYPOTHESIS A: WRONG SENTENCE BOUNDARIES")
    print("=" * 80)
    print()
    print("Testing if line-level segmentation shows repetition")
    print()

    # Show first 20 lines with word counts
    print("First 20 lines from f84v (with word counts):")
    print("-" * 80)
    for i, line_words in enumerate(lines[:20], 1):
        word_count = len(line_words)
        line_text = " ".join(line_words)
        print(f"Line {i:2d} ({word_count:2d} words): {line_text}")
    print()

    # Word count distribution
    word_counts = [len(line) for line in lines]
    avg_words = sum(word_counts) / len(word_counts)
    print(f"Average words per line: {avg_words:.1f}")
    print(f"Min: {min(word_counts)}, Max: {max(word_counts)}")
    print()

    # Check if lines start with repeated patterns
    line_initial_words = [line[0] for line in lines if line]
    initial_word_freq = Counter(line_initial_words)

    print("Top 10 line-initial words:")
    for word, count in initial_word_freq.most_common(10):
        pct = 100 * count / len(lines)
        print(f"  {word:15s} {count:4d} ({pct:5.1f}% of lines)")
    print()

    # Check for repeated line-initial bigrams
    line_initial_bigrams = []
    for line in lines:
        if len(line) >= 2:
            line_initial_bigrams.append(f"{line[0]} {line[1]}")

    bigram_freq = Counter(line_initial_bigrams)
    print("Top 10 line-initial bigrams:")
    for bigram, count in bigram_freq.most_common(10):
        if count > 1:  # Only show repeated patterns
            pct = 100 * count / len(line_initial_bigrams)
            print(f"  {bigram:30s} {count:4d} ({pct:5.1f}% of lines)")
    print()

    # VERDICT
    repeated_bigrams = sum(1 for count in bigram_freq.values() if count > 1)
    total_unique_bigrams = len(bigram_freq)
    repetition_rate = 100 * repeated_bigrams / total_unique_bigrams

    print(f"VERDICT:")
    print(f"  Line-initial bigram repetition: {repetition_rate:.1f}%")
    if repetition_rate > 30:
        print(f"  ✓ Lines show repetition - wrong boundaries likely!")
    else:
        print(f"  ✗ Lines don't show strong repetition")
    print()

    return {
        "avg_words_per_line": avg_words,
        "repetition_rate": repetition_rate,
        "initial_word_freq": dict(initial_word_freq.most_common(10)),
        "initial_bigram_freq": dict(bigram_freq.most_common(10)),
    }


def test_hypothesis_b_surface_forms(lines):
    """HYPOTHESIS B: Does decomposition hide surface repetition?

    Maybe whole words repeat but decomposition fragments them.
    """
    print("=" * 80)
    print("HYPOTHESIS B: OVER-AGGRESSIVE DECOMPOSITION")
    print("=" * 80)
    print()
    print("Testing if surface forms (before decomposition) show repetition")
    print()

    # Flatten to words
    all_words = [word for line in lines for word in line]

    # Get top 50 surface forms
    word_freq = Counter(all_words)
    top_50_words = set([word for word, _ in word_freq.most_common(50)])

    print(f"Top 50 most common surface forms:")
    for i, (word, count) in enumerate(word_freq.most_common(50), 1):
        print(f"  {i:2d}. {word:15s} {count:4d}")
    print()

    # Check if these surface forms appear in similar positions
    # Look for repeated sequences of top-50 words
    sequences = []
    for line in lines:
        # Only keep top-50 words, replace others with _
        filtered = [w if w in top_50_words else "_" for w in line]
        # Create bigrams and trigrams
        for i in range(len(filtered) - 1):
            if filtered[i] != "_" and filtered[i + 1] != "_":
                sequences.append(f"{filtered[i]} {filtered[i + 1]}")
        for i in range(len(filtered) - 2):
            if filtered[i] != "_" and filtered[i + 1] != "_" and filtered[i + 2] != "_":
                sequences.append(f"{filtered[i]} {filtered[i + 1]} {filtered[i + 2]}")

    seq_freq = Counter(sequences)
    repeated_seqs = [(seq, count) for seq, count in seq_freq.items() if count > 1]

    print(f"Repeated sequences of high-frequency surface forms:")
    print(f"  Total unique sequences: {len(seq_freq)}")
    print(f"  Sequences appearing 2+ times: {len(repeated_seqs)}")
    print()

    print("Top 15 repeated surface sequences:")
    for seq, count in sorted(repeated_seqs, key=lambda x: x[1], reverse=True)[:15]:
        print(f"  {seq:40s} {count:4d} times")
    print()

    # VERDICT
    repetition_pct = 100 * len(repeated_seqs) / len(seq_freq)
    print(f"VERDICT:")
    print(f"  Surface sequence repetition: {repetition_pct:.1f}%")
    if repetition_pct > 20:
        print(f"  ✓ Surface forms show repetition - decomposition might be hiding it!")
    else:
        print(f"  ✗ Even surface forms don't repeat much")
    print()

    return {
        "total_sequences": len(seq_freq),
        "repeated_sequences": len(repeated_seqs),
        "repetition_rate": repetition_pct,
        "top_repeated": dict(
            sorted(repeated_seqs, key=lambda x: x[1], reverse=True)[:15]
        ),
    }


def test_hypothesis_c_structural_templates(lines):
    """HYPOTHESIS C: Need structural patterns, not exact matches

    Abstract words to types, look for repeated templates.
    """
    print("=" * 80)
    print("HYPOTHESIS C: STRUCTURAL TEMPLATES (NOT EXACT MATCHES)")
    print("=" * 80)
    print()
    print("Testing if abstracted structural patterns show repetition")
    print()

    # Load validated knowledge
    with open("results/phase4/validated_knowledge.json", "r", encoding="utf-8") as f:
        validated = json.load(f)

    pronouns = set(validated["pronouns"].keys())

    # Define word type classification
    def classify_word(word):
        """Classify word into structural type"""
        # Pronouns
        if word in pronouns:
            return "PRO"

        # Verbs (chedy/shedy family)
        if "chedy" in word or "shedy" in word or word.endswith("edy"):
            return "VRB"

        # Case-marked nouns
        for case in ["al", "ar", "ol", "or"]:
            if word.endswith(case) and len(word) > len(case):
                return f"N-{case.upper()}"

        # Genitive prefix
        if word.startswith("qok") and len(word) > 3:
            return "GEN"

        # Unknown
        return "UNK"

    # Convert lines to structural patterns
    patterns = []
    for line in lines:
        pattern = [classify_word(word) for word in line]
        patterns.append(" ".join(pattern))

    # Count pattern frequency
    pattern_freq = Counter(patterns)
    repeated_patterns = [(p, c) for p, c in pattern_freq.items() if c > 1]

    print(f"STRUCTURAL PATTERN ANALYSIS:")
    print(f"  Total lines: {len(patterns)}")
    print(f"  Unique patterns: {len(pattern_freq)}")
    print(f"  Patterns appearing 2+ times: {len(repeated_patterns)}")
    print()

    print("Top 20 repeated structural patterns:")
    print("-" * 80)
    for pattern, count in sorted(repeated_patterns, key=lambda x: x[1], reverse=True)[
        :20
    ]:
        pct = 100 * count / len(patterns)
        print(f"  [{count:3d}x, {pct:5.1f}%] {pattern}")
    print()

    # Also try partial pattern matching (subsequences)
    print("PARTIAL PATTERN ANALYSIS (subsequences):")
    print()

    # Extract all 2-word and 3-word subsequences
    subpatterns = []
    for pattern in patterns:
        parts = pattern.split()
        # 2-word
        for i in range(len(parts) - 1):
            subpatterns.append(f"{parts[i]} {parts[i + 1]}")
        # 3-word
        for i in range(len(parts) - 2):
            subpatterns.append(f"{parts[i]} {parts[i + 1]} {parts[i + 2]}")

    subpattern_freq = Counter(subpatterns)
    repeated_subpatterns = [(p, c) for p, c in subpattern_freq.items() if c > 2]

    print("Top 20 repeated subsequences (appearing 3+ times):")
    print("-" * 80)
    for subpattern, count in sorted(
        repeated_subpatterns, key=lambda x: x[1], reverse=True
    )[:20]:
        print(f"  [{count:3d}x] {subpattern}")
    print()

    # VERDICT
    full_repetition_pct = 100 * len(repeated_patterns) / len(pattern_freq)
    sub_repetition_pct = 100 * len(repeated_subpatterns) / len(subpattern_freq)

    print(f"VERDICT:")
    print(f"  Full pattern repetition: {full_repetition_pct:.1f}%")
    print(f"  Subsequence repetition: {sub_repetition_pct:.1f}%")

    if full_repetition_pct > 10:
        print(f"  ✓✓ STRUCTURAL PATTERNS REPEAT - this is the answer!")
    elif sub_repetition_pct > 20:
        print(f"  ✓ Subsequences repeat - need partial matching!")
    else:
        print(f"  ✗ Even structural patterns don't repeat")
    print()

    return {
        "total_patterns": len(pattern_freq),
        "unique_patterns": len(pattern_freq),
        "repeated_patterns": len(repeated_patterns),
        "full_repetition_rate": full_repetition_pct,
        "sub_repetition_rate": sub_repetition_pct,
        "top_repeated_patterns": dict(
            sorted(repeated_patterns, key=lambda x: x[1], reverse=True)[:20]
        ),
        "top_repeated_subpatterns": dict(
            sorted(repeated_subpatterns, key=lambda x: x[1], reverse=True)[:20]
        ),
    }


def main():
    print("=" * 80)
    print("DIAGNOSTIC: WHY ZERO REPEATED SENTENCE STRUCTURES?")
    print("=" * 80)
    print()
    print("Testing three hypotheses:")
    print("  A. Wrong sentence boundaries (line vs paragraph)")
    print("  B. Over-aggressive decomposition hiding repetition")
    print("  C. Need structural templates, not exact matches")
    print()

    # Load f84v text with line breaks preserved
    lines = load_voynich_text()
    print(f"Loaded {len(lines)} lines from f84v")
    print()

    # Test each hypothesis
    results_a = test_hypothesis_a_line_boundaries(lines)
    results_b = test_hypothesis_b_surface_forms(lines)
    results_c = test_hypothesis_c_structural_templates(lines)

    # Final diagnosis
    print("=" * 80)
    print("FINAL DIAGNOSIS")
    print("=" * 80)
    print()

    # Determine which hypothesis has strongest support
    scores = {
        "A (line boundaries)": results_a["repetition_rate"],
        "B (surface forms)": results_b["repetition_rate"],
        "C (structural patterns)": max(
            results_c["full_repetition_rate"], results_c["sub_repetition_rate"]
        ),
    }

    best_hypothesis = max(scores.items(), key=lambda x: x[1])

    print("Repetition rates by hypothesis:")
    for hyp, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        marker = "✓✓ WINNER" if hyp == best_hypothesis[0] else ""
        print(f"  {hyp:30s} {score:6.1f}% {marker}")
    print()

    print(f"CONCLUSION: {best_hypothesis[0]} explains the 'zero repetition' finding")
    print()

    # Save results
    results = {
        "hypothesis_a": results_a,
        "hypothesis_b": results_b,
        "hypothesis_c": results_c,
        "conclusion": best_hypothesis[0],
        "scores": scores,
    }

    output_path = Path("results/phase4/zero_repetition_diagnosis.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
