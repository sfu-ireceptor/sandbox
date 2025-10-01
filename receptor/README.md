# From IEDB

- Export all receptors from IEDB

From the Excel spreadsheet from IEDB

- Generate a Junction AA for Chain 2 (TRB) column
  - Check if calculate exists
  - Check if curated exists
  - If curated is the same as calculate with C*[WF] then fill in junction_aa

- Generate a _calculated and _curated column for v_gene and j_gene
  - Generate a gene call based on whether the call is allele or gene
  - Essentially drop the allele part

- Generate a v-gene and j_gene column
  - Take the respective _calculated if it exists
  - If not then take the respective _curated value

# On the Unix side:

- Get rid of the first line, the IEDB file has two header rows.
```bash
tail -n +2 iedb_tcr_positive_v3_2024-08-06.tsv > iedb_tcr_positive_v3_tail_2024-08-06.tsv
```

- Get the header columns of interest

```bash
bash cut_headers.sh iedb_tcr_positive_v3_tail_2024-08-06.tsv 'junction_aa,v_gene,j_gene' > iedb_tcr_positive_v3_tail_trb_2024-08-06.tsv
```

- Extract only rows that have a hopefully valid junction_aa, v_gene, j_gene

```bash
cat iedb_tcr_positive_v3_tail_trb_2024-08-06.tsv | awk -F'\t' '$1 ~ /^C.*F$/ && $2 ~ /TRB/ && $3 ~ /TRB/' > iedb_tcr_positive_v3_tail_trb_full_receptor_2024-08-06.tsv
```

- Sort them for uniqueness

```bash
cat iedb_tcr_positive_v3_tail_trb_full_receptor_2024-08-06.tsv | sort -u > iedb_tcr_positive_v3_tail_trb_full_receptor_unique_2024-08-06.tsv
```

- We have a list of TCR chain receptors

```bash
wc -l iedb_tcr_positive_v3_tail_trb_full_receptor_unique_2024-08-06.tsv
134821 iedb_tcr_positive_v3_tail_trb_full_receptor_unique_2024-08-06.tsv
```

