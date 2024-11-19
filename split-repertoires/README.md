# ADC Split Repertoires Utility

This utility is designed to work with downloads from the iReceptor Gateway. It
essentially takes a AIRR Rearrangement TSV file that contains many annotated
sequences from many AIRR Repertoires, and splits the single large TSV file into
a set of TSV files, one per Repertoire (split on the AIRR field repertoire_id),
that contain all the Rearragements from that Repertoire.

# Usage
```
bash split_repertoires.sh airr-covid-19.tsv ouput_dir
```

The above command will split the file `airr-covid-19.tsv` into N files, one
per repertoire_id (file name based on the repertoire_id field) and store the
output files in `output_dir`. This is designed to work on download files from
the iReceptor Gateway, but it will work fine on any AIRR tsv Rearrangement file.

If you want to map a file name from the above to information about that repertoire,
it is possible to extract information about the repertoire using `jq` to find
different field values. For example, for data from a Repertoire with repetoire_id =
5efbc71e5f94cb6215deecbe you extract the subject and sample info from a iReceptor
Gateway download with metadata file `airr-covid-19-metadata.json` with the following:

```
$ jq '.Repertoire[] | select(.repertoire_id == "5efbc71e5f94cb6215deecbe") | {repertoire_id, sample_id: .sample[].sample_id, locus: .sample[].pcr_target[].pcr_target_locus}' airr-covid-19-metadata.json
{
  "repertoire_id": "5efbc71e5f94cb6215deecbe",
  "sample_id": "Pt-19-1",
  "locus": "IGH"
}
```
