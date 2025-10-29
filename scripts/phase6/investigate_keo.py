"""
Investigate "keo" - potential pharmaceutical-specific root

From compound analysis:
- "keo" appears 78 times
- Mostly as: keol, keody (with case/verbal markers)
- Enriched in pharmaceutical section (60.7% of "eo" words)

Is "keo" a semantic noun (pharmaceutical term)?
"""

import re
from collections import Counter


def load_voynich_with_context(filepath):
    """Load with line context preserved"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    contexts = []
    current_section = "unknown"

    for line in lines:
        line_stripped = line.strip()

        # Track section
        if "# herbal" in line_stripped.lower() or "Language A" in line_stripped:
            current_section = "herbal"
        elif "# pharmaceutical" in line_stripped.lower():
            current_section = "pharmaceutical"
        elif (
            "# biological" in line_stripped.lower()
            or "# balnea" in line_stripped.lower()
        ):
            current_section = "biological"
        elif (
            "# astronomical" in line_stripped.lower()
            or "# cosmo" in line_stripped.lower()
        ):
            current_section = "astronomical"

        # Parse folio lines
        if line_stripped.startswith("<f"):
            # Extract section from folio number
            folio_match = re.search(r"<f(\d+)[rv]", line_stripped)
            if folio_match:
                num = int(folio_match.group(1))
                if 1 <= num <= 66:
                    current_section = "herbal"
                elif 67 <= num <= 73:
                    current_section = "astronomical"
                elif 75 <= num <= 84:
                    current_section = "biological"
                elif 85 <= num <= 116:
                    current_section = "pharmaceutical"

            match = re.search(r"<f\d+[rv]\d*\.[^>]+>\s+(.+)$", line_stripped)
            if match:
                text = match.group(1)
                text = re.sub(r"<[^>]+>", "", text)
                text = re.sub(r"\{[^}]+\}", "", text)
                text = re.sub(r"\[[^\]]+\]", "", text)
                text = re.sub(r"[@!]\d+;", "", text)
                words = re.findall(r"[a-z]+", text.lower())

                # Find TRUE "keo" instances (not ok/qok + eol)
                for i, word in enumerate(words):
                    if "keo" not in word:
                        continue

                    # EXCLUDE if it's actually oak + suffix (okeol, qokeol, okeody, etc.)
                    if word.startswith("ok") or word.startswith("qok"):
                        continue

                    # EXCLUDE other known roots
                    if word.startswith("ot") or word.startswith("qot"):
                        continue
                    if word.startswith("cho") or word.startswith("cheo"):
                        continue
                    if word.startswith("she"):
                        continue
                    if word.startswith("sho"):
                        continue

                    # NOW we have TRUE "keo" instance
                    if True:
                        context = {
                            "word": word,
                            "section": current_section,
                            "before": words[max(0, i - 3) : i],
                            "after": words[i + 1 : min(len(words), i + 4)],
                        }
                        contexts.append(context)

    return contexts


def analyze_keo(contexts):
    """Analyze 'keo' as potential root"""

    print("\n" + "=" * 70)
    print('"KEO" INVESTIGATION - Pharmaceutical-specific root?')
    print("=" * 70)

    print(f"\nTotal instances: {len(contexts)}")

    # Section distribution
    by_section = Counter(ctx["section"] for ctx in contexts)
    print(f"\nSection distribution:")
    total = len(contexts)
    for section, count in by_section.most_common():
        pct = 100 * count / total
        # Calculate enrichment (vs 25% baseline)
        enrichment = pct / 25.0
        print(f"  {section:20} {count:4} ({pct:5.1f}%) - {enrichment:.2f}x enrichment")

    # Forms
    keo_forms = Counter(ctx["word"] for ctx in contexts)
    print(f"\nTop 20 forms:")
    for form, count in keo_forms.most_common(20):
        print(f"  {form:20} ({count:3})")

    # Morphological analysis
    case_markers = ["al", "ol", "ar", "or"]
    verbal_markers = ["dy", "edy"]

    case_count = sum(
        1 for ctx in contexts if any(ctx["word"].endswith(m) for m in case_markers)
    )
    verbal_count = sum(
        1 for ctx in contexts if any(ctx["word"].endswith(m) for m in verbal_markers)
    )

    case_pct = 100 * case_count / total
    verbal_pct = 100 * verbal_count / total

    print("\n" + "=" * 70)
    print("MORPHOLOGICAL EVIDENCE")
    print("=" * 70)
    print(f"Case markers (-ol/-al/-or/-ar): {case_count} ({case_pct:.1f}%)")
    print(f"Verbal markers (-dy/-edy):       {verbal_count} ({verbal_pct:.1f}%)")

    if case_pct >= 30 and case_pct <= 60:
        print("  ✓ Case-marking in NOMINAL sweet spot (30-60%)")
    else:
        print(f"  ? Case-marking outside nominal range: {case_pct:.1f}%")

    if verbal_pct < 15:
        print("  ✓ Low verbal rate (nominal pattern)")
    else:
        print(f"  ? High verbal rate: {verbal_pct:.1f}%")

    # Co-occurrence with validated nouns
    known_roots = ["ok", "qok", "ot", "qot", "shee", "she", "cho", "cheo", "dor", "sho"]

    cooccur_count = 0
    for ctx in contexts:
        before_after = ctx["before"] + ctx["after"]
        if any(any(root in w for root in known_roots) for w in before_after):
            cooccur_count += 1

    cooccur_pct = 100 * cooccur_count / total
    print(f"\nCo-occurs with validated nouns: {cooccur_count} ({cooccur_pct:.1f}%)")

    if cooccur_pct > 25:
        print("  ✓ Frequently appears with known botanical/concrete terms")

    # Sample contexts
    print("\n" + "=" * 70)
    print("SAMPLE CONTEXTS (first 15)")
    print("=" * 70)
    for i, ctx in enumerate(contexts[:15], 1):
        before_str = " ".join(ctx["before"][-2:]) if ctx["before"] else ""
        after_str = " ".join(ctx["after"][:2]) if ctx["after"] else ""
        section_tag = ctx["section"][:4].upper()
        print(
            f"{i:2}. [{section_tag}] {before_str:25} >>> {ctx['word']:15} <<< {after_str}"
        )

    # Calculate evidence score (out of 8)
    score = 0
    evidence = []

    # 1. Co-occurrence (max 2)
    if cooccur_pct > 30:
        score += 2
        evidence.append("✓ High co-occurrence with validated nouns (2/2)")
    elif cooccur_pct > 20:
        score += 1
        evidence.append("✓ Moderate co-occurrence (1/2)")

    # 2. Section enrichment (max 2)
    top_section_pct = 100 * by_section.most_common(1)[0][1] / total
    if top_section_pct > 40:
        score += 2
        evidence.append(
            f"✓ Strong enrichment in {by_section.most_common(1)[0][0]} ({top_section_pct:.1f}%) (2/2)"
        )
    elif top_section_pct > 30:
        score += 1
        evidence.append(f"✓ Moderate enrichment (1/2)")

    # 3. Case-marking (max 2)
    if 30 <= case_pct <= 60:
        score += 2
        evidence.append(f"✓ Ideal case-marking rate ({case_pct:.1f}%) (2/2)")
    elif 20 <= case_pct <= 70:
        score += 1
        evidence.append(f"✓ Acceptable case-marking (1/2)")

    # 4. Verbal rate (max 2)
    if verbal_pct < 10:
        score += 2
        evidence.append(f"✓ Very low verbal rate ({verbal_pct:.1f}%) (2/2)")
    elif verbal_pct < 15:
        score += 1
        evidence.append(f"✓ Low verbal rate (1/2)")

    print("\n" + "=" * 70)
    print("EVIDENCE SCORE")
    print("=" * 70)
    for ev in evidence:
        print(f"  {ev}")

    print(f"\nTOTAL SCORE: {score}/8")

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    if score >= 6:
        print(f"  ✓✓✓ VALIDATED as semantic noun ({score}/8)")
        top_section = by_section.most_common(1)[0][0]
        print(f'  ✓✓✓ "KEO" is a {top_section.upper()}-SPECIFIC TERM')
        return True
    elif score >= 4:
        print(f"  ? POSSIBLE noun ({score}/8) - needs more investigation")
        return False
    else:
        print(f"  ✗ Unlikely to be a noun ({score}/8)")
        return False


if __name__ == "__main__":
    filepath = (
        "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/ZL3b-n.txt"
    )

    print("Loading Voynich manuscript...")
    contexts = load_voynich_with_context(filepath)

    validated = analyze_keo(contexts)

    if validated:
        print("\n" + "=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print('  1. Add "keo" to validated vocabulary')
        print("  2. Re-test translations with 8 nouns")
        print("  3. Continue validating more candidates")
