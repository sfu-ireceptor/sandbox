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
    parser.add_argument("motif_regex", help="The AA motif regular expression to use. Only standard AA characters and the single character [] and . RegEx characters are accepted.")

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
        help="The Amino Acid alphabet to use, defaults to 'ACDEFGHIKLMNPQRSTVWY'."
    )

    # Query ADC API operation to use, either "=" or "contains"
    parser.add_argument(
        "--query_operation",
        dest="query_operation",
        default="=",
        help="The ADC API query operation to use, either '=' or 'contains'."
    )

    # Facet field to use
    parser.add_argument(
        "--facet_field",
        dest="facet_field",
        default="repertoire_id",
        help="The ADC API field to facet/count on (default 'repertoire_id')"
    )


    # Parse the command line arguements.
    options = parser.parse_args()
    return options

# Function that returns False if the character is in our REGEX alphabet.
# This is used to filter out all valid characters, leaving a string with
# only invalid characters which we can report as an error.
def filterAlphabet(character):
    #print('checking %s in %s'%(character, extended_alphabet))
    if character in extended_alphabet:
        return False
    else:
        return True


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

    # Check the opertation
    if options.query_operation != '=' and options.query_operation != 'contains':
        print('ERROR: Invalid query operation %s, expecting "=" or "contains"'%(options.query_operation), file=sys.stderr)
        sys.exit(1)

    # Check validity of regex. We only accept [] and . as regex characters.
    # We also only accept characters in the alphabet.
    extended_alphabet = options.alphabet + '[].'
    # Filter characters in the extended alphabet, leaving a list of characters
    # that are invalid in our regex.
    my_list = list(filter(filterAlphabet, options.motif_regex.upper()))
    # If there are invalid characters, report an error.
    if len(my_list) != 0:
        print('ERROR: Invalid characters (%s) in CDR3 motif regex %s'%("".join(my_list), options.motif_regex),file=sys.stderr)
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
            print('%s'%(cdr3.upper()), file=output_handle)
        else:
            if count == num-1:
                separator = ''
            else:
                separator = ','
            print('    { "op":"%s", "content": { "field":"junction_aa", "value":"%s" } }%s'%(options.query_operation, cdr3.upper(), separator), file=output_handle)
        count = count + 1

    # If generating an ADC API query, generate the footer of the query.
    if not options.generate_list:
        print('] }, "facets":"%s" }'%(options.facet_field), file=output_handle)

    sys.exit(0)
