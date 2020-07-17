# Overview

A short piece of python code that uses the ADC API to search for CDR3s from
a file.

# Usage

usage: python ADC-cdr3-search.py [-h] [-v] url cdr3_file column_header

# Example usage

Create a tab delimited file that contains your CDR3s with a header line that
names the columns in the file. The file can have as many columns as you want, 
you simply need to tell the python code the name of the file and which column
to use.

The example below uses a set of CDR3s downloaded from the VDJDB database
(https://vdjdb.cdr3.net/search). There is an example file with three lines
of CDR3 data from VDJDB included in this Github repository. The data
are CDR3s (in the CDR3 column of the file) that have been shown to be 
specific to SARS-CoV-2. It searches the ADC repository
http://covid19-1.ireceptor.org and reports how many instances of the CDR3
were found as well as the number of Repertoires in which they were found.

example: python ADC-cdr3-search.py http://covid19-1.ireceptor.org/airr/v1/rearrangement VDJDB-SARS-CoV2-3lines.tsv CDR3
