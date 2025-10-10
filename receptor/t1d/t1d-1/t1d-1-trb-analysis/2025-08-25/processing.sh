# Run the IEDB receptor search (TAKES A VERY LONG TIME - DAYS)
nohup bash run-t1d-1.sh "2025-08-25_trb_additions_*" /data/src/sandbox/adc-search/receptor/2025-08-25 > 2025-08-27-t1d-1.out &

# Annotate each sequence in the analysis with its epitope (TAKES A WHILE - HOURS)
nohup bash $IR_SANDBOX/adc-search/hits-trb.sh hits-sequence-trb-2025-08-25-2025-10-09.tsv > hits-trb-2025-08-25-2025-10-09.out &
head -1 hits-sequence-trb-header-2025-08-25-2025-10-02.tsv > hits-sequence-trb-header-2025-08-25-2025-10-09.tsv
cat hits-sequence-trb-2025-08-25-2025-10-09.tsv >> hits-sequence-trb-header-2025-08-25-2025-10-09.tsv
wc -l hits-sequence-trb-*.tsv
   1236 hits-sequence-trb-2025-08-25-2025-10-02.tsv
   1236 hits-sequence-trb-2025-08-25-2025-10-09.tsv
   1237 hits-sequence-trb-header-2025-08-25-2025-10-02.tsv
   1237 hits-sequence-trb-header-2025-08-25-2025-10-09.tsv
   4946 total

