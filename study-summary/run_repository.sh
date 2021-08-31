#!/bin/bash

SCRIPT_DIR=`dirname "$0"`

# check number of arguments
NB_ARGS=3
if [ $# -lt $NB_ARGS ];
then
    echo "$0: wrong number of arguments ($# instead of $NB_ARGS)"
    echo "usage: $0 REPERTOIRE_URL AIRR_FIELD QUERY_FILE [--json_output|--html_output|--irplus_output]"
    exit 1
fi

REPERTOIRE_URL=$1
AIRR_FIELD=$2
QUERY_FILE=$3

if [ $# -eq 3 ];
then
	OUTPUT_TYPE="--json_output"
else
	OUTPUT_TYPE=$4
fi

echo "Running study summary for ${REPERTOIRE_URL}"

./get_repertoire_field.sh ${REPERTOIRE_URL} ${AIRR_FIELD} ${QUERY_FILE} > /tmp/studies.tsv

python3 ./ADC-study-summary.py ${REPERTOIRE_URL} /tmp/studies.tsv ${AIRR_FIELD} ${OUTPUT_TYPE}


