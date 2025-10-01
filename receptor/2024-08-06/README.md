# Initial IEDB Export

This export was produced on 2024-08-06, using the process described in
the directory above.

On the Unix side:

- Get rid of the first line, the IEDB file has two header rows.

tail -n +2 iedb_tcr_positive_v3_2024-08-06.tsv > iedb_tcr_positive_v3_tail_2024-08-06.tsv

- Get the header columns of interest

bash cut_headers.sh iedb_tcr_positive_v3_tail_2024-08-06.tsv 'junction_aa,v_gene,j_gene' > iedb_tcr_positive_v3_tail_trb_2024-08-06.tsv

- Extract only rows that have a hopefully valid junction_aa, v_gene, j_gene

cat iedb_tcr_positive_v3_tail_trb_2024-08-06.tsv | awk -F'\t' '$1 ~ /^C.*F$/ && $2 ~ /TRB/ && $3 ~ /TRB/' > iedb_tcr_positive_v3_tail_trb_full_r
eceptor_2024-08-06.tsv

- Sort them for uniqueness

cat iedb_tcr_positive_v3_tail_trb_full_receptor_2024-08-06.tsv | sort -u > iedb_tcr_positive_v3_tail_trb_full_receptor_unique_2024-08-06.tsv

- We have a list of TCR chain receptors

wc -l iedb_tcr_positive_v3_tail_trb_full_receptor_unique_2024-08-06.tsv
134821 iedb_tcr_positive_v3_tail_trb_full_receptor_unique_2024-08-06.tsv

- Split the file into a manageable subset with 10000 receptors in each file

split -l 10000 -d -a 2 --additional-suffix=.tsv iedb_tcr_positive_v3_tail_trb_full_receptor_unique_2024-08-06.tsv iedb_tcr_trb
