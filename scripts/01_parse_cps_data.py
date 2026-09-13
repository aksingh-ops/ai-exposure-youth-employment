"""
01_parse_cps_data.py

Parses the raw IPUMS CPS fixed-width microdata extract into a clean CSV.

INPUT:  data/cps_00001.dat   (see data/README.md for how to obtain this)
OUTPUT: data/step1_cps_clean.csv
"""

import pandas as pd
import os

DAT_FILE = "data/cps_00001.dat"
assert os.path.exists(DAT_FILE), (
    f"{DAT_FILE} not found. See data/README.md for how to generate and download this file "
    "from IPUMS CPS - it is not included in this repo due to size and license terms."
)

# Column positions taken directly from the official IPUMS DDI codebook that accompanies
# every extract. These are NOT guessed - IPUMS provides an exact per-variable start/end
# position for fixed-width files, documented in the extract's own DDI/XML codebook.
IPUMS_COLUMN_POSITIONS_1INDEXED = {
    "YEAR":    (1, 4),     # survey year
    "MONTH":   (10, 11),   # survey month
    "WTFINL":  (50, 63),   # final person weight (4 implied decimals - see fix below)
    "AGE":     (104, 105), # age at last birthday (top-coded at 85 for privacy)
    "EMPSTAT": (106, 107), # employment status code
    "OCC":     (108, 111), # 4-digit Census occupation code
}

colspecs = [(start - 1, end) for start, end in IPUMS_COLUMN_POSITIONS_1INDEXED.values()]
names = list(IPUMS_COLUMN_POSITIONS_1INDEXED.keys())

print(f"Reading {DAT_FILE} in chunks...")
chunks = []
for i, chunk in enumerate(pd.read_fwf(DAT_FILE, colspecs=colspecs, names=names, chunksize=500_000)):
    chunks.append(chunk)
    print(f"  chunk {i+1}: {len(chunk):,} rows")

df = pd.concat(chunks, ignore_index=True)

# IPUMS stores WTFINL with 4 implied decimal places (no literal decimal point in the raw
# file) - this division is required, not optional, or every weighted statistic is wrong
# by a factor of 10,000.
df["WTFINL"] = df["WTFINL"] / 10_000

print(f"\nTotal rows loaded: {len(df):,}")
print(f"YEAR range: {df['YEAR'].min()}-{df['YEAR'].max()}")
print(f"AGE range: {df['AGE'].min()}-{df['AGE'].max()}  (top-coded at 85, documented CPS behavior)")

# Data-quality notes, documented rather than silently handled:
#   - AGE tops out at 85: the Census Bureau top-codes age for privacy. This is expected.
#   - ~9.8% of rows have a missing WTFINL, concentrated entirely in March: these are ASEC
#     supplement households, which are not part of the basic monthly sample and correctly
#     have no basic monthly weight. They are excluded downstream, not treated as an error.

os.makedirs("data", exist_ok=True)
df.to_csv("data/step1_cps_clean.csv", index=False)
print("\nSaved: data/step1_cps_clean.csv")
