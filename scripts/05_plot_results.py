"""
05_plot_results.py

Produces the final chart: young workers' share of employment by AI-exposure category, over
time.

INPUT:  outputs/young_share_by_category_year.csv
OUTPUT: outputs/final_chart.png
"""

import pandas as pd
import matplotlib.pyplot as plt

pivot = pd.read_csv("outputs/young_share_by_category_year.csv")

fig, ax = plt.subplots(figsize=(10, 6))
colors = {
    "No observed AI use": "#4C72B0",
    "Low (non-zero)": "#8C9EB5",
    "Medium": "#DD8452",
    "High": "#C44E52",
}
for category, color in colors.items():
    sub = pivot[pivot["exposure_category"] == category].sort_values("YEAR")
    linewidth = 3 if category in ("No observed AI use", "High") else 1.8
    ax.plot(
        sub["YEAR"], sub["young_share"] * 100,
        marker="o", label=category, color=color, linewidth=linewidth,
    )

ax.set_title(
    "Young Workers' (Age 22-25) Share of Employment, by AI-Exposure Category\n"
    "U.S. Current Population Survey, 2022-2026",
    fontsize=13, fontweight="bold",
)
ax.set_xlabel("Year")
ax.set_ylabel("Young workers as % of employment\n(vs. prime-age 35-54 comparison group)")
ax.set_xticks(pivot["YEAR"].unique())
ax.legend(title="AI-Exposure Category (Anthropic Economic Index)")
ax.grid(True, alpha=0.3)

fig.text(
    0.5, -0.03,
    "Data: IPUMS CPS + Anthropic Economic Index + Census OCC-SOC crosswalk.\n"
    "Effect is directionally consistent with published literature but marginal, not "
    "statistically conclusive (p\u22480.09).",
    ha="center", fontsize=8, style="italic", color="gray",
)

plt.tight_layout()
plt.savefig("outputs/final_chart.png", dpi=200, bbox_inches="tight")
print("Saved: outputs/final_chart.png")
plt.show()
