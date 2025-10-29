"""
END-TO-END TRANSLATION TEST

The critical validation: Can we actually translate complete sentences?

This will reveal what's blocking translation:
- Missing vocabulary?
- Wrong grammar model?
- Incorrect morphological boundaries?

Author: Research Assistant
Date: 2025-10-29
"""

import json
from pathlib import Path


def load_f84v_sentences():
    """Load first 5 sentences from f84v"""
    with open(
        "results/phase4/readable_passages/f84v_oak_oat_bath_folio.txt",
        "r",
        encoding="utf-8",
    ) as f:
        sentences = []
        for line in f:
            line = line.strip()
            if line.startswith("Voynich:"):
                text = line.replace("Voynich:", "").strip()
                words = text.split()
                if words:
                    sentences.append(words)
                if len(sentences) >= 5:
                    break
        return sentences


def decompose_word(word):
    """Morphologically decompose a word using validated knowledge

    Returns: {
        'original': word,
        'prefix': genitive prefix if present,
        'root': core root,
        'suffixes': list of suffixes,
        'known_elements': list of known meanings
    }
    """
    original = word
    components = {
        "original": original,
        "prefix": None,
        "root": None,
        "suffixes": [],
        "known_elements": [],
    }

    remaining = word.lower()

    # Step 1: Check for genitive prefix qok-
    if remaining.startswith("qok") and len(remaining) > 3:
        components["prefix"] = "qok"
        components["known_elements"].append("GENITIVE")
        remaining = remaining[3:]

    # Step 2: Strip case suffixes (may be multiple!)
    case_markers = ["al", "ar", "ol", "or"]
    while len(remaining) > 2:
        found_case = False
        for case in case_markers:
            if remaining.endswith(case):
                components["suffixes"].insert(0, case)
                components["known_elements"].append(f"CASE:{case}")
                remaining = remaining[:-2]
                found_case = True
                break
        if not found_case:
            break

    # Step 3: Check for verbal suffix -edy
    if remaining.endswith("edy") and len(remaining) > 3:
        components["suffixes"].insert(0, "edy")
        components["known_elements"].append("VERBAL")
        remaining = remaining[:-3]

    # Step 4: What's left is the root
    components["root"] = remaining

    # Step 5: Identify known roots
    if "ok" in remaining:
        components["known_elements"].append("ROOT:oak")
    if "ot" in remaining and "ok" not in remaining:
        components["known_elements"].append("ROOT:oat")
    if remaining in ["daiin", "aiin", "saiin", "oiin"]:
        components["known_elements"].append("PRONOUN")
    if remaining in ["chear", "shear"]:
        components["known_elements"].append("ROOT:ear")
    if "cheek" in remaining:
        components["known_elements"].append("ROOT:cheek")
    if remaining == "dor":
        components["known_elements"].append("ROOT:red")
    if remaining in ["ol", "ar", "or", "al", "y", "dar"]:
        components["known_elements"].append("PARTICLE?")

    return components


def translate_word(decomposition):
    """Attempt to translate a decomposed word"""
    parts = []

    # Genitive
    if decomposition["prefix"] == "qok":
        parts.append("[of-")

    # Root
    root = decomposition["root"]
    if "ROOT:oak" in decomposition["known_elements"]:
        parts.append("oak")
    elif "ROOT:oat" in decomposition["known_elements"]:
        parts.append("oat")
    elif "ROOT:ear" in decomposition["known_elements"]:
        parts.append("ear")
    elif "ROOT:cheek" in decomposition["known_elements"]:
        parts.append("cheek")
    elif "ROOT:red" in decomposition["known_elements"]:
        parts.append("red")
    elif "PRONOUN" in decomposition["known_elements"]:
        if root == "daiin":
            parts.append("this/it")
        elif root == "aiin":
            parts.append("this/that")
        elif root == "saiin":
            parts.append("such/thus")
        else:
            parts.append(f"PRONOUN({root})")
    elif "PARTICLE?" in decomposition["known_elements"]:
        parts.append(f"[{root}]")
    else:
        parts.append(f"???({root})")

    # Genitive close
    if decomposition["prefix"] == "qok":
        parts.append("'s]")

    # Suffixes
    for suffix in decomposition["suffixes"]:
        if suffix in ["al", "ar", "ol", "or"]:
            parts.append(f"-{suffix.upper()}")
        elif suffix == "edy":
            parts.append("-VERB")

    return "".join(parts)


