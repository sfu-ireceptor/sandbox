# AIRR Specification flatten utility

This code takes the current AIRR specification, as loaded through the AIRR
python module being used, and "flattens" it into a TSV file. The TSV file
contains a set of columns with the attributes from the AIRR spec set as 
defined in the AIRR schema.

Usage: python3 airr-flatten.py > AIRR.tsv

This command is used to create the AIRR specific columns for the iReceptor AIRR
configuration file (https://github.com/sfu-ireceptor/config) used by the
various iReceptor platform tools. The columns in the iReceptor AIRR mapping
file that begin with "airr_" are generated using this tool.
