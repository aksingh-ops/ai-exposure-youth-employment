"""
03_build_exposure_categories.py

Builds honest AI-exposure categories for charting, and computes young workers' share of
employment within each category, by year.

Why not a plain 4-way quartile split? ~30% of the matched workforce sits at EXACTLY 0.0
observed exposure (a "zero-inflated" distribution, common in economics for adoption/usage
variables). A plain quartile split would put an arbitrary, tie-broken subset of these
zero-exposure occupations into different buckets. Instead, we treat "no observed AI use"
as its own explicit category, then split the real, non-tied remainder into three groups.

INPUT:  data/step2_merged.csv
OUTPUT: data/step3_categories.csv
        outputs/young_share_by_category_year.csv
"""

import pandas as pd
import os

df = pd.read_csv("data/step2_merged.csv")
df = df.dropna(subset=["exposure_value"])
print(f"Working dataset: {len(df):,} rows")

# ---------------------------------------------------------------------------
# The "two-part" fix for the zero-inflation problem
# ---------------------------------------------------------------------------
zero_mask = df["exposure_value"] == 0
nonzero = df[~zero_mask].sort_values("exposure_value").copy()
nonzero["cum_weight"] = nonzero["WTFINL"].cumsum()
nonzero["weight_pct"] = nonzero["cum_weight"] / nonzero["WTFINL"].sum()
nonzero["exposure_category"] = nonzero["weight_pct"].apply(
    lambda p: "Low (non-zero)" if p <= 1/3 else ("Medium" if p <= 2/3 else "High")
)
df.loc[zero_mask, "exposure_category"] = "No observed AI use"
df.loc[nonzero.index, "exposure_category"] = nonzero["exposure_category"]

print("\nWorkforce share by category (should each be roughly balanced, except the zero group):")
category_pct = (df.groupby("exposure_category")["WTFINL"].sum() / df["WTFINL"].sum() * 100)
print(category_pct.sort_values(ascending=False).to_string())

df.to_csv("data/step3_categories.csv", index=False)

# ---------------------------------------------------------------------------
# Young worker (22-25) share of employment, relative to prime-age (35-54), by category/year
# ---------------------------------------------------------------------------
df["age_group"] = df["AGE"].apply(
    lambda a: "young" if 22 <= a <= 25 else ("prime" if 35 <= a <= 54 else "other")
)
comparison = df[df["age_group"] != "other"].copy()

yearly = comparison.groupby(["exposure_category", "YEAR", "age_group"])["WTFINL"].sum().reset_index()
pivot = yearly.pivot_table(
    index=["exposure_category", "YEAR"], columns="age_group", values="WTFINL", fill_value=0
)
pivot["young_share"] = pivot["young"] / (pivot["young"] + pivot["prime"])
pivot = pivot.reset_index()

os.makedirs("outputs", exist_ok=True)
pivot.to_csv("outputs/young_share_by_category_year.csv", index=False)
print("\nSaved: data/step3_categories.csv")
print("Saved: outputs/young_share_by_category_year.csv")
print("\n" + pivot.to_string(index=False))
