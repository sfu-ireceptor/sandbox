# Run the IEDB receptor search (TAKES A VERY LONG TIME - DAYS)
nohup bash run-t1d-1.sh "2025-08-25_tra_additions_*" /data/src/sandbox/adc-search/receptor/2025-08-25 > 2025-08-27-t1d-1-tra.out

# Annotate each sequence in the analysis with its epitope (TAKES A WHILE - HOURS)
nohup bash $IR_SANDBOX/adc-search/hits-tra.sh hits-sequence-tra-2025-08-25-2025-10-03.tsv > hits-tra-2025-10-03.out &
head -1 ../../t1d-1-trb-analysis/2024-08-06/hits-sequence-trb-header-2024-08-06-2025-10-02.tsv > hits-sequence-tra-header-2025-08-25-2025-10-03.tsv
cat  hits-sequence-tra-2025-08-25-2025-10-03.tsv >> hits-sequence-tra-header-2025-08-25-2025-10-03.tsv
wc -l *.tsv
#   42 hits-sequence-tra-2025-08-25-2025-10-03.tsv
#   43 hits-sequence-tra-header-2025-08-25-2025-10-03.tsv


