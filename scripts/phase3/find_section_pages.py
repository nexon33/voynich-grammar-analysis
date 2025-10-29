#!/usr/bin/env python3
"""
Find which manuscript pages correspond to high-density medical sections.
"""

from pathlib import Path


def find_pages_for_sections():
    """Map sections to their manuscript pages/folios."""

    # Read the Voynich text
    text_path = Path(__file__).parent.parent.parent / "data" / "voynich_text_clean.txt"

    with open(text_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Track sections and pages
    word_count = 0
    current_page = "Unknown"
    section_pages = {}

    # High density sections to find (from analysis)
    target_sections = {
        4: (2000, 2500),
        24: (12000, 12500),
        51: (25500, 26000),
        55: (27500, 28000),
        60: (30000, 30500),
        72: (36000, 36500),
    }

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Page/folio marker
        if line.startswith("<"):
            current_page = line.strip("<>")
            continue

        # Skip comments
        if line.startswith("#"):
            continue

        # Count words in this line
        words = line.split()
        line_start = word_count
        word_count += len(words)
        line_end = word_count

        # Check if this line overlaps with any target section
        for section_id, (sect_start, sect_end) in target_sections.items():
            if line_end >= sect_start and line_start < sect_end:
                if section_id not in section_pages:
                    section_pages[section_id] = {
                        "pages": set(),
                        "first_line": line,
                        "word_range": (sect_start, sect_end),
                    }
                section_pages[section_id]["pages"].add(current_page)

    return section_pages


def main():
    print("Finding manuscript pages for high-density medical sections...")
    print("=" * 80)
    print()

    section_pages = find_pages_for_sections()

    # Display results
    for section_id in sorted(section_pages.keys()):
        info = section_pages[section_id]
        pages = sorted(info["pages"])

        print(
            f"Section {section_id} (Words {info['word_range'][0]}-{info['word_range'][1]})"
        )
        print(f"Pages/Folios: {', '.join(pages)}")
        print(f"First line: {info['first_line'][:80]}...")
        print()
        print("-" * 80)
        print()


if __name__ == "__main__":
    main()
