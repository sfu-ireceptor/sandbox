#!/bin/bash


# Check if a file is provided as an argument
if [ $# -lt 8 ]; then
    echo "Usage: $0 REPOSITORY_TSV REPERTOIRE_QUERY_JSON REPERTOIRE_FIELD_TSV JUNCTION VGENE JGENE OUTPUT_DIR SUMMARY_FILE"
    exit 1
fi

# Get the files to use
REPOSITORY_TSV=$1
REPERTOIRE_QUERY_JSON=$2
REPERTOIRE_FIELD_TSV=$3

# Expect parameters JUNCTION, V Gene, J Gene, and Epitope (optional)
# E.g. CASSLQSSYNSPLHF TRBV11-2 TRBJ1-6 QKRGIVEQCCTSICS
JUNCTION=$4
VGENE=$5
JGENE=$6

# Expect a summary file name to put high level statistics
OUTPUT_BASE_DIR=$7
SUMMARY_FILE=$8

# Create the hits and misses directories. We put any chains for
# which we found a receptor in $HITS_DIR and those where we
# didn't find any chains in the $MISSES_DIR
HITS_DIR=$OUTPUT_BASE_DIR/hits
MISSES_DIR=$OUTPUT_BASE_DIR/misses

# Sometimes we need the CDR3, so compute it if from the Junction
CDR3=${JUNCTION:1:-1}

# Store in the output directory named for the JUNCTION
BASE_RECEPTOR_STR="${JUNCTION}_${VGENE}_${JGENE}"
OUTPUT_DIR="$OUTPUT_BASE_DIR/${JUNCTION}_${VGENE}_${JGENE}"
REPORT_FILE=$OUTPUT_DIR/report.out

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set up the directories
mkdir -p $OUTPUT_DIR
mkdir -p $HITS_DIR
mkdir -p $MISSES_DIR

# Set up the repertoire query file name.
JSON_QUERY_FILE=$OUTPUT_DIR/$BASE_RECEPTOR_STR.json

echo "Performing search for $1 $2 $3 $4" > $REPORT_FILE
echo -n "Starting query at: " >> $REPORT_FILE
date >> $REPORT_FILE

# Loop over the repositories starting at the second line
tail -n +2 ${REPOSITORY_TSV} | while IFS=$'\t' read -r repository other_columns; do
    echo "Processing repository $repository"
    # Get the domain name of the repository
    domain_name=$(echo $repository | awk -F/ '{print $3}')

    # Get the results for the repertoire search
    curl -H 'content-type: application/json' -k -s -d @$REPERTOIRE_QUERY_JSON $repository/airr/v1/repertoire \
	    > $OUTPUT_DIR/repertoires-${domain_name}-$BASE_RECEPTOR_STR.json 
    if [ $? -ne 0 ]; then
        echo "ERROR: Curl command for repertoires failed"
	continue
    fi

    # Extract the list of repertoires.
    cat $OUTPUT_DIR/repertoires-${domain_name}-$BASE_RECEPTOR_STR.json | \
	    jq -r '.Repertoire[].repertoire_id' \
	    > $OUTPUT_DIR/repertoires-${domain_name}-$BASE_RECEPTOR_STR.tsv

    # Check for 0 repertoires
    num_repertoires=$(wc -l < $OUTPUT_DIR/repertoires-${domain_name}-$BASE_RECEPTOR_STR.tsv)

    if [ $num_repertoires -ne 0 ]; then
        # Generate the filter to search for the Receptor. This includes the
	# list of repertoire IDs to search.
        JSON_QUERY_FILE=$OUTPUT_DIR/${domain_name}-$BASE_RECEPTOR_STR.json
        echo '{ "filters": { "op" : "and", "content" : [' > $JSON_QUERY_FILE
	# Or for the repertoire IDs
        echo '{ "op" : "or", "content": ' >> $JSON_QUERY_FILE
        cat $OUTPUT_DIR/repertoires-${domain_name}-$BASE_RECEPTOR_STR.json | \
	        jq -r '[ .Repertoire[] | { "op" : "=", "content": { "field" : "repertoire_id",value : .repertoire_id}}]' \
	        >> $JSON_QUERY_FILE
        echo '},' >> $JSON_QUERY_FILE
	# The receptor fields
        echo "{ \"op\":\"=\", \"content\": { \"field\":\"junction_aa\", \"value\":\"${JUNCTION}\"}}," >> $JSON_QUERY_FILE
        echo "{ \"op\":\"=\", \"content\": { \"field\":\"v_gene\", \"value\":\"${VGENE}\"}}," >> $JSON_QUERY_FILE
        echo "{ \"op\":\"=\", \"content\": { \"field\":\"j_gene\", \"value\":\"${JGENE}\"}}" >> $JSON_QUERY_FILE
	# Ask for a facet count for each repertoire ID
        echo '] }, "facets":"repertoire_id"}' >> $JSON_QUERY_FILE
        
        # Search for the receptor of interest from the repertoires of interest.
        curl -H 'content-type: application/json' -k -s -d @${JSON_QUERY_FILE} ${repository}/airr/v1/rearrangement \
		> ${OUTPUT_DIR}/count-${domain_name}-${BASE_RECEPTOR_STR}.json
	if [ $? -ne 0 ]; then
	    echo "ERROR: Curl command for rearrangements failed"
	    continue
	fi
    
	# Get the count of the number of receptors and the number of repertoires
        COUNT=`cat $OUTPUT_DIR/count-${domain_name}-$BASE_RECEPTOR_STR.json | jq '[.Facet[].count]| add | if . > 0 then . else 0 end'`
        REPERTOIRES=`cat $OUTPUT_DIR/count-${domain_name}-$BASE_RECEPTOR_STR.json | jq ' [.Facet[].count]| length'`

        echo "" >> $REPORT_FILE
        echo "Repository $repository had $num_repertoire repertoires that met the search criteria" >> $REPORT_FILE
        echo "The Receptor $JUNCTION/$VGENE/$JGENE was found $COUNT times in repository $repository" >> $REPORT_FILE
        echo "The Receptor $JUNCTION/$VGENE/$JGENE was found in $REPERTOIRES repertoires in repository $repository" >> $REPORT_FILE
        echo "$repository	$OUTPUT_DIR	sequences/repertoires	$COUNT	$REPERTOIRES" >> $REPORT_FILE
        echo "" >> $REPORT_FILE

	# Add a line to the summary file
        echo "$repository	$OUTPUT_DIR	sequences/repertoires	$COUNT	$REPERTOIRES" >> $OUTPUT_BASE_DIR/$SUMMARY_FILE

        echo "Found $COUNT receptors in $num_repertoires repertoires in $repository"
	
	# If we got some results, download them
        if [ $COUNT -ne 0 ]; then
            # Generate the filter to download the receptor chain

            JSON_QUERY_FILE=$OUTPUT_DIR/${domain_name}-$BASE_RECEPTOR_STR.json
            echo '{ "filters": { "op" : "and", "content" : [' > $JSON_QUERY_FILE
	    # Or for the repertoire IDs
            echo '{ "op" : "or", "content": ' >> $JSON_QUERY_FILE
            cat $OUTPUT_DIR/repertoires-${domain_name}-$BASE_RECEPTOR_STR.json | \
	            jq -r '[ .Repertoire[] | { "op" : "=", "content": { "field" : "repertoire_id",value : .repertoire_id}}]' \
	            >> $JSON_QUERY_FILE
            echo '},' >> $JSON_QUERY_FILE
	    # The receptor fields
            echo "{ \"op\":\"=\", \"content\": { \"field\":\"junction_aa\", \"value\":\"${JUNCTION}\"}}," >> $JSON_QUERY_FILE
            echo "{ \"op\":\"=\", \"content\": { \"field\":\"v_gene\", \"value\":\"${VGENE}\"}}," >> $JSON_QUERY_FILE
            echo "{ \"op\":\"=\", \"content\": { \"field\":\"j_gene\", \"value\":\"${JGENE}\"}}" >> $JSON_QUERY_FILE
	    # Ask for a facet count for each repertoire ID
            echo '] }, "format":"tsv"}' >> $JSON_QUERY_FILE

            # Download the sequences for the receptor
            echo -n "Starting download at: " >> $REPORT_FILE
            date >> $REPORT_FILE
            curl -H 'content-type: application/json' -k -s -d @${JSON_QUERY_FILE} ${repository}/airr/v1/rearrangement \
		    > ${OUTPUT_DIR}/rearrangement-${domain_name}-${BASE_RECEPTOR_STR}.tsv
            echo -n "Done download at: " >> $REPORT_FILE
            date >> $REPORT_FILE
	fi
    else
        echo "Found 0 receptors in $num_repertoires repertoires in $repository"
    fi

done 

echo -n "Done query at: " >> $REPORT_FILE
date >> $REPORT_FILE

# If we found some receptors, move the directory to hits, else
# move the directory to the misses. We check the summary file
# to see if it has any output lines indicating a hit. Output lines
# look like this:
#
# https://t1d-1.ireceptor.org     trb00/CAISETGTDTQYF_TRBV10-3_TRBJ2-3    sequences/repertoires   22      22
#
# So we look for a number at the end of the line that is non-zero.
TOTAL=`egrep "[1-9][0-9]*$" $REPORT_FILE | grep "sequences/repertoires" | wc -l`
echo "Total = $TOTAL"
if [ $TOTAL -ne 0 ]; then
   mv $OUTPUT_DIR $HITS_DIR
   echo "Found receptors for $OUTPUT_DIR"
else
   mv $OUTPUT_DIR $MISSES_DIR
fi

