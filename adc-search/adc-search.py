import urllib.request, urllib.parse
import pandas as pd
import numpy as np
import argparse
import json
import os, ssl
import sys
import time
import yaml

def processQuery(query_url, header_dict, query_json="{}", verbose=False):
    # Build the required JSON data for the post request. The user
    # of the function provides both the header and the query data

    # Encode the JSON for the HTTP requqest
    query_json_encoded = query_json.encode('utf-8')

    # Try to connect the URL and get a response. On error return an
    # empty JSON array.
    try:
        # Build the request
        request = urllib.request.Request(query_url, query_json_encoded, header_dict)
        # Make the request and get a handle for the response.
        response = urllib.request.urlopen(request)
        # Read the response
        url_response = response.read()
        # If we have a charset for the response, decode using it, otherwise assume utf-8
        if not response.headers.get_content_charset() is None:
            url_response = url_response.decode(response.headers.get_content_charset())
        else:
            url_response = url_response.decode("utf-8")
    except urllib.error.HTTPError as e:
        print('ERROR: Server could not fullfil the request to ' + query_url)
        print('ERROR: Error code = ' + str(e.code) + ', Message = ', e.read())
        return json.loads('[]')
    except urllib.error.URLError as e:
        print('ERROR: Failed to reach the server')
        print('ERROR: Reason =', e.reason)
        return json.loads('[]')
    except Exception as e:
        print('ERROR: Unable to process response')
        print('ERROR: Reason =' + str(e))
        return json.loads('[]')

    try:
        json_data = json.loads(url_response)
    except json.decoder.JSONDecodeError as error:
        if force:
            print("WARNING: Unable to process JSON response: " + str(error))
            if verbose:
                print("Warning: URL response = " + url_response)
            return json.loads('[]')
        else:
            print("ERROR: Unable to process JSON response: " + str(error))
            if verbose:
                print("ERROR: URL response = " + url_response)
            return json.loads('[]')
    except Exception as error:
        print("ERROR: Unable to process JSON response: " + str(error))
        if verbose:
            print("ERROR: JSON = " + url_response)
        return json.loads('[]')

    # Return the JSON data
    return json_data

def getHeaderDict():
    # Set up the header for the post request.
    header_dict = {'accept': 'application/json',
                   'Content-Type': 'application/json'}
    return header_dict

def initHTTP():
    # Deafult OS do not have create cient certificate bundles. It is
    # easiest for us to ignore HTTPS certificate errors in this case.
    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
        getattr(ssl, '_create_unverified_context', None)): 
        ssl._create_default_https_context = ssl._create_unverified_context

def generateQuery(field, value):
    query_str = "{ \"filters\": { \"op\":\"contains\", \"content\": { \"field\":\"%s\", \"value\":\"%s\" } }, \"facets\":\"repertoire_id\" }"%(field, value)
    return query_str


