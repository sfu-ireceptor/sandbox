import pandas as pd
import numpy as np
import sre_yield
import argparse
import json
import os, ssl
import sys
import time

def getArguments():
    # Set up the command line parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=""
    )

    # Limited regex used to generate the AA motif
    parser.add_argument("motif_regex")

    # Output file
    parser.add_argument(
        "--output_file",
        dest="output_file",
        default=None,
        help="The output file to use. If none supplied, uses stdout."
    )

    # AA alphabet to user
    parser.add_argument(
        "--generate_list",
        dest="generate_list",
        default=False,
        help="Generate a list. If not set, an ADC query is generated."
    )

    # AA alphabet to user
    parser.add_argument(
        "--alphabet",
        dest="alphabet",
        default="ACDEFGHIKLMNPQRSTVWY",
        help="The Amino Acid alphabet to use, defaults to 'ACDEFGHIKLMNPQRSTVWY' "
    )

    # Parse the command line arguements.
    options = parser.parse_args()
    return options


if __name__ == "__main__":
    # Get the command line arguments.
    options = getArguments()

    # Get the output file handle
    if options.output_file == None:
        output_handle = sys.stdout
    else:
        try:
            output_handle = open(options.output_file, "w")
        except Exception as err:
            print("ERROR: Unable to open output file %s - %s" % (options.output_file, err))
            sys.exit(1)

    # Generate the list of cdr3s
    cdr3_list = list(sre_yield.AllStrings(options.motif_regex,charset=options.alphabet))

    # Set up our counts
    num = len(cdr3_list)
    count = 0

    # If generating an ADC API query, generate the header.
    if not options.generate_list:
        print('{ "filters": { "op" : "or", "content" : [', file=output_handle)

    # For each CDR3 in the motif list
    for cdr3 in cdr3_list:
        # Either output it or output it as an ADC API query in the or list
        if options.generate_list:
            print('%s'%(cdr3), file=output_handle)
        else:
            if count == num-1:
                separator = ''
            else:
                separator = ','
            print('    { "op":"=", "content": { "field":"junction_aa", "value":"%s" } }%s'%(cdr3, separator), file=output_handle)
        count = count + 1

    # If generating an ADC API query, generate the footer of the query.
    if not options.generate_list:
        print('] }, "facets":"repertoire_id" }', file=output_handle)

