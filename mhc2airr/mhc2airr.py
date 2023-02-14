# This script creates an AIRR MHCGenotypeSet object, which can be used to update an AIRR Repertoire with MHC/HLA info.
# It requires 2 input tsv files: hla_file and id_file

# hla_file criteria:
# 1) A col named subject_id, and col(s) for the relevant mhc class I genes (A_1, A_2, B_1, B_2, C_1, C_2) and/or
# class II genes (DRB1_1, DRB1_2, DQA1_1, DQA1_2, DQB1_1, DQB1_2, DPA1_1, DPA1_2, DPB1_1, DPB1_2)
# 2) 1 row per subject
# 3) Genes mapped to HLA nomenclature (e.g. HLA-DRB1*08:01)
# 4) If sequencing was phased (i.e. _1 and _2 order is important), cols must be arranged as such (i.e. DRB1_1, DRB1_2)

# id_file criteria:
# 1) For each row (i.e. sample) in the metadata sheet, provide the following as it appears in the database:
# subject_id, repertoire_id, data_processing_id, sample_processing_id, data_processing_files

import pandas as pd
import copy
import json
import argparse

ap = argparse.ArgumentParser()

ap.add_argument("hla_file", help="path to hla file, with one row per subject")
ap.add_argument("id_file", help="path to id file, with per sample ids")

args = vars(ap.parse_args())

# Specify path for hla_file and id_file
# hla_file = r'C:\Users\rj_lu\Desktop\daisy_subject_hla_full.txt'
# id_file = r'C:\Users\rj_lu\Desktop\t1d-file2.txt'

# Read in the tsv files to data frames
hla_df = pd.read_csv(args["hla_file"], sep="\t")
id_df = pd.read_csv(args["id_file"], sep="\t")

# Define lists for mhc1 and mhc2 genes, based on the tsv headers
mhc_class_1_list = ['A_1', 'A_2', 'B_1', 'B_2', 'C_1', 'C_2']
mhc_class_2_list = ['DRB1_1', 'DRB1_2', 'DQA1_1', 'DQA1_2', 'DQB1_1', 'DQB1_2',	'DPA1_1', 'DPA1_2', 'DPB1_1', 'DPB1_2']

# Define the mapping for each gene to the MRO (https://www.ebi.ac.uk/ols/ontologies/mro)
mro_dict = {"MRO:0000057": "HLA-DRB1 gene", "MRO:0000053": "HLA-DQA gene", "MRO:0000054": "HLA-DQB gene",
            "MRO:0000051": "HLA-DPA gene", "MRO:0000052": "HLA-DPB gene", "MRO:0000046": "HLA-A gene", "MRO:0000047": "HLA-B gene",
            "MRO:0000049": "HLA-C gene"}

