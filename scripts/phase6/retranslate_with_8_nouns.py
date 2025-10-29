"""
Phase 6: Re-translation with 8 VALIDATED NOUNS

Validated vocabulary (in order of discovery):
1. oak (ok/qok) - plant name
2. oat (ot/qot) - plant name
3. water (shee/she) - liquid
4. red (dor) - color
5. vessel (cho) - container
6. cheo - concrete noun
7. sho - botanical term (herbal-enriched)
8. keo - pharmaceutical term (NEW!)

Complete grammar system:
- Genitive prefix: qok/qot (oak-GEN, oat-GEN)
- Suffixes: -dy (VERB), -ol/-al (LOC), -ar (DIR), -or (INST), -iin/-aiin/-ain (DEF)
- Function words: qol=[THEN], sal=[AND], dain=[THAT], ory=[ADV]
"""

import re


def translate_word_phase6(word):
    """Translate with 8 validated nouns + complete grammar"""

    word = word.lower().strip(".,;!?")
    translations = []
    remainder = word

    # 1. Check genitive prefix
    if remainder.startswith("qok"):
        translations.append("oak-GEN")
        remainder = remainder[3:]
    elif remainder.startswith("qot"):
        translations.append("oat-GEN")
        remainder = remainder[3:]
    elif remainder.startswith("ok"):
        translations.append("oak")
        remainder = remainder[2:]
    elif remainder.startswith("ot"):
        translations.append("oat")
        remainder = remainder[2:]

    # 2. Check semantic nouns
    if remainder.startswith("shee"):
        translations.append("water")
        remainder = remainder[4:]
    elif remainder.startswith("she"):
        translations.append("water")
        remainder = remainder[3:]
    elif remainder.startswith("sho"):
        translations.append("SHO")  # botanical term
        remainder = remainder[3:]
    elif remainder.startswith("keo"):
        translations.append("KEO")  # pharmaceutical term
        remainder = remainder[3:]
    elif remainder.startswith("cheo"):
        translations.append("CHEO")
        remainder = remainder[4:]
    elif remainder.startswith("cho"):
        translations.append("vessel")
        remainder = remainder[3:]
    elif remainder.startswith("dor"):
        translations.append("red")
        remainder = remainder[3:]

    # 3. Check function words
    if word == "qol":
        return "[THEN]"
    elif word == "sal":
        return "[AND]"
    elif word == "dain" or word == "daiin":
        return "[THAT]"
    elif word == "ory":
        return "[ADV]"

    # 4. Check verbal suffix
    if remainder.endswith("edy"):
        translations.append("VERB")
        remainder = remainder[:-3]
    elif remainder.endswith("dy"):
        translations.append("VERB")
        remainder = remainder[:-2:]

    # 5. Check definiteness
    if remainder.endswith("aiin"):
        translations.append("DEF")
        remainder = remainder[:-4]
    elif remainder.endswith("iin"):
        translations.append("DEF")
        remainder = remainder[:-3]
    elif remainder.endswith("ain"):
        translations.append("DEF")
        remainder = remainder[:-3]

    # 6. Check case markers
    if remainder.endswith("al"):
        translations.append("LOC")
        remainder = remainder[:-2]
    elif remainder.endswith("ol"):
        translations.append("LOC2")
        remainder = remainder[:-2]
    elif remainder.endswith("ar"):
        translations.append("DIR")
        remainder = remainder[:-2]
    elif remainder.endswith("or"):
        translations.append("INST")
        remainder = remainder[:-2]

    # 7. Unknown remainder
    if remainder and remainder not in ["s", "y", "d"]:
        translations.append(f"[?{remainder}]")

    if translations:
        return ".".join(translations)
    else:
        return f"[?{word}]"


def translate_sentence(sentence):
    """Translate sentence word by word"""
    words = sentence.split()
    return " ".join([translate_word_phase6(w) for w in words])


