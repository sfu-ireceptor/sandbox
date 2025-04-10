#!/bin/bash 

awk -F'\t' -v column_val="$1" '{ if (NR==1) {val=-1; for(i=1;i<=NF;i++) { if ($i == column_val) {val=i}}}; if(val != -1) {if (length($val) > 0) {print $val}}} ' $2

