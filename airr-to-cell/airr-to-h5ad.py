import sys
import argparse
import json
import pandas as pd
import numpy as np
import anndata as ad
from scipy.sparse import csr_matrix
from scipy.sparse import lil_matrix


# process GEX data from the 10X files provided.
def generateH5AD(airr_cell_file, airr_gex_file, output_file, verbose):
    # Open the AIRR Cell JSON file.
    try:
        with open(airr_cell_file) as f:
            cell_dict = json.load(f)
    except Exception as e:
        print('ERROR: Unable to read AIRR Cell JSON file %s'%(airr_cell_file))
        print('ERROR: Reason =' + str(e))
        return False
    if verbose:
        print(cell_dict)

    # Open the AIRR GEX JSON file.
    try:
        with open(airr_gex_file) as f:
            gex_dict = json.load(f)
    except Exception as e:
        print('ERROR: Unable to read AIRR GEX JSON file %s'%(airr_gex_file))
        print('ERROR: Reason =' + str(e))
        return False
    if verbose:
        print(gex_dict)

    cell_names = []
    if 'Cell' in cell_dict:
        cell_array = cell_dict['Cell']
        if isinstance(cell_array, list):
            num_cells = len(cell_array)
            print('Num cells = %s'%(num_cells))
            for cell in cell_array:
                cell_names.append(cell['cell_id'])
                

    property_names = []
    if 'CellExpression' in gex_dict:
        gex_array = gex_dict['CellExpression']
        if isinstance(gex_array, list):
            num_gex = len(gex_array)
            print('Num gex = %s'%(num_gex))
            for cell_property in gex_array:
                property_names.append(cell_property['property']['label'])

    #counts = np.zeros((num_cells, num_gex), dtype=np.int16)
    counts = lil_matrix((num_cells, num_gex), dtype=np.float32)
    print(counts)
    adata = ad.AnnData(counts)
    adata.obs_names = cell_names
    adata.var_names = property_names
    print(adata.obs_names[:10])
    print(adata.var_names[:10])
    
    count = 0
    print('starting to add data')
    for cell_property in gex_array:
        adata[cell_property['cell_id'], cell_property['property']['label']] = cell_property['value']
        print('count = %s'%(count))
        count = count + 1

    adata.write(output_file, compression="gzip")
    print('Wrote adata file to %s'%(output_file))
    return True

def getArguments():
    # Set up the command line parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=""
    )
    parser = argparse.ArgumentParser()

    # The t-cell/b-cell barcode file name
    parser.add_argument("airr_cell_file")
    # The cell/barcode file name
    parser.add_argument("airr_gex_file")
    # The repertoire_id to summarize
    parser.add_argument("output_file")
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

    # Process and produce a AIRR GEX file from the 10X VDJ pipeline. This uses the
    # standard 10X cell_barcodes.json to determine which cells are b or t-cells but still
    # uses the count pipeline barcodes.tsv file for the cell indexes and features.tsv for
    # the gene features. It uses the 10X matrix.mtx file (stripped of headers) to get the
    # count for each cell/gene pair. It has three columns, the first column is an index
    # into the features.tsv, the second column is the index into the barcodes.tsv file,
    # and the third column is the count of the number of times that feature was found
    # for that cell.
    success = generateH5AD(options.airr_cell_file, options.airr_gex_file, options.output_file,
                           options.verbose)

    # Return success if successful
    if not success:
        print('ERROR: Unable to process AIRR files (cells=%s, gex=%s)'%
              (options.airr_cell_file, options.airr_gex_file))
        sys.exit(1)
