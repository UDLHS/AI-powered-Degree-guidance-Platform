"""
STEP 2 — OCR the green images → extract degree–university pairs → save to ONE CSV.

Output CSV structure:
  Column 0 : blank  (placeholder — degree names start after this)
  Column 1 : blank  (placeholder)
  Column 2+: "DEGREE NAME ((UNI CODE))"  — one column per course

All pages are merged into a SINGLE csv so you can verify everything in one place.
Each page gets its own section row so you can trace back which page each column came from.

Keeps your exact logic:
  - ALL CAPS line = degree name
  - line with parentheses = university code
  - state-machine pairing (your most robust version)
"""

import os
import re
import glob
import easyocr
import numpy as np
import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================
GREEN_FOLDER  = "images/green"              # output from step 1
OUT_CSV       = "output/course_names.csv"   # single verification CSV
RAW_LOGS      = "output/raw_logs"           # raw OCR text per page (for debugging)
GPU           = True                        # set False if no GPU

# ============================================================
# HELPERS
# ============================================================

def is_all_caps(text: str) -> bool:
    """True if every alphabetic character in text is uppercase."""
    return any(c.isalpha() for c in text) and all(c.isupper() for c in text if c.isalpha())


def has_letters(text: str) -> bool:
    return any(c.isalpha() for c in text)


def extract_page_number(filename: str) -> int:
    m = re.search(r"page[_\-\s]?(\d+)", filename.lower())
    return int(m.group(1)) if m else 10 ** 9


def pair_degrees_and_universities(lines: list[str]) -> list[tuple[str, str]]:
    """
    State-machine pairing — your most robust version.
    Degree  = all-caps line(s)
    Uni     = lines that follow (not all-caps), may be multi-line
    Returns list of (degree, university) tuples.
    """
    pairs               = []
    current_degree_lines = []
    current_uni_lines    = []
    state                = None   # 'degree' | 'uni' | None

    for line in lines:
        if not has_letters(line):
            # Non-letter token (e.g. "&") — append to whichever block is active
            if state == "degree":
                current_degree_lines.append(line)
            elif state == "uni":
                current_uni_lines.append(line)
            continue

        if is_all_caps(line):
            if state == "uni":
                # Finalise the previous pair before starting a new degree
                degree = " ".join(current_degree_lines).strip()
                uni    = " ".join(current_uni_lines).strip()
                if degree and uni:
                    pairs.append((degree, uni))
                current_degree_lines = [line]
                current_uni_lines    = []
                state                = "degree"
            else:
                current_degree_lines.append(line)
                state = "degree"
        else:
            if state == "degree":
                current_uni_lines.append(line)
                state = "uni"
            elif state == "uni":
                current_uni_lines.append(line)
            # else: orphan uni line before any degree — ignore

    # Finalise last pair
    if state == "uni" and current_degree_lines and current_uni_lines:
        degree = " ".join(current_degree_lines).strip()
        uni    = " ".join(current_uni_lines).strip()
        if degree and uni:
            pairs.append((degree, uni))
    elif state == "degree" and current_degree_lines:
        print(f"    ⚠️  Trailing degree without university: {' '.join(current_degree_lines)}")

    return pairs


# ============================================================
# MAIN
# ============================================================

def main():
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    os.makedirs(RAW_LOGS, exist_ok=True)

    # Collect and sort images by page number
    all_images = sorted(
        glob.glob(os.path.join(GREEN_FOLDER, "*.png")) +
        glob.glob(os.path.join(GREEN_FOLDER, "*.jpg")),
        key=lambda p: extract_page_number(os.path.basename(p))
    )

    if not all_images:
        print(f"❌  No images found in {GREEN_FOLDER}")
        return

    print(f"Found {len(all_images)} green image(s).")
    print("Initialising EasyOCR reader (once)...")
    reader = easyocr.Reader(["en"], gpu=GPU)

    # We'll build one wide DataFrame — all pages merged side by side
    # Structure: [blank, blank, course1, course2, ... | blank, blank, course1, ...]
    # A separator column marks each page boundary so you can see them in the spreadsheet.

    all_columns = []   # column header strings in order
    page_map    = {}   # page_num -> list of column names belonging to that page

    for img_path in all_images:
        page_num = extract_page_number(os.path.basename(img_path))
        print(f"\n--- Page {page_num} : {os.path.basename(img_path)} ---")

        result = reader.readtext(img_path, detail=1, paragraph=False)
        lines  = [entry[1].strip() for entry in result if entry[1].strip()]

        print(f"  Detected {len(lines)} raw text lines.")

        # Save raw log for debugging
        raw_log = os.path.join(RAW_LOGS, f"page{page_num}_raw.txt")
        with open(raw_log, "w", encoding="utf-8") as f:
            for idx, line in enumerate(lines, 1):
                f.write(f"{idx:3d}: {line}\n")

        pairs = pair_degrees_and_universities(lines)
        print(f"  Found {len(pairs)} degree–university pairs.")

        if not pairs:
            print(f"  ⚠️  Skipping page {page_num} — no valid pairs.")
            continue

        # Build column names for this page
        # Two blank placeholders at the start of each page block (your original structure)
        page_cols = [f"_blank_p{page_num}_1", f"_blank_p{page_num}_2"]
        for deg, uni in pairs:
            page_cols.append(f"{deg} ({uni})")

        page_map[page_num] = page_cols
        all_columns.extend(page_cols)

    if not all_columns:
        print("\n❌  No data extracted from any page.")
        return

    # Build a single empty DataFrame — one column per course (for verification)
    # Blank placeholder columns are renamed to spaces so they look empty in Excel/Sheets
    display_cols = []
    for col in all_columns:
        if col.startswith("_blank_"):
            # Each blank gets a unique number of spaces so pandas doesn't deduplicate
            display_cols.append(" " * (all_columns.index(col) + 1))
        else:
            display_cols.append(col)

    df = pd.DataFrame(columns=display_cols)

    try:
        df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
        print(f"\n✅  Saved: {OUT_CSV}")
        print(f"    Total columns: {len(display_cols)} "
              f"({len([c for c in display_cols if c.strip()])} courses + "
              f"{len([c for c in display_cols if not c.strip()])} blank placeholders)")
    except PermissionError:
        print(f"\n❌  Cannot write {OUT_CSV} — close the file if it's open in Excel.")


if __name__ == "__main__":
    main()
