import requests
import urllib
import certifi
import pandas as pd
import numpy as np
import argparse
import json
import os, ssl
import sys
import time
import yaml

def getField(dictionary, field_path, verbose):
    field_list = field_path.split(".")
    current_object = dictionary
    for field_name in field_list:
        if field_name in current_object:
            current_object = current_object[field_name]
            if isinstance(current_object, list):
                if verbose:
                    print("Warning: Processing array field %s, first object only"%(field_name))
                current_object = current_object[0]

            current_field = field_name
        else:
            return None, None

    return current_field, current_object

def performRearrangementQuery(rearrangement_url, repertoires,
        rearrangement_dict, repertoire_field_df,
        output_handle, output_directory, output_format,
        service_delay, verbose):

    count = 0
    total = len(repertoires)
    print("Info: Processing %d repertoires from %s" %(total,rearrangement_url))
    if output_format == "JSON":
        print("{\n\"repository\":\"%s\",\n\"results\":["%(rearrangement_url), file=output_handle)

    t_start = time.perf_counter()
    for repertoire in repertoires:
        repertoire_id = repertoire['repertoire_id']
        query_dict = generateRearrangementQuery(repertoire_id, rearrangement_dict)
        query_response = processQuery(rearrangement_url, query_dict, output_format, verbose)
        # Print out an error if the query failed.
        if query_response == None:
            print('ERROR: Query %s failed to %s'%(query_dict, rearrangement_url))
            continue

        count = count + 1
        if verbose:
            print('Processing %d'%(count))

        if output_format == "JSON":
            repertoire_info = dict()
            for index, row in repertoire_field_df.iterrows():
                field, value = getField(repertoire, row[0], verbose)
                if not field == None:
                    repertoire_info[row[0]] = value
                    #print("\"%s\":\"%s\","%(field, value), file=output_handle)
            query_response["Repertoire"] = repertoire_info
            print("%s"%(json.dumps(query_response, indent = 4)), file=output_handle)
            if count < total:
                print(",", file=output_handle)
        else:

            # We only want to output a file if there is some data.
            # Get the lines. Note this is not memory efficient for large files.
            lines = query_response.splitlines()

            # We want to remove empty lines at the end. Some repositories return
            # empty lines (VDJServer does).
            index = len(lines) - 1
            # Traverse the list in reverse until we find a non-empty line
            while index >= 0 and lines[index].strip() == '':
                index -= 1
            # Remove the n empty lines at the end of the file.
            lines = lines[:index + 1]

            if len(lines) > 1:
                url_info = urllib.parse.urlparse(rearrangement_url)
                filename = url_info.netloc + '_' + repertoire_id + '.tsv'
                try:
                    tsv_handle = open(output_dir + filename, "w")
                except Exception as err:
                    print("ERROR: Unable to open output file %s - %s" %
                          (filename, err))
                    sys.exit(1)
                print("%s"%(query_response), file=tsv_handle)
                tsv_handle.close()

                print("repository", end='', file=output_handle)
                for index, row in repertoire_field_df.iterrows():
                    field, value = getField(repertoire, row[0], verbose)
                    if not field == None:
                        print("\t%s"%(row[0]), end='', file=output_handle)
                print("", file=output_handle)

                print(url_info.netloc, end='', file=output_handle)
                for index, row in repertoire_field_df.iterrows():
                    field, value = getField(repertoire, row[0], verbose)
                    if not field == None:
                        print("\t%s"%(value), end='', file=output_handle)
                print("", file=output_handle)

        time.sleep(service_delay)

    
    if output_format == "JSON":
        print("]\n}", file=output_handle, flush=True)
    t_end = time.perf_counter()
    print("Info: Performed %d queries in %f s, %f queries/s" %
          (count, t_end - t_start, count/(t_end - t_start)))

