# Phase 15: Comprehensive Missed Vocabulary Analysis & Recommendations

## Executive Summary

Systematic extraction of all validation attempts across Phases 10-14 reveals **8 initial missed opportunities**, of which **3 have been resolved** in subsequent phases:

**RESOLVED (3)**:
- ✓ **olkedy** → Reclassified as 9/10 validated compound (ol- + kedy) in Phase 12
- ✓ **cthor** → Reclassified as 7/10 compound (ct- + hor) in Phase 12  
- ✓ **ot-** → Validated as {OL} allomorph /ot/ ~ /ol/ in Phase 13 (χ²=945.29, p<0.001)

**REMAINING OPPORTUNITIES (5)**:
1. **keol** (n=21, 7/10 persistent in Phases 10-11) - HIGH PRIORITY
2. **chod** (n=10, 7/10 in Phase 11) - MEDIUM PRIORITY
3. **shee** (n=17, 7/10 in Phase 11) - MEDIUM PRIORITY
4. **tcho** (n=10, 7/10 in Phase 11) - MEDIUM PRIORITY
5. **ct-** prefix (n=335, 5/10 in Phase 12) - LOW PRIORITY (specialized botanical)

**Recommendation**: Phase 15 should focus on **re-validating keol** with updated 47-element vocabulary context, then investigate the three medium-priority elements (chod, shee, tcho) to determine if they are:
- Independent roots requiring validation
- Bound morphemes requiring different criteria
- Compound forms requiring decomposition

---

## Detailed Analysis of Remaining Opportunities

### HIGH PRIORITY: KEOL (n=21)

**Persistent Near-Validation Pattern**:
- Phase 10: 7/10 (reason: "Near-validated in Phase 10")
- Phase 11: 7/10 (reason: "Persistent near-validated (Phase 10-11)")

**Why This Is High Priority**:
1. **Persistent failure** - Scored 7/10 in TWO separate phases with identical scores
2. **Adequate frequency** (n=21) - Above minimum threshold (n=20)
3. **Consistent performance** - Not borderline fluctuation, but stable 7/10
4. **Context change** - Now have 47 validated elements (was 28-41 in Phases 10-11)

**Hypothesis for 7/10 Score**:
Likely failed on 3 of 5 validation criteria. Possible weaknesses:
- **Productivity**: May show low standalone usage (<70%)
- **Position**: May have borderline position pattern (~65-67% medial)
- **Co-occurrence**: May not significantly co-occur with validated vocabulary

**Recommended Action**:
**Phase 15A: Re-validate keol with updated vocabulary context**

With 47 validated elements (vs. 28-41 in original tests), the co-occurrence criterion may now pass. Create validation script:

```python
# scripts/phase15/revalidate_keol.py
# Test keol against CURRENT 47-element validated vocabulary
# Check if increased vocabulary improves co-occurrence score
```

**Expected Outcome**:
- If keol was borderline on co-occurrence (1/2 points), updated vocabulary may push it to 8/10 ✓
- If keol has fundamental morphological issues (compound form?), it remains 7/10

**Decomposition Hypothesis**:
Could keol be a compound like olkedy was?

Possible structures:
- **ke- + ol**: ke- (unknown) + ol (validated root Phase 14B, n=183)
- **k + eol**: k- (unknown) + eol (unknown)
- **keol** = standalone root (not compound)

**Test**: Check for morphological variants:
- Does `ke` appear independently? (validated in Phase 10, 8/10, n=78) ✓
- Does `eol` appear independently? (no data)
- Does `keol` appear with prefixes? (qok-keol, qot-keol, ol-keol?)
- Does `keol` appear with suffixes? (keol-dy, keol-ain?)

---

### MEDIUM PRIORITY: CHOD (n=10)

**Single Near-Validation**:
- Phase 11: 7/10 (reason: "Persistent near-validated (Phase 10-11)")
  - Note: Label says "persistent" but only appears in Phase 11 results

**Why Medium Priority**:
1. **Low frequency** (n=10) - At minimum threshold for low-frequency adjustment
2. **Single appearance** - Only tested once, not persistent
3. **Possible compound** - May be ch- + od or cho- + d

**Decomposition Analysis**:

| Possible Structure | Component Analysis |
|-------------------|-------------------|
| **ch- + od** | ch- = unknown prefix (high frequency 4120), od = unknown |
| **cho- + d** | cho- = validated root? (need to check Phase 8-10), d = unknown |
| **chod** | Standalone root |

