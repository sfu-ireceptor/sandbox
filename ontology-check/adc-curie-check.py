
import requests
import collections
import argparse
import yaml
import json
import sys
import airr
import pandas as pd
from airr.schema import Schema


def processGetQuery(query_url, verbose):

    # Do a post request
    url_response = requests.get(query_url)

    # Get the JSON data as a dictionary.
    try:
        json_data = url_response.json()
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

    # Return the JSON data
    return json_data


def processPostQuery(query_url, query_dict, verbose):

    # Do a post request
    url_response = requests.post(query_url, json=query_dict)

    # Get the JSON data as a dictionary.
    try:
        json_data = url_response.json()
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

    # Return the JSON data
    return json_data


def getOntologyIRIs(verbose):
    block = 'CURIEMap'
    # Use the AIRR library to get an AIRR Schema information for the block.
    ontology_iri_dict = {}
    curie_schema = Schema(block)
    for curie, values in curie_schema.properties.items():
        if values['type'] == 'ontology' or values['type'] == 'taxonomy':
            ontology_iri_dict[curie] = values['map']['OBO']['iri_prefix']
            if verbose:
                print('### %s IRI = %s'%(curie, ontology_iri_dict[curie]))
        else:
            if verbose:
                print('Warning: Can not check %s %s using OLS'%(values['type'], curie))

    return ontology_iri_dict


def getProviderURLs(verbose):

    block = 'InformationProvider'
    # Use the AIRR library to get an AIRR Schema block for the current block.
    provider_schema = Schema(block)

    # Get the two main objects in the schema, providers and parameters
    providers = provider_schema.properties['provider']
    parameters = provider_schema.properties['parameter']

    # Confirm that there is an OLS provider (all we support)
    if not 'OLS' in providers:
        print('ERROR: No OLS in the list of providers')
        return []

    # Make sure the expected OLS fields are present
    if not 'request' in providers['OLS']:
        print('ERROR: Malformed OLS object, expecting request field')
        return []

    if not 'url' in providers['OLS']['request']:
        print('ERROR: Malformed OLS object, expecting request.url field')
        return []

    # Get the URL template
    ols_url_template = providers['OLS']['request']['url']
    if verbose:
        print('### OLS url template = %s'%(ols_url_template))

    # Loop over the parameter items and build a URL for each onotology
    ontology_url_dict = {}
    for ontology, parameter in parameters.items():
        if 'OLS' in parameter:
            ontology_url_dict[ontology] = ols_url_template.replace('{ontology_id}',parameter['OLS']['ontology_id'])
            if verbose:
                print('### %s OLS URL = %s'%(ontology, ontology_url_dict[ontology]))
        else:
            print('WARNING: Could not find an OLS parameter for %s'%(ontology))

    # Return a dictionary with the OLS URLs
    return ontology_url_dict

def checkOntologyLabel(curie, curie_label, ontology_iri_dict, ontology_url_dict, verbose):

    # Check to see if the CURIE is None. This is valid if and only if both the curie and
    # the label are None.
    if curie is None:
        if curie_label is None:
            return True
        else:
            print('ERROR: Invalid Null CURIE with label set to %s'%(curie_label))
            return False

    # CURIEs are of the form NCBITAXON:9606. They have two elements split by a ":"
    curie_array = curie.split(':')
    if len(curie_array) != 2:
        print('ERROR: Invalid CURIE %s'%(curie))
        return False

    # Get the prefic and ID value.
    curie_prefix = curie_array[0]
    curie_value = curie_array[1]

    # Check to see if the CURIE prefic can be looked up as an IRI and
    # as an OLS query
    if not curie_prefix in ontology_iri_dict:
        print('ERROR: Curie prefix %s not in IRI list'%(curie_prefix))
        return False
    if not curie_prefix in ontology_url_dict:
        print('ERROR: Curie prefix %s not in URL list'%(curie_prefix))
        return False

    # Build the query by replacing the '{iri} text with the IRI info
    query_iri = ontology_iri_dict[curie_prefix]+str(curie_value)
    query = ontology_url_dict[curie_prefix].replace('{iri}',query_iri)
    if verbose:
        print('### Query = %s'%(query))

    # Perform the query
    response = processGetQuery(query, verbose)

    # Process the response. OBO query repsonses have the ontology label in the field
    # _embeded.terms.label
    obo_terms = response['_embedded']['terms']
    for term in obo_terms:
        if term['label'] == curie_label:
            if verbose:
                print('### CURIE MATCHES (%s, %s)'%(term['label'], curie_label))
            return True

    print('ERROR: Invalid CURIE/label: %s, %s, correct label = %s'%(curie, curie_label, term['label']))
    return False

def getField(dictionary, field_path, verbose):
    field_list = field_path.split(".")
    current_object = dictionary
    for field_name in field_list:
        if field_name in current_object:
            current_object = current_object[field_name]
            if isinstance(current_object, list):
                if verbose:
                    print("Warning: Processing array field, first object only")
                current_object = current_object[0]

            current_field = field_name
        else:
            return None, None

    return current_field, current_object

