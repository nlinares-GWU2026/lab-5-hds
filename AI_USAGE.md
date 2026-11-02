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

