# Phase 7: Function Words & Environmental Vocabulary

**Date**: 2025-10-30  
**Status**: Investigation scripts ready  
**Goal**: Validate 3-4 new function words to push translation capability to 50-55%

---

## Overview

Following Phase 6D's spatial system breakthrough (dair="there", air="sky"), Phase 7 systematically validates high-frequency function words that appear throughout the manuscript.

### Priority Targets:

1. **"y"** (981 occurrences) - Conjunction "and" (Polish parallel hypothesis)
2. **"ar"** (738 occurrences) - Locative preposition "at/in" (completes "dair ar air")
3. **"daiin"** (2,302 occurrences) - Demonstrative "that/which/it" (TOP 5 word!)

---

## Execution Instructions

### Phase 7A: Run Investigation Scripts (3-4 hours total)

#### Task 1: Investigate "y" as Conjunction [60-90 minutes]

```bash
cd C:\Users\adria\Documents\manuscript
python scripts/phase7/investigate_y_conjunction.py
```

**What it does**:
- Analyzes all 981 instances of "y"
- Calculates morphology (expect <5% for conjunctions)
- Tests position patterns (between nouns/phrases?)
- Checks if "y" connects validated terms
- Applies 12-point validation scoring

**Expected result**: Validation score 10+/12 if conjunction

**Key test patterns**:
- "okair y otair" = "oak-constellation AND oat-constellation"
- "tair y qotalody" = "constellation AND oat-preparation"

**Manual input required**: 
- At end, you'll be asked to score contextual coherence (0-2 points)
- Review sample translations and decide if "y" = "and" makes sense

**Estimated runtime**: 60-90 minutes

---

#### Task 2: Investigate "ar" as Preposition [60-90 minutes]

```bash
python scripts/phase7/investigate_ar_preposition.py
```

**What it does**:
- Distinguishes standalone "ar" from "-ar" suffix
- Focuses on "dair ar" pattern
- Tests if "ar" completes spatial formula
- Analyzes astronomical section contexts

**Expected result**: Validation score 9+/12 if preposition

**Key test patterns**:
- "dair ar air" = "there AT sky"
- "dair ar chedar" = "there AT [term]"
- "qotair ar alor" = "constellation AT [place]"

**Manual input required**:
- Contextual coherence scoring (0-2 points)
- Does "dair ar air" = "there at sky" make spatial sense?

**Estimated runtime**: 60-90 minutes

**Note**: If "ar" only exists as suffix (not standalone), validation will fail - this is OK and informative!

---

#### Task 3: Investigate "daiin" [45-60 minutes]

```bash
python scripts/phase7/investigate_daiin_particle.py
```

**What it does**:
- Samples 300 of 2,302 instances for analysis
- Confirms 1.1% morphology (already documented)
- Analyzes position and repetition patterns
- Tests demonstrative/complementizer function

**Expected result**: Validation score 10+/12

**Key patterns**:
- Very high frequency (TOP 5 word!)
- "daiin daiin" repetition (discourse marker?)
- Universal distribution

**Manual input required**:
- Contextual coherence scoring (0-2 points)
- Does "daiin" connect clauses naturally?

**Estimated runtime**: 45-60 minutes

---

## Interpreting Results

### Validation Scoring:

| Score | Status | Action |
|-------|--------|--------|
| 10-12/12 | ✓✓✓ **VALIDATED** | Add to vocabulary, update translator |
| 8-9/12 | ✓✓ **LIKELY** | Probably correct, needs minor confirmation |
| 6-7/12 | ✓ **POSSIBLE** | Tentative, investigate further |
| <6/12 | ✗ **REJECTED** | Hypothesis doesn't fit data |

### Expected Outcomes:

**Best case** (all 3 validate):
- 12 validated terms total (9 nouns + 2 spatial + 3 function words)
- Translation capability: ~52-55%
- Complete spatial-prepositional system
- Major improvement in astronomical section

**Likely case** (2 validate):
- 11 validated terms
- Translation capability: ~48-52%
- Good progress on function words

**Minimum case** (1 validates):
- 10 validated terms
- Translation capability: ~45-48%
- Still progress, methodology refined

---

## Phase 7B: Update Translation Framework

### After running investigations, if any terms validated:

1. **Update retranslate script**:
   - Add validated terms to `translate_word_phase7()` function
   - Test on 10-15 sample sentences
   - Calculate new recognition percentages

2. **Create new translation script**:
```bash
# Create scripts/phase7/retranslate_with_validated_phase7.py
# Template available from phase6/retranslate_with_9_nouns.py
```