def attempt_translation(sentence_words):
    """Attempt end-to-end translation of a sentence"""

    print("  STEP 1: MORPHOLOGICAL DECOMPOSITION")
    print("  " + "-" * 76)

    decompositions = []
    for word in sentence_words:
        decomp = decompose_word(word)
        decompositions.append(decomp)

        # Show decomposition
        parts = []
        if decomp["prefix"]:
            parts.append(f"{decomp['prefix']}-")
        parts.append(decomp["root"])
        if decomp["suffixes"]:
            parts.append(f"-{'|'.join(decomp['suffixes'])}")

        known = (
            ", ".join(decomp["known_elements"])
            if decomp["known_elements"]
            else "UNKNOWN"
        )
        print(f"    {decomp['original']:15s} → {' '.join(parts):20s} [{known}]")

    print()
    print("  STEP 2: WORD-BY-WORD TRANSLATION")
    print("  " + "-" * 76)

    translations = []
    for decomp in decompositions:
        trans = translate_word(decomp)
        translations.append(trans)
        print(f"    {decomp['original']:15s} → {trans}")

    print()
    print("  STEP 3: SENTENCE RECONSTRUCTION")
    print("  " + "-" * 76)

    # Count knowns vs unknowns
    total_words = len(decompositions)
    known_words = sum(1 for d in decompositions if d["known_elements"])
    unknown_words = total_words - known_words

    print(
        f"    Coverage: {known_words}/{total_words} words recognized ({100 * known_words / total_words:.1f}%)"
    )
    print()
    print(f"    Raw gloss: {' '.join(translations)}")
    print()

    # Attempt coherent translation
    print("  STEP 4: COHERENCE ATTEMPT")
    print("  " + "-" * 76)

    # Try to build a coherent sentence
    coherent_attempt = attempt_coherent_translation(decompositions, translations)

    print(f"    Best guess: {coherent_attempt['translation']}")
    print(f"    Confidence: {coherent_attempt['confidence']}")
    print()

    print("  STEP 5: TRANSLATION BLOCKERS")
    print("  " + "-" * 76)

    blockers = identify_blockers(decompositions, coherent_attempt)

    for i, blocker in enumerate(blockers, 1):
        print(f"    {i}. {blocker}")
    print()

    return {
        "sentence": " ".join(sentence_words),
        "decompositions": decompositions,
        "translations": translations,
        "coverage": 100 * known_words / total_words,
        "coherent_attempt": coherent_attempt,
        "blockers": blockers,
    }


def attempt_coherent_translation(decompositions, translations):
    """Try to build a coherent sentence from translations"""

    # Check if we have a pronoun at the start
    has_initial_pronoun = (
        "PRONOUN" in decompositions[0]["known_elements"] if decompositions else False
    )

    # Check if we have known verbs
    has_verb = any("VERBAL" in d["known_elements"] for d in decompositions)

    # Check if we have oak/oat
    has_oak_oat = any(
        "ROOT:oak" in d["known_elements"] or "ROOT:oat" in d["known_elements"]
        for d in decompositions
    )

    # Attempt translation based on structure
    if has_initial_pronoun and has_oak_oat:
        # Pattern: PRONOUN ... oak/oat ...
        # Likely: "This [involves/uses] oak/oat..."
        translation = "This [preparation] with " + " and ".join(
            [t for t in translations if "oak" in t or "oat" in t]
        )
        confidence = "LOW - missing verbs"
    elif has_oak_oat:
        # Pattern: ... oak/oat ...
        # Likely: "[Using] oak/oat..."
        translation = "[Prepare] with " + " and ".join(
            [t for t in translations if "oak" in t or "oat" in t]
        )
        confidence = "VERY LOW - missing subject and verb"
    else:
        # Can't construct anything
        translation = "[Cannot translate - insufficient vocabulary]"
        confidence = "NONE"

    return {
        "translation": translation,
        "confidence": confidence,
        "has_pronoun": has_initial_pronoun,
        "has_verb": has_verb,
        "has_content": has_oak_oat,
    }


