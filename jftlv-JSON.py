import re
import json
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------

INPUT_FILE = "JFTLVraw.txt"
OUTPUT_FILE = "JFTLV.json"

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

# -----------------------------
# LOAD RAW ENTRIES
# -----------------------------

entries = []
current_date = None
current_lines = []

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for raw_line in f:
        line = raw_line.rstrip("\n")

        if not line.strip():
            continue

        m = date_regex.match(line.strip())
        if m:
            if current_date and current_lines:
                entries.append((current_date, current_lines))
            current_date = line.strip()
            current_lines = []
            continue

        if current_date:
            current_lines.append(line)

if current_date and current_lines:
    entries.append((current_date, current_lines))

# -----------------------------
# PARSE ENTRIES
# -----------------------------

structured = []
year = datetime.now().year

def is_quote_start(s):
    return s.startswith("“")

def is_quote_end(s):
    return (
        s.endswith("”") or
        s.endswith("”.") or
        s.endswith(".”") or
        s.endswith("” ") or
        "”" in s  # fallback: contains closing quote anywhere
    )

for date_lv, lines in entries:
    m = date_regex.match(date_lv)
    if not m:
        continue

    day = int(m.group(1))
    month_lv = m.group(2).lower()
    month = lv_months[month_lv]

    date_iso = f"{year:04d}-{month:02d}-{day:02d}"

    # Clean lines
    lines = [l.strip() for l in lines if l.strip()]

    # -----------------------------
    # TITLE
    # -----------------------------
    title = lines[0]

    # -----------------------------
    # QUOTE (multi-line, robust)
    # -----------------------------
    quote_lines = []
    quote_start = None
    quote_end = None

    for i, l in enumerate(lines[1:], start=1):
        if is_quote_start(l) and quote_start is None:
            quote_start = i

        if quote_start is not None:
            quote_lines.append(l)

        if quote_start is not None and is_quote_end(l):
            quote_end = i
            break

    # Fallback: missing closing quote
    if quote_start is not None and quote_end is None:
        quote_end = quote_start
        quote_lines = [lines[quote_start]]

    quote = " ".join(quote_lines)

    # -----------------------------
    # REFERENCE (flexible detection)
    # -----------------------------
    start_after_quote = (quote_end + 1) if quote_end is not None else 1
    ref_idx = None

    # Primary match
    for i in range(start_after_quote, len(lines)):
        if "Bāzes teksts" in lines[i].replace(" ", ""):
            ref_idx = i
            break

    # Relaxed match
    if ref_idx is None:
        for i in range(start_after_quote, len(lines)):
            if "Bāzes" in lines[i] and "tekst" in lines[i]:
                ref_idx = i
                break

    # Fallback
    if ref_idx is None:
        reference = ""
        body_start = start_after_quote
    else:
        reference = lines[ref_idx]
        body_start = ref_idx + 1

    # -----------------------------
    # AFFIRMATION
    # -----------------------------
    aff_idx = None
    for i in range(body_start, len(lines)):
        if lines[i].startswith("Tikai šodien"):
            aff_idx = i
            break

    if aff_idx is None:
        body_lines = lines[body_start:]
        affirmation = ""
    else:
        body_lines = lines[body_start:aff_idx]
        affirmation = " ".join(lines[aff_idx:])

    # -----------------------------
    # BODY
    # -----------------------------
    body = " ".join(body_lines)

    # -----------------------------
    # SAVE ENTRY
    # -----------------------------
    structured.append({
        "date": date_iso,
        "dateLV": date_lv,
        "title": title,
        "quote": quote,
        "reference": reference,
        "body": body,
        "affirmation": affirmation
    })

# -----------------------------
# SAVE JSON
# -----------------------------

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(structured, f, ensure_ascii=False, indent=2)

print(f"Saved {len(structured)} entries to {OUTPUT_FILE}")