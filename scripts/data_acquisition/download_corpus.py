#!/usr/bin/env python3
"""
Download Middle English Corpus Materials
Voynich-Kempe Hypothesis Research Project

Downloads publicly available Middle English corpora focusing on 1400-1450 period.
Primary focus: CMEPV (GitHub), PPCME2 (instructions), supporting materials.
"""

import os
import sys
import subprocess
from pathlib import Path
import argparse
import requests
from tqdm import tqdm


class CorpusDownloader:
    """Downloads Middle English corpus materials."""

    def __init__(self, output_dir: str = "data/middle_english_corpus"):
        """Initialize downloader."""
        self.output_dir = Path(output_dir)
        self.cmepv_dir = self.output_dir / "cmepv"
        self.ppcme2_dir = self.output_dir / "ppcme2"
        self.norfolk_dir = self.output_dir / "norfolk_dialect"

        # Create directories
        for directory in [self.cmepv_dir, self.ppcme2_dir, self.norfolk_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def download_cmepv_github(self) -> bool:
        """
        Clone CMEPV corpus from GitHub.

        Returns:
            True if successful
        """
        print("=" * 70)
        print("DOWNLOADING CORPUS OF MIDDLE ENGLISH PROSE AND VERSE")
        print("=" * 70)
        print("\nSource: GitHub - Classical Language Toolkit")
        print("Repository: cltk/middle_english_text_cmepv")
        print("Format: SGML files (~300 texts)")

        repo_url = "https://github.com/cltk/middle_english_text_cmepv.git"
        clone_path = self.cmepv_dir / "middle_english_text_cmepv"

        # Check if already cloned
        if clone_path.exists():
            print(f"\n✓ Repository already exists at: {clone_path}")
            update = input("  Update to latest version? (y/n): ").lower().strip()

            if update == "y":
                try:
                    print("\n  Updating repository...")
                    subprocess.run(
                        ["git", "pull"], cwd=clone_path, check=True, capture_output=True
                    )
                    print("  ✓ Updated successfully")
                    return True
                except subprocess.CalledProcessError as e:
                    print(f"  ✗ Update failed: {e}")
                    return False
            else:
                return True

        # Clone repository
        try:
            print(f"\nCloning from: {repo_url}")
            print(f"To: {self.cmepv_dir}")
            print("\nThis may take several minutes...")

            subprocess.run(["git", "clone", repo_url], cwd=self.cmepv_dir, check=True)

            print(f"\n✓ Successfully cloned CMEPV corpus")
            print(f"  Location: {clone_path}")

            # Count files
            sgml_files = list(clone_path.rglob("*.sgm"))
            print(f"  SGML files: {len(sgml_files)}")

            return True

        except subprocess.CalledProcessError as e:
            print(f"\n✗ Git clone failed: {e}")
            print("\nTroubleshooting:")
            print("  1. Ensure git is installed: git --version")
            print("  2. Check internet connection")
            print("  3. Try manual download from GitHub")
            return False
        except FileNotFoundError:
            print("\n✗ Git not found on system")
            print("\nPlease install Git:")
            print("  Windows: https://git-scm.com/download/win")
            print("  Or download ZIP manually from GitHub")
            return False

    def create_ppcme2_instructions(self) -> None:
        """Create instructions for obtaining PPCME2."""
        readme_file = self.ppcme2_dir / "DOWNLOAD_INSTRUCTIONS.md"

        content = """# Penn-Helsinki Parsed Corpus of Middle English, 2nd Edition (PPCME2)

## Status: Requires User Agreement

PPCME2 is freely available but requires completing a user agreement form.

## How to Obtain

### Step 1: Visit Official Website
Navigate to: https://www.ling.upenn.edu/hist-corpora/

### Step 2: Download Forms
1. Download the **User Agreement** PDF
2. Download the **Order Form** PDF

### Step 3: Complete Forms
- Fill out User Agreement
- Fill out Order Form
- Specify: PPCME2 (Penn-Helsinki Parsed Corpus of Middle English, 2nd edition)
- Include your research project description

### Step 4: Submit
- Follow submission instructions on website
- Email or mail completed forms as directed

### Step 5: Receive Access
- You will receive download instructions via email
- Usually within a few business days
- Download includes CorpusSearch2 tool

## What You Get

- **Size**: 1.2 million words
- **Date Range**: 1150-1500 (focus on 1400-1450 for our research)
- **Format**: Parsed text files with syntactic annotation
- **Tool**: CorpusSearch2 for querying
- **Documentation**: Complete linguistic documentation

## Why We Need PPCME2

For our Voynich-Kempe hypothesis research:

1. **Phonological Analysis**: Extract phoneme frequencies from 1400-1450 texts
2. **Grammatical Patterns**: Identify ME morphological structures
3. **Dialect Features**: Focus on East Midlands/Norfolk texts
4. **Statistical Baseline**: Compare against Voynich symbol distributions

## Key Texts for Our Research (1400-1450)

Once you have PPCME2, prioritize:
- Religious prose from East Anglia
- Medical treatises
- Sermons
- Any Norfolk/East Midlands dialect texts

## Alternative: Use CMEPV While Waiting

While waiting for PPCME2 access:
1. We have CMEPV corpus (already downloaded)
2. Filter CMEPV for 1400-1450 texts
3. Begin initial analysis
4. PPCME2 will provide additional validation

## Installation (After Receiving Files)

1. Extract downloaded ZIP file to this directory
2. Install CorpusSearch2 (included)
3. Test with sample queries
4. See `USAGE_GUIDE.md` for analysis instructions

## Status Tracking

- [ ] Downloaded User Agreement
- [ ] Completed User Agreement
- [ ] Downloaded Order Form
- [ ] Completed Order Form
- [ ] Submitted forms
- [ ] Received download link
- [ ] Downloaded PPCME2
- [ ] Installed CorpusSearch2
- [ ] Verified installation
- [ ] Extracted 1400-1450 texts

## Contact

If you encounter issues:
- Check PPCME2 website for updated instructions
- Contact corpus maintainers (contact info on website)
- Check university library for existing institutional access

---

**Note**: Update this file with your progress and any notes about the process.
"""

        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"\n✓ Created PPCME2 instructions: {readme_file}")

    def create_norfolk_resources(self) -> None:
        """Create guide for Norfolk dialect resources."""
        readme_file = self.norfolk_dir / "RESOURCES.md"

        content = """# Norfolk Dialect Resources (1400-1450)

## Primary Resource: eLALME

**Linguistic Atlas of Late Mediaeval English (electronic)**

- **URL**: http://www.amc.lel.ed.ac.uk/amc-projects-hub/project/elalme/
- **Date Range**: 1325-1450 (PERFECT for our needs)
- **Access**: Free online, some features require registration
- **Focus**: Geographic distribution of dialect features

### How to Use eLALME for Our Research

1. **Access the Atlas**
   - Visit URL above
   - Register if required (free)
   - Explore interactive map

2. **Focus on Norfolk/East Anglia**
   - Locate Norfolk region on map
   - East Midlands dialect area
   - King's Lynn area (where Margery Kempe lived)

3. **Extract Key Features**
   - Phonological markers
   - Lexical variations
   - Morphological patterns
   - Compare to Standard Middle English

4. **Document Findings**
   - Create feature list for Norfolk dialect 1400-1450
   - Note pronunciation differences
   - Identify characteristic vocabulary
   - Map to possible Voynich patterns

## Norfolk Dialect Characteristics

### Known Features (from modern/historical sources)

1. **H-Retention**
   - Unlike most English dialects, Norfolk does NOT drop /h/
   - Initial /h/ consistently pronounced
   - IMPORTANT for phonological analysis

2. **Consonant Cluster Changes**
   - ⟨thr⟩ → /tr/ (three = tree)
   - ⟨shr⟩ → /sr/ (shriek = /sriːk/)
   - May apply to Middle English period

3. **Geographic Context**
   - East Midlands dialect area
   - Distinct from Northern and Southern ME
   - Influenced by Norwich (major urban center)

4. **Margery Kempe's Language**
   - Native Norfolk speaker
   - Dictated in local dialect
   - TEAMS text preserves dialectal features
   - Compare with Standard ME

## Research Tasks

### Task 1: Create Norfolk Feature List
- [ ] Access eLALME
- [ ] Navigate to Norfolk region
- [ ] List phonological features
- [ ] List lexical features
- [ ] Document in `norfolk_features.txt`

### Task 2: Extract from Margery Kempe
- [ ] Identify Norfolk-specific vocabulary in Kempe text
- [ ] Note pronunciation markers
- [ ] Compare with Standard ME equivalents
- [ ] Document in `kempe_dialect_markers.txt`

### Task 3: Create Phoneme Inventory
- [ ] List Norfolk ME consonants
- [ ] List Norfolk ME vowels
- [ ] Note diphthongs
- [ ] Create frequency distribution
- [ ] Compare with Voynich symbol frequencies

## Additional Resources

### Academic Sources

1. **LALME Print Edition**
   - If available at university library
   - More detailed than online version
   - Complete linguistic profiles

2. **Middle English Dialect Studies**
   - Search Google Scholar: "Norfolk Middle English"
   - East Anglia linguistic studies
   - 15th century dialect papers

3. **East Anglian English Studies**
   - Historical phonology papers
   - Dialect geography
   - Medieval language contact

### Online Resources

1. **Middle English Compendium** (University of Michigan)
   - https://quod.lib.umich.edu/m/middle-english-dictionary/
   - Search for Norfolk-attested words
   - Check geographic distribution

2. **Medieval Studies Sites**
   - Luminarium Middle English resources
   - Medieval studies blogs
   - Digital humanities projects

## Integration with Main Research

### How Norfolk Features Connect to Hypothesis

1. **If Voynich is Middle English**:
   - Should show ME phoneme distribution
   - Might show dialect-specific features
   - Norfolk features would suggest English origin

2. **Margery Kempe as Key**:
   - Her Norfolk dialect provides baseline
   - Vocabulary overlap would validate
   - Phonological patterns could decode alphabet

3. **Testing Protocol**:
   - Extract Norfolk phoneme frequencies
   - Compare with Voynich symbol frequencies
   - Look for statistical correlation
   - Test decoding hypotheses

## Data Collection Format

Create structured files:
- `norfolk_phonemes.json` - Phoneme inventory with frequencies
- `norfolk_vocabulary.txt` - Characteristic Norfolk words
- `kempe_dialect_features.txt` - Features in Margery's text
- `comparison_notes.md` - Analysis notes

---

**Status**: Research in progress
**Last Updated**: 2025-10-29
"""

        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✓ Created Norfolk resources guide: {readme_file}")

    def verify_downloads(self) -> dict:
        """Verify what has been downloaded."""
        print("\n" + "=" * 70)
        print("VERIFICATION")
        print("=" * 70)

        results = {}

        # Check CMEPV
        cmepv_repo = self.cmepv_dir / "middle_english_text_cmepv"
        if cmepv_repo.exists():
            sgml_files = list(cmepv_repo.rglob("*.sgm"))
            if len(sgml_files) > 0:
                print(f"✓ CMEPV: OK ({len(sgml_files)} SGML files)")
                results["cmepv"] = True
            else:
                print(f"✗ CMEPV: Directory exists but no SGML files found")
                results["cmepv"] = False
        else:
            print(f"✗ CMEPV: Not downloaded")
            results["cmepv"] = False

        # Check PPCME2 instructions
        ppcme2_readme = self.ppcme2_dir / "DOWNLOAD_INSTRUCTIONS.md"
        if ppcme2_readme.exists():
            print(f"✓ PPCME2 Instructions: Created")
            results["ppcme2_instructions"] = True
        else:
            print(f"✗ PPCME2 Instructions: Missing")
            results["ppcme2_instructions"] = False

        # Check Norfolk resources
        norfolk_readme = self.norfolk_dir / "RESOURCES.md"
        if norfolk_readme.exists():
            print(f"✓ Norfolk Resources Guide: Created")
            results["norfolk_resources"] = True
        else:
            print(f"✗ Norfolk Resources Guide: Missing")
            results["norfolk_resources"] = False

        return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Download Middle English corpus materials",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all available corpora
  python download_corpus.py

  # Only download CMEPV
  python download_corpus.py --cmepv-only

  # Verify existing downloads
  python download_corpus.py --verify-only
        """,
    )

    parser.add_argument(
        "--output-dir",
        default="data/middle_english_corpus",
        help="Output directory for corpus materials",
    )

    parser.add_argument(
        "--cmepv-only", action="store_true", help="Only download CMEPV corpus"
    )

    parser.add_argument(
        "--verify-only", action="store_true", help="Only verify existing downloads"
    )

    args = parser.parse_args()

    # Initialize downloader
    downloader = CorpusDownloader(args.output_dir)

    # Verify only mode
    if args.verify_only:
        downloader.verify_downloads()
        return

    # Download CMEPV
    print("\n" + "=" * 70)
    print("MIDDLE ENGLISH CORPUS ACQUISITION")
    print("=" * 70)

    cmepv_success = downloader.download_cmepv_github()

    # Create instruction files (always)
    if not args.cmepv_only:
        downloader.create_ppcme2_instructions()
        downloader.create_norfolk_resources()

    # Verify
    results = downloader.verify_downloads()

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if cmepv_success:
        print("\n✓ CMEPV corpus downloaded successfully")
        print(f"  Location: {downloader.cmepv_dir / 'middle_english_text_cmepv'}")

    if results.get("ppcme2_instructions"):
        print(f"\n📋 PPCME2 instructions created")
        print(f"  Location: {downloader.ppcme2_dir / 'DOWNLOAD_INSTRUCTIONS.md'}")
        print("  ACTION REQUIRED: Follow instructions to obtain PPCME2")

    if results.get("norfolk_resources"):
        print(f"\n📋 Norfolk resources guide created")
        print(f"  Location: {downloader.norfolk_dir / 'RESOURCES.md'}")

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("\n1. Review downloaded CMEPV corpus")
    print("2. Submit PPCME2 user agreement (see instructions)")
    print("3. Access eLALME for Norfolk dialect data")
    print("4. Download reference materials:")
    print("   python scripts/data_acquisition/download_references.py")
    print("\n5. Begin analysis when all data sources ready")


if __name__ == "__main__":
    main()
