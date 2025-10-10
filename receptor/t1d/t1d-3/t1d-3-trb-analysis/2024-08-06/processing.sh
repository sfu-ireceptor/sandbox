# Run the IEDB receptor search (days)
nohup bash run_t1d-3.sh > t1d-3-2025-03-22.out

# Generate sequences with hits (hours)
nohup bash $IR_SANDBOX/adc-search/hits-trb.sh hits-sequence-trb-2024-08-06-2025-10-09.tsv > hits-2024-08-06-2025-10-09.out &

head -1 hits-sequence-trb-header-2024-08-06-2025-10-03.tsv > hits-sequence-trb-header-2024-08-06-2025-10-09.tsv
cat hits-sequence-trb-2024-08-06-2025-10-09.tsv >> hits-sequence-trb-header-2024-08-06-2025-10-09.tsv
wc -l hits-sequence*.tsv
    874173 hits-sequence-2025-06-30.tsv
    874173 hits-sequence-2025-07-03.tsv
    874173 hits-sequence-trb-2024-08-06-2025-10-03.tsv
    874173 hits-sequence-trb-2024-08-06-2025-10-09.tsv
    874174 hits-sequence-trb-header-2024-08-06-2025-10-03.tsv
    874174 hits-sequence-trb-header-2024-08-06-2025-10-09.tsv

