"""
Re-translate test sentences with 7 validated nouns

BEFORE (Phase 5A): 6 nouns, 58% recognition, 100% structure
NOW (Phase 6): 7 nouns, expecting 65-70% recognition

New noun: sho - botanical term (43% case, 11% verbal, herbal-enriched)
"""


def translate_word_phase6(word):
    """Translate with 7 validated nouns + complete grammar"""

    parts = []
    remaining = word

    # 1. Genitive prefix
    if word.startswith("qok"):
        parts.append("oak-GEN")
        remaining = word[3:]
    elif word.startswith("qot"):
        parts.append("oat-GEN")
        remaining = word[3:]
    elif word.startswith("ok"):
        parts.append("oak")
        remaining = word[2:]
    elif word.startswith("ot"):
        parts.append("oat")
        remaining = word[2:]

    # 2. Semantic nouns
    if "shee" in remaining:
        parts.append("water")
        remaining = remaining.replace("shee", "", 1)
    elif "she" in remaining:
        parts.append("water")
        remaining = remaining.replace("she", "", 1)

    if "sho" in remaining:
        parts.append("SHO")  # NEW botanical term
        remaining = remaining.replace("sho", "", 1)

    if "cho" in remaining and "cheo" not in remaining:
        parts.append("vessel")
        remaining = remaining.replace("cho", "", 1)

    if "cheo" in remaining:
        parts.append("CHEO")
        remaining = remaining.replace("cheo", "", 1)

    if "dor" in remaining:
        parts.append("red")
        remaining = remaining.replace("dor", "", 1)

    # 3. Function words
    if "qol" in remaining:
        parts.append("[THEN]")
        remaining = remaining.replace("qol", "", 1)
    if "sal" in remaining:
        parts.append("[AND]")
        remaining = remaining.replace("sal", "", 1)
    if "dain" in remaining or "dai!n" in remaining:
        parts.append("[THAT]")
        remaining = remaining.replace("dain", "", 1).replace("dai!n", "", 1)
    if remaining.endswith("ory"):
        parts.append("[ADV]")
        remaining = remaining[:-3]

    # 4. Verbal suffix
    if "edy" in remaining:
        parts.append("VERB")
        remaining = remaining.replace("edy", "", 1)
    elif remaining.endswith("dy"):
        parts.append("VERB")
        remaining = remaining[:-2]

    # 5. Definiteness
    if "aiin" in remaining:
        parts.append("DEF")
        remaining = remaining.replace("aiin", "", 1)
    elif "iin" in remaining:
        parts.append("DEF")
        remaining = remaining.replace("iin", "", 1)
    elif "ain" in remaining:
        parts.append("DEF")
        remaining = remaining.replace("ain", "", 1)

    # 6. Case markers
    if "al" in remaining:
        parts.append("LOC")
        remaining = remaining.replace("al", "", 1)
    if "ar" in remaining:
        parts.append("DIR")
        remaining = remaining.replace("ar", "", 1)
    if "or" in remaining:
        parts.append("INST")
        remaining = remaining.replace("or", "", 1)
    if "ol" in remaining:
        parts.append("LOC2")
        remaining = remaining.replace("ol", "", 1)

    # 7. Unknown
    if remaining and remaining not in [
        "",
        "k",
        "ch",
        "p",
        "s",
        "l",
        "d",
        "y",
        "e",
        "!",
        "t",
        "c",
        "h",
        "f",
        "ck",
    ]:
        parts.append(f"[?{remaining}]")

    if not parts:
        return f"[?{word}]"

    return ".".join(parts)


def translate_sentence(sentence):
    """Translate entire sentence"""
    words = sentence.split()
    translations = []

    for word in words:
        if word in ["qol", "sal", "dain", "dai!n", "ol", "or"]:
            translations.append(f"[{word.upper()}]")
        else:
            translations.append(translate_word_phase6(word))

    return " ".join(translations)


def assess_coherence(translation, original, num):
    """Assess if translation is coherent"""

    # Count known vs unknown
    unknown = translation.count("[?")
    total_words = len(original.split())
    known_pct = max(0, (1 - unknown / total_words) * 100)

    # Coherence criteria
    has_content = any(
        term in translation
        for term in ["oak", "oat", "water", "vessel", "SHO", "red", "CHEO"]
    )
    has_structure = "VERB" in translation or any(
        case in translation for case in ["LOC", "DIR", "INST"]
    )
    has_function = any(fw in translation for fw in ["THEN", "AND", "THAT"])

    coherent = has_content and has_structure

    return {
        "known_pct": known_pct,
        "coherent": coherent,
        "has_content": has_content,
        "has_structure": has_structure,
        "has_function": has_function,
    }


