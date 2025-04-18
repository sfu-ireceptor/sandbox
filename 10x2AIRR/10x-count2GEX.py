import sys
import argparse
import json
import pandas as pd
import numpy as np


# process GEX data from the 10X files provided.
def processGEX(cell_file, feature_file, matrix_file,
               skip_mtx_header, ensembl_only, verbose):
    # Open the cell file.
    try:
        with open(cell_file) as f:
            cell_df = pd.read_csv(f, sep='\t', header=None)
    except Exception as e:
        print('ERROR: Unable to read Cell file %s'%(cell_file))
        print('ERROR: Reason =' + str(e))
        return False
    if verbose:
        print(cell_df)

    # Open the feature file.
    try:
        with open(feature_file) as f:
            feature_df = pd.read_csv(f, sep='\t', header=None)
    except Exception as e:
        print('ERROR: Unable to read Feature file %s'%(feature_file))
        print('ERROR: Reason =' + str(e))
        return False
    if verbose:
        print(feature_df)

    # Open the matrix file for reading in chunks.
    chunk_size = 1000
    try:
        with open(matrix_file) as f:
            #matrix_df_reader = pd.read_csv(f, sep=' ', chunksize=chunk_size)
            #matrix_df = pd.read_csv(f, sep=' ', header=[0,1,2])
            if skip_mtx_header:
                matrix_df = pd.read_csv(f, sep=' ', skiprows=1, header=None)
            else:
                matrix_df = pd.read_csv(f, sep=' ', header=None)
    except Exception as e:
        print('ERROR: Unable to read matrix file %s'%(matrix_file))
        print('ERROR: Reason =' + str(e))
        return False
    if verbose:
        print(matrix_df)

    # Iterate over the file a chunk at a time. Each chunk is a data frame.
    #total_records = 0
    #for df_chunk in matrix_df_reader:
        #total_records += chunk_size
        #print("Read %d records"%(total_records))
    print("[")
    max_index = len(matrix_df.index)-1
    gex_count = 0
    for ind in matrix_df.index:
        gene_index = matrix_df[0][ind]
        cell_index = matrix_df[1][ind]
        level = matrix_df[2][ind]

        gene_id = feature_df[0][gene_index-1]
        gene_label = feature_df[1][gene_index-1]

        cell = cell_df[0][cell_index-1]

        gex_count = gex_count + 1

        if gene_id[:4] == "ENSG":
            # We don't print a JSON separator or new line on each line (which is what we want for
            # the last line). So if we are processing any but the first line, we want to print
            # out the separator needed for the previous line. This means the last line won't have
            # a comma separator but all other will.
            if gex_count > 1:
                print(',')
            print('{"cell_id":"%s", "property":{"id":"ENSG:%s", "label":"%s"}, "value":%d}'%
                  (cell, gene_id, gene_label, level),end='')
        else:
            if not ensembl_only:
                # We don't print a JSON separator or new line on each line (which is what we want for
                # the last line). So if we are processing any but the first line, we want to print
                # out the separator needed for the previous line. This means the last line won't have
                # a comma separator but all other will.
                if gex_count > 1:
                    print(',')
                print('{"cell_id":"%s", "property":{"id":"%s", "label":"%s"}, "value":%d}'%
                  (cell, gene_id, gene_label, level),end='')

    print("]")

    return True

def getArguments():
    # Set up the command line parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=""
    )
    parser = argparse.ArgumentParser()

    # The cell/barcode file name
    parser.add_argument("cell_file")
    # The repertoire_id to summarize
    parser.add_argument("feature_file")
    # The repertoire_id to summarize
    parser.add_argument("matrix_file")
    # Verbosity flag
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Run the program in verbose mode.")
    # Skip header flag
    parser.add_argument(
        "-s",
        "--skip_mtx_header",
        action="store_true",
        help="Skip the header line in the matrix file.")
    # Only process Ensembl IDs
    parser.add_argument(
        "-e",
        "--ensembl_only",
        action="store_true",
        help="Only process GEX that are Ensembl IDs (with an ID that starts wiht ENSG).")

    # Parse the command line arguements.
    options = parser.parse_args()
    return options


if __name__ == "__main__":
    # Get the command line arguments.
    options = getArguments()

    # Process and produce a GEX file from the 10X count pipeline. This uses the
    # standard 10X barcodes.tsv for the cells, features.tsv for the gene features
    # and the 10X matrix.mtx file (stripped of headers) which has three columns, the
    # first column is an index into the features.tsv, the second column is the index
    # into the barcodes.tsv file, and the third column is the count of the number of
    # times that feature was found for that cell.
    success = processGEX(options.cell_file, options.feature_file,
                         options.matrix_file, options.skip_mtx_header,
                         options.ensembl_only, options.verbose)

    # Return success if successful
    if not success:
        print('ERROR: Unable to process 10X files (cells=%s, features=%s, matrix=%s)'%
              (options.cell_file, options.feature_file,options.matrix_file))
        sys.exit(1)
