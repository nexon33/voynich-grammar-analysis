"""
Quick test of astronomical section f67r2

Simple focused test to validate grammar works in astronomical domain
"""

import re

# Test lines from f67r2 (from manual inspection of file)
test_lines = [
    "opodchol s ain aldy",
    "soeey doiin oldy",
    "odaiiin okoes oekain y",
    "otchey soraiir dy",
    "qopchy daiin dal",
    "ydchos ain ar amy",
    "chocfhy saral",
    "sain am ar",
    "oparchy salsain",
    "sodar ofar ar",
]


def parse_word_fixed_grammar(word):
    """Parse using fixed grammar"""
    components = {"roots": [], "function_words": [], "suffixes": [], "unknown": []}
    remaining = word

    # Semantic roots
    if word.startswith("qok"):
        components["roots"].append("oak-GEN")
        remaining = word[3:]
    elif word.startswith("qot"):
        components["roots"].append("oat-GEN")
        remaining = word[3:]
    elif word.startswith("ok"):
        components["roots"].append("oak")
        remaining = word[2:]
    elif word.startswith("ot"):
        components["roots"].append("oat")
        remaining = word[2:]

    if "shee" in remaining:
        components["roots"].append("water")
        remaining = remaining.replace("shee", "", 1)
    elif "she" in remaining:
        components["roots"].append("water")
        remaining = remaining.replace("she", "", 1)

    if "cho" in remaining and "cheo" not in remaining:
        components["roots"].append("vessel")
        remaining = remaining.replace("cho", "", 1)

    if "cheo" in remaining:
        components["roots"].append("CHEO")
        remaining = remaining.replace("cheo", "", 1)

    if "dor" in remaining:
        components["roots"].append("red")
        remaining = remaining.replace("dor", "", 1)

    # Function words
    if "qol" in remaining:
        components["function_words"].append("THEN")
        remaining = remaining.replace("qol", "", 1)
    if "sal" in remaining:
        components["function_words"].append("AND")
        remaining = remaining.replace("sal", "", 1)
    if "dain" in remaining or "dai!n" in remaining:
        components["function_words"].append("THAT")
        remaining = remaining.replace("dain", "", 1).replace("dai!n", "", 1)
    if remaining.endswith("ory"):
        components["suffixes"].append("ADV")
        remaining = remaining[:-3]

    # Verbal
    if "edy" in remaining:
        components["suffixes"].append("VERB")
        remaining = remaining.replace("edy", "", 1)
    elif remaining.endswith("dy"):
        components["suffixes"].append("VERB")
        remaining = remaining[:-2]

    # Definiteness
    if "aiin" in remaining:
        components["suffixes"].append("DEF")
        remaining = remaining.replace("aiin", "", 1)
    elif "iin" in remaining:
        components["suffixes"].append("DEF")
        remaining = remaining.replace("iin", "", 1)
    elif "ain" in remaining:
        components["suffixes"].append("DEF")
        remaining = remaining.replace("ain", "", 1)

    # Cases
    if "al" in remaining:
        components["suffixes"].append("LOC")
        remaining = remaining.replace("al", "", 1)
    if "ar" in remaining:
        components["suffixes"].append("DIR")
        remaining = remaining.replace("ar", "", 1)
    if "or" in remaining:
        components["suffixes"].append("INST")
        remaining = remaining.replace("or", "", 1)
    if "ol" in remaining:
        components["suffixes"].append("LOC2")
        remaining = remaining.replace("ol", "", 1)

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
    ]:
        components["unknown"].append(remaining)

    return components


def format_parsed(word, comp):
    parts = []
    if comp["roots"]:
        parts.extend(comp["roots"])
    if comp["function_words"]:
        parts.extend([f"[{fw}]" for fw in comp["function_words"]])
    if comp["suffixes"]:
        parts.append("-" + "-".join(comp["suffixes"]))
    if comp["unknown"]:
        parts.append(f"[?{comp['unknown'][0]}]")
    return ".".join(parts) if parts else f"[?{word}]"


def calc_recog(comp):
    recog = len(comp["roots"]) + len(comp["function_words"]) + len(comp["suffixes"])
    total = recog + len(comp["unknown"])
    return recog / total if total > 0 else 0


def assess_structure(parsed_words):
    has_roots = any(w["roots"] for w in parsed_words)
    has_suffixes = any(w["suffixes"] for w in parsed_words)
    has_case = any(
        s in w["suffixes"] for w in parsed_words for s in ["LOC", "DIR", "INST", "LOC2"]
    )
    has_verbal = any("VERB" in w["suffixes"] for w in parsed_words)
    has_function = any(w["function_words"] for w in parsed_words)
    score = sum([has_roots, has_suffixes, has_case or has_verbal, has_function])
    return score >= 2, score


print("ASTRONOMICAL SECTION TEST (f67r2)")
print("=" * 70)

results = []
for i, line in enumerate(test_lines, 1):
    words = line.split()
    parsed = []
    recog_rates = []

    for word in words:
        if word in ["qol", "sal", "dain", "dai!n", "ol", "or"]:
            comp = {
                "roots": [],
                "function_words": [word.upper()],
                "suffixes": [],
                "unknown": [],
            }
            recog_rates.append(1.0)
        else:
            comp = parse_word_fixed_grammar(word)
            recog_rates.append(calc_recog(comp))
        parsed.append(comp)

    translation = " ".join(
        format_parsed(w, parsed[j])
        if w not in ["qol", "sal", "dain", "ol", "or"]
        else f"[{w.upper()}]"
        for j, w in enumerate(words)
    )
    avg_recog = sum(recog_rates) / len(recog_rates) if recog_rates else 0
    has_struct, score = assess_structure(parsed)

    print(f"\nLine {i}:")
    print(f"  Original:    {line}")
    print(f"  Translation: {translation}")
    print(f"  Recognition: {avg_recog * 100:.0f}%")
    print(f"  Structure:   {'YES' if has_struct else 'NO'} (score: {score}/4)")

    results.append({"recog": avg_recog, "struct": has_struct})

avg_recog = sum(r["recog"] for r in results) / len(results) * 100
struct_pct = sum(1 for r in results if r["struct"]) / len(results) * 100

print(f"\n{'=' * 70}")
print(f"ASTRONOMICAL SECTION SUMMARY")
print(f"{'=' * 70}")
print(f"Average recognition: {avg_recog:.1f}%")
print(
    f"Structural coherence: {struct_pct:.0f}% ({sum(1 for r in results if r['struct'])}/{len(results)} lines)"
)

if struct_pct >= 80:
    print("\nRESULT: PASS - Astronomical section validates grammar!")
else:
    print("\nRESULT: PARTIAL - Some structural coherence, but below 80% threshold")