**Cross-Linguistic Parallel Check**:
- Does "chod" show section enrichment? (Biological/pharmaceutical like other ch- roots?)
- Does "chod" combine with validated suffixes? (-dy, -ain, -ol, -ar?)

**Recommended Action**:
**Phase 15B: Investigate chod morphological structure**
1. Check if cho/chol/chom are validated (all are roots from Phase 8-11)
2. Test if chod = cho + -d suffix pattern
3. If standalone root, re-validate with updated vocabulary

---

### MEDIUM PRIORITY: SHEE (n=17)

**Single Near-Validation**:
- Phase 11: 7/10 (reason: "Persistent near-validated (Phase 10-11)")
  - Note: Label says "persistent" but only appears in Phase 11 results

**Why Medium Priority**:
1. **Adequate frequency** (n=17) - Below standard threshold (n=20) but above low-frequency minimum
2. **Single appearance** - Only tested once
3. **SHE- prefix connection** - We have validated "she-" morpheme (water/liquid, Phase 8)

**Critical Question**: Is shee a variant of "she"?

**Validated SHE- morpheme (Phase 8)**:
- Function: Water/liquid marker
- Validated combinations: shedy (she- + -dy verbal), shecthy (she- + cth- + -y)
- Frequency: High productivity across biological/pharmaceutical sections

**Hypothesis**: shee may be:
1. **Phonological variant**: she ~ shee (lengthened vowel in specific contexts?)
2. **Morphological variant**: she + -e suffix pattern
3. **Independent root**: Separate from she- morpheme

**Recommended Action**:
**Phase 15B: Compare shee vs she distribution**

Test questions:
- Do shee and she appear in complementary distribution? (phonological variants)
- Do shee and she co-occur in same contexts? (separate morphemes)
- Does shee show same section distribution as she? (water/liquid semantic)
- Does shee combine with validated suffixes? (shee-dy, shee-ol?)

**Expected Outcome**:
- If shee ~ she are variants → Validate shee as 8/10 allomorph
- If shee ≠ she distribution → Test shee as independent root

---

### MEDIUM PRIORITY: TCHO (n=10)

**Single Near-Validation**:
- Phase 11: 7/10 (reason: "Persistent near-validated (Phase 10-11)")
  - Note: Label says "persistent" but only appears in Phase 11 results

**Why Medium Priority**:
1. **Low frequency** (n=10) - At minimum threshold
2. **Single appearance** - Only tested once
3. **TCH- morpheme connection** - We have multiple tch- combinations validated

**Decomposition Analysis**:

**Validated TCH- containing elements**:
- **tchy** (Phase 9 function word)
- **otchol** (Phase 9, 9/10 compound: ot- + chol)
- **shecthy** (Phase 11, 9/10 compound: she- + cth- + -y)

**Possible structures for tcho**:
1. **tch- + o**: tch- prefix + o suffix/root
2. **t + cho**: t- prefix + cho (validated Phase 8 root) ✓
3. **tcho**: Standalone root

**Critical Check**: Is "cho" validated?
- Need to check Phase 8-10 validation results for "cho" root

**Recommended Action**:
**Phase 15B: Investigate tcho structure**

Test questions:
- Is cho a validated root? (likely yes from Phase 8)
- If tcho = t- + cho, is t- a productive prefix?
- Does tcho appear with validated suffixes? (tcho-dy, tcho-ain?)
- Does tcho show same section distribution as other tch- elements?

**Expected Outcome**:
- If tcho = t- + cho compound → Reclassify as compound (like olkedy)
- If tcho = standalone → Re-validate with updated vocabulary

---

### LOW PRIORITY: CT- PREFIX (n=335, 5/10)

**Phase 12 Performance**:
- Score: 5/10
- Uses: 335
- Unique stems: 67 (needs 100 for highly productive status)
- Validated combinations: 0% (needs >0% for threshold)

**Why Low Priority**:
1. **Specialized function** - 66% herbal section bias (botanical marker)
2. **Limited productivity** - Only 67 unique stems
3. **No validated combinations** - May combine with unvalidated botanical vocabulary

**Phase 12 Interpretation**:
> "ct- appears to be a **specialized prefix** for herbal/botanical contexts, but with limited stem diversity."

**Key Finding**: Top stem **ct-hol** (56 occurrences)
- "chol" is validated Phase 8 botanical root
- Suggests ct- may be variant of "ch-" prefix in botanical contexts

**Hypothesis**: ct- is a **botanical allomorph** of ch-
- **ch-**: General use (4120 occurrences)
- **ct-**: Botanical specialist (335 occurrences, 66% herbal)

