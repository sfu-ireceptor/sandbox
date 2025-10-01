#!/bin/bash 

split -l 1000 -d -a 3 --additional-suffix=.tsv iedb_tcr_positive_v3_tail_trb_full_receptor_unique_2024-08-06.tsv iedb_tcr_trb_1000
