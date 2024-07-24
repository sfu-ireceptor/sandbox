#!/bin/bash


# Check if a file is provided as an argument
if [ $# -ne 7 ]; then
    echo "Usage: $0 CDR3 VGENE JGENE EPITOPE REPOSITORY_TSV REPERTOIRE_QUERY_JSON REPERTOIRE_FIELD_TSV"
    exit 1
fi


# Expect parameters CDR3, V Gene, J Gene, and Epitope
# E.g. CASSLQSSYNSPLHF TRBV11-2 TRBJ1-6 QKRGIVEQCCTSICS
CDR3=$1
VGENE=$2
JGENE=$3
EPITOPE=$4

# Get the files to use
REPOSITORY_TSV=$5
REPERTOIRE_QUERY_JSON=$6
REPERTOIRE_FIELD_TSV=$7

# Store in the output directory named for the CDR3
OUTPUT_DIR=$1_$2_$3_$4
REPORT_FILE=$OUTPUT_DIR/report.out

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p $OUTPUT_DIR
JSON_QUERY_FILE=$OUTPUT_DIR/$CDR3.json

echo "Performing search for $1 $2 $3 $4" > $REPORT_FILE
echo -n "Starting query at: " >> $REPORT_FILE
date >> $REPORT_FILE

# Generate the filter to search for the Receptor

echo '{ "filters": { "op" : "and", "content" : [' > $JSON_QUERY_FILE
echo "{ \"op\":\"=\", \"content\": { \"field\":\"junction_aa\", \"value\":\"${CDR3}\"}}," >> $JSON_QUERY_FILE
echo "{ \"op\":\"=\", \"content\": { \"field\":\"v_gene\", \"value\":\"${VGENE}\"}}," >> $JSON_QUERY_FILE
echo "{ \"op\":\"=\", \"content\": { \"field\":\"j_gene\", \"value\":\"${JGENE}\"}}" >> $JSON_QUERY_FILE
echo '] }, "facets":"repertoire_id"}' >> $JSON_QUERY_FILE

# Search the ADC for instances of said receptor

python3 ${SCRIPT_DIR}/adc-search.py ${REPOSITORY_TSV} ${REPERTOIRE_QUERY_JSON} $JSON_QUERY_FILE --service_delay=0.2 --output_file=$OUTPUT_DIR/count-$CDR3.json --field_file=${REPERTOIRE_FIELD_TSV} --verbose > $OUTPUT_DIR/count-$CDR3.out

# Generate the filter to download the receptor chain

echo '{ "filters": { "op" : "and", "content" : [' > $JSON_QUERY_FILE
echo "{ \"op\":\"=\", \"content\": { \"field\":\"junction_aa\", \"value\":\"${CDR3}\"}}," >> $JSON_QUERY_FILE
echo "{ \"op\":\"=\", \"content\": { \"field\":\"v_gene\", \"value\":\"${VGENE}\"}}," >> $JSON_QUERY_FILE
echo "{ \"op\":\"=\", \"content\": { \"field\":\"j_gene\", \"value\":\"${JGENE}\"}}" >> $JSON_QUERY_FILE
echo '] }, "format":"tsv"}' >> $JSON_QUERY_FILE

# Download the sequences for the receptor

python3 ${SCRIPT_DIR}/adc-search.py --verbose ${REPOSITORY_TSV} ${REPERTOIRE_QUERY_JSON} $JSON_QUERY_FILE --output_format=TSV --output_file=$OUTPUT_DIR/download-$CDR3.tsv --output_dir=${OUTPUT_DIR}/ --field_file=${REPERTOIRE_FIELD_TSV} > $OUTPUT_DIR/download-$CDR3.out


# Generate a report for the repertoires where the receptor was found

COUNT=`cat $OUTPUT_DIR/count-$CDR3.json | jq '[.[].results[].Facet[].count]| add | if . > 0 then . else 0 end'`
REPERTOIRES=`cat $OUTPUT_DIR/count-$CDR3.json | jq ' [.[].results[].Facet[].count]| length'`

echo "" >> $REPORT_FILE
echo "The Receptor $CDR3/$VGENE/$JGENE was found $COUNT times in the ADC" >> $REPORT_FILE
echo "The Receptor $CDR3/$VGENE/$JGENE was found in $REPERTOIRES repertoires" >> $REPORT_FILE
echo "sequences/repertoires $COUNT $REPERTOIRES" >> $REPORT_FILE
echo "" >> $REPORT_FILE

#echo "" >> $REPORT_FILE
#echo "The Receptor $CDR3/$VGENE/$JGENE was found in the following ADC repertoires" >> $REPORT_FILE
#echo "" >> $REPORT_FILE
#
#cat $OUTPUT_DIR/count-$1.json | jq ' [ .[].results[] | if .Facet[0].count > 0 then {Repertoire: .Repertoire, count: .Facet[0].count} else empty end ]' >> $REPORT_FILE

# Generate a list of all Receptors in IEDB that contain the CDR3

curl -s https://query-api.iedb.org/tcr_search?chain1_cdr3_seq=like.*$CDR3* > $OUTPUT_DIR/iedb-tcr-chain1-$CDR3.json
echo "Found TCR receptors that contain $CDR3 in IEDB:" >> $REPORT_FILE
cat $OUTPUT_DIR/iedb-tcr-chain1-$CDR3.json | jq '[ .[] | { receptor_group_iri: .receptor_group_iri, receptor_chain1_types: .receptor_chain1_types, chain1_cdr3_seq: .chain1_cdr3_seq,  receptor_chain2_types: .receptor_chain2_types, chain2_cdr3_seq: .chain2_cdr3_seq, antigens: .curated_source_antigens, epitope_iris: .structure_iris, epitopes: .structure_descriptions, disease_names: .disease_names} ]' >> $REPORT_FILE

curl -s https://query-api.iedb.org/tcr_search?chain2_cdr3_seq=like.*$CDR3* > $OUTPUT_DIR/iedb-tcr-chain2-$CDR3.json
cat $OUTPUT_DIR/iedb-tcr-chain2-$CDR3.json | jq '[ .[] | { receptor_group_iri: .receptor_group_iri, receptor_chain1_types: .receptor_chain1_types, chain1_cdr3_seq: .chain1_cdr3_seq,  receptor_chain2_types: .receptor_chain2_types, chain2_cdr3_seq: .chain2_cdr3_seq, antigens: .curated_source_antigens, epitope_iris: .structure_iris, epitopes: .structure_descriptions, disease_names: .disease_names} ]' >> $REPORT_FILE

echo "Found BCR receptors that contain $CDR3 in IEDB:" >> $REPORT_FILE
curl -s https://query-api.iedb.org/bcr_search?chain1_cdr3_seq=like.*$CDR3* > $OUTPUT_DIR/iedb-bcr-chain1-$CDR3.json
cat $OUTPUT_DIR/iedb-bcr-chain1-$CDR3.json | jq '[ .[] | { receptor_group_iri: .receptor_group_iri, receptor_chain1_types: .receptor_chain1_types, chain1_cdr3_seq: .chain1_cdr3_seq,  receptor_chain2_types: .receptor_chain2_types, chain2_cdr3_seq: .chain2_cdr3_seq, antigens: .curated_source_antigens, epitope_iris: .structure_iris, epitopes: .structure_descriptions, disease_names: .disease_names} ]' >> $REPORT_FILE
curl -s https://query-api.iedb.org/bcr_search?chain2_cdr3_seq=like.*$CDR3* > $OUTPUT_DIR/iedb-bcr-chain2-$CDR3.json
cat $OUTPUT_DIR/iedb-bcr-chain2-$CDR3.json | jq '[ .[] | { receptor_group_iri: .receptor_group_iri, receptor_chain1_types: .receptor_chain1_types, chain1_cdr3_seq: .chain1_cdr3_seq,  receptor_chain2_types: .receptor_chain2_types, chain2_cdr3_seq: .chain2_cdr3_seq, antigens: .curated_source_antigens, epitope_iris: .structure_iris, epitopes: .structure_descriptions, disease_names: .disease_names} ]' >> $REPORT_FILE

# Generate a list of all Receptors in IEDB that are known to react with the epitope

curl -s "https://query-api.iedb.org/epitope_search?linear_sequence=eq.$EPITOPE" > $OUTPUT_DIR/iedb-epitope-$EPITOPE.json 

# Generate a report of the key data.

echo "" >> $REPORT_FILE
echo "Epitope data for $EPITOPE was found in IEDB" >> $REPORT_FILE
echo "" >> $REPORT_FILE
cat $OUTPUT_DIR/iedb-epitope-$EPITOPE.json | jq '. | [ { linear_sequence: .[].linear_sequence, structure_type: .[].structure_type, structure_iri: .[].structure_iri, host_organism_names: .[].host_organism_names, mhc_allele_names: .[].mhc_allele_names, disease_names: .[].disease_names, r_object_source_molecule_names: .[].r_object_source_molecule_names, receptor_group_iris: .[].receptor_group_iris} ]' >> $REPORT_FILE


echo -n "Done query at: " >> $REPORT_FILE
date >> $REPORT_FILE