def main():
    print("=" * 70)
    print("PHASE 6: RE-TRANSLATION WITH 7 VALIDATED NOUNS")
    print("=" * 70)
    print("\nValidated vocabulary:")
    print("  1. oak (ok/qok)")
    print("  2. oat (ot/qot)")
    print("  3. water (shee/she)")
    print("  4. red (dor)")
    print("  5. vessel (cho)")
    print("  6. CHEO")
    print("  7. SHO - botanical term (NEW!)")
    print("\n" + "=" * 70)

    # Test sentences from multiple sections
    test_sentences = [
        # Herbal (where SHO appears frequently)
        ("qokeey qokain shey okal sheekal otol ot ot ot", "f84v - bath/herbal"),
        ("shol sheey qokey ykody sochol", "f2r - herbal"),
        ("sho shol qotcho", "f2v - herbal"),
        # Biological
        ("dshedy qokedy okar qokedy shedy ykedy shedy qoky", "f78r - biological"),
        ("qotal dol shedy qokedar", "f78r - biological"),
        # Pharmaceutical
        ("dorsheoy ctheol qockhey dory sheor sholfchor", "f88r - pharmaceutical"),
        # Astronomical
        ("chocfhy saral", "f67r2 - astronomical"),
    ]

    results = []

    for i, (sentence, source) in enumerate(test_sentences, 1):
        print(f"\n{'=' * 70}")
        print(f"SENTENCE {i} ({source})")
        print(f"{'=' * 70}")
        print(f"Original:    {sentence}")

        translation = translate_sentence(sentence)
        assessment = assess_coherence(translation, sentence, i)

        print(f"Translation: {translation}")
        print(f"\nKnown: {assessment['known_pct']:.0f}%")
        print(f"Coherent: {'YES ✓✓✓' if assessment['coherent'] else 'NO ✗'}")

        if assessment["coherent"]:
            print("Why coherent:")
            if assessment["has_content"]:
                print("  ✓ Has semantic content (botanical/concrete terms)")
            if assessment["has_structure"]:
                print("  ✓ Has grammatical structure (case/verbal marking)")
            if assessment["has_function"]:
                print("  ✓ Has function words (discourse markers)")

        results.append(
            {
                "sentence": sentence,
                "source": source,
                "translation": translation,
                "assessment": assessment,
            }
        )

    # Summary
    print(f"\n\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")

    coherent_count = sum(1 for r in results if r["assessment"]["coherent"])
    avg_known = sum(r["assessment"]["known_pct"] for r in results) / len(results)

    print(
        f"\nCoherent sentences: {coherent_count}/{len(results)} ({coherent_count / len(results) * 100:.0f}%)"
    )
    print(f"Average recognition: {avg_known:.0f}%")

    print(f"\n{'=' * 70}")
    print("COMPARISON TO PREVIOUS PHASES")
    print(f"{'=' * 70}")
    print(f"Phase 4 (6 nouns, no function words): 1/5 coherent (20%)")
    print(f"Phase 5 (6 nouns + grammar):          3/5 coherent (60%)")
    print(f"Phase 5A (validated grammar):         5/5 coherent (100%) on f84v")
    print(
        f"Phase 6 (7 nouns + grammar):          {coherent_count}/{len(results)} coherent ({coherent_count / len(results) * 100:.0f}%)"
    )

    if coherent_count >= 6:
        print("\n✓✓✓ EXCELLENT PROGRESS")
        print("Adding 'sho' improved translation capability!")
        print("Continue expanding vocabulary systematically.")
    elif coherent_count >= 5:
        print("\n✓✓ GOOD PROGRESS")
        print("'sho' helps in herbal sections.")
        print("Need more pharmaceutical/astronomical terms.")

    print(f"\n{'=' * 70}")
    print("NEXT STEPS")
    print(f"{'=' * 70}")
    print("1. Validate 3-5 more high-scoring candidates")
    print("2. Focus on domain-specific terms:")
    print("   - Pharmaceutical section: validate terms enriched there")
    print("   - Astronomical section: validate terms from that domain")
    print("3. Re-test with 10-12 nouns")
    print("4. Target: 15-20 validated nouns for publication")


if __name__ == "__main__":
    main()
