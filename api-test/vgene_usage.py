import urllib.request, urllib.parse
import json
import os, ssl
import time

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
        url_response = response.read()
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
        url_response = response.read()
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
    # Return the JSON data
    return json_data

# Deafult OS do not have create cient certificate bundles. It is
# easiest for us to ignore HTTPS certificate errors in this case.
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)): 
    ssl._create_default_https_context = ssl._create_unverified_context

# Set the base URL to use 
#base_url = 'ipa1.ireceptor.org'
#base_url = 'ipa2.ireceptor.org'
#base_url = 'ipa3.ireceptor.org'
#base_url = 'ipa4.ireceptor.org'
#base_url = 'vdjserver.org/ireceptor'
base_url = 'turnkey-test2.ireceptor.org'

# Select the API entry point to use, in this case /v2/samples
sample_url = 'http://'+base_url+'/v2/samples'
sequence_url = 'http://'+base_url+'/v2/sequences_summary'

# Set up the header for the post request.
header_dict = {'accept': 'application/json',
               'Content-Type': 'application/x-www-form-urlencoded'}

# Junction AA length queries.
query_key = 'junction_aa_length'
query_values = range(40)

# Possible v_call queries
#query_key = 'v_call'
#query_values = ['IGHV1','IGHV2','IGHV3','IGHV4','IGHV5','IGHV6','IGHV7','IGHV8']
#query_values = ['IGHV1','IGHV2','IGHV3','IGHV4','IGHV5','IGHV6','IGHV7','IGHV8']
#query_values = ['TRBV1','TRBV2','TRBV3','TRBV4','TRBV5','TRBV6','TRBV7','TRBV8']

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

for sample in sample_json:
    value_dict = sample_dict[str(sample['_id'])] 
    print('sample = ' + sample['sample_id'])
    for key, value in value_dict.items():
        print(str(key) + ' = ' + str(value))
        


# Get the samples from the URL, no query filters... In this case we iterated over all
# samples and search for each value for each sample. This has a much higher overhead
# as it does many more API calls than the above. It also may start timing out, as the
# queries are generated but not flushed it appears, so we get too many queries against
# the service. 
#sample_json = getSamples(sample_url, header_dict)
#print("There are %d samples in the response" % (len(sample_json)))
#for sample in sample_json:
#    print(str(sample['ir_project_sample_id']) + " " +
#          sample['study_id'] + " " +
#          sample['sample_id'] + " " +
#          str(sample['ir_sequence_count']))
#    for value in query_values:
#        query_dict = dict()
#        query_dict.update({'ir_project_sample_id_list[]': sample['ir_project_sample_id']})
#        query_dict.update({query_key: value})
#        sequence_summary_json = getSequenceSummary(sequence_url, header_dict, query_dict)
#        filtered_sequence_count = 0
#        if len(sequence_summary_json) > 0:
#            values = sequence_summary_json[0]
#            filtered_sequence_count = values['ir_filtered_sequence_count']
#        print('   ' + query_key + ' ' + str(value) + ' = ' + str(filtered_sequence_count))
#        time.sleep(0.5)
