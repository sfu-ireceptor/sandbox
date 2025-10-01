# Initial TRA IEDB Export

This export was produced on 2025-07-11, using the process described in
the directory above.

- Change column from e.g. junction_aa to junction_aa_tra to differentiate between TRA and TRB
```bash
vi iedb_tcr_positive_v3_2025-07-11.tsv

- Get rid of the first line, the IEDB file has two header rows.

```bash
tail -n +2 iedb_tcr_positive_v3_2025-07-11.tsv > iedb_tcr_positive_v3_tail_2025-07-11.tsv
```

- Get the header columns of interest

```bash
bash ../cut_headers.sh iedb_tcr_positive_v3_tail_2025-07-11.tsv 'junction_aa_tra,v_gene_tra,j_gene_tra' > iedb_tcr_positive_v3_tail_tra_2025-07-11.tsv
```

- Extract only rows that have a hopefully valid junction_aa, v_gene, j_gene

```bash
cat iedb_tcr_positive_v3_tail_tra_2025-07-11.tsv | awk -F'\t' '$1 ~ /^C.*F$/ && $2 ~ /TRA/ && $3 ~ /TRA/'> iedb_tcr_positive_v3_tail_tra_full_receptor_2025-07-11.tsv
```

- Sort them for uniqueness

```bash
cat iedb_tcr_positive_v3_tail_tra_full_receptor_2025-07-11.tsv | sort -u > iedb_tcr_positive_v3_tail_tra_full_receptor_unique_2025-07-11.tsv
```

- We have a list of TCR chain receptors

```bash
wc -l iedb_tcr_positive_v3_tail_tra_full_receptor_unique_2025-07-11.tsv
23581 iedb_tcr_positive_v3_tail_tra_full_receptor_unique_2025-07-11.tsv
```

- Split the file into a manageable subset with 10000 receptors in each file

```bash
split -l 10000 -d -a 2 --additional-suffix=.tsv iedb_tcr_positive_v3_tail_tra_full_receptor_unique_2025-07-11.tsv iedb_tcr_tra
wc -l iedb_tcr_tra*
 10000 iedb_tcr_tra00.tsv
 10000 iedb_tcr_tra01.tsv
  3581 iedb_tcr_tra02.tsv
 23581 total
```

