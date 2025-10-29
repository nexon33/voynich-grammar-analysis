# Voynich-Kempe Hypothesis Research Project

**Testing whether the Voynich Manuscript contains obfuscated Middle English women's medical knowledge**

---

## Project Overview

This research project systematically tests the hypothesis that the Voynich Manuscript (1404-1438) is Middle English women's medical knowledge encoded using an invented alphabet, with The Book of Margery Kempe (1436-1438) serving as a contemporary parallel text for linguistic decoding.

**Status**: Data acquisition phase
**Timeline**: 6-8 weeks initial testing
**Approach**: Computational linguistics + historical cryptography + digital humanities

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download Data Sources

```bash
# Voynich EVA transcription
python scripts/data_acquisition/download_voynich.py

# Margery Kempe Middle English text
python scripts/data_acquisition/download_kempe.py --version middle_english

# Middle English corpus
python scripts/data_acquisition/download_corpus.py

# Reference materials
python scripts/data_acquisition/download_references.py --category all
```

### 3. Read Documentation

- **Research Background**: See `action-plan.md`, `research.md`, `voynich-kempe-research.md`
- **Data Sources**: See `docs/data_sources.md`
- **Methodology**: See `docs/methodology.md`

### 4. Begin Analysis

Follow the 4-phase testing protocol outlined in `docs/methodology.md`

---

## Repository Structure

```
manuscript/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── action-plan.md                     # Original hypothesis & action plan
├── research.md                        # Oral tradition research
├── voynich-kempe-research.md          # Detailed hypothesis documentation
│
├── data/                              # All data sources (gitignored)
│   ├── voynich/
│   │   ├── eva_transcription/        # Voynich EVA text
│   │   └── images/                   # Manuscript images
│   ├── margery_kempe/
│   │   ├── middle_english/           # ME text from TEAMS
│   │   └── modern_translation/       # Modern translation (user-provided)
│   ├── middle_english_corpus/
│   │   ├── ppcme2/                   # Penn-Helsinki Corpus
│   │   ├── cmepv/                    # Corpus of ME Prose & Verse
│   │   └── norfolk_dialect/          # Dialect resources
│   └── reference_materials/
│       ├── herbals/                  # Medieval herbals
│       ├── womens_secrets/           # Secreta Mulierum, Trotula
│       └── phonology/                # ME phonology resources
│
├── scripts/                          # Analysis scripts
│   ├── data_acquisition/            # Download scripts
│   │   ├── download_voynich.py
│   │   ├── download_kempe.py
│   │   ├── download_corpus.py
│   │   └── download_references.py
│   ├── preprocessing/               # Data cleaning & preparation
│   └── analysis/                    # Core analysis scripts
│
└── docs/                            # Documentation
    ├── data_sources.md              # Complete data source guide
    └── methodology.md               # Formal research protocol
```

---

## The Hypothesis

### Core Claim

The Voynich Manuscript contains Middle English women's medical knowledge (gynecology, herbalism, contraception) obfuscated with an invented alphabet to protect it from persecution. The Book of Margery Kempe, written in the exact same timeframe (1436-1438) in the same dialect region (Norfolk), provides the linguistic key for decoding.

### Why This Could Work

1. **Timeline Convergence**
   - Voynich: 1404-1438 (carbon dating)
   - Margery Kempe: 1436-1438 (written)
   - Malleus Maleficarum: 1487 (witch-hunt manual, 50 years later)
   - **Both created right before systematic persecution began**

2. **Content Overlap**
   - Voynich: Women's health, herbalism, gynecology, astronomy
   - Margery: 14 children, postpartum crisis, healing networks, religious devotion
   - **Same knowledge domains**

3. **Historical Validation**
   - 2024 study (Brewer & Lewis) confirmed Voynich likely contains "women's secrets"
   - Johannes Hartlieb (c. 1410-68) advocated CIPHER for gynecology recipes
   - Decoding of 21-line Italian cipher revealed abortion recipe
   - **This was a documented cultural pattern**

4. **Linguistic Evidence**
   - Voynich statistical properties match natural language
   - Middle English corpus from 1400-1450 exists
   - Norfolk dialect features can be reconstructed
   - **Testable predictions possible**

5. **Obfuscation vs. Encryption**
   - NSA failed because they treated it as mathematical encryption
   - This approach treats it as cultural obfuscation requiring recognition
   - **Different paradigm = different methods**

### Why Previous Approaches Failed

