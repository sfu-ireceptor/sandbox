# Perform initial receptor mapping
nohup bash run_ipa.sh > run_ipa-2025-01-14.out &

# Peform the mapping from TRB search output to a per sequence hit list
nohup bash $IR_SANDBOX/adc-search/hits-trb.sh hits-sequence-trb-2025-08-25-2025-10-18.tsv > hits-trb-2025-08-25-2025-10-18.out &

# Get the number of unique receptors in all *header* files in this
# nd sub-directories.
find . \( -type d \( -name "hits" -o -name "misses" -o -name "old" \) -prune \) -o -type f -name "*header*" -print | egrep "10-23" | xargs cat | grep TRB | cut -f 6 | jq -r '.[]' | sort -u > TRBReceptor.tsv
wc -l TRBReceptor.tsv
37810 TRBReceptor.tsv

# Count the SARAS-CoV2 specific sequences
egrep "NCBITaxon:2697049" hits-sequence-trb-2024-08-06-2025-10-23.tsv | wc -l
10902181

# Count the sequences that are specific to SARS-CoV2 and any other antigen
egrep "NCBITaxon:2697049\",|,\"NCBITaxon:2697049" hits-sequence-trb-2024-08-06-2025-10-23.tsv
1026983

# Get the Receptors that are SARS-CoV2 specific
egrep "NCBITaxon:2697049" hits-sequence-trb-2024-08-06-2025-10-23.tsv | grep TRB | cut -f 6 | jq -r '.[]' | sort -u > TRBReceptorCOVID.tsv
wc -l TRBReceptorCOVID.tsv
30371 TRBReceptorCOVID.tsv

# Get the Receptors that are SARS-CoV2 and multi-antigen specific
egrep "NCBITaxon:2697049\",|,\"NCBITaxon:2697049" hits-sequence-trb-2024-08-06-2025-10-23.tsv | grep TRB | cut -f 6 | jq -r '.[]' | sort -u > TRBReceptorCOVIDMulti.tsv
wc -l TRBReceptorCOVIDMulti.tsv
1112 TRBReceptorCOVIDMulti.tsv

# Get the Receptors that are not SARS-CoV2 specific
egrep -v "NCBITaxon:2697049" hits-sequence-trb-2024-08-06-2025-10-23.tsv | grep TRB | cut -f 6 | jq -r '.[]' | sort -u > TRBReceptorNoCOVID.tsv
wc -l TRBReceptorNoCOVID.tsv
7487 TRBReceptorNoCOVID.tsv



