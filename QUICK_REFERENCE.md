# Quick Reference Card

**Keep this handy while working**

---

## The Hypothesis in One Sentence

The Voynich Manuscript (1404-1438) is Middle English women's medical knowledge obfuscated with an invented alphabet, decodable using Margery Kempe's Book (1436-1438) as a parallel linguistic corpus.

---

## Your Data Locations

```
Voynich:        data/voynich/eva_transcription/voynich_eva_takahashi.txt
Kempe:          data/margery_kempe/middle_english/complete_text.txt
ME Corpus:      data/middle_english_corpus/cmepv/middle_english_text_cmepv/sgml/
References:     data/reference_materials/
```

---

## Key Documents

| Document | When to Use |
|----------|-------------|
| `README.md` | Overview, quick reference |
| `GETTING_STARTED.md` | First-time setup |
| `DEEP_DIVE_GUIDE.md` | Before starting analysis |
| `DATA_ACQUISITION_STATUS.md` | Check what data you have |
| `docs/methodology.md` | Detailed research protocol |
| `docs/data_sources.md` | Finding additional resources |

---

## The 4 Phases

**Phase 1** (Weeks 1-2): Frequency Analysis
- Test: Do Voynich symbols correlate with ME phonemes?
- Success: r > 0.6, p < 0.05
- Failure: No correlation → Stop

**Phase 2** (Weeks 2-3): Vocabulary Mapping  
- Test: Does Kempe vocabulary appear in Voynich?
- Success: >20% thematic clustering
- Failure: Random distribution → Stop

**Phase 3** (Weeks 3-5): Alphabet Hypothesis
- Test: Can we decode coherent Middle English?
- Success: >30% dictionary matches
- Failure: Only gibberish → Stop

**Phase 4** (Weeks 5-6): Content Validation
- Test: Does decoded text discuss women's medicine?
- Success: Semantic coherence + accurate content
- Failure: Nonsense or wrong content → Hypothesis rejected

---

## Statistical Tests Cheat Sheet

**Chi-Square Test**:
```python
from scipy.stats import chisquare
statistic, pvalue = chisquare(observed, expected)
# If p < 0.05: distributions are different
# If p > 0.05: distributions are similar (what we want!)
```

**Pearson Correlation**:
```python
from scipy.stats import pearsonr
r, pvalue = pearsonr(x, y)
# r > 0.6: strong positive correlation (what we want!)
# p < 0.05: correlation is significant
```

**Spearman Correlation**:
```python
from scipy.stats import spearmanr
rho, pvalue = spearmanr(x, y)
# Same interpretation as Pearson
# Better for non-normal distributions
```

---

## Decision Criteria

**Proceed to next phase if**:
- Statistical tests pass thresholds
- At least 2 independent tests support hypothesis
- Results are replicable
- No major red flags

**Stop research if**:
- All statistical tests fail
- Results clearly contradict hypothesis
- No path forward visible
- More harm than good to continue

**Seek expert input if**:
- Results are ambiguous
- Unexpected patterns emerge
- Need validation before proceeding
- Stuck on technical issue

---

## Common Commands

**View data**:
```bash
head -n 50 data/voynich/eva_transcription/voynich_eva_takahashi.txt
head -n 50 data/margery_kempe/middle_english/complete_text.txt
ls data/middle_english_corpus/cmepv/middle_english_text_cmepv/sgml/
```

**Run scripts**:
```bash
python scripts/exploration/explore_voynich.py
python scripts/analysis/voynich_symbol_frequency.py
python scripts/analysis/me_phoneme_frequency.py
python scripts/analysis/compare_distributions.py
```

**Check environment**:
```bash
python --version
pip list | grep -E "nltk|pandas|scipy|matplotlib"
```

---

## EVA Alphabet Reference

**Common Characters**:
```
a, o, e, i, y    - "Vowels"
d, l, r, s, t    - Common "consonants"  
k, f, p          - Less common
ch, sh           - Digraphs (two characters, one sound?)
8, 9             - "Gallows" (rare, significant)
```

**Frequency Order** (approximate):
`o > a > y > d > l > e > s > r > ...`

---

## Middle English Quick Guide

**Common Spelling Variations**:
```
ME              Modern
sche, scho      she
chylde          child
tyme            time
goode           good
whan            when
thei            they
```

**Pronunciation Notes**:
- `gh` was pronounced: "knight" = /kniçt/
- Final `-e` sometimes silent by 1400
- Long vowels before Great Vowel Shift
- `y` often = /i/ sound

---

## Troubleshooting

**Import errors**:
```bash
pip install --upgrade nltk pandas scipy matplotlib seaborn
```

**File not found**:
- Check you're in manuscript/ directory
- Use absolute paths if needed
- Verify file actually downloaded

**Git clone failed (CMEPV)**:
- Files are there despite warning
- Check: `ls data/middle_english_corpus/cmepv/middle_english_text_cmepv/sgml/`
- Should see ~127 files

**Can't download PDFs**:
- Use browser to manually download from Archive.org
- Not critical for Phase 1

---

## Journal Files to Maintain

Create and update regularly:
```
journal/daily_log.md              - What you did each day
journal/voynich_observations.md   - Patterns you notice
journal/analysis_notes.md         - Technical notes
journal/questions.md              - Things you're unsure about
journal/results.md                - Findings as you go
```

---

## Getting Unstuck

**If confused about hypothesis**:
- Re-read: `README.md`, `action-plan.md`
- Review timeline convergence
- Remember: Obfuscation, not encryption

**If confused about methodology**:
- Read relevant phase in `docs/methodology.md`
- Check decision criteria
- Review statistical tests

**If stuck on code**:
- Check Python documentation
- Search Stack Overflow
- Start simpler, build up
- Ask for help

**If overwhelmed**:
- Take a break
- Focus on one small task
- Review quick wins
- Remember: Process matters more than outcome

---

## Success Looks Like

**Short-term** (this week):
- Voynich frequencies calculated ✓
- ME phonology researched ✓
- First scripts written ✓
- Data visualized ✓

**Medium-term** (Phase 1 complete):
- Statistical tests run ✓
- Decision made (proceed or stop) ✓
- Results documented ✓
- Learning achieved ✓

**Long-term** (project complete):
- Hypothesis tested rigorously ✓
- Results published (positive or negative) ✓
- Skills developed ✓
- Contribution to field ✓

---

## Remember

✓ Negative results are valuable  
✓ Process matters more than outcome  
✓ Rigor beats wishful thinking  
✓ Document everything  
✓ Take breaks  
✓ Ask for help  
✓ Enjoy the journey  

---

**You're doing real science. Stay curious, stay rigorous, stay honest.**

---

*Quick Reference v1.0*
*Last updated: 2025-10-29*
