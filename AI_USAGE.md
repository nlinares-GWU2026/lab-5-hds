# AI Usage
- **Tool:** Claude (Sonnet 5.5)
- **What I was doing:**
- **What I asked (verbatim):**
- **Exact output (verbatim):**
## Entry 1:
- **Tool:** Claude (Sonnet 5.5)
- **What I was doing:** Setting up an environment for the lab.
- **What I asked (verbatim):** "Besides python (3.12), snakemake (v9), pandas v 2.2, matplotlib, what other dependency do I need to create a DAG? (Pasted my environment file).
- **Exact output (verbatim):**
Write environment.yml
```bash
cat > environment.yml << 'EOF'
name: lab-5-hds
channels:
  - conda-forge
  - bioconda
dependencies:
  - python=3.12
  - snakemake>=9
  - pandas=2.2
  - matplotlib
  - graphviz
EOF
```
What each line is for:

- snakemake>=9 is the workflow manager. It lives on the bioconda channel, which is why that channel is listed.
- matplotlib draws the figure for our summary report.
- graphviz provides the dot command that draws the DAG picture. We’ll want that picture as evidence.
SQLite needs no entry because it comes built into Python.

## Entry 2:
- **Tool:** Claude (Sonnet 5.5)
- **What I was doing:** Adjusting my scripts without the file paths written so Snakemake use them (no hidden dependencies).
- **What I asked (verbatim):** "How do I adjust these following files so they do not have any dependencies and Snakemake can use them? (attached `clean_samples_regex.py`, `build_analytic_table.py`, and `build_feature_table.py` and added my previous lab 3 and lab 4 GitHub repo links)
- **Exact output (verbatim):**
First I'll read your Lab 3 and Lab 4 scripts in full, so the instructions match your actual code.

**Why change them.** Right now your scripts have their file paths written inside them, such as `RAW = ROOT / "data/raw/..."`. Snakemake can't see those paths, which is a hidden dependency, and "No hidden dependencies" is worth 20 rubric points. We'll change each script to take its files as command-line flags (`--input`, `--output`), so the Snakefile can say exactly what goes in and comes out. This is the same `argparse` pattern as the course's `clean_site.py` in the Week 10 practical. Your cleaning logic doesn't change at all.

**Pull the files in**

Download them from your public repos, so you don't have to hunt for where your old folders live:

```bash
cd ~/lab-5-hds
conda activate lab-5-hds
mkdir -p sql
BASE=https://raw.githubusercontent.com/nlinares-GWU2026
curl -L -o scripts/clean_samples_regex.py $BASE/lab-3-hds/main/src/clean_samples_regex.py
curl -L -o scripts/build_analytic_table.py $BASE/lab-3-hds/main/src/build_analytic_table.py
curl -L -o scripts/build_feature_table.py $BASE/lab-4-hds/main/scripts/build_feature_table.py
curl -L -o sql/query_1.sql $BASE/lab-4-hds/main/sql/query_1.sql
curl -L -o sql/query_3.sql $BASE/lab-4-hds/main/sql/query_3.sql
ls scripts sql
```

These are the versions you pushed to GitHub. We skip `query_2.sql`, because the feature-table script doesn't use it.

**`scripts/clean_samples_regex.py`**

Open it with `nano scripts/clean_samples_regex.py` (Ctrl+W searches, Ctrl+O saves, Ctrl+X exits) or in your editor. There are four edits:

1. Add `import argparse` on its own line above `import re`.
2. Delete these three lines, since they hard-code the paths:
   ```python
   ROOT = Path(__file__).resolve().parent.parent
   RAW = ROOT / "data/raw/lab3-messy-data/messy_samples.csv"
   OUT = ROOT / "data/processed/samples_clean_regex.csv"
   ```
3. Directly under `def main():`, add this block, indented 4 spaces, followed by a blank line:
   ```python
       parser = argparse.ArgumentParser()
       parser.add_argument("--input", required=True)
       parser.add_argument("--output", required=True)
       args = parser.parse_args()
   ```
4. Replace these four pieces of text elsewhere in `main()`:

| Find | Replace with |
|---|---|
| `pd.read_csv(RAW,` | `pd.read_csv(args.input,` |
| `OUT.parent.mkdir(parents=True, exist_ok=True)` | `Path(args.output).parent.mkdir(parents=True, exist_ok=True)` |
| `out.to_csv(OUT, index=False)` | `out.to_csv(args.output, index=False)` |
| `{OUT.relative_to(ROOT)}` | `{args.output}` |

**`scripts/build_analytic_table.py`**

1. Add `import argparse` above `from datetime import date`.
2. Delete the three lines `ROOT = ...`, `CLEAN = ...`, and `OUT = ...`.
3. Add the same four-line `argparse` block directly under `def main():`. It does **not** go under `def age_from_dob`.
4. Replace:

| Find | Replace with |
|---|---|
| `pd.read_csv(CLEAN,` | `pd.read_csv(args.input,` |
| `out.to_csv(OUT)` | `out.to_csv(args.output)` |
| `{OUT.relative_to(ROOT)}` | `{args.output}` |

