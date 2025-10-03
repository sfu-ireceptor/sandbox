#!/bin/bash

# Check if the input TSV file is provided as an argument
if [ $# -ne 2 ]; then
    echo "Usage: $0 RECEPTOR_FILE_REGEX RECEPTOR_FILE_PATH"
    exit 1
fi

receptor_file_regex=$1
receptor_file_path=$2

#for file in ${receptor_file_path}/${receptor_file_regex} ; do
find "$receptor_file_path" -maxdepth 1 -type f | while read -r file; do
    base_file=$(basename "$file")
    base_name=$(basename "$file" .tsv)
    #echo $file
    #echo $base_file
    #echo $base_name
    if [[ $base_file =~ $receptor_file_regex ]]; then
	echo "../../run_receptor_reports_fast.sh ${receptor_file_path}/${base_name}.tsv repository-t1d-1.tsv repertoire-trb-contains-schema-rearrangement.json repertoire_fields.tsv $base_name > $base_name.out"
	../../run_receptor_reports_fast.sh ${receptor_file_path}/${base_name}.tsv repository-t1d-1.tsv repertoire-tr-contains-schema-rearrangement.json repertoire_fields.tsv $base_name > $base_name.out
	#../../run_receptor_reports_fast.sh ../../receptor/2024-08-06/iedb_tcr_$base_str.tsv repository-t1d-1.tsv repertoire-trb-contains-schema-rearrangement.json repertoire_fields.tsv $base_str > $base_str.out
    fi
done

