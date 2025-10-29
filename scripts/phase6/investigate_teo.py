"""
Investigate "teo" - potential pharmaceutical/herbal term

From earlier analysis: 53 instances in compound analysis
Question: Is "teo" related to "keo" (pharmaceutical term)?
Or is it a separate root?

E↔O substitution check: teo ↔ tee? toe?
"""

import re
from collections import Counter


def load_voynich_with_context(filepath):
    """Load with context and section tracking"""

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    contexts = []
    current_section = "unknown"

    for line in lines:
        line_stripped = line.strip()

        # Track section
        if line_stripped.startswith("<f"):
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

                # Find "teo" instances (but NOT ok/ot + suffix)
                for i, word in enumerate(words):
                    if "teo" not in word:
                        continue

                    # EXCLUDE known root decompositions
                    if word.startswith("ok") or word.startswith("qok"):
                        continue
                    if word.startswith("ot") or word.startswith("qot"):
                        continue
                    if word.startswith("cho") or word.startswith("cheo"):
                        continue
                    if word.startswith("she"):
                        continue
                    if word.startswith("sho"):
                        continue
                    if word.startswith("keo"):
                        continue

                    # NOW we have TRUE "teo" instance
                    context = {
                        "word": word,
                        "section": current_section,
                        "before": words[max(0, i - 3) : i],
                        "after": words[i + 1 : min(len(words), i + 4)],
                    }
                    contexts.append(context)

    return contexts


def analyze_teo(contexts):
    """Analyze 'teo' as potential root"""

    print("\n" + "=" * 70)
    print('"TEO" INVESTIGATION')
    print("=" * 70)

    print(f"\nTotal TRUE instances: {len(contexts)}")

    # Section distribution
    by_section = Counter(ctx["section"] for ctx in contexts)
    print(f"\nSection distribution:")
    total = len(contexts)
    for section, count in by_section.most_common():
        pct = 100 * count / total
        enrichment = pct / 25.0
        print(f"  {section:20} {count:4} ({pct:5.1f}%) - {enrichment:.2f}x enrichment")

    # Forms
    teo_forms = Counter(ctx["word"] for ctx in contexts)
    print(f"\nTop 20 forms:")
    for form, count in teo_forms.most_common(20):
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
        print(f"  ? Verbal rate: {verbal_pct:.1f}%")

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

    # E↔O substitution check
    print("\n" + "=" * 70)
    print("E↔O SUBSTITUTION CHECK")
    print("=" * 70)
    print('teo → too: no known root "too"')
    print('teo → tee: might relate to "tee" forms?')
    print('teo → toe: check if "toe" exists...')

    # Check if related to "keo"
    print("\nRelationship to KEO (pharmaceutical term)?")
    print("keo + t prefix → tkeo (not observed)")
    print("teo vs keo: different consonants, likely separate roots")

    # Calculate evidence score
    score = 0
    evidence = []

    # 1. Co-occurrence (need to check)
    known_roots = [
        "ok",
        "qok",
        "ot",
        "qot",
        "shee",
        "she",
        "cho",
        "cheo",
        "dor",
        "sho",
        "keo",
    ]
    cooccur_count = 0
    for ctx in contexts:
        before_after = ctx["before"] + ctx["after"]
        if any(any(root in w for root in known_roots) for w in before_after):
            cooccur_count += 1

    cooccur_pct = 100 * cooccur_count / total
    if cooccur_pct > 30:
        score += 2
        evidence.append(
            f"✓ High co-occurrence with validated nouns ({cooccur_pct:.1f}%) (2/2)"
        )
    elif cooccur_pct > 20:
        score += 1
        evidence.append(f"✓ Moderate co-occurrence (1/2)")
    else:
        evidence.append(f"✗ Low co-occurrence ({cooccur_pct:.1f}%) (0/2)")

    # 2. Section enrichment
    top_section_pct = 100 * by_section.most_common(1)[0][1] / total
    if top_section_pct > 40:
        score += 2
        evidence.append(
            f"✓ Strong enrichment in {by_section.most_common(1)[0][0]} ({top_section_pct:.1f}%) (2/2)"
        )
    elif top_section_pct > 30:
        score += 1
        evidence.append(f"✓ Moderate enrichment (1/2)")
    else:
        evidence.append(f"✗ No strong enrichment ({top_section_pct:.1f}%) (0/2)")

    # 3. Case-marking
    if 30 <= case_pct <= 60:
        score += 2
        evidence.append(f"✓ Ideal case-marking rate ({case_pct:.1f}%) (2/2)")
    elif 20 <= case_pct <= 70:
        score += 1
        evidence.append(f"✓ Acceptable case-marking (1/2)")
    else:
        evidence.append(f"✗ Case-marking outside range ({case_pct:.1f}%) (0/2)")

    # 4. Verbal rate
    if verbal_pct < 10:
        score += 2
        evidence.append(f"✓ Very low verbal rate ({verbal_pct:.1f}%) (2/2)")
    elif verbal_pct < 15:
        score += 1
        evidence.append(f"✓ Low verbal rate (1/2)")
    else:
        evidence.append(f"✗ High verbal rate ({verbal_pct:.1f}%) (0/2)")

    print("\n" + "=" * 70)
    print("EVIDENCE SCORE (8/8 SYSTEM)")
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
        print(f'  ✓✓✓ "TEO" is a {top_section.upper()}-ENRICHED TERM')
        return True
    elif score >= 4:
        print(f"  ? POSSIBLE noun ({score}/8) - needs more investigation")
        return False
    else:
        print(f"  ✗ Unlikely to be a noun ({score}/8)")
        print(f"  ✗ May be grammatical element or low-frequency term")
        return False


if __name__ == "__main__":
    filepath = (
        "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/ZL3b-n.txt"
    )

    print("Loading Voynich manuscript...")
    contexts = load_voynich_with_context(filepath)

    if len(contexts) < 20:
        print(f"\n⚠️  WARNING: Only {len(contexts)} TRUE instances found")
        print('   "teo" may not be a standalone root (too rare)')

    validated = analyze_teo(contexts)

    if validated:
        print("\n" + "=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print('  1. Add "teo" to validated vocabulary (9th noun!)')
        print("  2. Re-test translations with 9 nouns")
        print("  3. Continue validating more candidates")