# Loop through each row in id_file, with nested loop through hla_file
for id_ind, id_row in id_df.iterrows():
    for hla_ind, hla_row in hla_df.iterrows():
        # Ensure subject_id matches in each file, then assign value of subject_id to subject variable
        if id_row["subject_id"] == hla_row["subject_id"]:
            subject = id_row["subject_id"]
            # From the multi-subject hla_df, create a subset hla_df for subject
            hla_df_subject = hla_df[hla_df['subject_id']==subject]

            # Make empty lists and dictionaries
            mhc_1_alleles_list = list()
            mhc_2_alleles_list = list()
            mhc_1_alleles_dict = dict()
            mhc_2_alleles_dict = dict()
            mhc_1_mro_dict = dict()
            mhc_2_mro_dict = dict()
            mhc_1_list = list()
            mhc_2_list = list()
            mhc_1_genotype_set_dict = dict()
            mhc_2_genotype_set_dict = dict()

            # Loop through the indexes (i.e. rows) in hla_df_subject, with nested loop through the cols
            for index in hla_df_subject.index:
                for col in hla_df_subject.columns:
                    # Check whether col header is in mhc_class_1_list
                    if col in mhc_class_1_list:
                        # If col is in mhc_class_1_list, take the value at index/col and assign it to mhc1 allele name for that col
                        mhc_1_name = hla_df_subject.at[index,col]
                        # Ignore NA cases
                        if not pd.isna(mhc_1_name):
                            # Make a dictionary with gene:typed mhc1 allele, e.g. {'A_1': 'HLA-A*03:01'}
                            dict1 = {col:mhc_1_name}
                            # Add each mhc1 allele dict to a growing list
                            # e.g. [{'A_1': 'HLA-A*03:01'}, {'A_2': 'HLA-A*24:02'}, {'B_1': 'HLA-B*39:06'}, {'B_2': 'HLA-B*44:02'},...]
                            mhc_1_alleles_list.append(dict1)

                    # If the allele is in the mhc_class_2_list, repeat the above procedure
                    # End result is a list of mhc2 allele dicts, e.g. [{'DRB1_1': 'HLA-DRB1*08:01'}, {'DQA1_1': 'HLA-DQA1*04:01'},...]
                    # Note the need to have cols in tsv organized as DRB1_1, DRB1_2, else you get the above out of order list...
                    if col in mhc_class_2_list:
                        mhc_2_name = hla_df_subject.at[index,col]
                        if not pd.isna(mhc_2_name):
                            dict2 = {col:mhc_2_name}
                            mhc_2_alleles_list.append(dict2)

            # Loop through each mhc1 dict, with nested loop through each dict key/value pair
            for mhc1_dict in mhc_1_alleles_list:
                for key, value in mhc1_dict.items():
                    # Create a dict like so  {"allele_designation":"HLA-A*0201"}
                    mhc_1_alleles_dict["allele_designation"] = mhc1_dict[key]
                    # Loop through mro_dict
                    for mro_key, mro_value in mro_dict.items():
                        # Check which key (mro ontology id) to assign the gene
                        if value[0:5] in mro_value:
                            mhc_1_mro_dict["id"] = mro_key
                            mhc_1_mro_dict["label"] = mro_value
                            mhc_1_alleles_dict["gene"] = mhc_1_mro_dict

                    # Copy the mhc_1_alleles_dict, then add the copy to a list with one item
                    dict_copy = copy.deepcopy(mhc_1_alleles_dict)
                    mhc_1_list.append(dict_copy)

            # Repeat the above for each mhc2 dict
            for mhc2_dict in mhc_2_alleles_list:
                for key, value in mhc2_dict.items():
                    mhc_2_alleles_dict["allele_designation"] = mhc2_dict[key]
                    for mro_key, mro_value in mro_dict.items():
                        if value[0:7] in mro_value:
                            mhc_2_mro_dict["id"] = mro_key
                            mhc_2_mro_dict["label"] = mro_value
                            mhc_2_alleles_dict["gene"] = mhc_2_mro_dict
                    dict_copy2 = copy.deepcopy(mhc_2_alleles_dict)
                    mhc_2_list.append(dict_copy2)

            # Make an mhc_genotype_set dict for both mhc1 and mhc2. The dicts include mhc1_list and mhc2_list from above.
            if mhc_1_list: # Ensures list is not empty (in Daisy study, not all subjects had mhc1 gene calls)
                mhc_1_genotype_set_dict["mhc_genotype_id"] = str(subject) + "_TCRB_MHC-I" # Could make locus a variable
                mhc_1_genotype_set_dict["mhc_class"] = "MHC-I"
                mhc_1_genotype_set_dict["mhc_alleles"] = mhc_1_list
                mhc_1_genotype_set_dict["mhc_genotyping_method"] = hla_df_subject.at[index,"mhc_genotyping_method"]

            mhc_2_genotype_set_dict["mhc_genotype_id"] = str(subject) + "_TCRB_MHC-II" # Could make locus a variable
            mhc_2_genotype_set_dict["mhc_class"] = "MHC-II"
            mhc_2_genotype_set_dict["mhc_alleles"] = mhc_2_list
            mhc_2_genotype_set_dict["mhc_genotyping_method"] = hla_df_subject.at[index,"mhc_genotyping_method"]

            # Make the mhc_genotype_set list, which is a 2-element list [mhc_1_genotype_set_dict, mhc_2_genotype_set_dict]
            mhc_genotype_list =[]
            if mhc_1_list: # Ensures a non-empty list
                mhc_genotype_list.append(mhc_1_genotype_set_dict)
            mhc_genotype_list.append(mhc_2_genotype_set_dict)

            # Make the mhc_genotype_set object, which is a dict that includes the mhc_genotype_list
            mhc_genotype_set = {}
            mhc_genotype_set["mhc_genotype_set_id"] = str(subject) + "_TCRB_MHC" # Could make locus a variable
            mhc_genotype_set["mhc_genotype_list"] = mhc_genotype_list

            # Make the genotype object, which is a dict that contains one element, the mhc_genotype_set
            genotype = {}
            genotype["mhc_genotype_set"] = mhc_genotype_set

            # Make the subject object, which is a dict that contains one element, the genotype
            subject_dict = {}
            subject_dict["genotype"] = genotype

            # Make the sample object
            sample = {}
            sample["sample_processing_id"] = id_df.loc[id_ind,"sample_processing_id"] # Look up the sample_processing_id value in col == "sample_processing_id", in id_df
            sample_id = id_df.loc[id_ind,"sample_processing_id"] # Define sample_id, which we include in the output file name
            data_processing_files = []
            data_processing_files.append(id_df.loc[id_ind,"data_processing_files"]) # Look up the data_processing_files, as above

            # Make the data_processing object, which includes the list of data_processing_files
            data_processing_dict = {}
            data_processing_dict["data_processing_id"] = id_df.loc[id_ind,"data_processing_id"] # Look up the data_processing_id, as above
            data_processing_dict["data_processing_files"] = data_processing_files

            # Make a data_processing_list, which contains one element, the data_processsing object
            data_processing_list = []
            data_processing_list.append(data_processing_dict)

            # Make the repertoire object
            repertoire_dict = {}
            repertoire_dict["repertoire_id"] = id_df.loc[id_ind,"repertoire_id"]
            repertoire_dict["data_processing"] = data_processing_list
            repertoire_dict["sample"] = sample
            repertoire_dict["subject"] = subject_dict

            # Put the repertoire object into a one-element list
            repertoire_list = []
            repertoire_list.append(repertoire_dict)

            # Create the top level object, which contains one element, the repertoire list
            repertoire_top_dict = {}
            repertoire_top_dict["Repertoire"] = repertoire_list

            print(repertoire_top_dict)

            # create the output file
            # with open(str(subject) + "_" + str(sample_id) + "_mhc_genotype.json", "w") as outfile:
            #     json.dump(repertoire_top_dict, outfile) # dump the repertoire top object to outfile, in json format

# def getArguments():
#     # Set up the command line parser
#     parser = argparse.ArgumentParser(
#         formatter_class=argparse.RawDescriptionHelpFormatter,
#         description=""
#     )
#     parser = argparse.ArgumentParser()
#
#     # The hla file name
#     parser.add_argument("hla_file")
#     # The id file name
#     parser.add_argument("id_file")
#
# if __name__ == "__main__":
#     # Get the command line arguments.
#     options = getArguments()


