#!/bin/bash

# Shell script that loops over directories produced by "receptor_report_fast.sh",
# looks up each receptor in IEDB, and produces a receptor/epitope pair file that
# can be loaded into an iReceptor database. TRA and TRB are different, so we need
# separate scripts.
#
# Traverses the directory tree and for every directory not named "misses" (this
# should leave only directories named "hits") it processes all of the directories
# with names of the form C* which should be a junction AA. Directories are of the
# form "CAISETGTDTQYF_TRBV10-3_TRBJ2-3" which represent the output for the ADC
# search for that receptor. Find command used to do this:
#    - find  . -type d \( -name "misses" -prune \) -o -type d -name "C*" -print

# Check if we have an output file
if [ $# -ne 1 ]; then
    echo "Usage: $0 OUTPUT_FILE"
    exit 1
fi

# Check if the output file exists, if not create it.
output_file=$1
if [ -f "$output_file" ]; then
    echo "Error: Output file '$output_file' already exists."
    exit 1
fi

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

    # Extract the junction V and J genes from the directory name
    receptor_string=$(basename $dir)
    IFS="_" read -r -a parts <<< "$receptor_string"
    # first element
    junction_aa="${parts[0]}"
    # last element
    j_gene="${parts[-1]}"
    # everything in between, joined with "_"
    v_gene=$(IFS="/"; echo "${parts[*]:1:${#parts[@]}-2}")
    #IFS='_' read -r junction_aa v_gene j_gene <<< "$receptor_string"

    # Compute the CDR3 as IEDB sometimes has this only
    cdr3_aa="${junction_aa:1:-1}"

    # Generate the query response for the CDR3. We need the V and J genes so
    # that we can make sure we have an exact match in IEDB.
    query_response_str=$(curl -s https://query-api.iedb.org/tcr_search?chain1_cdr3_seq=like.*$cdr3_aa*\&\&select=chain1_cdr3_seq,receptor_group_iri,curated_source_antigens,parent_source_antigen_iris,structure_iris,mhc_allele_iris,mhc_allele_names,tcr_export\(chain_1__curated_v_gene,chain_1__curated_j_gene,chain_1__calculated_v_gene,chain_1__calculated_j_gene\) )

    # Get the list of Receptor IRIs. We check both calculated and curated genes 
    # to make sure we find all matches.
    iedb_receptor_iri=$(echo $query_response_str | \
	    jq --arg v $v_gene --arg j $j_gene --arg cdr3_aa $cdr3_aa --arg junction_aa $junction_aa '[ .[] | select( (.chain1_cdr3_seq == $cdr3_aa or .chain1_cdr3_seq == $junction_aa) and (.tcr_export[] | (if .chain_1__calculated_v_gene != null then .chain_1__calculated_v_gene else .chain_1__curated_v_gene end // "" | split("*") | .[0] == $v) and (if .chain_1__calculated_j_gene != null then .chain_1__calculated_j_gene else .chain_1__curated_j_gene end // "" | split("*") | .[0] == $j))) ] | [.[].receptor_group_iri ] | unique' | \
	tr -d '\n' | tr -d ' ')

    # Get the list of Organism IRIs. We check both calculated and curated genes 
    # to make sure we find all matches.
    iedb_organism_iri="$(echo $query_response_str | \
	    jq --arg v $v_gene --arg j $j_gene --arg cdr3_aa $cdr3_aa --arg junction_aa $junction_aa '[ .[] | select((.chain1_cdr3_seq == $cdr3_aa or .chain1_cdr3_seq == $junction_aa) and (.tcr_export[] | (if .chain_1__calculated_v_gene != null then .chain_1__calculated_v_gene else .chain_1__curated_v_gene end // "" | split("*") | .[0] == $v) and (if .chain_1__calculated_j_gene != null then .chain_1__calculated_j_gene else .chain_1__curated_j_gene end // "" | split("*") | .[0] == $j))) ] | [.[].curated_source_antigens // [] | .[].source_organism_iri ] | unique' | \
        tr -d '\n' | tr -d ' ' )"

    # Get the list of Antigen IRIs. We check both calculated and curated genes 
    # to make sure we find all matches.
    iedb_antigen_iri="$(echo $query_response_str | \
	    jq --arg v $v_gene --arg j $j_gene --arg cdr3_aa $cdr3_aa --arg junction_aa $junction_aa '[ .[] | select((.chain1_cdr3_seq == $cdr3_aa or .chain1_cdr3_seq == $junction_aa) and (.tcr_export[] | (if .chain_1__calculated_v_gene != null then .chain_1__calculated_v_gene else .chain_1__curated_v_gene end // "" | split("*") | .[0] == $v) and (if .chain_1__calculated_j_gene != null then .chain_1__calculated_j_gene else .chain_1__curated_j_gene end // "" | split("*") | .[0] == $j))) ] | [.[].parent_source_antigen_iris // [] | .[]] | unique' | \
        tr -d '\n' | tr -d ' ' )"

    # Get the list of Eptiope IRIs. We check both calculated and curated genes 
    # to make sure we find all matches.
    iedb_epitope_iri="$(echo $query_response_str | \
	    jq --arg v $v_gene --arg j $j_gene --arg cdr3_aa $cdr3_aa --arg junction_aa $junction_aa '[ .[] | select((.chain1_cdr3_seq == $cdr3_aa or .chain1_cdr3_seq == $junction_aa) and (.tcr_export[] | (if .chain_1__calculated_v_gene != null then .chain_1__calculated_v_gene else .chain_1__curated_v_gene end // "" | split("*") | .[0] == $v) and (if .chain_1__calculated_j_gene != null then .chain_1__calculated_j_gene else .chain_1__curated_j_gene end // "" | split("*") | .[0] == $j))) ] | [.[].structure_iris[] ] | unique' | \
        tr -d '\n' | tr -d ' ' )"

    # Get the list of HLA IRIs. We check both calculated and curated genes 
    # to make sure we find all matches.
    iedb_hla_iri="$(echo $query_response_str | \
	    jq --arg v $v_gene --arg j $j_gene --arg cdr3_aa $cdr3_aa --arg junction_aa $junction_aa '[ .[] | select((.chain1_cdr3_seq == $cdr3_aa or .chain1_cdr3_seq == $junction_aa) and (.tcr_export[] | (if .chain_1__calculated_v_gene != null then .chain_1__calculated_v_gene else .chain_1__curated_v_gene end // "" | split("*") | .[0] == $v) and (if .chain_1__calculated_j_gene != null then .chain_1__calculated_j_gene else .chain_1__curated_j_gene end // "" | split("*") | .[0] == $j))) ] | [.[].mhc_allele_iris[] ] | unique' | \
        tr -d '\n' | tr -d ' ' )"

    # Get the list of HLA names. We check both calculated and curated genes 
    # to make sure we find all matches.
    iedb_hla_name="$(echo $query_response_str | \
	    jq --arg v $v_gene --arg j $j_gene --arg cdr3_aa $cdr3_aa --arg junction_aa $junction_aa '[ .[] | select((.chain1_cdr3_seq == $cdr3_aa or .chain1_cdr3_seq == $junction_aa) and (.tcr_export[] | (if .chain_1__calculated_v_gene != null then .chain_1__calculated_v_gene else .chain_1__curated_v_gene end // "" | split("*") | .[0] == $v) and (if .chain_1__calculated_j_gene != null then .chain_1__calculated_j_gene else .chain_1__curated_j_gene end // "" | split("*") | .[0] == $j))) ] | [.[].mhc_allele_names[] ] | unique' | \
        tr -d '\n' | tr -d ' ' )"

    # For each rearrangement file in the directory, process it. Recall that
    # it is possible to have more than one rearrangement file as we may span
    # multiple repositories.
    for file in $dir/rearrangement*.tsv; do
	echo "    Processing $(basename $file)"
	# Get the repository from the file name. Filenames are of the form:
	# rearrangement-t1d-1.ireceptor.org-CASESSGANVLTF_TRBV19_TRBJ2-6.tsv
	repository=$(echo ${file} |  grep -oP '(?<=rearrangement-)[^.]+\.[^.]+\.[a-zA-Z]{2,}')
	echo "        Repository = $repository"

	# Get the number of rearrangements (less the header)
	line_count=$(tail +2 $file | wc -l)

	# Get the column where the reperotire_id is stored.
	repertoire_column=$(awk -F'\t' -v label="repertoire_id" 'NR==1 {for (i=1; i<=NF; i++) if ($i == label) print i; exit}' $file)
	sequence_column=$(awk -F'\t' -v label="sequence_id" 'NR==1 {for (i=1; i<=NF; i++) if ($i == label) print i; exit}' $file)
	v_column=$(awk -F'\t' -v label="v_gene" 'NR==1 {for (i=1; i<=NF; i++) if ($i == label) print i; exit}' $file)
	j_column=$(awk -F'\t' -v label="j_gene" 'NR==1 {for (i=1; i<=NF; i++) if ($i == label) print i; exit}' $file)
	junction_column=$(awk -F'\t' -v label="junction_aa" 'NR==1 {for (i=1; i<=NF; i++) if ($i == label) print i; exit}' $file)
	
	# Extract the list of unique repertoires into a tmp file and count them 
	tail +2 $file | cut -f $repertoire_column | sort -u > $tmp_file
	repertoire_count=$(cat $tmp_file | wc -l)

	# Add these repertoires to the global list of repertoires.
	cat $tmp_file >> $repertoire_tmp_file

	# Generate the rearrangements annotated with receptor, epitope, antigen, and organism
	awk -F'\t' -v sequence_column=$sequence_column -v repertoire_column=$repertoire_column \
		-v v_column=$v_column -v j_column=$j_column -v junction_column=$junction_column \
		-v iedb_receptor_iri=$iedb_receptor_iri -v iedb_antigen_iri="$iedb_antigen_iri" \
		-v iedb_epitope_iri="$iedb_epitope_iri" -v iedb_organism_iri="$iedb_organism_iri"\
		-v iedb_hla_iri="$iedb_hla_iri" -v iedb_hla_name="$iedb_hla_name"\
		-v repository="$repository" \
		'NR>1 {printf("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n",$sequence_column,$repertoire_column,$v_column,$j_column,$junction_column,iedb_receptor_iri,iedb_epitope_iri, iedb_antigen_iri, iedb_organism_iri, iedb_hla_iri, iedb_hla_name, repository);}' $file >> $output_file

	# Print out some reporting
        echo "        Receptor info = $junction_aa $v_gene $j_gene"
        echo "        Searching for $cdr3_aa"
	echo "        Number of Rearrangements with match for $(basename $dir) = $line_count"
	echo "        Number of Repertoires with match for $(basename $dir) = $repertoire_count"
	echo "        Receptor IRI = $iedb_receptor_iri"
	echo "        Epitope IRI = $iedb_epitope_iri"
	echo "        Antigen IRI = $iedb_antigen_iri"
	echo "        Organism IRI = $iedb_organism_iri"
	echo "        HLA IRI = $iedb_hla_iri"
        echo "        HLA name = $iedb_hla_name"


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

