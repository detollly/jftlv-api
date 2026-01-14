import re
import json
from datetime import datetime

input_file = "jftlvraw.txt"
output_file = "jftlv.json"

lv_months = {
    "janvāris": 1, "februāris": 2, "marts": 3, "aprīlis": 4,
    "maijs": 5, "jūnijs": 6, "jūlijs": 7, "augusts": 8,
    "septembris": 9, "oktobris": 10, "novembris": 11, "decembris": 12
}

date_regex = re.compile(
    r"^(\d{1,2})\.\s+(janvāris|februāris|marts|aprīlis|maijs|jūnijs|"
    r"jūlijs|augusts|septembris|oktobris|novembris|decembris)$",
    re.IGNORECASE
)

entries = []
current_date = None
current_lines = []

# Read file line by line
with open(input_file, "r", encoding="utf-8") as f:
    for raw_line in f:
        line = raw_line.rstrip("\n")

        # Ignore *completely* empty lines as separators
        if not line.strip():
            continue

        # Detect date line
        m = date_regex.match(line.strip())
        if m:
            # Save previous entry
            if current_date and current_lines:
                entries.append((current_date, current_lines))

            # Start new entry
            current_date = line.strip()
            current_lines = []
            continue

        # Accumulate content lines
        if current_date:
            current_lines.append(line)

# Save last entry
if current_date and current_lines:
    entries.append((current_date, current_lines))

structured = []

year = datetime.now().year

for date_lv, lines in entries:
    m = date_regex.match(date_lv)
    if not m:
        print(f"WARNING: could not parse date line '{date_lv}'")
        continue

    day = int(m.group(1))
    month_lv = m.group(2).lower()
    month = lv_months[month_lv]

    # Validate date
    try:
        date_iso = datetime(year, month, day).strftime("%Y-%m-%d")
    except ValueError:
        print(f"ERROR: Invalid date '{date_lv}' — skipping")
        continue

    # We’ll work with indices instead of fixed positions
    # Clean leading/trailing blank lines just in case
    lines = [l for l in lines if l.strip()]

    if len(lines) < 3:
        print(f"WARNING: Entry for {date_lv} looks too short ({len(lines)} content lines)")
        continue

    # Title and quote are still fairly reliable as first two logical lines
    title = lines[0].strip()
    quote = lines[1].strip()

    # Find reference: first line containing 'Bāzes teksts'
    ref_idx = None
    for i, l in enumerate(lines[2:], start=2):
        if "Bāzes teksts" in l:
            ref_idx = i
            break

    if ref_idx is None:
        print(f"WARNING: No reference ('Bāzes teksts') found for {date_lv}")
        reference = ""
        body_start = 2
    else:
        reference = lines[ref_idx].strip()
        body_start = ref_idx + 1

    # Find affirmation start: first line starting with 'Tikai šodien'
    aff_idx = None
    for i in range(body_start, len(lines)):
        if lines[i].lstrip().startswith("Tikai šodien"):
            aff_idx = i
            break

    # Body: from body_start up to (but not including) aff_idx
    if aff_idx is None:
        body_lines = lines[body_start:]
        affirmation = ""
    else:
        body_lines = lines[body_start:aff_idx]

        # Affirmation may span multiple lines; take all lines from aff_idx to the end
        aff_lines = [lines[aff_idx].strip()]
        # If you want to merge continuation lines into one paragraph, uncomment:
        for cont in lines[aff_idx + 1:]:
            aff_lines.append(cont.strip())
        affirmation = " ".join(aff_lines)

        # If you prefer to preserve line breaks:
        aff_lines.extend(l.strip() for l in lines[aff_idx + 1:])
        affirmation = "\n".join(aff_lines)

    body = "\n".join(l.strip() for l in body_lines)

    structured.append({
        "date": date_iso,
        "dateLV": date_lv,
        "title": title,
        "quote": quote,
        "reference": reference,
        "body": body,
        "affirmation": affirmation,
    })

# Save JSON
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(structured, f, ensure_ascii=False, indent=2)

print(f"Saved {len(structured)} structured entries to {output_file}")