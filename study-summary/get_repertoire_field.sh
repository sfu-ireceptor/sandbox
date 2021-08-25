#!/bin/bash

SCRIPT_DIR=`dirname "$0"`

# check number of arguments
NB_ARGS=3
if [ $# -ne $NB_ARGS ];
then
    echo "$0: wrong number of arguments ($# instead of $NB_ARGS)"
    echo "usage: $0 REPERTOIRE_URL AIRR_FIELD QUERY_FILE"
    exit 1
fi


curl -k -s --data @$3 $1 | python3 -m json.tool | grep $2 |  awk '{$1=$1;print}' | sort -u | awk -F '"' -v variable=$2 'BEGIN {print variable}{print $4}'