def identify_blockers(decompositions, coherent_attempt):
    """Identify what's preventing successful translation"""

    blockers = []

    # Count unknowns
    unknown_roots = [d["root"] for d in decompositions if not d["known_elements"]]
    if unknown_roots:
        unique_unknowns = set(unknown_roots)
        blockers.append(
            f"Unknown roots: {len(unique_unknowns)} distinct ({', '.join(list(unique_unknowns)[:5])}...)"
        )

    # Check for particles
    particles = [
        d["root"] for d in decompositions if "PARTICLE?" in d["known_elements"]
    ]
    if particles:
        blockers.append(f"Unknown function of particles: {set(particles)}")

    # Check verb meanings
    verbs = [d["root"] for d in decompositions if "VERBAL" in d["known_elements"]]
    if verbs:
        blockers.append(
            f"Unknown verb meanings: {set(verbs)} (we know they're verbs, but not what they mean)"
        )

    # Check case system
    cases = [
        s
        for d in decompositions
        for s in d["suffixes"]
        if s in ["al", "ar", "ol", "or"]
    ]
    if cases and not coherent_attempt["has_verb"]:
        blockers.append(
            f"Case markers present but unclear function without verbs: {set(cases)}"
        )

    # Overall coverage issue
    total_known = sum(1 for d in decompositions if d["known_elements"])
    total_words = len(decompositions)
    if total_known / total_words < 0.5:
        blockers.append(
            f"Insufficient vocabulary coverage: only {100 * total_known / total_words:.0f}% known"
        )

    if not blockers:
        blockers.append("No clear blockers - should be translatable!")

    return blockers


def main():
    print("=" * 80)
    print("END-TO-END TRANSLATION TEST")
    print("=" * 80)
    print()
    print("GOAL: Attempt complete translation of 5 f84v sentences")
    print("      Document what prevents successful translation")
    print()

    # Load sentences
    sentences = load_f84v_sentences()

    print(f"Loaded {len(sentences)} sentences from f84v (bath section)")
    print()

    # Attempt translation for each
    results = []

    for i, sentence in enumerate(sentences, 1):
        print("=" * 80)
        print(f"SENTENCE {i}")
        print("=" * 80)
        print()
        print(f"  Raw text: {' '.join(sentence)}")
        print()

        result = attempt_translation(sentence)
        results.append(result)

    # Overall summary
    print("=" * 80)
    print("OVERALL TRANSLATION DIAGNOSIS")
    print("=" * 80)
    print()

    avg_coverage = sum(r["coverage"] for r in results) / len(results)
    print(f"Average vocabulary coverage: {avg_coverage:.1f}%")
    print()

    # Collect all blockers
    all_blockers = {}
    for result in results:
        for blocker in result["blockers"]:
            all_blockers[blocker] = all_blockers.get(blocker, 0) + 1

    print("MOST COMMON TRANSLATION BLOCKERS:")
    print()
    for blocker, count in sorted(
        all_blockers.items(), key=lambda x: x[1], reverse=True
    ):
        print(f"  [{count}/5 sentences] {blocker}")
    print()

    # Diagnosis
    print("=" * 80)
    print("DIAGNOSTIC CONCLUSION")
    print("=" * 80)
    print()

    if avg_coverage < 30:
        print("✗ CRITICAL BOTTLENECK: Insufficient vocabulary")
        print()
        print("  Primary issue: Too many unknown roots")
        print("  Recommended fix: Expand validated vocabulary through:")
        print("    - N-gram analysis around known words")
        print("    - Co-occurrence patterns with oak/oat")
        print("    - Cross-section validation")
    elif avg_coverage < 60:
        print("~ MODERATE BOTTLENECK: Partial vocabulary")
        print()
        print("  Primary issue: Know structure but not enough content words")
        print("  Recommended fix: Focus on decoding high-frequency unknown roots")
    else:
        print("✓ GOOD COVERAGE: Should be translatable")
        print()
        print("  Primary issue: Need to understand word order and grammar better")
        print("  Recommended fix: Study sentence structure patterns")
    print()

    # Save results
    output_path = Path("results/phase4/end_to_end_translation_test.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Detailed results saved to: {output_path}")


if __name__ == "__main__":
    main()
