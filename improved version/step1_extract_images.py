"""
STEP 1 — Extract images from PDF pages.
Saves green region (course names) and pink region (z-scores) as separate PNGs.
Combines: pdf_rotate.py + save_green.py + save_pink.py
"""

import os
import fitz
import cv2
import numpy as np
from pdf2image import convert_from_path

# ============================================================
# CONFIGURATION
# ============================================================
PDF_PATH     = "zscores.pdf"       # your input PDF
OUT_GREEN    = "images/green"      # where green crops are saved
OUT_PINK     = "images/pink"       # where pink crops are saved
DPI          = 400
POPPLER_PATH = None                # Windows: r"poppler-25.11.0\Library\bin"  |  Linux/Mac: None

# ============================================================
# HSV COLOUR RANGES
# ============================================================
GREEN_LOWER  = np.array([35, 25, 40])
GREEN_UPPER  = np.array([95, 255, 255])
PINK_LOWER   = np.array([120, 20, 50])
PINK_UPPER   = np.array([179, 255, 255])
MORPH_KERNEL = np.ones((7, 7), np.uint8)

# ============================================================
# HELPERS
# ============================================================

def render_page_rotated(doc, page_index: int, dpi: int = 400) -> np.ndarray:
    """
    Render a PDF page to BGR numpy array, then rotate 90° clockwise with cv2.
    We render WITHOUT any matrix rotation first (so PyMuPDF doesn't fight with
    the PDF's internal /Rotate flag), then rotate the raw pixels explicitly.
    This matches the behaviour of your original working save_green.py exactly.
    """
    page = doc.load_page(page_index)
    zoom = dpi / 72.0
    mat  = fitz.Matrix(zoom, zoom)          # no prerotate here
    pix  = page.get_pixmap(matrix=mat, alpha=False)
    img  = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    img  = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    # Green region is upside-down — needs 180° rotation
    return cv2.rotate(img, cv2.ROTATE_180)


def crop_largest_colour_region(img_bgr: np.ndarray,
                                lower: np.ndarray,
                                upper: np.ndarray,
                                skip_top_fraction: float = 0.0) -> np.ndarray | None:
    """
    Detect and crop the largest HSV-matched colour region in the image.

    skip_top_fraction: fraction of the found region to skip from the top
                       (set to 0.06 for green to remove the header row).
    Returns cropped BGR image, or None if nothing found.
    """
    hsv  = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, MORPH_KERNEL, iterations=2)

    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return None

    largest = max(cnts, key=cv2.contourArea)
    if cv2.contourArea(largest) < 2000:
        return None

    x, y, w, h = cv2.boundingRect(largest)
    crop        = img_bgr[y : y + h, x : x + w].copy()

    if skip_top_fraction > 0.0:
        crop_mask  = mask[y : y + h, x : x + w]
        row_ratio  = (crop_mask > 0).sum(axis=1) / crop_mask.shape[1]
        header_end = 0
        for idx, ratio in enumerate(row_ratio):
            if ratio > 0.25:
                header_end = idx
                break
        header_end = min(header_end + int(skip_top_fraction * crop.shape[0]), crop.shape[0] - 1)
        crop = crop[header_end:, :]

    return crop


# ============================================================
# MAIN
# ============================================================

def main():
    os.makedirs(OUT_GREEN, exist_ok=True)
    os.makedirs(OUT_PINK,  exist_ok=True)

    print(f"📄  Opening: {PDF_PATH}")
    doc   = fitz.open(PDF_PATH)
    total = doc.page_count
    print(f"    Total pages: {total}\n")

    pdf2img_kwargs = {"dpi": DPI}
    if POPPLER_PATH:
        pdf2img_kwargs["poppler_path"] = POPPLER_PATH

    for p in range(total):
        page_num = p + 1
        print(f"--- Page {page_num}/{total} ---")

        # GREEN — rendered with PyMuPDF (handles rotation internally)
        img_green = render_page_rotated(doc, p, dpi=DPI)
        green     = crop_largest_colour_region(img_green, GREEN_LOWER, GREEN_UPPER,
                                               skip_top_fraction=0.06)
        if green is not None:
            out = os.path.join(OUT_GREEN, f"page_{page_num}_green.png")
            cv2.imwrite(out, green)
            print(f"  [GREEN] ✅ {out}")
        else:
            print(f"  [GREEN] ⚠️  No green region on page {page_num}")

        # PINK — rendered with pdf2image
        # Pink region needs 90° clockwise rotation (confirmed from screenshot).
        pages_img = convert_from_path(PDF_PATH,
                                      first_page=page_num,
                                      last_page=page_num,
                                      **pdf2img_kwargs)
        img_pink = cv2.cvtColor(np.array(pages_img[0]), cv2.COLOR_RGB2BGR)
        img_pink = cv2.rotate(img_pink, cv2.ROTATE_90_CLOCKWISE)
        pink     = crop_largest_colour_region(img_pink, PINK_LOWER, PINK_UPPER)
        if pink is not None:
            out = os.path.join(OUT_PINK, f"page_{page_num}_pink.png")
            cv2.imwrite(out, pink, [cv2.IMWRITE_PNG_COMPRESSION, 0])
            print(f"  [PINK]  ✅ {out}")
        else:
            print(f"  [PINK]  ⚠️  No pink region on page {page_num}")

    doc.close()
    print("\n✅  Step 1 done — all images saved.")


if __name__ == "__main__":
    main()