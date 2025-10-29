"""
Phase 5A Follow-up: Context Analysis of Ambiguous Words

All 4 Tier 1 words scored AMBIGUOUS (4-5/8).
This script investigates their actual USAGE PATTERNS to determine their function.

Key questions:
1. What positions do they occupy? (sentence-initial, sentence-final, mid-sentence?)
2. What words appear IMMEDIATELY before/after them?
3. Do they appear in fixed collocations?
4. Are they independent words or typically bound forms?
"""

import re
from collections import defaultdict, Counter


def load_voynich_text(filepath):
    """Load Voynich text preserving line structure"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    all_words = []
    line_breaks = []  # Track where lines begin

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("<"):
            continue

        words = re.findall(r"[a-z!]+", line.lower())
        line_breaks.append(len(all_words))
        all_words.extend(words)

    return all_words, line_breaks


def analyze_positional_distribution(root, all_words, line_breaks):
    """Analyze where word appears: line-initial, line-final, mid-line"""
    positions = {"line_initial": 0, "line_final": 0, "mid_line": 0}

    # Create set of line boundaries
    line_starts = set(line_breaks)
    line_ends = set([pos - 1 for pos in line_breaks[1:]] + [len(all_words) - 1])

    for i, word in enumerate(all_words):
        if root in word:
            if i in line_starts:
                positions["line_initial"] += 1
            elif i in line_ends:
                positions["line_final"] += 1
            else:
                positions["mid_line"] += 1

    total = sum(positions.values())
    if total > 0:
        for key in positions:
            positions[key] = (positions[key], f"{positions[key] / total * 100:.1f}%")

    return positions


def analyze_immediate_context(root, all_words, window=1):
    """Analyze words that appear IMMEDIATELY before/after"""
    before = Counter()
    after = Counter()

    for i, word in enumerate(all_words):
        if root in word:
            if i > 0:
                before[all_words[i - 1]] += 1
            if i < len(all_words) - 1:
                after[all_words[i + 1]] += 1

    return before.most_common(10), after.most_common(10)


def analyze_bound_vs_free(root, all_words):
    """Check if root appears standalone or always in compound forms"""
    standalone = 0
    bound = 0
    compounds = []

    for word in all_words:
        if word == root:
            standalone += 1
        elif root in word:
            bound += 1
            if len(compounds) < 20:
                compounds.append(word)

    total = standalone + bound
    standalone_rate = (standalone / total * 100) if total > 0 else 0

    return standalone, bound, standalone_rate, compounds


def find_fixed_collocations(root, all_words, window=2):
    """Find common multi-word patterns containing root"""
    ngrams = Counter()

    for i, word in enumerate(all_words):
        if root in word:
            # Extract 3-gram centered on this word
            if i > 0 and i < len(all_words) - 1:
                trigram = f"{all_words[i - 1]} {word} {all_words[i + 1]}"
                ngrams[trigram] += 1

    return ngrams.most_common(10)


def main():
    print("Phase 5A: Context Analysis of Ambiguous Words")
    print("=" * 70)

    filepath = "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/voynich_eva_takahashi.txt"
    all_words, line_breaks = load_voynich_text(filepath)

    print(f"Loaded {len(all_words)} words, {len(line_breaks)} lines\n")

    targets = ["qol", "ory", "sal", "dain"]

    for root in targets:
        print(f"\n{'=' * 70}")
        print(f"ANALYZING: {root}")
        print(f"{'=' * 70}")

        # 1. Bound vs Free
        standalone, bound, standalone_rate, compounds = analyze_bound_vs_free(
            root, all_words
        )
        print(f"\n1. BOUND vs FREE:")
        print(f"   Standalone: {standalone} ({standalone_rate:.1f}%)")
        print(f"   In compounds: {bound} ({100 - standalone_rate:.1f}%)")
        print(f"   Sample compounds: {', '.join(compounds[:10])}")

        # 2. Positional distribution
        positions = analyze_positional_distribution(root, all_words, line_breaks)
        print(f"\n2. POSITIONAL DISTRIBUTION:")
        for pos_type, (count, pct) in positions.items():
            print(f"   {pos_type:15}: {count:4} ({pct})")

        # 3. Immediate context
        before, after = analyze_immediate_context(root, all_words)
        print(f"\n3. IMMEDIATE CONTEXT:")
        print(f"   Words BEFORE (top 10):")
        for word, count in before:
            print(f"      {word:15} ({count})")
        print(f"   Words AFTER (top 10):")
        for word, count in after:
            print(f"      {word:15} ({count})")

        # 4. Fixed collocations
        collocations = find_fixed_collocations(root, all_words)
        if collocations:
            print(f"\n4. FIXED COLLOCATIONS (3-grams):")
            for ngram, count in collocations:
                if count >= 3:
                    print(f"      {ngram} ({count}x)")

    # Cross-comparison: Do these words co-occur with EACH OTHER?
    print(f"\n\n{'=' * 70}")
    print("CROSS-WORD CO-OCCURRENCE")
    print(f"{'=' * 70}")
    print("Do the ambiguous words appear together?")

    cooccur_matrix = defaultdict(lambda: defaultdict(int))

    for i, word in enumerate(all_words):
        # Check which roots this word contains
        word_roots = [r for r in targets if r in word]
        if not word_roots:
            continue

        # Check neighboring words
        window = 3
        start = max(0, i - window)
        end = min(len(all_words), i + window + 1)

        for j in range(start, end):
            if j == i:
                continue
            neighbor = all_words[j]
            neighbor_roots = [r for r in targets if r in neighbor]

            for wr in word_roots:
                for nr in neighbor_roots:
                    cooccur_matrix[wr][nr] += 1

    print("\nCo-occurrence matrix (within 3-word window):")
    print(f"         {'qol':>8} {'ory':>8} {'sal':>8} {'dain':>8}")
    for r1 in targets:
        row = f"{r1:5}"
        for r2 in targets:
            if r1 == r2:
                row += f"{'--':>8}"
            else:
                row += f"{cooccur_matrix[r1][r2]:>8}"
        print(row)


if __name__ == "__main__":
    main()
