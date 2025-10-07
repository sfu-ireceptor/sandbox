#!/bin/bash

receptor_base=../../receptor/2025-07-11
repertoire_query=repertoire-tra-contains-schema-rearrangement.json

for base_str in tra00 tra01 tra02; do
	echo "Running ../../run_receptor_reports_fast.sh ${receptor_base}/iedb_tcr_$base_str.tsv repository-t1d-1.tsv ${repertoire_query} repertoire_fields.tsv $base_str > $base_str.out"
	../../run_receptor_reports_fast.sh ${receptor_base}/iedb_tcr_$base_str.tsv repository-t1d-1.tsv ${repertoire_query} repertoire_fields.tsv $base_str > $base_str.out
done
