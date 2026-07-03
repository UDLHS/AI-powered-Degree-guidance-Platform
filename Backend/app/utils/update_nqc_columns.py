from sqlalchemy import text
from app.database import engine


def main():
    with engine.begin() as connection:
        connection.execute(text("""
            ALTER TABLE ocr_extracted_rows
            ADD COLUMN IF NOT EXISTS raw_cutoff_mark VARCHAR(50);
        """))

        connection.execute(text("""
            ALTER TABLE ocr_extracted_rows
            ADD COLUMN IF NOT EXISTS cutoff_status VARCHAR(30) DEFAULT 'QUALIFIED';
        """))

        connection.execute(text("""
            ALTER TABLE cutoff_marks
            ADD COLUMN IF NOT EXISTS raw_cutoff_mark VARCHAR(50);
        """))

        connection.execute(text("""
            ALTER TABLE cutoff_marks
            ADD COLUMN IF NOT EXISTS cutoff_status VARCHAR(30) DEFAULT 'QUALIFIED';
        """))

        connection.execute(text("""
            ALTER TABLE cutoff_marks
            ADD COLUMN IF NOT EXISTS is_nqc BOOLEAN DEFAULT FALSE;
        """))

    print("NQC columns added successfully.")


if __name__ == "__main__":
    main()