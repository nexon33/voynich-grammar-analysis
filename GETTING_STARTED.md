# Getting Started: Voynich-Kempe Hypothesis Research

**Quick start guide for beginning data acquisition and analysis**

---

## Step 1: Understand the Project (10 minutes)

### Read These Documents (in order):

1. **README.md** - Project overview and quick reference
2. **action-plan.md** - Original hypothesis and motivation
3. **docs/methodology.md** - Formal research protocol
4. **docs/data_sources.md** - Comprehensive data guide

### The One-Paragraph Summary:

We're testing whether the Voynich Manuscript (1404-1438) is Middle English women's medical knowledge encoded with an invented alphabet. Both the Voynich and Margery Kempe's Book (1436-1438) were created in the exact same moment—right before witch hunts began—suggesting coordinated preservation of dangerous knowledge. Recent research (Brewer & Lewis 2024) proves encoding gynecological knowledge was common practice. If our hypothesis is correct, statistical patterns and parallel vocabulary will reveal the connection.

---

## Step 2: Set Up Your Environment (15 minutes)

### Install Python Dependencies

```bash
# Make sure you have Python 3.9+ installed
python --version

# Install required packages
pip install -r requirements.txt

# This installs:
# - Data science: numpy, pandas, scipy
# - NLP: nltk, spacy
# - Visualization: matplotlib, seaborn
# - Web scraping: requests, beautifulsoup4
# - Statistics: scikit-learn, statsmodels
```

### Verify Installation

```bash
python -c "import nltk, pandas, scipy, requests; print('✓ All packages installed successfully')"
```

### Optional: Install Git

If you don't have git (needed for CMEPV corpus download):
- **Windows**: https://git-scm.com/download/win
- **Mac**: `brew install git`
- **Linux**: `sudo apt-get install git`

---

## Step 3: Download Data Sources (30-60 minutes)

### Priority 1: Essential Sources (Run Now)

These are free, publicly accessible, and can be downloaded immediately:

```bash
# 1. Voynich EVA Transcription (~2 minutes)
python scripts/data_acquisition/download_voynich.py

# 2. Margery Kempe Middle English Text (~5 minutes)
python scripts/data_acquisition/download_kempe.py --version middle_english

# 3. Middle English Corpus from GitHub (~10 minutes)
python scripts/data_acquisition/download_corpus.py
```

**If any download fails**: See troubleshooting in `docs/data_sources.md`

### Priority 2: Reference Materials (Run Now)

```bash
# Women's Secrets texts (PDFs from Archive.org)
python scripts/data_acquisition/download_references.py --category womens_secrets

# This will also create guides for manual acquisition:
# - Medieval herbals (British Library)
# - Phonology resources
# - Hartlieb 2024 study access instructions
```

### Priority 3: Manual Actions (This Week)

These require forms or purchase but are important:

1. **PPCME2 Corpus** (Required for Phase 1)
   - Read: `data/middle_english_corpus/ppcme2/DOWNLOAD_INSTRUCTIONS.md`
   - Action: Submit user agreement to UPenn
   - Timeline: Usually receive access within 3-5 days

2. **Margery Kempe Modern Translation** (Helpful for understanding)
   - Purchase: Windeatt edition (Penguin Classics, ~$15-20)
   - Or: Check university library
   - See: `data/margery_kempe/modern_translation/README.md`

3. **Hartlieb 2024 Study** (Important context)
   - Access through university library if available
   - Or read free summary: https://theconversation.com/for-600-years-the-voynich-manuscript-has-remained-a-mystery-now-we-think-its-partly-about-sex-227157
   - See: `data/reference_materials/womens_secrets/HARTLIEB_STUDY.md`

---

## Step 4: Verify Your Data (5 minutes)

### Check What You've Downloaded

```bash
# Verify Voynich
python scripts/data_acquisition/download_voynich.py --verify-only --stats

# Verify Kempe
python scripts/data_acquisition/download_kempe.py --verify-only --stats

# Verify Corpus
python scripts/data_acquisition/download_corpus.py --verify-only
```

