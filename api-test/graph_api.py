import urllib.request, urllib.parse
import argparse
import json
import os, ssl
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict

def getSequenceSummary(sequence_url, header_dict, query_dict={}):
    # Build the required JSON data for the post request. The user
    # of the function provides both the header and the query data
    url_dict = dict()
    url_dict.update(header_dict)
    url_dict.update(query_dict)
    url_data = urllib.parse.urlencode(url_dict).encode()

    # Try to make the connection and get a response.
    try:
        response = urllib.request.urlopen(sequence_url, data=url_data)
        url_response = response.read().decode(response.headers.get_content_charset())
    except urllib.error.HTTPError as e:
        print('Error: Server could not fullfil the request')
        print('Error: Error code =', e.code)
        print(e.read())
        return json.loads('[]')
    except urllib.error.URLError as e:
        print('Error: Failed to reach the server')
        print('Error: Reason =', e.reason)
        return json.loads('[]')
    
    # Convert the response to JSON so we can process it easily.
    json_data = json.loads(url_response)
    
    # Print out the summary stats for the repository.
    sample_summary = json_data['summary']

    # Return the JSON of the results.
    return sample_summary

def getSamples(sample_url, header_dict, query_dict={}):
    # Build the required JSON data for the post request. The user
    # of the function provides both the header and the query data
    url_dict = dict()
    url_dict.update(header_dict)
    url_dict.update(query_dict)
    url_data = urllib.parse.urlencode(url_dict).encode()

    # Try to connect the URL and get a response. On error return an
    # empty JSON array.
    try:
        response = urllib.request.urlopen(sample_url, data=url_data)
        url_response = response.read().decode(response.headers.get_content_charset())
    except urllib.error.HTTPError as e:
        print('Error: Server could not fullfil the request')
        print('Error: Error code =', e.code)
        print(e.read())
        return json.loads('[]')
    except urllib.error.URLError as e:
        print('Error: Failed to reach the server')
        print('Error: Reason =', e.reason)
        return json.loads('[]')

    # Convert the response to JSON so we can process it easily.
    print(url_response)
    json_data = json.loads(url_response)
    # Return the JSON data
    return json_data

def getHeaderDict():
    # Set up the header for the post request.
    header_dict = {'accept': 'application/json',
                   'Content-Type': 'application/x-www-form-urlencoded'}
    return header_dict

def initHTTP():
    # Deafult OS do not have create cient certificate bundles. It is
    # easiest for us to ignore HTTPS certificate errors in this case.
    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
        getattr(ssl, '_create_unverified_context', None)): 
        ssl._create_default_https_context = ssl._create_unverified_context

# Set the base URL to use 
#base_url = 'https://ipa1.ireceptor.org'
#base_url = 'https://ipa2.ireceptor.org'
#base_url = 'https://ipa3.ireceptor.org'
#base_url = 'https://ipa4.ireceptor.org'
#base_url = 'https://vdjserver.org/ireceptor'
#base_url = 'http://turnkey-test2.ireceptor.org'

# Junction AA length queries.
#query_key = 'junction_aa_length'
#query_values = range(40)

# Possible v_call queries
#query_key = 'v_call'
#query_values = ['IGHV1','IGHV2','IGHV3','IGHV4','IGHV5','IGHV6','IGHV7']
#query_key = 'd_call'
#query_values = ['IGHD1','IGHD2','IGHD3','IGHD4','IGHD5','IGHD6','IGHD7']
#query_values = ['TRBV1','TRBV2','TRBV3','TRBV4','TRBV5','TRBV6','TRBV7','TRBV8']

def performQueryAnalysis(base_url, query_key, query_values):
    # Ensure our HTTP set up has been done.
    initHTTP()
    # Get the HTTP header information (on the form of a dictionary)
    header_dict = getHeaderDict()

    # Select the API entry points to use, based on the base URL provided
    sample_url = base_url+'/v2/samples'
    sequence_url = base_url+'/v2/sequences_summary'

    sample_json = getSamples(sample_url, header_dict)
    sample_dict = dict()
    for sample in sample_json:
        sample_dict[str(sample['_id'])] = dict()

    # Iterate over the query values of interest. One query per value gives us results
    # for all samples so this is about as efficient as it gets.
    for value in query_values:
        query_dict = dict()
        query_dict.update({query_key: value})
        sequence_summary_json = getSequenceSummary(sequence_url, header_dict, query_dict)
        result = {}
        for sample in sequence_summary_json:
            # Get the dictionaries of values for this sample
            value_dict = sample_dict[str(sample['_id'])]
            # Update the count for the value we are considering
            #pair = {sample['ir_filtered_sequence_count'], sample['sample_id']}
            #value_dict.update({value:pair})
            filtered_sequence_count = sample['ir_filtered_sequence_count']
            value_dict.update({value:filtered_sequence_count})
            sample_dict[str(sample['_id'])] = value_dict
            #result[sample['_id'], value] = pair
            print('   ' + query_key + ' ' + str(value) + ' = ' + str(sample['ir_filtered_sequence_count']))

    data = dict()
    grand_total = 0
    for sample in sample_json:
        value_dict = sample_dict[str(sample['_id'])] 
        sequence_count = sample['ir_sequence_count']
        print('\nsample = ' + sample['sample_id'] + ' (' + str(sequence_count) + ')')
        total = 0
        for key, value in value_dict.items():
            if key in data:
                data.update({key:data[key]+value})
            else:
                data.update({key:value})
            print(str(key) + ' = ' + str(value) + ' (' + '%.2f' % ((value/sequence_count)*100.0) + '%)')
            total = total + value
            grand_total = grand_total + value
        print('sample = ' + sample['sample_id'] + ' (' + str(total) + ')')
        
    for key, value in data.items():
        print(str(key) + ' = ' + str(value))
    print('grand total = ' + str(grand_total))

    return data

def plotData(plot_names, plot_data, title, filename):
    #plot_data = list(data.values())
    #plot_names = list(data.keys())

    plt.rcParams.update({'figure.autolayout': True})
    fig, ax = plt.subplots()
    ax.barh(plot_names, plot_data)

    fig.savefig(filename, transparent=False, dpi=80, bbox_inches="tight")

def getArguments():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Note: for proper data processing, project --samples metadata should\n" +
        "generally be read first into the database before loading other data types."
    )

    parser.add_argument("api_field")
    parser.add_argument("graph_values")
    parser.add_argument("base_url")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Run the program in verbose mode. This option will generate a lot of output, but is recommended from a data provenance perspective as it will inform you of how it mapped input data columns into repository columns.")

    # Add configuration options
    #config_group = parser.add_argument_group("Configuration file options", "")
    #config_group.add_argument(
    #    "--mapfile",
    #    dest="mapfile",
    #    default="ireceptor.cfg",
    #    help="the iReceptor configuration file. Defaults to 'ireceptor.cfg' in the local directory where the command is run. This file contains the mappings between the AIRR Community field definitions, the annotation tool field definitions, and the fields and their names that are stored in the repository."
    #)

    options = parser.parse_args()
    return options


if __name__ == "__main__":
    # Get the command line arguments.
    options = getArguments()
    # Split the comma separated input string.
    values = options.graph_values.split(',')
    # Perform the query analysis, gives us back a dictionary.
    data = performQueryAnalysis(options.base_url, options.api_field, values)
    sorted_data = OrderedDict(sorted(data.items(), key=lambda t: t[0]))
    # Graph the results
    title = options.api_field
    filename = options.api_field + ".png"
    plotData(list(sorted_data.keys()), list(sorted_data.values()), title, filename)

    # Return success
    sys.exit(0)

