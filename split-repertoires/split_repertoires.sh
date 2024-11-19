#!/bin/bash

# Check if the inputs are correct
if [ $# -ne 2 ]; then
    echo "Usage: $0 REARRANGEMENT_FILE OUTPUT_DIR"
    exit 1
fi

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Get the input variables
REARRANGEMENT_FILE=$1
OUTPUT_DIR=$2

# Column we are splitting on
COLUMN_NAME="repertoire_id"

# Check if the input file exists
if [ ! -f "$REARRANGEMENT_FILE" ]; then
    echo "Error: File '$REARRANGEMENT_FILE' not found."
    exit 1
fi

# Check if the output directory is a directory
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Error: '$OUTPUT_DIR' is not a directory."
    exit 1
fi

# Get the column index for the column of interest
COLUMN_INDEX=$(head -n 1 "$REARRANGEMENT_FILE" | tr '\t' '\n' | grep -nx "$COLUMN_NAME" | cut -d: -f1)

# Check if the column exists
if [[ -z $COLUMN_INDEX ]]; then
    echo "Error: Column '$COLUMN_NAME' not found in file!"
    exit 1
fi

echo "Column = $COLUMN_INDEX"

# Get the repertoires by extracting them all (based on COLUMN_INDEX), sorting and getting the unique
# values, and then printing them on a single and generating an array.
REPERTOIRES=( `awk -v col="$COLUMN_INDEX" -F '\t' 'NR > 1 { print $col }' $REARRANGEMENT_FILE | sort -u | awk '{printf("%s ",$0)}'` )

echo "Repertoires = $REPERTOIRES"

# Create a file for each repertoire_id, with a header.
for REPERTOIRE_ID in "${REPERTOIRES[@]}"; do
    echo "INFO: Creating ${OUTPUT_DIR}/${REPERTOIRE_ID}.tsv"
    head -n 1 ${REARRANGEMENT_FILE} > ${OUTPUT_DIR}/${REPERTOIRE_ID}.tsv
done

# Split the file into N files based on SPLIT_FIELD.
# AWK is pretty efficient at this
awk -F '\t' -v tmpdir=${OUTPUT_DIR} -v column=${COLUMN_INDEX} '{if (NR>1) {print $0 >> tmpdir"/"$column".tsv"}}' ${REARRANGEMENT_FILE}
if [ $? -ne 0 ]
then
    echo "ERROR: Could not split ${data_file} on field ${SPLIT_FIELD}"
fi


