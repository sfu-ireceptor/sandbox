#!/bin/bash

filename=$1
column=$2

cut -f $2 $1 | sed -E 's/\[\s*//g; s/\s*\]//g; s/\"/\n/g' | sed '/^$/d' | sed '/,/d' | sort -u
#cut -f $2 $1 | sed -E 's/\[\s*"(IEDB_EPITOPE:[0-9]+)"(,\s*"IEDB_EPITOPE:[0-9]+")*\s*\]/\1\2/g' | sed -E 's/\[\s*//g; s/\s*\]//g; s/IEDB_EPITOPE:/\nIEDB_EPITOPE:/g' | sed -E 's/,//g' | sed -E 's/"//g' | sed -E 's/ //g' | sort -u
#cut -f 7 hits-Seay-TRB-DM-2025-02-18.tsv | cut -f 7 hits-Seay-TRB-DM-2025-02-18.tsv | sed -E "s/\[\s*\"(${IEDB_STR}:[0-9]+)\"(,\s*\"${IEDB_STR}:[0-9]+\")*\s*\]/\1\2/g" | sed -E "s/\[\s*//g; s/\s*\]//g; s/${IEDB_STR}:/\n${IEDB_STR}:/g" | sed -E "s/,//g" | sed -E "s/\"//g" | sed -E "s/ //g" | sort -u | wc -l
