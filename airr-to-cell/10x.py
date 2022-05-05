# This code from this page: https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/output/matrices#mat-py
import csv
import gzip
import os
import scipy.io
import pandas as pd
 
# define MEX directory
matrix_dir = "/opt/sample345/outs/filtered_feature_bc_matrix"
# read in MEX format matrix as table
mat = scipy.io.mmread(os.path.join(matrix_dir, "matrix.mtx.gz"))
 
# list of transcript ids, e.g. 'ENSG00000243485'
features_path = os.path.join(matrix_dir, "features.tsv.gz")
feature_ids = [row[0] for row in csv.reader(gzip.open(features_path, mode="rt"), delimiter="\t")]
 
# list of gene names, e.g. 'MIR1302-2HG'
gene_names = [row[1] for row in csv.reader(gzip.open(features_path, mode="rt"), delimiter="\t")]
 
# list of feature_types, e.g. 'Gene Expression'
feature_types = [row[2] for row in csv.reader(gzip.open(features_path, mode="rt"), delimiter="\t")]
barcodes_path = os.path.join(matrix_dir, "barcodes.tsv.gz")
barcodes = [row[0] for row in csv.reader(gzip.open(barcodes_path, mode="rt"), delimiter="\t")]

# transform table to pandas dataframe and label rows and columns
matrix = pd.DataFrame.sparse.from_spmatrix(mat)
matrix.columns = barcodes
matrix.insert(loc=0, column="feature_id", value=feature_ids)
matrix.insert(loc=0, column="gene", value=gene_names)
matrix.insert(loc=0, column="feature_type", value=feature_types)

# display matrix
print(matrix)
# save the table as a CSV (note the CSV will be a very large file)
matrix.to_csv("mex_matrix.csv", index=False)
