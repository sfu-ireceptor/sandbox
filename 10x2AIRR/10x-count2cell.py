import sys
import argparse
import json
import pandas as pd
import numpy as np


# process Cell data from the 10X cell file provided.
def processCountCell(cell_file, skip_header, verbose):
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

    # Each object in the AIRR format has some constant string attributes
    # that we add for each cell.
    the_rest = '"virtual_pairing":false, "expression_study_method":"single-cell transcriptome"'
    separator = ','


    # Each row in the file has a cell barcode.
    print("[")
    num_cells = cell_df.shape[0]
    # If we have a header, we have one less cell.
    if skip_header:
        num_cells = num_cells - 1
    count = 0
    for index, row in cell_df.iterrows():
        # Skip the header line if requested
        if skip_header and index > 0:
            # Handle the last line, no trailing comma
            if count == num_cells-1:
                separator = ''
            print('{"cell_id":"%s", %s}%s'%(row[0],  the_rest, separator))
            count = count + 1
    print("]")

    if verbose:
        print("Number of cells = %d"%(cell_count))

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
    # Verbosity flag
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Run the program in verbose mode.")
    # Add flag for skipping header
    parser.add_argument(
        "-s",
        "--skip_header",
        action="store_true",
        help="Skip the header line in the file.")

    # Parse the command line arguements.
    options = parser.parse_args()
    return options


if __name__ == "__main__":
    # Get the command line arguments.
    options = getArguments()

    # Process and produce a AIRR Cell file from the 10X Count pipeline. This uses the
    # standard 10X barcodes.txv to determine which cells are b or t-cells
    success = processCountCell(options.cell_file, options.skip_header, options.verbose)

    # Return success if successful
    if not success:
        print('ERROR: Unable to process 10X Cell file %s)'% (options.cell_file))
        sys.exit(1)
