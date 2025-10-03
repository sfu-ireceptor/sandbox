# Run the IEDB receptor search (TAKES A VERY LONG TIME - DAYS)
nohup bash run_t1d-2_tra.sh > run_t1d-2_tra-2025-07-11.out

# Annotate each sequence in the analysis with its epitope (TAKES A WHILE - HOURS)
#nohup bash ../../../hits-tra.sh hits-tra-sequence-2025-08-21.tsv > hits-tra-sequence-2025-08-21.out &
nohup bash $IR_SANDBOX/adc-search/hits-tra.sh hits-sequence-tra-2025-07-11-2025-10-02.tsv > hits-tra-2025-07-11-2025-10-02.out &
head -1 ../../t1d-1-trb-analysis/2024-08-06/hits-sequence-trb-header-2024-08-06-2025-10-02.tsv > hits-sequence-tra-header-2025-07-11-2025-10-02.tsv
cat hits-sequence-tra-2025-07-11-2025-10-02.tsv >> hits-sequence-tra-header-2025-07-11-2025-10-02.tsv
wc -l hits-sequence-tra-header-2025-07-11-2025-10-02.tsv
#170 hits-sequence-tra-header-2025-07-11-2025-10-02.tsv


# Extract the unique receptors, epitopes, antigens, and organisms
bash $IR_SANDBOX/adc-search/unique_extract.sh hits-sequence-tra-2025-07-11-2025-10-02.tsv 6 > receptors-2025-10-02.tsv
bash $IR_SANDBOX/adc-search/unique_extract.sh hits-sequence-tra-2025-07-11-2025-10-02.tsv 7 > epitopes-2025-10-02.out
bash $IR_SANDBOX/adc-search/unique_extract.sh hits-sequence-tra-2025-07-11-2025-10-02.tsv 8 > antigens-2025-10-02.out
bash $IR_SANDBOX/adc-search/unique_extract.sh hits-sequence-tra-2025-07-11-2025-10-02.tsv 9 > organsims-2025-10-02.out
bash $IR_SANDBOX/adc-search/unique_extract.sh hits-sequence-tra-2025-07-11-2025-10-02.tsv 10 > mhc-2025-10-02.out
wc -l *2025-10*.out
#   23 antigens-2025-10-02.out
#   86 epitopes-2025-10-02.out
#   33 mhc-2025-10-02.out
#   11 organsims-2025-10-02.out
#  177 receptors-2025-10-02.out

