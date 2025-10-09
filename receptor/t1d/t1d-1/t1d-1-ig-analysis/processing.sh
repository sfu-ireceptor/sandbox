# Run the IEDB receptor search (TAKES A VERY LONG TIME - DAYS)
nohup bash run-t1d-1-IG.sh "2025-08-25-bcr_receptor_table_export_1753794648_tail_IG_full_chain_unique.tsv" $IR_SANDBOX/receptor/2025-08-25-TR-IG > 2025-10-07-t1d-1-IG.out

# Annotate each sequence in the analysis with its epitope (TAKES A WHILE - HOURS)
nohup bash $IR_SANDBOX/adc-search/hits-igh.sh hits-sequence-IG-2025-08-25-2025-10-09.tsv > hits-IG-2025-08-25-2025-10-09.out
# No IG hits found int t1d-1
wc -l hits-sequence-IG-2025-08-25-2025-10-09.tsv
0 hits-sequence-IG-2025-08-25-2025-10-09.tsv

