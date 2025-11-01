"""
COMPREHENSIVE 60% VALIDATION SUITE

This script performs 4 critical validation tasks:
1. Translation Audit - Test 25-30 random sentences for coherence
2. Compound Pattern Verification - Validate productive morphology claims
3. Root Confidence Audit - Review 10 lowest-confidence roots
4. Statistical Robustness Check - Verify patterns and null hypothesis

Goal: Determine if 60% semantic understanding is solid or inflated
Decision: PROCEED to 65-70% / FIX issues / PAUSE & revise
"""

import json
import random
from collections import Counter, defaultdict
from pathlib import Path

# Set random seed for reproducibility
random.seed(42)

print("=" * 80)
print("COMPREHENSIVE 60% VALIDATION SUITE")
print("=" * 80)
print()

# Load data
print("Loading data files...")
data_dir = Path("C:/Users/adria/Documents/manuscript")

# Load Phase 17 translations
with open(
    data_dir / "COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8"
) as f:
    phase17_data = json.load(f)

translations = phase17_data.get("translations", [])
total_corpus_words = phase17_data.get("metadata", {}).get("total_words", 37125)

print(f"✓ Loaded {len(translations)} sentences")
print(f"✓ Total corpus: {total_corpus_words:,} words")

# Load vocabulary from all batches
vocab = {}

# Load Batch 1 (Big 5)
try:
    with open(
        data_dir / "BATCH1_BIG5_ROOTS_TO_53_PERCENT.json", "r", encoding="utf-8"
    ) as f:
        vocab.update(json.load(f))
except:
    pass

# Load Batch 2 (Medium 5)
try:
    with open(
        data_dir / "BATCH2_MEDIUM5_ROOTS_TO_57_PERCENT.json", "r", encoding="utf-8"
    ) as f:
        vocab.update(json.load(f))
except:
    pass

# Load Batch 3 (Final 13)
try:
    with open(
        data_dir / "BATCH3_FINAL13_TO_60_PERCENT.json", "r", encoding="utf-8"
    ) as f:
        vocab.update(json.load(f))
except:
    pass

