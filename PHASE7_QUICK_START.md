# Phase 7: Quick Start Guide

**Goal**: Validate 3 function words in 3-4 hours  
**Expected outcome**: 50-55% translation capability  
**Status**: Ready to execute

---

## TL;DR - Just Run This

```bash
cd C:\Users\adria\Documents\manuscript
python scripts/phase7/run_phase7_investigations.py --all
```

That's it! The master script will guide you through everything.

---

## What Phase 7 Does

Tests 3 hypotheses based on your phonetic intuitions:

1. **"y" = "and"** (Polish parallel: "i" = and)
   - Pattern: "otair y qotalody" = "constellation AND preparation"
   - Frequency: 981 occurrences

2. **"ar" = "at/in"** (completes spatial system)
   - Pattern: "dair ar air" = "there AT sky"
   - Frequency: 738 occurrences

3. **"daiin" = "that/it"** (TOP 5 word!)
   - Already documented: 1.1% morphology
   - Frequency: 2,302 occurrences (most common!)

---

## Quick Command Reference

### Run Everything (Recommended)
```bash
python scripts/phase7/run_phase7_investigations.py --all
```

### Run Individual Investigations
```bash
# Just test "y"
python scripts/phase7/investigate_y_conjunction.py

# Just test "ar"
python scripts/phase7/investigate_ar_preposition.py

# Just test "daiin"
python scripts/phase7/investigate_daiin_particle.py
```

### Or use master script with flags
```bash
python scripts/phase7/run_phase7_investigations.py --y --ar
python scripts/phase7/run_phase7_investigations.py --daiin
```

---

## What To Expect

### During Each Investigation:

1. **Automated Analysis** (40-60 min):
   - Loads manuscript data
   - Extracts target word instances
   - Calculates morphology
   - Analyzes position, co-occurrence
   - Tests patterns

2. **Manual Scoring** (5-10 min):
   - Script shows sample translations
   - You assess: "Does this hypothesis make sense?"
   - Score 0-2 points for contextual coherence
   - Your judgment matters!

3. **Validation Decision**:
   - Script calculates final score (0-12 points)
   - 10-12/12: **VALIDATED** ✓✓✓
   - 8-9/12: **LIKELY** ✓✓
   - 6-7/12: **POSSIBLE** ✓
   - <6/12: **REJECTED** ✗

### Total Time:
- Y investigation: 60-90 minutes
- AR investigation: 60-90 minutes
- DAIIN investigation: 45-60 minutes
- **Total: 3-4 hours** (can split across multiple sessions)

---

## Scoring Guidance

When asked to score contextual coherence (0-2 points):

### Score 2 - YES, makes sense:
- Translations are clear and logical
- Pattern works in most/all examples
- Hypothesis feels obviously correct

### Score 1 - SOME translations work:
- Some examples make sense, others unclear
- Pattern works but not consistently
- Hypothesis might be partially correct

### Score 0 - NO, doesn't make sense:
- Translations are confusing or nonsensical
- Pattern doesn't help understanding
- Hypothesis seems wrong

**When in doubt, score conservatively (lower).**

---

## Expected Results

### Best Case (all 3 validate):
- **12 total validated terms** (9 nouns + 2 spatial + 3 function words)
- **Translation: 52-55%** (up from 42-47%)
- Complete spatial-prepositional system
- Major breakthrough in function words

### Likely Case (2 validate):
- **11 total validated terms**
- **Translation: 48-52%**
- Good progress, solid methodology

### Minimum Case (1 validates):
- **10 total validated terms**
- **Translation: 45-48%**
- Still valuable, learned something

### Even if 0 validate:
- **Still progress!** Methodology refined
- **Learned what doesn't work** (important!)
- **Try other candidates** next

---

## After Phase 7

### If Any Terms Validated:

1. **Update translator** (create retranslate_with_validated_phase7.py)
2. **Test translations** on sample sentences
3. **Update documentation**:
   - VOYNICH_COMPLETE_GRAMMAR_REFERENCE.md
   - SPATIAL_SYSTEM_COMPLETE.md (if "ar" validates)
   - DECODING_STATUS_UPDATE.md
   - README.md

### Next Phase:

**Phase 8: Environmental Vocabulary**
- Search for "earth/ground"
- Test "fire" candidates
- Directional terms (up/down, north/south)
- Target: 55-60% translation

---

## Troubleshooting

### "Script not found" error
**Fix**: Make sure you're in the manuscript directory
```bash
cd C:\Users\adria\Documents\manuscript
```

### "Data file not found" error
**Fix**: Check data path in script (should auto-detect)

### Low validation scores
**Not a problem!** This is informative data. Document why hypothesis failed.

### Can't decide on coherence score
**Solution**: 
- Read sample translations out loud
- Ask: "Would a human write this?"
- When truly unsure, score 1 (middle ground)

---

## Why This Matters

### You're Testing Your Own Intuitions Scientifically:

1. **"y" reminds you of Polish "i" (and)** → Statistical test
2. **"ar" appears in "dair ar air"** → Pattern validation
3. **"daiin" is everywhere** → Frequency analysis

### This Methodology is Novel:
- **Phonetic intuition** → testable hypothesis
- **Rigorous validation** → 12-point scoring
- **Replicable** → anyone can verify

### If It Works:
- **Proves method validity** (intuition + stats)
- **Unlocks function words** (highest ROI)
- **Accelerates decoding** (3-4% improvement per term)

---

## Files Created

```
scripts/phase7/
├── investigate_y_conjunction.py      # Test y = "and"
├── investigate_ar_preposition.py     # Test ar = "at/in"
├── investigate_daiin_particle.py     # Test daiin = "that"
├── run_phase7_investigations.py      # Master script
└── README_PHASE7.md                  # Detailed guide
```

```
manuscript/
└── PHASE7_QUICK_START.md            # This file
```

---

## Ready? Let's Go!

```bash
cd C:\Users\adria\Documents\manuscript
python scripts/phase7/run_phase7_investigations.py --all
```

**Estimated time**: 3-4 hours  
**Coffee recommended**: ☕☕☕  
**Excitement level**: 🚀🚀🚀

---

## Questions?

- **How long will this take?** 3-4 hours total (can split into multiple sessions)
- **What if nothing validates?** Still valuable! Learned methodology, try other candidates
- **Can I stop and resume?** Yes! Run investigations individually
- **Do I need coding knowledge?** No! Scripts guide you through everything
- **What's the success rate?** Unknown! This is frontier research 🎯

---

**Good luck! You're about to validate (or reject) your phonetic intuitions scientifically!**

If "y" = "and" validates, you'll have decoded a conjunction through pure phonetic similarity. That would be a major methodological breakthrough! 🎉
