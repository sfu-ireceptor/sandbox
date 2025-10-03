# Run the IEDB receptor search (TAKES A VERY LONG TIME - DAYS)
nohup bash run-t1d-1.sh "2025-08-25_trb_additions_*" /data/src/sandbox/adc-search/receptor/2025-08-25 > 2025-08-27-t1d-1.out &

# Annotate each sequence in the analysis with its epitope (TAKES A WHILE - HOURS)
nohup bash ../../../../hits.sh hits-sequence-2025-08-27.tsv > hits-2025-08-27.out &