**Recommended Action**:
**Phase 15C: Test ct- as CH- botanical allomorph**

Phonological conditioning test:
- Does ct- appear before specific phonological contexts? (vowels? specific consonants?)
- Does ct- vs ch- show complementary distribution in herbal section?
- Statistical test: χ² test for ct- ~ ch- allomorphy in herbal contexts

**Expected Outcome**:
- If ct- ~ ch- are allomorphs → Validate ct- as phonological variant (like ot- ~ ol-)
- If ct- ≠ ch- distribution → Remains specialized botanical prefix (5/10)

---

## Phase 15 Recommended Structure

### Phase 15A: Re-validate keol with Updated Vocabulary (HIGH PRIORITY)

**Objective**: Determine if keol's 7/10 score improves with expanded validated vocabulary context (now 47 elements vs. 28-41 in original tests)

**Method**:
1. Run full 10-point validation on keol with current vocabulary
2. Test morphological decomposition (ke- + ol, keol standalone)
3. Check for prefix/suffix combinations (qok-keol, keol-dy, etc.)

**Success Criterion**: 
- ✓ keol scores 8/10 or higher → Validate as new root
- ✗ keol remains 7/10 → Document persistent failure reason

**Estimated Time**: 2-3 hours (single element focused analysis)

---

### Phase 15B: Investigate Three Medium-Priority Elements (MEDIUM PRIORITY)

**Objective**: Determine morphological status of chod, shee, tcho

**Method**:

1. **CHOD Analysis**:
   - Check if cho/chol are validated (expect yes from Phase 8)
   - Test chod = cho + -d suffix pattern
   - If standalone, re-validate with updated vocabulary

2. **SHEE Analysis**:
   - Compare shee vs she distributional patterns
   - Test for phonological allomorphy (she ~ shee)
   - Check section distribution (expect water/liquid semantic if related)

3. **TCHO Analysis**:
   - Confirm cho is validated root
   - Test tcho = t- + cho compound hypothesis
   - Check for tch- morpheme pattern consistency

**Success Criteria**:
- Identify whether each element is: (a) independent root, (b) compound form, (c) phonological variant
- Validate or reclassify all three elements
- Update COMPLETE_VALIDATED_VOCABULARY.md with findings

**Estimated Time**: 4-6 hours (three elements with morphological analysis)

---

### Phase 15C: Test CT- as CH- Botanical Allomorph (OPTIONAL)

**Objective**: Determine if ct- is a phonologically conditioned allomorph of ch- in botanical contexts

**Method**:
1. Extract all ct- and ch- combinations in herbal section
2. Test for complementary distribution (ct- before X sounds, ch- before Y sounds)
3. Chi-square test for statistical significance of distribution
4. Compare to ot- ~ ol- allomorphy pattern (Phase 13 precedent)

**Success Criterion**:
- χ² test p<0.05 → Validate ct- as ch- botanical allomorph
- No significant pattern → ct- remains specialized prefix (5/10)

**Estimated Time**: 3-4 hours (statistical allomorphy testing)

---

## Predicted Outcomes

### Best Case Scenario:
- **keol**: Re-validates to 8/10 with updated vocabulary → +1 root
- **chod**: Identified as cho + -d pattern, reclassified as compound 8/10 → +1 compound
- **shee**: Validated as she- allomorph 8/10 → +1 variant
- **tcho**: Identified as t- + cho compound 8/10 → +1 compound
- **ct-**: Validated as ch- allomorph with χ²>100, p<0.001 → +1 prefix variant

**Total gain**: 5 validated structures

---

### Most Likely Scenario:
- **keol**: Re-validates to 8/10 → +1 root
- **chod**: Remains 7/10 (insufficient data for compound analysis at n=10) → No change
- **shee**: Validated as she- related variant 8/10 → +1 variant  
- **tcho**: Identified as t- + cho compound 7-8/10 → +1 compound or remain unvalidated
- **ct-**: Insufficient evidence for allomorphy, remains 5/10 → No change

**Total gain**: 2-3 validated structures

---

### Conservative Scenario:
- **keol**: Remains 7/10 (fundamental morphological issue) → Document failure
- **chod**: Insufficient data (n=10) → Defer to future phase
- **shee**: Distributional overlap with she but not clear allomorphy → Remains 7/10
- **tcho**: Insufficient data (n=10) → Defer to future phase
- **ct-**: Remains specialized prefix 5/10 → No change

