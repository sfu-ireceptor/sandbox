# ADC Ontology Checks

The ADC ontology checking tools are designed to check the validity of ontology fields
and their values. These checks are based on the AIRR specification and the Ontology
definitions in the AIRR Spec are used to build the queries to determine if the ontology
values are correct. As a result it is a *requirement* that python has the AIRR python 
package installed. Also note that for now, this requires an AIRR Library that has the
CURIEMap and InformationProvider objects defined (likely v1.4) which is not currently 
available through pip.

The ontology checks are strict, in that they expect the CURIE of interest
(e.g. NCBITAXON:9606) to map exactly to the ontology label for that ID (e.g. "Homo sapiens")
including the case of the label. If the label reports an error, and you are satisfied that the
label is an appropriate synonym for that ontology ID, then such error messages can be ignored as 
synonyms are acceptable in the label for an ontology field.

# ADC CURIE checks

The tool takes a list of repositories, and for each reperotire in that repository, checks a list of fields
to ensure that any ontology values are valid. A valid ontology field is one that contains a CURIE in the
ontology `id` field and contains a matching `label` according to the AIRR Ontology provider as listed in 
the AIRR Spec for that field.
```
python3 adc-curie-check.py repository.tsv fields.tsv
```
Positional parameters:
- repository.tsv: A TSV file with a column called URL. This column should have a list of the ADC repositories that you want to search.
- fields.tsv: A list of AIRR ontology fields that you want to check. These fields are specified using the field "dot" notation that is used to specify fields in the ADC API (e.g. study.study_type). The file should contain a column with a "Field" column header. This column should hold only AIRR Ontology field names, otherwise errors will be reported for each repertoire.
- -v: run in verbose mode, providing potentially useful output for debugging when things don't work as epxected.

# Output format

The ouput of the command returns a report per repertoire in each repository

```
$ python3 adc-curie-check.py repository.tsv fields.tsv
Info: Reading input files
Info: Building AIRR Spec ontology queury mappings
Info: Running CURIE check on repository https://ipa1.ireceptor.org
Info: Processing repertoire 2
Info: Processing repertoire 5
Info: Processing repertoire 4

[Good repertoire reports delete...]

Info: Processing repertoire 94
Info: Processing repertoire 96
ERROR: Invalid CURIE/label: DOID:0050873, small lymphocytic lymphoma, follicular lymphoma, correct label = follicular lymphoma
Info: Processing repertoire 95
Info: Processing repertoire 97
Info: Processing repertoire 93
Info: Processing repertoire 98
Info: Processing repertoire 99
ERROR: Invalid CURIE/label: DOID:1040, CLL/SLL, correct label = chronic lymphocytic leukemia
Info: Processing repertoire 100
ERROR: Invalid CURIE/label: DOID:0050873, small lymphocytic lymphoma, follicular lymphoma, correct label = follicular lymphoma
```
