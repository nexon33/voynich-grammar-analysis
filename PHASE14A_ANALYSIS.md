# Phase 14A Analysis: Bound Morphemes vs. Independent Roots

## Discovery

Phase 14A identified 101 vowel-initial candidates with n≥20, but **most are bound morphemes** (suffixes, connecting vowels, prefix components) rather than independent morphological roots.

## Evidence

### Top "Candidates" are Actually Known Suffixes/Elements

| Element | Total | Standalone | Prod% | Identity |
|---------|-------|------------|-------|----------|
| **ok** | 6123 | 0.6% | 99.4% | qok-/qot- GENITIVE PREFIX (known) |
| **in** | 6059 | 0.4% | 99.6% | -ain/-iin/-aiin SUFFIX (known) |
| **ol** | 5462 | 10.5% | 89.5% | {OL} LOCATIVE PREFIX + -ol SUFFIX (known) |
| **ee** | 4874 | 1.0% | 99.0% | Vowel reduplication/lengthening element |
| **iin** | 4315 | 0.6% | 99.4% | -iin SUFFIX variant (known) |
| **ey** | 4069 | 0.9% | 99.1% | -ey SUFFIX variant |
| **ot** | 3906 | 0.7% | 99.3% | {OL} /ot/ ALLOMORPH (Phase 13 discovery!) |
| **al** | 3110 | 8.7% | 91.3% | -al LOCATIVE SUFFIX (known) |
| **ain** | 1684 | 7.2% | 92.8% | -ain SUFFIX (known) |

### Key Observation

All top candidates show **<11% standalone frequency** and **>85% productivity**, indicating they are **BOUND MORPHEMES** that almost never appear as complete words.

### Comparison to Validated Independent Elements

For contrast, validated independent roots show different patterns:

| Element | Type | Standalone% | Prod% |
|---------|------|-------------|-------|
| **or** | Root | 14.8% | 85.2% | 
| **okal** | Root | 33.3% | 66.7% |
| **chol** | Root | 47.1% | 52.9% |
| **chey** | Function | 98.9% | 1.1% |
| **aiin** | Demonstrative | Unknown | ~15% |

Independent roots typically show **>15-50% standalone usage**, while function words show **>80% standalone**.

## What We Actually Need

From Phase 13's ot- stem analysis, the **true vowel-initial root candidates** are:

### High Priority (appeared frequently with ot-)

| Stem | ot- count | Expected Type |
|------|-----------|---------------|
| **edy** | 162 | Root (possibly verbal) |
| **aiin** | 154 | ALREADY VALIDATED 9/10 |
| **eeedy** | 98 | Root or reduplication+suffix |
| **eey** | 72 | Root or suffix variant |
| **eedy** | 68 | Root or edy+suffix |
| **or** | 61 | ALREADY VALIDATED 10/10 |
| **ol** (independent) | 54 | May be function word or root |
| **ar** | 32 | ALREADY VALIDATED (function word) |

### Medium Priority

| Stem | ot- count | Expected Type |
|------|-----------|---------------|
| **ain** (independent) | 24 | Possibly function word |
| **al** (independent) | 19 | Possibly function word |
| **eeey** | 48 | Vowel sequence + suffix |
| **eeeedy** | 42 | Vowel sequence + suffix |

## The Problem with Current Approach

The current script's `calculate_morphological_productivity()` function treats **substring matches** as productivity:

```python
if target_word == word:  # Exact match
    total_count += 1
elif target_word in word:  # PROBLEM: counts -ain in daiin, kaiin, etc.
    total_count += 1
    compound_count += 1
```

This counts:
- **ain** appearing in: d**ain**, k**ain**, sh**ain**, qok**ain**, ot-**ain**, etc.
- **ol** appearing in: ch**ol**, sh**ol**, qok**ol**, ot-**ol**, **ol**kedy, etc.

But these aren't compounds of "ain" or "ol" as roots—they're words containing -ain or -ol as **suffixes** or words with ol- as a **prefix**.

## Solution: Revised Phase 14B Approach

### Strategy 1: Focus on Complete Words

