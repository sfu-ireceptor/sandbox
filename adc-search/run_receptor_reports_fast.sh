#!/bin/bash

# Check if the input TSV file is provided as an argument
if [ $# -ne 5 ]; then
    echo "Usage: $0 RECEPTOR_TSV REPOSITORY_TSV REPERTOIRE_QUERY_JSON REPERTOIRE_FIELD_TSV OUTPUT_DIR"
    exit 1
fi

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RECEPTOR_TSV=$1
REPOSITORY_TSV=$2
REPERTOIRE_QUERY_JSON=$3
REPERTOIRE_FIELD_TSV=$4
OUTPUT_DIR=$5

# Check if the output directory exists
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Error: '$OUTPUT_DIR' is not a directory."
    exit 1
fi

# Generate a summary file
DATE_STRING=`date --iso-8601=seconds`
SUMMARY_FILE="Summary_${DATE_STRING}.out"

# Output some header information
echo "Receptor file = $RECEPTOR_TSV" > $OUTPUT_DIR/$SUMMARY_FILE
echo "Repository file = $REPOSITORY_TSV" >> $OUTPUT_DIR/$SUMMARY_FILE
echo "Repertoire query file = $REPERTOIRE_QUERY_JSON" >> $OUTPUT_DIR/$SUMMARY_FILE
echo "Repertoire fields file = $REPERTOIRE_FIELD_TSV" >> $OUTPUT_DIR/$SUMMARY_FILE
echo -n "Report run at: " >> $OUTPUT_DIR/$SUMMARY_FILE
date >> $OUTPUT_DIR/$SUMMARY_FILE
echo "" >> $OUTPUT_DIR/$SUMMARY_FILE

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
    
    echo "" >> $OUTPUT_DIR/$SUMMARY_FILE
    echo -n "Running report for $cdr3 $vgene $jgene at " >> $OUTPUT_DIR/$SUMMARY_FILE
    date >> $OUTPUT_DIR/$SUMMARY_FILE

    ${SCRIPT_DIR}/receptor_report_fast.sh "$REPOSITORY_TSV" "$REPERTOIRE_QUERY_JSON" "$REPERTOIRE_FIELD_TSV" "$cdr3" "$vgene" "$jgene" "$OUTPUT_DIR" "$SUMMARY_FILE"
done < "$RECEPTOR_TSV"

echo -n "Finished processing at "
date

echo "" >> $OUTPUT_DIR/$SUMMARY_FILE
echo -n "Report finished at: " >> $OUTPUT_DIR/$SUMMARY_FILE
date >> $OUTPUT_DIR/$SUMMARY_FILE
