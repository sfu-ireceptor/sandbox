# MHC to AIRR JSON

Code to help generate subject level MHC that can be loaded into
the AIRR Data commons.

This code takes two TSV files, a per subject set of HLA alleles and
a per repertoire set of ID information, and generates a JSON file that
can be used with the [iReceptor Turnkey](https://github.com/sfu-ireceptor/turnkey-service-php)
to update the subject level metadata in a repository.


## Repertoire processing

We need to create a file that has the following data:
   - repertoire_id
   - sample_processing_id
   - data_processing_id
   - data_processing_files
   - subject_id

These are required fields for iReceptor update_metadata.sh to work.

First create a file with the headers:

```
echo -e "subject_id\trepertoire_id\tdata_processing_id\tsample_processing_id\tdata_processing_files" > Kent-Repertoires.tsv
```

Then extract the fields for the study of interest (e.g. IR-T1D-000002)
using a JSON query to the appropriate ADC repository (t1d-2). We use 
jq to process the JSON and output the fields to the file in TSV format.

```
curl -s -d '{"filters":{"op":"=","content":{"field":"study.study_id","value":"IR-T1D-000002"}},"fields":["subject.subject_id","repertoire_id","sample.sample_processing_id","data_processing.data_processing_id","data_processing.data_processing_files"]}' https://t1d-2.ireceptor.org/airr/v1/repertoire | jq --raw-output '.Repertoire[] | [.subject.subject_id, .repertoire_id, .data_processing[].data_processing_id, .sample[].sample_processing_id, .data_processing[].data_processing_files | if type == "array" then join(", ") else . end] | @tsv' >> Kent-Repertoires.tsv
```

## HLA Processing

Create an HLA data per subject with a single row per subject. 
The file should gave columns with headers as follows: a column
subject_id, a column mhc_genotyping_method, and columns for the
relevant mhc class I genes (A_1, A_2, B_1, B_2, C_1, C_2) and/or
class II genes (DRB1_1, DRB1_2, DQA1_1, DQA1_2, DQB1_1, DQB1_2,
DPA1_1, DPA1_2, DPB1_1, DPB1_2). See the example HLA file in this
github repository.

This data in this file, per repertoire, should match the data that is
retrieved using the following query:
```
curl -s -d '{"filters":{"op":"=","content":{"field":"study.study_id","value":"IR-T1D-000002"}},"fields":["subject.subject_id","repertoire_id","sample.sample_processing_id","data_processing.data_processing_id","data_processing.data_processing_files", "subject.genotype"]}' https://t1d-2.ireceptor.org/airr/v1/repertoire
```

## Generate the AIRR JSON update files, one per repertoire.
```
mkdir output
python3 mhc2airr-json.py Kent-HLA.tsv Kent-Repertoires.tsv output 
```

## Load the data

Load the data into an AIRR repository, assuming you have access
to the repository directly. You can run the iReceptor Turnkey
update_metadata script on each file generated to update the subject
MHC for each repertoire in the repository.
```
update_metadata.sh repertoire output/XXX.json
```
