"""Make a summary figure and a short text summary from the combined table."""
import argparse
import matplotlib
matplotlib.use("Agg")  # draw to a file, no screen needed
import matplotlib.pyplot as plt
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--figure", required=True)
parser.add_argument("--summary", required=True)
args = parser.parse_args()

df = pd.read_csv(args.input)
cohorts = list(df["cohort"].unique())

# Figure: age distribution (left) and sex counts (right), one group per cohort.
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
ax1.boxplot([df.loc[df["cohort"] == c, "age_years"].dropna() for c in cohorts],
            tick_labels=cohorts)
ax1.set_ylabel("Age (years)")
ax1.set_title("Age by cohort")

sex_counts = df.groupby(["cohort", "sex"]).size().unstack(fill_value=0).loc[cohorts]
sex_counts.plot(kind="bar", ax=ax2, rot=0)
ax2.set_ylabel("Number of records")
ax2.set_title("Sex by cohort")
ax2.set_xlabel("")
fig.tight_layout()
fig.savefig(args.figure, dpi=150)

# Text summary
lines = ["# Combined table summary", ""]
lines.append(f"Total records: {len(df)}")
lines.append("")
for c in cohorts:
    sub = df[df["cohort"] == c]
    age = sub["age_years"].dropna()
    lines.append(f"## {c} ({len(sub)} records)")
    lines.append(f"- Age: median {age.median():.1f}, range {age.min():.0f} to {age.max():.0f} "
                 f"({len(sub) - len(age)} missing)")
    sex = sub["sex"].value_counts().to_dict()
    lines.append("- Sex: " + ", ".join(f"{k} {v}" for k, v in sex.items()))
    if c == "clinic_samples":
        lines.append(f"- Glucose (mg/dL): mean {sub['glucose_mg_dl'].mean():.1f} "
                     f"({sub['glucose_mg_dl'].isna().sum()} missing)")
    else:
        lines.append(f"- Tumor mutation burden: median {sub['tmb_nonsynonymous'].median():.1f}")
        gene_cols = [col for col in df.columns if col.endswith("_count")]
        for g in gene_cols:
            lines.append(f"- Patients with at least one {g.replace('_count', '')} "
                         f"protein-altering mutation: {(sub[g] > 0).sum()}")
    lines.append("")
lines.append("Note: the two cohorts are different groups of people from different studies, "
             "so they were stacked, not joined. Age means 'age as of 2026-09-30' in the "
             "clinic cohort and 'age at diagnosis' in the LUAD cohort.")
with open(args.summary, "w") as f:
    f.write("\n".join(lines) + "\n")
print(f"Wrote {args.figure} and {args.summary}")