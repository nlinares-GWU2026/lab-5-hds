"""Stack the Lab 3 samples table and the Lab 4 feature table into one combined table.

The two tables have no shared ID (different people, different studies), so they cannot
be joined row-to-row. Instead the columns they have in common (sex, age, site) are
harmonized to one naming and coding scheme, and the rows are stacked. A 'cohort'
column records which table each row came from. Columns that exist in only one
table are left empty (NA) for rows from the other.
"""
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("--samples", required=True)
parser.add_argument("--features", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()

samples = pd.read_csv(args.samples, keep_default_na=False,
                      na_values={"glucose_mg_dl": ""})
features = pd.read_csv(args.features, sep="\t")

# Lab 3 table -> shared column names. Sex codes M/F/U become male/female/unknown.
clinic = pd.DataFrame({
    "cohort": "clinic_samples",
    "record_id": samples["sample_id"],
    "sex": samples["sex"].map({"M": "male", "F": "female", "U": "unknown"}),
    "age_years": samples["age_years"],
    "site": samples["enrollment_site"],
    "glucose_mg_dl": samples["glucose_mg_dl"],
})

# Lab 4 table -> shared column names. A missing sex becomes 'unknown' to match Lab 3.
luad = pd.DataFrame({
    "cohort": "luad_tcga",
    "record_id": features["patient_id"],
    "sex": features["sex"].fillna("unknown"),
    "age_years": features["age_at_diagnosis"],
    "site": features["tissue_source_site"],
    "stage": features["stage"],
    "tmb_nonsynonymous": features["tmb_nonsynonymous"],
})
for col in ["TP53_count", "KRAS_count", "EGFR_count", "STK11_count", "KEAP1_count"]:
    luad[col] = features[col]

combined = pd.concat([clinic, luad], ignore_index=True)

# Checks: stacking must not lose or invent rows or IDs.
assert len(combined) == len(samples) + len(features), "row count changed during stacking"
assert combined["record_id"].is_unique, "a record_id appears more than once"

print("Rows per cohort:")
print(combined["cohort"].value_counts().to_string())
print("Missing values per column:")
print(combined.isna().sum().to_string())

combined.to_csv(args.output, index=False, na_rep="NA")
print(f"Wrote {args.output}: {combined.shape[0]} rows x {combined.shape[1]} columns")