def processRepository( repertoire_api, repertoire_field_df,
                       ontology_iri_dict, ontology_url_dict,
                       verbose):
    # Perform the query. We want all repertoires so no query dictionary
    repertoire_dict = {}
    query_json = processPostQuery(repertoire_api, repertoire_dict, verbose)

    # Print out an error if the query failed.
    if query_json == None:
        print('ERROR: Query %s failed to %s'%(query_json, repertoire_url))
        return None

    # Check for a correct Info object.
    if not "Info" in query_json:
        print("ERROR: Expected to find an 'Info' object, none found")
        return None

    # Check for a valid Repertoire object
    if not "Repertoire" in query_json:
        print("ERROR: Expected to find an 'Repertoire' object, none found")
        return None

    # Loop over all of the Repertoires returned by the query.
    invalid_curies = 0
    total_curies = 0
    for repertoire in query_json['Repertoire']:
        print('Info: Processing repertoire %s'%(repertoire['repertoire_id']))
        # For each field, check to see if it is a valid ontology
        for index, row in repertoire_field_df.iterrows():

            # Get the field_object from the reperotire with the given field name
            field, field_object = getField(repertoire,row['Field'],verbose)
            if verbose:
                print('Checking field %s = %s'%(field, field_object))
            
            # Check to see if the repertoire has the field. If not then don't do
            # anything - we only report errors if it has a CURIE and it is not a 
            # valid one...
            if field is None or field_object is None:
                continue

            # Check to see if the returned object is valid. If it is an AIRR ontology
            # it should be a dictionary object with an 'id' and 'label' field.
            valid_curie = False
            if isinstance(field_object, dict):
                # Check for an empty dict object, with no id and label. This is valid 
                # and we don't want to do anything. If we have one field and not the
                # other it is invalid.
                if not 'id' in field_object and not 'label' in field_object:
                    continue
                elif not 'id' in field_object:
                    print('FAIL: field %s does not have an ontology id'%(field))
                    print('FAIL: field_ibject = %s'%(field_object))
                elif not 'label' in field_object:
                    print('FAIL: field %s does not have an ontology id'%(field))
                    print('FAIL: field_ibject = %s'%(field_object))
                else:
                    # If it is valid, we should check to ensure that the CURIE and
                    # the label match according to the external ontology provider.
                    valid_curie = checkOntologyLabel(field_object['id'], field_object['label'], ontology_iri_dict, ontology_url_dict, verbose)
            else:
                print('FAIL: field %s is not a compound object (id, label)'%(field))

            # Keep track of total and failed CURIEs.
            total_curies = total_curies+1
            if not valid_curie:
                invalid_curies = invalid_curies + 1

    return invalid_curies


def getArguments():
    # Set up the command line parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=""
    )

    # A file that contains a list of URLs to send queries to
    parser.add_argument("repository_url_file")
    # Field file
    parser.add_argument(
        dest="field_file",
        default=None,
        help="File that contains a list of AIRR fields in dot notation (subject.subject_id). These fields are checked to determine if they are valid ontology fields."
    )
    # Repertoire entry point to use - should be the normal AIRR reptetoire
    parser.add_argument(
        "--repertoire_api",
        dest="repertoire_api",
        default="/airr/v1/repertoire",
        help="The repertoire API entry point. Defaults to '/airr/v1/repertoire'/")

    #parser.add_argument("curie")
    #parser.add_argument("curie_label")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Run the program in verbose mode. This option will generate debug output and may cause a problem with using the config file as a TSV file.")


    # Parse the command line arguements.
    options = parser.parse_args()
    return options

if __name__ == "__main__":
    # Get the command line arguments.
    options = getArguments()

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

    # Get the IRI and URL info, both dictionaries keyed on CURIE prefix
    ontology_iri_dict = getOntologyIRIs(options.verbose)
    ontology_url_dict = getProviderURLs(options.verbose)

    # Iterate over the repositories
    for index, row in repository_df.iterrows():
        if options.verbose:
            print("Row %d: %s"% (index, row['URL']+options.repertoire_api))
        num = processRepository(row['URL']+options.repertoire_api,
                repertoire_field_df, ontology_iri_dict, ontology_url_dict,
                options.verbose)
        print('Info: Number of invlaid CURIEs in %s = %d'%(row['URL'],num))
    valid = True

    # Check the value of the CURIE
    #valid_curie = checkOntologyLabel(options.curie, options.curie_label,
    #                                 ontology_iri_dict, ontology_url_dict,
    #                                 options.verbose)
    # Print an exit code based on whether the test passed or failed
    if valid:
        #print('Valid CURIE and label: %s, %s'%(options.curie, options.curie_label))
        sys.exit(0)
    else:
        sys.exit(1)


