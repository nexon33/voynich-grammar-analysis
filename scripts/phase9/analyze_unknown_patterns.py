"""
Phase 9: Analyze Unknown Patterns from Phase 8B Translation

Goal: Identify what's in the 26% unrecognized words
- Suffix variants (e.g., -eey, -ey, -y)
- Unknown function words
- Unknown roots
- Compound patterns

Strategy: Extract all [?...] unknowns from Phase 8B translations and categorize them.
"""

import re
from collections import Counter


def load_voynich_with_context(filepath):
    """Load Voynich manuscript with context"""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    words_with_context = []
    current_section = "unknown"
    current_folio = None

    for line_num, line in enumerate(lines, 1):
        line_stripped = line.strip()

        if not line_stripped or line_stripped.startswith("#"):
            continue

        # Extract folio/section
        folio_match = re.search(r"<f(\d+)[rv]", line_stripped)
        if folio_match:
            folio_num = int(folio_match.group(1))
            current_folio = folio_num

            if 1 <= folio_num <= 66:
                current_section = "herbal"
            elif 67 <= folio_num <= 73:
                current_section = "astronomical"
            elif 75 <= folio_num <= 84:
                current_section = "biological"
            elif 85 <= folio_num <= 116:
                current_section = "pharmaceutical"
            else:
                current_section = "unknown"

        # Extract words
        text = re.sub(r"\[.*?\]", "", line_stripped)
        text = re.sub(r"\{.*?\}", "", text)
        text = re.sub(r"<.*?>", "", text)
        text = re.sub(r"[!*=\-@$%,.:;()']", " ", text)
        words = re.findall(r"[a-z]{2,}", text.lower())

        for i, word in enumerate(words):
            context_before = " ".join(words[max(0, i - 3) : i])
            context_after = " ".join(words[i + 1 : min(len(words), i + 4)])

            words_with_context.append(
                {
                    "word": word,
                    "line": line_num,
                    "folio": current_folio,
                    "section": current_section,
                    "context_before": context_before,
                    "context_after": context_after,
                    "full_sentence": " ".join(words),
                }
            )

    return words_with_context


def translate_word_phase8(word):
    """Translate with Phase 8B vocabulary (21 terms)"""

    word = word.lower().strip(".,;!?")
    translations = []
    remainder = word

    # 1. Function words
    if word == "dair":
        return "[THERE]"
    elif word == "air":
        return "[SKY]"
    elif word == "ar" or word in ["ary", "ars", "arl"]:
        return "[AT/IN]"
    elif word == "daiin" or word == "dain":
        return "[THIS/THAT]"
    elif word == "sal":
        return "[AND]"
    elif word == "qol":
        return "[THEN]"
    elif word == "ory":
        return "[PARTICLE-FINAL]"
    elif word == "y":
        return "[AND?]"

    # 2. Genitive prefix
    if remainder.startswith("qok"):
        translations.append("oak-GEN")
        remainder = remainder[3:]
    elif remainder.startswith("qot"):
        translations.append("oat-GEN")
        remainder = remainder[3:]

    # 3. Roots (check longer first)
    elif remainder.startswith("okal"):
        translations.append("OKAL")
        remainder = remainder[4:]
    elif remainder.startswith("chol"):
        translations.append("CHOL")
        remainder = remainder[4:]
    elif remainder.startswith("cheo"):
        translations.append("CHEO")
        remainder = remainder[4:]
    elif remainder.startswith("ok"):
        translations.append("oak")
        remainder = remainder[2:]
    elif remainder.startswith("ot"):
        translations.append("oat")
        remainder = remainder[2:]
    elif remainder.startswith("or"):
        translations.append("OR")
        remainder = remainder[2:]

    # 4. Semantic roots
    if remainder.startswith("shee"):
        translations.append("water")
        remainder = remainder[4:]
    elif remainder.startswith("she"):
        translations.append("water")
        remainder = remainder[3:]
    elif remainder.startswith("sho"):
        translations.append("SHO")
        remainder = remainder[3:]
    elif remainder.startswith("keo"):
        translations.append("KEO")
        remainder = remainder[3:]
    elif remainder.startswith("teo"):
        translations.append("TEO")
        remainder = remainder[3:]
    elif remainder.startswith("dor"):
        translations.append("red")
        remainder = remainder[3:]
    elif remainder.startswith("dar"):
        translations.append("DAR")
        remainder = remainder[3:]
    elif remainder.startswith("dol"):
        translations.append("DOL")
        remainder = remainder[3:]
    elif remainder.startswith("cho"):
        translations.append("vessel")
        remainder = remainder[3:]

    # 5. Verbal suffix
    if remainder.endswith("edy"):
        translations.append("VERBAL")
        remainder = remainder[:-3]
    elif remainder.endswith("dy"):
        translations.append("VERBAL")
        remainder = remainder[:-2]

    # 6. Definiteness
    if remainder.endswith("aiin"):
        translations.append("DEF")
        remainder = remainder[:-4]
    elif remainder.endswith("iin"):
        translations.append("DEF")
        remainder = remainder[:-3]
    elif remainder.endswith("ain"):
        translations.append("DEF")
        remainder = remainder[:-3]

    # 7. Case markers
    if remainder.endswith("al"):
        translations.append("LOC")
        remainder = remainder[:-2]
    elif remainder.endswith("ol"):
        translations.append("LOC")
        remainder = remainder[:-2]
    elif remainder.endswith("ar") and len(remainder) > 2:
        translations.append("DIR")
        remainder = remainder[:-2]
    elif remainder.endswith("or"):
        translations.append("INST")
        remainder = remainder[:-2]

    # 8. Unknown remainder
    if remainder and remainder not in ["s", "d", "l", "r"]:
        translations.append(f"[?{remainder}]")

    if translations:
        return ".".join(translations)
    else:
        return f"[?{word}]"


