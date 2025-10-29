"""
Quick validation of top 5 vocabulary candidates

Based on scoring:
1. sho (6/8) - already investigated, botanical term
2. ol (5/8) - but likely suffix, not semantic root
3. al (5/8) - but likely suffix
4. eo (5/8) - worth investigating
5. ar (4/8) - but likely suffix

Let's focus on eo and any other 4-5/8 candidates that aren't suffixes
"""

import re
from collections import Counter


def load_and_find(filepath, target_root):
    """Load text and find target root contexts"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    contexts = []
    current_section = "unknown"

    for line in lines:
        line_stripped = line.strip()

        if "# herbal" in line_stripped.lower():
            current_section = "herbal"
        elif "# pharmaceutical" in line_stripped.lower():
            current_section = "pharmaceutical"
        elif (
            "# biological" in line_stripped.lower() or "# bath" in line_stripped.lower()
        ):
            current_section = "biological"
        elif "# astronomical" in line_stripped.lower():
            current_section = "astronomical"

        if line_stripped.startswith("<f"):
            match = re.search(r"<f\d+[rv]\d*\.[^>]+>\s+(.+)$", line_stripped)
            if match:
                text = match.group(1)
                text = re.sub(r"<[^>]+>", "", text)
                text = re.sub(r"\{[^}]+\}", "", text)
                text = re.sub(r"\[[^\]]+\]", "", text)
                text = re.sub(r"[@!]\d+;", "", text)
                words = re.findall(r"[a-z!]+", text.lower())

                for i, word in enumerate(words):
                    # Check if target appears (but not as part of known roots)
                    if target_root in word:
                        # Exclude if it's part of known roots
                        if target_root == "eo":
                            if "cheo" in word:  # cheo is validated
                                continue
                            if (
                                "sheo" in word or "oeo" in word
                            ):  # likely compound with known root
                                continue

                        context = {
                            "word": word,
                            "section": current_section,
                            "before": words[max(0, i - 2) : i],
                            "after": words[i + 1 : min(len(words), i + 3)],
                        }
                        contexts.append(context)

    return contexts


def analyze_candidate(root_name, contexts):
    """Quick analysis of candidate"""

    print(f"\n{'=' * 70}")
    print(f"ANALYZING: {root_name}")
    print(f"{'=' * 70}")

    if not contexts:
        print("No contexts found!")
        return

    print(f"Total instances: {len(contexts)}")

    # Section distribution
    by_section = Counter(c["section"] for c in contexts)
    print(f"\nSection distribution:")
    for section, count in by_section.most_common():
        pct = count / len(contexts) * 100
        print(f"  {section}: {count} ({pct:.1f}%)")

    # Forms
    forms = Counter(c["word"] for c in contexts)
    print(f"\nTop 15 forms:")
    for form, count in forms.most_common(15):
        print(f"  {form:20} ({count})")

    # Morphology
    with_case = sum(1 for c in contexts if c["word"].endswith(("al", "ar", "ol", "or")))
    with_verbal = sum(1 for c in contexts if "dy" in c["word"] or "edy" in c["word"])

    print(f"\nMorphological patterns:")
    print(f"  With case: {with_case} ({with_case / len(contexts) * 100:.1f}%)")
    print(f"  With verbal: {with_verbal} ({with_verbal / len(contexts) * 100:.1f}%)")

    # Sample contexts
    print(f"\nSample contexts (first 10):")
    for i, ctx in enumerate(contexts[:10], 1):
        before = " ".join(ctx["before"])
        after = " ".join(ctx["after"])
        print(f"  {i}. {before} >>> {ctx['word']} <<< {after}")

    # Assessment
    print(f"\nQUICK ASSESSMENT:")
    case_rate = with_case / len(contexts) * 100
    verbal_rate = with_verbal / len(contexts) * 100

    if 30 <= case_rate <= 60 and verbal_rate < 20:
        print(f"  ✓ LIKELY NOUN (case: {case_rate:.1f}%, verbal: {verbal_rate:.1f}%)")
    elif case_rate < 20 and verbal_rate > 40:
        print(f"  ✓ LIKELY VERB (case: {case_rate:.1f}%, verbal: {verbal_rate:.1f}%)")
    elif case_rate > 70:
        print(f"  ✗ LIKELY SUFFIX (case: {case_rate:.1f}% - too high)")
    else:
        print(f"  ? AMBIGUOUS (case: {case_rate:.1f}%, verbal: {verbal_rate:.1f}%)")


def main():
    print("QUICK VALIDATION OF TOP VOCABULARY CANDIDATES")
    print("=" * 70)

    filepath = (
        "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/ZL3b-n.txt"
    )

    # Test candidates (excluding clear suffixes)
    candidates = [
        ("eo", "5/8 score"),
        ("sho", "6/8 score - already validated as botanical"),
    ]

    for root, note in candidates:
        contexts = load_and_find(filepath, root)
        analyze_candidate(f"{root} ({note})", contexts)

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print("\nValidated so far:")
    print("  1. oak (ok/qok) - plant name")
    print("  2. oat (ot/qot) - plant name")
    print("  3. water (shee/she) - liquid")
    print("  4. red (dor) - color")
    print("  5. vessel (cho) - container")
    print("  6. cheo - concrete noun")
    print("  7. sho - botanical term (NEW!)")

    print("\nNext to validate:")
    print("  - eo (if shows nominal pattern)")
    print("  - Additional candidates from 4-5/8 range")


if __name__ == "__main__":
    main()