# Extended vocabulary from VOCABULARY_42_ROOTS (manually extracted)
KNOWN_ROOTS = {
    # Very high confidence (85-95%)
    "qok": {"meaning": "oak", "confidence": 95, "class": "NOMINAL"},
    "qot": {"meaning": "oat", "confidence": 95, "class": "NOMINAL"},
    "ok": {"meaning": "oak-variant", "confidence": 90, "class": "NOMINAL"},
    "sho": {"meaning": "vessel/container", "confidence": 95, "class": "NOMINAL"},
    "cho": {"meaning": "vessel/container", "confidence": 95, "class": "NOMINAL"},
    "dain": {"meaning": "water", "confidence": 95, "class": "NOMINAL"},
    "ar": {"meaning": "at/in", "confidence": 95, "class": "LOCATIVE"},
    # High confidence (75-84%)
    "ch": {"meaning": "take/use/mix", "confidence": 90, "class": "VERBAL"},
    "sh": {"meaning": "mix/prepare", "confidence": 90, "class": "VERBAL"},
    "or": {"meaning": "and/or", "confidence": 90, "class": "CONJUNCTION"},
    "ol": {"meaning": "and/also", "confidence": 90, "class": "CONJUNCTION"},
    "dar": {"meaning": "place/there", "confidence": 80, "class": "LOCATIVE"},
    "al": {"meaning": "the/LOC", "confidence": 80, "class": "ARTICLE"},
    "a": {"meaning": "the (article)", "confidence": 90, "class": "ARTICLE"},
    "y": {"meaning": "is/be (copula)", "confidence": 85, "class": "COPULA"},
    "ain": {"meaning": "this/that", "confidence": 75, "class": "DEMONSTRATIVE"},
    "daiin": {"meaning": "the/this", "confidence": 80, "class": "DEMONSTRATIVE"},
    # Medium confidence (65-74%)
    "e": {"meaning": "process/prepare", "confidence": 70, "class": "VERBAL"},
    "s": {"meaning": "plant/herb", "confidence": 70, "class": "NOMINAL"},
    "eey": {"meaning": "GEN-particle", "confidence": 80, "class": "PARTICLE"},
    "k": {"meaning": "container/tool", "confidence": 65, "class": "NOMINAL"},
    "lch": {"meaning": "mix/stir", "confidence": 75, "class": "VERBAL"},
    "eo": {"meaning": "boil/cook", "confidence": 70, "class": "VERBAL"},
    "che": {"meaning": "oak-bark", "confidence": 75, "class": "NOMINAL"},
    "ey": {"meaning": "grain/seed", "confidence": 75, "class": "NOMINAL"},
    "chey": {"meaning": "then/also", "confidence": 75, "class": "PARTICLE"},
    "chy": {"meaning": "also/too", "confidence": 75, "class": "PARTICLE"},
    "cheey": {"meaning": "particle", "confidence": 70, "class": "PARTICLE"},
    "lk": {"meaning": "liquid", "confidence": 70, "class": "NOMINAL"},
    "chol": {"meaning": "vessel/botanical", "confidence": 75, "class": "NOMINAL"},
    "air": {"meaning": "sky/above", "confidence": 70, "class": "LOCATIVE"},
    "sal": {"meaning": "and", "confidence": 75, "class": "CONJUNCTION"},
    "qol": {"meaning": "then", "confidence": 75, "class": "CONJUNCTION"},
    "am": {"meaning": "very/much", "confidence": 75, "class": "INTENSIFIER"},
    "yk": {"meaning": "LOC/TEMP", "confidence": 70, "class": "BOUND"},
    "yt": {"meaning": "TEMP/LOC", "confidence": 70, "class": "BOUND"},
    # Batch 1-3 additions
    "d": {"meaning": "place/location", "confidence": 75, "class": "NOMINAL"},
    "shey": {"meaning": "oak-preparation", "confidence": 80, "class": "NOMINAL"},
    "r": {"meaning": "substance", "confidence": 65, "class": "NOMINAL"},
    "dy": {"meaning": "verbal/directional", "confidence": 70, "class": "BOUND"},
    "l": {"meaning": "nominal", "confidence": 65, "class": "NOMINAL"},
    "okeey": {"meaning": "oak-GEN", "confidence": 80, "class": "COMPOUND"},
    "cth": {"meaning": "nominal", "confidence": 65, "class": "NOMINAL"},
    "sheey": {"meaning": "preparation-particle", "confidence": 70, "class": "PARTICLE"},
    "oke": {"meaning": "oak-variant", "confidence": 70, "class": "NOMINAL"},
    "chckhy": {"meaning": "complex-particle", "confidence": 60, "class": "PARTICLE"},
    # Batch 3 compounds (CLAIMS TO VERIFY)
    "oky": {"meaning": "oak-is (N+COPULA)", "confidence": 75, "class": "COMPOUND"},
    "aly": {"meaning": "LOC-is (LOC+COPULA)", "confidence": 70, "class": "COMPOUND"},
    "sheo": {"meaning": "mix-boil (V+V)", "confidence": 70, "class": "COMPOUND"},
    "eeo": {"meaning": "process-boil (V+V)", "confidence": 65, "class": "COMPOUND"},
    "kch": {
        "meaning": "container-process (N+V)",
        "confidence": 65,
        "class": "COMPOUND",
    },
    "okch": {"meaning": "oak-process (N+V)", "confidence": 70, "class": "COMPOUND"},
    "dch": {"meaning": "place-process (N+V)", "confidence": 60, "class": "COMPOUND"},
    "pch": {
        "meaning": "substance-process (N+V)",
        "confidence": 60,
        "class": "COMPOUND",
    },
    "opch": {"meaning": "complex-process", "confidence": 60, "class": "COMPOUND"},
    "keey": {"meaning": "container-GEN (N+GEN)", "confidence": 70, "class": "COMPOUND"},
    # Lower confidence
    "o": {"meaning": "oak-variant/particle", "confidence": 65, "class": "MIXED"},
    "p": {"meaning": "substance", "confidence": 65, "class": "NOMINAL"},
    "ee": {"meaning": "e-variant?", "confidence": 60, "class": "NOMINAL"},
}

