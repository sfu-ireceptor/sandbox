import sys
import argparse
import json
import pandas as pd
import numpy as np

# process COVAbDab data from the file provided.
def processCOVAbDab(filename, verbose):
    # Open the cell file.
    try:
        with open(filename) as f:
            cad_df = pd.read_csv(f, sep=',')
    except Exception as e:
        print('ERROR: Unable to read COVAbDab file %s'%(cell_file))
        print('ERROR: Reason =' + str(e))
        return False
    if verbose:
        print(cad_df)

    # Process ieach row in the file 
    num_abs = cad_df.shape[0]
    count = 0
    # Print the 10X style header line.
    print('barcode\tchain\tv_gene\tcdr3\tj_gene')
    for index, row in cad_df.iterrows():
        barcode = row['Name']
        # If we have a v gene extract the locus (first 3 characters)
        # and the gene ("IGHV3-48 (Human)" becomes "IGHV3-48" - split
        # on space separator and take the first element.
        if type(row['Heavy V Gene']) is str:
            chain1_locus = row['Heavy V Gene'][0:3]
            chain1_vgene = row['Heavy V Gene'].split()[0]
        else:
            chain1_locus = '' 
            chain1_vgene = ''
        # Get the CDR3
        chain1_cdr3 = row['CDRH3']
        # Extract the J gene as above
        if type(row['Heavy J Gene']) is str:
            chain1_jgene = row['Heavy J Gene'].split()[0]
        else:
            chain1_jgene = ''

        # Repeat for the light chain.
        if type(row['Light V Gene']) is str:
            chain2_locus = row['Light V Gene'][0:3]
            chain2_vgene = row['Light V Gene'].split()[0]
        else:
            chain2_locus = '' 
            chain2_vgene = ''
        chain2_cdr3 = row['CDRL3']
        if type(row['Light J Gene']) is str:
            chain2_jgene = row['Light J Gene'].split()[0]
        else:
            chain2_jgene = ''

        # Print out both chains.
        print('%s\t%s\t%s\t%s\t%s'%(barcode, chain1_locus, chain1_vgene, chain1_cdr3, chain1_jgene))
        print('%s\t%s\t%s\t%s\t%s'%(barcode, chain2_locus, chain2_vgene, chain2_cdr3, chain2_jgene))
        count = count + 1

    if verbose:
        print("Number of Abs processed = %d"%(count))

    return True

def getArguments():
    # Set up the command line parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=""
    )
    parser = argparse.ArgumentParser()

    # The cell/barcode file name
    parser.add_argument("filename")
    # Verbosity flag
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Run the program in verbose mode.")

    # Parse the command line arguements.
    options = parser.parse_args()
    return options


if __name__ == "__main__":
    # Get the command line arguments.
    options = getArguments()

    # Process a COVAbDab file and output a 10X file, which bcrdist can input
    success = processCOVAbDab(options.filename, options.verbose)

    # Return success if successful
    if not success:
        print('ERROR: Unable to process COVAbDab file %s)'% (options.filename))
        sys.exit(1)
