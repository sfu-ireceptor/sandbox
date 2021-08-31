#!/bin/bash


SCRIPT_DIR=`dirname "$0"`

# check number of arguments
NB_ARGS=1
if [ $# -ne $NB_ARGS ];
then
    echo "$0: wrong number of arguments ($# instead of $NB_ARGS)"
    echo "usage: $0 URL"
    exit 1
fi


curl -k -s --data '{"fields":["study.study_id"]}' $1 | python3 -m json.tool | grep study_id |  awk '{$1=$1;print}' | sort -u | awk -F '"' 'BEGIN {print "study_id"}{print $4}'
