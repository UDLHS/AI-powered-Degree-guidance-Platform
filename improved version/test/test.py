"""
STEP 4 — Merge degree names + zscores → save CSV + store in PostgreSQL.

Input 1: page1_dnames.csv  → 1 row, 28 columns (degree names)
Input 2: page1_zscores.csv → 25 rows, col 0 = district, col 1-28 = z-scores

Output CSV + PostgreSQL table: zscores_2024
    district     | MEDICINE (University of Colombo) | MEDICINE (University of Peradeniya) | ...
    COLOMBO        2.4516                              2.2279
    GAMPAHA        2.4412                              2.2147
    ...
"""

import re
import os
import pandas as pd
import psycopg2

# ============================================================
# CONFIGURATION
# ============================================================
COURSE_NAMES_CSV = "test/page1_dnames.csv"
ZSCORES_CSV      = "test/page1_zscores.csv"
OUTPUT_CSV       = "output/merged_zscores.csv"
YEAR             = 2024

DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "degree_guidance",
    "user":     "postgres",
    "password": "123456",
}

# ============================================================
# HELPERS
# ============================================================

def get_degrees(csv_path: str) -> list[str]:
    """
    Read degree names from the first row of dnames CSV.
    Cleans double brackets: 'MEDICINE ((University of Colombo))' → 'MEDICINE (University of Colombo)'
    """
    df = pd.read_csv(csv_path, header=None, nrows=1)
    degrees = []
    for col in df.iloc[0]:
        name = str(col).strip()
        name = re.sub(r'\(\(', '(', name)
        name = re.sub(r'\)\)', ')', name)
        degrees.append(name)
    return degrees


def load_zscores(csv_path: str) -> pd.DataFrame:
    """
    Load zscores CSV.
      col 0  = district name
      col 1+ = z-score values
    """
    df        = pd.read_csv(csv_path, header=None, dtype=str)
    districts = df.iloc[:, 0].str.strip().str.upper()
    zdata     = df.iloc[:, 1:].reset_index(drop=True)
    zdata.insert(0, "district", districts.values)
    return zdata


def parse_zscore(val):
    """Return float or None for NQC / missing."""
    v = str(val).strip().upper()
    if v in ("NQC", "NAN", "", "-"):
        return None
    try:
        return float(v)
    except ValueError:
        return None


# ============================================================
# MAIN
# ============================================================

def main():

    # ── 1. Load degree names ──────────────────────────────────
    print("Reading degree names...")
    degrees = get_degrees(COURSE_NAMES_CSV)
    print(f"  {len(degrees)} degrees found.")

    # ── 2. Load z-scores ──────────────────────────────────────
    print("Reading z-scores...")
    zdf     = load_zscores(ZSCORES_CSV)
    n_zcols = zdf.shape[1] - 1
    print(f"  {zdf.shape[0]} districts, {n_zcols} z-score columns.")

    # ── 3. Validate ───────────────────────────────────────────
    if len(degrees) != n_zcols:
        print(f"\n⚠️  MISMATCH — {len(degrees)} degrees vs {n_zcols} z-score columns.")
        return

    # ── 4. Assign degree names as column headers ──────────────
    zdf.columns = ["district"] + degrees
    print(f"\nMerged: {zdf.shape[0]} rows × {zdf.shape[1]} columns")

    # ── 5. Save merged CSV ────────────────────────────────────
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    zdf.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"✅  CSV saved: {OUTPUT_CSV}")

    # ── 6. Store in PostgreSQL ────────────────────────────────
    print("\nConnecting to PostgreSQL...")
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur  = conn.cursor()
        table = f"zscores_{YEAR}"

        # Build and run CREATE TABLE dynamically from degree names
        degree_cols_sql = ",\n    ".join(f'"{d}" NUMERIC(6,4)' for d in degrees)
        cur.execute(f"DROP TABLE IF EXISTS {table};")
        cur.execute(f"""
            CREATE TABLE {table} (
                district  TEXT PRIMARY KEY,
                {degree_cols_sql}
            );
        """)

        # Insert rows
        quoted_cols  = '"district", ' + ', '.join(f'"{d}"' for d in degrees)
        placeholders = ', '.join(['%s'] * (len(degrees) + 1))
        insert_sql   = f'INSERT INTO {table} ({quoted_cols}) VALUES ({placeholders})'

        rows = []
        for _, row in zdf.iterrows():
            values = [row["district"]] + [parse_zscore(row[d]) for d in degrees]
            rows.append(tuple(values))

        cur.executemany(insert_sql, rows)
        conn.commit()
        cur.close()

        print(f"✅  DB done!")
        print(f"    Table   : {table}")
        print(f"    Rows    : {len(rows)} districts")
        print(f"    Columns : {len(degrees)} degrees + district")

    except psycopg2.Error as e:
        print(f"\n❌  Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()