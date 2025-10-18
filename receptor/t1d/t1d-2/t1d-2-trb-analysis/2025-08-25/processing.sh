# Run the IEDB receptor search (TAKES A VERY LONG TIME - DAYS)
nohup bash run-t1d-2.sh "2025-08-25_trb_additions_*" /data/src/sandbox/receptor/2025-08-25-TR-IG > 2025-10-18-t1d-2.out &

# Annotate each sequence in the analysis with its epitope (TAKES A WHILE - HOURS)
nohup bash $IR_SANDBOX/adc-search/hits-trb.sh hits-sequence-trb-2025-08-25-2025-10-18.tsv > hits-trb-2025-08-25-2025-10-18.out &
head -1 ../../../t1d-1/t1d-1-trb-analysis/2025-08-25/hits-sequence-trb-header-2025-08-25-2025-10-09.tsv > hits-sequence-trb-header-2025-08-25-2025-10-18.tsv
cat hits-sequence-trb-2025-08-25-2025-10-18.tsv >> hits-sequence-trb-header-2025-08-25-2025-10-18.tsv
wc -l hits-sequence-trb-*.tsv
   2935 hits-sequence-trb-2025-08-25-2025-10-18.tsv
   2936 hits-sequence-trb-header-2025-08-25-2025-10-18.tsv
   5871 total
