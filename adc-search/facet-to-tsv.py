import pandas as pd
import numpy as np
import argparse
import json
import os, ssl
import sys
import time

def getArguments():
    # Set up the command line parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=""
    )

    # A JSON file as output by adc_search.py
    parser.add_argument("adc_analysis_json")

    # Field file
    parser.add_argument(
        "--field_file",
        dest="field_file",
        default=None,
        help="File that contains a list of AIRR fields in dot notation (subject.subject_id). These fields are output in every repertoire query output in a 'Repertoire' object. If no file is provided then an empty repertoire object is created."
    )

    # Output file
    parser.add_argument(
        "--output_file",
        dest="output_file",
        default=None,
        help="The output file to use. If none supplied, uses stdout."
    )

    # Parse the command line arguements.
    options = parser.parse_args()
    return options


if __name__ == "__main__":
    # Get the command line arguments.
    options = getArguments()

    # Get the output file handle
    if options.output_file == None:
        output_handle = sys.stdout
    else:
        try:
            output_handle = open(options.output_file, "w")
            print("Output file = %s"%(options.output_file))
        except Exception as err:
            print("ERROR: Unable to open output file %s - %s" % (options.output_file, err))
            sys.exit(1)

    # Read in the repertoire field file
    if options.field_file is None:
        repertoire_field_df = pd.DataFrame([])
    else:
        try:
            repertoire_field_df = pd.read_csv(options.field_file, sep='\t',
                                        engine='python', encoding='utf-8-sig')
        except Exception as err:
            print("ERROR: Unable to open file %s - %s" % (options.repository_url_file, err))
            sys.exit(1)

    # Open the analysis file.
    with open(options.adc_analysis_json) as f:
        analysis_dict = json.load(f)

    # Set up the data frame
    columns = ["repository","repertoire_id","count"]
    for index, row in repertoire_field_df.iterrows():
       columns.append(row["Fields"])
    analysis_df = pd.DataFrame(columns=columns)
    print("Empty analysis Dataframe ", analysis_df, sep='\n')
    print("Done")

    for repository_dict in analysis_dict:
        repository = repository_dict["repository"]
        for result in repository_dict["results"]:
            record_dict = dict()
            record_dict["repository"] = repository
            if "Facet" in result:
                if len(result["Facet"]) >= 1:
                    record_dict["count"] = result["Facet"][0]["count"]
                    record_dict["repertoire_id"] = result["Facet"][0]["repertoire_id"]
                else:
                    record_dict["count"] = 0
                    record_dict["repertoire_id"] = ""
            if "Repertoire" in result:
                repertoire_info = result["Repertoire"]
                for field in repertoire_info:
                    record_dict[field] = repertoire_info[field]

            print("Record = " + str(record_dict))
            #analysis_df = analysis_df.append(record_dict, ignore_index=True)
            #analysis_df = pd.concat([analysis_df, pd.DataFrame([record_dict])], ignore_index=True)
            #analysis_df = pd.concat([analysis_df, pd.DataFrame([record_dict])])
            analysis_df.iloc[-1] = record_dict
    print("Dataframe ", analysis_df, sep='\n')
    analysis_df.to_csv(output_handle, sep='\t',index=False)