def processQuery(query_url, query_dict, output_format, verbose):

    # Perform delay when queries fail with HTTP 429 (too
    # many requests) failure.
    success = False
    tries = 0
    max_tries = 10
    sleep_time = 5
    json_data = {}

    # While we don't have a success and we haven't hit our maximum
    # number of tries, keep trying. Eventually after max_tries we
    # give up.
    while tries < max_tries and success == False:

        # Do a post request
        url_response = requests.post(query_url, json=query_dict)
        tries = tries + 1
        success = True
        if verbose:
            print("IR-INFO: HTTP Response status code = %d"%(url_response.status_code))

        # If it is a 429 error, sleep and then retry. Otherwise just fail.
        if url_response.status_code == 429:
            print("IR-INFO: Unable to process JSON response (tries = %d)"%(tries))
            print("IR-INFO: Reason = %s (status code = %d)"%(url_response.reason, url_response.status_code))
            print("IR-INFO: Retrying after delay")
            success = False
            time.sleep(sleep_time)
        elif output_format == "JSON":
            # Get the JSON data as a dictionary.
            try:
                json_data = url_response.json()
                success = True
            except json.decoder.JSONDecodeError as error:
                print("ERROR: Unable to process JSON response: " + str(error))
                print("ERROR: Status code = %s"%(url_response.status_code))
                print("ERROR: Reason = %s"%(url_response.reason))
                if verbose:
                    print("ERROR: Query = " + str(query_dict))
                return None
            except Exception as error:
                print("ERROR: Unable to process JSON response: " + str(error))
                print("ERROR: Status code = %s"%(url_response.status_code))
                print("ERROR: Reason = %s"%(url_response.reason))
                if verbose:
                    print("ERROR: Query = " + str(query_dict))
                return None

    # Return the data if successful, None otherwise
    if not success:
        print("IR-ERROR: Unable to make connection after %d tries: "%(max_tries))
        return None
    else:
        if output_format == "JSON":
            return json_data
        else:
            return url_response.content.decode('utf-8')

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

def generateRearrangementQuery(repertoire_id, query_dict):
    # Create a new query
    query_with_repertoire = dict()
    if "filters" in query_dict:
        # Add an and clause that contains the repertoire_id and the original query
        and_filter_list = []
        and_filter_list.append({ "op":"=", "content": { "field":"repertoire_id", "value":str(repertoire_id) }})
        and_filter_list.append(query_dict["filters"])
    
        query_with_repertoire = {"filters": { "op":"and", "content": and_filter_list}}
    else:
        query_with_repertoire = {"filters": {"op":"=", "content": { "field":"repertoire_id", "value":str(repertoire_id) }}}

    #query_with_repertoire["filters"]["content"].append({ "op":"=", "content": { "field":"repertoire_id", "value":str(repertoire_id) }}, original_filter ] }}

    # Copy any other query info other than filters (e.g. facets, from, size etc)
    for query_field in query_dict:
        if not query_field == "filters":
            query_with_repertoire[query_field] = query_dict[query_field]

    # Return the new response
    return query_with_repertoire


