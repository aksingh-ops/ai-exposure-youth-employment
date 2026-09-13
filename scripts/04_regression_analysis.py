"""
04_regression_analysis.py

The formal statistical test: does young workers' probability of employment (vs. prime-age
workers) trend differently over time depending on AI exposure level? Uses the CONTINUOUS
exposure value directly - not the categorical buckets from script 03, which are for
charting only. Standard errors are clustered by occupation.

Why cluster? Millions of individual survey respondents share only ~530 distinct occupation-
level exposure values. Treating every person as an independent observation understates
the true uncertainty and overstates statistical significance - an early, uncorrected version
of this exact regression showed p < 0.0001, which dropped to p = 0.09 once properly
clustered. That correction is disclosed here, not hidden.

INPUT:  data/step2_merged.csv
OUTPUT: printed regression output; no file written (this is the final analytical step)
"""

import pandas as pd
import statsmodels.formula.api as smf

df = pd.read_csv("data/step2_merged.csv")
df = df.dropna(subset=["exposure_value"])

df["age_group"] = df["AGE"].apply(
    lambda a: "young" if 22 <= a <= 25 else ("prime" if 35 <= a <= 54 else "other")
)
comparison = df[df["age_group"] != "other"].copy()
comparison["is_young"] = (comparison["age_group"] == "young").astype(int)
comparison["year_centered"] = comparison["YEAR"] - comparison["YEAR"].mean()

model = smf.wls(
    "is_young ~ year_centered * exposure_value",
    data=comparison,
    weights=comparison["WTFINL"],
).fit(cov_type="cluster", cov_kwds={"groups": comparison["OCC"]})

print(model.summary())

coef = model.params["year_centered:exposure_value"]
pval = model.pvalues["year_centered:exposure_value"]
max_exposure = df["exposure_value"].max()
baseline_young_share = 0.17  # approximate average young-worker share across the sample
implied_relative_decline_pct = (coef * max_exposure * 4) / baseline_young_share * 100

print("\n" + "=" * 70)
print("RESULT SUMMARY")
print("=" * 70)
print(f"Interaction coefficient (year_centered x exposure_value): {coef:.6f}")
print(f"P-value: {pval:.4f}")
print(f"Implied relative decline in young-worker share, highest-exposure occupations, "
      f"2022-2026: {implied_relative_decline_pct:.1f}%")
print("For comparison: Brynjolfsson, Chandar & Chen (2025) report a 13-19% relative decline "
      "using private ADP payroll data.")
if pval < 0.05:
    print("=> Statistically significant at the conventional 5% level.")
else:
    print("=> NOT statistically significant at the conventional 5% level "
          "(marginal/suggestive, not conclusive).")
