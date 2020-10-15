#!/bin/bash

curl -k -s --data '{"fields":["study.study_id"]}' $1 | python -m json.tool | grep study_id |  awk '{$1=$1;print}' | sort -u | awk -F '"' 'BEGIN {print "study_id"}{print $4}'
