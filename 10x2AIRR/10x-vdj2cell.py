import sys
import argparse
import json
import pandas as pd
import numpy as np


# process Cell data from the 10X cell file provided.
def processVDJCell(cell_file, drop_cell_file, verbose):
    # Open the b_cell or t_cell JSON file.
    try:
        with open(cell_file) as f:
            cell_dict = json.load(f)
    except Exception as e:
        print('ERROR: Unable to read B/T Cell JSON file %s'%(cell_file))
        print('ERROR: Reason =' + str(e))
        return False
    if verbose:
        print(cell_dict, file=sys.stderr)

    # Read in the Cell drop list.
    drop_cell_list = []
    if not drop_cell_file is None:
        try:
            drop_cell_df = pd.read_csv(drop_cell_file, sep=',', header=None)
            drop_cell_list = drop_cell_df[0].tolist()
        except Exception as e:
            print('ERROR: Unable to read Cell drop file %s'%(drop_cell_file))
            print('ERROR: Reason =' + str(e))
            return False
        if verbose:
            print(drop_cell_df, file=sys.stderr)


    # Each JSON object in the AIRR format has some constant string attributes
    # that we add for each cell.
    the_rest = '"virtual_pairing":false, "expression_study_method":"single-cell transcriptome"'
    separator = ','

    # Start of JSON array
    print("[")
    num_cells = len(cell_dict)
    count = 0
    total_count = 0
    # For each cell in the input file
    for cell in cell_dict:
        # Check if it should be dropped - if not process it.
        if not cell in drop_cell_list:
            # If we are processing the last cell, don't output the separator.
            if total_count == num_cells-1:
                separator = ''
            # Print a line for the cell.
            print('{"cell_id":"%s", %s}%s'%(cell,  the_rest, separator))
            count = count + 1
        else:
            print('Dropping cell %s'%(cell), file=sys.stderr)
        total_count = total_count + 1
    # End of JSON array.
    print("]")

    if verbose:
        print("Number of cells = %d"%(count), file=sys.stderr)

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
    # File to use that includes a list of cell_id's to drop
    parser.add_argument(
        "--drop-cells",
        dest="drop_cell_file",
        default=None,
        help="Name of the file that contains a list of cell_id's that should be ignored."
    )

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

    # Process and produce a AIRR Cell file from the 10X VDJ pipeline. This uses the
    # standard 10X cell_barcodes.json to determine which cells are b or t-cells
    success = processVDJCell(options.cell_file, options.drop_cell_file, options.verbose)

    # Return success if successful
    if not success:
        print('ERROR: Unable to process 10X Cell file %s)'% (options.cell_file))
        sys.exit(1)
