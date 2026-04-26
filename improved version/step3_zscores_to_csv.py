"""
STEP 3 — OCR the pink images → extract z-score grid → merge ALL pages HORIZONTALLY.

Structure of each pink page:
    Row 0  : District name  (Colombo, Gampaha, Kandy ...)
    Col 1+ : Z-score values for that district

Each page = one degree program.
Final merged CSV = districts as rows, all degree z-score columns side by side.

Example:
    Page 1 (Degree A)         Page 2 (Degree B)
    Colombo  1.823  1.756     Colombo  2.100  1.990
    Gampaha  1.799  NQC       Gampaha  2.089  2.011

    Merged (horizontal join on district):
    Colombo  1.823  1.756  |  2.100  1.990
    Gampaha  1.799  NQC    |  2.089  2.011
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
PINK_FOLDER = "images/pink"              # output from step 1
OUT_FOLDER  = "output/zscores_per_page"  # individual page CSVs (for traceability)
FINAL_CSV   = "output/zscores_all.csv"  # final horizontally merged CSV
GPU         = True

# ============================================================
# HELPERS — your grid-clustering logic, untouched
# ============================================================

def cx(bbox) -> float:
    return float(sum(p[0] for p in bbox) / 4)

def cy(bbox) -> float:
    return float(sum(p[1] for p in bbox) / 4)

def h(bbox) -> float:
    ys = [p[1] for p in bbox]
    return float(max(ys) - min(ys))

def extract_page_number(filename: str) -> int:
    m = re.search(r"page[_\-\s]?(\d+)", filename.lower())
    return int(m.group(1)) if m else 10 ** 9

def cluster_positions(values: list[float], tol: float) -> list[float]:
    values   = sorted(values)
    clusters = []
    for v in values:
        if not clusters:
            clusters.append([v])
        elif abs(v - np.mean(clusters[-1])) <= tol:
            clusters[-1].append(v)
        else:
            clusters.append([v])
    return [float(np.mean(c)) for c in clusters]

def nearest_index(centers: list[float], v: float) -> int:
    return int(np.argmin(np.abs(np.array(centers, dtype=float) - v)))

def image_to_grid(image_path: str, reader: easyocr.Reader) -> pd.DataFrame | None:
    """
    Run OCR on one pink image and reconstruct the z-score table as a DataFrame.
    Your grid-clustering logic — exactly preserved.
    """
    results = reader.readtext(image_path, detail=1, paragraph=False)

    items = []
    for bbox, text, conf in results:
        text = str(text).strip()
        if not text:
            continue
        items.append({
            "text": text,
            "conf": float(conf),
            "cx":   cx(bbox),
            "cy":   cy(bbox),
            "h":    h(bbox),
        })

    if not items:
        print(f"    ⚠️  No text detected.")
        return None

    heights  = sorted([it["h"] for it in items])
    median_h = heights[len(heights) // 2]
    row_tol  = max(8.0,  0.6 * median_h)
    col_tol  = max(10.0, 0.9 * median_h)

    row_centers = cluster_positions([it["cy"] for it in items], tol=row_tol)
    col_centers = cluster_positions([it["cx"] for it in items], tol=col_tol)

    grid = [["" for _ in range(len(col_centers))] for _ in range(len(row_centers))]

    for it in items:
        r = nearest_index(row_centers, it["cy"])
        c = nearest_index(col_centers, it["cx"])
        if grid[r][c] == "":
            grid[r][c] = it["text"]
        else:
            grid[r][c] = grid[r][c] + " " + it["text"]

    return pd.DataFrame(grid)



# ============================================================
# MAIN
# ============================================================

def main():
    os.makedirs(OUT_FOLDER, exist_ok=True)
    os.makedirs(os.path.dirname(FINAL_CSV), exist_ok=True)

    all_images = sorted(
        glob.glob(os.path.join(PINK_FOLDER, "*.png")) +
        glob.glob(os.path.join(PINK_FOLDER, "*.jpg")),
        key=lambda p: extract_page_number(os.path.basename(p))
    )

    if not all_images:
        print(f"❌  No images found in {PINK_FOLDER}")
        return

    print(f"Found {len(all_images)} pink image(s).")
    print("Initialising EasyOCR reader (once)...")
    reader = easyocr.Reader(["en"], gpu=GPU)

    all_dfs     = []   # raw DataFrames in page order
    saved_pages = 0

    for img_path in all_images:
        page_num = extract_page_number(os.path.basename(img_path))
        print(f"\n--- Page {page_num} : {os.path.basename(img_path)} ---")

        raw_df = image_to_grid(img_path, reader)
        if raw_df is None:
            continue

        # Save raw per-page CSV for traceability
        page_csv = os.path.join(OUT_FOLDER, f"page{page_num}.csv")
        try:
            raw_df.to_csv(page_csv, index=False, header=False, encoding="utf-8-sig")
            print(f"  ✅  Saved: {page_csv}  (rows={raw_df.shape[0]}, cols={raw_df.shape[1]})")
            saved_pages += 1
        except PermissionError:
            print(f"  ❌  Cannot write {page_csv} — close if open in Excel.")
            continue

        all_dfs.append(raw_df)

    if not all_dfs:
        print("\n❌  No data to merge.")
        return

    # ── HORIZONTAL MERGE ─────────────────────────────────────────
    # First file  → keep ALL columns (district col + z-score cols)
    # Other files → skip first 2 columns (district + repeat col), keep z-scores only
    frames = [all_dfs[0]]
    for df in all_dfs[1:]:
        frames.append(df.iloc[:, 2:])   # drop first 2 cols

    merged = pd.concat(frames, axis=1, ignore_index=True)

    try:
        merged.to_csv(FINAL_CSV, index=False, header=False, encoding="utf-8-sig")
        print(f"\n✅  Horizontally merged CSV saved: {FINAL_CSV}")
        print(f"    Pages processed : {saved_pages}")
        print(f"    Total rows      : {merged.shape[0]}")
        print(f"    Total columns   : {merged.shape[1]}")
    except PermissionError:
        print(f"\n❌  Cannot write {FINAL_CSV} — close if open in Excel.")


if __name__ == "__main__":
    main()