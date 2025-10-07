# Run the IEDB receptor search (days)
nohup bash run_t1d-2_tra.sh > run_t1d-2_tra-2025-07-11.out &

# Generate sequences with hits (hours) - Believe this is correct.
nohup bash $IR_SANDBOX/adc-search/hits-tra.sh hits-sequence-tra-2025-07-11-2025-10-07.tsv > hits-2025-10-07.out &
head -1 ../../t1d-1/t1d-1-trb-analysis/2024-08-06/hits-sequence-trb-header-2024-08-06-2025-10-02.tsv > hits-sequence-tra-header-2025-07-11-2025-10-07.tsv
cat hits-sequence-tra-2025-07-11-2025-10-07.tsv >> hits-sequence-tra-header-2025-07-11-2025-10-07.tsv

# Count number of sequences
wc -l hits*seq*.tsv
    9568 hits-sequence-tra-2025-07-11-2025-10-07.tsv
    9569 hits-sequence-tra-header-2025-07-11-2025-10-07.tsv
    9568 hits-tra-sequence-2025-08-21.tsv

