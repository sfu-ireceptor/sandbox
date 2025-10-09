# Run the IEDB receptor search (TAKES A VERY LONG TIME - DAYS)
nohup bash run-t1d-3.sh "2025-08-25_trb_additions_*" $IR_SANDBOX/receptor/2025-08-25-TR-IG > t1d-3-2025-10-03.out &

# Generate sequences with hits (hours)
nohup bash $IR_SANDBOX/adc-search/hits-trb.sh hits-sequence-trb-2025-08-25-2025-10-09.tsv > hits-2025-08-25-2025-10-09.out
head -1 hits-sequence-trb-header-2025-08-25-2025-10-06.tsv > hits-sequence-trb-header-2025-08-25-2025-10-09.tsv
cat hits-sequence-trb-2025-08-25-2025-10-09.tsv >> hits-sequence-trb-header-2025-08-25-2025-10-09.tsv
wc -l hits-sequence-trb-*.tsv
   1997 hits-sequence-trb-2025-08-25-2025-10-06.tsv
   1997 hits-sequence-trb-2025-08-25-2025-10-09.tsv
   1998 hits-sequence-trb-header-2025-08-25-2025-10-06.tsv
   1998 hits-sequence-trb-header-2025-08-25-2025-10-09.tsv
   7990 total

