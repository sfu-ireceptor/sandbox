import sys
import argparse
import json
import time
import pandas as pd
import numpy as np


# Convert AIRR Cell/GEX to 10X Cell/Gex
def generate10X(airr_cell_file, airr_gex_file, 
                feature_file, barcode_file, matrix_file, verbose):
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

    # Check for valid Cell data and write out the barcodes file. The AIRR file
    # should have a JSON Cell object that is an array of Cells.
    cell_names = []
    if 'Cell' in cell_dict:
        cell_array = cell_dict['Cell']
        if isinstance(cell_array, list):
            num_cells = len(cell_array)
            print('Num cells = %s'%(num_cells))
            # If file structure is good, output and cache the cell_ids
            try:
                with open(barcode_file, 'w') as file_object:
                    for cell in cell_array:
                        cell_names.append(cell['cell_id'])
                        cell_info = cell['cell_id'] + '\n'
                        file_object.write(cell_info)
            except Exception as e:
                print('ERROR: Unable to write 10X barcode file  %s'%(barcode_file))
                print('ERROR: Reason = ' + str(e))
                return False
        else:
            print("ERROR: Cell object is not an array in file %s"%(airr_cell_file))
            return False
    else:
        print("ERROR: Could not find Cell object in file %s"%(airr_cell_file))
        return False

    # Check for valid CellExpression data and write out the features and matrix files.
    # The AIRR file should have a JSON CellExpression object that is an array of cell
    # properties..
    if 'CellExpression' in gex_dict:
        gex_array = gex_dict['CellExpression']
        if isinstance(gex_array, list):
            num_gex = len(gex_array)
            print('Num gex = %s'%(num_gex))
        else:
            print("ERROR: CellExpression object is not an array in file %s"%(airr_gex_file))
            return False
    else:
        print("ERROR: Could not find CellExpression object in file %s"%(airr_gex_file))
        return False

    print('starting to generate matrix')
    property_names = []
    property_count = 0
    try:
            # Open the matrix and featire files. We write them in one pass.
            matrix_fh = open(matrix_file+'.tmp', 'w')
            feature_fh = open(feature_file, 'w')
            # Write the matrix header as per 10X files. We don't add the count
            # line yet as we want to we don't have the number of features.
            matrix_fh.write('%%MatrixMarket matrix coordinate integer general\n')
            matrix_fh.write('%metadata_json: {"software_version": "iReceptor Gateway v4.0", "format_version": 2}\n')
            # Set up some counting and caching stuff
            count = 0
            last_cell_id = ''
            last_cell_index = -1
            property_count = 0
            t_start = time.perf_counter()
            # Iterate over each cell property.
            for cell_property in gex_array:
                # If we don't have it listed as a property yet, add it.
                if not cell_property['property']['id'] in property_names:
                    # Add it to our list
                    property_names.append(cell_property['property']['id'])
                    # The AIRR standard uses CURIEs for propertys. Handle the case
                    # where an ID is a CURIE of the form ENSG:ENSGXXXXX. The 10X names
                    # don't have the CURIE part.
                    property_str = cell_property['property']['id']
                    if property_str.find(':') >= 0:
                        property_str = property_str.split(':')[1]
                    # Prepare the property for writing, and write it to the feature file.
                    feature = property_str + '\t' + cell_property['property']['label'] + '\tGene Expression\n'
                    feature_fh.write(feature)
                    property_count = property_count + 1
                    # Store the index of the property (the one we just added).
                    property_index = property_count
                else:
                    # If we already have the property look it up to get the index.
                    property_index = property_names.index(cell_property['property']['id'])

                # Get the cell index. Since all propertyies for a cell are often loaded
                # together we can use a cache so we don't have to look it up every time.
                if last_cell_id == cell_property['cell_id']:
                    cell_index = last_cell_index
                else:
                    cell_index = cell_names.index(cell_property['cell_id']) + 1

                # Pring out some progress monitoring.
                if count % 10000 == 0:
                    t_end = time.perf_counter()
                    print('count = %s (%d s, %f percent done)'%(count, t_end-t_start, count/num_gex))
                    t_start = time.perf_counter()

                # Prepare the matrix string for writing and write it.
                matrix_info = str(property_index) + ' ' + str(cell_index) + ' ' + str(cell_property['value']) + '\n'
                matrix_fh.write(matrix_info)
                count = count + 1
            print('Property count = %d'%(property_count))
    except Exception as e:
        print('ERROR: Unable to read AIRR GEX JSON file %s'%(airr_gex_file))
        print('ERROR: Reason = ' + str(e))
        return False

    # Close files.
    matrix_fh.close()
    feature_fh.close()

    # Not sure this is the best way to do this, but...
    # We only now have the number of features, so we rewrite the
    # file with a new third line with the counts of the three files.
    with open(matrix_file+'.tmp','r') as f:
      with open(matrix_file,'w') as f2:
        line_count = 1
        for line in f:
            # If we are on line 2, add the third line with the counts.
            if line_count == 2:
                f2.write(line)
                f2.write(str(property_count) + ' ' + str(num_cells) + ' ' + str(num_gex) + '\n')
            else:
                f2.write(line)
            line_count = line_count + 1

    return True

def getArguments():
    # Set up the command line parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=""
    )
    parser = argparse.ArgumentParser()

    # The t-cell/b-cell barcode file name
    parser.add_argument("airr_rearrangement_file")
    # The repertoire_id to summarize
    parser.add_argument("contig_file")
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

    # Open the rearrangements file.
    try:
        with open(options.airr_rearrangement_file) as f:
            rearrangement_df = pd.read_csv(f, sep='\t')
    except Exception as e:
        print('ERROR: Unable to read Rearrangement file %s'%(options.airr_rearrangement_file))
        print('ERROR: Reason =' + str(e))
        sys.exit(1)

    rearrangement_df.rename({'cell_id':'barcode'}, axis='columns', inplace=True)
    rearrangement_df.rename({'clone_id':'raw_clonotype_id'}, axis='columns', inplace=True)
    rearrangement_df.rename({'v_call':'v_gene'}, axis='columns', inplace=True)
    rearrangement_df.rename({'d_call':'d_gene'}, axis='columns', inplace=True)
    rearrangement_df.rename({'j_call':'j_gene'}, axis='columns', inplace=True)
    rearrangement_df.rename({'locus':'chain'}, axis='columns', inplace=True)
    rearrangement_df.rename({'duplicate_count':'umis'}, axis='columns', inplace=True)
    rearrangement_df['cdr3'] = rearrangement_df['junction_aa']
    rearrangement_df['cdr3_nt'] = rearrangement_df['junction']
    rearrangement_df['productive'] = True

    # Output the file
    try:
        with open(options.contig_file, 'w') as f:
            rearrangement_df.to_csv(f,  index=False)
    except Exception as e:
        print('ERROR: Unable to wrtie 10X contig file %s'%(options.contig_file))
        print('ERROR: Reason =' + str(e))
        sys.exit(1)