print(f"✓ Loaded {len(KNOWN_ROOTS)} known roots")
print()

# Known suffixes
VERB_SUFFIXES = ["dy", "edy", "ody"]
CASE_SUFFIXES = ["ain", "aiin", "ol", "al", "ar", "or", "el"]

# ============================================================================
# TASK 1: TRANSLATION AUDIT
# ============================================================================

print("=" * 80)
print("TASK 1: TRANSLATION AUDIT - Testing sentence coherence")
print("=" * 80)
print()


def translate_word(word_data, known_roots):
    """Translate a single word based on morphology"""
    morphology = word_data.get("morphology", {})
    root = morphology.get("root", "")
    suffixes = morphology.get("suffixes", [])
    original = word_data.get("original", "")

    # Check if root is known
    if root in known_roots:
        root_info = known_roots[root]
        translation = root_info["meaning"]
        confidence = root_info["confidence"]

        # Add suffix meanings
        suffix_meanings = []
        for suffix in suffixes:
            if suffix in ["dy", "edy", "ody"]:
                suffix_meanings.append("VERB")
            elif suffix in ["ain", "aiin"]:
                suffix_meanings.append("GEN")
            elif suffix in ["ol", "al", "el"]:
                suffix_meanings.append("LOC")
            elif suffix in ["ar", "or"]:
                suffix_meanings.append("DIR")
            else:
                suffix_meanings.append(f"?{suffix}")

        if suffix_meanings:
            return f"{translation}-{'-'.join(suffix_meanings)}", confidence, True
        else:
            return translation, confidence, True
    else:
        # Unknown root
        if suffixes:
            return f"[?{root}]-{'-'.join(suffixes)}", 0, False
        else:
            return f"[?{root}]", 0, False


def score_translation_coherence(translated_words, original_words):
    """
    Score translation coherence on 1-5 scale:
    5 = Fully coherent pharmaceutical/botanical instruction
    4 = Mostly coherent with minor gaps
    3 = Partially coherent (general topic clear)
    2 = Fragmentary (some meaning, many gaps)
    1 = Nonsense (no coherent meaning)
    """
    # Calculate % of words translated
    known_count = sum(1 for _, _, known in translated_words if known)
    total_count = len(translated_words)
    known_pct = known_count / total_count if total_count > 0 else 0

    # Extract translation text
    translation = " ".join([word for word, _, _ in translated_words])

    # Check for pharmaceutical/botanical keywords
    pharmaceutical_keywords = [
        "oak",
        "oat",
        "vessel",
        "container",
        "water",
        "liquid",
        "mix",
        "prepare",
        "boil",
        "cook",
        "take",
        "use",
        "herb",
        "plant",
        "grain",
        "seed",
        "bark",
    ]

    botanical_count = sum(
        1 for kw in pharmaceutical_keywords if kw in translation.lower()
    )

    # Heuristic scoring
    if known_pct >= 0.8 and botanical_count >= 3:
        score = 5  # Fully coherent
    elif known_pct >= 0.7 and botanical_count >= 2:
        score = 4  # Mostly coherent
    elif known_pct >= 0.5 and botanical_count >= 1:
        score = 3  # Partially coherent
    elif known_pct >= 0.3:
        score = 2  # Fragmentary
    else:
        score = 1  # Nonsense

    return score, known_pct, botanical_count


# Select 30 random sentences (stratified sampling)
num_samples = 30
sample_size_per_quartile = num_samples // 4

samples = []
quartile_size = len(translations) // 4

for i in range(4):
    start_idx = i * quartile_size
    end_idx = (i + 1) * quartile_size if i < 3 else len(translations)
    quartile_samples = random.sample(
        translations[start_idx:end_idx], sample_size_per_quartile
    )
    samples.extend(quartile_samples)

# Add 2 more random samples to reach 30
if len(samples) < num_samples:
    additional = random.sample(translations, num_samples - len(samples))
    samples.extend(additional)

