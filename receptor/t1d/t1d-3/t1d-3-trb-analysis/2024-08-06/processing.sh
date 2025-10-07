# Run the IEDB receptor search (days)
nohup bash run_t1d-3.sh > t1d-3-2025-03-22.out

# Generate sequences with hits (hours)
nohup bash $IR_SANDBOX/adc-search/hits-trb.sh hits-sequence-trb-2024-08-06-2025-10-03.tsv > hits-2024-08-06-2025-10-03.out &

# Count number of sequences
$ wc -l hits-sequence-trb-2024-08-06-2025-10-03.tsv
# 874173 hits-sequence-trb-2024-08-06-2025-10-03.tsv
# wc -l hits-sequences-2025-04-02.out
# 874173 hits-sequences-2025-04-02.out

# Count number of unique repertoires (column 2)
$ cut -f 2 hits-sequence-trb-2024-08-06-2025-10-03.tsv | sort -u | wc -l
# 2072
# cut -f 2 hits-sequences-2025-04-02.out | sort -u | wc -l
# 2072

# Count number of unique IEDB receptors (column 6)
bash $IR_SANDBOX/adc-search/unique_extract.sh hits-sequence-trb-2024-08-06-2025-10-03.tsv 6 > receptors-2025-10-06.tsv
wc -l receptors-2025-10-06.tsv
# 26864 receptors-2025-10-06.tsv

