import urllib.request, urllib.parse
import json
import os, ssl

# Deafult OS do not have create client certificate bundles. It is
# easiest for us to turn off HTTPS in this case.
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)): 
    ssl._create_default_https_context = ssl._create_unverified_context

# Set the base URL to use 
#base_url = 'ipa1.ireceptor.org'
#base_url = 'ipa2.ireceptor.org'
#base_url = 'ipa3.ireceptor.org'
base_url = 'ipa4.ireceptor.org'
#base_url = 'vdjserver.org/ireceptor'

# Select the API entry point to use, in this case /v2/samples
sample_url = 'https://'+base_url+'/v2/samples'

# Set up the header for the post request.
header = {'accept': 'application/json',
          'Content-Type': 'application/x-www-form-urlencoded'}
data = urllib.parse.urlencode(header).encode()

# Try to make the connection and get a response.
try:
    response = urllib.request.urlopen(sample_url, data=data) 
    url_response = response.read()
except urllib.error.HTTPError as e:
    print('Error: Server could not fullfil the request')
    print('Error: Error code =', e.code)
    exit()
except urllib.error.URLError as e:
    print('Error: Failed to reach the server')
    print('Error: Reason =', e.reason)
    exit()

# Convert the response to JSON so we can process it easily.
json_data = json.loads(url_response)

# Print out the summary stats for the repository.
print("There are %d samples in the response" % (len(json_data)))
for sample in json_data:
    print(str(sample['ir_project_sample_id']) + " " +
          sample['study_id'] + " " + 
          sample['sample_id'] + " " + 
          str(sample['ir_sequence_count']))

