import fitz  # PyMuPDF
import cv2
import numpy as np
import os

# ================================
# SETTINGS
# ================================

PDF_FOLDER = "../pdf rotate"   # folder containing PDFs
OUT_DIR = "uniNcourse"
DPI = 400

os.makedirs(OUT_DIR, exist_ok=True)


# ================================
# FUNCTIONS
# ================================

def render_page_rotated(doc, page_index, dpi=400):
    page = doc.load_page(page_index)
    zoom = dpi / 72.0

    # rotate 90° clockwise
    mat = fitz.Matrix(zoom, zoom).prerotate(90)

    pix = page.get_pixmap(matrix=mat, alpha=False)

    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
        pix.height, pix.width, 3
    )

    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img


def crop_green_region_excluding_header(img_bgr):
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    # Green mask range
    lower = np.array([35, 25, 40])
    upper = np.array([95, 255, 255])

    mask = cv2.inRange(hsv, lower, upper)

    # Clean noise
    kernel = np.ones((7, 7), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Find largest green blob
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not cnts:
        return None

    largest = max(cnts, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)

    green_crop = img_bgr[y:y+h, x:x+w].copy()
    green_mask_crop = mask[y:y+h, x:x+w]

    # Remove header (first green cell)
    row_sum = (green_mask_crop > 0).sum(axis=1)
    row_ratio = row_sum / green_mask_crop.shape[1]

    threshold = 0.25
    start = 0
    for i in range(len(row_ratio)):
        if row_ratio[i] > threshold:
            start = i
            break

    start = min(start + int(0.06 * green_crop.shape[0]),
                green_crop.shape[0] - 1)

    return green_crop[start:, :]


# ================================
# MAIN LOOP FOR ALL PDFs
# ================================

def main():

    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]

    if not pdf_files:
        print("❌ No PDF files found in folder!")
        return

    print("Found PDFs:", pdf_files)

    for pdf_name in pdf_files:

        pdf_path = os.path.join(PDF_FOLDER, pdf_name)
        print("\nProcessing:", pdf_name)

        doc = fitz.open(pdf_path)

        for p in range(doc.page_count):

            img = render_page_rotated(doc, p, dpi=DPI)

            green = crop_green_region_excluding_header(img)

            if green is None:
                print(f"   Page {p+1}: No green found")
                continue

            # Save with PDF name + page number
            out_path = os.path.join(
                OUT_DIR,
                f"{pdf_name[:-4]}_page_{p+1}_green.png"
            )

            cv2.imwrite(out_path, green)
            print("   Saved:", out_path)

        doc.close()

    print("\n✅ Done! All PDFs processed successfully.")


if __name__ == "__main__":
    main()
