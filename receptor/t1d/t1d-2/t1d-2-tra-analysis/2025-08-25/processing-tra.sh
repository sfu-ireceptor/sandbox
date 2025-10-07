# Run the IEDB receptor search (TAKES A VERY LONG TIME - DAYS)
nohup bash run-t1d-2.sh "2025-08-25_tra_additions_*" $IR_SANDBOX/receptor/2025-08-25-TR-IG > 2025-10-07-t1d-2-tra.out

# Annotate each sequence in the analysis with its epitope (TAKES A WHILE - HOURS)
nohup bash $IR_SANDBOX/adc-search/hits-tra.sh hits-sequence-tra-2025-08-25-2025-10-07.tsv > hits-tra-2025-10-07.out &
head -1 ../2025-07-11/hits-sequence-tra-header-2025-07-11-2025-10-07.tsv > hits-sequence-tra-header-2025-08-25-2025-10-07.tsv
cat hits-sequence-tra-2025-08-25-2025-10-07.tsv >> hits-sequence-tra-header-2025-08-25-2025-10-07.tsv
wc -l hits-sequence-tra-*
  16 hits-sequence-tra-2025-08-25-2025-10-07.tsv
  17 hits-sequence-tra-header-2025-08-25-2025-10-07.tsv