def searchCDR3(url, cdr3_file, cdr3_header, verbose):
    # Ensure our HTTP set up has been done.
    initHTTP()
    # Get the HTTP header information (in the form of a dictionary)
    header_dict = getHeaderDict()

    # Open the file that contains the list of CDR3s to search
    try:
        cdr3_df = pd.read_csv(cdr3_file, sep=None, engine='python', encoding='utf-8-sig')
    except Exception as err:
        print("ERROR: Unable to open file %s - %s" % (cdr3_file, err))
        return False

    # Get the CDR3 list from the column header.
    if not cdr3_header in cdr3_df:
        print("ERROR: Could not find header %s in file %s" % (cdr3_header, cdr3_file))
        return False
        
    # Build the full URL combining the URL and the entry point.
    query_url = url

    # Iterate over the CDR3s
    for index, cdr3_row in cdr3_df.iterrows():
        if verbose:
            print("INFO: Looking for CDR3 %s"%(cdr3_row[cdr3_header]))

        cdr3_query = generateQuery("junction_aa", cdr3_row[cdr3_header])

        if verbose:
            print('INFO: Performing query: ' + str(cdr3_query))

        # Perform the query.
        query_json = processQuery(query_url, header_dict, cdr3_query, verbose)
        if verbose:
            print('INFO: Query response: ' + str(query_json))

        # Print out an error if the query failed.
        if len(query_json) == 0:
            print('ERROR: Query %s failed to %s'%(query_json, query_url))
            continue
            return False

        # Check for a correct Info object.
        if not "Info" in query_json:
            print("ERROR: Expected to find an 'Info' object, none found")
            return False

        # Check for a correct Facet object.
        facet_key = "Facet"
        if not facet_key in query_json:
            print("ERROR: Expected to find a 'Facet' object, none found")
            return False

        # Get the Facet array - a facet repsonse looks like this:
        # 'Facet': [{'count': 71, 'repertoire_id': '5ec449f0ba06faa86ec02506'}]
        facet_array = query_json[facet_key ]
        num_responses = len(facet_array)
        total = 0
        if num_responses > 0:
            for repertoire in facet_array:
                total = total + repertoire["count"]
            print("%d: Found %d instances of %s in %d repertoires"%
                  (index, total, cdr3_row[cdr3_header], num_responses),flush=True)

            #print("    Details: %s (%s %s), MHC = %s,%s (%s), Epitope = %s (%s,%s)"%(
            #      cdr3_row["Gene"], cdr3_row["V"], cdr3_row["J"],
            #      cdr3_row["MHC A"], cdr3_row["MHC B"], cdr3_row["MHC class"],
            #      cdr3_row["Epitope"], cdr3_row["Epitope gene"], cdr3_row["Epitope species"]),
            #      flush=True)
        else:
            print("%d: Found %d instances of %s"% (index, total, cdr3_row[cdr3_header]),flush=True)
                  
                   
        time.sleep(0.5)
    return True

    if False:
            # check if facets query
            if query_dict.get('facets'):
                response_tag = "Facet"

            if not response_tag in query_json:
                print("ERROR: Expected to find a '" + response_tag +"' object, none found")
                return 1
        
            query_response_array = query_json[response_tag]
            num_responses = len(query_response_array)

            if not gold_disabled:
                if gold_results.get(query_name):
                    if gold_results[query_name].get('records'):
                        if num_responses != int(gold_results[query_name]['records']):
                            print("ERROR: Expected " + str(gold_results[query_name]['records']) + " != " + str(num_responses) + " records")
                            return 1
                    else:
                        print('WARNING: No expected records specified for ' + query_name)
                else:
                    print('WARNING: No gold expectation for ' + query_name)

            print("INFO: Received " + str(num_responses) + " " + response_tag + "s from query")
            print('PASS: Query file ' + query_file + ' to ' + query_url + ' OK')

    return 0

def getArguments():
    # Set up the command line parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=""
    )

    # A file that contains a list of URLs to send queries to
    parser.add_argument("repository_url_file")
    # A file that contains the repertoire query to send to each repository.
    parser.add_argument("repertoire_search_json")
    # A file that contains the rearrangement query to send to each repository.
    parser.add_argument("rearrangement_search_json")
    # Repertoire entry point to use - should be the normal AIRR reptetoire
    parser.add_argument(
        "--repertoire-api",
        dest="repertoire_api",
        default="/airr/v1/repertoire",
        help="The repertoire API entry point. Defaults to '/airr/v1/repertoire'/")
    # Rearragement entry point to use - should be the normal AIRR rearrangements or 
    # the iR Plus Stats.
    parser.add_argument(
        "--rearrangement-api",
        dest="rerrangement_api",
        default="/airr/v1/rearrangement",
        help="The Rearrangement API entry point. Defaults to '/airr/v1/rearrangement'/"
    )

    # Flag to determine if AIRR Rearrangement or iR+ Stats API should be used.
    parser.add_argument(
        "-s",
        "--stats",
        action="store_true",
        help="Use the Stats API rather than the Rearrangement API.")
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

    # Read in the repository file
    try:
        repository_df = pd.read_csv(options.repository_url_file, sep='\t',
                                    engine='python', encoding='utf-8-sig')
    except Exception as err:
        print("ERROR: Unable to open file %s - %s" % (options.repository_url_file, err))
        sys.exit(1)

    # Open the Repertoire JSON query file.
    with open(options.repertoire_search_json) as f:
        repertoire_json = json.load(f)
    print("Repertoire query = %s"%(repertoire_json))

    # Open the Rearrangement JSON query file.
    with open(options.rearrangement_search_json) as f:
        rearrangement_json = json.load(f)
    print("Rearrangement query = %s"%(rearrangement_json))

    for index, row in repository_df.iterrows():
        print("Row %d: %s"% (index, row['URL']+options.repertoire_api))
        #repertoires = getRepertoires(row['URL']+options.repertoire_api,

    # Perform the query analysis, gives us back a dictionary.
    #success = searchCDR3(options.url, options.cdr3_file,
    #                     options.column_header, options.verbose)
    # Return success if successful
    #if not success:
    #    sys.exit(1)

