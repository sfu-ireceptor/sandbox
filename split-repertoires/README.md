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
