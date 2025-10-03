#!/bin/bash

for base_str in trb09 trb10 trb11 trb12 trb13; do
	echo "../../run_receptor_reports_fast.sh ../../receptor/2024-08-06/iedb_tcr_$base_str.tsv repository-t1d-1.tsv repertoire-trb-contains-schema-rearrangement.json repertoire_fields.tsv $base_str > $base_str.out"
	../../run_receptor_reports_fast.sh ../../receptor/2024-08-06/iedb_tcr_$base_str.tsv repository-t1d-1.tsv repertoire-trb-contains-schema-rearrangement.json repertoire_fields.tsv $base_str > $base_str.out
done
