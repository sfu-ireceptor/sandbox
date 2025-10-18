#!/bin/bash

# Check if the input TSV file is provided as an argument
if [ $# -ne 2 ]; then
    echo "Usage: $0 RECEPTOR_FILE_REGEX RECEPTOR_FILE_PATH"
    exit 1
fi

receptor_file_regex=$1
receptor_file_path=$2

# Loop over all the files in the receptor file path
find "$receptor_file_path" -maxdepth 1 -type f | while read -r file; do
    # Extract base file name and the base file root (without the tsv)
    base_file=$(basename "$file")
    base_name=$(basename "$file" .tsv)
    # If the file name fits the regular expression, process it.
    if [[ $base_file =~ $receptor_file_regex ]]; then
	echo "$IR_SANDBOX/adc-search/run_receptor_reports_fast.sh ${receptor_file_path}/${base_name}.tsv repository-t1d-2.tsv repertoire-tr-contains-schema-rearrangement.json repertoire_fields.tsv $base_name > $base_name.out"
	$IR_SANDBOX/adc-search/run_receptor_reports_fast.sh ${receptor_file_path}/${base_name}.tsv repository-t1d-2.tsv repertoire-tr-contains-schema-rearrangement.json repertoire_fields.tsv $base_name > $base_name.out
    fi
done

