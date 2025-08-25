#!/bin/bash

# Check if the correct number of command line paramaters are given
if [ $# -ne 3 ]; then
    echo "Usage: $0 IEDB_RECEPTOR_FILE LOCUS_COLUMN LOCUS_PATTERN"
    exit 1
fi

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Input IEDB file is first parameter.
iedb_receptor_file=$1
locus_column=$2
locus_pattern=$3

# Get the directory the data lives in.
data_dir=$(dirname ${iedb_receptor_file})
# Get the base file name
base_file=$(basename ${iedb_receptor_file} .tsv)

# Strip off the first header line, the IEDB file has two header lines.
echo "tail"
tail -n +2 ${iedb_receptor_file} > ${base_file}_tail.tsv

# Cut out all columns except the named ones, junction_aa, v_gene, j_gene
# for the correct IEDB chain. IEDB has both chains in one file, with
# separate columns for each. We name the columns with the locus (either tra or trb).
# NOTE: The tra column has both TRA and TRG while trb column has both TRB and TRD
echo "cut headers"
bash ${SCRIPT_DIR}/cut_headers.sh ${base_file}_tail.tsv "junction_aa_${locus_column},v_gene_${locus_column},j_gene_${locus_column}" > ${base_file}_tail_${locus_column}.tsv

# Extract only those chains that have a valid junction, V and J gene.
# Valid junctions start with C and end with W or F.
# Valid genes contain TR[ABGD] in their columns. We are a bit
# permissive here in case there is a TRB or TRD in the tra column in
# case there is a glitch in IEDB and the two chains are reversed. 
echo "get valid"
cat ${base_file}_tail_${locus_column}.tsv | awk -F'\t' -v pattern="${locus_pattern}" '$1 ~ /^C.*[FW]$/ && $2 ~ pattern && $3 ~ pattern' > ${base_file}_tail_${locus_column}_full_chain.tsv 

# Sort and extract unique chains, we don't want to process the same one more than once.
echo "unique"
cat ${base_file}_tail_${locus_column}_full_chain.tsv | sort -u > ${base_file}_tail_${locus_column}_full_chain_unique.tsv
