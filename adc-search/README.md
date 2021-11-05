# ADC Search tools

The ADC search tools are designed to make it "easy" to do relatively complex searches
of the entire AIRR Data Commons (ADC). Because the ADC is a distributed data
commons, it is necessary to send the same query to many repositories. In addition, 
because the ADC query API (ADC API) has two main entry points (/repertoire and /rearrangement)
most queries require the user to build a list of repertoires based on a repertoire query and
then perform a rearrangement query on each repertoire. As such, a typical API workflow looks
like the following:

- For each repository in the ADC
- Get a list of repertoires that match a repertoire query
  - E.g. Ask for all t-cell beta chain repertoires whose subject has a COVID-19 disease diagnosis
- For each repertoire found above, perform a specific rearrangement query
  - E.g. Search for a specific Junction AA sequence.

The ADC Search python program makes it possible to do this quite complex query with a single command. 

# Command usage 

python3 adc-search.py repository.tsv repertoire-query.json rearrangement-query.json --service_delay=0.2 --output_file=covid19-trb-shomuradova-facet.json --field_file repertoire_fields.tsv

Positional parameters:
- repository.tsv: A TSV file with a column called URL. This column should have a list of the iADC repositories that you want to search.
- repertoire-query.json: A JSON repertoire query in the ADC API query format. This query is sent to the ADC API /repertoire query end point of each repository. The list of repertoire_ids that are returned from this query are used to determine which repertoire to use in the /rearrangement search (see below).
- rearrangement-query.json: A JSON query rearrangement query in the ADC API query format. This query is sent to the /rearrangement entry point of each repository, once for each repertoire_id that is identified in the previous step.

Optional arguments:
- --field_file=field_filename.tsv: Query responses by default only contain the reperotire_id and the information that is requested from the rearrangement-query.json. This is not particularly helpful in that you don't know any details about the repertoire (study/subject/sample metadata). The field file allows you to ask for a set of repertoire metadata fields to be added to the search output. These fields are specified using the field "dot" notation that is used to specify fields in the ADC API (e.g. study.study_id). The file should contain a column with a "Field" column header.
- -v: run in verbose mode, providing potentially useful output for debugging when things don't work as epxected.
- --service_delay=N: The above command can easily generate thousands of queries. Some web services have a throttling mechanism where they begin to return error messages (Too many requests) if they are bombarded by too many queries. This is to prevent Denial of Service attacks. In some cases it may be necessary to use a service delay to throttle the queries sent to the repositories.
- --output_file=output_filename.json: By default the query responses from the repositories are printed to stdout. If you want you can redirect the output to a file of your choice.

# Output format

The ouput of the command returns a JSON array, structured as follows:
- There is one array element per repository
  - Each element consists of two fields, a repository and results field
    - "repository" : "http://covid19-1.ireceptor.org/airr/v1/rearrangement"
    - "results" : Array of JSON objects, one per repertoire,  structured as follows:
      - "Info": The standard ADC API JSON Info object. This is identical to the Info object returned by the ADC API.
      - The normal ADC API /rearrangement object that is returned by the ADC API (see the ADC API docs for more info). This will either be a "Facet" field or a "Rearrangement" field. Its structure is described in the ADC API documentation.
      - "Repertoire": A JSON object that contains the requested repertoire metadata fields for this query (essentially the fields in the "field_filename.tsv" file above) 
