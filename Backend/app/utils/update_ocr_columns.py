from sqlalchemy import text
from app.database import engine


def main():
    with engine.begin() as connection:
        connection.execute(text("""
            ALTER TABLE ocr_extracted_rows
            ADD COLUMN IF NOT EXISTS confidence_score DOUBLE PRECISION DEFAULT 0;
        """))

        connection.execute(text("""
            ALTER TABLE ocr_extracted_rows
            ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'PENDING';
        """))

        connection.execute(text("""
            ALTER TABLE ocr_extracted_rows
            ADD COLUMN IF NOT EXISTS admin_note TEXT;
        """))

    print("OCR extracted row columns updated successfully.")


if __name__ == "__main__":
    main()