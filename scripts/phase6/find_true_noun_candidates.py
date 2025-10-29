"""
Find TRUE noun candidates (not prefixes/particles)

Key difference from previous search:
- Require candidates to appear STANDALONE frequently (not just in compounds)
- Require strong nominal morphology (30-60% case-marking)
- Check that they're not always word-initial (which suggests prefix)
"""

import re
from collections import Counter


def load_voynich_all_words(filepath):
    """Load all words"""

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

    return all_words


def find_standalone_roots(all_words):
    """Find roots that appear standalone (not always in compounds)"""

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

    word_counts = Counter(all_words)

    # Find 2-4 letter words (likely roots) with moderate frequency
    candidates = {}

    for word, count in word_counts.items():
        # Skip if too short or too long
        if len(word) < 2 or len(word) > 5:
            continue

        # Skip if validated
        if word in validated:
            continue

        # Skip if starts with validated root
        skip = False
        for root in validated:
            if word.startswith(root) and word != root:
                skip = True
                break

        if skip:
            continue

        # Must have moderate frequency
        if 30 <= count <= 300:
            candidates[word] = count

    return candidates


def analyze_morphology(word, all_words):
    """Analyze morphological behavior"""

    # Find all instances of this word (exact and with suffixes)
    instances = [w for w in all_words if word in w]

    if not instances:
        return None

    # Count exact matches (standalone)
    standalone_count = all_words.count(word)
    standalone_pct = 100 * standalone_count / len(instances)

    # Count with case markers
    case_markers = ["al", "ol", "ar", "or"]
    case_forms = [w for w in instances if any(w.endswith(m) for m in case_markers)]
    case_pct = 100 * len(case_forms) / len(instances)

    # Count with verbal markers
    verbal_markers = ["dy", "edy"]
    verbal_forms = [w for w in instances if any(w.endswith(m) for m in verbal_markers)]
    verbal_pct = 100 * len(verbal_forms) / len(instances)

    # Count word-initial position (if mostly initial, it's a prefix)
    initial_count = sum(1 for w in instances if w.startswith(word) and w != word)
    initial_pct = 100 * initial_count / len(instances)

    return {
        "word": word,
        "total_instances": len(instances),
        "standalone_pct": standalone_pct,
        "case_pct": case_pct,
        "verbal_pct": verbal_pct,
        "word_initial_pct": initial_pct,
        "forms": Counter(instances).most_common(5),
    }


def score_as_noun(analysis):
    """Score likelihood of being a noun"""

    score = 0
    reasons = []

    # Must appear standalone sometimes
    if analysis["standalone_pct"] < 10:
        reasons.append("✗ Rarely standalone (likely prefix)")
        return 0, reasons

    # Good case-marking
    if 30 <= analysis["case_pct"] <= 60:
        score += 2
        reasons.append(f"✓✓ Ideal case-marking ({analysis['case_pct']:.1f}%)")
    elif 20 <= analysis["case_pct"] <= 70:
        score += 1
        reasons.append(f"✓ Acceptable case-marking ({analysis['case_pct']:.1f}%)")
    else:
        reasons.append(f"✗ Poor case-marking ({analysis['case_pct']:.1f}%)")

    # Low verbal rate
    if analysis["verbal_pct"] < 10:
        score += 2
        reasons.append(f"✓✓ Very low verbal ({analysis['verbal_pct']:.1f}%)")
    elif analysis["verbal_pct"] < 15:
        score += 1
        reasons.append(f"✓ Low verbal ({analysis['verbal_pct']:.1f}%)")
    else:
        reasons.append(f"✗ High verbal ({analysis['verbal_pct']:.1f}%)")

    # Not always word-initial (not a prefix)
    if analysis["word_initial_pct"] < 30:
        score += 1
        reasons.append(
            f"✓ Not primarily prefix ({analysis['word_initial_pct']:.1f}% initial)"
        )
    else:
        reasons.append(f"? Often word-initial ({analysis['word_initial_pct']:.1f}%)")

    return score, reasons


if __name__ == "__main__":
    filepath = (
        "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/ZL3b-n.txt"
    )

    print("Loading Voynich manuscript...")
    all_words = load_voynich_all_words(filepath)

    print(f"Total words: {len(all_words)}")

    print("\\nFinding standalone root candidates...")
    candidates = find_standalone_roots(all_words)

    print(f"Found {len(candidates)} potential roots (2-5 letters, 30-300 freq)")

    print("\\nAnalyzing morphology...")

    results = []

    for word in list(candidates.keys())[:50]:  # Analyze top 50
        analysis = analyze_morphology(word, all_words)
        if analysis:
            score, reasons = score_as_noun(analysis)

            if score >= 3:  # Minimum threshold
                results.append(
                    {"analysis": analysis, "score": score, "reasons": reasons}
                )

    # Sort by score
    results.sort(key=lambda x: x["score"], reverse=True)

    print("\\n" + "=" * 70)
    print("TOP NOUN CANDIDATES (3+ score)")
    print("=" * 70)

    for i, result in enumerate(results[:10], 1):
        analysis = result["analysis"]
        print(f"\\n{i}. {analysis['word'].upper()} (score: {result['score']}/5)")
        print(f"   Total instances: {analysis['total_instances']}")
        print(f"   Standalone: {analysis['standalone_pct']:.1f}%")
        print(f"   Case-marking: {analysis['case_pct']:.1f}%")
        print(f"   Verbal: {analysis['verbal_pct']:.1f}%")
        print(f"   Top forms: {', '.join(f[0] for f in analysis['forms'][:3])}")
        print(f"   Assessment:")
        for reason in result["reasons"]:
            print(f"     {reason}")

    print("\\n" + "=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)

    if results:
        top_3 = results[:3]
        print(f"\\nInvestigate these candidates with full 8/8 scoring:")
        for i, result in enumerate(top_3, 1):
            word = result["analysis"]["word"]
            score = result["score"]
            count = result["analysis"]["total_instances"]
            print(f"  {i}. {word:10} (preliminary {score}/5, {count} instances)")
    else:
        print("\\n? No strong noun candidates found")
        print("? May have exhausted medium-frequency nouns")
        print("? Consider: lower frequency terms, or we have most key vocabulary")