**Total gain**: 0 validated structures, but complete documentation of persistent near-validated elements

---

## Methodological Improvements

### Lesson 1: Compound Forms Need Separate Validation Track

Phase 12 revealed **olkedy** and **cthor** were compounds, not roots. They scored 7/10 because:
- Low standalone productivity (high compound usage)
- Borderline position patterns (compounds behave differently)

**Improvement**: When element scores 7/10 with low standalone productivity + borderline position:
1. **First check**: Is this a compound form? (prefix + root, root + suffix)
2. **Second**: Apply compound-specific validation criteria
3. **Third**: If compound components are validated, reclassify as compound (not failed root)

### Lesson 2: Allomorphy Can Explain Near-Validated Prefixes

Phase 13 revealed **ot-** (7/10 in Phase 12) was actually an allomorph of **ol-**:
- χ²=945.29, p<0.001
- ot- prefers V-initial stems (80.7%)
- ol- prefers C-initial stems (83.1%)

**Improvement**: When prefix scores 7/10 with high frequency but low validated combinations:
1. **Check**: Does another validated prefix show complementary distribution?
2. **Test**: Chi-square test for phonological conditioning
3. **Result**: May validate as allomorph rather than separate morpheme

### Lesson 3: Vocabulary Growth Changes Validation Context

**keol** scored 7/10 in both Phase 10 and Phase 11 with 28-41 validated elements.

Now with **47 validated elements**, the co-occurrence criterion may change:
- More validated vocabulary = more opportunities for significant co-occurrence
- Element that barely failed co-occurrence (1/2 points) may now pass (2/2 points)

**Improvement**: When persistent near-validated elements exist, **re-validate after major vocabulary expansions** (every 10-15 new elements).

---

## Updated Vocabulary Statistics After Phase 15 (Projected)

### Current Status (End of Phase 14):
- **Total validated vocabulary**: 47 elements
- **By type**: 30 roots (27 C-initial, 3 V-initial), 13 function words, 2 particles, 3 prefixes
- **Validated compounds**: 2 (olkedy, olchedy)

### After Phase 15 (Best Case):
- **Total validated vocabulary**: 52 elements (+5)
- **By type**: 31 roots, 13 function words, 2 particles, 3 prefixes, 1 allomorph variant
- **Validated compounds**: 4 (+2: chod, tcho)
- **Prefix allomorphs**: 2 ({OL} = ol-/ot-, {CH} = ch-/ct-)

### After Phase 15 (Most Likely):
- **Total validated vocabulary**: 49-50 elements (+2-3)
- **By type**: 31 roots, 13 function words, 2 particles, 3 prefixes
- **Validated compounds**: 3-4
- **Documented persistent 7/10**: 2-3 elements (deferred to future phases)

---

## Conclusion

Systematic extraction of validation attempts reveals **Phase 15 has 5 genuine opportunities** (after accounting for 3 resolved cases):

**Immediate Action** (Phase 15A):
- Re-validate **keol** (n=21, persistent 7/10) with updated 47-element vocabulary

**Secondary Investigation** (Phase 15B):
- Analyze morphological structure of **chod, shee, tcho** (all 7/10, n=10-17)
- Determine if compounds, allomorphs, or independent roots

**Optional Advanced** (Phase 15C):
- Test **ct-** as ch- botanical allomorph (following Phase 13 allomorphy precedent)

**Expected Outcome**:
- Best case: +5 validated structures (total 52 elements)
- Most likely: +2-3 validated structures (total 49-50 elements)
- Conservative: +0 but complete documentation of persistent failures

**Methodological Advance**:
- Formalized compound validation criteria
- Established re-validation protocol after vocabulary growth
- Confirmed allomorphy testing as standard procedure for near-validated affixes

With systematic extraction complete, Phase 15 can now proceed with **targeted, high-probability validation attempts** rather than exploratory candidate identification.

---

## Next Steps

**User Decision Point**: Which Phase 15 track to pursue?

**Option A (Recommended)**: Phase 15A only - Re-validate keol (2-3 hours, high probability of success)

**Option B**: Phase 15A + 15B - Add investigation of chod/shee/tcho (6-9 hours total, medium probability)

**Option C**: Full Phase 15A+B+C - Include ct- allomorphy testing (9-13 hours total, comprehensive)

**Option D**: Defer Phase 15 - Move to Phase 16 with different focus (translation testing, cross-scribe validation, semantic analysis)

Awaiting user direction for Phase 15 execution strategy.
