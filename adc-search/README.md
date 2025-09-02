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
- --output_format=[JSON|TSV]: By default the query responses from the repositories are printed in JSON format as they list stats per repertoire. If you want to download the rearrangements per repertoire to a TSV file, use the TSV output format. If you want you can redirect the JSON output to a file of your choice and the TSV repertoire output to a set of files in an output directory of your choice.
- --output_file=output_filename.json: By default the query responses from the repositories are printed to stdout. If you want you can redirect the output to a file of your choice.
- --output_dir=output_directory: By default the query responses from the repositories are printed to stdout. If you want you can redirect the output to a directory of choice. This only applies to the TSV file format. 

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
python3 adc-search.py repository-covid19.tsv repertoire-covid19-trb.json rearrangemetn-shomuradova-cdr3-motif.json --service_delay=0.2 --output_file=covid19-trb-shomuradova-facet.json --field_file repertoire_fields.tsv
```
This command searches the COVID 19 repositories [repository-covid19.tsv](repository-covid19.tsv) for repetoires with TRB data from subjects diagnosed with COVID-19 [reperotire-covid19-trb.json](repertoire-covid19-trb.json) and then issues a CDR3 motif search (searching for CDR3 with the following pattern - CASS[YD][SGR][DTGN]TGELFF) and asks for a facet (count) response for each repertoire_id [rearrangement-shomuradova-cdr3-motif.json](rearrangement-shomuradova-cdr3-motif.json). It also asks for a set or Repertoire metadata to be returned as specified in [repertoire_fields.tsv](repertoire_fields.tsv).

This query is essentially searching the iReceptor COVID19 data (a substantial portion of the ADC) for the public CDR3 motif that was found in the paper from Shomuradov et al. [SARS-CoV-2 Epitopes Are Recognized by a Public and Diverse Repertoire of Human T Cell Receptors](https://doi.org/10.1016/j.immuni.2020.11.004).

# Example Output

The output from the following very basic query of a single repertoire is given as follows:

```
python3 adc-search.py repository-covid19.tsv repertoire-covid19-1-repertoire.json rearrangement-shomuradova-cdr3-motif.json --service_delay=0.2 --output_file=output_one_reperotire.json --field_file repertoire_fields.tsv
Info: Processing 1 repertoires from http://covid19-1.ireceptor.org/airr/v1/rearrangement
Info: Performed 1 queries in 0.447262 s, 2.235828 queries/s
Info: Processing 0 repertoires from http://covid19-2.ireceptor.org/airr/v1/rearrangement
Info: Performed 0 queries in 0.000003 s, 0.000000 queries/s
Info: Processing 0 repertoires from http://covid19-3.ireceptor.org/airr/v1/rearrangement
Info: Performed 0 queries in 0.000002 s, 0.000000 queries/s
Info: Processing 0 repertoires from http://covid19-4.ireceptor.org/airr/v1/rearrangement
Info: Performed 0 queries in 0.000004 s, 0.000000 queries/s
```
The output from this query can be found [output_one_repertoire.json](output_one_repertoire.json). In this case, the repertoire_id of interest is found in only one repository and the JSON response contains a count of the number of CDR3s of interest in that reperotire as well as the requested repertoire metadata.

# Utility scripts

Two utility scripts are provided, integrating queries across both the AIRR Data Commons and the
[Immune Epitope Database](http://iedb.org). These utility scripts make extensive use of
adc_search.py to perform complicated queries across the ADC.

## Receptor report

receptor-report.sh takes similar input files for repositories, repertoire query, and repertoire fields
to display, but it also take a Junction, a V gene, a J gene. 

```
$ ./receptor_report_fast.sh
Usage: ./receptor_report_fast.sh REPOSITORY_TSV REPERTOIRE_QUERY_JSON REPERTOIRE_FIELD_TSV JUNCTION VGENE JGENE OUTPUT_DIR SUMMARY_FILE
```
The ADC part of the output is generated as follows:
- The ADC repositories in `REPOSITORY_TSV` are searched using the `REPERTOTOIRE_QUERY_JSON`
- For each Repertoire found, the repertoire is searched for an exact match of the given
"Receptor Chain" given by `JUNCTION VGENE JGENE`
- Output will reside in `OUTPUT_DIR`
- A summary of the output will reside in OUTPUT_DIR/SUMMARY_FILE
- For each Receptor a directory will be created that will include:
  - The full JSON response of the query as sent to adc_search.py
  - A TSV file for each repertoire with the rearrangements for the chain.
  - A summary of the number of instances discovered and the number of repertoires in which the receptor chain was found is written to `report.out`. 

## Run Receptor Reports

run_receptor_reports.sh is a utility script the runs `receptor_report.sh` many times, once per "Receptor Chain"
that is included in an input Receptor file. 

```
$ ./run_receptor_reports_fast.sh
Usage: ./run_receptor_reports_fast.sh RECEPTOR_TSV REPOSITORY_TSV REPERTOIRE_QUERY_JSON REPERTOIRE_FIELD_TSV OUTPUT_DIR
```

Similar to `receptor_report.sh` it takes a `REPOSITORY_TSV` file that determines the repositories it
searches, a `REPERTOIRE_QUERY_JSON` file that has the repertoire query to perform, and a `REPERTOIRE_FIELD_TSV`
file that determines the fields of interest. Rather than run on a single "Receptor Chain" it takes as input
a TSV file with three columns that contain the Junction AA string, the V gene, and the J gene. 

A directory for each "Receptor Chain" is created, and the report generated by `receptor_report.sh` is placed in this directory.

