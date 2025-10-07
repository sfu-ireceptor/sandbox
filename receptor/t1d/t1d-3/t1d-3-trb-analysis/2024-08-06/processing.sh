# Run the IEDB receptor search (days)
nohup bash run_t1d-3.sh > t1d-3-2025-03-22.out

# Generate sequences with hits (hours)
nohup bash $IR_SANDBOX/adc-search/hits-trb.sh hits-sequence-trb-2024-08-06-2025-10-03.tsv > hits-2024-08-06-2025-10-03.out &
head -1 ../../../t1d-1/t1d-1-trb-analysis/2024-08-06/hits-sequence-trb-header-2024-08-06-2025-10-02.tsv > hits-sequence-trb-header-2024-08-06-2025-10-03.tsv
cat hits-sequence-trb-2024-08-06-2025-10-03.tsv >> hits-sequence-trb-header-2024-08-06-2025-10-03.tsv
wc -l hits-sequence-trb-*
   874173 hits-sequence-trb-2024-08-06-2025-10-03.tsv
   874174 hits-sequence-trb-header-2024-08-06-2025-10-03.tsv
# wc -l hits-sequences-2025-04-02.out
# 874173 hits-sequences-2025-04-02.out

