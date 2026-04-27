import fitz
import os

# ─────────────────────────────────────────
#  CONFIGURATION  ← change these
# ─────────────────────────────────────────
PDF_PATH   = "student_handbook_english.pdf"
OUTPUT_PDF = "zscore_pages.pdf"

# 1-indexed, both edges included  e.g. [3, 7] → pages 3,4,5,6,7
START_PAGE = 175
END_PAGE   = 184


# ─────────────────────────────────────────
def extract_and_rotate(pdf_path, output_path, start, end):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Cannot find: {pdf_path}")

    src = fitz.open(pdf_path)
    total = len(src)
    print(f"PDF has {total} pages total")

    if start < 1 or end > total or start > end:
        raise ValueError(
            f"Invalid range [{start}, {end}]. PDF has {total} pages."
        )

    out = fitz.open()  # new blank PDF

    for page_num in range(start - 1, end):  # fitz is 0-indexed
        out.insert_pdf(src, from_page=page_num, to_page=page_num)

        # Rotate the last inserted page 90° clockwise
        new_page = out[out.page_count - 1]
        current_rotation = new_page.rotation
        new_page.set_rotation((current_rotation + 90) % 360)

        print(f"  ✅ Added page {page_num + 1} (rotated 90° CW)")

    out.save(output_path)
    out.close()
    src.close()

    print(f"\n✅ Done! {end - start + 1} pages saved → {output_path}")
    print(f"   Full path: {os.path.abspath(output_path)}")


# ─────────────────────────────────────────
if __name__ == "__main__":
    extract_and_rotate(PDF_PATH, OUTPUT_PDF, START_PAGE, END_PAGE)
