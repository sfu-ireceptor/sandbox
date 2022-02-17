
import requests
import collections
import argparse
import yaml
import json
import sys
import airr
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
    if verbose:
        print("#### getProviders %s\n"%(block))
    # Use the AIRR library to get an AIRR Schema block for the current block.
    provider_schema = Schema(block)

    # Get the two main objects in the schema, providers and parameters
    providers = provider_schema.properties['provider']
    parameters = provider_schema.properties['parameter']

    # Confirm that there is an OLS provider (all we support)
    if not 'OLS' in providers:
        print('ERROR: No OLS in the list of providers')
        return []
    #print(providers['OLS'])

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
    curie_array = curie.split(':')
    if len(curie_array) != 2:
        print('ERROR: Invalud CURIE %s'%(curie))
        return False

    curie_prefix = curie_array[0]
    curie_value = curie_array[1]

    if not curie_prefix in ontology_iri_dict:
        print('ERROR: Curie prefix %s not in IRI list'%(curie_prefix))
        return False
    if not curie_prefix in ontology_url_dict:
        print('ERROR: Curie prefix %s not in URL list'%(curie_prefix))
        return False

    query_iri = ontology_iri_dict[curie_prefix]+str(curie_value)
    query = ontology_url_dict[curie_prefix].replace('{iri}',query_iri)
    if verbose:
        print('### Query = %s'%(query))
    response = processGetQuery(query, verbose)
    if verbose:
        print('### Response = %s'%(response))
    obo_terms = response['_embedded']['terms']
    for term in obo_terms:
        if term['label'] == curie_label:
            if verbose:
                print('### CURIE MATCHES (%s, %s)'%(term['label'], curie_label))
            return True

    print('ERROR: Invalid CURIE/label: %s, %s, correct label = %s'%(options.curie, options.curie_label, term['label']))
    return False



def getArguments():
    # Set up the command line parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=""
    )

    # The YAML spec file to load
    parser.add_argument("curie")
    parser.add_argument("curie_label")
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

    # Get the IRI and URL info, both dictionaries keyed on CURIE prefix
    ontology_iri_dict = getOntologyIRIs(options.verbose)
    ontology_url_dict = getProviderURLs(options.verbose)

    # Check the value of the CURIE
    valid_curie = checkOntologyLabel(options.curie, options.curie_label,
                                     ontology_iri_dict, ontology_url_dict,
                                     options.verbose)
    # Print an exit code based on whether the test passed or failed
    if valid_curie:
        print('Valid CURIE and label: %s, %s'%(options.curie, options.curie_label))
        sys.exit(0)
    else:
        sys.exit(1)