- Assumed Continental European origin (but could be English)
- Assumed male authorship (but could be women's networks)
- Used cryptanalysis (but it's obfuscation, not encryption)
- Ignored cultural context (persecution of women's knowledge)
- No parallel text (we have Margery Kempe)
- **Asked wrong questions**

---

## Research Methodology

### Four-Phase Testing Protocol

#### Phase 1: Frequency Analysis (Weeks 1-2)
**Question**: Do Voynich symbol frequencies correlate with Middle English phoneme frequencies?

**Method**:
- Extract Voynich symbol frequencies from EVA transcription
- Calculate ME phoneme frequencies from 1400-1450 corpus
- Statistical comparison (χ², correlation, K-S tests)

**Success Criteria**: r > 0.6, p < 0.05

---

#### Phase 2: Vocabulary Mapping (Weeks 2-3)
**Question**: Does vocabulary from Margery Kempe appear in appropriate Voynich sections?

**Method**:
- Extract themed vocabulary from Kempe (medical, botanical, anatomical)
- Convert to phonemic representations
- Search Voynich for matching patterns
- Validate against illustrations

**Success Criteria**: >20% vocabulary matches with thematic clustering

---

#### Phase 3: Alphabet Hypothesis (Weeks 3-5)
**Question**: Can we develop a symbol-to-phoneme mapping that produces coherent Middle English?

**Method**:
- Propose initial alphabet based on frequency alignments
- Decode test passages
- Iteratively refine mappings
- Full page decode attempt

**Success Criteria**: >30% decoded words match ME dictionary

---

#### Phase 4: Content Validation (Weeks 5-6)
**Question**: Does decoded content discuss women's medical knowledge as hypothesized?

**Method**:
- Decode botanical, balneological, and astronomical sections
- Compare with medieval medical texts
- Validate historical accuracy
- Check for "women's secrets" content

**Success Criteria**: Semantic coherence + medically accurate + period-appropriate

---

## Key Decision Points

### Decision Point 1 (After Phase 1)
- **Proceed if**: Statistical correlation exists
- **Halt if**: No correlation (distributions incompatible)

### Decision Point 2 (After Phase 2)
- **Proceed if**: Thematic vocabulary clustering is non-random
- **Halt if**: Completely random distribution

### Decision Point 3 (After Phase 3)
- **Proceed if**: Coherent ME words emerge from decoding
- **Halt if**: Only gibberish after systematic attempts

### Final Assessment (After Phase 4)
- **Hypothesis Supported**: Semantic coherence + accurate content
- **Hypothesis Rejected**: Nonsense or contradictory content

---

## Falsification Criteria

This hypothesis is **definitively false** if:

1. Voynich symbol frequencies show NO correlation with ME phoneme frequencies (r < 0.2)
2. Vocabulary matches are at random chance level
3. No alphabet hypothesis produces >10% dictionary matches
4. Decoded text is semantically incoherent
5. Content contradicts medieval medical knowledge

**We will report negative results honestly.** Falsification is valuable scientific output.

---

## Data Sources

### Primary Sources (Free & Open Access)

| Source | Location | Status |
|--------|----------|--------|
| Voynich EVA Transcription | voynich.nu, Archive.org | ✅ Available |
| Margery Kempe Middle English | TEAMS (U. Rochester) | ✅ Available |
| CMEPV Corpus | U. Michigan / GitHub | ✅ Available |
| Secreta Mulierum | Archive.org | ✅ Available |
| Trotula | Archive.org | ✅ Available |
| Medieval Herbals | British Library | ✅ Available |

### Requires User Agreement

| Source | Access Method |
|--------|---------------|
| PPCME2 | Submit form to UPenn |
| eLALME | Free registration |

### Purchase/Library Access

| Source | Notes |
|--------|-------|
| Margery Kempe Modern Translation | Windeatt edition (Penguin) |
| Hartlieb 2024 Study | Journal or interlibrary loan |

**Complete details**: See `docs/data_sources.md`

---

## Technical Requirements

### Software

- **Python 3.9+**
- **R 4.0+** (for statistical validation)
- **Git** (for downloading CMEPV)

### Python Libraries

```
numpy, pandas, scipy          # Data science
nltk, spacy                   # NLP
matplotlib, seaborn, plotly   # Visualization
requests, beautifulsoup4      # Web scraping
lxml, xmltodict              # XML processing
scikit-learn, statsmodels    # Statistics
```

Install all: `pip install -r requirements.txt`

### Hardware

- Minimal requirements (data files ~500MB)
- Any modern computer sufficient
- No GPU needed

---

## Usage Examples

### Download All Data

```bash
# Run all download scripts
python scripts/data_acquisition/download_voynich.py
python scripts/data_acquisition/download_kempe.py --version all
python scripts/data_acquisition/download_corpus.py
python scripts/data_acquisition/download_references.py
```

### Verify Downloads

```bash
python scripts/data_acquisition/download_voynich.py --verify-only --stats
python scripts/data_acquisition/download_kempe.py --verify-only --stats
python scripts/data_acquisition/download_corpus.py --verify-only
```

### Begin Analysis

*(Analysis scripts to be developed in Phases 1-4)*

```bash
# Phase 1
python scripts/analysis/voynich_symbol_frequency.py
python scripts/analysis/me_phoneme_frequency.py
python scripts/analysis/compare_distributions.py

# Phase 2
python scripts/analysis/extract_kempe_vocabulary.py
python scripts/analysis/search_voynich_patterns.py

# Phase 3
python scripts/analysis/propose_alphabet.py
python scripts/analysis/decode_passage.py

# Phase 4
python scripts/analysis/validate_content.py
```

---

## Contributing

### How to Contribute

1. **Code**: Submit pull requests for analysis scripts
2. **Data**: Identify additional relevant sources
3. **Expertise**: Provide feedback on methodology
4. **Review**: Critical analysis of findings

### Areas Needing Expertise

- Medieval English linguistics
- Historical cryptography
- Women's medical history
- Digital humanities methods
- Statistical analysis

### Contact

*(Add contact information or GitHub issues link)*

---

## Ethics & Responsible Research

### Commitments

1. **Transparent Methodology**: All code and data open source (after peer review)
2. **Falsification Focus**: Actively seek disconfirming evidence
3. **Honest Reporting**: Publish negative results if hypothesis fails
4. **Peer Review**: Consult experts before making claims
5. **No Sensationalism**: Avoid hype, acknowledge uncertainty

### Acknowledgments

- Yale Beinecke Library (Voynich Manuscript digitization)
- University of Rochester TEAMS (Margery Kempe edition)
- University of Michigan (CMEPV corpus)
- University of Pennsylvania (PPCME2)
- Classical Language Toolkit (GitHub corpus hosting)
- Brewer & Lewis (2024) for critical historical context

---

## Timeline

### Current Phase: Data Acquisition
- [x] Project structure created
- [x] Documentation written
- [x] Download scripts developed
- [ ] Data sources acquired
- [ ] Initial exploration

### Next Phase: Frequency Analysis
- Weeks 1-2 after data complete
- First decision point

### Projected Completion
- Initial 6-week testing phase
- Extended research if results positive
- Publication timeline depends on findings

---

## Expected Outcomes

### If Hypothesis is Correct
- Voynich decoded (partially or fully)
- Women's medical knowledge recovered
- Historical understanding transformed
- New approach to "unsolvable" texts

### If Hypothesis is Wrong
- Systematic methodology demonstrated
- Middle English hypothesis properly tested
- Negative results documented
- Community learns from approach

**Either way**: Contribution to field

---

## License

### Code
MIT License - Free to use, modify, distribute

### Data
- Voynich Manuscript: Public domain
- Medieval texts: Public domain
- Modern corpora: Respect original licenses
- Our processed data: Open access (after publication)

### Documentation
Creative Commons Attribution 4.0 International (CC BY 4.0)

---

## Citation

If using this methodology or data:

```
[Author Name]. (2025). Voynich-Kempe Hypothesis Research Project: 
Testing Whether the Voynich Manuscript Contains Obfuscated Middle English 
Women's Medical Knowledge. GitHub repository. 
https://github.com/[username]/voynich-kempe-research
```

*(Update with actual publication information if findings are published)*

---

## Frequently Asked Questions

### Q: Has this been tried before?
A: Not with this specific combination of:
- Middle English (most assume Continental European)
- Women's authorship focus
- Margery Kempe as parallel text
- Obfuscation vs. encryption paradigm
- Recent Brewer & Lewis (2024) historical validation

### Q: What if it doesn't work?
A: We document the methodology, report negative results, and contribute to scientific understanding. Falsification is valuable.

### Q: Isn't this just pattern matching on noise?
A: That's why we use rigorous statistical testing, falsification criteria, and decision points. If it's noise, the statistics will show it.

### Q: Why would women encode knowledge?
A: The 2024 Brewer & Lewis study proves this was common practice. Johannes Hartlieb explicitly recommended it. Decoded period ciphers show gynecological content. This isn't speculative—it's documented historical practice.

### Q: How long until you know if it works?
A: Phase 1 takes 1-2 weeks. If correlations fail, we stop. If promising, full testing takes 6-8 weeks.

### Q: Can I help?
A: Yes! See Contributing section. Expertise in medieval studies, linguistics, or statistics especially valuable.

---

## Status Updates

### 2025-10-29: Project Initialized
- Repository structure created
- Documentation completed
- Download scripts developed
- Ready for data acquisition phase

### Next Update
Will be posted after Phase 1 completion (Frequency Analysis)

---

## Final Thought

> *"Maybe the imperfection IS the point?"*

Sometimes breakthroughs come not from more expertise, but from **asking a different question**.

This research asks:
- What if it's English, not Latin?
- What if women wrote it, not men?
- What if it's obfuscation, not encryption?
- What if the timeline is the key?

**Let's find out.**

---

**Documentation Version**: 1.0  
**Last Updated**: 2025-10-29  
**Status**: Ready for execution  
**Contact**: *(Add contact info)*
