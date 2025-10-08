# Run the IEDB receptor search (days)
nohup bash run-t1d-2.sh "trb[0-1]*" /data/src/sandbox/receptor/2024-08-06-TRB > run-t1d-2-2025-10-08.out &

# Generate sequences with hits (hours) - original data with two studies
nohup bash ../../hits.sh hits-sequences-2025-02-14.out > hits-2025-02-14.out &

# Count number of sequences - original data with two studies
wc -l hits-sequence-2025-02-14.tsv
6198 hits-sequence-2025-02-14.tsv

