#!/bin/bash

# Check if we have an output file
if [ $# -ne 1 ]; then
    echo "Usage: $0 OUTPUT_FILE"
    exit 1
fi

# Check if the output file exists, if not create it.
output_file=$1
#if [ -f "$output_file" ]; then
#    echo "Error: Output file '$output_file' already exists."
#    exit 1
#fi

touch $output_file

# Intialize counts
total_rearrangements=0
total_repertoires=0
total_receptors=0

# Create some temporary files to hold repertoire info as we go.
repertoire_tmp_file=$(mktemp)
tmp_file=$(mktemp)

# Loop over the directories we found that contain valid receptor hits.
while IFS= read -r dir; do
    echo "Processing $dir"
    # Look up the IEDB recepetor
    receptor_string=$(basename $dir)
    IFS='_' read -r junction_aa v_gene j_gene <<< "$receptor_string"
    #echo $junction_aa 
    #echo $v_gene 
    #echo $j_gene 
    cdr3_aa="${junction_aa:1:-1}"
    #echo $cdr3_aa 
    #curl -s https://query-api.iedb.org/tcr_search?chain1_cdr3_seq=like.$junction_aa | \
		#jq -r 'if length > 0 then [.[] | [.receptor_group_iri] else empty end'
    #iedb_receptor_iri="$(curl -s https://query-api.iedb.org/tcr_search?chain2_cdr3_seq=like.*$cdr3_aa*| \
    #	jq 'if length > 0 then [.[] | .receptor_group_iri ] else empty end' | \
    #	tr -d '\n' | tr -d ' ')"
    #query_response_str=$(curl -s https://query-api.iedb.org/tcr_search?chain2_cdr3_seq=like.*$cdr3_aa*\&\&select=chain2_cdr3_seq,receptor_group_iri,curated_source_antigens,structure_iris,tcr_export\(chain_2__curated_v_gene,chain_2__curated_j_gene\) | jq -r 'if length > 0 then .[] | "\(.receptor_group_iri)\t\(.chain2_cdr3_seq)\t \(.tcr_export[0].chain_2__curated_v_gene)\t\(.tcr_export[0].chain_2__curated_j_gene)" else empty end')
    query_response_str=$(curl -s https://query-api.iedb.org/tcr_search?chain2_cdr3_seq=like.*$cdr3_aa*\&\&select=chain2_cdr3_seq,receptor_group_iri,curated_source_antigens,structure_iris,tcr_export\(chain_2__curated_v_gene,chain_2__curated_j_gene,chain_2__calculated_v_gene,chain_2__calculated_j_gene\) )
    #echo $query_response_str 
    iedb_receptor_iri=$(echo $query_response_str | \
        jq --arg v $v_gene --arg j $j_gene '[ .[] | select(.tcr_export[] | (if .chain_2__calculated_v_gene != null then .chain_2__calculated_v_gene else .chain_2__curated_v_gene end | split("*") | .[0] == $v) and (if .chain_2__calculated_j_gene != null then .chain_2__calculated_j_gene else .chain_2__curated_j_gene end | split("*") | .[0] == $j)) ] | [.[].receptor_group_iri ] | unique' | \
	tr -d '\n' | tr -d ' ')
    #echo $iedb_receptor_iri
    iedb_organism_iri="$(echo $query_response_str | \
        jq --arg v $v_gene --arg j $j_gene '[ .[] | select(.tcr_export[] | (if .chain_2__calculated_v_gene != null then .chain_2__calculated_v_gene else .chain_2__curated_v_gene end | split("*") | .[0] == $v) and (if .chain_2__calculated_j_gene != null then .chain_2__calculated_j_gene else .chain_2__curated_j_gene end | split("*") | .[0] == $j)) ] | [.[].curated_source_antigens[].source_organism_iri ] | unique' | \
        tr -d '\n' | tr -d ' ' )"
    #echo $iedb_organism_iri
    iedb_antigen_iri="$(echo $query_response_str | \
        jq --arg v $v_gene --arg j $j_gene '[ .[] | select(.tcr_export[] | (if .chain_2__calculated_v_gene != null then .chain_2__calculated_v_gene else .chain_2__curated_v_gene end | split("*") | .[0] == $v) and (if .chain_2__calculated_j_gene != null then .chain_2__calculated_j_gene else .chain_2__curated_j_gene end | split("*") | .[0] == $j)) ] | [.[].curated_source_antigens[].iri ] | unique' | \
        tr -d '\n' | tr -d ' ' )"
    #echo $iedb_antigen_iri
    iedb_epitope_iri="$(echo $query_response_str | \
        jq --arg v $v_gene --arg j $j_gene '[ .[] | select(.tcr_export[] | (if .chain_2__calculated_v_gene != null then .chain_2__calculated_v_gene else .chain_2__curated_v_gene end | split("*") | .[0] == $v) and (if .chain_2__calculated_j_gene != null then .chain_2__calculated_j_gene else .chain_2__curated_j_gene end | split("*") | .[0] == $j)) ] | [.[].structure_iris[] ] | unique' | \
        tr -d '\n' | tr -d ' ' )"
    #echo $iedb_epitope_iri
    #query_response_str=$(curl -s https://query-api.iedb.org/tcr_search?chain2_cdr3_seq=like.*$cdr3_aa*)
    #iedb_receptor_iri="$(echo $query_response_str | \
        #jq 'if length > 0 then [.[] | .receptor_group_iri] else empty end' | \
	#tr -d '\n' | tr -d ' ')"
    #iedb_antigen_info="$(echo $query_response_str | \
    #    jq 'if length > 0 then [.[] | .curated_source_antigens] else empty end' | \
    #    tr -d '\n' | tr -s ' ' )"
    #iedb_epitope_iri="$(echo $query_response_str | \
    #    jq 'if length > 0 then [.[] | .structure_iris] else empty end' | \
    #    tr -d '\n' | tr -s ' ' )"

    for file in $dir/rearrangement*.tsv; do
	echo "    Processing $(basename $file)"
	# Get the number of rearrangements (less the header)
	line_count=$(tail +2 $file | wc -l)

	# Get the column where the reperotire_id is stored.
	repertoire_column=$(awk -F'\t' -v label="repertoire_id" 'NR==1 {for (i=1; i<=NF; i++) if ($i == label) print i; exit}' $file)
	sequence_column=$(awk -F'\t' -v label="sequence_id" 'NR==1 {for (i=1; i<=NF; i++) if ($i == label) print i; exit}' $file)
	v_column=$(awk -F'\t' -v label="v_call" 'NR==1 {for (i=1; i<=NF; i++) if ($i == label) print i; exit}' $file)
	j_column=$(awk -F'\t' -v label="j_call" 'NR==1 {for (i=1; i<=NF; i++) if ($i == label) print i; exit}' $file)
	junction_column=$(awk -F'\t' -v label="junction_aa" 'NR==1 {for (i=1; i<=NF; i++) if ($i == label) print i; exit}' $file)
	
	# Extract the list of unique repertoires into a tmp file and count them 
	tail +2 $file | cut -f $repertoire_column | sort -u > $tmp_file
	repertoire_count=$(cat $tmp_file | wc -l)

	# Add these repertoires to the global list of repertoires.
	cat $tmp_file >> $repertoire_tmp_file

	# Generate the rearrangements annotated with epitope
	awk -F'\t' -v sequence_column=$sequence_column -v repertoire_column=$repertoire_column \
		-v v_column=$v_column -v j_column=$j_column -v junction_column=$junction_column \
		-v iedb_receptor_iri=$iedb_receptor_iri -v iedb_antigen_iri="$iedb_antigen_iri" \
		-v iedb_epitope_iri="$iedb_epitope_iri" -v iedb_organism_iri="$iedb_organism_iri"\
		'NR>1 {printf("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n",$sequence_column,$repertoire_column,$v_column,$j_column,$junction_column,iedb_receptor_iri,iedb_epitope_iri, iedb_antigen_iri, iedb_organism_iri);}' $file >> $output_file

	# Print out some reporting
	echo "        Number of Rearrangements with match for $(basename $dir) = $line_count"
	echo "        Number of Repertoires with match for $(basename $dir) = $repertoire_count"
	echo "        Receptor IRI = $iedb_receptor_iri"
	echo "        Epitope IRI = $iedb_epitope_iri"
	echo "        Antigen info = $iedb_antigen_iri"
	echo "        Organism info = $iedb_organism_iri"

	# Keep track of the totals
	total_repertoires=$((total_repertoires + repertoire_count))
	total_rearrangements=$((total_rearrangements + line_count))
	total_receptors=$((total_receptors + 1))
    done

# The directories we are interested in are not the misses. We traverse all other
# subdirectories (should be hits) and process any directory that starts with C
# which should be a receptor directory of the form CASLGGGYTF_TRBV19_TRBJ1-2
done < <(find  . -type d \( -name "misses" -prune \) -o -type d -name "C*" -print)

# Get the unique repertoires in our total repertoire file.
unique_repertoires=$(cat $repertoire_tmp_file | sort -u | wc -l)

# Print out a report.
echo "Total IEDB receptors = $total_receptors"
echo "Total ADC repertoire hits = $total_repertoires"
echo "Total ADC unique repertoires = $unique_repertoires"
echo "Total ADC rearrangements = $total_rearrangements"

# Remove the temporary files
rm $repertoire_tmp_file
rm $tmp_file

