#!/bin/bash

# Counts the number of times each CDR3 (from column 1 in RECEPTOR_TSV)
# occurs in the ADC repository TSV file, and outputs a report per
# CDR3 in OUTPUT_DIR. The output is a JSON object with a key per
# repository and the value an array, one element per repertoire 
# where the CDR3 wsa found. Each element in the array is a JSON 
# object that contains the repertoire_id and the count of the number
# of times it was found. For example the file CASSLQSSYNSPLHF.json:
# { "https://covid19-1.ireceptor.org":
# [ 
#    { "repertoire_id": "5efbc72d5f94cb6215deecee", "count": 3 }
# ]
# }
# indicates that the CDR3 "CASSLQSSYNSPLHF" was found three times in
# repertoire_id "5efbc72d5f94cb6215deecee" in repository
# "https://covid19-1.ireceptor.org"
# A total count of the number of times a given CDR3 was found can be
# acquired with the following command:
#   cat CASSLQSSYNSPLHF.json | jq '[.[] | .[] | .count ] | add'  
# Which flattens the repository and repertoire lists, creates an array
# of just the counts, and then adds them all up.

# Check if the input TSV file is provided as an argument
if [ $# -ne 3 ]; then
    echo "Usage: $0 RECEPTOR_TSV REPOSITORY_TSV OUTPUT_DIR"
    exit 1
fi

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RECEPTOR_TSV=$1
REPOSITORY_TSV=$2
OUTPUT_DIR=$3

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

# Get a temp file for generated query.
rearrangement_query=$(mktemp)

# Read the CDR3 TSV file line by line and iterate over the cdr3s
while IFS=$'\t' read -r cdr3 therest; do
    echo -n "Running report for $cdr3 at "
    date
    echo "{" > $OUTPUT_DIR/$cdr3.json
    first_time=true
    # Read the repository TSV file line by line and iterate over the repositories
    tail -n +2 $REPOSITORY_TSV | while IFS=$'\t' read -r repository therest; do

        # Report and diagnostic output
        echo -n "Running report for $repository at "
        date
        echo "" >> $OUTPUT_DIR/$SUMMARY_FILE
        echo -n "Running report for $cdr3 at " >> $OUTPUT_DIR/$SUMMARY_FILE
        date >> $OUTPUT_DIR/$SUMMARY_FILE

	# Generate the JSON key for the facet output, the repository name.
	# We need to comma separate all but the first object in the list
	if $first_time; then
            first_time=false
        else
	    echo "," >> $OUTPUT_DIR/$cdr3.json
        fi
	echo "\"$repository\":" >> $OUTPUT_DIR/$cdr3.json

	# Generate the facet query for the CDR3
        echo "{ \"filters\": {\"op\":\"=\", \"content\": { \"field\":\"junction_aa\", \"value\":\"$cdr3\"}},\"facets\":\"repertoire_id\"}" > $rearrangement_query
	# Perform the query. Extrace the Facet element using jq and append it to the file.
        curl -k -s -H 'content-type: application/json' -d @$rearrangement_query $repository/airr/v1/rearrangement | jq '.Facet' >> $OUTPUT_DIR/$cdr3.json 

    done 
    echo "}" >> $OUTPUT_DIR/$cdr3.json
done < "$RECEPTOR_TSV"

# Clean up the tmp file.
rm $rearrangement_query

echo -n "Finished processing at "
date

echo "" >> $OUTPUT_DIR/$SUMMARY_FILE
echo -n "Report finished at: " >> $OUTPUT_DIR/$SUMMARY_FILE
date >> $OUTPUT_DIR/$SUMMARY_FILE