### Expected Output

You should have:
- ✅ Voynich EVA transcription (~35,000 words)
- ✅ Margery Kempe Middle English text (~58,000 words)
- ✅ CMEPV corpus (~300 texts in SGML format)
- ✅ Secreta Mulierum PDF
- ✅ Trotula PDF
- ✅ Various guide documents created

### If Something Failed

1. Check internet connection
2. Try manual download (URLs in `docs/data_sources.md`)
3. Check error messages in terminal
4. Some sources (British Library, PPCME2) require manual steps—this is expected

---

## Step 5: Explore the Data (30 minutes)

### Quick Look at Voynich EVA

```bash
cd data/voynich/eva_transcription
head -n 20 voynich_eva_complete.txt
```

**What you're seeing**: The Voynich text encoded in Latin characters (EVA = European Voynich Alphabet). Each letter represents a Voynich glyph.

### Quick Look at Margery Kempe

```bash
cd data/margery_kempe/middle_english
head -n 50 book1_part1.txt
```

**What you're seeing**: Actual Middle English from 1436-1438, same time and place as Voynich. Notice the spelling looks strange—that's authentic Middle English orthography.

### Quick Look at CMEPV

```bash
cd data/middle_english_corpus/cmepv/middle_english_text_cmepv
ls sgml/ | head -n 20
```

**What you're seeing**: 300+ Middle English texts in SGML format. We'll filter these by date (1400-1450) for analysis.

---

## Step 6: Understanding the Research Plan

### The Four Phases

We proceed systematically through four phases, with decision points after each:

**Week 1-2: Phase 1 - Frequency Analysis**
- Question: Do Voynich symbols correlate with Middle English sounds?
- Method: Statistical comparison of distributions
- Decision: If correlation exists, proceed; if not, hypothesis rejected

**Week 2-3: Phase 2 - Vocabulary Mapping**
- Question: Does Margery's vocabulary appear in Voynich?
- Method: Extract themes, search for patterns
- Decision: If thematic clustering found, proceed; if random, stop

**Week 3-5: Phase 3 - Alphabet Hypothesis**
- Question: Can we map symbols to sounds and decode coherent text?
- Method: Propose mappings, test on passages, refine
- Decision: If Middle English words emerge, proceed; if gibberish, stop

**Week 5-6: Phase 4 - Content Validation**
- Question: Does decoded text discuss women's medicine?
- Method: Decode sections, validate against historical sources
- Decision: Final assessment of hypothesis

### Key Principle: Falsification First

At each decision point, we ask: "Does the data support continuing?" If not, we stop and report negative results. **Falsification is success in science.**

---

## Step 7: Next Actions (Choose Your Path)

### Option A: Start Analysis Immediately

If you have Voynich + Margery Kempe + CMEPV downloaded:

1. Review `docs/methodology.md` Phase 1 in detail
2. Begin developing frequency analysis scripts
3. Extract Voynich symbol frequencies
4. Research Middle English phonology
5. Plan statistical comparison

### Option B: Complete Data Acquisition First

If waiting for PPCME2 or want all sources:

1. Submit PPCME2 user agreement
2. Purchase/borrow Margery Kempe modern translation
3. Access Hartlieb study through library
4. Download medieval herbals from British Library
5. Wait for access, then begin analysis

### Option C: Literature Review Deep Dive

If you want more context before starting:

1. Read Brewer & Lewis (2024) Hartlieb study
2. Explore *Secreta Mulierum* and *Trotula* PDFs
3. Review Middle English phonology resources
4. Study Voynich statistical properties papers
5. Read Margery Kempe modern translation for content familiarity

### Recommendation: Option A + C in Parallel

- **Day 1-3**: Literature review while data downloads
- **Day 4-7**: Begin Phase 1 frequency analysis
- **Week 2+**: PPCME2 arrives, continue with full dataset

