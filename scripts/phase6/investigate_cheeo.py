"""
Investigate "cheeo" vs "cheo"

We know "cheo" is a validated noun.
Is "cheeo" just a variant (e↔o substitution)? Or a compound "che + eo"?
Or is "chee" the actual root?
"""

import re
from collections import Counter


def load_and_compare(filepath):
    """Load and compare cheo vs cheeo"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    cheo_forms = Counter()
    cheeo_forms = Counter()

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

                for word in words:
                    # Count "cheo" forms (but not "cheeo")
                    if "cheo" in word and "cheeo" not in word:
                        cheo_forms[word] += 1
                    # Count "cheeo" forms
                    elif "cheeo" in word:
                        cheeo_forms[word] += 1

    return cheo_forms, cheeo_forms


def analyze_comparison(cheo_forms, cheeo_forms):
    """Compare cheo vs cheeo"""

    print("\n" + "=" * 70)
    print("CHEO vs CHEEO COMPARISON")
    print("=" * 70)

    print(f'\n"cheo" total instances: {sum(cheo_forms.values())}')
    print(f'"cheeo" total instances: {sum(cheeo_forms.values())}')

    print(f'\nTop 15 "cheo" forms:')
    for form, count in cheo_forms.most_common(15):
        print(f"  {form:20} ({count:3})")

    print(f'\nTop 15 "cheeo" forms:')
    for form, count in cheeo_forms.most_common(15):
        print(f"  {form:20} ({count:3})")

    # Check morphology
    case_markers = ["al", "ol", "ar", "or"]
    verbal_markers = ["dy", "edy"]

    cheo_case = sum(
        count
        for form, count in cheo_forms.items()
        if any(form.endswith(m) for m in case_markers)
    )
    cheo_verbal = sum(
        count
        for form, count in cheo_forms.items()
        if any(form.endswith(m) for m in verbal_markers)
    )

    cheeo_case = sum(
        count
        for form, count in cheeo_forms.items()
        if any(form.endswith(m) for m in case_markers)
    )
    cheeo_verbal = sum(
        count
        for form, count in cheeo_forms.items()
        if any(form.endswith(m) for m in verbal_markers)
    )

    cheo_total = sum(cheo_forms.values())
    cheeo_total = sum(cheeo_forms.values())

    print("\n" + "=" * 70)
    print("MORPHOLOGICAL COMPARISON")
    print("=" * 70)
    print(
        f'"cheo":  case {100 * cheo_case / cheo_total:.1f}%, verbal {100 * cheo_verbal / cheo_total:.1f}%'
    )
    print(
        f'"cheeo": case {100 * cheeo_case / cheeo_total:.1f}%, verbal {100 * cheeo_verbal / cheeo_total:.1f}%'
    )

    print("\n" + "=" * 70)
    print("HYPOTHESIS")
    print("=" * 70)

    # If similar morphology, they might be related
    if abs(100 * cheo_case / cheo_total - 100 * cheeo_case / cheeo_total) < 10:
        print("  → Similar morphological patterns")
        print('  → "cheeo" might be a variant of "cheo"')
        print("  → Consider: cheo + e → cheeo (with e insertion)?")
        print('  → Or: chee + o (chee is the root, "o" is something else)?')
    else:
        print("  → Different morphological patterns")
        print('  → "cheeo" is likely a SEPARATE root from "cheo"')

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    if cheeo_total < 50:
        print(f'  → "cheeo" has few instances ({cheeo_total})')
        print("  → Not a high-priority candidate")
    else:
        print(f'  → "cheeo" has sufficient instances ({cheeo_total})')
        print('  → Could be a separate root OR variant of "cheo"')
        print('  → Recommend: treat as ALLOMORPH of "cheo" for now')


if __name__ == "__main__":
    filepath = (
        "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/ZL3b-n.txt"
    )

    print('Loading and comparing "cheo" vs "cheeo"...')
    cheo_forms, cheeo_forms = load_and_compare(filepath)

    analyze_comparison(cheo_forms, cheeo_forms)