def getRepertoires(repertoire_url, repertoire_dict, output_handle, verbose):
    # Ensure our HTTP set up has been done.
    initHTTP()
    # Get the HTTP header information (in the form of a dictionary)
    header_dict = getHeaderDict()

    #if verbose:
    #    print('INFO: Query: ' + str(repertoire_dict))
    # Perform the query.
    query_json = processQuery(repertoire_url, repertoire_dict, "JSON", verbose)
    #if verbose:
    #    print('INFO: Query response: ' + str(query_json))

    # Print out an error if the query failed, return empty list if error
    if query_json == None:
        print('ERROR: Query %s failed to %s'%(query_json, repertoire_url))
        return []

    # Check for a correct Info object, return empty list if error
    if not "Info" in query_json:
        print("ERROR: Expected to find an 'Info' object, none found")
        return []

    # Check for a valid Repertoire object, return empty list if error
    if not "Repertoire" in query_json:
        print("ERROR: Expected to find an 'Repertoire' object, none found")
        return []

    repertoire_list = query_json['Repertoire']

    return repertoire_list


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
        "--repertoire_api",
        dest="repertoire_api",
        default="/airr/v1/repertoire",
        help="The repertoire API entry point. Defaults to '/airr/v1/repertoire'/")
    # Rearragement entry point to use - should be the normal AIRR rearrangements or 
    # the iR Plus Stats.
    parser.add_argument(
        "--rearrangement_api",
        dest="rearrangement_api",
        default="/airr/v1/rearrangement",
        help="The Rearrangement API entry point. Defaults to '/airr/v1/rearrangement'/"
    )
    # Field file
    parser.add_argument(
        "--field_file",
        dest="field_file",
        default=None,
        help="File that contains a list of AIRR fields in dot notation (subject.subject_id). These fields are output in every repertoire query output in a 'Repertoire' object. If no file is provided then an empty repertoire object is created."
    )
    # Output file.
    parser.add_argument(
        "--output_file",
        dest="output_file",
        default=None,
        help="The output file to use. If none supplied, uses stdout."
    )
    # Output directory. Used only if TSV output is chosen.
    parser.add_argument(
        "--output_dir",
        dest="output_dir",
        default="",
        help="The output directory to use. Should have a trailing slash if a path is provided."
    )
    # Output format
    parser.add_argument(
        "--output_format",
        dest="output_format",
        default="JSON",
        help="The output format to use. If none supplied, uses JSON."
    )

    # Choose a time delay between repertoire queries. This is so we can be nice
    # to the service and not inundate it with queries. Note the service will
    # reject queries if we go too fast, so this may or may not be needed.
    parser.add_argument(
        "--service_delay",
        dest="service_delay",
        default=0.2,
        type=float,
        help="The service delay to use between rearrangement queries. If we go too fast the serive may reject queries with an error. Default = 0.2"
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

    # Check the file output format options, it should be either
    # JSON or TSV.
    if options.output_format != "JSON" and options.output_format != "TSV":
        print("ERROR: Invalid output format %s, should be JSON or TSV"%(options.output_format, err))
        sys.exit(1)

    # Get the output information. If JSON output, everything goes in
    # the JSON file. If TSV output, repertoire info goes in the JSON
    # file and the TSV data goes in a file per repertoire in the
    # output_dir.
    if options.output_file == None:
        output_handle = sys.stdout
    else:
        try:
            output_handle = open(options.output_file, "w")
        except Exception as err:
            print("ERROR: Unable to open output file %s - %s" %
                  (options.output_file, err))
            sys.exit(1)
    if options.output_format == "TSV":
        output_dir = options.output_dir
        if not os.path.isdir(output_dir):
            print("ERROR: %s is not a directory" % (output_dir))
            sys.exit(1)
    else:
        output_dir = None


    # Read in the repertoire field file
    if options.field_file is None:
        repertoire_field_df = pd.DataFrame([]) 
    else:
        try:
            repertoire_field_df = pd.read_csv(options.field_file, sep='\t',
                                        engine='python', encoding='utf-8-sig')
        except Exception as err:
            print("ERROR: Unable to open file %s - %s" % (options.repository_url_file, err))
            sys.exit(1)

    # Read in the repository file
    try:
        repository_df = pd.read_csv(options.repository_url_file, sep='\t',
                                    engine='python', encoding='utf-8-sig')
    except Exception as err:
        print("ERROR: Unable to open file %s - %s" % (options.repository_url_file, err))
        sys.exit(1)

    # Open the Repertoire JSON query file.
    with open(options.repertoire_search_json) as f:
        repertoire_dict = json.load(f)
        repertoire_json = str(repertoire_dict)
    if options.verbose:
        print("Repertoire query = %s"%(repertoire_json))

    # Open the Rearrangement JSON query file.
    with open(options.rearrangement_search_json) as f:
        rearrangement_dict = json.load(f)
        rearrangement_json = str(rearrangement_dict)
    if options.verbose:
        print("Rearrangement query = %s"%(rearrangement_json))

    repo_count = 0
    if options.output_format == "JSON":
        print("[", file=output_handle)
    number_repos = len(repository_df.index)
    for index, row in repository_df.iterrows():
        if options.verbose:
            print("Row %d: %s"% (index, row['URL']+options.repertoire_api))
        repertoires = getRepertoires(row['URL']+options.repertoire_api,
                repertoire_dict, output_handle, options.verbose)

        if not repertoires == None:
            performRearrangementQuery(row['URL']+options.rearrangement_api,
                    repertoires, rearrangement_dict, repertoire_field_df,
                    output_handle, output_dir, options.output_format,
                    options.service_delay, options.verbose)
        repo_count = repo_count+1
        if options.output_format == "JSON":
            if repo_count < number_repos:
                print(",", file=output_handle)

    if options.output_format == "JSON":
        print("]", file=output_handle)
    #if not success:
    #    sys.exit(1)

