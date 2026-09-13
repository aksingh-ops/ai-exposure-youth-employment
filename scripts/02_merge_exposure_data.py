"""
02_merge_exposure_data.py

Cleans the Census OCC-to-SOC crosswalk, matches each occupation to a real AI exposure
score from the Anthropic Economic Index, and merges the result onto the cleaned CPS data.

INPUTS:
  data/step1_cps_clean.csv                          (output of 01_parse_cps_data.py)
  data/job_exposure.csv                             (Anthropic Economic Index)
  data/2018-occupation-code-list-and-crosswalk.xlsx (Census Bureau crosswalk)
OUTPUT:
  data/step2_merged.csv
"""

import pandas as pd

# ---------------------------------------------------------------------------
# Clean the Census OCC -> SOC crosswalk
# ---------------------------------------------------------------------------
xl = pd.ExcelFile("data/2018-occupation-code-list-and-crosswalk.xlsx")
crosswalk_raw = xl.parse("2018 Census Occ Code List", header=4)
crosswalk_raw.columns = ["category_header", "title", "census_code", "soc_code"]

# Drop section-header rows (blank codes) and SOC-range rows (e.g. "11-0000 - 29-0000"),
# which are aggregate category labels, not real individual occupation codes.
crosswalk = crosswalk_raw.dropna(subset=["census_code", "soc_code"]).copy()
crosswalk["census_code"] = crosswalk["census_code"].astype(str).str.strip()
crosswalk = crosswalk[crosswalk["census_code"].str.len() == 4]
crosswalk = crosswalk[~crosswalk["soc_code"].str.contains(" - ", na=False)]

# CRITICAL FIX: the crosswalk stores codes as text with a leading zero ("0010"), but our
# parsed CPS data reads OCC as a plain integer (10). Without this conversion, the join
# below silently returns zero matches - not an error, just an empty result.
crosswalk["OCC"] = crosswalk["census_code"].astype(int)
crosswalk["soc_code"] = crosswalk["soc_code"].str.strip()

print(f"Clean crosswalk: {len(crosswalk)} real occupation codes")

# ---------------------------------------------------------------------------
# Load the Anthropic Economic Index job exposure data
# ---------------------------------------------------------------------------
exposure = pd.read_csv("data/job_exposure.csv")
exposure.columns = ["SOC", "title", "observed_exposure"]
exposure["SOC"] = exposure["SOC"].str.strip()
print(f"Job exposure data: {len(exposure)} occupations")


def get_exposure(soc_code, exposure_df):
    """
    Match a crosswalk SOC code to an exposure score.

    Some Census codes map to a BROAD or COMBINED SOC group rather than one specific
    detailed occupation (e.g. "53-3030" or "37-201X" - the Census Bureau does this to
    protect respondent confidentiality when a detailed breakdown would be too small a
    sample). Anthropic's dataset only scores DETAILED occupations.

    Per the official BLS SOC coding structure, a broad code's detailed "children" always
    share the same leading digits with a non-zero final digit - so we average the
    detailed occupations that roll up under a broad/combined code. This is a documented
    modeling choice, not a silent guess, and it is disclosed in every output row via the
    match_type and n_children_averaged columns.
    """
    if soc_code == "none":
        return None, "not_an_occupation", 0
    exact = exposure_df[exposure_df["SOC"] == soc_code]
    if len(exact):
        return exact.iloc[0]["observed_exposure"], "exact", 1
    prefix = soc_code.rstrip("0X").rstrip("-")
    if len(prefix) < 3:  # too short a prefix to trust - would risk false matches
        return None, "no_match", 0
    children = exposure_df[exposure_df["SOC"].str.startswith(prefix)]
    if len(children):
        return children["observed_exposure"].mean(), "aggregated", len(children)
    return None, "no_match", 0


results = crosswalk["soc_code"].apply(lambda s: get_exposure(s, exposure))
crosswalk["exposure_value"] = results.apply(lambda x: x[0])
crosswalk["match_type"] = results.apply(lambda x: x[1])
crosswalk["n_children_averaged"] = results.apply(lambda x: x[2])

print("\nCrosswalk match breakdown:")
print(crosswalk["match_type"].value_counts().to_string())

# ---------------------------------------------------------------------------
# Merge onto the cleaned CPS data
# ---------------------------------------------------------------------------
cps = pd.read_csv("data/step1_cps_clean.csv")
cps_before = len(cps)
cps = cps[cps["OCC"] != 0]           # exclude people not currently working (no occupation to score)
cps = cps.dropna(subset=["WTFINL"])  # exclude ASEC-only March households (see script 01 notes)
print(f"\nCPS rows after excluding non-workers and ASEC-only rows: {len(cps):,} "
      f"(dropped {cps_before - len(cps):,})")

final = cps.merge(
    crosswalk[["OCC", "exposure_value", "match_type", "n_children_averaged"]],
    on="OCC", how="left"
)

matched = final["exposure_value"].notna().sum()
print(f"\nFinal coverage: {matched:,} / {len(final):,} rows matched to a real exposure score "
      f"({matched/len(final)*100:.1f}%)")

final.to_csv("data/step2_merged.csv", index=False)
print("\nSaved: data/step2_merged.csv")
