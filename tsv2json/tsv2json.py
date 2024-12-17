import sys
import argparse
import json
import csv

def convert(key, value, dict_fields):
    # Try to convert strings
    if type(value) is str:
        if len(value) > 0:
            if value[0] == '{' and value[-1] == '}':
                # If it looks like it might be JSON string, try to convert
                try:
                    # If successful, return it
                    return json.loads(value)
                except:
                    # If conversion fails, return original
                    return value
            elif value[0] == '[' and value[-1] == ']':
                # If it looks like it might be JSON array, try to convert
                try:
                    # If successful, return it
                    return json.loads(value)
                except:
                    # If conversion fails, return original
                    return value
            else:
                try:
                    # Try to convert to int first.
                    if '.' not in value:
                        return int(value)
                    # If the value has a decimal point, try converting to a float
                    return float(value)
                except ValueError:
                    # If conversion fails, return the original string
                    return value
        else:
            # Zero length string, handle special case for dictionary fields if specified.
            # If in the list, we want to return an empty dictionary.
            if key in dict_fields:
                return dict()
        
    return value



# Transform an input TSV file into a JSON array with key value pairs
# according to the values in the row.
def tsv_to_json(tsv_file_handle, json_file_handle, dict_fields):
    # Read the TSV data from the file handle
    reader = csv.DictReader(tsv_file_handle, delimiter='\t')

    # Convert the data to a list of dictionaries
    data = []
    for row in reader:
        dictionary = dict()
        for key, value in row.items():
            dictionary[key] = convert(key, value, dict_fields)
        data.append(dictionary)

    # Write the data to the JSON file handle
    json.dump(data, json_file_handle, indent=4)
    print('', file=json_file_handle)

def getArguments():
    # Set up the command line parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=""
    )
    parser = argparse.ArgumentParser()

    # The input TSV file name
    parser.add_argument("tsv_file_name")
    # JSON output file name
    parser.add_argument(
        "-o",
        "--output",
        dest="json_file_name",
        default="",
        help="The output file, uses stdout if no file provided.")
    # Fields that should be treated as dictionaries
    parser.add_argument(
        "--dictionary_fields",
        dest="dictionary_fields",
        default="",
        help="A comma separated string of field names that should be explicitly treated as dictionaries.")
    # Verbosity flag
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Run the program in verbose mode.")

    # Parse the command line arguements.
    options = parser.parse_args()
    return options


if __name__ == "__main__":
    # Get the command line arguments.
    options = getArguments()

    # Turn the dictionary fields string into an array
    dict_fields = options.dictionary_fields.split(",")

    # Open the ouput file, use stdout if no file name supplied.
    if options.json_file_name == "":
        json_file = sys.stdout
    else:
        try:
            json_file = open(options.json_file_name, mode='w', encoding='utf-8')
        except Exception as e:
            # Gereate an error on failure
            print('ERROR: Unable to open output file %s'%(options.json_file_name))
            print('ERROR: Reason =' + str(e))
            sys.exit(1)

    # Open the input file
    try:
        tsv_file = open(options.tsv_file_name, mode='r', encoding='utf-8')
    except Exception as e:
        # Generate an error on failure
        print('ERROR: Unable to open input file %s'%(options.tsv_file_name))
        print('ERROR: Reason =' + str(e))
        sys.exit(1)

    # Perform the conversion
    tsv_to_json(tsv_file, json_file, dict_fields)