**`scripts/build_feature_table.py`**

This one has four inputs and outputs: the database and the two SQL files it reads, plus the output file. The SQL files count as inputs too. If you edit a query, the results change, so Snakemake needs to know.

1. Add `import argparse` above `import sqlite3`.
2. Delete these four lines, but **keep** `GENES` and `GENE_COLUMNS`:
   ```python
   DB_PATH = "data/cohort.db"
   BASE_SQL = "sql/query_3.sql"
   GENE_COUNTS_SQL = "sql/query_1.sql"
   OUTPUT_PATH = "outputs/feature_table.tsv"
   ```
3. Directly under `def main():`, add:
   ```python
       parser = argparse.ArgumentParser()
       parser.add_argument("--db", required=True)
       parser.add_argument("--base-sql", required=True)
       parser.add_argument("--counts-sql", required=True)
       parser.add_argument("--output", required=True)
       args = parser.parse_args()
   ```
4. Replace:

| Find | Replace with |
|---|---|
| `sqlite3.connect(DB_PATH)` | `sqlite3.connect(args.db)` |
| `run_sql_file(con, BASE_SQL)` | `run_sql_file(con, args.base_sql)` |
| `run_sql_file(con, GENE_COUNTS_SQL)` | `run_sql_file(con, args.counts_sql)` |
| `feature_table.to_csv(OUTPUT_PATH,` | `feature_table.to_csv(args.output,` |
| `print(f"Wrote {OUTPUT_PATH}:` | `print(f"Wrote {args.output}:` |

**Check for leftovers, then test each script by hand**

This should print nothing:

```bash
grep -nE "\b(ROOT|RAW|OUT|CLEAN|OUTPUT_PATH|DB_PATH|BASE_SQL|GENE_COUNTS_SQL)\b" scripts/*.py
```

Then run each script once:

```bash
mkdir -p results
python scripts/clean_samples_regex.py --input data/raw/lab3-messy-data/messy_samples.csv --output results/samples_clean.csv
python scripts/build_analytic_table.py --input results/samples_clean.csv --output results/samples_table.csv
python scripts/build_feature_table.py --db data/raw/lab4-cbioportal-luad/cohort.db --base-sql sql/query_3.sql --counts-sql sql/query_1.sql --output results/feature_table.tsv
```

The last line of each should be:
- `Wrote 60 rows to results/samples_clean.csv`
- `Wrote 60 rows to results/samples_table.csv`
- `Wrote results/feature_table.tsv: 566 rows x 11 columns`

Those file names under `results/` are the ones the Snakefile will use, so keep them exactly.

**Now delete those test outputs:**

```bash
rm -r results
```

This matters. Snakemake skips any step whose output files already exist and are up to date. If we leave these test files in place, your first real Snakemake run would say "Nothing to be done" and prove nothing.
- **Verification:** I ran all commands and they went smoothly. It makes sense how the process works for removing the file paths and where to adjust the following lines in the scripts. It also was logical to run a test to make sure all the files ran smoothly. 

## Entry 3:
- **Tool:** Claude (Sonnet 5.5)
- **What I was doing:** Drafting the Snakefile.
- **What I asked (verbatim):** With these scripts, can you help me draft a Snakefile? Additionally, I am supposed to merge the two into a "combined analytic table", although I am not sure how to do this because the two tables have no shared ID and no overlapping patients. Some columns are the same but I have no idea how I would join them row-to-row. Do you have an idea/plan on how to do this?"
- **Exact output (verbatim):**
### The first three rules of the Snakefile

I tested this Snakefile on my scratch copy with Snakemake 9. The dry run, the real run and the "nothing to do" re-check all behaved as described below.

**Before we write it, a quick explanation of how it works.** A Snakefile describes the pipeline backwards. Each `rule` says "to make this output, I need these inputs, and here's the command." Snakemake reads the rules, works out the order itself, and draws the DAG. That is the whole point of a workflow manager. The first rule, `rule all`, lists the final files you want. Snakemake starts from those and works backwards.

For now `rule all` asks for the two tables we already know how to make. In the next step we'll change it to ask for the final report, and the DAG will grow.

**Create the Snakefile**

With the environment active:

```bash
cat > Snakefile << 'EOF'
rule all:
    input:
        "results/samples_table.csv",
        "results/feature_table.tsv",


rule clean_samples:
    input:
        "data/raw/lab3-messy-data/messy_samples.csv",
    output:
        "results/samples_clean.csv",
    shell:
        "python scripts/clean_samples_regex.py --input {input} --output {output}"


rule build_samples_table:
    input:
        "results/samples_clean.csv",
    output:
        "results/samples_table.csv",
    shell:
        "python scripts/build_analytic_table.py --input {input} --output {output}"


rule build_feature_table:
    input:
        db="data/raw/lab4-cbioportal-luad/cohort.db",
        base_sql="sql/query_3.sql",
        counts_sql="sql/query_1.sql",
    output:
        "results/feature_table.tsv",
    shell:
        "python scripts/build_feature_table.py --db {input.db} "
        "--base-sql {input.base_sql} --counts-sql {input.counts_sql} --output {output}"
EOF
```

