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

- snakemake>=9 is the workflow manager. It lives on the bioconda channel, which is why that channel is listed, exactly as in the Week 10 environment.yml.
- pandas=2.2 is the version your Lab 4 environment used, so your old scripts behave the same.
- matplotlib draws the figure for our summary report.
- graphviz provides the dot command that draws the DAG picture. We’ll want that picture as evidence.
SQLite needs no entry because it comes built into Python.

## Entry 2:
- **Tool:** Claude (Sonnet 5.5)
- **What I was doing:** Adjusting my scripts without the file paths written so Snakemake use them (no hidden dependencies).
- **What I asked (verbatim):** "How do I adjust these following files so they do not have any dependencies and Snakemake can use them? (attached `clean_samples_regex.py`, `build_analytic_table.py`, and `build_feature_table.py`)
- **Exact output (verbatim):**
First I'll read your Lab 3 and Lab 4 scripts in full, so the instructions match your actual code.

I'll test the exact edits I'm about to give you on a scratch copy first, so the instructions are known to work against the real data.

In my roadmap, steps 3 and 4 are "copy in your scripts" and "write the Snakefile". We'll do the scripts now, because the Snakefile depends on how they're called. I tested every edit below on a scratch copy against the real data, and your scripts produce exactly your Lab 4 numbers (566 rows × 11 columns).

## Step 4: Bring in your Lab 3 and Lab 4 scripts and adapt them

**Why copy them in.** The labs README says each lab is its own repo with no cross-lab dependencies, so Lab 5 needs its own copies.

**Why change them.** Right now your scripts have their file paths written inside them, such as `RAW = ROOT / "data/raw/..."`. Snakemake can't see those paths, which is a hidden dependency, and "No hidden dependencies" is worth 20 rubric points. We'll change each script to take its files as command-line flags (`--input`, `--output`), so the Snakefile can say exactly what goes in and comes out. This is the same `argparse` pattern as the course's `clean_site.py` in the Week 10 practical. Your cleaning logic doesn't change at all.

**4a. Pull the files in**

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

**4b. Edit `scripts/clean_samples_regex.py`**

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

**4c. Edit `scripts/build_analytic_table.py`**

1. Add `import argparse` above `from datetime import date`.
2. Delete the three lines `ROOT = ...`, `CLEAN = ...`, and `OUT = ...`.
3. Add the same four-line `argparse` block directly under `def main():`. It does **not** go under `def age_from_dob`.
4. Replace:

| Find | Replace with |
|---|---|
| `pd.read_csv(CLEAN,` | `pd.read_csv(args.input,` |
| `out.to_csv(OUT)` | `out.to_csv(args.output)` |
| `{OUT.relative_to(ROOT)}` | `{args.output}` |

**4d. Edit `scripts/build_feature_table.py`**

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

**4e. Check for leftovers, then test each script by hand**

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

