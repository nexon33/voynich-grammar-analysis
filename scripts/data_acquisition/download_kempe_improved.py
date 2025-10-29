#!/usr/bin/env python3
"""
Improved Margery Kempe Download - Extract Actual Middle English Text
Tries multiple sources and better HTML parsing
"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time

output_dir = Path("data/margery_kempe/middle_english")
output_dir.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("DOWNLOADING MARGERY KEMPE - IMPROVED EXTRACTION")
print("=" * 70)

# Try Luminarium first - usually has cleaner excerpts
luminarium_url = "https://www.luminarium.org/medlit/kempebk.htm"

print(f"\nTrying Luminarium source...")
print(f"URL: {luminarium_url}")

try:
    response = requests.get(luminarium_url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    # Find the main content
    # Luminarium usually has text in <p> tags or <blockquote>
    content_blocks = []

    # Look for blockquotes (often contain the ME text)
    for blockquote in soup.find_all("blockquote"):
        text = blockquote.get_text(separator="\n", strip=True)
        if len(text) > 100:  # Only substantial blocks
            content_blocks.append(text)

    # Also check for paragraphs with ME characteristics
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        # Check if it looks like Middle English (has characteristic words)
        if any(
            word in text.lower() for word in ["sche", "hir", "whan", "creatur", "ȝ"]
        ):
            if len(text) > 50:
                content_blocks.append(text)

    if content_blocks:
        output_file = output_dir / "kempe_luminarium_excerpts.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# The Book of Margery Kempe - Excerpts\n")
            f.write("# Source: Luminarium Medieval Literature\n")
            f.write(f"# URL: {luminarium_url}\n\n")
            f.write("=" * 70 + "\n\n")

            for i, block in enumerate(content_blocks, 1):
                f.write(f"\n--- Excerpt {i} ---\n\n")
                f.write(block)
                f.write("\n\n")

        print(f"✓ Downloaded {len(content_blocks)} text blocks")
        print(f"✓ Saved to: {output_file}")
        print(f"  File size: {output_file.stat().st_size:,} bytes")
    else:
        print("✗ No substantial Middle English text found")

except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 70)
print("ALTERNATIVE: MANUAL CORPUS OF MIDDLE ENGLISH")
print("=" * 70)
print("""
Since web scraping is tricky, let's use what we already have!

The CMEPV corpus we downloaded includes LOTS of Middle English texts
from the same period (1400-1450). We can use those for frequency analysis!

Recommended approach:
1. Use CMEPV texts for ME frequency baseline
2. Filter by date (1400-1450)
3. Analyze those for character frequencies
4. Compare with Voynich

This is actually BETTER because:
- More data = more reliable statistics
- Multiple authors = less individual bias
- Verified ME texts from exact period
- Already downloaded and ready!

Let's use what we have!
""")

print("\nNext step: Analyze CMEPV texts for ME character frequencies")
