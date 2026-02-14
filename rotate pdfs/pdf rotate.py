from pypdf import PdfReader, PdfWriter

# ================================
# INPUT PDF
# ================================

PDF_PATH = "zscores rotated.pdf"   # change to your file name
# Example: PDF_PATH = "zscores rotated.pdf"

# ================================
# LOAD PDF
# ================================

reader = PdfReader(PDF_PATH)

total_pages = len(reader.pages)
print("Total pages found:", total_pages)

# ================================
# ROTATE + SAVE EACH PAGE
# ================================

for i in range(total_pages):

    writer = PdfWriter()

    page = reader.pages[i]

    # Rotate 90 degrees clockwise
    page.rotate(90)

    writer.add_page(page)

    # Output file name
    output_name = f"page_{i+1}_rotated.pdf"

    # Save rotated single-page PDF
    with open(output_name, "wb") as f:
        writer.write(f)

    print("Saved:", output_name)

print("\n✅ All pages rotated and saved separately!")
