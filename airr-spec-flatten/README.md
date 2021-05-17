# AIRR Specification flatten utility

This code takes the current AIRR specification, as loaded through the AIRR
python module being used, and "flattens" it into a TSV file. Note that the
AIRR python library has the spec built in to the library, and it is this
specification that is used. The TSV file
contains a set of columns with the attributes from the AIRR spec set as 
defined in the AIRR schema.

Usage: python3 airr-flatten.py > AIRR.tsv

This command is used to create the AIRR specific columns for the iReceptor AIRR
configuration file (https://github.com/sfu-ireceptor/config) used by the
various iReceptor platform tools. The columns in the iReceptor AIRR mapping
file that begin with "airr_" are generated using this tool.

# Using a different AIRR version

If you want to use a different AIRR specification than the one built into the AIRR
library installed through PIP, then you have to install that version. To do this from
the AIRR Github, check out/clone the version that you want from the AIRR Github
(https://github.com/airr-community/airr-standards) and install it following the
python install instructions here: 
https://github.com/airr-community/airr-standards/tree/master/lang/python

A typical install command for a custom AIRR version would be:

python3 setup.py install --user


