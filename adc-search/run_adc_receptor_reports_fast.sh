#!/bin/bash

# Check if the input TSV file is provided as an argument
if [ $# -ne 4 ]; then
    echo "Usage: $0 RECEPTOR_TSV REPOSITORY_TSV REPERTOIRE_QUERY_JSON REPERTOIRE_FIELD_TSV"
    exit 1
fi

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RECEPTOR_TSV=$1
REPOSITORY_TSV=$2
REPERTOIRE_QUERY_JSON=$3
REPERTOIRE_FIELD_TSV=$4

# Check if the input file exists
if [ ! -f "$RECEPTOR_TSV" ]; then
    echo "Error: File '$RECEPTOR_TSV' not found."
    exit 1
fi
# Check if the input file exists
if [ ! -f "$REPOSITORY_TSV" ]; then
    echo "Error: File '$REPOSITORY_TSV' not found."
    exit 1
fi
# Check if the input file exists
if [ ! -f "$REPERTOIRE_QUERY_JSON" ]; then
    echo "Error: File '$REPERTOIRE_QUERY_JSON' not found."
    exit 1
fi
# Check if the input file exists
if [ ! -f "$REPERTOIRE_FIELD_TSV" ]; then
    echo "Error: File '$REPERTOIRE_FIELD_TSV' not found."
    exit 1
fi

# Read the TSV file line by line and get the four columns
while IFS=$'\t' read -r cdr3 vgene jgene; do
    # Call the receptor_report script with the four column values
    # as parameters to generate a report for each receptor
    echo -n "Running report for $cdr3 $vgene $jgene at "
    date
    ${SCRIPT_DIR}/receptor_report_fast.sh "$REPOSITORY_TSV" "$REPERTOIRE_QUERY_JSON" "$REPERTOIRE_FIELD_TSV" "$cdr3" "$vgene" "$jgene" 
done < "$RECEPTOR_TSV"
echo -n "Finished processing at "
date