3. **Test translations**:
   - Sample from all 4 manuscript sections
   - Check if new terms improve coherence
   - Calculate recognition improvement

---

## Phase 7C: Update Documentation

### Files to update (if terms validated):

1. **VOYNICH_COMPLETE_GRAMMAR_REFERENCE.md**
   - Add validated function words to section 3.5
   - Update examples with new terms
   - Update vocabulary statistics

2. **SPATIAL_SYSTEM_COMPLETE.md** (if "ar" validates)
   - Add prepositional system section
   - Document "dair ar air" = "there at sky"
   - Update constellation labeling examples

3. **DECODING_STATUS_UPDATE.md**
   - Update to 50-55% practical translation (if 3 validate)
   - Add new validated terms
   - Update section-specific coverage

4. **README.md**
   - Update validated vocabulary list
   - Update quick start examples
   - Update coverage statistics

---

## Expected Timeline

### Session 1 (2-3 hours):
- **Hour 1**: Run `investigate_y_conjunction.py`
- **Hour 2**: Run `investigate_ar_preposition.py`
- **Break**: Review results, coffee!
- **Hour 3**: Run `investigate_daiin_particle.py`

### Session 2 (1-2 hours):
- **If validated**: Update translation framework
- **Test**: Re-translate sample sentences
- **Calculate**: New recognition percentages

### Session 3 (30-45 minutes):
- **Update**: Documentation files
- **Commit**: All changes with validation results
- **Prepare**: Phase 7 completion report

**Total estimated time**: 3-4 hours over 1-2 days

---

## Success Criteria

**Phase 7A Complete**:
- ✅ 3 investigation scripts executed
- ✅ Validation scores recorded
- ✅ At least 1 new term validated

**Phase 7B Complete**:
- ✅ Translation framework updated
- ✅ Sample sentences re-translated
- ✅ Recognition improvement quantified

**Phase 7C Complete**:
- ✅ Documentation updated
- ✅ Statistics reflect new vocabulary
- ✅ Examples showcase new terms

**Overall Phase 7 Success**:
- ✅ 10-12+ validated terms total
- ✅ 48-55% practical translation
- ✅ Function word methodology validated
- ✅ Foundation for Phase 8

---

## Troubleshooting

### Issue: Script won't run
**Solution**: Check Python path, ensure you're in manuscript directory

### Issue: Low validation scores
**Analysis**: This is informative! Document why hypothesis failed
**Action**: Revise hypothesis or move to next candidate

### Issue: Can't decide on coherence scoring
**Guidance**: 
- Score 2 if translations obviously make sense
- Score 1 if some work but unclear
- Score 0 if translations are nonsensical
- When in doubt, score conservatively (lower)

### Issue: "ar" only appears as suffix
**Expected**: This is a valid finding!
**Interpretation**: "ar" is directional case marker, not standalone preposition
**Action**: Document result, spatial system still complete without it

---

## Next Steps After Phase 7

### Phase 8: Environmental Vocabulary (2-3 weeks)
- Search for "earth/ground" (complement to "sky")
- Investigate directional terms (up/down, north/south)
- Test "fire" candidates (complete four elements)
- Target: 55-60% translation

### Phase 9: Astronomical Detail (2-3 weeks)
- Complete constellation catalog
- Map to astronomical diagrams
- Celestial mechanics terms
- Target: 60-65% translation

### Publication Track:
- Manuscript draft preparation
- Peer review outreach
- Preprint submission (arXiv)
- Conference abstract

---

## Files Created

### Investigation Scripts:
- `investigate_y_conjunction.py` - Tests y = "and"
- `investigate_ar_preposition.py` - Tests ar = "at/in"
- `investigate_daiin_particle.py` - Tests daiin = "that/it"

### Supporting Files:
- `README_PHASE7.md` - This file (execution guide)

### To Be Created (Phase 7B):
- `retranslate_with_validated_phase7.py` - Updated translator
- `phase7_validation_results.json` - Validation scores
- `PHASE7_COMPLETE.md` - Completion report

---

## Notes

**Methodological Innovation**:
- Testing phonetic intuitions systematically ("y" = Polish "and")
- Distinguishing standalone words from suffixes (critical for "ar")
- Sampling large datasets efficiently (daiin with 2,302 instances)

**Risk Management**:
- Quick validation tests (60-90 min each)
- Low investment if hypothesis fails
- Multiple candidates (don't rely on single term)

**Validation Rigor**:
- 12-point scoring system
- Multiple independent criteria
- Manual coherence check (human judgment important)

---

**Ready to begin? Start with Task 1: `investigate_y_conjunction.py`**

Good luck! 🚀
