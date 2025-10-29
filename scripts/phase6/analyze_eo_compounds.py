"""
Analyze "eo" - is it a suffix/compound element or standalone root?

Looking at forms: keol, keody, teol, teody, cheeo, cheeor...
These suggest: ke + ol, te + ol, chee + or

Maybe "keo", "teo", "chee" are roots? Or is "eo" itself a root?
"""

import re
from collections import Counter


def load_and_extract_eo_patterns(filepath):
    """Extract all words containing 'eo' and analyze their structure"""

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    all_words = []

    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith("<f"):
            match = re.search(r"<f\d+[rv]\d*\.[^>]+>\s+(.+)$", line_stripped)
            if match:
                text = match.group(1)
                text = re.sub(r"<[^>]+>", "", text)
                text = re.sub(r"\{[^}]+\}", "", text)
                text = re.sub(r"\[[^\]]+\]", "", text)
                text = re.sub(r"[@!]\d+;", "", text)
                words = re.findall(r"[a-z]+", text.lower())
                all_words.extend(words)

    # Find all words with 'eo'
    eo_words = [w for w in all_words if "eo" in w]

    # Exclude known roots
    eo_words_filtered = []
    for w in eo_words:
        if w.startswith("ok") or w.startswith("qok"):
            continue
        if w.startswith("ot") or w.startswith("qot"):
            continue
        if w.startswith("cho") or w.startswith("cheo"):
            continue
        if w.startswith("she"):
            continue
        eo_words_filtered.append(w)

    return Counter(eo_words_filtered)


def analyze_structure(word_counts):
    """Analyze structural patterns in 'eo' words"""

    print("\n" + "=" * 70)
    print('STRUCTURAL ANALYSIS OF "EO" WORDS')
    print("=" * 70)

    # Try to identify: what comes BEFORE 'eo'?
    before_eo = Counter()
    after_eo = Counter()

    for word in word_counts.keys():
        # Find position of 'eo'
        match = re.search(r"(.*)eo(.*)", word)
        if match:
            before = match.group(1)
            after = match.group(2)

            if before:  # Something before 'eo'
                before_eo[before] += word_counts[word]

            if after:  # Something after 'eo'
                after_eo[after] += word_counts[word]

    print(f'\nTop 20 elements BEFORE "eo":')
    for elem, count in before_eo.most_common(20):
        print(f"  {elem:15} + eo : {count:4} instances")

    print(f'\nTop 20 elements AFTER "eo":')
    for elem, count in after_eo.most_common(20):
        print(f"  eo + {elem:15} : {count:4} instances")

    # Check if these are known morphemes
    suffixes = ["dy", "edy", "ol", "al", "or", "ar", "aiin", "iin", "ain"]

    print("\n" + "=" * 70)
    print("HYPOTHESIS TESTING")
    print("=" * 70)

    # Hypothesis 1: "eo" is a root, takes normal suffixes
    h1_count = sum(
        count for elem, count in after_eo.items() if elem in suffixes or not elem
    )
    h1_pct = 100 * h1_count / sum(after_eo.values()) if after_eo else 0
    print(f'\nHypothesis 1: "eo" is a SEMANTIC ROOT')
    print(f'  Evidence: "eo" + known suffix = {h1_count} instances ({h1_pct:.1f}%)')
    print(f"  Examples: eo + dy, eo + ol, eo + or, etc.")

    # Hypothesis 2: "eo" is part of compound roots (keo, teo, chee, etc.)
    compound_roots = ["k", "t", "y", "ch", "ke", "te", "ye", "che", "kche", "tche"]
    h2_count = sum(count for elem, count in before_eo.items() if elem in compound_roots)
    h2_pct = 100 * h2_count / sum(before_eo.values()) if before_eo else 0
    print(f'\nHypothesis 2: "eo" is part of COMPOUND roots')
    print(f'  Evidence: consonant + "eo" = {h2_count} instances ({h2_pct:.1f}%)')
    print(f"  Examples: k+eo, t+eo, ch+eo, etc.")
    print(f'  Possible roots: "keo", "teo", "cheo" (wait, we know "cheo"!)')

    # Hypothesis 3: "eo" appears bare (standalone)
    bare_eo = word_counts.get("eo", 0)
    print(f'\nHypothesis 3: "eo" appears as standalone word')
    print(f'  Evidence: bare "eo" = {bare_eo} instances')

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    if bare_eo > 20:
        print('  → "eo" DOES appear standalone frequently')
        print("  → Likely a SEMANTIC ROOT (function word or noun)")
    else:
        print('  → "eo" RARELY appears standalone')
        print("  → Likely a COMPOUND ELEMENT or SUFFIX")

    if h2_pct > 60:
        print('  → Most instances are consonant + "eo"')
        print('  → Possible roots: "keo", "teo", "yeo", etc.')

    # Check specific candidates
    print("\n" + "=" * 70)
    print("CANDIDATE ROOTS TO INVESTIGATE")
    print("=" * 70)

    candidates = []
    for elem in before_eo.most_common(10):
        root = elem[0] + "eo"
        candidates.append((root, elem[1]))

    print('\nTop candidate roots (prefix + "eo"):')
    for root, count in candidates:
        print(f"  {root:10} : {count:4} instances → investigate this!")


if __name__ == "__main__":
    filepath = (
        "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/ZL3b-n.txt"
    )

    print('Loading and analyzing "eo" word structure...')
    word_counts = load_and_extract_eo_patterns(filepath)

    print(f'\nTotal "eo" words (excluding ok/ot/cho/she): {len(word_counts)}')
    print(f"Total instances: {sum(word_counts.values())}")

    analyze_structure(word_counts)