What to notice:
- **Everything is a declared input.** `build_feature_table` lists the database and both SQL files by name, with labels (`db=`, `base_sql=`, and so on). That is exactly the "no hidden dependencies" the rubric asks for. If you edit `query_1.sql`, Snakemake knows this step is out of date.
- **`{input}` and `{output}` in the shell command** are filled in from the lists above them. That's why the scripts needed the `--input` and `--output` flags in Step 4. `{input.db}` picks one named input.
- **Indentation is 4 spaces, never tabs.** Mixed tabs and spaces are the `IndentationError`.

**Then dry run**

```bash
snakemake -n
```

`-n` is a **dry run**. It shows what *would* run and why, and changes nothing. Look at the `Job stats` table at the bottom. The `total` line should match your prediction. Also read the `reason:` lines. They say "Missing output files", which is Snakemake explaining why it wants to run each step.

**Run it for real**

```bash
snakemake --cores 2
```

`--cores 2` lets up to two jobs run at once. Snakemake requires it, and without it you get the `cores have to be specified` error. Look at the output. `clean_samples` and `build_feature_table` don't depend on each other, so they can run in parallel, and that's what "scalable" means here.

You should see the same three "Wrote …" lines as in Step 4: 60 rows, 60 rows, and `566 rows x 11 columns`.

**The key check**

```bash
snakemake -n
```

It should now say `Nothing to be done (all requested files are present and up to date).` Snakemake looks at the files, sees that every output is newer than its inputs, and does nothing.

**Commit**

```bash
git status
git add Snakefile
git commit -m "Add Snakefile: clean samples, build samples table, build feature table"
git push
```

`git status` should show `results/` as untracked. That's fine. We'll commit the results at the end, once the final table and report exist.

**Send me the `total` job count from and the last line**

**A heads-up about the merge** 
I compared your two tables. They have no shared ID and no overlapping people, but they do share two columns: `sex` and age (`age_years` in one table, `age_at_diagnosis` in the other). Because of that, there's no honest way to join them row-to-row. My plan is to harmonize those shared columns and stack the two tables into one combined table, with a `cohort` column saying where each row came from. That fits a "combined analytic table". We'll document the choice. If you'd rather do it a different way, tell me.
- **Verification:** I completed all the steps and all ran smoothly. I predicted 4 steps/jobs that would be completed prior to the actual run, which was correct. I thought about the proposal to merge the two datasets this way and couldn't think of a better way to do it myself, so I agreed with Claude's approach. 

## Entry 4:
- **Tool:** Claude (Sonnet 5.5)
- **What I was doing:** Merging the two tables.
- **What I asked (verbatim):** "I couldn't think of another way to merge the two tables together, so let's go ahead and stack them by shared categories like sex and age_years. Maybe we could add a column saying which table each row came from? Leave the missing ones as NA. Can you help me write a python script for this? Additionally, I need help writing a summary report and a figure (it can be simple) about the data."
- **Exact output (verbatim):**
Your two tables share `sex` and age, so stacking them is the simplest honest merge. Next I'll write and test the merge script and the report script.

The pipeline works end to end. I'll look at the figure before sending you anything.

### The merge and the report (all four stages)

**How the merge works.** Your two tables are different groups of people with no shared ID, so I stacked them instead of joining them. Each table's columns are renamed to a shared scheme (`sex`, `age_years`, `site`) and the rows go one under the other. A `cohort` column says which table each row came from. Columns that only exist in one table, such as glucose or the gene counts, are `NA` for the other. The script also checks that the row count is exactly 60 + 566 and that no ID repeats, like the audits in your Lab 4 script.

Two decisions in the script you should know about:
- A missing sex in the Lab 4 data becomes `unknown`, to match Lab 3's `U` code.
- "Age" means different things in the two tables: age as of Sep 30 for the clinic samples, and age at diagnosis for the cancer patients. The report notes this.

**Create `scripts/merge_tables.py`**

```bash
cat > scripts/merge_tables.py << 'EOF'
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
EOF
```

**Create `scripts/make_report.py`**

```bash
cat > scripts/make_report.py << 'EOF'
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
EOF
```

You should see Wrote results/combined_table.csv: 626 rows x 13 columns, and the summary should say 626 total records (60 clinic, 566 LUAD). To see the figure, open it from Windows Explorer at \\wsl$\Ubuntu\home\<your-username>\lab-5-hds\results\summary_figure.png, or run explorer.exe results from your terminal. You should see an age boxplot and a sex bar chart for the two cohorts.
- **Verification:** I created the scripts, then updated the Snakefile to include the rule for `merge_tables` and `make_report`. I made the inputs for these the outputs of two earlier rules `build_samples_table` and `build_feature_table`. I then did a dry run and predicted a total of 3 jobs because now Snakemake will have the results from the other 3 already done and then th new 2 from the `merge_tables` and `make_report`. I ran a test run and inspected the `summary.md`. I checked that against what Claude said the expected `results/combined_table.csv` and inspected the figure. Both matched what Claude said. Everything checked out and I was correct in my prediction of 3 jobs.   