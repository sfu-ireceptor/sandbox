#!/bin/bash


# Check if a file is provided as an argument
if [ $# -lt 6 ]; then
    echo "Usage: $0 REPOSITORY_TSV REPERTOIRE_QUERY_JSON REPERTOIRE_FIELD_TSV JUNCTION VGENE JGENE"
    exit 1
fi

# Get the files to use
REPOSITORY_TSV=$1
REPERTOIRE_QUERY_JSON=$2
REPERTOIRE_FIELD_TSV=$3

# Expect parameters JUNCTION, V Gene, J Gene, and Epitope (optional)
# E.g. CASSLQSSYNSPLHF TRBV11-2 TRBJ1-6 QKRGIVEQCCTSICS
JUNCTION=$4
VGENE=$5
JGENE=$6

# Sometimes we need the CDR3, so compute it if from the Junction
CDR3=${JUNCTION:1:-1}

# Store in the output directory named for the JUNCTION
if [ $# -eq 6 ]; then
  OUTPUT_DIR="${JUNCTION}_${VGENE}_${JGENE}"
else
  EPITOPE=$7
  OUTPUT_DIR="${JUNCTION}_${VGENE}_${JGENE}_${EPITOPE}"
fi
REPORT_FILE=$OUTPUT_DIR/report.out

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p $OUTPUT_DIR
JSON_QUERY_FILE=$OUTPUT_DIR/$JUNCTION.json

echo "Performing search for $1 $2 $3 $4" > $REPORT_FILE
echo -n "Starting query at: " >> $REPORT_FILE
date >> $REPORT_FILE

# Generate the filter to search for the Receptor

echo '{ "filters": { "op" : "and", "content" : [' > $JSON_QUERY_FILE
echo "{ \"op\":\"=\", \"content\": { \"field\":\"junction_aa\", \"value\":\"${JUNCTION}\"}}," >> $JSON_QUERY_FILE
echo "{ \"op\":\"=\", \"content\": { \"field\":\"v_gene\", \"value\":\"${VGENE}\"}}," >> $JSON_QUERY_FILE
echo "{ \"op\":\"=\", \"content\": { \"field\":\"j_gene\", \"value\":\"${JGENE}\"}}" >> $JSON_QUERY_FILE
echo '] }, "facets":"repertoire_id"}' >> $JSON_QUERY_FILE

# Search the ADC for instances of said receptor

python3 ${SCRIPT_DIR}/adc-search.py ${REPOSITORY_TSV} ${REPERTOIRE_QUERY_JSON} $JSON_QUERY_FILE --service_delay=0.2 --output_file=$OUTPUT_DIR/count-$JUNCTION.json --field_file=${REPERTOIRE_FIELD_TSV} --verbose > $OUTPUT_DIR/count-$JUNCTION.out
echo -n "Done count at: " >> $REPORT_FILE
date >> $REPORT_FILE

# Generate a report for the repertoires where the receptor was found

COUNT=`cat $OUTPUT_DIR/count-$JUNCTION.json | jq '[.[].results[].Facet[].count]| add | if . > 0 then . else 0 end'`
REPERTOIRES=`cat $OUTPUT_DIR/count-$JUNCTION.json | jq ' [.[].results[].Facet[].count]| length'`

echo "" >> $REPORT_FILE
echo "The Receptor $JUNCTION/$VGENE/$JGENE was found $COUNT times in the ADC" >> $REPORT_FILE
echo "The Receptor $JUNCTION/$VGENE/$JGENE was found in $REPERTOIRES repertoires" >> $REPORT_FILE
echo "ADC Summary,$JUNCTION/$VGENE/$JGENE,$COUNT,$REPERTOIRES" >> $REPORT_FILE
echo "" >> $REPORT_FILE

if [ $COUNT -gt 0 ]; then
    # Generate the filter to download the receptor chain

    echo '{ "filters": { "op" : "and", "content" : [' > $JSON_QUERY_FILE
    echo "{ \"op\":\"=\", \"content\": { \"field\":\"junction_aa\", \"value\":\"${JUNCTION}\"}}," >> $JSON_QUERY_FILE
    echo "{ \"op\":\"=\", \"content\": { \"field\":\"v_gene\", \"value\":\"${VGENE}\"}}," >> $JSON_QUERY_FILE
    echo "{ \"op\":\"=\", \"content\": { \"field\":\"j_gene\", \"value\":\"${JGENE}\"}}" >> $JSON_QUERY_FILE
    echo '] }, "format":"tsv"}' >> $JSON_QUERY_FILE

    # Download the sequences for the receptor

    python3 ${SCRIPT_DIR}/adc-search.py --verbose --service_delay=0.2 ${REPOSITORY_TSV} ${REPERTOIRE_QUERY_JSON} $JSON_QUERY_FILE --output_format=TSV --output_file=$OUTPUT_DIR/download-$JUNCTION.tsv --output_dir=${OUTPUT_DIR}/ --field_file=${REPERTOIRE_FIELD_TSV} > $OUTPUT_DIR/download-$JUNCTION.out
    echo -n "Done download at: " >> $REPORT_FILE
    date >> $REPORT_FILE
fi

echo -n "Done query at: " >> $REPORT_FILE
date >> $REPORT_FILE
