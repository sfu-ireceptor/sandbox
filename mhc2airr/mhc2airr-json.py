# This script creates an AIRR MHCGenotypeSet object, which can be
# used to update an AIRR Repertoire with MHC/HLA info.
# It requires 2 input tsv files: hla_file and id_file

# hla_file criteria:
# 1) A col named subject_id, a col named mhc_genotyping_method, and col(s)
#    for the relevant mhc class I genes (A_1, A_2, B_1, B_2, C_1, C_2) and/or
#    class II genes (DRB1_1, DRB1_2, DQA1_1, DQA1_2, DQB1_1, DQB1_2, DPA1_1, DPA1_2, DPB1_1, DPB1_2)
# 2) 1 row per subject (MHC is subject specific)
# 3) Genes mapped to HLA/MHC gene nomenclature (e.g. HLA-DRB1*08:01)
# 4) If sequencing was phased (i.e. _1 and _2 order is important), cols must be arranged as such (i.e. DRB1_1, DRB1_2)

# id_file criteria:
# 1) For each row (i.e. sample) in the metadata sheet (each repertoire),
# provide the following as it appears in the database:
# subject_id, repertoire_id, data_processing_id, sample_processing_id, data_processing_files, 

import pandas as pd
import math
import copy
import json
import argparse

# Process the MHC data provided
def processMHC(mhc_path, id_path, output_dir):
    # Read in the tsv files to data frames
    mhc_df = pd.read_csv(mhc_path, sep="\t")
    id_df = pd.read_csv(id_path, sep="\t")

    # Define lists for mhc1 and mhc2 genes, based on the tsv headers
    mhc_class_1_list = ['A_1', 'A_2', 'B_1', 'B_2', 'C_1', 'C_2']
    mhc_class_2_list = ['DRB1_1', 'DRB1_2', 'DRB3_1', 'DRB3_2', 'DRB4_1', 'DRB4_2', 'DRB5_1', 'DRB5_2',
                        'DQA1_1', 'DQA1_2', 'DQB1_1', 'DQB1_2', 'DPA1_1', 'DPA1_2', 'DPB1_1', 'DPB1_2']

    # Define the mapping for each gene to the MRO (https://www.ebi.ac.uk/ols/ontologies/mro)
    mro_dict = {"MRO:0000057": "HLA-DRB1 gene",
                "MRO:0000058": "HLA-DRB3 gene",
                "MRO:0000059": "HLA-DRB4 gene",
                "MRO:0000060": "HLA-DRB5 gene",
                "MRO:0000053": "HLA-DQA1 gene",
                "MRO:0000054": "HLA-DQB1 gene",
                "MRO:0000051": "HLA-DPA1 gene",
                "MRO:0000052": "HLA-DPB1 gene",
                "MRO:0000046": "HLA-A gene",
                "MRO:0000047": "HLA-B gene",
                "MRO:0000049": "HLA-C gene"}

    # Loop through each row in id_file, we want a MHC JSON file for each repertoire
    for id_ind, id_row in id_df.iterrows():
            # Get the subject ID
            subject = id_row["subject_id"]
            
            # From the multi-subject mhc_df, create a subset mhc_df for subject
            mhc_df_subject = mhc_df[mhc_df['subject_id']==subject]

            # Check to make sure there is only one result. There should be a
            # unique HLA for each subject.
            if mhc_df_subject.shape[0] != 1:
                print("Warning: Non unique MHC for subject %s"%(subject))
            # Get the subject MHC info as a dictionary
            mhc_dict = mhc_df_subject.iloc[0].to_dict()

            # Make empty lists to keep track of the MHC data for this subject
            mhc_1_list = list()
            mhc_2_list = list()

            # Loop through the MHC values for this subject
            for mhc_key, mhc_value in mhc_dict.items():
                    
                    # Check whether the key is in mhc_class_1_list
                    if mhc_key in mhc_class_1_list:
                        # Check if value is a string (pandas reads empty values as nan)
                        # If empty, replace with an empty string.
                        if not isinstance(mhc_value,str):
                            mhc_value = ""
                        # If the string is > 0 in length then process the allele.
                        if len(mhc_value) > 0:
                            # Create empty dict, use the value as the default allele
                            airr_mhc_dict = dict()
                            mhc_allele = mhc_value

                            # If we are processing a measurement per allele, extract it
                            # Alleles with measurements are expected to be of the form
                            # "HLA-DRB1*03:01,0.86,probability" where the second comma
                            # separated component is a measured value and the third is
                            # the metric that was used.
                            mhc_with_measurements = mhc_value.split(",")
                            # If we have a comma separated list, the allele is element
                            # 0 and the measurement is element 1
                            length = len(mhc_with_measurements)
                            if length > 1:
                                mhc_allele = mhc_with_measurements[0]
                                airr_mhc_dict["ir_allele_measurement"] = mhc_with_measurements[1]
                                if length == 3:
                                    airr_mhc_dict["ir_allele_metric"] = mhc_with_measurements[2]

                            # Assign the allele to be the value for this subject
                            airr_mhc_dict["allele_designation"] = mhc_allele

                            # Extract the gene from the allele (HLA-DRB1*03:01)
                            # Split on allele separator * and take the first element
                            mhc_gene = mhc_allele.split("*")[0]
    
                            # Loop through mro_dict for the mhc_gene
                            found = False
                            for mro_key, mro_value in mro_dict.items():
                                # Check which key (mro ontology id) to assign the gene
                                if mhc_gene in mro_value:
                                    ontology_dict = dict()
                                    ontology_dict["id"] = mro_key
                                    ontology_dict["label"] = mro_value
                                    airr_mhc_dict["gene"] = ontology_dict
                                    found = True
                                    break
                            if not found:
                                print("Warning: Could not find MRO ontology entry for %s"%(mhc_allele))

                            # Add the MHC dictionary to the list.
                            mhc_1_list.append(airr_mhc_dict)

                    # If the allele is in the mhc_class_2_list, repeat the above procedure
                    # Note the need to have cols in tsv organized as DRB1_1, DRB1_2, else you
                    # get the above out of order list...
                    if mhc_key in mhc_class_2_list:
                        # Check if value is a string (pandas reads empty values as nan)
                        # If empty, replace with an empty string.
                        if not isinstance(mhc_value,str):
                            mhc_value = ""
                        # If the string is > 0 in length then process the allele.
                        if len(mhc_value) > 0:
                            # Create empty dict, use the value as the default allele
                            airr_mhc_dict = dict()
                            mhc_allele = mhc_value

                            # If we are processing a measurement per allele, extract it
                            # Alleles with measurements are expected to be of the form
                            # "HLA-DRB1*03:01,0.86,probability" where the second comma
                            # separated component is a measured value and the third is
                            # the metric that was used.
                            mhc_with_measurements = mhc_value.split(",")
                            # If we have a comma separated list, the allele is element
                            # 0 and the measurement is element 1
                            length = len(mhc_with_measurements)
                            if length > 1:
                                mhc_allele = mhc_with_measurements[0]
                                airr_mhc_dict["ir_allele_measurement"] = mhc_with_measurements[1]
                                if length == 3:
                                    airr_mhc_dict["ir_allele_metric"] = mhc_with_measurements[2]

                            # Assign the allele to be the value for this subject
                            airr_mhc_dict["allele_designation"] = mhc_allele

                            # Extract the gene from the allele (HLA-DRB1*03:01)
                            # Split on allele separator * and take the first element
                            mhc_gene = mhc_allele.split("*")[0]
                        
                            # Loop through mro_dict for the mhc_gene
                            found = False
                            for mro_key, mro_value in mro_dict.items():
                                # Check which key (mro ontology id) to assign the gene
                                if mhc_gene in mro_value:
                                    ontology_dict = dict()
                                    ontology_dict["id"] = mro_key
                                    ontology_dict["label"] = mro_value
                                    airr_mhc_dict["gene"] = ontology_dict
                                    found = True
                            if not found:
                                print("Warning: Could not find MRO ontology entry for %s"%(mhc_allele))

                            # Add the MHC dictionary to the list.
                            mhc_2_list.append(airr_mhc_dict)

            # Make an mhc_genotype_set dict for both mhc1 and mhc2. The dicts include
            # mhc1_list and mhc2_list from above.
            # Ensures list is not empty (not all subjects will have both MHC-1 and MHC-2)
            mhc_1_genotype_set_dict = dict()
            if mhc_1_list: 
                mhc_1_genotype_set_dict["mhc_genotype_id"] = str(subject) + "_MHC-I" 
                mhc_1_genotype_set_dict["mhc_class"] = "MHC-I"
                mhc_1_genotype_set_dict["mhc_alleles"] = mhc_1_list
                if "mhc_genotyping_method" in mhc_dict:
                    mhc_1_genotype_set_dict["mhc_genotyping_method"] = mhc_dict["mhc_genotyping_method"]

            # Ensures list is not empty (not all subjects will have both MHC-1 and MHC-2)
            mhc_2_genotype_set_dict = dict()
            if mhc_2_list:
                mhc_2_genotype_set_dict["mhc_genotype_id"] = str(subject) + "_MHC-II"
                mhc_2_genotype_set_dict["mhc_class"] = "MHC-II"
                mhc_2_genotype_set_dict["mhc_alleles"] = mhc_2_list
                if "mhc_genotyping_method" in  mhc_dict:
                    mhc_2_genotype_set_dict["mhc_genotyping_method"] = mhc_dict["mhc_genotyping_method"]

            # Make the mhc_genotype_set list, which is a 2-element list [mhc_1_genotype_set_dict, mhc_2_genotype_set_dict]
            mhc_genotype_list =[]
            if mhc_1_list: # Ensures a non-empty list
                mhc_genotype_list.append(mhc_1_genotype_set_dict)
            if mhc_2_list: # Ensures a non-empty list
                mhc_genotype_list.append(mhc_2_genotype_set_dict)

            # Make the mhc_genotype_set object, which is a dict that includes the mhc_genotype_list
            mhc_genotype_set = {}
            mhc_genotype_set["mhc_genotype_set_id"] = str(subject) + "_MHC" 
            mhc_genotype_set["mhc_genotype_list"] = mhc_genotype_list

            # Make the genotype object, which is a dict that contains one element, the mhc_genotype_set
            genotype = {}
            genotype["mhc_genotype_set"] = mhc_genotype_set

            # Make the subject object, which is a dict that contains one element, the genotype
            subject_dict = {}
            subject_dict["genotype"] = genotype

            # Make the sample object
            sample_dict = {}
            # Look up the sample_processing_id value in col == "sample_processing_id", in id_df
            sample_dict["sample_processing_id"] = id_df.loc[id_ind,"sample_processing_id"] 
            
            # Look up the data_processing_files, as above. Because data_processing_files is
            # an array of file names, we split the string value in the TSV file on "," and
            # store it as an array.
            data_processing_files_str = id_df.loc[id_ind,"data_processing_files"]
            data_processing_files = data_processing_files_str.split(",")
            data_processing_files = [x.strip() for x in data_processing_files]

            # Make the data_processing object, which includes the list of data_processing_files
            data_processing_dict = {}
            # Look up the data_processing_id, as above
            data_processing_dict["data_processing_id"] = id_df.loc[id_ind,"data_processing_id"]
            data_processing_dict["data_processing_files"] = data_processing_files

            # Make a data_processing_list, which contains one element, the data_processsing object
            data_processing_list = []
            data_processing_list.append(data_processing_dict)

            # Make the repertoire object
            repertoire_dict = {}
            repertoire_id = id_df.loc[id_ind,"repertoire_id"] 
            repertoire_dict["repertoire_id"] = repertoire_id
            repertoire_dict["data_processing"] = data_processing_list
            repertoire_dict["sample"] = sample_dict
            repertoire_dict["subject"] = subject_dict

            # Put the repertoire object into a one-element list
            repertoire_list = []
            repertoire_list.append(repertoire_dict)

            # Create the top level object, which contains one element, the repertoire list
            repertoire_top_dict = {}
            repertoire_top_dict["Repertoire"] = repertoire_list

            # create the output file
            filename = output_dir + "/" + str(subject) + "_" + str(repertoire_id) + "_mhc_genotype.json"
            print("Info: Writing HLA file %s"%(filename))
            with open(filename, "w") as outfile:
                json.dump(repertoire_top_dict, outfile) # dump the repertoire top object to outfile, in json format
                outfile.write("\n")


def getArguments():
    # Set up the command line parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=""
    )
    parser = argparse.ArgumentParser()

    # The hla file name
    parser.add_argument("mhc_file")
    # The id file name
    parser.add_argument("id_file")
    # Output directory
    parser.add_argument("output_dir", help="Path to write output files to")

    # Parse the args and return the options.
    options = parser.parse_args()
    return options

if __name__ == "__main__":
    # Get the command line arguments.
    options = getArguments()

    processMHC(options.mhc_file, options.id_file, options.output_dir)


