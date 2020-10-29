#!/bin/bash

echo "Running study summary for $1"

./get_study_id.sh $1 > /tmp/studies.tsv

python3 ./ADC-study-summary.py -v $1 /tmp/studies.tsv study_id 


