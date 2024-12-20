#!/bin/bash

# Check if the inputs are correct
if [ $# -ne 3 ]; then
    echo "Usage: $0 SPLIT_COLUMN TSV_FILE OUTPUT_DIR"
    exit 1
fi

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Get the input variables
SPLIT_COLUMN=$1
TSV_FILE=$2
OUTPUT_DIR=$3

# Column we are splitting on

# Check if the input file exists
if [ ! -f "$TSV_FILE" ]; then
    echo "Error: File '$TSV_FILE' not found."
    exit 1
fi

# Check if the output directory is a directory
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Error: '$OUTPUT_DIR' is not a directory."
    exit 1
fi

# Get the column index for the column of interest
COLUMN_INDEX=$(head -n 1 "$TSV_FILE" | tr '\t' '\n' | grep -nx "$SPLIT_COLUMN" | cut -d: -f1)

# Check if the column exists
if [[ -z $COLUMN_INDEX ]]; then
    echo "Error: Column '$SPLIT_COLUMN' not found in file!"
    exit 1
fi

echo "\"$SPLIT_COLUMN\" found in column $COLUMN_INDEX"

# Get the column values by extracting them all (based on COLUMN_INDEX),
# sorting and getting the unique values, and then printing them on a
# single and generating an array.
COLUMNS=( `awk -v col="$COLUMN_INDEX" -F '\t' 'NR > 1 { print $col }' $TSV_FILE | sort -u | awk '{printf("%s ",$0)}'` )

echo "Column values = ${COLUMNS[@]}"

# Create a file for each repertoire_id, with a header.
for COLUMN_VALUE in "${COLUMNS[@]}"; do
    echo "INFO: Creating ${OUTPUT_DIR}/${COLUMN_VALUE}"
    head -n 1 ${TSV_FILE} > ${OUTPUT_DIR}/${COLUMN_VALUE}
done

# Split the file into N files based on SPLIT_COLUMN.
# AWK is pretty efficient at this
awk -F '\t' -v tmpdir=${OUTPUT_DIR} -v column=${COLUMN_INDEX} '{if (NR>1) {print $0 >> tmpdir"/"$column}}' ${TSV_FILE}
if [ $? -ne 0 ]
then
    echo "ERROR: Could not split ${TSV_FILE} on field ${SPLIT_COLUMN}"
fi


