"""Find astronomical section folios in ZL transcription"""

import re

with open("data/voynich/eva_transcription/ZL3b-n.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

folios = []
for i, line in enumerate(lines):
    if "# astronomical" in line.lower() or "# cosmological" in line.lower():
        # Look ahead for folio marker
        for j in range(i, min(i + 20, len(lines))):
            match = re.match(r"^<(f\d+[rv]\d*)>", lines[j].strip())
            if match:
                folio_id = match.group(1)
                # Check if it has substantial text (not just labels)
                text_lines = 0
                for k in range(j, min(j + 30, len(lines))):
                    if re.match(r"^<f\d+[rv]", lines[k].strip()):
                        if text_lines >= 10:
                            folios.append((folio_id, text_lines))
                        break
                    elif lines[k].strip() and not lines[k].strip().startswith("#"):
                        text_lines += 1
                break

# Print results
print("Astronomical/Cosmological folios with substantial text:")
for folio, line_count in sorted(set(folios))[:10]:
    print(f"{folio}: {line_count} lines")
