import urllib.request, urllib.parse
import pandas as pd
import numpy as np
import argparse
import pprint
import json
from json2html import *
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

def generateFacetsQuery(field, value):
    query_str = "{ \"filters\": { \"op\":\"contains\", \"content\": { \"field\":\"%s\", \"value\":\"%s\" } }, \"facets\":\"repertoire_id\" }"%(field, value)
    return query_str
 
def generateQuery(field, value):
    query_str = "{ \"filters\": { \"op\":\"contains\", \"content\": { \"field\":\"%s\", \"value\":\"%s\" } } }"%(field, value)
    return query_str


def studySummary(url, study_file, study_header, json_output, html_output, irplus_output, verbose):
    # Ensure our HTTP set up has been done.
    initHTTP()
    # Get the HTTP header information (in the form of a dictionary)
    header_dict = getHeaderDict()

    # Open the file that contains the list of studies to search
    try:
        study_df = pd.read_csv(study_file, sep='\t', engine='python', encoding='utf-8-sig')
    except Exception as err:
        print("ERROR: Unable to open file %s - %s" % (study_file, err))
        return False

    # Get the study list from the column header.
    if not study_header in study_df:
        print("ERROR: Could not find header %s in file %s" % (study_header, study_file))
        return False
        
    # Build the full URL combining the URL and the entry point.
    query_url = url

    # Create a dictionary to track all of our studies.
    study_list_dict = dict()

    # Iterate over the studies
    for index, study_row in study_df.iterrows():
        study_id = study_row[study_header]
        if verbose:
            print("INFO: Looking for study %s"%(study_id))

        study_query = generateQuery("study.study_id", study_id)

        if verbose:
            print('INFO: Performing query: ' + str(study_query))

        # Perform the query to get all of the Repertoires for the study.
        query_json = processQuery(query_url, header_dict, study_query, verbose)
        if verbose:
            print('INFO: Query response: ' + str(query_json))

        # Print out an error if the query failed.
        if len(query_json) == 0:
            print('ERROR: Query %s failed to %s'%(query_json, query_url))
            return False

        # Check for a correct Info object.
        if not "Info" in query_json:
            print("ERROR: Expected to find an 'Info' object, none found")
            return False

        # Check for a correct Repertoire object.
        repertoire_key = "Repertoire"
        if not repertoire_key in query_json:
            print("ERROR: Expected to find a 'Repertoire' object, none found")
            return False

        # Get the Repertoire array 
        repertoire_array = query_json[repertoire_key]

        num_responses = len(repertoire_array)
        if num_responses > 0:
            study_dict = dict()
            if study_id not in study_list_dict:
                study_list_dict[study_id] = study_dict 

            study_dict['subjects'] = dict()

            total = 0

            # Initialize the fields
            keywords_study = []
            cell_subset = []
            pcr_target_locus = []
            forward_pcr_primer_target_location = []
            reverse_pcr_primer_target_location = []
            template_class = []
            library_generation_method = []
            subject_list = []
            sample_list = []
            data_processing_protocols = []
            software_versions = []
            germline_database = []
            paired_reads_assembly = []
            quality_thresholds = []
            primer_match_cutoffs = []
            collapsing_method = []
            
            for repertoire in repertoire_array:
                repertoire_id = repertoire['repertoire_id']
                study_json = repertoire['study']
                subject_json = repertoire['subject']

                # Handle the field where there is one per study
                if total == 0:
                    if 'study_id' in study_json:
                        study_id = study_json['study_id']
                    if 'pub_ids' in study_json:
                        pub_ids = study_json['pub_ids']

                if 'keywords_study' in study_json and not study_json['keywords_study'] in keywords_study:
                    keywords_study.append(study_json['keywords_study'])
                if 'subject_id' in subject_json and not subject_json['subject_id'] in subject_list:
                    subject_list.append(subject_json['subject_id'])

                if 'subject_id' in subject_json:
                    subject_id = subject_json['subject_id']
                    if not subject_id in study_dict['subjects']:
                        subject_dict = dict()
                        subject_dict['samples'] = dict()
                        study_dict['study_title'] = study_json['study_title']
                        study_dict['pub_ids'] = study_json['pub_ids']
                        study_dict['subjects'][subject_id] = subject_dict
                    else:
                        subject_dict = study_dict['subjects'][subject_id]

                # For each sample...
                for sample_json in repertoire['sample']:
                    if 'sample_id' in sample_json:
                        sample_id = sample_json['sample_id']
                        sample_dict = dict()
                        if not sample_id in subject_dict['samples']:
                            sample_dict = dict()
                            subject_dict['samples'][sample_id] = sample_dict
                        else:
                            sample_dict = subject_dict['samples'][sample_id]

                    if total == 0:
                        if 'sequencing_platform' in sample_json:
                            sequencing_platform = sample_json['sequencing_platform']
                    if ('cell_subset' in sample_json and 
                        'label' in sample_json['cell_subset'] and
                        not sample_json['cell_subset']['label'] is None and
                        not sample_json['cell_subset']['label'] in cell_subset):
                        cell_subset.append(sample_json['cell_subset']['label'])

                    if 'library_generation_method' in sample_json and not sample_json['library_generation_method'] in library_generation_method:
                        library_generation_method.append(sample_json['library_generation_method'])
                    if 'template_class' in sample_json and not sample_json['template_class'] in template_class:
                        template_class.append(sample_json['template_class'])
                    if 'sample_id' in sample_json and not sample_json['sample_id'] in sample_list:
                        sample_list.append(sample_json['sample_id'])

                    # Handle the pcr_target (we assume one and only one)
                    pcr_target = sample_json['pcr_target'][0]
                    if 'pcr_target_locus' in pcr_target and not pcr_target['pcr_target_locus'] in pcr_target_locus:
                        pcr_target_locus.append(pcr_target['pcr_target_locus'])
                    if 'forward_pcr_primer_target_location' in pcr_target and not pcr_target['forward_pcr_primer_target_location'] in forward_pcr_primer_target_location:
                        forward_pcr_primer_target_location.append(pcr_target['forward_pcr_primer_target_location'])
                    if 'reverse_pcr_primer_target_location' in pcr_target and not pcr_target['reverse_pcr_primer_target_location'] in reverse_pcr_primer_target_location:
                        reverse_pcr_primer_target_location.append(pcr_target['reverse_pcr_primer_target_location'])

                # Handle data_processing (we assume one)
                data_processing = repertoire['data_processing'][0]
                if total == 0:
                    if 'data_processing_protocols' in data_processing:
                        data_processing_protocols = data_processing['data_processing_protocols']  
                    if 'software_versions' in data_processing:
                        software_versions = data_processing['software_versions']  
                    if 'germline_database' in data_processing:
                        germline_database = data_processing['germline_database']  
                    if 'paired_reads_assembly' in data_processing:
                        paired_reads_assembly = data_processing['paired_reads_assembly']  
                    if 'quality_thresholds' in data_processing:
                        quality_thresholds = data_processing['quality_thresholds']  
                    if 'primer_match_cutoffs' in data_processing:
                        primer_match_cutoffs = data_processing['primer_match_cutoffs']  
                    if 'collapsing_method' in data_processing:
                        collapsing_method = data_processing['collapsing_method']  


                total = total + 1
                
            num_subjects = len(subject_list)
            if irplus_output:
                print("%s\t%s\t%s\t%s\t%d\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s/%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s"%
                     (study_row[study_header], keywords_study,
                      cell_subset, pcr_target_locus, num_subjects,
                      num_responses, template_class,
                      library_generation_method,
                      "null",
                      forward_pcr_primer_target_location,
                      reverse_pcr_primer_target_location,
                      "Bulk",
                      pub_ids, study_id, sequencing_platform,
                      "null",
                      query_url, repertoire_id,
                      "null",
                      "null",
                      data_processing_protocols,
                      "null",
                      software_versions, germline_database, paired_reads_assembly,
                      quality_thresholds, primer_match_cutoffs, collapsing_method
                      ))
        else:
            print("Error: Could not find study %s in %s"%
                  (study_row[study_header],query_url))
            print(query_json)
            return False
                  
                   
        time.sleep(0.5)

    #print(study_list_dict)
    if html_output: 
        print("<!DOCTYPE html>\n<html>\n<head>\n<style>")
        print("table { border: 0px; border-collapse: collapse; text-align: left; vertical-align: top;}")
        print("td { border: 0px; border-collapse: collapse; text-align: left; vertical-align: top;}")
        print("th { border: 0px; border-collapse: collapse; text-align: left; vertical-align: top;}")
        print("</style>")
        print("</head>\n<body>")
        json_table = json2html.convert(json = study_list_dict, table_attributes="")
        print(json_table)
        print("</body>\n</html>")

    if json_output: 
        print(json.dumps(study_list_dict, sort_keys=True, indent=4))
    return True

def getArguments():
    # Set up the command line parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=""
    )
    parser = argparse.ArgumentParser()

    # The URL for the repository to test
    parser.add_argument("url")
    # The API entry point to use
    parser.add_argument("study_file")
    # Comma separated list of query files to test.
    parser.add_argument("column_header")
    # Output JSON
    parser.add_argument(
        "--json_output",
        action="store_true",
        help="Output the study summaries in JSON")
    # Output HTML
    parser.add_argument(
        "--html_output",
        action="store_true",
        help="Output the study summaries in an HTML table")
    # Output iRPlus table format
    parser.add_argument(
        "--irplus_output",
        action="store_true",
        help="Output the study summaries in iRPlus table format")
    # Verbosity flag
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Run the program in verbose mode.")

    # Parse the command line arguements.
    options = parser.parse_args()
    return options

# Search the given ADC API repoistory for a set of studys from a column in a file
# that contains a study ID, give us back a summary of each study.
if __name__ == "__main__":
    # Get the command line arguments.
    options = getArguments()
    # Perform the query analysis
    success = studySummary(options.url, options.study_file,
                           options.column_header, 
                           options.json_output, options.html_output, options.irplus_output,
                           options.verbose)
    # Return success if successful
    if not success:
        sys.exit(1)