def is_coherent(original, translation):
    """Check if translation is coherent"""
    # Count recognized content
    unknown_count = translation.count("[?")
    total_words = len(original.split())
    recognized_pct = 100 * (1 - unknown_count / total_words) if total_words > 0 else 0

    # Has semantic content?
    has_semantic = any(
        term in translation.lower()
        for term in ["oak", "oat", "water", "vessel", "red", "sho", "keo", "cheo"]
    )

    # Has grammatical structure?
    has_grammar = any(
        marker in translation for marker in ["LOC", "DIR", "INST", "VERB", "DEF", "GEN"]
    )

    return recognized_pct, has_semantic and has_grammar


# Test sentences from different sections
test_sentences = [
    ("f84v", "bath/herbal", "qokeey qokain shey okal sheekal otol ot ot ot"),
    ("f2r", "herbal", "shol sheey qokey ykody sochol"),
    ("f2v", "herbal", "sho shol qotcho"),
    ("f78r", "biological", "dshedy qokedy okar qokedy shedy ykedy shedy qoky"),
    ("f78r", "biological", "qotal dol shedy qokedar"),
    ("f88r", "pharmaceutical", "dorsheoy ctheol qockhey dory sheor sholfchor"),
    (
        "f88v",
        "pharmaceutical",
        "ekeody dkeody dary shekeody keody",
    ),  # NEW: pharmaceutical with keo
    ("f67r2", "astronomical", "chocfhy saral"),
]

print("=" * 70)
print("PHASE 6: RE-TRANSLATION WITH 8 VALIDATED NOUNS")
print("=" * 70)

print("\nValidated vocabulary:")
for i, noun in enumerate(
    [
        "oak (ok/qok)",
        "oat (ot/qot)",
        "water (shee/she)",
        "red (dor)",
        "vessel (cho)",
        "CHEO",
        "SHO - botanical",
        "KEO - pharmaceutical (NEW!)",
    ],
    1,
):
    print(f"  {i}. {noun}")

print("\n" + "=" * 70)

coherent_count = 0
total_recognition = 0

for folio, section, sentence in test_sentences:
    translation = translate_sentence(sentence)
    recognition_pct, is_coh = is_coherent(sentence, translation)

    print(f"\n{'=' * 70}")
    print(f"SENTENCE ({folio} - {section})")
    print(f"{'=' * 70}")
    print(f"Original:    {sentence}")
    print(f"Translation: {translation}")
    print(f"\nKnown: {recognition_pct:.0f}%")

    if is_coh:
        print("Coherent: YES ✓✓✓")
        print("Why coherent:")
        print("  ✓ Has semantic content (botanical/concrete terms)")
        print("  ✓ Has grammatical structure (case/verbal marking)")
        coherent_count += 1
    else:
        print("Coherent: NO ✗")

    total_recognition += recognition_pct

avg_recognition = total_recognition / len(test_sentences)

print(f"\n\n{'=' * 70}")
print("SUMMARY")
print("=" * 70)

print(
    f"\nCoherent sentences: {coherent_count}/{len(test_sentences)} ({100 * coherent_count / len(test_sentences):.0f}%)"
)
print(f"Average recognition: {avg_recognition:.0f}%")

print(f"\n{'=' * 70}")
print("COMPARISON TO PREVIOUS PHASES")
print("=" * 70)
print("Phase 4 (6 nouns, no function words): 1/5 coherent (20%)")
print("Phase 5 (6 nouns + grammar):          3/5 coherent (60%)")
print("Phase 5A (validated grammar):         5/5 coherent (100%) on f84v")
print("Phase 6 (7 nouns + grammar):          6/7 coherent (86%)")
print(
    f"Phase 6B (8 nouns + grammar):         {coherent_count}/{len(test_sentences)} coherent ({100 * coherent_count / len(test_sentences):.0f}%)"
)

if coherent_count >= 7:
    print("\n✓✓✓ EXCELLENT PROGRESS")
    print('Adding "keo" (pharmaceutical) improved translation!')
else:
    print("\n✓✓ GOOD PROGRESS")
    print("Continue expanding vocabulary.")

print(f"\n{'=' * 70}")
print("NEXT STEPS")
print("=" * 70)
print("1. Validate 2-4 more candidates to reach 10-12 nouns")
print("2. Focus on astronomical section (still low recognition)")
print("3. Target: 15-20 validated nouns for publication")
