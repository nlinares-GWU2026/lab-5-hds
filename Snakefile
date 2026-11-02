rule all:
    input:
        "results/combined_table.csv",
        "results/summary_figure.png",
        "results/summary.md",


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


rule merge_tables:
    input:
        samples="results/samples_table.csv",
        features="results/feature_table.tsv",
    output:
        "results/combined_table.csv",
    shell:
        "python scripts/merge_tables.py --samples {input.samples} "
        "--features {input.features} --output {output}"


rule make_report:
    input:
        "results/combined_table.csv",
    output:
        figure="results/summary_figure.png",
        summary="results/summary.md",
    shell:
        "python scripts/make_report.py --input {input} "
        "--figure {output.figure} --summary {output.summary}"