from pdf2image import convert_from_path
import cv2
import numpy as np
import os

# ===== CONFIGURATION =====
PDF_FOLDER = r"../pdf rotate"               # folder containing input PDFs
POPPLER_PATH = r"poppler-25.11.0\Library\bin"  # path to poppler binaries
OUTPUT_FOLDER = r"districtNunicode"          # folder for cropped images
DPI = 500                                    # high DPI = better OCR/detail
PADDING = 0                                   # set to 0 to crop exactly the pink region

# Pink color range in HSV (tune these if needed)
LOWER_PINK = np.array([120, 20, 50])
UPPER_PINK = np.array([179, 255, 255])

# Morphological kernel for cleaning the mask
KERNEL = np.ones((7, 7), np.uint8)
# =========================

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def crop_pink_region(img_bgr):
    """
    Detect the largest pink region in the image and return a tight crop.
    Returns None if no suitable pink area is found.
    """
    # Convert to HSV and create mask
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_PINK, UPPER_PINK)

    # Clean the mask: close small gaps and remove noise
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, KERNEL, iterations=2)

    # Find all pink contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    # Keep the largest contour (assumed to be the target pink region)
    largest = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest) < 2000:   # ignore very small blobs
        return None

    # Get bounding box of the largest pink area
    x, y, w, h = cv2.boundingRect(largest)

    # Apply padding (if any) while staying inside image boundaries
    if PADDING > 0:
        x = max(0, x - PADDING)
        y = max(0, y - PADDING)
        w = min(img_bgr.shape[1] - x, w + 2 * PADDING)
        h = min(img_bgr.shape[0] - y, h + 2 * PADDING)

    # Crop and return
    return img_bgr[y:y+h, x:x+w].copy()

def main():
    # Find all PDF files in the input folder
    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print("❌ No PDF files found in", PDF_FOLDER)
        return

    for pdf_name in pdf_files:
        pdf_path = os.path.join(PDF_FOLDER, pdf_name)
        base_name = os.path.splitext(pdf_name)[0]
        print(f"\nProcessing: {pdf_name}")

        # Convert first page of PDF to image (pdf2image respects /Rotate)
        pages = convert_from_path(pdf_path, dpi=DPI, poppler_path=POPPLER_PATH)
        img = cv2.cvtColor(np.array(pages[0]), cv2.COLOR_RGB2BGR)

        # Crop the pink region
        cropped = crop_pink_region(img)
        if cropped is None:
            print("❌ Pink region not found or too small.")
            continue

        # Save as high‑quality PNG (no compression)
        out_path = os.path.join(OUTPUT_FOLDER, f"{base_name}_pink.png")
        cv2.imwrite(out_path, cropped, [cv2.IMWRITE_PNG_COMPRESSION, 0])
        print(f"✅ Saved: {out_path}")

    print("\n🎉 All done. Pink crops saved (no rotation applied).")

if __name__ == "__main__":
    main()