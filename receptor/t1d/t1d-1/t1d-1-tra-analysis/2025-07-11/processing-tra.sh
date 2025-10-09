# Run the IEDB receptor search (TAKES A VERY LONG TIME - DAYS)
nohup bash run_t1d-2_tra.sh > run_t1d-2_tra-2025-07-11.out

# Annotate each sequence in the analysis with its epitope (TAKES A WHILE - HOURS)
nohup bash $IR_SANDBOX/adc-search/hits-tra.sh hits-sequence-tra-2025-07-11-2025-10-09.tsv > hits-tra-2025-07-11-2025-10-09.out &
head -1 hits-sequence-tra-header-2025-07-11-2025-10-02.tsv > hits-sequence-tra-header-2025-07-11-2025-10-09.tsv
cat hits-sequence-tra-2025-07-11-2025-10-09.tsv >> hits-sequence-tra-header-2025-07-11-2025-10-09.tsv
wc -l hits-sequence-tra-*
   169 hits-sequence-tra-2025-07-11-2025-10-02.tsv
   169 hits-sequence-tra-2025-07-11-2025-10-09.tsv
   170 hits-sequence-tra-header-2025-07-11-2025-10-02.tsv
   170 hits-sequence-tra-header-2025-07-11-2025-10-09.tsv

# Extract the unique receptors, epitopes, antigens, and organisms
bash $IR_SANDBOX/adc-search/unique_extract.sh hits-sequence-tra-2025-07-11-2025-10-09.tsv 6 > receptors-2025-10-09.out
bash $IR_SANDBOX/adc-search/unique_extract.sh hits-sequence-tra-2025-07-11-2025-10-09.tsv 7 > epitopes-2025-10-09.out
bash $IR_SANDBOX/adc-search/unique_extract.sh hits-sequence-tra-2025-07-11-2025-10-09.tsv 8 > antigens-2025-10-09.out
bash $IR_SANDBOX/adc-search/unique_extract.sh hits-sequence-tra-2025-07-11-2025-10-09.tsv 9 > organsims-2025-10-09.out
bash $IR_SANDBOX/adc-search/unique_extract.sh hits-sequence-tra-2025-07-11-2025-10-09.tsv 10 > mhc-2025-10-09.out
wc -l *2025-10-09*.out
   23 antigens-2025-10-09.out
   86 epitopes-2025-10-09.out
 1280 hits-tra-2025-07-11-2025-10-09.out
   33 mhc-2025-10-09.out
   11 organsims-2025-10-09.out
  177 receptors-2025-10-09.out