---

## Step 8: Track Your Progress

### Use Git (Recommended)

```bash
# Initialize repository
git init
git add .
git commit -m "Initial project setup"

# Track changes as you work
git add .
git commit -m "Phase 1: Completed frequency analysis"
```

### Document Findings

Create a research journal:
```bash
mkdir journal
touch journal/phase1_notes.md
touch journal/observations.md
touch journal/problems_encountered.md
```

### Update Status

As you progress, update:
- README.md status section
- Methodology.md checkboxes
- Your own notes in journal/

---

## Common Questions

### Q: I'm not a programmer. Can I still contribute?

**Yes!** Non-coding contributions:
- Medieval history expertise
- Middle English linguistics knowledge
- Research assistance (literature review)
- Data validation (checking transcriptions)
- Historical context (women's medical history)

### Q: This seems really complex. Where do I start?

**Start simple**:
1. Read README.md (overview)
2. Read action-plan.md (motivation)
3. Download Voynich + Kempe (easy)
4. Look at the data (text files)
5. Read methodology Phase 1 (first step)

Don't try to understand everything at once. Focus on Phase 1 first.

### Q: What if I find a problem with the methodology?

**Perfect!** That's valuable:
- Open an issue (if using GitHub)
- Document the problem
- Propose alternative approach
- Critical review makes research stronger

### Q: How long until we know if it works?

**Phase 1** (frequency analysis) takes 1-2 weeks. If no correlation, we stop there. If promising, full testing takes 6-8 weeks total.

### Q: What if it doesn't work?

We document the approach, report negative results, and contribute to the field. **Negative results are valuable results.**

---

## Troubleshooting

### Downloads Failing

**Problem**: Script can't download files

**Solutions**:
1. Check internet connection
2. Try manual download (URLs in data_sources.md)
3. Some downloads are large (be patient)
4. Check if antivirus blocking requests

### Python Errors

**Problem**: Import errors or script failures

**Solutions**:
1. Verify Python 3.9+: `python --version`
2. Reinstall packages: `pip install -r requirements.txt`
3. Try: `pip install --upgrade pip`
4. Check specific error messages

### Git Not Found

**Problem**: CMEPV download fails (git not installed)

**Solutions**:
1. Install git (see Step 2)
2. Or download manually: https://github.com/cltk/middle_english_text_cmepv
3. Extract to: `data/middle_english_corpus/cmepv/`

### File Permissions

**Problem**: Can't write to directories

**Solutions**:
1. Check you have write permissions
2. Try running as administrator (Windows)
3. Check disk space

---

## Getting Help

### Resources

1. **Documentation**: Check `docs/` folder first
2. **Data Sources**: See `docs/data_sources.md` for all access info
3. **Methodology**: See `docs/methodology.md` for detailed procedures

### Contact

*(Add contact information, GitHub issues link, or email)*

---

## Ready to Begin!

### Your Checklist:

- [ ] Read README.md
- [ ] Installed Python dependencies
- [ ] Downloaded Voynich EVA transcription
- [ ] Downloaded Margery Kempe Middle English text
- [ ] Downloaded CMEPV corpus
- [ ] Downloaded reference PDFs
- [ ] Submitted PPCME2 user agreement
- [ ] Read methodology.md Phase 1
- [ ] Ready to start frequency analysis!

### Next Step:

**Begin Phase 1: Frequency Analysis**

Read: `docs/methodology.md` → Section "Phase 1: Frequency Analysis"

Then develop:
- `scripts/analysis/voynich_symbol_frequency.py`
- `scripts/analysis/me_phoneme_frequency.py`
- `scripts/analysis/compare_distributions.py`

---

**Good luck! You're testing a hypothesis that could crack a 600-year-old mystery.**

**Or prove it wrong—which is equally valuable to science.**

**Either way: Let's find out what's actually in that manuscript.**

---

*Last Updated: 2025-10-29*  
*Status: Ready for Phase 1*