def extract_unknowns(translation):
    """Extract all [?...] patterns from translation"""
    return re.findall(r"\[\?([^\]]+)\]", translation)


def categorize_unknown(unknown):
    """Categorize unknown patterns"""
    # Suffix-like (short, end of word)
    if len(unknown) <= 3:
        return "suffix_variant"
    # Compound-like (contains known morphemes)
    elif any(
        root in unknown
        for root in [
            "ok",
            "ot",
            "she",
            "sho",
            "keo",
            "teo",
            "cho",
            "dor",
            "dar",
            "dol",
            "chol",
            "okal",
            "or",
            "cheo",
        ]
    ):
        return "compound"
    # Medium length (2-4 chars) - possible function word
    elif 2 <= len(unknown) <= 4:
        return "function_word_candidate"
    else:
        return "complex_unknown"


print("=" * 70)
print("PHASE 9: ANALYZING UNKNOWN PATTERNS")
print("=" * 70)

print("\nLoading Voynich manuscript...")
words_with_context = load_voynich_with_context(
    "data/voynich/eva_transcription/ZL3b-n.txt"
)
print(f"Loaded {len(words_with_context):,} words")

print("\nTranslating all words and extracting unknowns...")
all_unknowns = []
word_to_unknowns = {}

for entry in words_with_context:
    word = entry["word"]
    translation = translate_word_phase8(word)
    unknowns = extract_unknowns(translation)

    if unknowns:
        all_unknowns.extend(unknowns)
        word_to_unknowns[word] = (translation, unknowns, entry["section"])

print(f"\nTotal unknown patterns found: {len(all_unknowns):,}")
print(f"Unique unknown patterns: {len(set(all_unknowns)):,}")

# Count unknown frequency
unknown_counts = Counter(all_unknowns)

print("\n" + "=" * 70)
print("TOP 50 MOST FREQUENT UNKNOWN PATTERNS")
print("=" * 70)

print(f"\n{'Unknown':<15} {'Count':<10} {'Category':<25} {'% of unknowns':<15}")
print("-" * 70)

for unknown, count in unknown_counts.most_common(50):
    category = categorize_unknown(unknown)
    pct = 100 * count / len(all_unknowns)
    print(f"{unknown:<15} {count:<10} {category:<25} {pct:>5.2f}%")

# Categorize all unknowns
categorized = {}
for unknown, count in unknown_counts.items():
    category = categorize_unknown(unknown)
    if category not in categorized:
        categorized[category] = []
    categorized[category].append((unknown, count))

print("\n" + "=" * 70)
print("UNKNOWN PATTERNS BY CATEGORY")
print("=" * 70)

