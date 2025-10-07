# Run the IEDB receptor search (TAKES A VERY LONG TIME - DAYS)
nohup bash run-t1d-3.sh "2025-08-25_trb_additions_*" $IR_SANDBOX/receptor/2025-08-25-TR-IG > t1d-3-2025-10-03.out &

# Generate sequences with hits (hours)
nohup bash $IR_SANDBOX/adc-search/hits-trb.sh hits-sequence-trb-2025-08-25-2025-10-06.tsv > hits-2025-08-25-2025-10-06.out &

# Count number of sequences
$ wc -l hits-sequence-trb-2025-08-25-2025-10-06.tsv
1997 hits-sequence-trb-2025-08-25-2025-10-06.tsv

