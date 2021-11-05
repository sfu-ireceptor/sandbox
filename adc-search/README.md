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
```
python3 adc-search.py repository.tsv repertoire-query.json rearrangement-query.json --service_delay=0.2 --output_file=covid19-trb-shomuradova-facet.json --field_file repertoire_fields.tsv
```
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

# Example usage

An example use of this code, using the input files in the repository is:

```
python3 adc-search.py repository-covid19.tsv covid19-trb.json shomuradova-cdr3-motif-facets.json --service_delay=0.2 --output_file=covid19-trb-shomuradova-facet.json --field_file repertoire_fields.tsv
```
This command searches the COVID 19 repositories [repository-covid19.tsv](repository-covid19.tsv) for repetoires with TRB data from subjects diagnosed with COVID-19 [covid19-trb.json](covid19-trb.json) and then issues a CDR3 motif search (searching for CDR3 with the following pattern - CASS[YD][SGR][DTGN]TGELFF) and asks for a facet (count) response for each repertoire_id [shomuradova-cdr3-motif-facets.json](shomuradova-cdr3-motif-facets.json). It also asks for a set or Repertoire metadata to be returned as specified in [repertoire_fields.tsv](repertoire_fields.tsv).

This query is essentially searching the iReceptor COVID19 data (a substantial portion of the ADC) for the public CDR3 motif that was found in the paper from Shomuradov et al. [SARS-CoV-2 Epitopes Are Recognized by a Public and Diverse Repertoire of Human T Cell Receptors](https://doi.org/10.1016/j.immuni.2020.11.004).

# Example Output
The output from the following very basic query of a single repertoire is given as follows:

```
python3 adc-search.py repository-covid19.tsv covid19-1-repertoire.json shomuradova-cdr3-motif-facets.json --service_delay=0.2 --output_file=one_reperotire.json --field_file repertoire_fields.tsv
Info: Processing 1 repertoires from http://covid19-1.ireceptor.org/airr/v1/rearrangement
Info: Performed 1 queries in 0.447262 s, 2.235828 queries/s
Info: Processing 0 repertoires from http://covid19-2.ireceptor.org/airr/v1/rearrangement
Info: Performed 0 queries in 0.000003 s, 0.000000 queries/s
Info: Processing 0 repertoires from http://covid19-3.ireceptor.org/airr/v1/rearrangement
Info: Performed 0 queries in 0.000002 s, 0.000000 queries/s
Info: Processing 0 repertoires from http://covid19-4.ireceptor.org/airr/v1/rearrangement
Info: Performed 0 queries in 0.000004 s, 0.000000 queries/s
```
The output from this query can be found [one_reperotire.json](one_reperotire.json). In this case, the repertoire_id of interest is found in only one repository and the JSON response contains a count of the number of CDR3s of interest in that reperotire as well as the requested repertoire metadata.