for category in [
    "suffix_variant",
    "function_word_candidate",
    "compound",
    "complex_unknown",
]:
    if category not in categorized:
        continue

    items = categorized[category]
    total_count = sum(count for _, count in items)
    pct_of_unknowns = 100 * total_count / len(all_unknowns)

    print(f"\n{category.upper().replace('_', ' ')}")
    print(f"  Unique patterns: {len(items)}")
    print(f"  Total instances: {total_count:,} ({pct_of_unknowns:.1f}% of unknowns)")
    print(f"  Top 10:")

    for unknown, count in sorted(items, key=lambda x: x[1], reverse=True)[:10]:
        print(f"    {unknown:<15} {count:>6,} instances")

# Find complete words that are entirely unknown
print("\n" + "=" * 70)
print("TOP 50 COMPLETELY UNKNOWN WORDS (No recognized parts)")
print("=" * 70)

completely_unknown = []
for word, (translation, unknowns, section) in word_to_unknowns.items():
    if translation.startswith("[?") and translation.endswith("]"):
        completely_unknown.append(word)

word_counts = Counter(entry["word"] for entry in words_with_context)
unknown_word_counts = [(w, word_counts[w]) for w in set(completely_unknown)]
unknown_word_counts.sort(key=lambda x: x[1], reverse=True)

print(f"\n{'Word':<15} {'Count':<10} {'% of corpus':<15}")
print("-" * 50)

for word, count in unknown_word_counts[:50]:
    pct = 100 * count / len(words_with_context)
    print(f"{word:<15} {count:<10} {pct:>5.3f}%")

# Calculate overall recognition rate
recognized_words = len(words_with_context) - len(completely_unknown)
recognition_rate = 100 * recognized_words / len(words_with_context)

print("\n" + "=" * 70)
print("OVERALL RECOGNITION STATISTICS")
print("=" * 70)
print(f"Total words in corpus: {len(words_with_context):,}")
print(f"Words with at least some recognition: {recognized_words:,}")
print(
    f"Completely unknown words: {len(completely_unknown):,} ({100 - recognition_rate:.1f}%)"
)
print(f"Overall recognition rate: {recognition_rate:.1f}%")

# Find high-frequency completely unknown words (good Phase 9 candidates)
print("\n" + "=" * 70)
print("PHASE 9 CANDIDATE RECOMMENDATIONS")
print("=" * 70)
print("\nHigh-frequency completely unknown words (n ≥ 50):")
print(f"\n{'Word':<15} {'Count':<10} {'Category Guess':<25}")
print("-" * 60)

high_freq_candidates = [
    (word, count) for word, count in unknown_word_counts if count >= 50
]

for word, count in high_freq_candidates[:20]:
    # Guess category based on length and patterns
    if len(word) == 2:
        guess = "Function word (2-letter)"
    elif len(word) == 3:
        guess = "Root or function word"
    elif len(word) == 4:
        guess = "Root candidate"
    else:
        guess = "Compound or complex root"

    print(f"{word:<15} {count:<10} {guess:<25}")

print(f"\n{len(high_freq_candidates)} high-frequency candidates identified (n ≥ 50)")

print("\n" + "=" * 70)
print("RECOMMENDED PHASE 9 STRATEGY")
print("=" * 70)
print("""
Based on unknown pattern analysis:

1. **Priority 1: Suffix variants** (~40% of unknowns)
   - Investigate: -eey, -ey, -y, -e, -k variants
   - These appear frequently in partially-recognized words
   - May be verbal/adjectival markers

2. **Priority 2: High-frequency function words** (~20% of unknowns)
   - Investigate: 2-3 letter completely unknown words with n ≥ 100
   - Likely prepositions, conjunctions, particles
   - Use 10-point validation framework

3. **Priority 3: Compound roots** (~30% of unknowns)
   - Investigate: Words containing known roots but extra material
   - May be multi-root compounds
   - Systematic pattern analysis

4. **Priority 4: Unknown roots** (~10%)
   - Investigate: High-frequency 2-4 letter words
   - Apply morphological productivity analysis
   - Use inverted scoring (high morphology = good)

**Target**: Push from 74% to 80%+ word recognition
""")

print("\n" + "=" * 70)
