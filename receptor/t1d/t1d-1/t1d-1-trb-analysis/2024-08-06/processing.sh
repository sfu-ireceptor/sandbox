# Run the IEDB receptor search (TAKES A VERY LONG TIME - DAYS)
nohup bash run-t1d-1.sh > t1d-1-2024-12-08.out

# Annotate each sequence in the analysis with its epitope (TAKES A WHILE - HOURS)
nohup bash $IR_SANDBOX/adc-search/hits-trb.sh hits-sequence-trb-2024-08-06-2025-10-09.tsv > hits-trb-2024-08-06-2025-10-09.out

head -1 hits-sequence-trb-header-2024-08-06-2025-10-02.tsv > hits-sequence-trb-header-2024-08-06-2025-10-09.tsv
cat hits-sequence-trb-2024-08-06-2025-10-09.tsv >> hits-sequence-trb-header-2024-08-06-2025-10-09.tsv
wc -l hits-sequence-trb-*2024*.tsv
   621229 hits-sequence-trb-2024-08-06-2025-10-02.tsv
   621229 hits-sequence-trb-2024-08-06-2025-10-09.tsv
   621230 hits-sequence-trb-header-2024-08-06-2025-10-02.tsv
   621230 hits-sequence-trb-header-2024-08-06-2025-10-09.tsv

# Extract the unique receptors, epitopes, antigens, and organisms
bash ../../../unique_extract.sh hits-sequence-2025-06-30.tsv 6 > receptors-2025-06-30.tsv
bash ../../../unique_extract.sh hits-sequence-2025-06-30.tsv 7 > epitopes-2025-06-30.tsv
bash ../../../unique_extract.sh hits-sequence-2025-06-30.tsv 8 > antigens-2025-06-30.tsv
bash ../../../unique_extract.sh hits-sequence-2025-06-30.tsv 9 > organisms-2025-06-30.tsv

# Extract the repertoire IDs from the Seay study across different conditions
curl -s -d @Seay-TRB-Healthy.json https://t1d-1.ireceptor.org/airr/v1/repertoire | jq -r '.Repertoire[].repertoire_id' > Seay-TRB-Healthy-Repertoire.tsv
curl -s -d @Seay-TRB-T1D.json https://t1d-1.ireceptor.org/airr/v1/repertoire | jq -r '.Repertoire[].repertoire_id' > Seay-TRB-T1D-Repertoire.tsv
curl -s -d @Seay-TRB-T2D.json https://t1d-1.ireceptor.org/airr/v1/repertoire | jq -r '.Repertoire[].repertoire_id' > Seay-TRB-T2D-Repertoire.tsv
curl -s -d @Seay-TRB-DM.json https://t1d-1.ireceptor.org/airr/v1/repertoire | jq -r '.Repertoire[].repertoire_id' > Seay-TRB-DM-Repertoire.tsv

# Extract the sequences from the Seay study across different conditions
grep -f Seay-TRB-DM-Repertoire.tsv hits-sequence-2025-02-18.tsv > hits-Seay-TRB-DM-2025-02-18.tsv
grep -f Seay-TRB-Healthy-Repertoire.tsv hits-sequence-2025-02-18.tsv > hits-Seay-TRB-Healthy-2025-02-18.tsv
grep -f Seay-TRB-T2D-Repertoire.tsv hits-sequence-2025-02-18.tsv > hits-Seay-TRB-T2D-2025-02-18.tsv
grep -f Seay-TRB-T1D-Repertoire.tsv hits-sequence-2025-02-18.tsv > hits-Seay-TRB-T1D-2025-02-18.tsv

# Could the receptor, epitope, antigen, and species values across conditions
bash unique_extract.sh hits-Seay-TRB-DM-2025-02-18.tsv 6 | wc -l
bash unique_extract.sh hits-Seay-TRB-DM-2025-02-18.tsv 7 | wc -l
bash unique_extract.sh hits-Seay-TRB-DM-2025-02-18.tsv 8 | wc -l
bash unique_extract.sh hits-Seay-TRB-DM-2025-02-18.tsv 9 | wc -l

bash unique_extract.sh hits-Seay-TRB-T1D-2025-02-18.tsv 6 | wc -l
bash unique_extract.sh hits-Seay-TRB-T1D-2025-02-18.tsv 7 | wc -l
bash unique_extract.sh hits-Seay-TRB-T1D-2025-02-18.tsv 8 | wc -l
bash unique_extract.sh hits-Seay-TRB-T1D-2025-02-18.tsv 9 | wc -l

bash unique_extract.sh hits-Seay-TRB-T2D-2025-02-18.tsv 6 | wc -l
bash unique_extract.sh hits-Seay-TRB-T2D-2025-02-18.tsv 7 | wc -l
bash unique_extract.sh hits-Seay-TRB-T2D-2025-02-18.tsv 8 | wc -l
bash unique_extract.sh hits-Seay-TRB-T2D-2025-02-18.tsv 9 | wc -l

bash unique_extract.sh hits-Seay-TRB-Healthy-2025-02-18.tsv 6 | wc -l
bash unique_extract.sh hits-Seay-TRB-Healthy-2025-02-18.tsv 7 | wc -l
bash unique_extract.sh hits-Seay-TRB-Healthy-2025-02-18.tsv 8 | wc -l
bash unique_extract.sh hits-Seay-TRB-Healthy-2025-02-18.tsv 9 | wc -l