Instead of searching for substrings, identify **complete words** that:
1. Begin with vowels (a, e, i, o, u, y)
2. Have n ≥ 20 exact matches
3. Exclude already-validated elements
4. Show variation through suffixation (e.g., edy, edyy, edydy)

### Strategy 2: Morphological Boundary Detection

Look for words where vowel-initial element is the **stem**, not a suffix:

**Positive examples** (vowel-initial stems):
- **edy** appears as: edy, edy-y, edy-dy, edy-shey, ot-edy, ol-edy
- **eey** appears as: eey, eey-y, eey-dy, ot-eey
- **ain** (if independent) appears as: ain, ain-y, qok-ain, ot-ain

**Negative examples** (vowel elements as suffixes):
- **ain** in: d-**ain**, k-**ain**, sh-**ain** (suffix position)
- **ol** in: ch-**ol**, sh-**ol**, d-**ol** (suffix position)

### Strategy 3: Use Validated Prefix/Suffix System

We know:
- **Prefixes**: qok-, qot-, {OL} (/ol/ ~ /ot/)
- **Suffixes**: -dy, -y, -al, -ol, -ar, -or, -ain, -iin, -aiin, -edy

Words matching pattern: **[prefix]-STEM-[suffix]** where STEM is vowel-initial

## Revised Phase 14B Plan

### Step 1: Extract True Vowel-Initial Words

Identify complete words (not substrings) that:
- Begin with a, e, i, o, u, y
- n ≥ 20 exact matches  
- Length ≥ 3 characters (filter short suffixes)
- Exclude validated elements

### Step 2: Morphological Variant Detection

For each candidate, identify variants:
- **edy** → check for: edy, edyy, edydy, edyshey, oledy, otedy, qokedy
- Count as productive root if variants exist with known prefixes/suffixes

### Step 3: Apply 10-Point Framework

Score on:
1. **Productivity** (inverted): % appearing with prefixes/suffixes
2. **Standalone Frequency**: % appearing without modifications
3. **Position**: Initial/medial/final distribution  
4. **Section Distribution**: Universal or enriched
5. **Co-occurrence**: With validated elements

### Step 4: Validate Candidates

Threshold: ≥8/10 for validation

## Expected Outcomes (Revised)

### Realistic Estimates

Based on Phase 13 analysis, we expect to find:

**High-confidence candidates** (likely to validate):
- **edy** (162 ot- uses)
- **eey** (72 ot- uses)
- **eedy** (68 ot- uses)

**Medium-confidence**:
- **eeedy** (98 ot- uses) - might be ee-edy compound
- **ol** (54 ot- uses as stem, 5462 total) - need to distinguish stem from prefix
- **ain** (24 ot- uses as stem) - need to distinguish stem from suffix

**Expected validation count**: 3-6 new elements (more realistic than initial 5-10 estimate)

## Next Steps

1. **Revise validation script** to properly detect word boundaries
2. **Run Phase 14B** with corrected methodology
3. **Document findings** in PHASE14B_VALIDATION_RESULTS.md

## Linguistic Insight

This analysis reveals important structure:

**Voynichese morphology is ASYMMETRIC**:
- **Consonant-initial roots** (chol, dar, sho, she, kar, etc.) - MANY validated
- **Vowel-initial roots** (edy, eey, eedy, aiin, or, air) - FEW validated

This asymmetry may be REAL—many languages show C/V asymmetries:
- **Semitic languages**: Roots are exclusively C-initial (triconsonantal)
- **Austronesian languages**: Many roots are V-initial (but suffixes C-initial)
- **Japanese**: Noun roots often C-initial, verb roots often V-initial

The scarcity of vowel-initial independent roots may reflect genuine typological properties of Voynichese, not methodological limitations.

Alternatively, vowel-initial elements may function primarily as **connecting vowels** or **phonological buffer elements** rather than semantic roots—similar to Turkish y/n consonant insertion or Arabic hamza insertion.

---

**Status**: Phase 14A complete, methodology needs revision for Phase 14B
**Key finding**: Most vowel-initial high-frequency elements are bound morphemes (suffixes/prefixes), not independent roots
**Action**: Revise Phase 14B to focus on complete words with proper morphological boundary detection
