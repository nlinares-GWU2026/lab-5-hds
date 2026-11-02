"""Build a samples x features x metadata table from the cleaned CSV output,
following Week 5's shape, and check it against the readiness checklist."""
import argparse
from datetime import date
from pathlib import Path

import pandas as pd

FEATURE_COLS = ["glucose_mg_dl"]
METADATA_COLS = ["sex", "enrollment_site", "age_years", "notes",
                  "glucose_flag", "glucose_unit_original"]

# Calculates indvidual's age in whole completed years relative to a reference,
# benchmark date (as_of=date(2026, 09, 30)), splits a "YYYY-MM-DD" ISO dob string into integer year, month, and day components to 
# construct a standard datetime.date object (born), calculates the preliminary age by subtracting,
# the birth year from the reference year (as_of.year - born.year), and applies a check if the reference date's caldendar
# day/month occurs before the birth day/month in the current year, it subtracts 1 to account for the bday not having occurred yet. 
def age_from_dob(dob_str, as_of=date(2026, 9, 30)):
    """'YYYY-MM-DD' -> age in whole years as of as_of."""
    y, m, d = (int(p) for p in dob_str.split("-"))
    born = date(y, m, d)
    years = as_of.year - born.year
    if (as_of.month, as_of.day) < (born.month, born.day):
        years -= 1
    return years

# Loads CSV file into a df, uses keep_default_na=False and explicit na_values={"glucose_mg_dl": ""}, 
# to prevent Pandas from automatically parsing empty categorical text fields as NaN, while ensuring empty numeric cells in glucose_mg_dl,
#  are properly treated as missing numeric values, transforms the dob column into a derived feature column (age_years) by applying .map(age_from_dob),
# contructs the final structured table layout following the samples x features x metadata analytic architecture
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    df = pd.read_csv(args.input, keep_default_na=False,
                      na_values={"glucose_mg_dl": ""})
    df["age_years"] = df["dob"].map(age_from_dob)

    out = df[["sample_id"] + FEATURE_COLS + METADATA_COLS].set_index("sample_id")

    print(out.head(8).to_string(), "\n")
    print("dtypes:")
    print(out.dtypes.to_string(), "\n")
    print("Missing values per column:")
    print(out.isna().sum().to_string(), "\n")
    print("age_years range:", out["age_years"].min(), "to", out["age_years"].max())

    out.to_csv(args.output)
    print(f"\nWrote {len(out)} rows to {args.output}")


if __name__ == "__main__":
    main()