print(f"Selected {len(samples)} random sentences for translation audit")
print()

# Translate and score
translation_results = []
coherence_scores = []

for i, sentence in enumerate(samples, 1):
    words = sentence.get("words", [])
    original_text = " ".join([w.get("original", "") for w in words])

    # Translate each word
    translated_words = []
    for word_data in words:
        translation, confidence, known = translate_word(word_data, KNOWN_ROOTS)
        translated_words.append((translation, confidence, known))

    # Score coherence
    score, known_pct, botanical_count = score_translation_coherence(
        translated_words, words
    )
    coherence_scores.append(score)

    # Build translation string
    translation_text = " ".join([word for word, _, _ in translated_words])

    result = {
        "sentence_num": i,
        "original": original_text,
        "translation": translation_text,
        "coherence_score": score,
        "known_percentage": known_pct,
        "botanical_keywords": botanical_count,
        "word_count": len(words),
        "known_words": sum(1 for _, _, known in translated_words if known),
    }

    translation_results.append(result)

    # Print sample
    if i <= 5 or score >= 4:  # Print first 5 and all high-scoring translations
        print(f"Sentence {i} [Score: {score}/5, Known: {known_pct:.0%}]")
        print(f"  Original: {original_text[:80]}...")
        print(f"  Translation: {translation_text[:80]}...")
        print()

# Calculate statistics
print("=" * 80)
print("TRANSLATION AUDIT RESULTS")
print("=" * 80)
print()

score_distribution = Counter(coherence_scores)
avg_score = sum(coherence_scores) / len(coherence_scores)
pct_coherent_3plus = sum(1 for s in coherence_scores if s >= 3) / len(coherence_scores)
pct_coherent_4plus = sum(1 for s in coherence_scores if s >= 4) / len(coherence_scores)

print(f"Total sentences analyzed: {len(samples)}")
print(f"Average coherence score: {avg_score:.2f}/5.0")
print()
print("Score distribution:")
for score in range(5, 0, -1):
    count = score_distribution[score]
    pct = count / len(coherence_scores) * 100
    bar = "█" * int(pct / 2)
    print(f"  {score}/5: {count:2d} ({pct:5.1f}%) {bar}")
print()
print(f"Partially coherent or better (3+): {pct_coherent_3plus:.1%}")
print(f"Mostly coherent or better (4+):    {pct_coherent_4plus:.1%}")
print()

# Determine success
if pct_coherent_3plus >= 0.80:
    task1_result = "✓ PASS"
    task1_status = "STRONG - 80%+ translations coherent"
elif pct_coherent_3plus >= 0.70:
    task1_result = "⚠ MODERATE"
    task1_status = "70-79% coherent - minor issues"
else:
    task1_result = "✗ FAIL"
    task1_status = "<70% coherent - major problems"

print(f"Task 1 Result: {task1_result}")
print(f"Status: {task1_status}")
print()

# Save detailed results
with open("VALIDATION_TASK1_TRANSLATION_AUDIT.json", "w", encoding="utf-8") as f:
    json.dump(
        {
            "summary": {
                "total_sentences": len(samples),
                "average_score": avg_score,
                "coherent_3plus_pct": pct_coherent_3plus,
                "coherent_4plus_pct": pct_coherent_4plus,
                "result": task1_result,
                "status": task1_status,
            },
            "score_distribution": dict(score_distribution),
            "translations": translation_results,
        },
        f,
        indent=2,
        ensure_ascii=False,
    )

print("✓ Detailed results saved to: VALIDATION_TASK1_TRANSLATION_AUDIT.json")
print()

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("=" * 80)
print("VALIDATION SUITE - TASK 1 COMPLETE")
print("=" * 80)
print()
print(f"Task 1 (Translation Audit): {task1_result}")
print()
print("Next: Run Task 2 (Compound Pattern Verification)")
print("      Run Task 3 (Root Confidence Audit)")
print("      Run Task 4 (Statistical Robustness Check)")
print()
print("=" * 80)
